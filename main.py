import time

from automation.window import focus_miscrits
from automation.explore import explore
from automation.battle import battle


print("[BOT] Starting in 3 seconds...")
time.sleep(3)


# Focus Miscrits
if not focus_miscrits():
    print("[BOT] Stopping because Miscrits was not found.")
    exit()


time.sleep(1)


while True:

    state = explore()

    if state == "battle":
        print("[BOT] Entered battle!")

        result = battle()

        if result == "won":
            print("[BOT] Battle won!")
            print("[BOT] Returning to exploration...")
            time.sleep(1)

        else:
            print(f"[BOT] Battle ended with state: {result}")
            break

    elif state == "no_target":
        print("[BOT] No exploration target found.")
        time.sleep(1)

    else:
        print("[BOT] Unknown state.")
        break