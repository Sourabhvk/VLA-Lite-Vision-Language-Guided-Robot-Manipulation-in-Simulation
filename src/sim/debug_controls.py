import pybullet as pyb

from src.sim.robot_control import move_arm_to_home, open_gripper, step_simulation
from src.sim.scene_objects import sample_scene_positions
from src.sim.scene_registry import set_object_position


def create_reset_scene_control():
    # PyBullet gives us sliders, so this slider acts like a simple reset button.
    control_id = pyb.addUserDebugParameter("randomize scene + home", 0, 1, 0)
    return {"id": control_id, "last_value": 0}


def handle_reset_scene_control(control, panda_id, cube_ids, cube_names, tray_id):
    value = pyb.readUserDebugParameter(control["id"])
    if value == control["last_value"]:
        return

    control["last_value"] = value
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
