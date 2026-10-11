# Cookie Run Classic Automation

A high-performance, resource-efficient GUI automation bot for **CookieRun Classic** running on
**LDPlayer 14** (or any Android emulator/device). It combines ADB screen capture with OpenCV
template matching, a state-based sleep engine designed to keep CPU usage low, a modern dark-mode
PyQt5 dashboard, and a web dashboard.

## Highlights

- **Performance engine / anti-throttling**
  - `ingame_scan_delay` — after a match starts the bot skips screen capture *and* template
    matching for N seconds (default **100 s**) while the cookie auto-runs. The thread sits in a
    light 1 s loop, dropping CPU usage to ~0%. Scanning (Relay Cookie / Exit) only resumes after
    the timer expires.
  - Global main-loop throttle `sleep(random.uniform(0.3, 0.5))` keeps detection at ~2–3 FPS.
  - Region-of-Interest (ROI) cropping instead of scanning the full 1280×720 frame.
- **Custom heart sender scheduler** — set the interval in minutes (default **60**). Hearts are sent
  only while in the `LOBBY` state, never during a match, with a ±2 minute anti-detection jitter.
- **Native Multi-Buy reroll** (3-step flow): tap the Random Boost slot (1,200 Coins) → tap the pink
  "Multi" icon → tap the green "Multi-Buy" button for automatic rerolls.
- **Dynamic mode presets** (PyQt5 dashboard): one dropdown switches between
  - **Auto Run / Farming** — run controls only; treasure/gacha hidden.
  - **Treasure Gacha & Salvage** — runs the 9-step gacha routine in a loop; run controls hidden.
  - **Hybrid (Run + Gacha)** — runs normally and pauses for a gacha + salvage session every N runs.
- **Automated Treasure Gacha & Smart Salvage** (9 steps): Treasure menu → Draw tab → verify
  coins ≥ 5,000 → 5,000-coin gacha (+ confirm × rounds) → Cabinet → Sort by Obtained →
  Extract mode → smart-select uses **POSITIVE MATCH**: only treasures that match an approved
  `TREASURE_SALVAGE_*.png` template are ever touched (rainbow/S-tier and cookie items stay safe
  by default — no need to enumerate thousands of protected items) → confirm extraction
  (**two "Extract" taps: trigger + pop-up confirm**) → repeat passes until no salvageable
  treasures remain → back to lobby.
- **Windowless launcher** — `START_BOT.bat` runs `pythonw main.pyw`: no command-prompt window, all
  logs stream into the in-UI console, custom window/taskbar icon, and crashes are written to
  `src/bot_error.log`.
- **Human-like input** — randomized coordinate jitter and delays on every tap.
- **Two dashboards**
  - **PyQt5 desktop dashboard** (default, `main.pyw`): minimalist dark theme, KPI cards, mode
    presets, treasure/salvage panel, live console.
  - **Web dashboard** (`START_WEB.bat` → `run_web.py`): live screen stream, 50-round history,
    Discord settings, viewable from your phone on the same Wi-Fi.
- **Discord webhooks** — round summaries (coins/EXP), chest drops with screenshots, anti-bot alerts,
  connection-loss alerts, and goal-reached notifications.
- **Anti-bot captcha solver**, relic handling, daily rewards, session reset, and more.

## Requirements

- Python 3.10+ (tested on 3.14)
- [ADB](https://developer.android.com/tools/adb) available to the bot (auto-detected in common
  LDPlayer / MuMu / Nox / BlueStacks install paths, or on `PATH`).
- Emulator resolution set to **1280 × 720, landscape (16:9), DPI 240**.
- LDPlayer 14 ADB port: **5555** (second instance: 5554).

Python packages:

```
PyQt5
fastapi
uvicorn
requests
opencv-python
numpy
```

Install everything with the bundled installer or manually:

```bash
INSTALL.bat
# or
pip install -r src/requirements.txt
```

## Running

| Launcher        | What it opens                                                        |
| --------------- | -------------------------------------------------------------------- |
| `START_BOT.bat` | PyQt5 desktop dashboard (default) — windowless `pythonw main.pyw`    |
| `START_WEB.bat` | FastAPI web dashboard — `python run_web.py`                          |

`src/main.py` is a small compatibility shim that runs the same dashboard from a console
(`python main.py`) for debugging.

Both dashboards read and write the same `src/bot_settings.json`, so your settings follow you.

## Dashboard (PyQt5)

- **Header** — title, custom icon, **Mode Preset** dropdown, ADB status pill, Start/Stop toggle.
- **KPI cards** — Total Coins, Total EXP, Matches / Chests, Uptime / Active State.
  - Active states: `LOBBY`, `IN_GAME_WAITING`, `SCANNING_RELAY`, `GACHA`, `PAUSED`.
