import pybullet as pyb

from src.sim.robot_control import (
    close_gripper,
    enter_manual_mode,
    exit_manual_mode,
    move_arm_to_home,
    nudge_arm_joint,
    open_gripper,
)


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

    for arm_joint_number in range(1, 8):
        key = ord(str(arm_joint_number))
        if key in keys and keys[key] & pyb.KEY_WAS_TRIGGERED:
            print(f"Keyboard: nudge joint {arm_joint_number}")
            nudge_arm_joint(panda_id, arm_joint_number)
