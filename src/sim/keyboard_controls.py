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


APPROACH_HEIGHT_OFFSET = 0.25


def key_pressed(keys, key):
    key_code = ord(key)
    return key_code in keys and keys[key_code] & pyb.KEY_WAS_TRIGGERED


def handle_keyboard_controls(panda_id):
    keys = pyb.getKeyboardEvents()

    if key_pressed(keys, "h"):
        print("Keyboard: home pose")
        move_arm_to_home(panda_id)

    if key_pressed(keys, "o"):
        print("Keyboard: open gripper")
        open_gripper(panda_id)

    if key_pressed(keys, "c"):
        print("Keyboard: close gripper")
        close_gripper(panda_id)

    if key_pressed(keys, "f"):
        print("Keyboard: front camera")
        set_camera_view("front")

    if key_pressed(keys, "v"):
        print("Keyboard: side camera")
        set_camera_view("side")

    if key_pressed(keys, "t"):
        print("Keyboard: top camera")
        set_camera_view("top")

    if key_pressed(keys, "p"):
        target_position = [
            RED_CUBE_POSITION[0],
            RED_CUBE_POSITION[1],
            RED_CUBE_POSITION[2] + APPROACH_HEIGHT_OFFSET,
        ]
        print(f"Keyboard: move above cube {target_position}")
        move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "l"):
        target_position = [
            RED_CUBE_POSITION[0],
            RED_CUBE_POSITION[1],
            RED_CUBE_POSITION[2],
        ]
        print(f"Keyboard: lower toward cube {target_position}")
        move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "u"):
        print("Keyboard: lift gripper")
        move_ee_up(panda_id)
