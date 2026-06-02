# File: src/sim/console_focus.py
# Intent: Brings the launching Windows console forward before text command input.
# Usage: Called by keyboard command mode so input() is visible to the user.
# Presets: Windows ShowWindow restore code 9.
# Connects: src/sim/keyboard_controls.py; Windows user32/kernel32 APIs.
# User values: None.
#
# Functions:
# - focus_console_window(): Focuses the console on Windows and no-ops elsewhere.

import ctypes
import os

def focus_console_window():
    if os.name != "nt":
        return

    # Bring the PowerShell/cmd window that launched this process to the front.
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 9)
        ctypes.windll.user32.SetForegroundWindow(console_window)
