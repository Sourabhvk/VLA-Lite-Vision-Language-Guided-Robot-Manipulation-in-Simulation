from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pybullet as pyb

from src.sim.robot_control import END_EFFECTOR_LINK_INDEX


IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
CAMERA_FOV = 60
CAMERA_WORLD_OFFSET = [0.12, 0.0, 0.12]
CAMERA_LOOK_OFFSET = [0.18, 0.0, -0.28]
CAMERA_UP = [0, 0, 1]


def get_wrist_camera_pose(panda_id):
    link_state = pyb.getLinkState(panda_id, END_EFFECTOR_LINK_INDEX)
    position = np.array(link_state[0])

    # Follow the wrist from the tuned camera mount.
    eye = position + np.array(CAMERA_WORLD_OFFSET)
    target = position + np.array(CAMERA_LOOK_OFFSET)
    return eye.tolist(), target.tolist(), CAMERA_UP


def capture_rgbd(panda_id, width=IMAGE_WIDTH, height=IMAGE_HEIGHT):
    eye, target, up = get_wrist_camera_pose(panda_id)

    view_matrix = pyb.computeViewMatrix(
        cameraEyePosition=eye,
        cameraTargetPosition=target,
        cameraUpVector=up,
    )
    projection_matrix = pyb.computeProjectionMatrixFOV(
        fov=CAMERA_FOV,
        aspect=width / height,
        nearVal=0.01,
        farVal=2.0,
    )

    _, _, rgba, depth, _ = pyb.getCameraImage(
        width,
        height,
        viewMatrix=view_matrix,
        projectionMatrix=projection_matrix,
        renderer=pyb.ER_BULLET_HARDWARE_OPENGL,
    )

    # PyBullet gives RGBA; OpenCV/color detection usually wants RGB/BGR.
    rgb = np.array(rgba, dtype=np.uint8).reshape(height, width, 4)[:, :, :3]
    depth = np.array(depth).reshape(height, width)
    return rgb, depth, view_matrix, projection_matrix


def pixel_to_world(pixel, depth, view_matrix, projection_matrix, image_shape):
    x, y = pixel
    height, width = image_shape[:2]

    # PyBullet depth is an OpenGL z-buffer value in [0, 1].
    z_buffer = depth[y, x]

    # Convert pixel coordinates into normalized device coordinates.
    ndc_x = (2.0 * x / width) - 1.0
    ndc_y = 1.0 - (2.0 * y / height)
    ndc_z = (2.0 * z_buffer) - 1.0

    clip_space_point = np.array([ndc_x, ndc_y, ndc_z, 1.0])
    view_matrix = np.array(view_matrix).reshape(4, 4, order="F")
    projection_matrix = np.array(projection_matrix).reshape(4, 4, order="F")

    # Reverse projection and view transforms to get a PyBullet world point.
    world_point = np.linalg.inv(projection_matrix @ view_matrix) @ clip_space_point
    world_point /= world_point[3]
    return world_point[:3]


def save_rgb_frame(panda_id, path=None):
    rgb, _, _, _ = capture_rgbd(panda_id)
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = f"outputs/wrist_camera_rgb_{timestamp}.png"

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # cv2.imwrite expects BGR, so convert before saving.
    cv2.imwrite(str(output_path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    print(f"Saved camera frame: {output_path}")
