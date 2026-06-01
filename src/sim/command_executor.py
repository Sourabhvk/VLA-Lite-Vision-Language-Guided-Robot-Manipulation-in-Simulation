from src.perception.vision_routines import (
    vision_pick_and_place_colored_cube,
    vision_pick_colored_cube,
    vision_place_in_blue_tray,
)
from src.sim.robot_control import move_arm_to_home, step_simulation


def execute_task(panda_id, task):
    action = task["action"]

    if action in {"pick", "pick_place"} and task["source"]["quantity"] == "all":
        raise NotImplementedError("Picking all matching cubes is the next routine step")

    if action == "pick":
        vision_pick_colored_cube(panda_id, task["source"]["color"])
        return

    if action == "place":
        vision_place_in_blue_tray(panda_id)
    else:
        vision_pick_and_place_colored_cube(panda_id, task["source"]["color"])

    # After a place action the robot should leave the workspace clear.
    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
