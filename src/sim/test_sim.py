from src.sim.robot_control import (
    close_gripper,
    open_gripper,
    print_gripper_state,
    step_simulation,
)


def run_gripper_test(panda_id):
    # Quick sanity check: open, close, then open again.
    print("Gripper test: open")
    open_gripper(panda_id)
    step_simulation(seconds=3.0)
    print_gripper_state(panda_id)

    print("Gripper test: close")
    close_gripper(panda_id)
    step_simulation(seconds=3.0)
    print_gripper_state(panda_id)

    print("Gripper test: open")
    open_gripper(panda_id)
    step_simulation(seconds=3.0)
    print_gripper_state(panda_id)
