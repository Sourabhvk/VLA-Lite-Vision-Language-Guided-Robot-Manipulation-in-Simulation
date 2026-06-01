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
