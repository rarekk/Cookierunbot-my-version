# -------------------
# CONFIG
# -------------------
DEVICE_IP = "127.0.0.1"      # Change to your adb device's IP address
DEVICE_PORT = 5555           # LDPlayer 14 default ADB port (5555, or 5554 for the second instance)
TEMPLATE_DIR = "templates"
MATCH_THRESHOLD = 0.8
SESSION_RESET_INTERVAL = (5400, 10800)  # 1.5-3 hours

# -------------------
# PERFORMANCE ENGINE / ANTI-THROTTLING
# -------------------
# A. Dynamic in-game scanning delay (hold phase, seconds).
#    When a match starts the scanning thread does NOT capture the screen nor run
#    template matching for this many seconds. During the hold the thread sleeps in
#    a light 1s loop, dropping CPU usage to ~0% while the cookie is auto-running.
INGAME_SCAN_DELAY = 100

# Poll granularity of the light "hold phase" loop (seconds).
IN_GAME_HOLD_POLL_INTERVAL = 1.0

# B. Heart sender scheduler interval, in minutes. Only fires while in the LOBBY
#    state so an active match is never interrupted. A +/- 2 minute jitter is added
#    for anti-detection.
HEART_INTERVAL_MINUTES = 60
HEART_INTERVAL_JITTER_SECONDS = 120  # +/- 2 minutes

# C. Short relay / exit delay (T2, seconds) applied after a relay or exit tap when
#    the "Short Relay Exit" toggle is enabled.
SHORT_RELAY_EXIT_DELAY = 2.0

# D. Global main-loop throttle. Keeps detection at roughly 2-3 FPS to reduce CPU load
#    and avoid hammering the emulator with screencap calls.
LOOP_THROTTLE_MIN = 0.3
LOOP_THROTTLE_MAX = 0.5
SAME_STAGE_THROTTLE_MIN = 0.15
SAME_STAGE_THROTTLE_MAX = 0.25

# Default values for the GUI (kept in sync with bot_engine defaults).
DEFAULT_SMART_RELAY_GUARD = True
DEFAULT_SHORT_RELAY_EXIT = False

# In-game scan targets. After the hold phase expires the scanner only looks for the
# Relay Cookie prompt or the Exit button, matching within INGAME_SCAN_REGION. Missing
# template files are skipped gracefully by the detection layer.
INGAME_SCAN_TEMPLATES = ["GAME_RELAY_1.png", "GAME_EXIT_1.png"]
INGAME_SCAN_REGION = (0, 0, 1280, 720)  # full-frame ROI; narrow this if you have a tighter template

# -------------------
# STAGE DETECTION TEMPLATES
# -------------------
STAGE_MAINMENU_TEMPLATE = ["MAINMENU_1.png"]
STAGE_PURCHASE_ITEM_TEMPLATE = ["PURCHASE_ITEM_1.png"]
STAGE_GAME_START_TEMPLATE = ["GAME_START_1.png"]
STAGE_GAME_RELAY_TEMPLATE = ["GAME_RELAY_1.png"]
STAGE_GAME_COMPLETE_TEMPLATE = ["GAME_COMPLETE_1.png"]
STAGE_MYSTERY_BOX_TEMPLATE = ["MYSTERY_BOX_1.png"]
STAGE_CONGRATULATIONS_TEMPLATE = ["CONGRATULATIONS_1.png", "CONGRATULATIONS_2.png"]
STAGE_LEVEL_UP_TEMPLATE = ["LEVEL_UP_1.png"]
STAGE_RELIC_COMPLETE_TEMPLATE = ["RELIC_COMPLETE_1.png"]
STAGE_RELIC_CLAIM_TEMPLATE = ["RELIC_CLAIM_1.png"]
STAGE_DAILY_CHECKIN_TEMPLATE = ["DAILY_CHECKIN_1.png"]
STAGE_DAILY_CHECKIN_BOOST_SET_TEMPLATE = ["DAILY_CHECKIN_BOOST_SET_1.png"]
STAGE_DAILY_TREASURE_TEMPLATE = ["DAILY_TREASURE_1.png"]
STAGE_DAILY_NEW_TEMPLATE = ["DAILY_NEW_1.png"]
STAGE_ENTER_LEAGUE_TEMPLATE = ["ENTER_LEAGUE_1.png"]
STAGE_LEAGUE_RESULTS_TEMPLATE = ["LEAGUE_RESULTS_1.png"]
STAGE_ANTI_BOT_TEMPLATE = ["ANTI_BOT_1.png"]
STAGE_CONNECTION_LOST_TEMPLATE = ["CONNECTION_LOST_1.png", "CONNECTION_LOST_2.png"]
STAGE_INACTIVE_TEMPLATE = ["INACTIVE_1.png"]
STAGE_PREVIOUS_RANK_RESULTS_TEMPLATE = ["PREVIOUS_RANK_RESULTS_1.png"]
STAGE_TOO_MANY_TREASURES_TEMPLATE = ["TOO_MANY_TREASURES_1.png"]
STAGE_OVERTAKE_BREAK_SCORE_TEMPLATE = ["OVERTAKE_BREAK_SCORE_1.png"]
STAGE_PARTY_RUN_TEMPLATE = ["PARTY_RUN_1.png"]
STAGE_GAME_SETTINGS_TEMPLATE = ["GAME_SETTINGS_1.png"]

