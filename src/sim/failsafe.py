import pybullet as pyb

from src.sim.robot_control import ARM_JOINT_INDICES, ARM_MOTOR_FORCE

GRIPPER_LINKS = {9, 10}


def has_interference(panda_id, cube_id=None, tray_id=None, plane_id=None):
    for contact in pyb.getContactPoints(bodyA=panda_id):
        other_body = contact[2]
        panda_link = contact[3]

        if cube_id is not None and other_body == cube_id and panda_link not in GRIPPER_LINKS:
            return True

        if tray_id is not None and other_body == tray_id:
            return True

        if plane_id is not None and other_body == plane_id:
            return True

    return False


def stop_robot(panda_id):
    # Hold the arm wherever it is when interference is detected.
    for joint_index in ARM_JOINT_INDICES:
        current_angle = pyb.getJointState(panda_id, joint_index)[0]
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=current_angle,
            force=ARM_MOTOR_FORCE,
            maxVelocity=0,
        )
