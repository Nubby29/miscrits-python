import time

from automation.detector import find_image
from automation.mouse import click_position


def wait_for_image(
    template,
    confidence=0.8,
    timeout=10,
    interval=0.2
):
    print(f"[WAIT] Looking for {template}")

    start = time.time()

    while time.time() - start < timeout:

        result = find_image(
            template,
            confidence=confidence
        )

        if result:
            print(
                f"[FOUND] {template} "
                f"at ({result['x']}, {result['y']}) "
                f"confidence={result['confidence']:.2f}"
            )

            return result

        time.sleep(interval)

    print(f"[TIMEOUT] {template}")

    return None


def find_and_click(
    template,
    confidence=0.8,
    timeout=10
):
    print(f"[ACTION] Find and click: {template}")

    result = wait_for_image(
        template,
        confidence=confidence,
        timeout=timeout
    )

    if not result:
        print(f"[FAILED] Could not find {template}")
        return False

    click_position(
    result["x"],
    result["y"]
)

    return True