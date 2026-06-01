import random

import pybullet as pyb


CUBE_Z = 0.03
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
CUBE_COLORS = {
    "violet": [0.56, 0.0, 1.0, 1],
    "blue": [0.0, 0.0, 1.0, 1],
    "green": [0.0, 1.0, 0.0, 1],
    "yellow": [1.0, 1.0, 0.0, 1],
    "orange": [1.0, 0.5, 0.0, 1],
    "red": [1.0, 0.0, 0.0, 1],
}
DEFAULT_CUBE_NAMES = list(CUBE_COLORS)
RANDOM_CUBE_COLORS = [
    [1.0, 0.0, 1.0, 1],  # pink
    [0.0, 1.0, 1.0, 1],  # cyan
    [0.5, 0.5, 0.5, 1],  # gray
]


def sample_position(x_range, y_range, z):
    return (
        random.uniform(*x_range),
        random.uniform(*y_range),
        z,
    )


def sample_cube_position():
    return sample_position(CUBE_X_RANGE, CUBE_Y_RANGE, CUBE_Z)


def sample_blue_tray_position():
    return sample_position(TRAY_X_RANGE, TRAY_Y_RANGE, BLUE_TRAY_POSITION[2])


def footprints_overlap(position_a, half_extents_a, position_b, half_extents_b):
    # Compare 2D footprints on the table; z is fixed for both objects.
    return (
        abs(position_a[0] - position_b[0]) <= half_extents_a[0] + half_extents_b[0]
        and abs(position_a[1] - position_b[1]) <= half_extents_a[1] + half_extents_b[1]
    )


def sample_scene_positions(extra_cube_count=0):
    # Place cubes one by one so larger distractor counts still sample reliably.
    cube_extents = [CUBE_HALF_SIZE, CUBE_HALF_SIZE]

    for _ in range(100):
        tray_position = sample_blue_tray_position()
        cube_positions = []

        for _ in range(extra_cube_count + 1):
            for _ in range(100):
                cube_position = sample_cube_position()
                overlaps_tray = footprints_overlap(cube_position, cube_extents, tray_position, TRAY_HALF_EXTENTS)
                overlaps_cube = any(
                    footprints_overlap(cube_position, cube_extents, other, cube_extents)
                    for other in cube_positions
                )
                if not overlaps_tray and not overlaps_cube:
                    cube_positions.append(cube_position)
                    break

        if len(cube_positions) == extra_cube_count + 1:
            return cube_positions, tray_position

    raise RuntimeError("Could not sample non-overlapping cube/tray positions")


def create_red_cube(position=None):
    return create_colored_cube("red", position)


def create_colored_cube(color_name, position=None):
    # Keep cubes small enough for the Panda gripper.
    if position is None:
        position = sample_cube_position()

    color = CUBE_COLORS.get(color_name, random.choice(RANDOM_CUBE_COLORS))
    cube_collision_id = pyb.createCollisionShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=[CUBE_HALF_SIZE, CUBE_HALF_SIZE, CUBE_HALF_SIZE],
    )
    cube_visual_id = pyb.createVisualShape(
        shapeType=pyb.GEOM_BOX,
        halfExtents=[CUBE_HALF_SIZE, CUBE_HALF_SIZE, CUBE_HALF_SIZE],
        rgbaColor=color,
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
