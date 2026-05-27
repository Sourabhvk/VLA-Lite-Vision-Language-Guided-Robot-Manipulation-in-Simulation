from src.perception.object_localizer import localize_red_cube
from src.sim.routines import pick_and_place
from src.sim.scene_registry import get_object_position


def vision_pick_and_place_red_cube(panda_id):
    cube_position = localize_red_cube(panda_id)
    if cube_position is None:
        return

    pick_and_place(
        panda_id,
        cube_position,
        get_object_position("blue_tray"),
    )
