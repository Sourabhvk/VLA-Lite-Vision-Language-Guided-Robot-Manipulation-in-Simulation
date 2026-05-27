import pybullet as pyb

from src.sim.camera_controls import set_camera_view
from src.sim.robot_control import (
    close_gripper,
    move_ee_to_position,
    move_ee_up,
    move_arm_to_home,
    open_gripper,
)
from src.sim.scene_objects import RED_CUBE_POSITION


def handle_keyboard_controls(panda_id):
    keys = pyb.getKeyboardEvents()

    if ord("h") in keys and keys[ord("h")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: home pose")
        move_arm_to_home(panda_id)

    if ord("o") in keys and keys[ord("o")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: open gripper")
        open_gripper(panda_id)

    if ord("c") in keys and keys[ord("c")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: close gripper")
        close_gripper(panda_id)

    if ord("f") in keys and keys[ord("f")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: front camera")
        set_camera_view("front")

    if ord("v") in keys and keys[ord("v")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: side camera")
        set_camera_view("side")

    if ord("t") in keys and keys[ord("t")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: top camera")
        set_camera_view("top")

    if ord("p") in keys and keys[ord("p")] & pyb.KEY_WAS_TRIGGERED:
        target_position = [
            RED_CUBE_POSITION[0],
            RED_CUBE_POSITION[1],
            RED_CUBE_POSITION[2] + 0.25,
        ]
        print(f"Keyboard: move above cube {target_position}")
        move_ee_to_position(panda_id, target_position)

    if ord("l") in keys and keys[ord("l")] & pyb.KEY_WAS_TRIGGERED:
        target_position = [
            RED_CUBE_POSITION[0],
            RED_CUBE_POSITION[1],
            RED_CUBE_POSITION[2],
        ]
        print(f"Keyboard: lower toward cube {target_position}")
        move_ee_to_position(panda_id, target_position)

    if ord("u") in keys and keys[ord("u")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: lift gripper")
        move_ee_up(panda_id)
