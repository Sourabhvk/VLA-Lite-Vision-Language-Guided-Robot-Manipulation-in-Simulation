# File: src/sim/robot_control.py
# Intent: Provides low-level Panda arm, gripper, speed, and simulation stepping controls.
# Usage: Shared by startup, scripted routines, keyboard controls, tests, and vision routines.
# Presets: joint indices, home pose, gripper widths, motor forces, friction, default speeds.
# Connects: config/robot_speeds.txt; src/sim/ik_solver.py; PyBullet joint motor APIs.
# User values: home_max_velocity, ik_max_velocity, gripper_max_velocity.
#
# Functions:
# - load_speed_config(): Loads local speed overrides from config/robot_speeds.txt.
# - step_simulation(): Advances PyBullet for a requested duration and step rate.
# - move_arm_to_home(): Sends the Panda arm to the configured home joint pose.
# - configure_gripper_friction(): Applies lateral friction to the gripper finger joints.
# - move_ee_to_position(): Solves IK and commands arm joints toward a world target.
# - gripper_pinch_center(): Measures the midpoint between the two finger links.
# - move_pinch_center_to_position(): Iteratively corrects motion so the pinch center reaches target.
# - move_ee_up(): Raises the end effector by a requested distance.
# - set_gripper_width(): Commands both finger joints to a target opening width.
# - open_gripper(): Opens fingers to the configured open width.
# - close_gripper(): Closes fingers to the configured closed width.
# - print_gripper_state(): Prints current finger joint positions for debugging.

from pathlib import Path

import pybullet as pyb

ARM_JOINT_INDICES = [0, 1, 2, 3, 4, 5, 6]
GRIPPER_JOINT_INDICES = [9, 10]
END_EFFECTOR_LINK_INDEX = 11
HOME_POSE = [0.0, -0.6, 0.0, -2.2, 0.0, 1.6, 0.8]
OPEN_GRIPPER_WIDTH = 0.04
CLOSED_GRIPPER_WIDTH = 0.0
ARM_MOTOR_FORCE = 500
GRIPPER_MOTOR_FORCE = 200
FINGER_LATERAL_FRICTION = 2.0

DEFAULT_SPEEDS = {
    "home_max_velocity": 0.25,
    "ik_max_velocity": 0.25,
    "gripper_max_velocity": 0.02,
}


def load_speed_config():
    config_path = Path(__file__).resolve().parents[2] / "config" / "robot_speeds.txt"
    speeds = DEFAULT_SPEEDS.copy()

    if not config_path.exists():
        return speeds

    for line in config_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if key in speeds:
            speeds[key] = float(value.strip())

    return speeds


SPEEDS = load_speed_config()


def step_simulation(seconds=1.0, hz=240):
    # Motor commands need simulation steps before the robot visibly moves.
    for _ in range(int(seconds * hz)):
        pyb.stepSimulation()


def move_arm_to_home(panda_id):
    # A simple bent pose that keeps the arm away from singular straight lines.
    for joint_index, target_angle in zip(ARM_JOINT_INDICES, HOME_POSE):
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=target_angle,
            force=ARM_MOTOR_FORCE,
            maxVelocity=SPEEDS["home_max_velocity"],
        )


def configure_gripper_friction(panda_id):
    for joint_index in GRIPPER_JOINT_INDICES:
        pyb.changeDynamics(
            panda_id,
            joint_index,
            lateralFriction=FINGER_LATERAL_FRICTION,
        )


def move_ee_to_position(panda_id, target_position):
    from src.sim.ik_solver import solve_panda_ik

    joint_targets = solve_panda_ik(panda_id, target_position)

    for joint_index, target_angle in zip(ARM_JOINT_INDICES, joint_targets):
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=target_angle,
            force=ARM_MOTOR_FORCE,
            maxVelocity=SPEEDS["ik_max_velocity"],
        )


def gripper_pinch_center(panda_id):
    left = pyb.getLinkState(panda_id, GRIPPER_JOINT_INDICES[0])[0]
    right = pyb.getLinkState(panda_id, GRIPPER_JOINT_INDICES[1])[0]
    return [(left[index] + right[index]) / 2 for index in range(3)]


def move_pinch_center_to_position(panda_id, target_position, iterations=3, settle_seconds=0.35):
    ee_target = list(target_position)
    good_target = ee_target
    best_error = None
    for _ in range(iterations):
        move_ee_to_position(panda_id, ee_target)
        step_simulation(seconds=settle_seconds)
        pinch = gripper_pinch_center(panda_id)
        error = [target_position[index] - pinch[index] for index in range(3)]
        error_size = error[0] ** 2 + error[1] ** 2
        if best_error is not None and error_size >= best_error:
            move_ee_to_position(panda_id, good_target)
            step_simulation(seconds=settle_seconds)
            break
        best_error = error_size
        good_target = ee_target
        # IK can jump if the correction is too large; keep each refinement local.
        ee_target = [
            ee_target[0] + max(-0.02, min(0.02, error[0])),
            ee_target[1] + max(-0.02, min(0.02, error[1])),
            ee_target[2],
        ]


def move_ee_up(panda_id, distance=0.25):
    ee_state = pyb.getLinkState(panda_id, END_EFFECTOR_LINK_INDEX)
    current_position = ee_state[0]
    target_position = [
        current_position[0],
        current_position[1],
        current_position[2] + distance,
    ]

    move_ee_to_position(panda_id, target_position)


def set_gripper_width(panda_id, target_width):
    for joint_index in GRIPPER_JOINT_INDICES:
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=target_width,
            force=GRIPPER_MOTOR_FORCE,
            maxVelocity=SPEEDS["gripper_max_velocity"],
        )


def open_gripper(panda_id):
    # These joints slide the two fingers apart.
    set_gripper_width(panda_id, OPEN_GRIPPER_WIDTH)


def close_gripper(panda_id):
    # Fully closed is useful for testing before we grab real objects.
    set_gripper_width(panda_id, CLOSED_GRIPPER_WIDTH)


def print_gripper_state(panda_id):
    left_finger = pyb.getJointState(panda_id, GRIPPER_JOINT_INDICES[0])[0]
    right_finger = pyb.getJointState(panda_id, GRIPPER_JOINT_INDICES[1])[0]
    print(f"Gripper joints: left={left_finger:.4f}, right={right_finger:.4f}")
