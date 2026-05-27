def parse_command(command):
    command = command.lower()

    if "red cube" in command and "blue tray" in command:
        return {"source": "red_cube", "target": "blue_tray"}

    raise ValueError(f"Unsupported command: {command}")
