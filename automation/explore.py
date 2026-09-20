import time

from automation.actions import find_and_click, wait_for_image


def explore():
    print("[EXPLORE] Looking for exploration targets...")

    targets = [
        "templates/exploration/rock.png",
        "templates/exploration/bush.png",
        "templates/exploration/sunflower.png",
        "templates/exploration/w_grass.png",
        "templates/exploration/w_grass2.png",
        "templates/exploration/w_grass3.png",
        "templates/exploration/s_tree.png",
    ]

    while True:

        # --------------------------------
        # LOOK FOR A TARGET
        # --------------------------------
        target_clicked = False

        for target in targets:

            print(f"[EXPLORE] Checking {target}")

            if find_and_click(
                target,
                confidence=0.8,
                timeout=3
            ):
                print(f"[EXPLORE] Clicked {target}")

                target_clicked = True

                # --------------------------------
                # WAIT FOR BATTLE
                # --------------------------------
                print("[EXPLORE] Waiting for battle...")

                battle = wait_for_image(
                    "screenshots/battle.png",
                    confidence=0.8,
                    timeout=5
                )

                if battle:
                    print("[EXPLORE] Battle detected!")
                    return "battle"

                print(
                    "[EXPLORE] No battle triggered. "
                    "Looking for another target..."
                )

                # Go back to the target search
                break

        # --------------------------------
        # NO TARGET FOUND
        # --------------------------------
        if not target_clicked:
            print("[EXPLORE] No exploration targets found.")
            time.sleep(1)



