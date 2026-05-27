import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pybullet as pyb
import pybullet_data

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.sim.robot_control import configure_gripper_friction, move_arm_to_home, open_gripper, step_simulation
from src.sim.routines import pick_and_place
from src.sim.scene_objects import create_blue_tray, create_red_cube


RUNS = 100
TRAY_HALF_X = 0.12
TRAY_HALF_Y = 0.08
OUTPUT_DIR = Path("outputs/testing")


def cube_in_tray(cube_id, tray_position):
    cube_position, _ = pyb.getBasePositionAndOrientation(cube_id)
    return (
        abs(cube_position[0] - tray_position[0]) <= TRAY_HALF_X
        and abs(cube_position[1] - tray_position[1]) <= TRAY_HALF_Y
        and cube_position[2] > 0.02
    )


def reset_scene():
    pyb.resetSimulation()
    pyb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pyb.setGravity(0, 0, -9.81)
    pyb.loadURDF("plane.urdf")

    panda_id = pyb.loadURDF(
        "franka_panda/panda.urdf",
        basePosition=[0, 0, 0],
        useFixedBase=True,
    )
    cube_id, cube_position = create_red_cube()
    _, tray_position = create_blue_tray()
    configure_gripper_friction(panda_id)

    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
    open_gripper(panda_id)
    step_simulation(seconds=0.5)

    return panda_id, cube_id, cube_position, tray_position


def main():
    pyb.connect(pyb.DIRECT)
    results = []

    for run_index in range(1, RUNS + 1):
        panda_id, cube_id, cube_position, tray_position = reset_scene()
        pick_and_place(panda_id, cube_position, tray_position)
        step_simulation(seconds=1.0)

        success = cube_in_tray(cube_id, tray_position)
        results.append((run_index, cube_position, tray_position, success))
        print(f"{run_index:03d}: {'PASS' if success else 'FAIL'}")

    pyb.disconnect()
    write_results(results)
    plot_start_positions(results)
    plot_failure_heatmap(results)
    print_summary(results)


def write_results(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "pick_place_results.csv"

    with path.open("w") as file:
        file.write("run,cube_x,cube_y,cube_z,tray_x,tray_y,tray_z,success\n")
        for run_index, cube_position, tray_position, success in results:
            file.write(
                f"{run_index},{cube_position[0]:.6f},{cube_position[1]:.6f},"
                f"{cube_position[2]:.6f},{tray_position[0]:.6f},"
                f"{tray_position[1]:.6f},{tray_position[2]:.6f},{int(success)}\n"
            )

    print(f"Saved results: {path}")


def plot_start_positions(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "start_positions.png"

    passed = [result for result in results if result[3]]
    failed = [result for result in results if not result[3]]

    if passed:
        plt.scatter(
            [result[1][0] for result in passed],
            [result[1][1] for result in passed],
            c="green",
            label="pass",
        )
    if failed:
        plt.scatter(
            [result[1][0] for result in failed],
            [result[1][1] for result in failed],
            c="red",
            label="fail",
        )
    plt.scatter(
        [result[2][0] for result in results],
        [result[2][1] for result in results],
        c="blue",
        marker="x",
        label="tray",
    )

    plt.xlabel("cube start x")
    plt.ylabel("cube start y")
    plt.title("Pick-place success by cube start position")
    plt.legend()
    plt.grid(True)
    plt.savefig(path)
    plt.close()
    print(f"Saved plot: {path}")


def plot_failure_heatmap(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "failure_heatmap.png"
    failed = [result for result in results if not result[3]]

    if not failed:
        print("Skipped failure heatmap: no failures")
        return

    plt.hist2d(
        [result[1][0] for result in failed],
        [result[1][1] for result in failed],
        bins=8,
        cmap="Reds",
    )
    plt.scatter(
        [result[2][0] for result in results],
        [result[2][1] for result in results],
        c="blue",
        marker="x",
        label="tray",
    )
    plt.colorbar(label="failure count")
    plt.xlabel("cube start x")
    plt.ylabel("cube start y")
    plt.title("Failure heatmap by cube start position")
    plt.legend()
    plt.savefig(path)
    plt.close()
    print(f"Saved heatmap: {path}")


def print_summary(results):
    successes = sum(1 for result in results if result[3])
    failures = [result[1] for result in results if not result[3]]

    print(f"Success rate: {successes}/{RUNS}")
    print_failure_summary(failures)


def print_failure_summary(failures):
    if not failures:
        print("No failures.")
        return

    xs = [position[0] for position in failures]
    ys = [position[1] for position in failures]
    far_x = [position for position in failures if position[0] > 0.58]
    large_y = [position for position in failures if abs(position[1]) > 0.20]
    corners = [position for position in failures if position[0] > 0.58 and abs(position[1]) > 0.20]

    print("Failure summary:")
    print(f"  failures: {len(failures)}")
    print(f"  x range: {min(xs):.3f} to {max(xs):.3f}")
    print(f"  y range: {min(ys):.3f} to {max(ys):.3f}")
    print(f"  far x failures (x > 0.58): {len(far_x)}")
    print(f"  large y failures (abs(y) > 0.20): {len(large_y)}")
    print(f"  corner failures: {len(corners)}")
    print("  failed start positions:")
    for position in failures:
        print(f"    x={position[0]:.3f}, y={position[1]:.3f}, z={position[2]:.3f}")


if __name__ == "__main__":
    main()
