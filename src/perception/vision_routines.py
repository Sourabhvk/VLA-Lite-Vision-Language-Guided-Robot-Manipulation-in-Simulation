from src.perception.object_localizer import localize_red_cube
from src.sim.robot_control import close_gripper, move_ee_to_position, open_gripper, step_simulation
from src.sim.routines import (
    APPROACH_HEIGHT_OFFSET,
    GRASP_Z_OFFSET,
    PRE_GRASP_HEIGHT_OFFSET,
    TRAY_DROP_HEIGHT_OFFSET,
)
from src.sim.scene_registry import get_object_position


def vision_pick_and_place_red_cube(panda_id):
    cube_position = localize_red_cube(panda_id)
    if cube_position is None:
        return

    # First move above the rough detection, then re-detect from a closer view.
    move_ee_to_position(panda_id, above(cube_position, APPROACH_HEIGHT_OFFSET))
    step_simulation(seconds=1.2)

    refined_cube_position = localize_red_cube(panda_id)
    if refined_cube_position is not None:
        cube_position = refined_cube_position

    move_ee_to_position(panda_id, above(cube_position, PRE_GRASP_HEIGHT_OFFSET))
    step_simulation(seconds=0.8)

    move_ee_to_position(panda_id, above(cube_position, GRASP_Z_OFFSET))
    step_simulation(seconds=1.0)

    close_gripper(panda_id)
    step_simulation(seconds=0.8)

    move_ee_to_position(panda_id, above(cube_position, APPROACH_HEIGHT_OFFSET))
    step_simulation(seconds=1.2)

    tray_position = get_object_position("blue_tray")
    move_ee_to_position(panda_id, above(tray_position, APPROACH_HEIGHT_OFFSET))
    step_simulation(seconds=1.5)

    move_ee_to_position(panda_id, above(tray_position, TRAY_DROP_HEIGHT_OFFSET))
    step_simulation(seconds=1.0)

    open_gripper(panda_id)
    step_simulation(seconds=0.8)


def above(position, z_offset):
    return [position[0], position[1], position[2] + z_offset]
