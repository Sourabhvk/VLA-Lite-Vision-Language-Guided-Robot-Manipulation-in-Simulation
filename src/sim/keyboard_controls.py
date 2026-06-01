import pybullet as pyb
import time

from src.perception.camera import save_rgb_frame
from src.perception.object_localizer import localize_red_cube
from src.perception.vision_routines import vision_pick_and_place_red_cube
from src.sim.camera_controls import set_camera_view
from src.language.simple_parser import parse_command
from src.sim.logging_utils import log
from src.sim.routines import APPROACH_HEIGHT_OFFSET, TRAY_DROP_HEIGHT_OFFSET, pick_and_place
from src.sim.robot_control import (
    close_gripper,
    move_ee_to_position,
    move_ee_up,
    move_arm_to_home,
    open_gripper,
)
from src.sim.scene_registry import get_object_position


def run_text_command(panda_id, command):
    task = parse_command(command)
    print(task)

    # Bridge structured commands to the current scene registry names.
    source = f"{task['source']['color']}_{task['source']['type']}"
    target = f"{task['target']['color']}_{task['target']['type']}"
    pick_and_place(
        panda_id,
        get_object_position(source),
        get_object_position(target),
    )


def key_pressed(keys, key):
    key_code = ord(key)
    return key_code in keys and keys[key_code] & pyb.KEY_WAS_TRIGGERED


def handle_keyboard_controls(panda_id):
    keys = pyb.getKeyboardEvents()

    if key_pressed(keys, "h"):
        log("Keyboard: home pose")
        move_arm_to_home(panda_id)

    if key_pressed(keys, "o"):
        log("Keyboard: open gripper")
        open_gripper(panda_id)

    if key_pressed(keys, "c"):
        log("Keyboard: close gripper")
        close_gripper(panda_id)

    if key_pressed(keys, "f"):
        log("Keyboard: front camera")
        set_camera_view("front")

    if key_pressed(keys, "v"):
        log("Keyboard: side camera")
        set_camera_view("side")

    if key_pressed(keys, "t"):
        log("Keyboard: top camera")
        set_camera_view("top")

    if key_pressed(keys, "u"):
        log("Keyboard: lift gripper")
        move_ee_up(panda_id)

    if key_pressed(keys, "b"):
        tray_position = get_object_position("blue_tray")
        target_position = [
            tray_position[0],
            tray_position[1],
            tray_position[2] + APPROACH_HEIGHT_OFFSET,
        ]
        log(f"Keyboard: move above blue tray {target_position}")
        move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "d"):
        tray_position = get_object_position("blue_tray")
        target_position = [
            tray_position[0],
            tray_position[1],
            tray_position[2] + TRAY_DROP_HEIGHT_OFFSET,
        ]
        log(f"Keyboard: lower toward blue tray {target_position}")
        move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "i"):
        save_rgb_frame(panda_id)

    if key_pressed(keys, "y"):
        localize_red_cube(panda_id)

    if key_pressed(keys, "q"):
        cube_position = localize_red_cube(panda_id)
        if cube_position is not None:
            target_position = [
                cube_position[0],
                cube_position[1],
                cube_position[2] + APPROACH_HEIGHT_OFFSET,
            ]
            move_ee_to_position(panda_id, target_position)

    if key_pressed(keys, "j"):
        vision_pick_and_place_red_cube(panda_id)

    if key_pressed(keys, "m"):
        run_text_command(panda_id, "pick red cube and place in blue tray")

    if key_pressed(keys, "p"):
        print("Command prompt opening in 1 second...")
        time.sleep(1.0)
        command = input("Command > ")
        run_text_command(panda_id, command)
