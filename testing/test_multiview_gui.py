# File: testing/test_multiview_gui.py
# Intent: Runs a visible GUI multi-view scan and saves every image/calculation step.
# Usage: Run manually; watch PyBullet move through scan views and inspect outputs/multiview_gui/.
# Presets: red cube at a fixed pose, GUI mode, center/left/right/front multi-view inspection.
# Connects: src/perception camera/color/depth modules; src/sim robot/scene modules; outputs/multiview_gui/.
# User values: COLOR, CUBE_POSITION, OUTPUT_ROOT, VIEW_OFFSETS, and camera/perception constants.
#
# Functions:
# - main(): Builds the GUI scene, scans the cube from each view, writes artifacts, and keeps GUI open briefly.
# - make_output_dir(): Creates a timestamped output folder for one GUI scan run.
# - setup_scene(): Creates the visible PyBullet scene with one colored cube and an open Panda gripper.
# - scan_view(): Moves to one inspection target, captures RGB/depth/mask/debug images, and returns point bounds.
# - save_rgb(): Writes the raw camera RGB frame for one view.
# - save_mask(): Writes the OpenCV binary detection mask for one view.
# - save_depth(): Writes a normalized depth visualization for one view.
# - view_summary(): Computes per-view bbox, confidence, point count, and 3D bounds.
# - write_report(): Explains the center calculation from merged multi-view point bounds.
# - write_csv(): Writes per-view calculation details for quick comparison.

import csv
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pybullet as pyb
import pybullet_data

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_colored_cube, save_color_detection_debug
from src.perception.depth_cluster import mask_to_world_points, trim_outliers
from src.perception.multiview_localizer import VIEW_OFFSETS, estimate_center_from_views, inspection_targets
from src.sim.camera_controls import set_camera_view
from src.sim.robot_control import configure_gripper_friction, move_arm_to_home, move_pinch_center_to_position, open_gripper, step_simulation
from src.sim.scene_objects import CUBE_HALF_SIZE, CUBE_Z, create_colored_cube


OUTPUT_ROOT = Path("outputs/multiview_gui")
COLOR = "red"
CUBE_POSITION = (0.48, 0.00, CUBE_Z)
GUI_HOLD_SECONDS = 8


def main():
    output_dir = make_output_dir()
    panda_id, cube_id = setup_scene()
    actual = pyb.getBasePositionAndOrientation(cube_id)[0]

    summaries = []
    all_points = []
    for view_name, target in inspection_targets(actual).items():
        summary, points = scan_view(panda_id, view_name, target, output_dir)
        summaries.append(summary)
        if len(points):
            all_points.append(points)

    merged = np.vstack(all_points) if all_points else np.empty((0, 3))
    center = estimate_center_from_views(merged)
    write_csv(summaries, output_dir)
    write_report(summaries, merged, center, actual, output_dir)

    print(f"Multi-view GUI outputs: {output_dir}")
    print(f"Actual cube center: {[round(value, 4) for value in actual]}")
    print(f"Estimated center: {None if center is None else [round(float(value), 4) for value in center]}")
    time.sleep(GUI_HOLD_SECONDS)
    pyb.disconnect()


def make_output_dir():
    output_dir = OUTPUT_ROOT / datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def setup_scene():
    pyb.connect(pyb.GUI)
    pyb.resetSimulation()
    pyb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pyb.setGravity(0, 0, -9.81)
    pyb.loadURDF("plane.urdf")
    set_camera_view("front")

    panda_id = pyb.loadURDF("franka_panda/panda.urdf", basePosition=[0, 0, 0], useFixedBase=True)
    cube_id, _ = create_colored_cube(COLOR, CUBE_POSITION)
    configure_gripper_friction(panda_id)
    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
    open_gripper(panda_id)
    step_simulation(seconds=0.5)
    return panda_id, cube_id


