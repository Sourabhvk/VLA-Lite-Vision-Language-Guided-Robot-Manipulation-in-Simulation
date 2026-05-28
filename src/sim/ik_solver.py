import pybullet as pyb

from src.sim.robot_control import END_EFFECTOR_LINK_INDEX, HOME_POSE

#Found by experimenting with the PyBullet GUI and the Panda robot in the PyBullet data package. The lower and upper limits are the same as those defined in the URDF file for the Panda robot, but they need to be explicitly passed to the IK solver to get correct results.
PANDA_LOWER_LIMITS = [-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973]
PANDA_UPPER_LIMITS = [2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973]
PANDA_JOINT_RANGES = [
    upper - lower for lower, upper in zip(PANDA_LOWER_LIMITS, PANDA_UPPER_LIMITS)
]
PANDA_JOINT_DAMPING = [0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]

def solve_panda_ik(panda_id, target_position):
    # Bias IK toward the comfortable home pose instead of any valid arm shape.
    gripper_orientation = pyb.getQuaternionFromEuler([3.14159, 0, 0])
    joint_targets = pyb.calculateInverseKinematics(
        bodyUniqueId=panda_id,
        endEffectorLinkIndex=END_EFFECTOR_LINK_INDEX,
        targetPosition=target_position,
        targetOrientation=gripper_orientation,
        lowerLimits=PANDA_LOWER_LIMITS,
        upperLimits=PANDA_UPPER_LIMITS,
        jointRanges=PANDA_JOINT_RANGES,
        restPoses=HOME_POSE,
        jointDamping=PANDA_JOINT_DAMPING,
    )

    return joint_targets[: len(HOME_POSE)]
