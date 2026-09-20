import time

from automation.actions import find_and_click
from automation.detector import find_image
from automation.turn_detector import is_my_turn
from automation.move_detector import detect_moves


YOUR_TURN_TEMPLATE = "templates/battle/its_your_turn.png"
WIN_TEMPLATE = "templates/battle/win.png"
CONTINUE_TEMPLATE = "templates/battle/continue.png"

WISP_TEMPLATE = "templates/moves/e_wisp.png"

MAX_EXP_TEMPLATE = "templates/state/max_exp.png"
E_TRAIN_TEMPLATE = "templates/buttons/e_train.png"
READY_TO_TRAIN_TEMPLATE = "templates/state/ready_to_train.png"
M_TRAIN_TEMPLATE = "templates/state/m_train.png"


def battle_won():
    result = find_image(
        WIN_TEMPLATE,
        confidence=0.8
    )

    if result:
        print(
            f"[BATTLE] WIN detected "
            f"confidence={result['confidence']:.2f}"
        )
        return True

    return False


def handle_training():
    print("[TRAIN] Max EXP detected.")

    print("[TRAIN] Looking for E Train...")

    if not find_and_click(
        E_TRAIN_TEMPLATE,
        confidence=0.8,
        timeout=10
    ):
        print("[TRAIN] E Train button not found.")
        return False

    print("[TRAIN] E Train clicked.")
    print("[TRAIN] Miscrits menu opened.")

    print("[TRAIN] Looking for Ready to Train...")

    if not find_and_click(
        READY_TO_TRAIN_TEMPLATE,
        confidence=0.8,
        timeout=10
    ):
        print("[TRAIN] Ready to Train not found.")
        return False

    print("[TRAIN] Ready to Train clicked.")

    print("[TRAIN] Looking for M Train...")

    if not find_and_click(
        M_TRAIN_TEMPLATE,
        confidence=0.8,
        timeout=10
    ):
        print("[TRAIN] M Train not found.")
        return False

    print("[TRAIN] M Train clicked.")
    print("[TRAIN] Training completed.")

    return True


def finish_battle():
    print("[BATTLE] Victory screen detected!")

    # --------------------------------
    # CHECK MAX EXP
    # --------------------------------
    max_exp = find_image(
        MAX_EXP_TEMPLATE,
        confidence=0.8
    )

    if max_exp:
        print(
            f"[BATTLE] Max EXP detected "
            f"confidence={max_exp['confidence']:.2f}"
        )
        max_exp_detected = True
    else:
        print("[BATTLE] Max EXP not detected.")
        max_exp_detected = False

    # --------------------------------
    # CLICK CONTINUE
    # --------------------------------
    if not find_and_click(
        CONTINUE_TEMPLATE,
        confidence=0.8,
        timeout=10
    ):
        print("[BATTLE] Continue button not found.")
        return "win_continue_failed"

    print("[BATTLE] Continue clicked.")

    # --------------------------------
    # TRAIN IF MAX EXP
    # --------------------------------
    if max_exp_detected:

        print("[BATTLE] Starting training sequence...")

        if not handle_training():
            print("[BATTLE] Training sequence failed.")
            return "training_failed"

    print("[BATTLE] Battle finished.")

    return "won"


def wait_for_turn_indicator_to_disappear(timeout=10):
    print("[BATTLE] Waiting for turn indicator to disappear...")

    start = time.time()

    while time.time() - start < timeout:

        if battle_won():
            return True

        result = find_image(
            YOUR_TURN_TEMPLATE,
            confidence=0.8
        )

        if not result:
            print("[BATTLE] Turn indicator disappeared.")
            return True

        time.sleep(0.2)

    print("[BATTLE] Turn indicator did not disappear.")
    return False


def battle():
    print("[BATTLE] Battle started.")

    while True:

        # --------------------------------
        # CHECK FOR VICTORY
        # --------------------------------
        if battle_won():
            return finish_battle()

        # --------------------------------
        # WAIT FOR OUR TURN
        # --------------------------------
        print("[BATTLE] Waiting for our turn...")

        while True:

            # Battle could finish while waiting
            if battle_won():
                return finish_battle()

            if is_my_turn():
                print("[BATTLE] It's our turn!")

                moves = detect_moves()

                print(f"[BATTLE] Detected moves: {moves}")

                break

            print("[BATTLE] Not our turn. Waiting...")
            time.sleep(0.5)

        # --------------------------------
        # USE WISP
        # --------------------------------
        if find_and_click(
            WISP_TEMPLATE,
            confidence=0.8,
            timeout=10
        ):
            print("[BATTLE] Wisp selected.")

        else:
            print("[BATTLE] Wisp was not found.")
            return "no_move"

        # --------------------------------
        # WAIT FOR TURN INDICATOR TO CLEAR
        # --------------------------------
        wait_for_turn_indicator_to_disappear()

        time.sleep(0.5)

        print("[BATTLE] Move completed. Checking next turn...")