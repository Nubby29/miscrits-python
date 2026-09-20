# Version: explicit move icon crop diagnostics

import cv2
import numpy as np
import pyautogui


MOVES_TEMPLATE = "templates/battle/moves.png"

ELEMENTS = [
    "fire",
    "water",
    "nature",
    "wind",
    "earth",
    "lightning",
    "normal",
    "buff",
    "debuff",
    "effect",
]

ELEMENT_TEMPLATES = {
    element: f"templates/elements/{element}.png"
    for element in ELEMENTS
}


MOVE_COUNT = 4

# Explicit icon offsets from the detected move-bar origin.
# These replace cumulative slot-width calculations so each
# move icon has an independent, stable crop location.
MOVE_ICON_OFFSETS_X = [
    8,    # Move 1
    202,  # Move 2
    397,  # Move 3
    592,  # Move 4
]

MOVE_ICON_OFFSET_Y = 12
MOVE_ICON_WIDTH = 40
MOVE_ICON_HEIGHT = 40

# Diagnostic output directory.
DEBUG_MOVE_DIR = "debug/moves"


def load_element_templates():
    templates = {}

    for element, path in ELEMENT_TEMPLATES.items():

        image = cv2.imread(path)

        if image is None:
            print(f"[MOVE] Could not load {path}")
            continue

        templates[element] = image

    return templates


def find_moves_bar():

    screenshot = pyautogui.screenshot()

    frame = np.array(screenshot)
    frame = cv2.cvtColor(
        frame,
        cv2.COLOR_RGB2BGR
    )

    template = cv2.imread(MOVES_TEMPLATE)

    if template is None:
        raise FileNotFoundError(
            f"Could not load {MOVES_TEMPLATE}"
        )

    result = cv2.matchTemplate(
        frame,
        template,
        cv2.TM_CCOEFF_NORMED
    )

    _, confidence, _, location = cv2.minMaxLoc(result)

    print(
        f"[MOVE] Move bar confidence={confidence:.2f}"
    )

    if confidence < 0.8:
        print("[MOVE] Move bar not detected.")
        return None

    x, y = location

    print(
        f"[MOVE] Move bar found at ({x}, {y})"
    )

    return frame, x, y


