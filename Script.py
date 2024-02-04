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
"""


def getImagePosition(image: str, confidence=0.9, grayscale=True):
    try:
        pos = pyautogui.locateCenterOnScreen(
            image, confidence=confidence, grayscale=grayscale
        )
        return pos
    except pyautogui.ImageNotFoundException:
        return None


def moveAndClick(pos: pyautogui.Point):
    if pos != None:
        x, y = pos
        autoit.mouse_move(x, y)
        autoit.mouse_click("left")
    else:
        raise RuntimeError("Failed to click.")


def hitOk():
    ok_pos = getImagePosition(OK_IMG)
    if ok_pos != None:
        logger.info("Ok prompt found. Hitting ok.")
        moveAndClick(ok_pos)


def useEventItem(eventItemPosition: pyautogui.Point, displayStr: str):
    logger.info(f"Found {displayStr} in inventory. Using {displayStr}.")
    moveAndClick(eventItemPosition)

    time.sleep(1)

    hitOk()


def openItem(itemPosition: pyautogui.Point, itemImageString: str, displayStr: str):
    while itemPosition != None:
        logger.info(f"Found a {displayStr} in inventory. Opening {displayStr}.")
        moveAndClick(itemPosition)
        autoit.mouse_move(0, 0)
        itemPosition = getImagePosition(itemImageString)


def createKey(keyPartPosition: pyautogui.Point, keyType: str):
    logger.info(f"Upper and lower {keyType} found. Creating a {keyType}.")
    moveAndClick(keyPartPosition)

    time.sleep(1)

    logger.info("Clicking yes on key creation prompt.")
    yesPromptPosition = getImagePosition(YES_IMG)
    moveAndClick(yesPromptPosition)

    time.sleep(1)

    hitOk()


def farm(config: Config):

    global ENABLE_SCRIPT

    while ENABLE_SCRIPT:
        try:
            if True not in set(vars(config).values()):
                logger.info(
                    "Script started without any script functionalities enabled. Ending script."
                )
                ENABLE_SCRIPT = False
                break

            items_pos = getImagePosition(ITEMS_IMG)
            if items_pos == None:
                logger.info("Items inventory icon not found. Opening the menu.")
                menu_pos = getImagePosition(MENU_IMG)
                moveAndClick(menu_pos)
                continue

            moveAndClick(items_pos)

            if (
                config.CREATE_SECRET_KEYS
                and getImagePosition(SECRET_KEY_LOWER_IMG) != None
                and (secretKeyUpperPosition := getImagePosition(SECRET_KEY_UPPER_IMG))
                != None
            ):
                createKey(secretKeyUpperPosition, SECRET_KEY)
            elif (
                config.CREATE_CRYSTAL_KEYS
                and getImagePosition(CRYSTAL_KEY_LOWER_IMG) != None
                and (crystalKeyUpperPosition := getImagePosition(CRYSTAL_KEY_UPPER_IMG))
                != None
            ):
                createKey(crystalKeyUpperPosition, CRYSTAL_KEY)
            elif (
                config.OPEN_LARGE_GIFT_BAGS
                and (largeGiftBagPosition := getImagePosition(LARGE_GIFT_BAG_IMG))
                != None
            ):
                openItem(largeGiftBagPosition, LARGE_GIFT_BAG_IMG, LARGE_GIFT_BAG)
            elif (
                config.OPEN_SMALL_GIFT_BAGS
                and (smallGiftBagPosition := getImagePosition(SMALL_GIFT_BAG_IMG))
                != None
            ):
                openItem(smallGiftBagPosition, SMALL_GIFT_BAG_IMG, SMALL_GIFT_BAG)
            elif (
                config.OPEN_LUCKY_BLOCKS
                and (luckyBlockPosition := getImagePosition(LUCKY_BLOCK_IMG)) != None
            ):
                useEventItem(luckyBlockPosition, LUCKY_BLOCK)
            elif (
                config.OPEN_PINATAS
                and (pinataPosition := getImagePosition(PINATA_IMG)) != None
            ):
                useEventItem(pinataPosition, PINATA)
            elif (
                config.OPEN_PARTY_BOXES
                and (partyBoxPosition := getImagePosition(PARTY_BOX_IMG)) != None
            ):
                useEventItem(partyBoxPosition, PARTY_BOX)
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
        [
            SimpleGuiUtils.checkbox("Create Secret Keys", CREATE_SECRET_KEYS),
            SimpleGuiUtils.checkbox("Create Crystal Keys", CREATE_CRYSTAL_KEYS),
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

    while ENABLE_SCRIPT:
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
        scriptConfig.CREATE_SECRET_KEYS = values[CREATE_SECRET_KEYS]
        scriptConfig.CREATE_CRYSTAL_KEYS = values[CREATE_CRYSTAL_KEYS]
