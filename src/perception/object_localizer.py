from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_colored_cube, save_color_detection_debug
from src.perception.depth_cluster import mask_to_world_cluster


def localize_red_cube(panda_id):
    return localize_colored_cube(panda_id, "red")


def localize_colored_cube(panda_id, color):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_colored_cube(rgb, color)

    if detection is None:
        print(f"{color.title()} cube not detected with enough confidence")
        save_color_detection_debug(rgb, detection, color)
        return None

    world = mask_to_world_cluster(
        mask,
        depth,
        view_matrix,
        projection_matrix,
        rgb.shape,
    )
    if world is None:
        print(f"{color.title()} cube depth cluster failed")
        save_color_detection_debug(rgb, detection, color)
        return None

    detection["world"] = world
    print(f"{color.title()} cube world position: {world}, confidence={detection['confidence']:.2f}")
    save_color_detection_debug(rgb, detection, color)
    return world
