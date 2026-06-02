SUPPORTED_ACTIONS = {"pick", "pick_place", "place"}
SUPPORTED_QUANTITIES = {"one", "all"}
KNOWN_COLOR_HSV_RANGES = {
    "red": [
        {"lower": [0, 140, 120], "upper": [10, 255, 255]},
        {"lower": [170, 140, 120], "upper": [180, 255, 255]},
    ],
    "orange": [{"lower": [10, 120, 120], "upper": [25, 255, 255]}],
    "yellow": [{"lower": [25, 100, 120], "upper": [40, 255, 255]}],
    "green": [{"lower": [45, 100, 100], "upper": [80, 255, 255]}],
    "blue": [{"lower": [100, 120, 80], "upper": [130, 255, 255]}],
    "violet": [{"lower": [135, 80, 80], "upper": [165, 255, 255]}],
    "purple": [{"lower": [135, 80, 80], "upper": [165, 255, 255]}],
}


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
    if source.get("quantity") not in SUPPORTED_QUANTITIES:
        raise ValueError("Quantity must be one or all")
    apply_known_color_hsv_ranges(source)
    validate_hsv_ranges(source.get("hsv_ranges"))


def apply_known_color_hsv_ranges(source):
    color_text = str(source.get("color_text", "")).lower()
    for color, ranges in KNOWN_COLOR_HSV_RANGES.items():
        if color in color_text:
            source["hsv_ranges"] = ranges
            return


def validate_target(target):
    if target.get("type") != "tray":
        raise ValueError("Target must be a tray")
    if target.get("color") != "blue":
        raise ValueError("Only the blue tray exists right now")


def validate_hsv_ranges(ranges):
    if not isinstance(ranges, list) or not ranges:
        raise ValueError("Source must include hsv_ranges")

    for hsv_range in ranges:
        lower = hsv_range.get("lower") if isinstance(hsv_range, dict) else None
        upper = hsv_range.get("upper") if isinstance(hsv_range, dict) else None
        if not valid_hsv_triplet(lower) or not valid_hsv_triplet(upper):
            raise ValueError(f"Invalid HSV range: {hsv_range}")


def valid_hsv_triplet(value):
    return (
        isinstance(value, list)
        and len(value) == 3
        and 0 <= value[0] <= 180
        and 0 <= value[1] <= 255
        and 0 <= value[2] <= 255
    )
