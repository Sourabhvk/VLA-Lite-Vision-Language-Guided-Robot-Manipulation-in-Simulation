# File: src/perception/vision_routines.py
# Intent: Runs vision-guided pick and place motions from detected cube/tray positions.
# Usage: Called by keyboard demos and structured command execution.
# Presets: approach, pre-grasp, grasp, and tray drop height offsets from routines.py.
# Connects: src/perception/object_localizer.py; src/sim/robot_control.py; src/sim/scene_registry.py.
# User values: requested color, hsv_ranges, and command label text.
#
# Functions:
# - vision_pick_and_place_red_cube(): Runs the red cube pick-and-place demo.
# - vision_pick_and_place_colored_cube(): Picks a named color cube, then places it in the tray.
# - vision_pick_colored_cube(): Picks a cube located by built-in color preset.
# - vision_pick_hsv_cube(): Picks a cube located by validated HSV command ranges.
# - vision_pick_cube(): Shared vision pick sequence with close-range re-detection.
# - vision_place_in_blue_tray(): Moves above the blue tray, lowers, opens gripper, and releases.
# - above(): Adds a z offset to a world position.

from src.perception.object_localizer import localize_colored_cube, localize_hsv_cube
from src.sim.robot_control import close_gripper, move_ee_to_position, move_pinch_center_to_position, open_gripper, step_simulation
from src.sim.routines import (
    APPROACH_HEIGHT_OFFSET,
    GRASP_Z_OFFSET,
    PRE_GRASP_HEIGHT_OFFSET,
    TRAY_DROP_HEIGHT_OFFSET,
)
from src.sim.scene_registry import get_object_position


def vision_pick_and_place_red_cube(panda_id):
    vision_pick_and_place_colored_cube(panda_id, "red")


def vision_pick_and_place_colored_cube(panda_id, color):
    if vision_pick_colored_cube(panda_id, color):
        vision_place_in_blue_tray(panda_id)


def vision_pick_colored_cube(panda_id, color):
    return vision_pick_cube(panda_id, lambda: localize_colored_cube(panda_id, color))


def vision_pick_hsv_cube(panda_id, hsv_ranges, label="requested"):
    return vision_pick_cube(panda_id, lambda: localize_hsv_cube(panda_id, hsv_ranges, label))


def vision_pick_cube(panda_id, localize_cube):
    cube_position = localize_cube()
    if cube_position is None:
        return False

    # First move above the rough detection, then re-detect from a closer view.
    move_pinch_center_to_position(panda_id, above(cube_position, APPROACH_HEIGHT_OFFSET))
    step_simulation(seconds=1.2)

    refined_cube_position = localize_cube()
    if refined_cube_position is not None:
        cube_position = refined_cube_position

    move_pinch_center_to_position(panda_id, above(cube_position, PRE_GRASP_HEIGHT_OFFSET))
    step_simulation(seconds=0.8)

    move_pinch_center_to_position(panda_id, above(cube_position, GRASP_Z_OFFSET))
    step_simulation(seconds=1.0)

    close_gripper(panda_id)
    step_simulation(seconds=0.8)

    move_ee_to_position(panda_id, above(cube_position, APPROACH_HEIGHT_OFFSET))
    step_simulation(seconds=1.2)

    return True


def vision_place_in_blue_tray(panda_id):
    tray_position = get_object_position("blue_tray")
    move_ee_to_position(panda_id, above(tray_position, APPROACH_HEIGHT_OFFSET))
    step_simulation(seconds=1.5)

    move_ee_to_position(panda_id, above(tray_position, TRAY_DROP_HEIGHT_OFFSET))
    step_simulation(seconds=1.0)

    open_gripper(panda_id)
    step_simulation(seconds=0.8)


def above(position, z_offset):
    return [position[0], position[1], position[2] + z_offset]