# -------------------
# STAGE DETECTION REGIONS
# -------------------
# Format: (x1, y1, x2, y2)
STAGE_MAINMENU_REGION = (154, 150, 344, 225)
STAGE_PURCHASE_ITEM_REGION = (474, 84, 602, 138)
STAGE_GAME_START_REGION = (573, 265, 733, 427)
STAGE_GAME_RELAY_REGION = (573, 265, 733, 427)
STAGE_GAME_COMPLETE_REGION = (523, 27, 757, 116)
STAGE_MYSTERY_BOX_REGION = (503, 46, 782, 107)
STAGE_CONGRATULATIONS_REGION = (372, 85, 909, 200)
STAGE_LEVEL_UP_REGION = (481, 34, 798, 130)
STAGE_RELIC_COMPLETE_REGION = (480, 63, 578, 106)
STAGE_RELIC_CLAIM_REGION = (412, 72, 865, 191)
STAGE_DAILY_CHECKIN_REGION = (491, 21, 792, 75)
STAGE_DAILY_CHECKIN_BOOST_SET_REGION = (523, 88, 754, 182)
STAGE_DAILY_TREASURE_REGION = (452, 117, 824, 161)
STAGE_DAILY_NEW_REGION = (432, 12, 849, 78)
STAGE_ENTER_LEAGUE_REGION = (318, 235, 962, 384)
STAGE_LEAGUE_RESULTS_REGION = (512, 52, 779, 105)
STAGE_ANTI_BOT_REGION = (309, 10, 968, 111)
STAGE_CONNECTION_LOST_REGION = (351, 203, 936, 405)
STAGE_INACTIVE_REGION = (358, 247, 934, 372)
STAGE_PREVIOUS_RANK_RESULTS_REGION = (454, 42, 832, 115)
STAGE_TOO_MANY_TREASURES_REGION = (353, 154, 931, 476)
STAGE_OVERTAKE_BREAK_SCORE_REGION = (479, 64, 799, 132)
STAGE_PARTY_RUN_REGION = (359, 44, 922, 138)
STAGE_GAME_SETTINGS_REGION = (484, 62, 769, 122)

# -------------------
# DETECTION TEMPLATES
# -------------------
FRIEND_TOP_LEADERBOARD_TEMPLATE = ["FRIEND_TOP_LEADERBOARD_1.png"]
FRIEND_BOTTOM_LEADERBOARD_TEMPLATE = ["FRIEND_BOTTOM_LEADERBOARD_1.png"]
FRIEND_SEND_LIFE_TEMPLATE = ["FRIEND_SEND_LIFE_1.png"]
NO_LIVES_TO_RECEIVE_TEMPLATE = ["NO_LIVES_TO_RECEIVE_1.png"]
ALL_LIVES_RECEIVED_AND_SENT_TEMPLATE = ["ALL_LIVES_RECEIVED_AND_SENT_1.png"]
CONFIRM_SEND_LIFE_TEMPLATE = ["CONFIRM_SEND_LIFE_1.png"]

