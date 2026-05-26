import pybullet as pyb

def create_red_cube(position=(0.5, 0, 0.03)):
    # Keep the cube small enough for the Panda gripper.
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

    return pyb.createMultiBody(
        baseMass=0.1,
        baseCollisionShapeIndex=cube_collision_id,
        baseVisualShapeIndex=cube_visual_id,
        basePosition=position,
    )


def create_blue_tray(position=(0.35, -0.35, 0.01)):
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
