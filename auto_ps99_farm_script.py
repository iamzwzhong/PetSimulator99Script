import threading
import pyautogui
import time
import autoit
import keyboard

"""
TODO: Auto top up fruits
TODO: Auto combine keys
"""

# Images of PS99 Things
MENU_IMG = "images/menu.png"
ITEMS_IMG = "images/items.png"
PARTY_BOX_IMG = "images/party_box.png"
OK_IMG = "images/ok.png"
LUCKY_BLOCK_IMG = "images/lucky_block.png"
LARGE_GIFT_BAG_IMG = "images/large_gift_bag.png"
SMALL_GIFT_BAG_IMG = "images/small_gift_bag.png"
PINATA_IMG = "images/pinata.png"

# FLAGS
ENABLE_SCRIPT = False
OPEN_LUCKY_BLOCKS = True
OPEN_PARTY_BOXES = True
OPEN_LARGE_GIFT_BAGS = True
OPEN_SMALL_GIFT_BAGS = True
OPEN_PINATA = True


def getImagePosition(image: str):
    try:
        pos = pyautogui.locateCenterOnScreen(image, confidence=0.9, grayscale=True)
        return pos
    except pyautogui.ImageNotFoundException:
        return None


def moveAndClick(pos):
    if pos != None:
        x, y = pos
        autoit.mouse_move(x, y)
        autoit.mouse_click("left")


def farm():
    while True:
        try:
            if not ENABLE_SCRIPT:
                continue
            # Is there any errors on the screen?
            ok_pos = getImagePosition(OK_IMG)
            if ok_pos != None:
                print("Closing the error...")
                moveAndClick(ok_pos)
                continue

            items_pos = getImagePosition(ITEMS_IMG)
            if items_pos == None:
                # Can't see item icon. Open the menu.
                print("Opening the menu...")
                menu_pos = getImagePosition(MENU_IMG)
                moveAndClick(menu_pos)
                continue

            moveAndClick(items_pos)

            lucky_block_pos = getImagePosition(LUCKY_BLOCK_IMG)
            if lucky_block_pos != None and OPEN_LUCKY_BLOCKS:
                # Try to use a lucky block
                print("Found a lucky block. Using a lucky block.")
                moveAndClick(lucky_block_pos)
                continue

            pinata_pos = getImagePosition(PINATA_IMG)
            if pinata_pos != None and OPEN_PINATA:
                # Try to use a pinata
                print("Found a pinata. Using a pinata.")
                moveAndClick(pinata_pos)
                continue

            large_gift_bag_pos = getImagePosition(LARGE_GIFT_BAG_IMG)
            while large_gift_bag_pos != None and OPEN_LARGE_GIFT_BAGS:
                # Keep opening large gift bags
                print("Found a large gift bag. Opening large gift bag.")
                moveAndClick(large_gift_bag_pos)
                autoit.mouse_move(0, 0)
                large_gift_bag_pos = getImagePosition(LARGE_GIFT_BAG_IMG)

            small_gift_bag_pos = getImagePosition(SMALL_GIFT_BAG_IMG)
            while small_gift_bag_pos != None and OPEN_SMALL_GIFT_BAGS:
                # Keep opening small gift bags
                print("Found a small gift bag. Opening small gift bag.")
                moveAndClick(small_gift_bag_pos)
                autoit.mouse_move(0, 0)
                small_gift_bag_pos = getImagePosition(SMALL_GIFT_BAG_IMG)

            party_box_pos = getImagePosition(PARTY_BOX_IMG)
            if party_box_pos != None and OPEN_PARTY_BOXES:
                # Try to use a party box
                print("Found a party box. Using a party box.")
                moveAndClick(party_box_pos)
                continue
        finally:
            time.sleep(1)

thread = threading.Thread(target=farm)
thread.daemon = True
thread.start()

while True:
    if keyboard.is_pressed("F1"):
        ENABLE_SCRIPT = True
    elif keyboard.is_pressed("F2"):
        ENABLE_SCRIPT = False
    elif keyboard.is_pressed("F3"):
        break
