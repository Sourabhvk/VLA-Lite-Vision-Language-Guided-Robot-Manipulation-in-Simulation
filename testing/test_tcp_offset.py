# File: testing/test_tcp_offset.py
# Intent: Measures gripper TCP offset by comparing requested targets to actual finger pinch centers.
# Usage: Run manually to create CSV/report/plot artifacts under outputs/tcp_offset/.
# Presets: DIRECT PyBullet mode, open gripper, fixed reachable target positions, Panda link IDs.
# Connects: src/sim/robot_control.py; src/sim/scene_objects.py; outputs/tcp_offset/.
# User values: TARGETS, OUTPUT_ROOT, and robot speed config.
#
# Functions:
# - main(): Runs all target cases, writes artifacts, and prints the output folder.
# - make_output_dir(): Creates a timestamped output directory for this TCP test run.
# - setup_scene(): Creates a fresh DIRECT Panda scene in home pose with open gripper.
# - run_case(): Moves to one requested target and records link/pinch-center errors.
# - gripper_points(): Returns world positions for link 11 and the midpoint of finger links 9/10.
# - vector_error(): Computes actual minus requested xyz offset.
# - write_results(): Writes requested, link, pinch-center, and error vectors to CSV.
# - write_report(): Summarizes average/max link and pinch-center errors.
# - plot_offsets(): Saves a top-down arrow plot of requested target to pinch center.

import csv
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pybullet as pyb
import pybullet_data

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.sim.robot_control import (
    END_EFFECTOR_LINK_INDEX,
    GRIPPER_JOINT_INDICES,
    configure_gripper_friction,
    move_arm_to_home,
    move_ee_to_position,
    open_gripper,
    step_simulation,
)
from src.sim.scene_objects import CUBE_Z


OUTPUT_ROOT = Path("outputs/tcp_offset")
TARGETS = {
    "center": (0.48, 0.00, CUBE_Z + 0.08),
    "left": (0.48, 0.20, CUBE_Z + 0.08),
    "right": (0.48, -0.20, CUBE_Z + 0.08),
    "near_base": (0.32, 0.00, CUBE_Z + 0.08),
    "far": (0.62, 0.00, CUBE_Z + 0.08),
}


def main():
    output_dir = make_output_dir()
    panda_id = setup_scene()
    results = [run_case(panda_id, name, target) for name, target in TARGETS.items()]
    pyb.disconnect()

    write_results(results, output_dir)
    write_report(results, output_dir)
    plot_offsets(results, output_dir)
    print(f"TCP offset results: {output_dir}")


def make_output_dir():
    output_dir = OUTPUT_ROOT / datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def setup_scene():
    pyb.connect(pyb.DIRECT)
    pyb.resetSimulation()
    pyb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pyb.setGravity(0, 0, -9.81)
    pyb.loadURDF("plane.urdf")

    panda_id = pyb.loadURDF("franka_panda/panda.urdf", basePosition=[0, 0, 0], useFixedBase=True)
    configure_gripper_friction(panda_id)
    move_arm_to_home(panda_id)
    step_simulation(seconds=1.0)
    open_gripper(panda_id)
    step_simulation(seconds=0.5)
    return panda_id


def run_case(panda_id, name, target):
    move_ee_to_position(panda_id, target)
    step_simulation(seconds=2.0)
    link_position, pinch_center, left_finger, right_finger = gripper_points(panda_id)

    return {
        "name": name,
        "target": target,
        "link_position": link_position,
        "pinch_center": pinch_center,
        "left_finger": left_finger,
        "right_finger": right_finger,
        "link_error": vector_error(link_position, target),
        "pinch_error": vector_error(pinch_center, target),
    }


def gripper_points(panda_id):
    link_position = pyb.getLinkState(panda_id, END_EFFECTOR_LINK_INDEX)[0]
    left_finger = pyb.getLinkState(panda_id, GRIPPER_JOINT_INDICES[0])[0]
    right_finger = pyb.getLinkState(panda_id, GRIPPER_JOINT_INDICES[1])[0]
    pinch_center = [(left_finger[index] + right_finger[index]) / 2 for index in range(3)]
    return link_position, pinch_center, left_finger, right_finger


def vector_error(actual, requested):
    return [actual[index] - requested[index] for index in range(3)]


def write_results(results, output_dir):
    path = output_dir / "tcp_offsets.csv"
    with path.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "target_name",
                "target_x",
                "target_y",
                "target_z",
                "link_x",
                "link_y",
                "link_z",
                "pinch_x",
                "pinch_y",
                "pinch_z",
                "link_error_x",
                "link_error_y",
                "link_error_z",
                "pinch_error_x",
                "pinch_error_y",
                "pinch_error_z",
                "pinch_error_xy",
                "pinch_error_xyz",
            ]
        )
        for result in results:
            pinch_error = result["pinch_error"]
            writer.writerow(
                [
                    result["name"],
                    *result["target"],
                    *result["link_position"],
                    *result["pinch_center"],
                    *result["link_error"],
                    *pinch_error,
                    (pinch_error[0] ** 2 + pinch_error[1] ** 2) ** 0.5,
                    sum(value**2 for value in pinch_error) ** 0.5,
                ]
            )


def write_report(results, output_dir):
    link_errors = [sum(value**2 for value in result["link_error"]) ** 0.5 for result in results]
    pinch_errors = [sum(value**2 for value in result["pinch_error"]) ** 0.5 for result in results]
    pinch_xy_errors = [
        (result["pinch_error"][0] ** 2 + result["pinch_error"][1] ** 2) ** 0.5
        for result in results
    ]

    with (output_dir / "report.md").open("w") as file:
        file.write("# TCP Offset Report\n\n")
        file.write(f"- Cases: {len(results)}\n")
        file.write(f"- Average link-11 XYZ error: {sum(link_errors) / len(link_errors):.4f} m\n")
        file.write(f"- Max link-11 XYZ error: {max(link_errors):.4f} m\n")
        file.write(f"- Average pinch-center XY error: {sum(pinch_xy_errors) / len(pinch_xy_errors):.4f} m\n")
        file.write(f"- Max pinch-center XY error: {max(pinch_xy_errors):.4f} m\n")
        file.write(f"- Average pinch-center XYZ error: {sum(pinch_errors) / len(pinch_errors):.4f} m\n")
        file.write(f"- Max pinch-center XYZ error: {max(pinch_errors):.4f} m\n")


def plot_offsets(results, output_dir):
    for result in results:
        target = result["target"]
        pinch = result["pinch_center"]
        plt.scatter(target[0], target[1], c="black", marker="x")
        plt.arrow(target[0], target[1], pinch[0] - target[0], pinch[1] - target[1], head_width=0.01)
        plt.text(target[0], target[1], result["name"], fontsize=8)

    plt.title("TCP offset: requested target -> actual pinch center")
    plt.xlabel("world x")
    plt.ylabel("world y")
    plt.grid(True)
    plt.axis("equal")
    plt.savefig(output_dir / "tcp_offset_plot.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    main()
