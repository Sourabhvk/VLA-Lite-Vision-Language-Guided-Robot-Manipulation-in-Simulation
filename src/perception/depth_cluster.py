# File: src/perception/depth_cluster.py
# Intent: Converts detected mask pixels into a stable 3D world-space grasp center.
# Usage: Used after color detection to localize a cube from depth data.
# Presets: MAX_CLUSTER_PIXELS limits projection work for large masks.
# Connects: src/perception/camera.py; src/perception/object_localizer.py.
# User values: None.
#
# Functions:
# - mask_to_world_cluster(): Samples valid mask pixels, projects them, and returns a grasp-center estimate.
# - mask_to_world_points(): Projects valid depth pixels from a mask into world-space points.
# - estimate_grasp_center(): Moves from visible surface center toward the cube body.
# - trim_outliers(): Removes edge/depth noise before center estimation.

import numpy as np

from src.perception.camera import camera_position_from_view_matrix, pixel_to_world


MAX_CLUSTER_PIXELS = 800
INSET_RATIO = 0.35
MIN_CENTER_INSET = 0.012
MAX_CENTER_INSET = 0.035


def mask_to_world_cluster(mask, depth, view_matrix, projection_matrix, image_shape):
    points = mask_to_world_points(mask, depth, view_matrix, projection_matrix, image_shape)
    if len(points) == 0:
        return None

    camera_position = camera_position_from_view_matrix(view_matrix)
    return estimate_grasp_center(points, camera_position)


def mask_to_world_points(mask, depth, view_matrix, projection_matrix, image_shape):
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return np.empty((0, 3))

    # Use a spread-out sample so large masks do not make localization slow.
    sample_step = max(1, len(xs) // MAX_CLUSTER_PIXELS)
    xs = xs[::sample_step]
    ys = ys[::sample_step]

    points = []
    for x, y in zip(xs, ys):
        # Skip invalid far-plane pixels.
        if depth[y, x] >= 0.999:
            continue
        points.append(pixel_to_world((int(x), int(y)), depth, view_matrix, projection_matrix, image_shape))

    return np.array(points)


def estimate_grasp_center(points, camera_position):
    points = trim_outliers(points)
    visible_center = np.median(points, axis=0)

    # The visible mask is often the near face; shift inward along the camera ray.
    view_xy = visible_center[:2] - camera_position[:2]
    view_norm = np.linalg.norm(view_xy)
    if view_norm == 0:
        return visible_center

    spread_xy = np.ptp(points[:, :2], axis=0)
    inset = np.clip(np.linalg.norm(spread_xy) * INSET_RATIO, MIN_CENTER_INSET, MAX_CENTER_INSET)
    grasp_center = visible_center.copy()
    grasp_center[:2] += (view_xy / view_norm) * inset
    return grasp_center


def trim_outliers(points):
    if len(points) < 8:
        return points

    lower = np.percentile(points, 10, axis=0)
    upper = np.percentile(points, 90, axis=0)
    keep = np.all((points >= lower) & (points <= upper), axis=1)
    trimmed = points[keep]
    return trimmed if len(trimmed) else points
