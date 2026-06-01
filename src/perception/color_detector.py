from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


MIN_COLOR_CONFIDENCE = 0.65
MIN_CONTOUR_AREA = 120
MAX_IMAGE_AREA_RATIO = 0.15

COLOR_RANGES = {
    "red": [((0, 140, 120), (10, 255, 255)), ((170, 140, 120), (180, 255, 255))],
    "orange": [((10, 120, 120), (25, 255, 255))],
    "yellow": [((25, 100, 120), (40, 255, 255))],
    "green": [((45, 100, 100), (80, 255, 255))],
    "blue": [((100, 120, 80), (130, 255, 255))],
    "violet": [((135, 80, 80), (165, 255, 255))],
}


def detect_colored_cube(rgb, color):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = color_mask(hsv, color)
    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, mask

    detection = best_cube_detection(hsv, mask, contours, rgb.shape)
    if detection is None or detection["confidence"] < MIN_COLOR_CONFIDENCE:
        return None, mask

    detection["color"] = color
    return detection, mask


def color_mask(hsv, color):
    if color not in COLOR_RANGES:
        raise ValueError(f"Unsupported cube color: {color}")

    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in COLOR_RANGES[color]:
        mask |= cv2.inRange(hsv, np.array(lower), np.array(upper))
    return mask


def best_cube_detection(hsv, mask, contours, image_shape):
    best = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_CONTOUR_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        confidence = cube_confidence(hsv, mask, x, y, w, h, area, image_shape)
        if best is None or confidence > best["confidence"]:
            best = {
                "center": (x + w // 2, y + h // 2),
                "bbox": (x, y, w, h),
                "confidence": confidence,
            }

    return best


def cube_confidence(hsv, mask, x, y, w, h, area, image_shape):
    bbox_area = max(w * h, 1)
    color_fill = area / bbox_area
    square_score = min(w, h) / max(w, h)
    image_area = image_shape[0] * image_shape[1]
    size_score = 1.0 if bbox_area / image_area <= MAX_IMAGE_AREA_RATIO else 0.0

    # Sim cubes are small, bright, saturated blocks; this also helps reject the blue tray.
    roi_hsv = hsv[y : y + h, x : x + w]
    roi_mask = mask[y : y + h, x : x + w] > 0
    if not np.any(roi_mask):
        return 0.0

    saturation_score = np.mean(roi_hsv[:, :, 1][roi_mask]) / 255
    value_score = np.mean(roi_hsv[:, :, 2][roi_mask]) / 255
    confidence = (
        0.30 * color_fill
        + 0.25 * square_score
        + 0.20 * saturation_score
        + 0.15 * value_score
        + 0.10 * size_score
    )
    return float(min(confidence, 1.0))


def save_color_detection_debug(rgb, detection, color, path=None):
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = f"outputs/{color}_detection_{timestamp}.png"

    debug = rgb.copy()
    if detection is not None:
        x, y, w, h = detection["bbox"]
        cx, cy = detection["center"]
        cv2.rectangle(debug, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.circle(debug, (cx, cy), 6, (0, 255, 0), -1)
        cv2.putText(
            debug,
            f"px=({cx},{cy})",
            (x, max(y - 35, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        if "confidence" in detection:
            cv2.putText(
                debug,
                f"conf={detection['confidence']:.2f}",
                (x, min(y + h + 28, debug.shape[0] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        if "world" in detection:
            wx, wy, wz = detection["world"]
            cv2.putText(
                debug,
                f"world=({wx:.3f},{wy:.3f},{wz:.3f})",
                (x, max(y - 8, 45)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), cv2.cvtColor(debug, cv2.COLOR_RGB2BGR))
    print(f"Saved {color} detection debug: {output_path}")
