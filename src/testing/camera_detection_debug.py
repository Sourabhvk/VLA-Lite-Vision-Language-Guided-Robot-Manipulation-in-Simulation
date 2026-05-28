from datetime import datetime
from pathlib import Path

import cv2

from src.perception.camera import capture_rgbd
from src.perception.color_detector import detect_red_cube, save_red_detection_debug
from src.perception.depth_cluster import mask_to_world_cluster


def save_camera_detection_debug(panda_id):
    rgb, depth, view_matrix, projection_matrix = capture_rgbd(panda_id)
    detection, mask = detect_red_cube(rgb)

    if detection is not None:
        # Use the same depth-cluster localization we use before moving the robot.
        world = mask_to_world_cluster(mask, depth, view_matrix, projection_matrix, rgb.shape)
        if world is not None:
            detection["world"] = world

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = Path("outputs/testing/camera_detection")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_path = output_dir / f"wrist_rgb_{timestamp}.png"
    debug_path = output_dir / f"red_detection_{timestamp}.png"

    cv2.imwrite(str(raw_path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    save_red_detection_debug(rgb, detection, debug_path)
    print(f"Saved camera debug: {raw_path}")
