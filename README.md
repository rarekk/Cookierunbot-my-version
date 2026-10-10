# Cookie Run Classic Automation

A high-performance, resource-efficient GUI automation bot for **CookieRun Classic** running on
**LDPlayer 14** (or any Android emulator/device). It combines ADB screen capture with OpenCV
template matching, a state-based sleep engine designed to keep CPU usage low, and a modern
dark-mode dashboard.

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
- **Human-like input** — randomized coordinate jitter and delays on every tap.
- **Two dashboards**
  - **PyQt5 desktop dashboard** (default, `main.py`): minimalist dark theme, KPI cards, timing
    controls, live console.
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

| Launcher        | What it opens                                              |
| --------------- | ---------------------------------------------------------- |
| `START_BOT.bat` | PyQt5 desktop dashboard (default) — `python main.py`       |
| `START_WEB.bat` | FastAPI web dashboard — `python run_web.py`                |

Both dashboards read and write the same `src/bot_settings.json`, so your settings follow you.

## Dashboard (PyQt5)

- **Header** — title, ADB status pill (`Connected` / `Disconnected`), Start/Stop toggle.
- **KPI cards** — Total Coins, Total EXP, Matches / Chests, Uptime / Active State.
  - Active states: `LOBBY`, `IN_GAME_WAITING`, `SCANNING_RELAY`, `PAUSED`.
- **Timing & Automation**
  - In-Game Scan Delay (Sec) — default `100`
  - Send Hearts Every (Min) — default `60`
  - Short Relay Exit Delay (T2) — default `2.0`
  - Preferred Buff dropdown, Smart Relay Guard toggle, Short Relay Exit toggle
- **Gameplay options** — Fast Start, Cookie Relay, Random Boost, Send Hearts, Detect Relic.
- **Discord notifications** — enable + webhook URL + Save & Test.
- **Console log** — JetBrains Mono, timestamped, colour-coded by level.

## Project structure

```
cookierun-classic-bot/
├── main.py              # PyQt5 desktop dashboard (default entry point)
├── run_web.py           # Web dashboard launcher
├── web_server.py        # FastAPI backend for the web dashboard
├── web/index.html       # Web dashboard UI
├── bot_engine.py        # Threaded state machine + stats + performance engine
├── bot.py               # Legacy CLI entry point (upstream loop)
├── actions.py           # Tap/action handlers (Multi-Buy, relay, rewards, captcha...)
├── adb.py               # ADB connection, capture, tap, swipe, app reset
├── config.py            # Ports, timing, template paths, coordinates, ROIs
├── detection.py         # OpenCV template matching, digit/box extraction
├── discord_notifier.py  # Discord webhook notifications
├── debug.py             # Debug screenshot saving
├── requirements.txt     # Python dependencies
├── bot_settings.json    # Shared settings (GUI + web)
├── discord_config.json  # Discord webhook settings
└── templates/           # Detection templates (1280×720)
```

## Configuration (`config.py`)

| Constant                   | Default | Description                                              |
| -------------------------- | ------- | -------------------------------------------------------- |
| `DEVICE_IP`                | `127.0.0.1` | ADB device IP                                        |
| `DEVICE_PORT`              | `5555`  | LDPlayer 14 ADB port                                     |
| `MATCH_THRESHOLD`          | `0.8`   | Minimum template-match confidence                        |
| `SESSION_RESET_INTERVAL`   | `(5400, 10800)` | Random app-restart interval (1.5–3 h)          |
| `INGAME_SCAN_DELAY`        | `100`   | Seconds to skip capture/matching during a match          |
| `HEART_INTERVAL_MINUTES`   | `60`    | Heart sender interval (lobby only)                       |
| `HEART_INTERVAL_JITTER_SECONDS` | `120` | ± jitter applied to the heart interval                |
| `SHORT_RELAY_EXIT_DELAY`   | `2.0`   | T2 delay for short relay/exit                            |
| `LOOP_THROTTLE_MIN/MAX`    | `0.3 / 0.5` | Global main-loop throttle window (seconds)          |

`INGAME_SCAN_TEMPLATES` / `INGAME_SCAN_REGION` control what the post-hold in-game scanner looks
for. Missing template files are skipped gracefully.

## Setup notes

1. Enable ADB / USB debugging in LDPlayer (`Settings → Other → ADB debugging`). Connect with
   `adb connect 127.0.0.1:5555`.
2. Set the emulator display to **1280×720, DPI 240**.
3. Make sure your desired buff is selected in-game so the Multi-Buy reroll can match it.
4. Place any custom detection images in `templates/` (captured at 1280×720).

## Troubleshooting

- **Stage not detected** — capture a debug screenshot (`debug.save_debug_screen`) and compare it
  with `templates/`. Re-capture templates at 1280×720 if needed.
- **ADB connection failed** — verify `adb devices` shows the emulator and the port matches.
- **Wrong tap coordinates** — all coordinates are calibrated for 1280×720.
```
