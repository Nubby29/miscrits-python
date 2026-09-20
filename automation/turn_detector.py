from automation.detector import find_image

YOUR_TURN_TEMPLATE = "templates/battle/its_your_turn.png"


def is_my_turn():
    result = find_image(
        YOUR_TURN_TEMPLATE,
        confidence=0.8
    )

    if result:
        print(
            f"[TURN] YOUR TURN "
            f"confidence={result['confidence']:.2f}"
        )
        return True

    print("[TURN] OPPONENT TURN")
    return False