# -------------------
# DETECTION REGION
# -------------------
RANDOM_BOOST_REGION = (701, 505, 1091, 578)
FRIEND_TOP_LEADERBOARD_REGION = (149, 272, 203, 574)
FRIEND_BOTTOM_LEADERBOARD_REGION = (272, 545, 610, 625)
FRIEND_SEND_LIFE_REGION = (608, 274, 721, 630)
NO_LIVES_TO_RECEIVE_REGION = (454, 223, 824, 575)
ALL_LIVES_RECEIVED_AND_SENT_REGION = (396, 267, 882, 346)
CONFIRM_SEND_LIFE_REGION = (640, 402, 944, 515)

# -------------------
# BOOST TEMPLATES
# -------------------
BOOST_DOUBLE_COINS_TEMPLATE = ["BOOST_DOUBLE_COINS_1.png"]
BOOST_15P_SCORE_BONUS_TEMPLATE = ["BOOST_15P_SCORE_BONUS_1.png"]
BOOST_M15P_HP_DRAIN_TEMPLATE = ["BOOST_M15P_HP_DRAIN_1.png"]
BOOST_REVIVE_ONCE_WITH_80HP_TEMPLATE = ["BOOST_REVIVE_ONCE_WITH_80HP_1.png"]
BOOST_70P_CRUSH_CHANCE_TEMPLATE = ["BOOST_70P_CRUSH_CHANCE_1.png"]
BOOST_17P_BASE_SPEED_TEMPLATE = ["BOOST_17P_BASE_SPEED_1.png"]
BOOST_GOLD_COIN_MAGIC_TEMPLATE = ["BOOST_GOLD_COIN_MAGIC_1.png"]
BOOST_M30P_COLLISION_DAMAGE_TEMPLATE = ["BOOST_M30P_COLLISION_DAMAGE_1.png"]
BOOST_20P_HP_FROM_POTIONS_TEMPLATE = ["BOOST_20P_HP_FROM_POTIONS_1.png"]
BOOST_MAGNETIC_AURA_TEMPLATE = ["BOOST_MAGNETIC_AURA_1.png"]
BOOST_2PIT_LIFTS_TEMPLATE = ["BOOST_2PIT_LIFTS_1.png"]

BOOST_TEMPLATES = (
    BOOST_DOUBLE_COINS_TEMPLATE,
    BOOST_15P_SCORE_BONUS_TEMPLATE,
    BOOST_M15P_HP_DRAIN_TEMPLATE,
    BOOST_REVIVE_ONCE_WITH_80HP_TEMPLATE,
    BOOST_70P_CRUSH_CHANCE_TEMPLATE,
    BOOST_17P_BASE_SPEED_TEMPLATE,
    BOOST_GOLD_COIN_MAGIC_TEMPLATE,
    BOOST_M30P_COLLISION_DAMAGE_TEMPLATE,
    BOOST_20P_HP_FROM_POTIONS_TEMPLATE,
    BOOST_MAGNETIC_AURA_TEMPLATE,
    BOOST_2PIT_LIFTS_TEMPLATE,
)

