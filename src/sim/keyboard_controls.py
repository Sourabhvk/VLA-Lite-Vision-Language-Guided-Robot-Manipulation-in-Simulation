import pybullet as pyb

from src.sim.camera_controls import set_camera_view
from src.sim.robot_control import (
    close_gripper,
    enter_manual_mode,
    exit_manual_mode,
    move_ee_to_position,
    move_ee_up,
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

    if ord("f") in keys and keys[ord("f")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: front camera")
        set_camera_view("front")

    if ord("v") in keys and keys[ord("v")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: side camera")
        set_camera_view("side")

    if ord("t") in keys and keys[ord("t")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: top camera")
        set_camera_view("top")

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
            RED_CUBE_POSITION[2] + 0.0, 
            #For the PyBullet Franka Panda specifically, link
            #index 11 is commonly treated as the Panda 
            #end-effector/grasp target link.
        ]
        print(f"Keyboard: lower toward cube {target_position}")
        exit_manual_mode(panda_id)
        manual_mode_active = False
        move_ee_to_position(panda_id, target_position)

    if ord("u") in keys and keys[ord("u")] & pyb.KEY_WAS_TRIGGERED:
        print("Keyboard: lift gripper")
        exit_manual_mode(panda_id)
        manual_mode_active = False
        move_ee_up(panda_id)

    for arm_joint_number in range(1, 8):
        key = ord(str(arm_joint_number))
        if key in keys and keys[key] & pyb.KEY_WAS_TRIGGERED:
            print(f"Keyboard: nudge joint {arm_joint_number}")
            nudge_arm_joint(panda_id, arm_joint_number)
