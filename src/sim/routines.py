from src.sim.robot_control import (
    close_gripper,
    move_ee_to_position,
    open_gripper,
    step_simulation,
)

APPROACH_HEIGHT_OFFSET = 0.25
TRAY_DROP_HEIGHT_OFFSET = 0.08

#routine for pick and place, used in keyboard controls and failsafe
def pick_and_place(panda_id, source_position, target_position):
    source_above = [
        source_position[0],
        source_position[1],
        source_position[2] + APPROACH_HEIGHT_OFFSET,
    ]
    target_above = [
        target_position[0],
        target_position[1],
        target_position[2] + APPROACH_HEIGHT_OFFSET,
    ]
    target_drop = [
        target_position[0],
        target_position[1],
        target_position[2] + TRAY_DROP_HEIGHT_OFFSET,
    ]

    move_ee_to_position(panda_id, source_above)
    step_simulation(seconds=1.2)

    move_ee_to_position(panda_id, source_position)
    step_simulation(seconds=1.2)

    close_gripper(panda_id)
    step_simulation(seconds=0.8)

    move_ee_to_position(panda_id, source_above)
    step_simulation(seconds=1.2)

    move_ee_to_position(panda_id, target_above)
    step_simulation(seconds=1.5)

    move_ee_to_position(panda_id, target_drop)
    step_simulation(seconds=1.0)

    open_gripper(panda_id)
    step_simulation(seconds=0.8)
