from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_red_cube, save_red_detection_debug
from src.perception.depth_cluster import mask_to_world_cluster


def localize_red_cube(panda_id):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_red_cube(rgb)

    if detection is None:
        print("Red cube not detected with enough confidence")
        save_red_detection_debug(rgb, detection)
        return None

    world = mask_to_world_cluster(
        mask,
        depth,
        view_matrix,
        projection_matrix,
        rgb.shape,
    )
    if world is None:
        print("Red cube depth cluster failed")
        save_red_detection_debug(rgb, detection)
        return None

    detection["world"] = world
    print(f"Red cube world position: {world}, confidence={detection['confidence']:.2f}")
    save_red_detection_debug(rgb, detection)
    return world
