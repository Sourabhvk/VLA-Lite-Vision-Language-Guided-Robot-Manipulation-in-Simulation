# File: src/sim/logging_utils.py
# Intent: Provides a tiny verbose logging switch for keyboard/control messages.
# Usage: Enabled by panda_env.py when the --verbose flag is passed.
# Presets: VERBOSE defaults to False.
# Connects: src/sim/panda_env.py; src/sim/keyboard_controls.py.
# User values: --verbose CLI flag.
#
# Functions:
# - set_verbose(): Updates the module-wide verbose flag.
# - log(): Prints a message only when verbose mode is enabled.

VERBOSE = False


def set_verbose(enabled):
    global VERBOSE
    VERBOSE = enabled


def log(message):
    if VERBOSE:
        print(message)
