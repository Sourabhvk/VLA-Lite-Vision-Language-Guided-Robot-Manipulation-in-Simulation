import time

import pybullet as pyb
import pybullet_data

from src.sim.scene_objects import create_blue_tray, create_red_cube


def main():
    # Use GUI for now so we can actually see what the robot is doing.
    pyb.connect(pyb.GUI)

    # Start the debug camera at a useful angle for this tabletop scene.
    pyb.resetDebugVisualizerCamera(
        cameraDistance=1.2,
        cameraYaw=45,
        cameraPitch=-35,
        cameraTargetPosition=[0.35, 0, 0.2],
    )

    # Lets PyBullet find built-in URDFs like the plane and Franka Panda.
    pyb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pyb.setGravity(0, 0, -9.81)

    pyb.loadURDF("plane.urdf")

    # Fixed base keeps the arm bolted to the table/world.
    panda_id = pyb.loadURDF(
        "franka_panda/panda.urdf",
        basePosition=[0, 0, 0],
        useFixedBase=True,
    )

    create_red_cube()
    create_blue_tray()

    # Print joints once so we know which indices control the arm and gripper.
    num_joints = pyb.getNumJoints(panda_id)
    print(f"Panda loaded with {num_joints} joints")

    for joint_index in range(num_joints):
        joint_info = pyb.getJointInfo(panda_id, joint_index)
        joint_name = joint_info[1].decode("utf-8")
        joint_type = joint_info[2]
        print(joint_index, joint_name, joint_type)

    # Panda arm joints are 0-6. The finger joints come later.
    arm_joint_indices = [0, 1, 2, 3, 4, 5, 6]

    # A simple bent pose that keeps the arm away from singular straight lines.
    home_pose = [0.0, -0.6, 0.0, -2.2, 0.0, 1.6, 0.8]

    for joint_index, target_angle in zip(arm_joint_indices, home_pose):
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=target_angle,
            force=500,
        )

    # These two joints are the Panda finger sliders.
    gripper_joint_indices = [9, 10]
    open_gripper_width = 0.04

    for joint_index in gripper_joint_indices:
        pyb.setJointMotorControl2(
            bodyUniqueId=panda_id,
            jointIndex=joint_index,
            controlMode=pyb.POSITION_CONTROL,
            targetPosition=open_gripper_width,
            force=50,
        )

    # PyBullet does not run physics unless we step it.
    try:
        while True:
            pyb.stepSimulation()
            time.sleep(1.0 / 240.0)
    except KeyboardInterrupt:
        pyb.disconnect()


if __name__ == "__main__":
    main()
