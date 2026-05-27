from pathlib import Path

import pybullet as pyb

ARM_JOINT_INDICES = [0, 1, 2, 3, 4, 5, 6]
GRIPPER_JOINT_INDICES = [9, 10]
END_EFFECTOR_LINK_INDEX = 11
HOME_POSE = [0.0, -0.6, 0.0, -2.2, 0.0, 1.6, 0.8]
OPEN_GRIPPER_WIDTH = 0.04
CLOSED_GRIPPER_WIDTH = 0.0
ARM_MOTOR_FORCE = 500
GRIPPER_MOTOR_FORCE = 100

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


def move_ee_to_position(panda_id, target_position):
    # IK converts a gripper target position into arm joint targets.
    # This keeps the wrist pointing down instead of inheriting a random pose.
    gripper_orientation = pyb.getQuaternionFromEuler([3.14159, 0, 0])
    joint_targets = pyb.calculateInverseKinematics(
        bodyUniqueId=panda_id,
        endEffectorLinkIndex=END_EFFECTOR_LINK_INDEX,
        targetPosition=target_position,
        targetOrientation=gripper_orientation,
    )

    for joint_index, target_angle in zip(ARM_JOINT_INDICES, joint_targets):
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=target_angle,
            force=ARM_MOTOR_FORCE,
            maxVelocity=SPEEDS["ik_max_velocity"],
        )


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
