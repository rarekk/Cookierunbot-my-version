import os
import random
import time

import config
import logbus
from adb import safe_device_tap, safe_device_scroll, device_capture_screen
from config import (
    ACCEPT_ALL_LIVES_RECEIVED_AND_SENT_BUTTON,
    ACCEPT_CONGRATULATIONS_BUTTON,
    ACCEPT_DAILY_CHECKIN_BOOST_SET_BUTTON,
    ACCEPT_DAILY_CHECKIN_BUTTON,
    ACCEPT_DAILY_TREASURE_BUTTON,
    ACCEPT_DAILY_NEW_BUTTON,
    ACCEPT_ENTER_LEAGUE_BUTTON,
    ACCEPT_LEAGUE_RESULTS_BUTTON,
    ACCEPT_LEVEL_UP_BUTTON,
    ACCEPT_MYSTERY_BOX_BUTTON,
    ACCEPT_OVERTAKE_BREAK_SCORE_BUTTON,
    ACCEPT_PREVIOUS_RANK_RESULTS_BUTTON,
    ACCEPT_TOO_MANY_TREASURES_BUTTON,
    ALL_LIVES_RECEIVED_AND_SENT_REGION,
    ALL_LIVES_RECEIVED_AND_SENT_TEMPLATE,
    CLOSE_ANNOUNCEMENT_DIALOG_BUTTON,
    CLOSE_SEND_LIFE_DIALOG_BUTTON,
    COMPLETE_FINISH_BUTTON,
    CONFIRM_SEND_LIFE_BUTTON,
    CONFIRM_SEND_LIFE_REGION,
    CONFIRM_SEND_LIFE_TEMPLATE,
    COOKIE_RELAY_ITEM,
    COOKIE_RELAY_USE_BUTTON,
    EXIT_GAME_SETTINGS_BUTTON,
    EXIT_PARTY_RUN_MODE_BUTTON,
    FAST_START_ITEM,
    FAST_START_USE_BUTTON,
    FRIEND_BOTTOM_LEADERBOARD_REGION,
    FRIEND_BOTTOM_LEADERBOARD_TEMPLATE,
    FRIEND_SEND_LIFE_REGION,
    FRIEND_SEND_LIFE_TEMPLATE,
    FRIEND_TOP_LEADERBOARD_REGION,
    FRIEND_TOP_LEADERBOARD_TEMPLATE,
    INACTIVE_RELOAD_BUTTON,
    LEADERBOARD_BOTTOM_POSITION,
    LEADERBOARD_TOP_POSITION,
    MAIL_BOX_BUTTON,
    MAIL_BOX_LIVES_TAB_BUTTON,
    MAIL_BOX_CLOSE_BUTTON,
    MULTI_BUY_BUTTON,
    MULTI_ICON_BUTTON,
    MULTI_PURCHASE_BUTTON,
    NO_LIVES_TO_RECEIVE_REGION,
    NO_LIVES_TO_RECEIVE_TEMPLATE,
    PLAY_BUTTON,
    PURCHASE_BUTTON,
    QUICK_RECEIVE_AND_SEND_LIVES_BUTTON,
    RANDOM_BOOST_ITEM,
    RANDOM_BOOST_REGION,
    RELIC_CLAIM_BUTTON,
    RELIC_CLOSE_BUTTON,
    RELIC_COMPLETE_BUTTON,
    START_BUTTON,
    CONNECTION_LOST_RELOAD_BUTTON,
)
from detection import detect_templates, detect_anti_bot_odd_cards, detect_stage, extract_lobby_coins
from config import (
    ANTI_BOT_CARD_POS_1, ANTI_BOT_CARD_POS_2, ANTI_BOT_CARD_POS_3,
    ANTI_BOT_CARD_POS_4, ANTI_BOT_CARD_POS_5, ANTI_BOT_CARD_POS_6,
    ANTI_BOT_CARD_WIDTH, ANTI_BOT_CARD_HEIGHT,
)