def detect_element(icon, templates):

    best_element = None
    best_confidence = 0.0

    hsv = cv2.cvtColor(icon, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([15, 80, 100])
    upper_yellow = np.array([40, 255, 255])

    yellow_mask = cv2.inRange(
        hsv,
        lower_yellow,
        upper_yellow
    )

    cleaned_icon = icon.copy()

    if cv2.countNonZero(yellow_mask) > 0:

        cleaned_icon = cv2.inpaint(
            cleaned_icon,
            yellow_mask,
            3,
            cv2.INPAINT_TELEA
        )

    scales = [
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
        1.00,
        1.05,
        1.10,
        1.15,
        1.20,
        1.25,
        1.30,
    ]

    for element, original_template in templates.items():

        template = cv2.GaussianBlur(
            original_template,
            (3, 3),
            0
        )

        original_height, original_width = template.shape[:2]

        for scale in scales:

            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            if new_width < 5 or new_height < 5:
                continue

            if (
                new_width > cleaned_icon.shape[1]
                or new_height > cleaned_icon.shape[0]
            ):
                continue

            resized = cv2.resize(
                template,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA
            )

            result = cv2.matchTemplate(
                cleaned_icon,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            _, confidence, _, _ = cv2.minMaxLoc(result)

            if confidence > best_confidence:

                best_confidence = confidence
                best_element = element

    for element, original_template in templates.items():

        template = cv2.GaussianBlur(
            original_template,
            (3, 3),
            0
        )

        original_height, original_width = template.shape[:2]

        for scale in scales:

            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            if new_width < 5 or new_height < 5:
                continue

            if (
                new_width > icon.shape[1]
                or new_height > icon.shape[0]
            ):
                continue

            resized = cv2.resize(
                template,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA
            )

            result = cv2.matchTemplate(
                icon,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            _, confidence, _, _ = cv2.minMaxLoc(result)

            if confidence > best_confidence:

                best_confidence = confidence
                best_element = element

    return best_element, best_confidence


def diagnose_element_matches(icon, templates):
    """
    Prints the best match confidence for every element template
    against both the original and yellow-cleaned icon.
    This is diagnostic only and does not change recognition.
    """

    hsv = cv2.cvtColor(icon, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([15, 80, 100])
    upper_yellow = np.array([40, 255, 255])

    yellow_mask = cv2.inRange(
        hsv,
        lower_yellow,
        upper_yellow
    )

    cleaned_icon = icon.copy()

    if cv2.countNonZero(yellow_mask) > 0:
        cleaned_icon = cv2.inpaint(
            cleaned_icon,
            yellow_mask,
            3,
            cv2.INPAINT_TELEA
        )

    scales = [
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
        1.00,
        1.05,
        1.10,
        1.15,
        1.20,
        1.25,
        1.30,
    ]

    diagnostics = []

    for element, original_template in templates.items():

        template = cv2.GaussianBlur(
            original_template,
            (3, 3),
            0
        )

        original_height, original_width = template.shape[:2]

        best_original = 0.0
        best_cleaned = 0.0
        best_original_scale = None
        best_cleaned_scale = None

        for scale in scales:

            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            if new_width < 5 or new_height < 5:
                continue

            if (
                new_width > icon.shape[1]
                or new_height > icon.shape[0]
            ):
                continue

            resized = cv2.resize(
                template,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA
            )

            original_result = cv2.matchTemplate(
                icon,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            _, original_confidence, _, _ = cv2.minMaxLoc(
                original_result
            )

            if original_confidence > best_original:
                best_original = original_confidence
                best_original_scale = scale

            cleaned_result = cv2.matchTemplate(
                cleaned_icon,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            _, cleaned_confidence, _, _ = cv2.minMaxLoc(
                cleaned_result
            )

            if cleaned_confidence > best_cleaned:
                best_cleaned = cleaned_confidence
                best_cleaned_scale = scale

        diagnostics.append(
            (
                element,
                best_original,
                best_original_scale,
                best_cleaned,
                best_cleaned_scale,
            )
        )

    diagnostics.sort(
        key=lambda item: max(item[1], item[3]),
        reverse=True
    )

    for (
        element,
        original_confidence,
        original_scale,
        cleaned_confidence,
        cleaned_scale,
    ) in diagnostics:
        print(
            f"[DIAG] {element.upper():<10} "
            f"original={original_confidence:.2f} "
            f"@{original_scale if original_scale is not None else '-'} "
            f"cleaned={cleaned_confidence:.2f} "
            f"@{cleaned_scale if cleaned_scale is not None else '-'}"
        )

    print("[DIAG] ------------------------------")


def save_move_crop(move_number, icon, slot=None):
    """
    Saves the live move crop for visual inspection.
    This is diagnostic only.
    """

    import os

    os.makedirs(DEBUG_MOVE_DIR, exist_ok=True)

    icon_path = (
        f"{DEBUG_MOVE_DIR}/move_{move_number}_icon.png"
    )

    cv2.imwrite(icon_path, icon)

    if slot is not None:
        slot_path = (
            f"{DEBUG_MOVE_DIR}/move_{move_number}_slot.png"
        )
        cv2.imwrite(slot_path, slot)

    print(
        f"[DIAG] Saved Move {move_number} crop: "
        f"{icon_path}"
    )


def detect_moves():

    print("[MOVE] Scanning moves left to right...")

    found = find_moves_bar()

    if found is None:
        return [None, None, None, None]

    frame, bar_x, bar_y = found

    templates = load_element_templates()

    moves = []

    for index in range(MOVE_COUNT):

        move_number = index + 1

        # Each move now has an explicit independent icon offset.
        icon_x = bar_x + MOVE_ICON_OFFSETS_X[index]
        icon_y = bar_y + MOVE_ICON_OFFSET_Y

        # Keep the original slot concept for enchanted detection.
        # Slot boundaries are based on the midpoint between adjacent
        # explicit icon origins, avoiding cumulative float rounding.
        if index == 0:
            slot_x = bar_x
        else:
            slot_x = (
                bar_x
                + (
                    MOVE_ICON_OFFSETS_X[index - 1]
                    + MOVE_ICON_WIDTH
                )
            )

        if index < MOVE_COUNT - 1:
            next_icon_x = (
                bar_x
                + MOVE_ICON_OFFSETS_X[index + 1]
            )
            slot_right = next_icon_x
        else:
            slot_right = bar_x + 779

        slot_width = max(1, slot_right - slot_x)

        slot = frame[
            bar_y:bar_y + 74,
            slot_x:slot_x + slot_width
        ]

        enchanted = is_enchanted(slot)

        icon = frame[
            icon_y:icon_y + MOVE_ICON_HEIGHT,
            icon_x:icon_x + MOVE_ICON_WIDTH
        ]

        print(
            f"[MOVE] Move {move_number}: "
            f"slot=({slot_x},{bar_y}) "
            f"icon=({icon_x},{icon_y}) "
            f"size={icon.shape[1]}x{icon.shape[0]}"
        )

        save_move_crop(
            move_number,
            icon,
            slot
        )

        element, confidence = detect_element(
            icon,
            templates
        )

        diagnose_element_matches(
            icon,
            templates
        )

        if element is None or confidence < 0.80:

            print(
                f"[MOVE] Move {move_number}: "
                f"UNKNOWN "
                f"confidence={confidence:.2f} "
                f"enchanted={enchanted}"
            )

            moves.append(None)

        else:

            print(
                f"[MOVE] Move {move_number}: "
                f"{element.upper()} "
                f"confidence={confidence:.2f} "
                f"enchanted={enchanted}"
            )

            moves.append(element)

    print(f"[MOVE] Moves = {moves}")

    return moves


def is_enchanted(slot):
    """
    Detects the yellow enchanted background
    of a move button.
    """

    hsv = cv2.cvtColor(slot, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([15, 80, 120])
    upper_yellow = np.array([40, 255, 255])

    mask = cv2.inRange(
        hsv,
        lower_yellow,
        upper_yellow
    )

    yellow_pixels = cv2.countNonZero(mask)

    total_pixels = slot.shape[0] * slot.shape[1]

    percentage = yellow_pixels / total_pixels

    return percentage > 0.20
