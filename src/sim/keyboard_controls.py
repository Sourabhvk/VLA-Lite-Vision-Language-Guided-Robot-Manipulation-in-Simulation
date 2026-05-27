import pybullet as pyb

from src.sim.camera_controls import set_camera_view
from src.sim.contact_debug import print_contacts_for_body
from src.sim.robot_control import (
    close_gripper,
    move_ee_to_position,
    move_ee_up,
    move_arm_to_home,
    open_gripper,
)
from src.sim.scene_objects import BLUE_TRAY_POSITION, RED_CUBE_POSITION


APPROACH_HEIGHT_OFFSET = 0.25


def key_pressed(keys, key):
    key_code = ord(key)
    return key_code in keys and keys[key_code] & pyb.KEY_WAS_TRIGGERED


def handle_keyboard_controls(panda_id, cube_id=None):
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

    if key_pressed(keys, "b"):
        target_position = [
            BLUE_TRAY_POSITION[0],
            BLUE_TRAY_POSITION[1],
            BLUE_TRAY_POSITION[2] + APPROACH_HEIGHT_OFFSET,
        ]
        print(f"Keyboard: move above blue tray {target_position}")
        move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "d"):
        target_position = [
            BLUE_TRAY_POSITION[0],
            BLUE_TRAY_POSITION[1],
            BLUE_TRAY_POSITION[2] + 0.08,
        ]
        print(f"Keyboard: lower toward blue tray {target_position}")
        move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "x"):
        print_contacts_for_body(panda_id, "Panda")
        if cube_id is not None:
            print_contacts_for_body(cube_id, "Red cube")
