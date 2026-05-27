import random

import pybullet as pyb


RED_CUBE_POSITION = (0.5, 0, 0.03)
BLUE_TRAY_POSITION = (0.35, -0.35, 0.01)
CUBE_X_RANGE = (0.35, 0.68)
CUBE_Y_RANGE = (-0.28, 0.28)
TRAY_X_RANGE = (0.28, 0.45)
TRAY_Y_RANGE = (-0.42, -0.25)
TRAY_HALF_EXTENTS = [0.12, 0.08, 0.01]
CUBE_HALF_SIZE = 0.03
CUBE_LATERAL_FRICTION = 2.0
CUBE_SPINNING_FRICTION = 0.02
CUBE_ROLLING_FRICTION = 0.02


def sample_red_cube_position():
    return (
        random.uniform(*CUBE_X_RANGE),
        random.uniform(*CUBE_Y_RANGE),
        RED_CUBE_POSITION[2],
    )


def sample_blue_tray_position():
    return (
        random.uniform(*TRAY_X_RANGE),
        random.uniform(*TRAY_Y_RANGE),
        BLUE_TRAY_POSITION[2],
    )


def positions_overlap(cube_position, tray_position):
    # Compare 2D footprints on the table; z is fixed for both objects.
    return (
        abs(cube_position[0] - tray_position[0]) <= TRAY_HALF_EXTENTS[0] + CUBE_HALF_SIZE
        and abs(cube_position[1] - tray_position[1]) <= TRAY_HALF_EXTENTS[1] + CUBE_HALF_SIZE
    )


def sample_scene_positions():
    # Reject invalid randomized scenes where the cube starts inside the tray.
    for _ in range(100):
        cube_position = sample_red_cube_position()
        tray_position = sample_blue_tray_position()
        if not positions_overlap(cube_position, tray_position):
            return cube_position, tray_position

    raise RuntimeError("Could not sample non-overlapping cube/tray positions")


def create_red_cube(position=None):
    # Keep the cube small enough for the Panda gripper.
    if position is None:
        position = sample_red_cube_position()

    cube_collision_id = pyb.createCollisionShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=[CUBE_HALF_SIZE, CUBE_HALF_SIZE, CUBE_HALF_SIZE],
    )
    cube_visual_id = pyb.createVisualShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=[CUBE_HALF_SIZE, CUBE_HALF_SIZE, CUBE_HALF_SIZE],
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


def create_blue_tray(position=None):
    # For now the tray is a flat target zone, not a real container.
    if position is None:
        position = sample_blue_tray_position()

    tray_collision_id = pyb.createCollisionShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=TRAY_HALF_EXTENTS,
    )
    tray_visual_id = pyb.createVisualShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=TRAY_HALF_EXTENTS,
        rgbaColor=[0, 0.2, 1, 1],
    )

    tray_id = pyb.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=tray_collision_id,
        baseVisualShapeIndex=tray_visual_id,
        basePosition=position,
    )

    return tray_id, position
