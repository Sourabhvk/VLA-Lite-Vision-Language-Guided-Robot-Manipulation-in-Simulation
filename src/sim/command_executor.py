from src.perception.vision_routines import (
    vision_pick_hsv_cube,
    vision_place_in_blue_tray,
)
from src.sim.robot_control import move_arm_to_home, step_simulation


def execute_task(panda_id, task):
    action = task["action"]

    if action in {"pick", "pick_place"} and task["source"]["quantity"] == "all":
        raise NotImplementedError("Picking all matching cubes is the next routine step")

    if action == "pick":
        pick_from_source(panda_id, task["source"])
        return

    if action == "place":
        vision_place_in_blue_tray(panda_id)
    else:
        if pick_from_source(panda_id, task["source"]):
            vision_place_in_blue_tray(panda_id)

    # After a place action the robot should leave the workspace clear.
    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)


def pick_from_source(panda_id, source):
    label = source.get("color_text", "requested")
    return vision_pick_hsv_cube(panda_id, source["hsv_ranges"], label)
