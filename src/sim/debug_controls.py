# File: src/sim/debug_controls.py
# Intent: Resets cube/tray positions and returns the Panda arm to a known home state.
# Usage: Called by the keyboard reset hotkey during interactive simulation.
# Presets: scene sampler spacing, open gripper, and home pose reset.
# Connects: src/sim/keyboard_controls.py; scene_objects.py; scene_registry.py; robot_control.py.
# User values: cube_ids, cube_names, and tray_id from the active PyBullet scene.
#
# Functions:
# - reset_scene_and_home(): Resamples scene objects, updates the registry, opens gripper, and homes the arm.

import pybullet as pyb

from src.sim.robot_control import move_arm_to_home, open_gripper, step_simulation
from src.sim.scene_objects import sample_scene_positions
from src.sim.scene_registry import set_object_position


def reset_scene_and_home(panda_id, cube_ids, cube_names, tray_id):
    cube_positions, tray_position = sample_scene_positions(len(cube_ids) - 1)

    for cube_id, cube_name, cube_position in zip(cube_ids, cube_names, cube_positions):
        pyb.resetBasePositionAndOrientation(cube_id, cube_position, [0, 0, 0, 1])
        pyb.resetBaseVelocity(cube_id, [0, 0, 0], [0, 0, 0])
        set_object_position(f"{cube_name}_cube", cube_position)

    pyb.resetBasePositionAndOrientation(tray_id, tray_position, [0, 0, 0, 1])
    set_object_position("blue_tray", tray_position)

    open_gripper(panda_id)
    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
    print("Randomized scene and sent robot home")
