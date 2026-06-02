# File: src/sim/scene_registry.py
# Intent: Keeps lightweight names for important scene object positions.
# Usage: Lets routines find the current tray/cube positions after random scene resets.
# Presets: blue_tray starts at BLUE_TRAY_POSITION.
# Connects: src/sim/scene_objects.py; src/sim/debug_controls.py; src/perception/vision_routines.py.
# User values: object names and positions set during scene spawn/reset.
#
# Functions:
# - get_object_position(): Returns the last known world position for a named scene object.
# - set_object_position(): Stores or updates a named scene object's world position.

from src.sim.scene_objects import BLUE_TRAY_POSITION


OBJECT_POSITIONS = {
    "blue_tray": BLUE_TRAY_POSITION,
}


def get_object_position(name):
    return OBJECT_POSITIONS[name]


def set_object_position(name, position):
    OBJECT_POSITIONS[name] = position