def start_game():
    logbus.log("🏁 Starting the game...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, START_BUTTON[0], START_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def play_game():
    logbus.log("🎮 Playing the game...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, PLAY_BUTTON[0], PLAY_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def purchase_fast_start():
    logbus.log("🛒 Purchasing Fast Start...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, FAST_START_ITEM[0], FAST_START_ITEM[1])
    time.sleep(random.uniform(0.8, 1.4))
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, PURCHASE_BUTTON[0], PURCHASE_BUTTON[1])
    time.sleep(random.uniform(1, 2))


def purchase_cookie_relay():
    logbus.log("🛒 Purchasing Cookie Relay...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, COOKIE_RELAY_ITEM[0], COOKIE_RELAY_ITEM[1])
    time.sleep(random.uniform(0.8, 1.4))
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, PURCHASE_BUTTON[0], PURCHASE_BUTTON[1])
    time.sleep(random.uniform(1, 2))


def purchase_random_boost():
    logbus.log("🛒 Purchasing Random Boost...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, RANDOM_BOOST_ITEM[0], RANDOM_BOOST_ITEM[1])
    time.sleep(random.uniform(0.8, 1.4))
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, PURCHASE_BUTTON[0], PURCHASE_BUTTON[1])
    time.sleep(random.uniform(1, 2))


def purchase_random_boost_multibuy():
    """3-step native Multi-Buy reroll flow.

    Step 1 - tap the "Random Boost" slot (1,200 Coins) to open the purchase dialog.
    Step 2 - tap the small pink "Multi" icon at the top-right to open the Multi-Buy modal.
    Step 3 - tap the green "Multi-Buy" button, which performs the automatic rerolls.
    """
    logbus.log("🛒 [Multi-Buy 1/3] Selecting Random Boost slot (1,200 Coins)...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, RANDOM_BOOST_ITEM[0], RANDOM_BOOST_ITEM[1])
    time.sleep(random.uniform(0.8, 1.4))

    logbus.log("🛒 [Multi-Buy 2/3] Opening Multi-Buy modal (pink Multi icon)...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, MULTI_ICON_BUTTON[0], MULTI_ICON_BUTTON[1])
    time.sleep(random.uniform(1.0, 1.8))

    logbus.log("🛒 [Multi-Buy 3/3] Confirming green Multi-Buy (auto reroll)...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, MULTI_BUY_BUTTON[0], MULTI_BUY_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def purchase_desired_random_boost(desired_template, desired_name):
    logbus.log(f"🎲 Rolling Random Boost via Multi-Buy until '{desired_name}' appears...")
    purchase_random_boost_multibuy()
    logbus.log(f"🔍 Waiting for desired boost to be detected: {desired_name}...")
    timeout = 30
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            logbus.log(f"⏰ Timeout: Could not detect desired boost '{desired_name}' within {timeout} seconds.")
            logbus.log("⚠️ Skipping Desired Random Boost. Please verify your in-game boost config is correct.")
            return
        screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
        if detect_templates(screen, desired_template, RANDOM_BOOST_REGION):
            logbus.log(f"✅ Desired Boost detected: {desired_name}!")
            break
        time.sleep(0.5)


def using_fast_start():
    logbus.log("⚡ Using Fast Start...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, FAST_START_USE_BUTTON[0], FAST_START_USE_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.2))


def using_cookie_relay(exit_delay=None):
    """Tap the Relay Cookie use button.

    When ``exit_delay`` (T2) is provided, the bot waits exactly that many seconds after
    the tap so it can exit the relay prompt quickly instead of the default humanized wait.
    """
    logbus.log("🍪 Using Cookie Relay...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, COOKIE_RELAY_USE_BUTTON[0], COOKIE_RELAY_USE_BUTTON[1])
    if exit_delay is not None:
        logbus.log(f"⏱️ Short relay exit: waiting {exit_delay:.1f}s (T2) before resuming scan...")
        time.sleep(max(0.0, float(exit_delay)))
    else:
        time.sleep(random.uniform(0.8, 1.2))


def complete_finish():
    logbus.log("🏆 Completing the game...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, COMPLETE_FINISH_BUTTON[0], COMPLETE_FINISH_BUTTON[1])
    time.sleep(random.uniform(1.8, 2.4))


def accept_mystery_box():
    logbus.log("🎁 Opening Mystery Boxes...")
    # 1. Tap Open All button
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_MYSTERY_BOX_BUTTON[0], ACCEPT_MYSTERY_BOX_BUTTON[1])
    time.sleep(random.uniform(1.8, 2.4))
    # 2. Tap to confirm loot and return
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_MYSTERY_BOX_BUTTON[0], ACCEPT_MYSTERY_BOX_BUTTON[1])
    time.sleep(random.uniform(1.0, 1.5))


def accept_congratulations():
    logbus.log("🎉 Accepting Congratulations...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_CONGRATULATIONS_BUTTON[0], ACCEPT_CONGRATULATIONS_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_level_up():
    logbus.log("⬆️ Accepting Level Up...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_LEVEL_UP_BUTTON[0], ACCEPT_LEVEL_UP_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_daily_checkin():
    logbus.log("📅 Accepting Daily Check-in...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_DAILY_CHECKIN_BUTTON[0], ACCEPT_DAILY_CHECKIN_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_daily_checkin_boost_set():
    logbus.log("📅 Accepting Daily Check-in Boost Set...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_DAILY_CHECKIN_BOOST_SET_BUTTON[0], ACCEPT_DAILY_CHECKIN_BOOST_SET_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_daily_treasure():
    logbus.log("💎 Accepting Daily Treasure...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_DAILY_TREASURE_BUTTON[0], ACCEPT_DAILY_TREASURE_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_daily_new():
    logbus.log("📰 Accepting Daily New...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_DAILY_NEW_BUTTON[0], ACCEPT_DAILY_NEW_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_enter_league():
    logbus.log("🏆 Accepting Enter League...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_ENTER_LEAGUE_BUTTON[0], ACCEPT_ENTER_LEAGUE_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_league_results():
    logbus.log("🏆 Accepting League Results...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_LEAGUE_RESULTS_BUTTON[0], ACCEPT_LEAGUE_RESULTS_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_previous_rank_results():
    logbus.log("🏆 Accepting Previous Rank Results...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_PREVIOUS_RANK_RESULTS_BUTTON[0], ACCEPT_PREVIOUS_RANK_RESULTS_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_too_many_treasures():
    logbus.log("💎 Accepting Too Many Treasures...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_TOO_MANY_TREASURES_BUTTON[0], ACCEPT_TOO_MANY_TREASURES_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_overtake_break_score():
    logbus.log("🏆 Accepting Overtake Break Score...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_OVERTAKE_BREAK_SCORE_BUTTON[0], ACCEPT_OVERTAKE_BREAK_SCORE_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def open_relic_complete():
    logbus.log("🏺 Opening Relic Complete...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, RELIC_COMPLETE_BUTTON[0], RELIC_COMPLETE_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def accept_relic_claim():
    logbus.log("🏺 Accepting Relic Claim...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, RELIC_CLAIM_BUTTON[0], RELIC_CLAIM_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, RELIC_CLOSE_BUTTON[0], RELIC_CLOSE_BUTTON[1])
    time.sleep(random.uniform(10, 15))


def handle_anti_bot(screen):
    logbus.log("🤖 Solving Anti-Bot captcha...")
    card_coords = [
        ANTI_BOT_CARD_POS_1, ANTI_BOT_CARD_POS_2, ANTI_BOT_CARD_POS_3,
        ANTI_BOT_CARD_POS_4, ANTI_BOT_CARD_POS_5, ANTI_BOT_CARD_POS_6,
    ]

    odd_indices = detect_anti_bot_odd_cards(screen)
    card_nums = [i + 1 for i in odd_indices]
    logbus.log(f"🃏 Found odd cards: Card {card_nums[0]} and Card {card_nums[1]}")

    for idx in odd_indices:
        cx, cy = card_coords[idx]
        margin = 20
        tx = random.randint(cx + margin, cx + ANTI_BOT_CARD_WIDTH - margin)
        ty = random.randint(cy + margin, cy + ANTI_BOT_CARD_HEIGHT - margin)
        logbus.log(f"  👆 Tapping Card {idx + 1} at ({tx}, {ty})")
        safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, tx, ty)
        time.sleep(random.uniform(10, 15))

    logbus.log("✅ Anti-Bot captcha solved!")
    time.sleep(random.uniform(0.8, 1.4))


def handle_connection_lost():
    logbus.log("🔌 Handling Connection Lost...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, CONNECTION_LOST_RELOAD_BUTTON[0], CONNECTION_LOST_RELOAD_BUTTON[1])
    time.sleep(random.uniform(10, 15))


def handle_inactive():
    logbus.log("💤 Handling Inactive state...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, INACTIVE_RELOAD_BUTTON[0], INACTIVE_RELOAD_BUTTON[1])
    time.sleep(random.uniform(10, 15))


def handle_send_friend_life():
    logbus.log("💌 Handling Send Friend Life...")
    screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
    while True:
        if detect_templates(screen, FRIEND_TOP_LEADERBOARD_TEMPLATE, FRIEND_TOP_LEADERBOARD_REGION):
            logbus.log("✅ Top of Friend Leaderboard reached.")
            break
        logbus.log("🔄 Scrolling up to find Send Friend Life...")
        safe_device_scroll(config.DEVICE_IP, config.DEVICE_PORT, LEADERBOARD_BOTTOM_POSITION[0], LEADERBOARD_BOTTOM_POSITION[1], direction="down", distance=300, duration=150)
        time.sleep(random.uniform(0.8, 1.4))
        screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
    no_button_scroll_count = 0
    while True:
        screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
        if detect_templates(screen, FRIEND_BOTTOM_LEADERBOARD_TEMPLATE, FRIEND_BOTTOM_LEADERBOARD_REGION):
            logbus.log("✅ Bottom of Friend Leaderboard reached. Done sending lives.")
            break
        send_life_button_coords = detect_templates(screen, FRIEND_SEND_LIFE_TEMPLATE, FRIEND_SEND_LIFE_REGION)
        if send_life_button_coords:
            no_button_scroll_count = 0
            for x, y, w, h in send_life_button_coords:
                logbus.log("💌 Sending life to friend...")
                safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, x + w // 2, y + h // 2)
                time.sleep(random.uniform(0.8, 1.4))
                logbus.log("💌 Confirming send life...")
                safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, CONFIRM_SEND_LIFE_BUTTON[0], CONFIRM_SEND_LIFE_BUTTON[1])
                time.sleep(random.uniform(0.8, 1.4))
                logbus.log("💌 Closing send life dialog...")
                safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, CLOSE_SEND_LIFE_DIALOG_BUTTON[0], CLOSE_SEND_LIFE_DIALOG_BUTTON[1])
                time.sleep(random.uniform(0.8, 1.4))
        else:
            no_button_scroll_count += 1
            if no_button_scroll_count >= 30:
                logbus.log("⚠️ No send life buttons found for 30 consecutive scrolls. Giving up.")
                break
            logbus.log(f"🔄 No send life buttons found, scrolling down... ({no_button_scroll_count}/30)")
            safe_device_scroll(config.DEVICE_IP, config.DEVICE_PORT, LEADERBOARD_TOP_POSITION[0], LEADERBOARD_TOP_POSITION[1], direction="up", distance=70, duration=150)
            time.sleep(random.uniform(0.8, 1.4))


def handle_quick_receive_and_send_lives():
    logbus.log("✉️ Handling Quick Receive and Send Lives...")
    time.sleep(random.uniform(0.8, 1.4))
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, MAIL_BOX_BUTTON[0], MAIL_BOX_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, MAIL_BOX_LIVES_TAB_BUTTON[0], MAIL_BOX_LIVES_TAB_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))
    screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
    if detect_templates(screen, NO_LIVES_TO_RECEIVE_TEMPLATE, NO_LIVES_TO_RECEIVE_REGION):
        logbus.log("✉️ No lives to receive. Proceeding to send lives...")
        safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, MAIL_BOX_CLOSE_BUTTON[0], MAIL_BOX_CLOSE_BUTTON[1])
        return
    logbus.log("✉️ Receiving all lives...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, QUICK_RECEIVE_AND_SEND_LIVES_BUTTON[0], QUICK_RECEIVE_AND_SEND_LIVES_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))
    while True:
        screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
        all_lives_received_and_sent = detect_templates(screen, ALL_LIVES_RECEIVED_AND_SENT_TEMPLATE, ALL_LIVES_RECEIVED_AND_SENT_REGION)
        if all_lives_received_and_sent:
            logbus.log("✉️ All lives received and sent. Done!")
            safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, ACCEPT_ALL_LIVES_RECEIVED_AND_SENT_BUTTON[0], ACCEPT_ALL_LIVES_RECEIVED_AND_SENT_BUTTON[1])
            time.sleep(random.uniform(0.8, 1.4))
            safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, MAIL_BOX_CLOSE_BUTTON[0], MAIL_BOX_CLOSE_BUTTON[1])
            time.sleep(random.uniform(0.8, 1.4))
            break
        confirm_send_life_button_coords = detect_templates(screen, CONFIRM_SEND_LIFE_TEMPLATE, CONFIRM_SEND_LIFE_REGION)
        if confirm_send_life_button_coords:
            logbus.log("✉️ Sending lives to friends...")
            safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, CONFIRM_SEND_LIFE_BUTTON[0], CONFIRM_SEND_LIFE_BUTTON[1])
            time.sleep(random.uniform(0.8, 1.4))
    logbus.log("✉️ Quick Receive and Send Lives completed.")


def close_announcement_dialog():
    logbus.log("🖱️ Closing announcement dialog...")
    for i in range(5):
        logbus.log(f"🖱️ Tapping close announcement dialog button {i+1}/5")
        safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, CLOSE_ANNOUNCEMENT_DIALOG_BUTTON[0], CLOSE_ANNOUNCEMENT_DIALOG_BUTTON[1])
        time.sleep(random.uniform(0.8, 1.4))
    time.sleep(random.uniform(0.8, 1.4))
    device_screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
    if detect_stage(device_screen, ["PARTY_RUN"]) == "PARTY_RUN":
        close_party_run_mode()
    elif detect_stage(device_screen, ["GAME_SETTINGS"]) == "GAME_SETTINGS":
        close_game_settings()


def close_party_run_mode():
    logbus.log("🖱️ Closing Party Run mode...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, EXIT_PARTY_RUN_MODE_BUTTON[0], EXIT_PARTY_RUN_MODE_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


def close_game_settings():
    logbus.log("🖱️ Closing Game Settings...")
    safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, EXIT_GAME_SETTINGS_BUTTON[0], EXIT_GAME_SETTINGS_BUTTON[1])
    time.sleep(random.uniform(0.8, 1.4))


# ===================================================================================
# TREASURE GACHA & SMART SALVAGE
# -----------------------------------------------------------------------------------
# The 9-step routine below is fully template-driven. When a template has not been
# calibrated yet the helper falls back to the coordinate in config.py (and logs a
# warning so it is obvious which assets still need to be captured). Set
# ``config.TREASURE_ALLOW_COORD_FALLBACK = False`` to disable that once every
# TREASURE_* template exists.
# ===================================================================================

def _any_template_exists(templates) -> bool:
    """Return True if at least one template file in ``templates`` exists on disk."""
    if not templates:
        return False
    for name in templates:
        if os.path.exists(os.path.join(config.TEMPLATE_DIR, name)):
            return True
    return False


def _tap_template_or_coord(templates, region, coord, label, timeout=3.0) -> bool:
    """Locate a UI element by template and tap its centre, else fall back to ``coord``.

    Returns True when *something* was tapped (template match or coordinate fallback),
    False when nothing was found and the coordinate fallback is disabled.
    """
    deadline = time.time() + max(0.0, timeout)
    while time.time() < deadline:
        screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
        matches = detect_templates(screen, templates, region) if templates else []
        if matches:
            x, y, w, h = matches[0]
            tx, ty = x + w // 2, y + h // 2
            safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, tx, ty)
            logbus.log(f"👉 {label}: tapped template at ({tx}, {ty})")
            return True
        time.sleep(0.3)

    if coord is not None and config.TREASURE_ALLOW_COORD_FALLBACK:
        logbus.log(
            f"⚠️ {label}: template not found — using fallback coordinate {coord}. "
            f"(calibrate {label} for reliability)",
            "warning",
        )
        safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, coord[0], coord[1])
        return True

    logbus.log(f"❌ {label}: not found and coordinate fallback disabled.", "error")
    return False


def open_treasure_menu():
    """Step 1 - navigate to the Treasure menu from the lobby."""
    return _tap_template_or_coord(
        config.TREASURE_MENU_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_MENU_BUTTON, "Open Treasure Menu",
    )


def open_treasure_draw_tab():
    """Step 2 - open the Draw (Gacha) tab."""
    return _tap_template_or_coord(
        config.TREASURE_DRAW_TAB_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_DRAW_TAB_BUTTON, "Open Draw Tab",
    )


def draw_treasure_gacha(rounds: int) -> int:
    """Steps 3-5 - verify coins then run the 5,000-coin gacha ``rounds`` times.

    Returns the number of confirmed draws.
    """
    rounds = max(1, int(rounds))
    drawn = 0
    for i in range(rounds):
        screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
        coins = extract_lobby_coins(screen, config.LOBBY_COIN_REGION)
        if coins >= 0 and coins < config.TREASURE_GACHA_COST:
            logbus.log(
                f"🪙 Not enough coins ({coins:,} < {config.TREASURE_GACHA_COST:,}). "
                f"Stopping gacha after {drawn} draw(s).",
                "warning",
            )
            break
        if coins < 0:
            logbus.log(
                "🪙 Coin balance unreadable — proceeding without the 5,000-coin check "
                "(calibrate config.LOBBY_COIN_REGION for a hard check).",
                "warning",
            )

        logbus.log(f"🎰 Draw {i + 1}/{rounds}: 5,000-Coin gacha...")
        if not _tap_template_or_coord(
            config.TREASURE_5K_GACHA_TEMPLATE, config.TREASURE_BUTTON_REGION,
            config.TREASURE_5K_GACHA_BUTTON, "5,000-Coin Gacha",
        ):
            break
        time.sleep(random.uniform(1.5, 2.5))

        _tap_template_or_coord(
            config.TREASURE_CONFIRM_TEMPLATE, config.TREASURE_BUTTON_REGION,
            config.TREASURE_CONFIRM_BUTTON, "Confirm draw result",
        )
        time.sleep(random.uniform(1.0, 1.8))
        drawn += 1
    return drawn


def open_treasure_cabinet():
    """Step 6 - open the inventory (cabinet)."""
    return _tap_template_or_coord(
        config.TREASURE_CABINET_BTN_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_CABINET_BTN_BUTTON, "Open Treasure Cabinet",
    )


def sort_treasure_inventory():
    """Step 7 - sort so newly obtained treasures sit at the top."""
    ok = _tap_template_or_coord(
        config.TREASURE_SORT_BTN_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_SORT_BTN_BUTTON, "Open Sort menu",
    )
    time.sleep(random.uniform(0.8, 1.4))
    ok = _tap_template_or_coord(
        config.TREASURE_SORT_OBTAINED_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_SORT_OBTAINED_BUTTON, "Sort by Obtained",
    ) and ok
    return ok


def enable_treasure_extract_mode():
    """Step 8 - switch the inventory into Extract (salvage) mode."""
    return _tap_template_or_coord(
        config.TREASURE_EXTRACT_MODE_BTN_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_EXTRACT_MODE_BTN_BUTTON, "Enable Extract mode",
    )


def _resolve_salvage_templates() -> list:
    """Return templates of treasures that are known safe to extract.

    Auto-discovers every ``TREASURE_SALVAGE_<name>.png`` file in templates/ (so you
    can just drop new low-tier images in anytime). Falls back to
    ``config.TREASURE_SALVAGE_TEMPLATE`` when auto-discovery finds nothing.
    """
    discovered = []
    if os.path.isdir(config.TEMPLATE_DIR):
        discovered = sorted(
            f for f in os.listdir(config.TEMPLATE_DIR)
            if f.startswith("TREASURE_SALVAGE_") and f.lower().endswith(".png")
        )
    if discovered:
        return discovered
    return list(config.TREASURE_SALVAGE_TEMPLATE or [])


def _scan_and_select_low_tier(rainbow_templates, cookie_templates, salvage_templates) -> int:
    """One pass over the inventory grid.

    POSITIVE MATCH strategy: a slot is tapped only when it matches at least one
    ``salvage_templates`` image AND does not match any protection template. If
    ``salvage_templates`` is empty the caller must already have refused to run.

    Returns how many slots were selected in this pass.
    """
    positive_select = bool(salvage_templates)
    origin_x, origin_y = config.TREASURE_GRID_ORIGIN
    selected = 0
    for row in range(config.TREASURE_GRID_ROWS):
        if selected >= config.TREASURE_MAX_SELECTIONS:
            break
        for col in range(config.TREASURE_GRID_COLS):
            if selected >= config.TREASURE_MAX_SELECTIONS:
                break
            cx = origin_x + col * config.TREASURE_SLOT_W
            cy = origin_y + row * config.TREASURE_SLOT_H

            screen = device_capture_screen(config.DEVICE_IP, config.DEVICE_PORT)
            if screen is None:
                continue
            x1 = max(0, cx - config.TREASURE_SLOT_W // 2)
            y1 = max(0, cy - config.TREASURE_SLOT_H // 2)
            x2 = min(screen.shape[1], cx + config.TREASURE_SLOT_W // 2)
            y2 = min(screen.shape[0], cy + config.TREASURE_SLOT_H // 2)
            slot = screen[y1:y2, x1:x2]
            if slot.size == 0:
                continue

            # 1) Never touch protected treasures (belt-and-braces in both modes).
            if detect_templates(slot, rainbow_templates) or detect_templates(slot, cookie_templates):
                continue  # protected — never select

            # 2) POSITIVE MATCH: only tap what we positively know is safe.
            if positive_select and not detect_templates(slot, salvage_templates):
                continue  # not in the salvageable set — leave it alone

            safe_device_tap(config.DEVICE_IP, config.DEVICE_PORT, cx, cy)
            selected += 1
            time.sleep(random.uniform(0.15, 0.3))
    return selected


def _confirm_extraction() -> bool:
    """Extract is confirmed with TWO taps of a visually-similar "Extract" button that
    sits at different positions.

    1st tap: the Extract trigger (opens the confirmation pop-up).
    2nd tap: the Extract confirm button *inside* the pop-up — different position from
    the trigger. A dedicated pop-up template is preferred; when it is missing the
    routine reuses the shared extract-button template (same look) and falls back to
    ``TREASURE_EXTRACT_POPUP_CONFIRM_BUTTON`` for coordinates.
    """
    popup_templates = config.TREASURE_EXTRACT_POPUP_TEMPLATE
    if not _any_template_exists(popup_templates):
        popup_templates = config.TREASURE_EXTRACT_CONFIRM_TEMPLATE

    logbus.log("🧨 Tapping Extract (1/2 — trigger)...")
    if not _tap_template_or_coord(
        config.TREASURE_EXTRACT_CONFIRM_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_EXTRACT_CONFIRM_BUTTON, "Extract trigger",
    ):
        logbus.log("❌ Extract trigger tap failed.", "error")
        return False
    time.sleep(random.uniform(1.2, 2.0))  # wait for the confirmation pop-up

    logbus.log("🧨 Tapping Extract (2/2 — pop-up confirm)...")
    if not _tap_template_or_coord(
        popup_templates, config.TREASURE_BUTTON_REGION,
        config.TREASURE_EXTRACT_POPUP_CONFIRM_BUTTON, "Extract pop-up confirm",
    ):
        logbus.log("⚠️ Pop-up confirm tap failed — extraction may not have run.", "warning")
        return False
    time.sleep(random.uniform(2.0, 3.0))  # let the extraction finish
    return True


def smart_select_and_extract_treasures(preserve_rainbow=True, preserve_cookie=True) -> int:
    """Step 9 - repeatedly select + extract salvageable treasures until none remain.

    Selection strategy (``config.TREASURE_POSITIVE_SELECT``):
      * POSITIVE MATCH (default): only treasures matching a ``TREASURE_SALVAGE_*.png``
        template are selected — anything you did not approve is never touched. This is
        what you want when rainbow/S-tier items are too common to enumerate.
      * EXCLUSION (legacy): everything that is NOT rainbow-border or cookie-specific is
        selected (needs both protection templates).

    Returns the total number of treasures extracted across all passes.
    """
    rainbow_templates = config.TREASURE_RAINBOW_BORDER_TEMPLATE if preserve_rainbow else []
    cookie_templates = config.TREASURE_COOKIE_ICON_TEMPLATE if preserve_cookie else []
    positive = bool(config.TREASURE_POSITIVE_SELECT)
    salvage_templates = _resolve_salvage_templates() if positive else []

    # --- Guards ---------------------------------------------------------------
    blockers = []
    if positive and not salvage_templates:
        blockers.append(
            "at least one TREASURE_SALVAGE_*.png template (positive-select needs "
            "something to match)"
        )
    if not positive:
        if preserve_rainbow and not _any_template_exists(rainbow_templates):
            blockers.append("rainbow border (TREASURE_RAINBOW_1.png)")
        if preserve_cookie and not _any_template_exists(cookie_templates):
            blockers.append("cookie icon (TREASURE_COOKIE_1.png)")
    if blockers:
        logbus.log(
            "🛡️ SMART SELECT blocked: missing " + " and ".join(blockers) +
            ". Refusing to salvage to avoid touching the wrong treasure.",
            "warning",
        )
        return 0

    if positive:
        if preserve_rainbow and not _any_template_exists(rainbow_templates):
            logbus.log(
                "🛡️ Note: rainbow protection template missing — the positive-select "
                "filter keeps it safe anyway (it won't match any salvageable template).",
                "warning",
            )
        if preserve_cookie and not _any_template_exists(cookie_templates):
            logbus.log(
                "🍪 Note: cookie protection template missing — the positive-select "
                "filter keeps it safe anyway.",
                "warning",
            )
        logbus.log(
            f"✅ SMART SELECT strategy: POSITIVE MATCH with {len(salvage_templates)} "
            f"salvageable template(s): {', '.join(salvage_templates)}.",
            "info",
        )

    total_extracted = 0
    max_passes = max(1, int(config.TREASURE_EXTRACT_MAX_PASSES))
    for pass_no in range(1, max_passes + 1):
        selected = _scan_and_select_low_tier(rainbow_templates, cookie_templates, salvage_templates)
        if selected <= 0:
            logbus.log("♻️ No salvageable treasures left — extraction complete.")
            break
        logbus.log(
            f"♻️ Pass {pass_no}/{max_passes}: selected {selected} salvageable treasure(s) "
            f"— confirming extraction (2-tap)...",
        )
        _confirm_extraction()
        total_extracted += selected
    return total_extracted


def return_to_lobby():
    """Return from the Treasure menu back to the main lobby."""
    return _tap_template_or_coord(
        config.TREASURE_LOBBY_BACK_TEMPLATE, config.TREASURE_BUTTON_REGION,
        config.TREASURE_LOBBY_BACK_BUTTON, "Return to Lobby",
    )


def run_treasure_gacha_salvage(rounds=1, auto_dismantle=True,
                               preserve_rainbow=True, preserve_cookie=True) -> bool:
    """Execute the complete 9-step Treasure Gacha & Smart Salvage routine.

    Returns True if the session ran to completion (even if it salvaged 0 items).
    """
    logbus.log("💎 === Treasure Gacha & Salvage session started ===")

    # Step 1: Navigate to the Treasure menu.
    if not open_treasure_menu():
        return False
    time.sleep(random.uniform(1.0, 1.8))

    # Step 2: Open the Draw tab.
    open_treasure_draw_tab()
    time.sleep(random.uniform(1.0, 1.6))

    # Steps 3-5: 5,000-coin gacha + confirm, repeated for the configured rounds.
    drawn = draw_treasure_gacha(rounds)
    logbus.log(f"🎰 Gacha draws completed this session: {drawn}")

    # Steps 6-9: inventory clean-up (only when auto-dismantle is enabled).
    if auto_dismantle:
        open_treasure_cabinet()
        time.sleep(random.uniform(1.0, 1.8))
        sort_treasure_inventory()
        time.sleep(random.uniform(0.8, 1.4))
        enable_treasure_extract_mode()
        time.sleep(random.uniform(0.8, 1.4))
        salvaged = smart_select_and_extract_treasures(preserve_rainbow, preserve_cookie)
        logbus.log(f"♻️ Treasure cleanup finished — {salvaged} item(s) queued for extraction.")
    else:
        logbus.log("♻️ Auto-dismantle disabled — leaving the inventory untouched.")

    # Return to the lobby.
    return_to_lobby()
    time.sleep(random.uniform(1.0, 1.8))
    logbus.log("💎 === Treasure Gacha & Salvage session finished ===")
    return True
