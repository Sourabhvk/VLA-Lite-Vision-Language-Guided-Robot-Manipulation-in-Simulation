# File: src/perception/depth_cluster.py
# Intent: Converts detected mask pixels into a stable 3D world-space cube location.
# Usage: Used after color detection to localize a cube from depth data.
# Presets: MAX_CLUSTER_PIXELS limits projection work for large masks.
# Connects: src/perception/camera.py; src/perception/object_localizer.py.
# User values: None.
#
# Functions:
# - mask_to_world_cluster(): Samples valid mask pixels, projects them, and returns the median world point.

import numpy as np

from src.perception.camera import pixel_to_world


MAX_CLUSTER_PIXELS = 800


def mask_to_world_cluster(mask, depth, view_matrix, projection_matrix, image_shape):
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None

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

    if not points:
        return None

    # Median is less sensitive to noisy edge pixels than a plain average.
    return np.median(np.array(points), axis=0)
