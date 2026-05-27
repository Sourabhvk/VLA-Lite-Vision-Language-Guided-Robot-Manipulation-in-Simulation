import random

import pybullet as pyb


RED_CUBE_POSITION = (0.5, 0, 0.03)
BLUE_TRAY_POSITION = (0.35, -0.35, 0.01)
CUBE_X_RANGE = (0.43, 0.62)
CUBE_Y_RANGE = (-0.18, 0.18)
CUBE_LATERAL_FRICTION = 2.0
CUBE_SPINNING_FRICTION = 0.02
CUBE_ROLLING_FRICTION = 0.02


def sample_red_cube_position():
    return (
        random.uniform(*CUBE_X_RANGE),
        random.uniform(*CUBE_Y_RANGE),
        RED_CUBE_POSITION[2],
    )


def create_red_cube(position=None):
    # Keep the cube small enough for the Panda gripper.
    if position is None:
        position = sample_red_cube_position()

    cube_half_size = 0.03
    cube_collision_id = pyb.createCollisionShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=[cube_half_size, cube_half_size, cube_half_size],
    )
    cube_visual_id = pyb.createVisualShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=[cube_half_size, cube_half_size, cube_half_size],
        rgbaColor=[1, 0, 0, 1],
    )

    cube_id = pyb.createMultiBody(
        baseMass=0.1,
        baseCollisionShapeIndex=cube_collision_id,
        baseVisualShapeIndex=cube_visual_id,
        basePosition=position,
    )

    pyb.changeDynamics(
        cube_id,
        -1,
        lateralFriction=CUBE_LATERAL_FRICTION,
        spinningFriction=CUBE_SPINNING_FRICTION,
        rollingFriction=CUBE_ROLLING_FRICTION,
    )

    return cube_id, position


def create_blue_tray(position=BLUE_TRAY_POSITION):
    # For now the tray is a flat target zone, not a real container.
    tray_half_extents = [0.12, 0.08, 0.01]
    tray_collision_id = pyb.createCollisionShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=tray_half_extents,
    )
    tray_visual_id = pyb.createVisualShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=tray_half_extents,
        rgbaColor=[0, 0.2, 1, 1],
    )

    return pyb.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=tray_collision_id,
        baseVisualShapeIndex=tray_visual_id,
        basePosition=position,
    )
