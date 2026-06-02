# File: src/perception/multiview_localizer.py
# Intent: Builds a multi-view cube point cloud and estimates a less biased grasp center.
# Usage: Experimental perception helper; call after a rough single-view cube position is known.
# Presets: center/left/right/front inspection offsets, short settle time, cube geometry z correction.
# Connects: src/perception/camera.py; color_detector.py; depth_cluster.py; src/sim/robot_control.py.
# User values: rough_position, color or hsv_ranges, label, view offsets, and debug flag.
#
# Functions:
# - localize_colored_cube_multiview(): Scans a named-color cube from several hover poses.
# - localize_hsv_cube_multiview(): Scans a command-selected cube from several hover poses.
# - collect_multiview_points(): Moves through inspection poses and merges detected depth points.
# - capture_mask_points(): Captures one RGBD frame, detects the cube mask, and returns 3D mask points.
# - estimate_center_from_views(): Estimates cube center from the merged multi-view point cloud.
# - inspection_targets(): Builds world-space hover targets around the rough cube position.

from pathlib import Path

import numpy as np

from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_colored_cube, detect_hsv_cube, save_color_detection_debug
from src.perception.depth_cluster import mask_to_world_points, trim_outliers
from src.sim.robot_control import move_pinch_center_to_position, step_simulation
from src.sim.scene_objects import CUBE_HALF_SIZE


# These are not grasp offsets. They are camera inspection offsets around a rough cube position.
# The goal is to see different visible faces, merge their depth points, then estimate the cube center.
VIEW_OFFSETS = {
    "center": (0.00, 0.00, 0.30),
    "left": (0.00, 0.12, 0.30),
    "right": (0.00, -0.12, 0.30),
    "front": (-0.12, 0.00, 0.30),
}
SETTLE_SECONDS = 0.8
MIN_POINTS_PER_VIEW = 20


def localize_colored_cube_multiview(panda_id, color, rough_position, save_debug=False):
    points = collect_multiview_points(
        panda_id,
        rough_position,
        lambda rgb: detect_colored_cube(rgb, color),
        color,
        save_debug,
    )
    return estimate_center_from_views(points)


def localize_hsv_cube_multiview(panda_id, hsv_ranges, rough_position, label="requested", save_debug=False):
    points = collect_multiview_points(
        panda_id,
        rough_position,
        lambda rgb: detect_hsv_cube(rgb, hsv_ranges, label),
        label,
        save_debug,
    )
    return estimate_center_from_views(points)


def collect_multiview_points(panda_id, rough_position, detect_cube, label, save_debug=False):
    view_points = []

    for view_name, target in inspection_targets(rough_position).items():
        move_pinch_center_to_position(panda_id, target)
        step_simulation(seconds=SETTLE_SECONDS)

        points = capture_mask_points(panda_id, detect_cube, label, view_name, save_debug)
        if len(points) >= MIN_POINTS_PER_VIEW:
            view_points.append(points)

    if not view_points:
        return np.empty((0, 3))

    return np.vstack(view_points)


def capture_mask_points(panda_id, detect_cube, label, view_name, save_debug):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_cube(rgb)

    if detection is None:
        if save_debug:
            save_color_detection_debug(rgb, detection, label, f"outputs/multiview/{view_name}_{label}.png")
        return np.empty((0, 3))

    points = mask_to_world_points(mask, depth, view_matrix, projection_matrix, rgb.shape)

    if save_debug:
        center = estimate_center_from_views(points)
        if center is not None:
            detection["world"] = center
        path = Path("outputs/multiview") / f"{view_name}_{label}.png"
        save_color_detection_debug(rgb, detection, label, path)

    return points


def estimate_center_from_views(points):
    if len(points) == 0:
        return None

    points = trim_outliers(points)

    # Multi-view depth gives better x/y extent than one view because side faces appear from
    # different inspection angles. Use bounds here because the center of a cube is geometric,
    # not the median of whichever surface was most visible.
    lower = np.min(points, axis=0)
    upper = np.max(points, axis=0)
    center = (lower + upper) / 2

    # Depth rarely sees the bottom face of a tabletop cube. Treat the highest observed surface
    # as the top face and infer center height from known cube geometry instead of table height.
    center[2] = upper[2] - CUBE_HALF_SIZE
    return center


def inspection_targets(rough_position):
    return {
        name: [
            rough_position[0] + offset[0],
            rough_position[1] + offset[1],
            rough_position[2] + offset[2],
        ]
        for name, offset in VIEW_OFFSETS.items()
    }
