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
