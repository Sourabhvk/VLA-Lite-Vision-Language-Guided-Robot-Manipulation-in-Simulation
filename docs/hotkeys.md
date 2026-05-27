# Simulation Hotkeys

Click inside the PyBullet window before pressing keys.

## Robot controls

| Key | Action |
| --- | --- |
| `h` | Move Panda arm back to home pose |
| `r` | Enter manual mode |
| `o` | Open gripper |
| `c` | Close gripper |
| `1`-`7` | Nudge Panda arm joints 1 through 7 forward |
| `p` | Move gripper above the red cube |
| `l` | Lower gripper toward the red cube |
| `u` | Lift gripper upward |

## Camera controls

| Key | Action |
| --- | --- |
| `f` | Front camera view |
| `v` | Side camera view |
| `t` | Top camera view |

## Notes

- Manual mode disables gravity and motor resistance so the arm can be moved more easily.
- Press `h` to leave manual mode and restore normal gravity.
- `p` and `l` use hardcoded cube coordinates for now. Vision will replace those later.
- Basic grasp test: press `p`, then `l`, then `c`, then `u`. If the cube lifts naturally, the grasp worked.
