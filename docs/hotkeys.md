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
| `b` | Move gripper above the blue tray |
| `d` | Lower gripper toward the blue tray |
| `x` | Print active contact points |

## Camera controls

| Key | Action |
| --- | --- |
| `f` | Front camera view |
| `v` | Side camera view |
| `t` | Top camera view |

## Test Flow

- Basic pick-and-place test: press `p`, `l`, `c`, `u`, `b`, `d`, then `o`.
- `p` and `l` use hardcoded cube coordinates for now. Vision will replace those later.
