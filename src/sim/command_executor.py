from src.perception.vision_routines import vision_pick_and_place_colored_cube
from src.sim.robot_control import move_arm_to_home, step_simulation


def execute_task(panda_id, task):
    color = task["source"]["color"]
    quantity = task["source"]["quantity"]

    if quantity == "all":
        raise NotImplementedError("Picking all matching cubes is the next routine step")

    # Singular commands pick the nearest visible matching cube through vision.
    vision_pick_and_place_colored_cube(panda_id, color)
    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
