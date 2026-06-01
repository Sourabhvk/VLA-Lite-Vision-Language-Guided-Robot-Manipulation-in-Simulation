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
| `m` | Run the demo command through Ollama and execute it |
| `p` | Prompt for a terminal command, parse with Ollama, and execute it |

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
- Command-driven test: press `p` and type a prompt.
- Wrist camera captures are saved under `outputs/`.
- Fixed color cubes spawn inside a conservative reachable workspace.
- Prompt commands are parsed by Ollama, validated, then executed through vision.
- Vision commands use the wrist camera and OpenCV detection result directly.
