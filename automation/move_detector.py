# Version: diagnostic move-icon crop logging

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


# The move bar contains 4 equal slots.
MOVE_COUNT = 4


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

    # --------------------------------
    # REMOVE YELLOW ENCHANT OVERLAY
    # --------------------------------

    hsv = cv2.cvtColor(icon, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([15, 80, 100])
    upper_yellow = np.array([40, 255, 255])

    yellow_mask = cv2.inRange(
        hsv,
        lower_yellow,
        upper_yellow
    )

    # Keep the original icon intact.
    # Create a cleaned version only for enchanted icons.
    cleaned_icon = icon.copy()

    if cv2.countNonZero(yellow_mask) > 0:

        cleaned_icon = cv2.inpaint(
            cleaned_icon,
            yellow_mask,
            3,
            cv2.INPAINT_TELEA
        )

    # --------------------------------
    # TEMPLATE SCALES
    # --------------------------------

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

    # --------------------------------
    # MATCH CLEANED ICON
    # --------------------------------

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

            # IMPORTANT:
            # Never give matchTemplate a template
            # larger than the icon.
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

    # --------------------------------
    # FALLBACK: ORIGINAL ICON
    # --------------------------------
    #
    # This is important because the yellow
    # removal can sometimes make a normal
    # icon match worse.
    #

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


def detect_moves():

    print("[MOVE] Scanning moves left to right...")

    found = find_moves_bar()

    if found is None:
        return [None, None, None, None]

    frame, bar_x, bar_y = found

    templates = load_element_templates()

    # moves.png is 779 x 74
    bar_width = 779

    # Four equal move slots
    slot_width = bar_width / 4

    moves = []

    for index in range(4):

        move_number = index + 1

        slot_x = int(bar_x + (index * slot_width))
        slot_y = bar_y

        # --------------------------------
        # WHOLE MOVE SLOT
        # --------------------------------

        slot = frame[
            slot_y:slot_y + 74,
            slot_x:slot_x + int(slot_width)
        ]

        # --------------------------------
        # CHECK ENCHANTED STATE
        # --------------------------------

        enchanted = is_enchanted(slot)

        # --------------------------------
        # ICON ONLY
        # --------------------------------

        icon_x = slot_x + 8
        icon_y = slot_y + 12

        icon_width = 40
        icon_height = 40

        icon = frame[
            icon_y:icon_y + icon_height,
            icon_x:icon_x + icon_width
        ]

        print(
            f"[MOVE] Move {move_number}: "
            f"slot=({slot_x},{slot_y}) "
            f"icon=({icon_x},{icon_y}) "
            f"size={icon.shape[1]}x{icon.shape[0]}"
        )

        element, confidence = detect_element(
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

    # Yellow range
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