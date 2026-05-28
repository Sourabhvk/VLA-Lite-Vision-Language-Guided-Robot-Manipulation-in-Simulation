from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


MIN_RED_CONFIDENCE = 0.65
MIN_CONTOUR_AREA = 120


def detect_red_cube(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    lower_red_1 = np.array([0, 140, 120])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([170, 140, 120])
    upper_red_2 = np.array([180, 255, 255])

    mask = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask |= cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, mask

    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)
    if area < MIN_CONTOUR_AREA:
        return None, mask

    x, y, w, h = cv2.boundingRect(contour)
    confidence = red_cube_confidence(hsv, mask, x, y, w, h, area)
    if confidence < MIN_RED_CONFIDENCE:
        return None, mask

    center = (x + w // 2, y + h // 2)
    return {"center": center, "bbox": (x, y, w, h), "confidence": confidence}, mask


def red_cube_confidence(hsv, mask, x, y, w, h, area):
    bbox_area = max(w * h, 1)
    red_fill = area / bbox_area
    square_score = min(w, h) / max(w, h)

    # The cube is a bright saturated red in our sim, so weak red pixels should not pass.
    roi_hsv = hsv[y : y + h, x : x + w]
    roi_mask = mask[y : y + h, x : x + w] > 0
    if not np.any(roi_mask):
        return 0.0

    saturation_score = np.mean(roi_hsv[:, :, 1][roi_mask]) / 255
    value_score = np.mean(roi_hsv[:, :, 2][roi_mask]) / 255
    confidence = 0.35 * red_fill + 0.25 * square_score + 0.25 * saturation_score + 0.15 * value_score
    return float(min(confidence, 1.0))


def save_red_detection_debug(rgb, detection, path=None):
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = f"outputs/red_detection_{timestamp}.png"

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
    print(f"Saved red detection debug: {output_path}")
