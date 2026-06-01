SUPPORTED_ACTIONS = {"pick", "pick_place", "place"}
SUPPORTED_COLORS = {"violet", "blue", "green", "yellow", "orange", "red"}
SUPPORTED_QUANTITIES = {"one", "all"}


def validate_task(task):
    # Keep LLM output on a small safe schema before robot code sees it.
    action = task.get("action")
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported action: {action}")

    if action in {"pick", "pick_place"}:
        validate_source(task.get("source", {}))

    if action in {"pick_place", "place"}:
        task.setdefault("target", {"type": "tray", "color": "blue"})
        validate_target(task["target"])

    return task


def validate_source(source):
    if source.get("type") != "cube":
        raise ValueError("Source must be a cube")
    if source.get("color") not in SUPPORTED_COLORS:
        raise ValueError(f"Unsupported cube color: {source.get('color')}")
    if source.get("quantity") not in SUPPORTED_QUANTITIES:
        raise ValueError("Quantity must be one or all")


def validate_target(target):
    if target.get("type") != "tray":
        raise ValueError("Target must be a tray")
    if target.get("color") != "blue":
        raise ValueError("Only the blue tray exists right now")
