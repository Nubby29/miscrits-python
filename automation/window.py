import time
import pygetwindow as gw


def focus_miscrits():
    windows = gw.getAllWindows()

    for window in windows:

        if window.title.strip() == "Miscrits":

            print(f"[WINDOW] Found: {window.title}")

            if window.isMinimized:
                window.restore()

            window.activate()

            time.sleep(0.5)

            print("[WINDOW] Miscrits window activated.")

            return True

    print("[WINDOW] Miscrits window not found.")

    return False