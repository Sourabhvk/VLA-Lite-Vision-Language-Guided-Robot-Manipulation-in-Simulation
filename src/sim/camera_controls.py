# File: src/sim/camera_controls.py
# Intent: Stores and applies named PyBullet debug camera views.
# Usage: Called by startup and keyboard hotkeys to reframe the GUI camera.
# Presets: front, side, and top view dictionaries.
# Connects: src/sim/panda_env.py; src/sim/keyboard_controls.py; PyBullet debug visualizer.
# User values: cameraDistance, cameraYaw, cameraPitch, and cameraTargetPosition in CAMERA_VIEWS.
#
# Functions:
# - set_camera_view(): Applies one named camera preset to the PyBullet GUI.

import pybullet as pyb

CAMERA_VIEWS = {
    "front": {
        "cameraDistance": 0.9,
        "cameraYaw": 90,
        "cameraPitch": -35,
        "cameraTargetPosition": [0.45, 0, 0],
    },
    "side": {
        "cameraDistance": 1.1,
        "cameraYaw": 0,
        "cameraPitch": -30,
        "cameraTargetPosition": [0.3, 0, 0],
    },
    "top": {
        "cameraDistance": 1.0,
        "cameraYaw": 90,
        "cameraPitch": -75,
        "cameraTargetPosition": [0.45, 0, 0],
    },
}


def set_camera_view(name):
    view = CAMERA_VIEWS[name]
    pyb.resetDebugVisualizerCamera(**view)
