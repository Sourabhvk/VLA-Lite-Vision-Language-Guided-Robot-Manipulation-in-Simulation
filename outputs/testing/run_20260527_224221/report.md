# Pick-and-Place Test Report

- Runs: 1000
- Successes: 687
- Success rate: 68.70%
- Initial cube/tray overlaps: 51
- Non-overlap failures: 262

## Findings

- Failures are position-dependent rather than purely random.
- Initial cube/tray overlaps are invalid spawn cases and are tracked separately.
- The scatter plot is currently more informative than the heatmap when failure counts per bin are low.
- The next useful improvement is to prevent overlapping spawns and then re-run the reliability test.

## Artifacts

- `pick_place_results.csv`
- `start_positions.png`
- `failure_heatmap.png`