# -------------------
# STAGE MAP
# -------------------
STAGE_TEMPLATES = {
    # higher priority stages first
    "GAME_START":              STAGE_GAME_START_TEMPLATE,
    "GAME_RELAY":              STAGE_GAME_RELAY_TEMPLATE,
    "ANTI_BOT":                STAGE_ANTI_BOT_TEMPLATE,
    "CONNECTION_LOST":         STAGE_CONNECTION_LOST_TEMPLATE,
    "INACTIVE":                STAGE_INACTIVE_TEMPLATE,
    "GAME_COMPLETE":           STAGE_GAME_COMPLETE_TEMPLATE,
    "OVERTAKE_BREAK_SCORE":    STAGE_OVERTAKE_BREAK_SCORE_TEMPLATE,
    "MYSTERY_BOX":             STAGE_MYSTERY_BOX_TEMPLATE,
    "CONGRATULATIONS":         STAGE_CONGRATULATIONS_TEMPLATE,
    "RELIC_COMPLETE":          STAGE_RELIC_COMPLETE_TEMPLATE,
    "RELIC_CLAIM":             STAGE_RELIC_CLAIM_TEMPLATE,
    "TOO_MANY_TREASURES":      STAGE_TOO_MANY_TREASURES_TEMPLATE,
    "MAINMENU":                STAGE_MAINMENU_TEMPLATE,
    "PARTY_RUN":               STAGE_PARTY_RUN_TEMPLATE,
    "GAME_SETTINGS":           STAGE_GAME_SETTINGS_TEMPLATE,
    "PURCHASE_ITEM":           STAGE_PURCHASE_ITEM_TEMPLATE,
    "LEVEL_UP":                STAGE_LEVEL_UP_TEMPLATE,
    "DAILY_CHECKIN":           STAGE_DAILY_CHECKIN_TEMPLATE,
    "DAILY_CHECKIN_BOOST_SET": STAGE_DAILY_CHECKIN_BOOST_SET_TEMPLATE,
    "DAILY_TREASURE":          STAGE_DAILY_TREASURE_TEMPLATE,
    "DAILY_NEW":               STAGE_DAILY_NEW_TEMPLATE,
    "ENTER_LEAGUE":            STAGE_ENTER_LEAGUE_TEMPLATE,
    "LEAGUE_RESULTS":          STAGE_LEAGUE_RESULTS_TEMPLATE,
    "PREVIOUS_RANK_RESULTS":   STAGE_PREVIOUS_RANK_RESULTS_TEMPLATE,
}

STAGE_REGIONS = {
    "MAINMENU":                STAGE_MAINMENU_REGION,
    "PARTY_RUN":               STAGE_PARTY_RUN_REGION,
    "GAME_SETTINGS":           STAGE_GAME_SETTINGS_REGION,
    "PURCHASE_ITEM":           STAGE_PURCHASE_ITEM_REGION,
    "GAME_START":              STAGE_GAME_START_REGION,
    "GAME_RELAY":              STAGE_GAME_RELAY_REGION,
    "GAME_COMPLETE":           STAGE_GAME_COMPLETE_REGION,
    "OVERTAKE_BREAK_SCORE":    STAGE_OVERTAKE_BREAK_SCORE_REGION,
    "MYSTERY_BOX":             STAGE_MYSTERY_BOX_REGION,
    "CONGRATULATIONS":         STAGE_CONGRATULATIONS_REGION,
    "LEVEL_UP":                STAGE_LEVEL_UP_REGION,
    "RELIC_COMPLETE":          STAGE_RELIC_COMPLETE_REGION,
    "RELIC_CLAIM":             STAGE_RELIC_CLAIM_REGION,
    "DAILY_CHECKIN":           STAGE_DAILY_CHECKIN_REGION,
    "DAILY_CHECKIN_BOOST_SET": STAGE_DAILY_CHECKIN_BOOST_SET_REGION,
    "DAILY_TREASURE":          STAGE_DAILY_TREASURE_REGION,
    "DAILY_NEW":               STAGE_DAILY_NEW_REGION,
    "ENTER_LEAGUE":            STAGE_ENTER_LEAGUE_REGION,
    "LEAGUE_RESULTS":          STAGE_LEAGUE_RESULTS_REGION,
    "ANTI_BOT":                STAGE_ANTI_BOT_REGION,
    "CONNECTION_LOST":         STAGE_CONNECTION_LOST_REGION,
    "INACTIVE":                STAGE_INACTIVE_REGION,
    "PREVIOUS_RANK_RESULTS":   STAGE_PREVIOUS_RANK_RESULTS_REGION,
    "TOO_MANY_TREASURES":      STAGE_TOO_MANY_TREASURES_REGION,
}

# -------------------
# DETECTION GROUPS
# -------------------
DETECTION_ALWAYS_STAGES = (
    "CONNECTION_LOST",
    "INACTIVE",
)

