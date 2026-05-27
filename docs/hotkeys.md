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
| `i` | Capture and save wrist-camera RGB image |
| `a` | Run scripted pick-and-place |
| `m` | Parse text command and execute it |

## Camera controls

| Key | Action |
| --- | --- |
| `f` | Front camera view |
| `v` | Side camera view |
| `t` | Top camera view |

## Test Flow

- Basic pick-and-place test: press `p`, `l`, `c`, `u`, `b`, `d`, then `o`.
- Automated pick-and-place test: press `a`.
- Command-driven test: press `m`.
- The red cube spawns randomly inside a conservative reachable workspace.
- `p`, `l`, `a`, and `m` use the current scene registry position. Vision will update that registry later.
