# File: src/sim/routines.py
# Intent: Contains the basic scripted pick-and-place motion sequence.
# Usage: Used by manual tests and non-vision benchmark runs.
# Presets: approach, pre-grasp, grasp, and tray drop z offsets plus timing sleeps.
# Connects: src/sim/robot_control.py; testing/test_pick_place_100.py.
# User values: source_position and target_position passed by caller.
#
# Functions:
# - pick_and_place(): Moves above source, grasps, lifts, moves to tray, drops, and releases.

from src.sim.robot_control import (
    close_gripper,
    move_ee_to_position,
    open_gripper,
    step_simulation,
)

APPROACH_HEIGHT_OFFSET = 0.25
PRE_GRASP_HEIGHT_OFFSET = 0.08
GRASP_Z_OFFSET = 0.0
TRAY_DROP_HEIGHT_OFFSET = 0.08


# Scripted pick and place, used by keyboard controls and command parsing.
def pick_and_place(panda_id, source_position, target_position):
    source_above = [
        source_position[0],
        source_position[1],
        source_position[2] + APPROACH_HEIGHT_OFFSET,
    ]
    source_pre_grasp = [
        source_position[0],
        source_position[1],
        source_position[2] + PRE_GRASP_HEIGHT_OFFSET,
    ]
    source_grasp = [
        source_position[0],
        source_position[1],
        source_position[2] + GRASP_Z_OFFSET,
    ]
    target_above = [
        target_position[0],
        target_position[1],
        target_position[2] + APPROACH_HEIGHT_OFFSET,
    ]
    target_drop = [
        target_position[0],
        target_position[1],
        target_position[2] + TRAY_DROP_HEIGHT_OFFSET,
    ]

    move_ee_to_position(panda_id, source_above)
    step_simulation(seconds=1.2)

    move_ee_to_position(panda_id, source_pre_grasp)
    step_simulation(seconds=0.8)

    move_ee_to_position(panda_id, source_grasp)
    step_simulation(seconds=1.0)

    close_gripper(panda_id)
    step_simulation(seconds=0.8)

    move_ee_to_position(panda_id, source_above)
    step_simulation(seconds=1.2)

    move_ee_to_position(panda_id, target_above)
    step_simulation(seconds=1.5)

    move_ee_to_position(panda_id, target_drop)
    step_simulation(seconds=1.0)

    open_gripper(panda_id)
    step_simulation(seconds=0.8)
