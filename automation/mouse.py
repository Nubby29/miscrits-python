import time
import pyautogui


def click_position(
    x,
    y,
    move_duration=0.3,
    click_duration=0.25
):
    print(f"[CLICK] Moving to ({x}, {y})")

    pyautogui.moveTo(
        x,
        y,
        duration=move_duration
    )

    time.sleep(0.1)

    print("[CLICK] Mouse down")

    pyautogui.mouseDown()

    time.sleep(click_duration)

    print("[CLICK] Mouse up")

    pyautogui.mouseUp()

    print("[CLICK] Click completed")