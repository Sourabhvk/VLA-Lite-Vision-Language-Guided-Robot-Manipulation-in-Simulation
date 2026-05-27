import pybullet as pyb

from src.sim.robot_control import (
    close_gripper,
    enter_manual_mode,
    exit_manual_mode,
    move_ee_to_position,
    move_arm_to_home,
    nudge_arm_joint,
    open_gripper,
)
from src.sim.scene_objects import RED_CUBE_POSITION


manual_mode_active = False


def handle_keyboard_controls(panda_id):
    global manual_mode_active

    keys = pyb.getKeyboardEvents()

    if ord("h") in keys and keys[ord("h")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: home pose")
        exit_manual_mode(panda_id)
        manual_mode_active = False
        move_arm_to_home(panda_id)

    if ord("o") in keys and keys[ord("o")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: open gripper")
        open_gripper(panda_id)

    if ord("c") in keys and keys[ord("c")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: close gripper")
        close_gripper(panda_id)

    if ord("r") in keys and keys[ord("r")] & pyb.KEY_WAS_TRIGGERED:
        if manual_mode_active:
            print("Keyboard: manual mode already active")
            return

        print("Keyboard: manual mode")
        enter_manual_mode(panda_id)
        manual_mode_active = True

    if ord("p") in keys and keys[ord("p")] & pyb.KEY_WAS_TRIGGERED:
        target_position = [
            RED_CUBE_POSITION[0],
            RED_CUBE_POSITION[1],
            RED_CUBE_POSITION[2] + 0.25,
        ]
        print(f"Keyboard: move above cube {target_position}")
        exit_manual_mode(panda_id)
        manual_mode_active = False
        move_ee_to_position(panda_id, target_position)

    if ord("l") in keys and keys[ord("l")] & pyb.KEY_WAS_TRIGGERED:
        target_position = [
            RED_CUBE_POSITION[0],
            RED_CUBE_POSITION[1],
            RED_CUBE_POSITION[2] + 0.07,
        ]
        print(f"Keyboard: lower toward cube {target_position}")
        exit_manual_mode(panda_id)
        manual_mode_active = False
        move_ee_to_position(panda_id, target_position)

    for arm_joint_number in range(1, 8):
        key = ord(str(arm_joint_number))
        if key in keys and keys[key] & pyb.KEY_WAS_TRIGGERED:
            print(f"Keyboard: nudge joint {arm_joint_number}")
            nudge_arm_joint(panda_id, arm_joint_number)