def scan_view(panda_id, view_name, target, output_dir):
    move_pinch_center_to_position(panda_id, target)
    step_simulation(seconds=1.0)

    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_colored_cube(rgb, COLOR)
    points = mask_to_world_points(mask, depth, view_matrix, projection_matrix, rgb.shape)
    center = estimate_center_from_views(points)

    if detection is not None and center is not None:
        detection["world"] = center

    save_rgb(rgb, output_dir / f"{view_name}_01_rgb.png")
    save_mask(mask, output_dir / f"{view_name}_02_mask.png")
    save_depth(depth, output_dir / f"{view_name}_03_depth.png")
    save_color_detection_debug(rgb, detection, COLOR, output_dir / f"{view_name}_04_bbox_world.png")
    return view_summary(view_name, target, detection, points), points


def save_rgb(rgb, path):
    cv2.imwrite(str(path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))


def save_mask(mask, path):
    cv2.imwrite(str(path), mask)


def save_depth(depth, path):
    depth_image = np.clip(depth, 0, 1)
    depth_image = (255 * (1 - depth_image)).astype(np.uint8)
    cv2.imwrite(str(path), depth_image)


def view_summary(view_name, target, detection, points):
    clean_points = trim_outliers(points) if len(points) else points
    lower = np.min(clean_points, axis=0) if len(clean_points) else ["", "", ""]
    upper = np.max(clean_points, axis=0) if len(clean_points) else ["", "", ""]

    return {
        "view": view_name,
        "target": target,
        "bbox": "" if detection is None else detection["bbox"],
        "confidence": "" if detection is None else detection["confidence"],
        "points": len(points),
        "lower": lower,
        "upper": upper,
    }


def write_csv(summaries, output_dir):
    with (output_dir / "view_calculations.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "view",
                "target_x",
                "target_y",
                "target_z",
                "bbox",
                "confidence",
                "point_count",
                "min_x",
                "min_y",
                "min_z",
                "max_x",
                "max_y",
                "max_z",
            ]
        )
        for summary in summaries:
            writer.writerow(
                [
                    summary["view"],
                    *summary["target"],
                    summary["bbox"],
                    summary["confidence"],
                    summary["points"],
                    *summary["lower"],
                    *summary["upper"],
                ]
            )


def write_report(summaries, merged, center, actual, output_dir):
    clean = trim_outliers(merged) if len(merged) else merged
    lower = None if len(clean) == 0 else np.min(clean, axis=0)
    upper = None if len(clean) == 0 else np.max(clean, axis=0)

    with (output_dir / "report.md").open("w") as file:
        file.write("# Multi-View GUI Calculation Report\n\n")
        file.write(f"- Color: `{COLOR}`\n")
        file.write(f"- View offsets: `{VIEW_OFFSETS}`\n")
        file.write(f"- Actual PyBullet cube center: `{tuple(round(value, 5) for value in actual)}`\n")
        file.write(f"- Merged point count before trimming: `{len(merged)}`\n\n")

        file.write("## Per-View Artifacts\n\n")
        for summary in summaries:
            file.write(f"- `{summary['view']}`: RGB, mask, depth, and bbox/world debug PNGs saved.\n")

        file.write("\n## Center Calculation\n\n")
        if center is None:
            file.write("No center calculated because no view produced valid mask depth points.\n")
            return

        file.write(f"- Trimmed merged min xyz: `{tuple(round(float(value), 5) for value in lower)}`\n")
        file.write(f"- Trimmed merged max xyz: `{tuple(round(float(value), 5) for value in upper)}`\n")
        file.write("- Raw geometric center: `(min + max) / 2`\n")
        file.write(f"- Z correction: `center_z = max_z - CUBE_HALF_SIZE`, with `CUBE_HALF_SIZE={CUBE_HALF_SIZE}`\n")
        file.write(f"- Estimated center: `{tuple(round(float(value), 5) for value in center)}`\n")
        error = [center[index] - actual[index] for index in range(3)]
        file.write(f"- Error estimated - actual: `{tuple(round(float(value), 5) for value in error)}`\n")


if __name__ == "__main__":
    main()
