# File: testing/test_detection_offset.py
# Intent: Measures perception offset by comparing detected cube world position to PyBullet truth.
# Usage: Run manually to create CSV/report/plot/debug images under outputs/detection_offset/.
# Presets: named cube colors, three workspace positions, DIRECT PyBullet mode, wrist-camera detection.
# Connects: src/perception; src/sim/robot_control.py; src/sim/scene_objects.py; outputs/detection_offset/.
# User values: TEST_COLORS, TEST_POSITIONS, OUTPUT_ROOT, and camera/perception constants.
#
# Functions:
# - main(): Runs every color/position case, writes artifacts, and prints the output folder.
# - make_output_dir(): Creates a timestamped output directory for this test run.
# - run_case(): Builds one scene, points the wrist camera at one cube, detects it, and records error.
# - setup_scene(): Creates a fresh DIRECT scene with one Panda and one colored cube.
# - detect_cube_world(): Runs the same RGBD, color mask, and depth-cluster path used by picking.
# - write_results(): Writes per-case detection offsets to CSV.
# - write_report(): Writes a short Markdown summary with average/max errors.
# - plot_offsets(): Saves a top-down arrow plot from actual cube centers to detected centers.

import csv
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pybullet as pyb
import pybullet_data

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_colored_cube, save_color_detection_debug
from src.perception.depth_cluster import mask_to_world_cluster
from src.sim.robot_control import configure_gripper_friction, move_arm_to_home, move_ee_to_position, open_gripper, step_simulation
from src.sim.scene_objects import CUBE_COLORS, CUBE_Z, create_colored_cube


OUTPUT_ROOT = Path("outputs/detection_offset")
TEST_COLORS = list(CUBE_COLORS)
TEST_POSITIONS = {
    "center": (0.48, 0.00, CUBE_Z),
    "left": (0.48, 0.20, CUBE_Z),
    "right": (0.48, -0.20, CUBE_Z),
}
CAMERA_ABOVE_CUBE_Z = 0.30


def main():
    output_dir = make_output_dir()
    results = []

    for color in TEST_COLORS:
        for position_name, cube_position in TEST_POSITIONS.items():
            results.append(run_case(color, position_name, cube_position, output_dir))

    write_results(results, output_dir)
    write_report(results, output_dir)
    plot_offsets(results, output_dir)
    print(f"Detection offset results: {output_dir}")


def make_output_dir():
    output_dir = OUTPUT_ROOT / datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def run_case(color, position_name, cube_position, output_dir):
    panda_id, cube_id = setup_scene(color, cube_position)
    target = [cube_position[0], cube_position[1], cube_position[2] + CAMERA_ABOVE_CUBE_Z]

    move_ee_to_position(panda_id, target)
    step_simulation(seconds=1.5)

    detected, confidence = detect_cube_world(panda_id, color, output_dir / f"{position_name}_{color}.png")
    actual = pyb.getBasePositionAndOrientation(cube_id)[0]
    pyb.disconnect()

    error = None if detected is None else [detected[index] - actual[index] for index in range(3)]
    return {
        "color": color,
        "position_name": position_name,
        "actual": actual,
        "detected": detected,
        "confidence": confidence,
        "error": error,
    }


def setup_scene(color, cube_position):
    pyb.connect(pyb.DIRECT)
    pyb.resetSimulation()
    pyb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pyb.setGravity(0, 0, -9.81)
    pyb.loadURDF("plane.urdf")

    panda_id = pyb.loadURDF("franka_panda/panda.urdf", basePosition=[0, 0, 0], useFixedBase=True)
    cube_id, _ = create_colored_cube(color, cube_position)
    configure_gripper_friction(panda_id)

    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
    open_gripper(panda_id)
    step_simulation(seconds=0.5)
    return panda_id, cube_id


def detect_cube_world(panda_id, color, debug_path):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_colored_cube(rgb, color)
    if detection is None:
        save_color_detection_debug(rgb, detection, color, debug_path)
        return None, None

    world = mask_to_world_cluster(mask, depth, view_matrix, projection_matrix, rgb.shape)
    detection["world"] = world if world is not None else [0, 0, 0]
    save_color_detection_debug(rgb, detection, color, debug_path)
    return world, detection["confidence"]


def write_results(results, output_dir):
    path = output_dir / "detection_offsets.csv"
    with path.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "color",
                "position",
                "actual_x",
                "actual_y",
                "actual_z",
                "detected_x",
                "detected_y",
                "detected_z",
                "error_x",
                "error_y",
                "error_z",
                "error_xy",
                "error_xyz",
                "confidence",
            ]
        )
        for result in results:
            writer.writerow(result_row(result))


def result_row(result):
    actual = result["actual"]
    detected = ["", "", ""] if result["detected"] is None else result["detected"]
    error = ["", "", ""] if result["error"] is None else result["error"]
    error_xy = "" if result["error"] is None else (error[0] ** 2 + error[1] ** 2) ** 0.5
    error_xyz = "" if result["error"] is None else sum(value**2 for value in error) ** 0.5
    return [
        result["color"],
        result["position_name"],
        *actual,
        *detected,
        *error,
        error_xy,
        error_xyz,
        result["confidence"] or "",
    ]


def write_report(results, output_dir):
    good = [result for result in results if result["error"] is not None]
    xy_errors = [((r["error"][0] ** 2 + r["error"][1] ** 2) ** 0.5) for r in good]
    xyz_errors = [(sum(value**2 for value in r["error"]) ** 0.5) for r in good]

    with (output_dir / "report.md").open("w") as file:
        file.write("# Detection Offset Report\n\n")
        file.write(f"- Cases: {len(results)}\n")
        file.write(f"- Detections: {len(good)}\n")
        file.write(f"- Misses: {len(results) - len(good)}\n")
        if good:
            file.write(f"- Average XY error: {sum(xy_errors) / len(xy_errors):.4f} m\n")
            file.write(f"- Max XY error: {max(xy_errors):.4f} m\n")
            file.write(f"- Average XYZ error: {sum(xyz_errors) / len(xyz_errors):.4f} m\n")
            file.write(f"- Max XYZ error: {max(xyz_errors):.4f} m\n")


def plot_offsets(results, output_dir):
    plotted = [result for result in results if result["detected"] is not None]
    if not plotted:
        return

    for result in plotted:
        actual = result["actual"]
        detected = result["detected"]
        plt.scatter(actual[0], actual[1], c="black", marker="x")
        plt.arrow(actual[0], actual[1], detected[0] - actual[0], detected[1] - actual[1], head_width=0.01)
        plt.text(actual[0], actual[1], f"{result['color']} {result['position_name']}", fontsize=7)

    plt.title("Detection offset: actual cube center -> detected world point")
    plt.xlabel("world x")
    plt.ylabel("world y")
    plt.grid(True)
    plt.axis("equal")
    plt.savefig(output_dir / "offset_plot.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    main()
