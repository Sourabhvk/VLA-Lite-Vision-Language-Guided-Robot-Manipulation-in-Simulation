<!--
File: docs/hotkeys.md
Intent: Documents interactive PyBullet keyboard controls and command-driven demos.
Usage: Reference while the simulation GUI is running.
Presets: robot, camera, debug, perception, and language hotkeys.
Connects: src/sim/keyboard_controls.py; README.md.
User values: typed commands after l, and selected hotkeys during GUI control.

Functions:
- None: Documentation file.
-->

# Simulation Hotkeys

Click inside the PyBullet window before pressing keys.

## Robot controls

| Key | Action |
| --- | --- |
| `h` | Move Panda arm back to home pose |
| `o` | Open gripper |
| `c` | Close gripper |
| `u` | Lift gripper upward |
| `r` | Randomize scene, open gripper, and send robot home |
| `b` | Move gripper above the blue tray |
| `d` | Lower gripper toward the blue tray |
| `i` | Capture and save wrist-camera RGB image |
| `y` | Detect the red cube in wrist-camera image |
| `q` | Detect the red cube and move above it |
| `j` | Vision-based red-cube pick-and-place demo |
| `m` | Run the demo prompt through Ollama |
| `l` | Prompt for a terminal command, parse with Ollama, and execute it |

## Camera controls

| Key | Action |
| --- | --- |
| `f` | Front camera view |
| `v` | Side camera view |
| `t` | Top camera view |

## Test Flow

- Vision pick-and-place test: press `j`.
- Command-driven test: press `l` and type a prompt.
- Wrist camera captures are saved under `outputs/`.
- Fixed color cubes spawn inside a conservative reachable workspace.
- Prompt commands are parsed by Ollama, validated, then executed through vision.
- Vision commands use the wrist camera and OpenCV detection result directly.
