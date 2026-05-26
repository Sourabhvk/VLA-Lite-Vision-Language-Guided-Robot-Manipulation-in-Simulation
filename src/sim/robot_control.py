import pybullet as pyb

ARM_JOINT_INDICES = [0, 1, 2, 3, 4, 5, 6]
GRIPPER_JOINT_INDICES = [9, 10]
JOINT_NUDGE_AMOUNT = 0.15


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
            maxVelocity=0.25,
        )


def relax_arm(panda_id):
    # Motors stop fighting the GUI joint dragger.
    for joint_index in ARM_JOINT_INDICES:
        current_angle = pyb.getJointState(panda_id, joint_index)[0]
        pyb.resetJointState(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            targetValue=current_angle,
            targetVelocity=0,
        )
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.VELOCITY_CONTROL,
            force=0,
        )


def set_manual_damping(panda_id, enabled):
    # Damping keeps the arm from drifting forever after a mouse drag.
    linear_damping = 0.95 if enabled else 0.04
    angular_damping = 0.95 if enabled else 0.04
    joint_damping = 2.0 if enabled else 0.04

    for link_index in range(-1, pyb.getNumJoints(panda_id)):
        pyb.changeDynamics(
            panda_id,
            link_index,
            linearDamping=linear_damping,
            angularDamping=angular_damping,
            jointDamping=joint_damping,
        )


def enter_manual_mode(panda_id):
    # With motors relaxed, gravity would make the arm collapse.
    pyb.setGravity(0, 0, 0)
    set_manual_damping(panda_id, enabled=True)
    relax_arm(panda_id)


def exit_manual_mode(panda_id):
    pyb.setGravity(0, 0, -9.81)
    set_manual_damping(panda_id, enabled=False)


def nudge_arm_joint(panda_id, arm_joint_number):
    joint_index = ARM_JOINT_INDICES[arm_joint_number - 1]
    current_angle = pyb.getJointState(panda_id, joint_index)[0]
    target_angle = current_angle + JOINT_NUDGE_AMOUNT

    pyb.setJointMotorControl2(
        bodyUniqueId=panda_id,
        jointIndex=joint_index,
        controlMode=pyb.POSITION_CONTROL,
        targetPosition=target_angle,
        force=250,
        maxVelocity=0.2,
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
            maxVelocity=0.02,
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
            maxVelocity=0.02,
        )


def print_gripper_state(panda_id):
    left_finger = pyb.getJointState(panda_id, GRIPPER_JOINT_INDICES[0])[0]
    right_finger = pyb.getJointState(panda_id, GRIPPER_JOINT_INDICES[1])[0]
    print(f"Gripper joints: left={left_finger:.4f}, right={right_finger:.4f}")
