import pybullet as pyb

ARM_JOINT_INDICES = [0, 1, 2, 3, 4, 5, 6]
GRIPPER_JOINT_INDICES = [9, 10]


def step_simulation(seconds=1.0, hz=240):
    # Motor commands need simulation steps before the robot visibly moves.
    for _ in range(int(seconds * hz)):
        pyb.stepSimulation()


def move_arm_to_home(panda_id):
    # A simple bent pose that keeps the arm away from singular straight lines.
    home_pose = [0.0, -0.6, 0.0, -2.2, 0.0, 1.6, 0.8]

    for joint_index, target_angle in zip(ARM_JOINT_INDICES, home_pose):
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=target_angle,
            force=500,
        )


def open_gripper(panda_id):
    # These joints slide the two fingers apart.
    open_gripper_width = 0.04

    for joint_index in GRIPPER_JOINT_INDICES:
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=open_gripper_width,
            force=100,
            maxVelocity=0.05,
        )


def close_gripper(panda_id):
    # Fully closed is useful for testing before we grab real objects.
    closed_gripper_width = 0.0

    for joint_index in GRIPPER_JOINT_INDICES:
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=closed_gripper_width,
            force=100,
            maxVelocity=0.05,
        )


def print_gripper_state(panda_id):
    left_finger = pyb.getJointState(panda_id, GRIPPER_JOINT_INDICES[0])[0]
    right_finger = pyb.getJointState(panda_id, GRIPPER_JOINT_INDICES[1])[0]
    print(f"Gripper joints: left={left_finger:.4f}, right={right_finger:.4f}")
