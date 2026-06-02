# File: src/perception/object_localizer.py
# Intent: Combines camera capture, color detection, and depth clustering into cube world positions.
# Usage: Called by vision routines and manual red-cube debug controls.
# Presets: red debug localization, named color ranges, and validated HSV command ranges.
# Connects: src/perception/camera.py; color_detector.py; depth_cluster.py; vision_routines.py.
# User values: color names, hsv_ranges, label text, and save_debug flag.
#
# Functions:
# - localize_red_cube(): Localizes the red cube and saves debug imagery.
# - localize_colored_cube(): Captures RGBD and localizes a cube by named color preset.
# - localize_hsv_cube(): Captures RGBD and localizes a cube by validated HSV ranges.
# - detection_to_world(): Converts one detection mask into a world position or reports failure.

from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_colored_cube, detect_hsv_cube, save_color_detection_debug
from src.perception.depth_cluster import mask_to_world_cluster


def localize_red_cube(panda_id):
    return localize_colored_cube(panda_id, "red", save_debug=True)


def localize_colored_cube(panda_id, color, save_debug=False):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_colored_cube(rgb, color)
    return detection_to_world(rgb, depth, view_matrix, projection_matrix, detection, mask, color, save_debug)


def localize_hsv_cube(panda_id, hsv_ranges, label="requested", save_debug=False):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_hsv_cube(rgb, hsv_ranges, label)
    return detection_to_world(rgb, depth, view_matrix, projection_matrix, detection, mask, label, save_debug)


def detection_to_world(rgb, depth, view_matrix, projection_matrix, detection, mask, label, save_debug):
    if detection is None:
        print(f"No matching {label} cube found")
        if save_debug:
            save_color_detection_debug(rgb, detection, label)
        return None

    world = mask_to_world_cluster(
        mask,
        depth,
        view_matrix,
        projection_matrix,
        rgb.shape,
    )
    if world is None:
        print(f"{label.title()} cube depth cluster failed")
        if save_debug:
            save_color_detection_debug(rgb, detection, label)
        return None

    detection["world"] = world
    print(f"{label.title()} cube world position: {world}, confidence={detection['confidence']:.2f}")
    if save_debug:
        save_color_detection_debug(rgb, detection, label)
    return world