- **Mode 1 — Auto Run / Farming**: Timing & Automation + Gameplay options.
  - In-Game Scan Delay (Sec), Send Hearts Every (Min), Short Relay Exit Delay (T2),
    Preferred Buff dropdown, Smart Relay Guard, Short Relay Exit, Fast Start, Cookie Relay,
    Random Boost (Multi-Buy), Send Hearts, Detect Relic.
- **Mode 2 — Treasure Gacha & Salvage**: Gacha Rounds / Session, Auto-Dismantle Low-Tier,
  Preserve Rainbow / S-Tier, Preserve Cookie Treasures (+ strict-exclusion notice).
  Run controls are hidden to prevent configuration conflicts.
- **Mode 3 — Hybrid**: both panels plus *Gacha Session Every [X] Runs*.
- **Discord notifications** — enable + webhook URL + Save & Test.
- **Console log** — JetBrains Mono, timestamped, colour-coded by level. Every action/adb line
  streams here through the shared log bus.

## Treasure Gacha & Smart Salvage

The 9-step routine (`actions.run_treasure_gacha_salvage`) is template-driven with configurable
coordinate fallbacks:

1. `open_treasure_menu()` — tap the treasure lobby button.
2. `open_treasure_draw_tab()` — open the Draw (Gacha) tab.
3. `draw_treasure_gacha(rounds)` — reads the coin banner (`extract_lobby_coins`) and verifies
   coins ≥ 5,000 before each draw.
4. Tap the 5,000-coin gacha + confirm — repeated for the configured rounds.
5. `open_treasure_cabinet()` — open the inventory (when auto-dismantle is on).
6. `sort_treasure_inventory()` — sort by "Obtained" so new items appear on top.
7. `enable_treasure_extract_mode()` — switch to extract mode.
8. `smart_select_and_extract_treasures(...)` — walks the grid using **POSITIVE MATCH**
   (`config.TREASURE_POSITIVE_SELECT=True`, default): a slot is selected only when it matches at
   least one auto-discovered `TREASURE_SALVAGE_*.png` template. Anything you did not approve is
   never touched, so common rainbow/S-tier and cookie treasures are safe without huge exclusion
   lists. Belt-and-braces: if a `TREASURE_RAINBOW_1.png` / `TREASURE_COOKIE_1.png` protection
   template exists, slots matching them are still skipped.
9. Confirm extraction with two "Extract" taps (trigger, then pop-up confirm — similar look,
   different position), then re-scan: the select→extract pass repeats (up to
   `TREASURE_EXTRACT_MAX_PASSES`) until no salvageable treasures are left. Finally
   `return_to_lobby()`.

**Safety guard:** if POSITIVE MATCH is enabled but **no `TREASURE_SALVAGE_*.png` exists**, the
routine refuses to select anything (you must approve at least one image of a treasure you want to
extract). With the legacy `TREASURE_POSITIVE_SELECT=False`, it instead refuses when the rainbow or
cookie protection template is missing.

Required templates (drop the `.png` files into `templates/`, captured at 1280×720):

| Step | Template files                          |
| ---- | --------------------------------------- |
| Menu | `TREASURE_MENU_1.png`                   |
| Tab  | `TREASURE_DRAW_TAB_1.png`               |
| Gacha | `TREASURE_5K_GACHA_1.png`, `TREASURE_CONFIRM_1.png` |
| Cabinet / sort | `TREASURE_CABINET_BTN_1.png`, `TREASURE_SORT_BTN_1.png`, `TREASURE_SORT_OBTAINED_1.png` |
| Extract | `TREASURE_EXTRACT_MODE_BTN_1.png`, `TREASURE_EXTRACT_CONFIRM_1.png`, `TREASURE_EXTRACT_POPUP_CONFIRM_1.png` *(optional — pop-up confirm, same look, different spot)* |
| Salvageable *(positive-select)* | **`TREASURE_SALVAGE_<name>.png`** — one or more images of the treasures you WANT to extract. Auto-discovered, so drop in any name: `TREASURE_SALVAGE_LOW1.png`, ... |
| Protection *(exclusion mode / extra safety)* | `TREASURE_RAINBOW_1.png`, `TREASURE_COOKIE_1.png` |
| Back | `TREASURE_LOBBY_BACK_1.png` |

Gacha/salvage coordinates (lobby coin crop, button coords, inventory grid) are in `config.py` under
the `TREASURE_*` constants and start as `CALIBRATE`-me placeholders. Set
`TREASURE_ALLOW_COORD_FALLBACK = False` once every template is in place.

## Project structure

