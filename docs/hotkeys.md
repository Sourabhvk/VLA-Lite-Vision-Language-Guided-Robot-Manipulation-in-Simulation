# Simulation Hotkeys

Click inside the PyBullet window before pressing keys.

## Robot controls

| Key | Action |
| --- | --- |
| `h` | Move Panda arm back to home pose |
| `o` | Open gripper |
| `c` | Close gripper |
| `u` | Lift gripper upward |
| `b` | Move gripper above the blue tray |
| `d` | Lower gripper toward the blue tray |
| `i` | Capture and save wrist-camera RGB image |
| `y` | Detect red cube in wrist-camera image |
| `q` | Detect red cube and move above it |
| `j` | Vision-based red-cube pick-and-place |
| `m` | Parse text command and execute it |

## PyBullet panel controls

Use the `Params` panel on the right side of the PyBullet window.

| Control | Action |
| --- | --- |
| `randomize scene + home` | Randomize cube/tray positions, open gripper, and move Panda home |

## Camera controls

| Key | Action |
| --- | --- |
| `f` | Front camera view |
| `v` | Side camera view |
| `t` | Top camera view |

## Test Flow

- Vision pick-and-place test: press `j`.
- Command-driven test: press `m`.
- Wrist camera captures are saved under `outputs/`.
- The red cube spawns randomly inside a conservative reachable workspace.
- Manual/scripted commands use the current scene registry position.
- Vision commands use the wrist camera and OpenCV detection result directly.
