import datetime
import logging
from Logger import logger
import os
import threading
import pyautogui
import time
import autoit
import keyboard
import PySimpleGUI as sg
from Constants import *
from RuntimeVariables import RuntimeVariables
import SimpleGuiUtils
from Config import Config

"""
TODO: Load/save config
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
        autoit.mouse_move(0, 0)
    else:
        raise RuntimeError("Failed to move and click.")


def move(pos: pyautogui.Point):
    if pos != None:
        x, y = pos
        autoit.mouse_move(x, y)
    else:
        raise RuntimeError("Failed to move to position.")


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

    global ENABLE_SCRIPT

    while itemPosition != None and ENABLE_SCRIPT:
        logger.info(f"Found a {displayStr} in inventory. Opening {displayStr}.")
        moveAndClick(itemPosition)
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


def scrollToItem(itemImage: str):

    global ENABLE_SCRIPT

    item = getImagePosition(itemImage)
    while item == None and ENABLE_SCRIPT:
        autoit.mouse_wheel("down", 10)
        time.sleep(1)
        item = getImagePosition(itemImage)
    return item


def farm(config: Config):

    if config.SAVE_LOGS:
        if not os.path.exists(LOGS_FOLDER):
            os.makedirs(LOGS_FOLDER)
        currentTime = time.time()
        newLogFile = "logs/" + (
            time.strftime("%Y-%m-%d_%H%M%S", time.localtime(currentTime)) + ".log"
        )
        logFormat = "%(asctime)s %(levelname)s %(message)s"
        logFormatter = logging.Formatter(logFormat)
        fileHandler = logging.FileHandler(newLogFile)
        fileHandler.setFormatter(logFormatter)
        logger.handlers.pop()
        logger.addHandler(fileHandler)

    logger.info("Starting auto farm script.")

    global ENABLE_SCRIPT

    runtimeVariables = RuntimeVariables()

    while ENABLE_SCRIPT:
        try:
            # Check what is enabled in the script configuration. If there is nothing enabled,
            # the script will not do anything so there is no point in running.
            if True not in set(vars(config).values()):
                logger.info(
                    "Script started without any script functionalities enabled. Stopping script."
                )
                ENABLE_SCRIPT = False
                break

            if (
                config.OPEN_FREE_GIFTS
                and (freeGiftsPosition := getImagePosition(FREE_GIFT_READY_IMG)) != None
            ):
                logger.info(
                    "Unclaimed free gifts have been detected. Attempting to claim."
                )
                # Is the free gifts popup already open?
                freeGiftsPopupPosition = getImagePosition(FREE_GIFTS_POPUP_IMG)
                if freeGiftsPopupPosition == None:
                    # No free gifts pop up, click the free gifts icon
                    moveAndClick(freeGiftsPosition)
                    logger.info("Opened free gifts popup.")

                time.sleep(1)

                # Keep checking if the free gifts icon is still there while opening
                # all the types of gifts
                while freeGiftsPosition != None and ENABLE_SCRIPT:
                    if (
                        freeGiftType1Position := getImagePosition(REDEEM_GIFT_1_IMG)
                    ) != None:
                        moveAndClick(freeGiftType1Position)
                        logger.info("Opened free gift type 1.")
                    elif (
                        freeGiftType2Position := getImagePosition(
                            REDEEM_GIFT_2_IMG, grayscale=False
                        )
                    ) != None:
                        moveAndClick(freeGiftType2Position)
                        logger.info("Opened free gift type 2.")
                    elif (
                        freeGiftType3Position := getImagePosition(
                            REDEEM_GIFT_3_IMG, grayscale=False
                        )
                    ) != None:
                        moveAndClick(freeGiftType3Position)
                        logger.info("Opened free gift type 3.")
                    elif (
                        freeGiftType4Position := getImagePosition(REDEEM_GIFT_4_IMG)
                    ) != None:
                        moveAndClick(freeGiftType4Position)
                        logger.info("Opened free gift type 4.")
                    freeGiftsPosition = getImagePosition(FREE_GIFT_READY_IMG)
                continue
            elif (
                config.OPEN_RANK_REWARDS
                and (
                    rankRewardsPosition := getImagePosition(RANK_REWARDS_CLAIMABLE_IMG)
                )
                != None
            ):
                logger.info(
                    "Unclaimed rank rewards have been detected. Attempting to claim."
                )
                moveAndClick(rankRewardsPosition)
                scrollPosition = getImagePosition(SCROLL_IMG, grayscale=False)
                move(scrollPosition)
                while rankRewardsPosition != None and ENABLE_SCRIPT:
                    rankRewardsClaimPosition = getImagePosition(CLAIM_RANK_REWARD_IMG)
                    if rankRewardsClaimPosition == None:
                        autoit.mouse_wheel("down", 10)
                    else:
                        moveAndClick(rankRewardsClaimPosition)
                        logger.info("Claimed a rank reward.")
                    rankRewardsPosition = getImagePosition(RANK_REWARDS_CLAIMABLE_IMG)
                continue

            items_pos = getImagePosition(ITEMS_IMG)
            if items_pos == None:
                logger.info("Items inventory icon not found. Opening the menu.")
                menu_pos = getImagePosition(MENU_IMG)

                if menu_pos == None:
                    raise RuntimeError("Menu not found. Stopping script.")

                moveAndClick(menu_pos)
                continue

            moveAndClick(items_pos)

            if (
                config.MAX_APPLE_BOOSTS
                or config.MAX_BANANA_BOOSTS
                or config.MAX_ORANGE_BOOSTS
                or config.MAX_PINEAPPLE_BOOSTS
                or config.MAX_RAINBOW_FRUITS_BOOSTS
            ):
                currentTime = datetime.datetime.now()
                secondsSinceLastFruitBoost = (
                    None
                    if runtimeVariables.fruitBoostTimer == None
                    else (
                        currentTime - runtimeVariables.fruitBoostTimer
                    ).total_seconds()
                )
                if (
                    runtimeVariables.fruitBoostTimer == None
                    or secondsSinceLastFruitBoost >= 300
                ):
                    scrollPosition = getImagePosition(SCROLL_IMG, grayscale=False)
                    fruitToUseFruitFlag = {
                        ORANGES: config.MAX_ORANGE_BOOSTS,
                        APPLES: config.MAX_APPLE_BOOSTS,
                        BANANAS: config.MAX_BANANA_BOOSTS,
                        PINEAPPLES: config.MAX_PINEAPPLE_BOOSTS,
                        RAINBOW_FRUITS: config.MAX_RAINBOW_FRUITS_BOOSTS,
                    }
                    fruitToImageDict = {
                        ORANGES: ORANGE_IMG,
                        APPLES: APPLE_IMG,
                        BANANAS: BANANA_IMG,
                        PINEAPPLES: PINEAPPLE_IMG,
                        RAINBOW_FRUITS: RAINBOW_FRUIT_IMG,
                    }
                    for fruit, fruitImage in fruitToImageDict.items():
                        if fruitToUseFruitFlag.get(fruit):
                            move(scrollPosition)
                            fruitPosition = scrollToItem(fruitImage)
                            openItem(fruitPosition, fruitImage, fruit)
                            hitOk()
                    runtimeVariables.fruitBoostTimer = datetime.datetime.now()

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
        except Exception as e:
            logger.exception(e)
            ENABLE_SCRIPT = False
        finally:
            time.sleep(1)
    logger.info("Stopping script.")


def setupGUI():
    sg.theme("DarkAmber")
    layout = [
        [sg.Text("Script Settings", font=HEADER_FONT)],
        [
            sg.Checkbox(
                "Save Logs",
                key=SAVE_LOGS,
                enable_events=True,
                default=False,
            ),
            sg.FolderBrowse(
                initial_folder=os.getcwd(),
                enable_events=True,
                disabled=True,
                key=BROWSE_LOGS_FOLDER,
            ),
        ],
        [
            sg.Frame(
                "Item Usage",
                [
                    [sg.Button(SELECT_ALL), sg.Button(SELECT_NONE)],
                    [
                        SimpleGuiUtils.checkbox("Open Lucky Blocks", OPEN_LUCKY_BLOCKS),
                        SimpleGuiUtils.checkbox("Open Pinatas", OPEN_PINATAS),
                    ],
                    [
                        SimpleGuiUtils.checkbox(
                            "Open Small Gift Bags", OPEN_SMALL_GIFT_BAGS
                        ),
                        SimpleGuiUtils.checkbox(
                            "Open Large Gift Bags", OPEN_LARGE_GIFT_BAGS
                        ),
                    ],
                    [
                        SimpleGuiUtils.checkbox(
                            "Create Crystal Keys", CREATE_CRYSTAL_KEYS
                        ),
                        SimpleGuiUtils.checkbox(
                            "Create Secret Keys", CREATE_SECRET_KEYS
                        ),
                    ],
                    [
                        SimpleGuiUtils.checkbox("Open Party Boxes", OPEN_PARTY_BOXES),
                    ],
                ],
                font=HEADER_FONT,
            )
        ],
        [
            sg.Frame(
                "Fruit Boosts",
                [
                    [sg.Button(SELECT_ALL_FRUITS), sg.Button(SELECT_NO_FRUITS)],
                    [
                        sg.Checkbox(
                            "Oranges",
                            key=ORANGES,
                            enable_events=True,
                            default=True,
                            size=10,
                        ),
                        sg.Checkbox(
                            "Apples",
                            key=APPLES,
                            enable_events=True,
                            default=True,
                            size=10,
                        ),
                    ],
                    [
                        sg.Checkbox(
                            "Pineapples",
                            key=PINEAPPLES,
                            enable_events=True,
                            default=True,
                            size=10,
                        ),
                        sg.Checkbox(
                            "Bananas",
                            key=BANANAS,
                            enable_events=True,
                            default=True,
                            size=10,
                        ),
                    ],
                    [
                        sg.Checkbox(
                            "Rainbow Fruits",
                            key=RAINBOW_FRUITS,
                            enable_events=True,
                            default=True,
                            size=16,
                        ),
                    ],
                ],
                font=HEADER_FONT,
            ),
        ],
        [
            sg.Frame(
                "Rewards",
                [
                    [
                        SimpleGuiUtils.checkbox("Open Free Gifts", OPEN_FREE_GIFTS),
                    ],
                    [
                        SimpleGuiUtils.checkbox("Open Rank Rewards", OPEN_RANK_REWARDS),
                    ],
                ],
                font=HEADER_FONT,
            ),
        ],
        [sg.Button(START_SCRIPT), sg.Text("Status: Stopped", key=STATUS)],
    ]
    return sg.Window("Pet Simulator 99 Script", layout, keep_on_top=True)


def updateAllSettings(window, boolean):
    window[OPEN_LUCKY_BLOCKS].update(boolean)
    window[OPEN_PINATAS].update(boolean)
    window[OPEN_PARTY_BOXES].update(boolean)
    window[OPEN_SMALL_GIFT_BAGS].update(boolean)
    window[OPEN_LARGE_GIFT_BAGS].update(boolean)
    window[CREATE_SECRET_KEYS].update(boolean)
    window[CREATE_CRYSTAL_KEYS].update(boolean)


def updateFruitBoostSettings(window, boolean):
    window[APPLES].update(boolean)
    window[ORANGES].update(boolean)
    window[PINEAPPLES].update(boolean)
    window[BANANAS].update(boolean)
    window[RAINBOW_FRUITS].update(boolean)


def runScript(config: Config):

    global ENABLE_SCRIPT
    ENABLE_SCRIPT = True

    thread = threading.Thread(target=farm, args=[config])
    thread.daemon = True
    thread.start()

    while ENABLE_SCRIPT:
        if keyboard.is_pressed("F1"):
            logger.info("Received input to stop script.")
            break

    ENABLE_SCRIPT = False


if __name__ == "__main__":

    window = setupGUI()
    scriptConfig = Config()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == START_SCRIPT:
            window[STATUS].update(value="Status: Started")
            window.refresh()
            runScript(scriptConfig)
            window[STATUS].update(value="Status: Stopped")
            window.refresh()
        elif event == SELECT_ALL:
            updateAllSettings(window, True)
        elif event == SELECT_NONE:
            updateAllSettings(window, False)
        elif event == SELECT_ALL_FRUITS:
            updateFruitBoostSettings(window, True)
        elif event == SELECT_NO_FRUITS:
            updateFruitBoostSettings(window, False)

        scriptConfig.SAVE_LOGS = values[SAVE_LOGS]

        scriptConfig.OPEN_LUCKY_BLOCKS = values[OPEN_LUCKY_BLOCKS]
        scriptConfig.OPEN_PINATAS = values[OPEN_PINATAS]
        scriptConfig.OPEN_PARTY_BOXES = values[OPEN_PARTY_BOXES]
        scriptConfig.OPEN_SMALL_GIFT_BAGS = values[OPEN_SMALL_GIFT_BAGS]
        scriptConfig.OPEN_LARGE_GIFT_BAGS = values[OPEN_LARGE_GIFT_BAGS]
        scriptConfig.CREATE_SECRET_KEYS = values[CREATE_SECRET_KEYS]
        scriptConfig.CREATE_CRYSTAL_KEYS = values[CREATE_CRYSTAL_KEYS]

        scriptConfig.MAX_BANANA_BOOSTS = values[BANANAS]
        scriptConfig.MAX_APPLE_BOOSTS = values[APPLES]
        scriptConfig.MAX_PINEAPPLE_BOOSTS = values[PINEAPPLES]
        scriptConfig.MAX_ORANGE_BOOSTS = values[ORANGES]
        scriptConfig.MAX_RAINBOW_FRUITS_BOOSTS = values[RAINBOW_FRUITS]

        scriptConfig.OPEN_FREE_GIFTS = values[OPEN_FREE_GIFTS]
        scriptConfig.OPEN_RANK_REWARDS = values[OPEN_RANK_REWARDS]

        if values[SAVE_LOGS] == True:
            window[BROWSE_LOGS_FOLDER].update(disabled=False)
