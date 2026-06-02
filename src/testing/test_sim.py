# File: src/testing/test_sim.py
# Intent: Provides a quick gripper sanity routine for the interactive simulation.
# Usage: Called by panda_env.py when --test-gripper is enabled.
# Presets: open-close-open sequence with short simulation waits.
# Connects: src/sim/panda_env.py; src/sim/robot_control.py.
# User values: panda_id from the active scene.
#
# Functions:
# - run_gripper_test(): Opens, closes, reopens, and prints gripper joint state.

from src.sim.robot_control import (
    close_gripper,
    open_gripper,
    print_gripper_state,
    step_simulation,
)


def run_gripper_test(panda_id):
    # Quick sanity check: open, close, then open again.
    print("Gripper test: open")
    open_gripper(panda_id)
    step_simulation(seconds=3.0)
    print_gripper_state(panda_id)

    print("Gripper test: close")
    close_gripper(panda_id)
    step_simulation(seconds=3.0)
    print_gripper_state(panda_id)

    print("Gripper test: open")
    open_gripper(panda_id)
    step_simulation(seconds=3.0)
    print_gripper_state(panda_id)
