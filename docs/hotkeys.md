# Simulation Hotkeys

Click inside the PyBullet window before pressing keys.

## Robot controls

| Key | Action |
| --- | --- |
| `h` | Move Panda arm back to home pose |
| `o` | Open gripper |
| `c` | Close gripper |
| `p` | Move gripper above the red cube |
| `l` | Lower gripper toward the red cube |
| `u` | Lift gripper upward |

## Camera controls

| Key | Action |
| --- | --- |
| `f` | Front camera view |
| `v` | Side camera view |
| `t` | Top camera view |

## Test Flow

- Basic grasp test: press `p`, then `l`, then `c`, then `u`.
- Press `o` to release the cube.
- `p` and `l` use hardcoded cube coordinates for now. Vision will replace those later.
