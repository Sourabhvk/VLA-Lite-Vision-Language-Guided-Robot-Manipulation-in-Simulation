# File: src/sim/panda_env.py
# Intent: Starts the PyBullet Panda scene and runs the interactive robot control loop.
# Usage: Main entry point via python -m src.sim.panda_env or VS Code debug launch.
# Presets: GUI mode, front camera, one extra cube by default, Panda URDF, plane, blue tray.
# Connects: keyboard_controls.py; scene_objects.py; robot_control.py; camera_controls.py; failsafe.py.
# User values: --test-gripper, --verbose, --extra-cubes, and config/robot_speeds.txt.
#
# Functions:
# - build_cube_names(): Combines fixed color cubes with requested random distractor names.
# - spawn_cubes(): Samples positions, creates cubes, and records them in the scene registry.
# - disable_pybullet_profiling(): Disables PyBullet profiling when the local build exposes that flag.
# - remove_pybullet_timing_dumps(): Removes PyBullet timings_*.json files from the workspace root.
# - main(): Parses CLI flags, creates the scene, initializes the arm, and runs the GUI loop.

import argparse
from pathlib import Path
import time

import pybullet as pyb
import pybullet_data

from src.sim.camera_controls import set_camera_view
from src.sim.failsafe import has_interference, stop_robot
from src.sim.keyboard_controls import handle_keyboard_controls
from src.sim.logging_utils import set_verbose
from src.sim.robot_control import (
    configure_gripper_friction,
    move_arm_to_home,
    open_gripper,
    step_simulation,
)
from src.sim.scene_objects import (
    DEFAULT_CUBE_NAMES,
    create_blue_tray,
    create_colored_cube,
    sample_scene_positions,
)
from src.sim.scene_registry import set_object_position
from src.testing.test_sim import run_gripper_test


TIMING_DUMP_PATTERN = "timings_*.json"


def build_cube_names(extra_cube_count):
    random_names = [f"random_{index + 1}" for index in range(extra_cube_count)]
    return DEFAULT_CUBE_NAMES + random_names


def spawn_cubes(cube_names):
    cube_positions, tray_position = sample_scene_positions(len(cube_names) - 1)
    cube_ids = []

    for cube_name, cube_position in zip(cube_names, cube_positions):
        cube_id, cube_position = create_colored_cube(cube_name, cube_position)
        cube_ids.append(cube_id)
        set_object_position(f"{cube_name}_cube", cube_position)

    return cube_ids, tray_position


def disable_pybullet_profiling():
    # We do not use PyBullet's internal timing dumps; they are noisy and can stall.
    if hasattr(pyb, "COV_ENABLE_PROFILE_TIMINGS"):
        pyb.configureDebugVisualizer(pyb.COV_ENABLE_PROFILE_TIMINGS, 0)


def remove_pybullet_timing_dumps():
    for path in Path.cwd().glob(TIMING_DUMP_PATTERN):
        try:
            path.unlink()
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-gripper",
        action="store_true",
        help="Run a simple open-close-open gripper test.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print joint metadata and keyboard action logs.",
    )
    parser.add_argument(
        "--extra-cubes",
        type=int,
        default=1,
        help="Spawn this many random distractor cubes in addition to the fixed color cubes.",
    )
    args = parser.parse_args()
    set_verbose(args.verbose)
    remove_pybullet_timing_dumps()

    # Use GUI for now so we can actually see what the robot is doing.
    pyb.connect(pyb.GUI)
    disable_pybullet_profiling()

    # Start the debug camera at a useful angle for this tabletop scene.
    set_camera_view("front")

    # Lets PyBullet find built-in URDFs like the plane and Franka Panda.
    pyb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pyb.setGravity(0, 0, -9.81)

    plane_id = pyb.loadURDF("plane.urdf")

    # Fixed base keeps the arm bolted to the table/world.
    panda_id = pyb.loadURDF(
        "franka_panda/panda.urdf",
        basePosition=[0, 0, 0],
        useFixedBase=True,
    )

    # Promptable colors spawn first; extras are random visual distractors.
    cube_names = build_cube_names(args.extra_cubes)
    cube_ids, tray_position = spawn_cubes(cube_names)
    cube_id = cube_ids[cube_names.index("red")]
    tray_id, tray_position = create_blue_tray(tray_position)
    set_object_position("blue_tray", tray_position)
    configure_gripper_friction(panda_id)

    if args.verbose:
        num_joints = pyb.getNumJoints(panda_id)
        print(f"Panda loaded with {num_joints} joints")

        for joint_index in range(num_joints):
            joint_info = pyb.getJointInfo(panda_id, joint_index)
            joint_name = joint_info[1].decode("utf-8")
            joint_type = joint_info[2]
            print(joint_index, joint_name, joint_type)

    print("Scene loaded. Starting motion in 5 seconds...")
    step_simulation(seconds=5.0)

    move_arm_to_home(panda_id)
    step_simulation(seconds=2.0)

    open_gripper(panda_id)
    step_simulation(seconds=1.5)

    if args.test_gripper:
        run_gripper_test(panda_id)

    # PyBullet does not run physics unless we step it.
    try:
        while True:
            handle_keyboard_controls(panda_id, cube_ids, cube_names, tray_id)
            if has_interference(panda_id, cube_id, tray_id, plane_id):
                print("Failsafe: interference detected, stopping robot")
                stop_robot(panda_id)
            pyb.stepSimulation()
            time.sleep(1.0 / 240.0)
    except KeyboardInterrupt:
        pyb.disconnect()
    finally:
        remove_pybullet_timing_dumps()


if __name__ == "__main__":
    main()
