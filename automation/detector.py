import cv2
import pyautogui


def find_image(template_path, confidence=0.8):
    screenshot = pyautogui.screenshot()

    screenshot = cv2.cvtColor(
        __import__("numpy").array(screenshot),
        cv2.COLOR_RGB2BGR
    )

    template = cv2.imread(template_path)

    if template is None:
        raise FileNotFoundError(
            f"Template not found: {template_path}"
        )

    result = cv2.matchTemplate(
        screenshot,
        template,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_value, _, max_location = cv2.minMaxLoc(result)

    if max_value < confidence:
        return None

    height, width = template.shape[:2]

    x = max_location[0]
    y = max_location[1]

    center_x = x + width // 2
    center_y = y + height // 2

    return {
        "x": center_x,
        "y": center_y,
        "confidence": max_value
    }