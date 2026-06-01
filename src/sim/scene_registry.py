from src.sim.scene_objects import BLUE_TRAY_POSITION


OBJECT_POSITIONS = {
    "blue_tray": BLUE_TRAY_POSITION,
}


def get_object_position(name):
    return OBJECT_POSITIONS[name]


def set_object_position(name, position):
    OBJECT_POSITIONS[name] = position