DETECTION_GROUP_PRE_GAME = (
    "CONGRATULATIONS",
    "LEVEL_UP",
    "RELIC_COMPLETE",
    "RELIC_CLAIM",
    "DAILY_CHECKIN",
    "DAILY_CHECKIN_BOOST_SET",
    "DAILY_TREASURE",
    "DAILY_NEW",
    "ENTER_LEAGUE",
    "LEAGUE_RESULTS",
    "PREVIOUS_RANK_RESULTS",
    "TOO_MANY_TREASURES",
    "PARTY_RUN",
    "GAME_SETTINGS",
    "MAINMENU",
    "PURCHASE_ITEM",
)

DETECTION_GROUP_IN_GAME = (
    "GAME_START",
    "GAME_RELAY",
    "GAME_COMPLETE",
)

DETECTION_GROUP_POST_GAME = (
    "ANTI_BOT",
    "OVERTAKE_BREAK_SCORE",
    "MYSTERY_BOX",
    "MAINMENU",
)

DETECTION_GROUPS = {
    "PRE_GAME":  DETECTION_GROUP_PRE_GAME,
    "IN_GAME":   DETECTION_GROUP_IN_GAME,
    "POST_GAME": DETECTION_GROUP_POST_GAME,
}

DETECTION_RECOVERY_SCAN_INTERVAL = {
    "PRE_GAME":  60.0,  # seconds
    "IN_GAME":  300.0,  # seconds
    "POST_GAME": 30.0,  # seconds
}

# -------------------
# ITEM COORDINATES
# -------------------
START_BUTTON = (955, 650)
PLAY_BUTTON = (895, 620)
FAST_START_ITEM = (235, 600)
COOKIE_RELAY_ITEM = (385, 600)
RANDOM_BOOST_ITEM = (535, 600)
PURCHASE_BUTTON = (925, 295)
# --- Multi-Buy 3-step flow (see actions.purchase_desired_random_boost) ---
# Step 1: RANDOM_BOOST_ITEM selects the "Random Boost" slot (1,200 coins).
# Step 2: MULTI_ICON_BUTTON is the small pink "Multi" icon at the top-right of the
#         purchase dialog. It opens the Multi-Buy modal.
# Step 3: MULTI_BUY_BUTTON is the green "Multi-Buy" button on the modal. It performs
#         the automatic rerolls until the desired boost appears.
MULTI_ICON_BUTTON = (1100, 195)
MULTI_PURCHASE_BUTTON = MULTI_ICON_BUTTON  # legacy alias
MULTI_BUY_BUTTON = (640, 587)
FAST_START_USE_BUTTON = (655, 340)
COOKIE_RELAY_USE_BUTTON = (655, 340)
COMPLETE_FINISH_BUTTON = (460, 625)
ACCEPT_MYSTERY_BOX_BUTTON = (650, 645)
ACCEPT_CONGRATULATIONS_BUTTON = (640, 565)
ACCEPT_LEVEL_UP_BUTTON = (640, 640)
ACCEPT_DAILY_CHECKIN_BUTTON = (640, 660)
ACCEPT_DAILY_CHECKIN_BOOST_SET_BUTTON = (640, 568)
ACCEPT_DAILY_TREASURE_BUTTON = (650, 570)
ACCEPT_DAILY_NEW_BUTTON = (1128, 74)
ACCEPT_ENTER_LEAGUE_BUTTON = (640, 460)
ACCEPT_LEAGUE_RESULTS_BUTTON = (640, 610)
ACCEPT_PREVIOUS_RANK_RESULTS_BUTTON = (640, 615)
ACCEPT_TOO_MANY_TREASURES_BUTTON = (640, 545)
ACCEPT_OVERTAKE_BREAK_SCORE_BUTTON = (465, 640)
RELIC_COMPLETE_BUTTON = (530, 110)
RELIC_CLAIM_BUTTON = (640, 580)
RELIC_CLOSE_BUTTON = (1076, 154)
CONNECTION_LOST_RELOAD_BUTTON = (640, 460)
INACTIVE_RELOAD_BUTTON = (640, 460)
MAIL_BOX_BUTTON = (686, 677)
MAIL_BOX_LIVES_TAB_BUTTON = (630, 148)
MAIL_BOX_CLOSE_BUTTON = (1130, 87)
QUICK_RECEIVE_AND_SEND_LIVES_BUTTON = (652, 612)
ACCEPT_ALL_LIVES_RECEIVED_AND_SENT_BUTTON = (640, 462)
CONFIRM_SEND_LIFE_BUTTON = (797, 460)
CLOSE_SEND_LIFE_DIALOG_BUTTON = (645, 463)
LEADERBOARD_TOP_POSITION = (435, 260)
LEADERBOARD_BOTTOM_POSITION = (435, 620)
CLOSE_ANNOUNCEMENT_DIALOG_BUTTON = (1127, 66)
EXIT_PARTY_RUN_MODE_BUTTON = (1214, 89)
EXIT_GAME_SETTINGS_BUTTON = (1116, 98)

