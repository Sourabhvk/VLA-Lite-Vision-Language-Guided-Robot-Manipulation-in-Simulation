SUPPORTED_COLORS = {"violet", "blue", "green", "yellow", "orange", "red"}
SUPPORTED_QUANTITIES = {"one", "all"}


def validate_task(task):
    # Keep LLM output on a small safe schema before robot code sees it.
    if task.get("action") != "pick_place":
        raise ValueError("Only pick_place commands are supported")

    source = task.get("source", {})
    target = task.get("target", {})

    if source.get("type") != "cube":
        raise ValueError("Source must be a cube")
    if source.get("color") not in SUPPORTED_COLORS:
        raise ValueError(f"Unsupported cube color: {source.get('color')}")
    if source.get("quantity") not in SUPPORTED_QUANTITIES:
        raise ValueError("Quantity must be one or all")

    if target.get("type") != "tray":
        raise ValueError("Target must be a tray")
    if target.get("color") != "blue":
        raise ValueError("Only the blue tray exists right now")

    return task
