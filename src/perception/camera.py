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
    return rgb, depth


def save_rgb_frame(panda_id, path=None):
    rgb, _ = capture_rgbd(panda_id)
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = f"outputs/wrist_camera_rgb_{timestamp}.png"

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # cv2.imwrite expects BGR, so convert before saving.
    cv2.imwrite(str(output_path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    print(f"Saved camera frame: {output_path}")
