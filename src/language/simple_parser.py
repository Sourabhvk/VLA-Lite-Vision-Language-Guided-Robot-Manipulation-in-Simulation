SUPPORTED_COLORS = ("violet", "blue", "green", "yellow", "orange", "red")


def parse_command(command):
    command = command.lower()

    if "pick" not in command or "place" not in command:
        raise ValueError(f"Unsupported command: {command}")

    source_color = find_color(command, "cube")
    target_color = find_color(command, "tray")
    quantity = "all" if "all" in command or "cubes" in command else "one"

    # Keep parser output structured so an LLM can later produce the same shape.
    return {
        "action": "pick_place",
        "source": {"type": "cube", "color": source_color, "quantity": quantity},
        "target": {"type": "tray", "color": target_color},
    }


def find_color(command, object_type):
    for color in SUPPORTED_COLORS:
        if f"{color} {object_type}" in command:
            return color

    raise ValueError(f"Missing supported {object_type} color in: {command}")