# -------------------
# ANTI-BOT CAPTCHA
# -------------------
ANTI_BOT_CARD_POS_1 = (346, 179)
ANTI_BOT_CARD_POS_2 = (542, 179)
ANTI_BOT_CARD_POS_3 = (738, 179)
ANTI_BOT_CARD_POS_4 = (346, 435)
ANTI_BOT_CARD_POS_5 = (542, 435)
ANTI_BOT_CARD_POS_6 = (738, 435)
ANTI_BOT_CARD_WIDTH = 183
ANTI_BOT_CARD_HEIGHT = 241

# ===================================================================================
# APPLICATION ICON  (main.pyw uses this for the window + taskbar icon)
# ===================================================================================
# Resolved relative to the "src" directory. The first existing file wins.
APP_ICON_CANDIDATES = (
    "templates/app_icon.png",
    "templates/app_icon.ico",
    "bot_icon.ico",
)
# Windows taskbar grouping id so the app does not show the generic Python icon.
APP_USER_MODEL_ID = "CookieRun.Classic.Automation"

# ===================================================================================
# MODE PRESETS  (dynamic dashboard presets: farming / gacha / hybrid)
# ===================================================================================
MODE_FARMING = "FARMING"
MODE_GACHA = "GACHA"
MODE_HYBRID = "HYBRID"
DEFAULT_BOT_MODE = MODE_FARMING

# ===================================================================================
# TREASURE GACHA & SMART SALVAGE
# ===================================================================================
# 9-step routine:
#   1. tap treasure_menu        5. tap treasure_cabinet_btn
#   2. tap treasure_draw_tab     6. tap treasure_sort_btn -> treasure_sort_obtained
#   3. verify coins >= 5,000     7. tap treasure_extract_mode_btn
#   4. tap treasure_5k_gacha + confirm (x rounds)   8. smart-select low tier
#   9. confirm extraction -> back to lobby
TREASURE_GACHA_COST = 5000
DEFAULT_GACHA_ROUNDS = 1
DEFAULT_GACHA_AUTO_DISMANTLE = True
DEFAULT_GACHA_PRESERVE_RAINBOW = True      # never salvage rainbow / S-tier borders
DEFAULT_GACHA_PRESERVE_COOKIE = True       # never salvage cookie-specific treasures
DEFAULT_GACHA_EVERY_N_RUNS = 10            # hybrid mode: run a gacha session every N runs

# In pure Gacha mode the bot loops: session -> rest -> session.
GACHA_LOOP_INTERVAL_SECONDS = 30

# Allow coordinate fallbacks when a treasure template has not been calibrated yet.
# Set to False once every TREASURE_* template exists for maximum safety.
TREASURE_ALLOW_COORD_FALLBACK = True

