# Multi-View GUI Calculation Report

- Color: `red`
- View offsets: `{'center': (0.0, 0.0, 0.3), 'left': (0.0, 0.12, 0.3), 'right': (0.0, -0.12, 0.3), 'front': (-0.12, 0.0, 0.3)}`
- Actual PyBullet cube center: `(0.48, 0.0, 0.02999)`
- Merged point count before trimming: `3344`

## Per-View Artifacts

- `center`: RGB, mask, depth, and bbox/world debug PNGs saved.
- `left`: RGB, mask, depth, and bbox/world debug PNGs saved.
- `right`: RGB, mask, depth, and bbox/world debug PNGs saved.
- `front`: RGB, mask, depth, and bbox/world debug PNGs saved.

## Center Calculation

- Trimmed merged min xyz: `(0.45655, -0.02554, 0.06003)`
- Trimmed merged max xyz: `(0.50998, 0.02573, 0.06004)`
- Raw geometric center: `(min + max) / 2`
- Z correction: `center_z = max_z - CUBE_HALF_SIZE`, with `CUBE_HALF_SIZE=0.03`
- Estimated center: `(0.48327, 9e-05, 0.03004)`
- Error estimated - actual: `(0.00327, 9e-05, 5e-05)`