```
cookierun-classic-bot/
├── START_BOT.bat         # Windowless PyQt5 launcher (pythonw main.pyw)
├── START_WEB.bat         # Web dashboard launcher
├── INSTALL.bat           # Dependency installer
├── src/
│   ├── main.pyw          # PyQt5 desktop dashboard (windowless default entry point)
│   ├── main.py           # Console-debug shim -> runs main.pyw
│   ├── run_web.py        # Web dashboard launcher
│   ├── web_server.py     # FastAPI backend for the web dashboard
│   ├── web/index.html    # Web dashboard UI
│   ├── bot_engine.py     # Threaded state machine + stats + performance engine + gacha loop
│   ├── bot.py            # Legacy CLI entry point (upstream loop)
│   ├── actions.py        # Tap/action handlers (Multi-Buy, relay, rewards, captcha, treasure gacha)
│   ├── adb.py            # ADB connection, capture, tap, swipe, app reset
│   ├── config.py         # Ports, timing, template paths, coordinates, ROIs, gacha config
│   ├── detection.py      # OpenCV template matching, digit/box extraction, lobby coins
│   ├── logbus.py         # Tiny in-process log bus (actions/adb -> engine -> UI console)
│   ├── discord_notifier.py  # Discord webhook notifications
│   ├── debug.py          # Debug screenshot saving
│   ├── requirements.txt  # Python dependencies
│   ├── bot_settings.json # Shared settings (GUI + web)
│   ├── discord_config.json  # Discord webhook settings
│   └── templates/        # Detection templates (1280×720) + app_icon.png
```

## Configuration (`config.py`)

| Constant                         | Default | Description                                              |
| -------------------------------- | ------- | -------------------------------------------------------- |
| `DEVICE_IP` / `DEVICE_PORT`      | `127.0.0.1` / `5555` | ADB device                              |
| `MATCH_THRESHOLD`                | `0.8`   | Minimum template-match confidence                        |
| `SESSION_RESET_INTERVAL`         | `(5400, 10800)` | Random app-restart interval (1.5–3 h)          |
| `INGAME_SCAN_DELAY`              | `100`   | Seconds to skip capture/matching during a match          |
| `HEART_INTERVAL_MINUTES`         | `60`    | Heart sender interval (lobby only)                       |
| `SHORT_RELAY_EXIT_DELAY`         | `2.0`   | T2 delay for short relay/exit                            |
| `LOOP_THROTTLE_MIN/MAX`          | `0.3 / 0.5` | Global main-loop throttle window (seconds)          |
| `DEFAULT_BOT_MODE`               | `FARMING` | `FARMING` / `GACHA` / `HYBRID` preset                |
| `TREASURE_GACHA_COST`            | `5000`  | Coin cost of one gacha draw                              |
| `DEFAULT_GACHA_ROUNDS`           | `1`     | Gacha draws per session                                  |
| `DEFAULT_GACHA_AUTO_DISMANTLE`   | `True`  | Clean the inventory after drawing                        |
| `DEFAULT_GACHA_PRESERVE_RAINBOW` | `True`  | Never salvage rainbow / S-tier treasures                 |
| `DEFAULT_GACHA_PRESERVE_COOKIE`  | `True`  | Never salvage cookie-specific treasures                  |
| `DEFAULT_GACHA_EVERY_N_RUNS`     | `10`    | Hybrid mode: session every N runs                        |
| `TREASURE_POSITIVE_SELECT`       | `True`  | Smart-select strategy (True = only approved salvageable templates are touched) |
| `GACHA_LOOP_INTERVAL_SECONDS`    | `30`    | Rest between sessions in pure gacha mode                 |

`INGAME_SCAN_TEMPLATES` / `INGAME_SCAN_REGION` control what the post-hold in-game scanner looks
for. Missing template files are skipped gracefully.

## Setup notes

1. Enable ADB / USB debugging in LDPlayer (`Settings → Other → ADB debugging`). Connect with
   `adb connect 127.0.0.1:5555`.
2. Set the emulator display to **1280×720, DPI 240**.
3. Make sure your desired buff is selected in-game so the Multi-Buy reroll can match it.
4. Place any custom detection images in `templates/` (captured at 1280×720) — including the
   treasure-gacha templates listed above.

## Troubleshooting

- **Stage not detected** — capture a debug screenshot (`debug.save_debug_screen`) and compare it
  with `templates/`. Re-capture templates at 1280×720 if needed.
- **ADB connection failed** — verify `adb devices` shows the emulator and the port matches.
- **Wrong tap coordinates** — all coordinates are calibrated for 1280×720.
- **Dashboard crashes silently** — check `src/bot_error.log` (written by the global excepthook).
- **Gacha refuses to salvage** — a protection template (`TREASURE_RAINBOW_1.png` /
  `TREASURE_COOKIE_1.png`) is missing; the strict-exclusion rule is doing its job.