# --- Treasure templates (drop the .png files into templates/) ---
TREASURE_MENU_TEMPLATE = ["TREASURE_MENU_1.png"]
TREASURE_DRAW_TAB_TEMPLATE = ["TREASURE_DRAW_TAB_1.png"]
TREASURE_5K_GACHA_TEMPLATE = ["TREASURE_5K_GACHA_1.png"]
TREASURE_CONFIRM_TEMPLATE = ["TREASURE_CONFIRM_1.png"]
TREASURE_CABINET_BTN_TEMPLATE = ["TREASURE_CABINET_BTN_1.png"]
TREASURE_SORT_BTN_TEMPLATE = ["TREASURE_SORT_BTN_1.png"]
TREASURE_SORT_OBTAINED_TEMPLATE = ["TREASURE_SORT_OBTAINED_1.png"]
TREASURE_EXTRACT_MODE_BTN_TEMPLATE = ["TREASURE_EXTRACT_MODE_BTN_1.png"]
TREASURE_EXTRACT_CONFIRM_TEMPLATE = ["TREASURE_EXTRACT_CONFIRM_1.png"]
# The pop-up "Extract" confirm button looks similar to the trigger button but sits at
# a DIFFERENT position. Optional: capture it as its own template for maximum accuracy.
# When this template file is absent the routine reuses TREASURE_EXTRACT_CONFIRM_TEMPLATE
# (same look) for the second tap and relies on the separate pop-up fallback coordinate.
TREASURE_EXTRACT_POPUP_TEMPLATE = ["TREASURE_EXTRACT_POPUP_CONFIRM_1.png"]
TREASURE_LOBBY_BACK_TEMPLATE = ["TREASURE_LOBBY_BACK_1.png"]
# --- Smart-selection strategy ------------------------------------------------
#  True (recommended): POSITIVE MATCH — a slot is tapped ONLY when it matches at
#        least one "salvageable" template (TREASURE_SALVAGE_*.png in templates/).
#        Nothing else is ever touched, so common rainbow/S-tier items are safe by
#        default without needing thousands of exclusion templates.
#  False: EXCLUSION — tap everything that is NOT protected (requires the rainbow +
#        cookie protection templates, hard to maintain when rainbow items are common).
TREASURE_POSITIVE_SELECT = True
# Optional fallback list. The primary source is auto-discovery of TREASURE_SALVAGE_*.png
# files dropped into templates/ (you can add new low-tier images anytime without editing config).
TREASURE_SALVAGE_TEMPLATE = []
# STRICT EXCLUSION protection templates — even in positive-select mode a match on any
# of these in a slot means the treasure is protected and will NEVER be selected.
TREASURE_RAINBOW_BORDER_TEMPLATE = ["TREASURE_RAINBOW_1.png"]
TREASURE_COOKIE_ICON_TEMPLATE = ["TREASURE_COOKIE_1.png"]

# --- Treasure regions (full frame unless a tighter search box is known) ---
TREASURE_SCAN_REGION = (0, 0, 1280, 720)
TREASURE_BUTTON_REGION = (0, 0, 1280, 720)

# --- Coordinate fallbacks (CALIBRATE against your own 1280x720 layout) ---
TREASURE_MENU_BUTTON = (1160, 640)
TREASURE_DRAW_TAB_BUTTON = (640, 110)
TREASURE_5K_GACHA_BUTTON = (900, 620)
TREASURE_CONFIRM_BUTTON = (640, 620)
TREASURE_CABINET_BTN_BUTTON = (1100, 110)
TREASURE_SORT_BTN_BUTTON = (1150, 110)
TREASURE_SORT_OBTAINED_BUTTON = (1000, 210)
TREASURE_EXTRACT_MODE_BTN_BUTTON = (1150, 170)
TREASURE_EXTRACT_CONFIRM_BUTTON = (640, 600)
# The Extract confirmation appears twice as an identical "Extract" button:
# first the trigger, then a pop-up confirm (usually near the screen centre).
TREASURE_EXTRACT_POPUP_CONFIRM_BUTTON = (640, 400)
TREASURE_LOBBY_BACK_BUTTON = (60, 60)

# --- Smart-selection inventory grid (CALIBRATE) ---
TREASURE_GRID_ORIGIN = (250, 215)   # top-left slot centre origin (x, y)
TREASURE_GRID_COLS = 6
TREASURE_GRID_ROWS = 3
TREASURE_SLOT_W = 130
TREASURE_SLOT_H = 120
TREASURE_MAX_SELECTIONS = 30
# How many select+extract passes to run — the routine stops early (with a log)
# as soon as a pass finds nothing left to salvage.
TREASURE_EXTRACT_MAX_PASSES = 4

# --- Lobby coin balance banner (used to verify the 5,000-coin cost) ---
# Crop of the coin counter in the top currency banner. ``extract_lobby_coins``
# returns -1 when the value cannot be read (callers then proceed with a warning).
LOBBY_COIN_REGION = (940, 22, 1215, 60)
