import logging
import threading
import pyautogui
import time
import autoit
import keyboard
import PySimpleGUI as sg
from Constants import *
import SimpleGuiUtils

from Config import Config

# Setup logging for script
logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger()
logger.setLevel("DEBUG")

"""
TODO: Auto top up fruits
TODO: Auto combine keys
"""


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


def farm(config: Config):

    global ENABLE_SCRIPT

    while ENABLE_SCRIPT:
        try:
            ok_pos = getImagePosition(OK_IMG)
            if ok_pos != None:
                logger.info("Error found. Closing the error.")
                moveAndClick(ok_pos)
                continue

            items_pos = getImagePosition(ITEMS_IMG)
            if items_pos == None:
                logger.info("Items inventory icon not found. Opening the menu.")
                menu_pos = getImagePosition(MENU_IMG)
                moveAndClick(menu_pos)
                continue

            moveAndClick(items_pos)

            lucky_block_pos = getImagePosition(LUCKY_BLOCK_IMG)
            if lucky_block_pos != None and config.OPEN_LUCKY_BLOCKS:
                logger.info("Found a lucky block in inventory. Using lucky block.")
                moveAndClick(lucky_block_pos)
                continue

            pinata_pos = getImagePosition(PINATA_IMG)
            if pinata_pos != None and config.OPEN_PINATAS:
                logger.info("Found a pinata in inventory. Using pinata.")
                moveAndClick(pinata_pos)
                continue

            large_gift_bag_pos = getImagePosition(LARGE_GIFT_BAG_IMG)
            while large_gift_bag_pos != None and config.OPEN_LARGE_GIFT_BAGS:
                logger.info(
                    "Found a large gift bag in inventory. Opening large gift bag."
                )
                moveAndClick(large_gift_bag_pos)
                autoit.mouse_move(0, 0)
                large_gift_bag_pos = getImagePosition(LARGE_GIFT_BAG_IMG)

            small_gift_bag_pos = getImagePosition(SMALL_GIFT_BAG_IMG)
            while small_gift_bag_pos != None and config.OPEN_SMALL_GIFT_BAGS:
                logger.info(
                    "Found a small gift bag in inventory. Opening small gift bag."
                )
                moveAndClick(small_gift_bag_pos)
                autoit.mouse_move(0, 0)
                small_gift_bag_pos = getImagePosition(SMALL_GIFT_BAG_IMG)

            party_box_pos = getImagePosition(PARTY_BOX_IMG)
            if party_box_pos != None and config.OPEN_PARTY_BOXES:
                logger.info("Found a party box in inventory. Using party box.")
                moveAndClick(party_box_pos)
                continue
        finally:
            time.sleep(1)


def setupGUI():
    logger.info("Initializing GUI")
    sg.theme("DarkAmber")
    layout = [
        [sg.Text("This is a Pet Simulator 99 Script")],
        [
            SimpleGuiUtils.checkbox("Open Lucky Blocks", OPEN_LUCKY_BLOCKS),
            SimpleGuiUtils.checkbox("Open Pinatas", OPEN_PINATAS),
            SimpleGuiUtils.checkbox("Open Party Boxes", OPEN_PARTY_BOXES),
        ],
        [
            SimpleGuiUtils.checkbox("Open Small Gift Bags", OPEN_SMALL_GIFT_BAGS),
            SimpleGuiUtils.checkbox("Open Large Gift Bags", OPEN_LARGE_GIFT_BAGS),
        ],
        [sg.Button("Start Script"), sg.Text("Status: Stopped", key=STATUS)],
    ]
    return sg.Window("Pet Simulator 99 Script", layout)


def runScript(config: Config):

    global ENABLE_SCRIPT
    ENABLE_SCRIPT = True

    thread = threading.Thread(target=farm, args=[config])
    thread.daemon = True
    thread.start()

    while True:
        if keyboard.is_pressed("F1"):
            break

    logger.info("Stopping script")
    ENABLE_SCRIPT = False


if __name__ == "__main__":

    window = setupGUI()
    scriptConfig = Config()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "Start Script":
            logger.info("Starting script")
            window[STATUS].update(value="Status: Started")
            window.refresh()
            runScript(scriptConfig)
            window[STATUS].update(value="Status: Stopped")
            window.refresh()

        scriptConfig.OPEN_LUCKY_BLOCKS = values[OPEN_LUCKY_BLOCKS]
        scriptConfig.OPEN_PINATAS = values[OPEN_PINATAS]
        scriptConfig.OPEN_PARTY_BOXES = values[OPEN_PARTY_BOXES]
        scriptConfig.OPEN_SMALL_GIFT_BAGS = values[OPEN_SMALL_GIFT_BAGS]
        scriptConfig.OPEN_LARGE_GIFT_BAGS = values[OPEN_LARGE_GIFT_BAGS]
