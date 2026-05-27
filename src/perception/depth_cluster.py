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
