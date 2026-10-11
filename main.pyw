"""Cookie Run Classic Automation - PyQt5 Minimalist Dark Dashboard (windowless).

Run with ``pythonw main.pyw`` (or double-click) so **no command-prompt window**
appears. All bot + action logs stream into the in-UI console via ``bot_engine``,
which is registered as the logbus sink.

Launch behaviour
----------------
* The custom window/taskbar icon is resolved from ``config.APP_ICON_CANDIDATES``
  (``templates/app_icon.png`` first, ``bot_icon.ico`` as a fallback).
* ``pythonw`` has no console, so stdout is ``None``. A global ``excepthook``
  writes any crash to ``bot_error.log`` next to this file and shows a dialog.

Design system
-------------
Background : #0F172A (slate)
Card       : #1E293B
Border     : #334155
Accent     : #F97316 (orange brand)
Fonts      : Inter / Segoe UI for labels, JetBrains Mono for numbers & logs.
"""

import html
import json
import os
import sys
import time
import traceback


def _configure_stdio():
    """Force UTF-8 console output so emoji logs never crash on Windows (cp1252)."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_configure_stdio()

LOG_ERROR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_error.log")


def _write_crash(text: str) -> None:
    try:
        with open(LOG_ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except Exception:
        pass


def _excepthook(exc_type, exc, tb):
    text = "".join(traceback.format_exception(exc_type, exc, tb))
    _write_crash(text)
    try:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Cookie Run Bot - Error", text)
    except Exception:
        pass


sys.excepthook = _excepthook

from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen
from PyQt5.QtWidgets import (
    QAbstractButton,
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import config
from adb import device_check_connection, device_reset_app, get_adb_path
from bot_engine import BOOST_OPTIONS, bot_engine
from discord_notifier import discord_notifier

# --------------------------------------------------------------------------- #
# Design tokens
# --------------------------------------------------------------------------- #
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
ACCENT = "#F97316"
GREEN = "#22C55E"
BLUE = "#38BDF8"
AMBER = "#F59E0B"
RED = "#EF4444"
PURPLE = "#A855F7"

STATE_COLORS = {
    "LOBBY": GREEN,
    "IN_GAME_WAITING": AMBER,
    "SCANNING_RELAY": BLUE,
    "GACHA": PURPLE,
    "PAUSED": "#64748B",
    "IDLE": "#64748B",
    "INITIALIZING": MUTED,
}

MODE_LABELS = (
    ("▶  Auto Run / Farming", config.MODE_FARMING),
    ("💎  Treasure Gacha & Salvage", config.MODE_GACHA),
    ("🔀  Hybrid (Run + Gacha)", config.MODE_HYBRID),
)


def _pick_font(candidates, fallback):
    try:
        families = set(QFontDatabase().families())
    except Exception:
        families = set()
    for name in candidates:
        if name in families:
            return name
    return fallback


# NOTE: QFontDatabase must only be queried after a QApplication exists, so these
# are resolved lazily via init_fonts() (called from main() and Dashboard.__init__).
UI_FONT = "Segoe UI"
MONO_FONT = "Consolas"


def init_fonts():
    global UI_FONT, MONO_FONT
    UI_FONT = _pick_font(["Inter", "Segoe UI", "Helvetica Neue", "Arial"], "Segoe UI")
    MONO_FONT = _pick_font(
        ["JetBrains Mono", "Cascadia Mono", "Cascadia Code", "Consolas", "Courier New"],
        "Consolas",
    )


def _set_app_user_model_id() -> None:
    """Give the process a real AppUserModelID so the taskbar shows our icon."""
    if os.name != "nt":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_USER_MODEL_ID)
    except Exception:
        pass


def _resolve_icon_path():
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in config.APP_ICON_CANDIDATES:
        path = os.path.join(here, rel)
        if os.path.isfile(path):
            return path
    return None


SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_settings.json")

DEFAULT_SETTINGS = {
    "device_ip": "127.0.0.1",
    "device_port": 5555,
    "use_fast_start": False,
    "fast_start_min_stock": 10,
    "use_cookie_relay": False,
    "cookie_relay_min_stock": 10,
    "use_desired_random_boost": False,
    "desired_boost_id": "double_coins",
    "detect_relic": True,
    "send_friend_lives": True,
    "stop_goal_rounds_enabled": False,
    "stop_goal_rounds_target": 50,
    "stop_goal_time_enabled": False,
    "stop_goal_time_hours": 2.0,
    "ingame_scan_delay": 100.0,
    "heart_interval_minutes": 60.0,
    "short_relay_exit_delay": 2.0,
    "smart_relay_guard": True,
    "short_relay_exit": False,
    # Mode presets + Treasure Gacha / Salvage
    "bot_mode": config.DEFAULT_BOT_MODE,
    "gacha_rounds": config.DEFAULT_GACHA_ROUNDS,
    "gacha_auto_dismantle": config.DEFAULT_GACHA_AUTO_DISMANTLE,
    "gacha_preserve_rainbow": config.DEFAULT_GACHA_PRESERVE_RAINBOW,
    "gacha_preserve_cookie": config.DEFAULT_GACHA_PRESERVE_COOKIE,
    "gacha_every_n_runs": config.DEFAULT_GACHA_EVERY_N_RUNS,
    "gacha_loop_interval": config.GACHA_LOOP_INTERVAL_SECONDS,
}


def load_settings() -> dict:
    data = dict(DEFAULT_SETTINGS)
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data.update(json.load(f))
        except Exception:
            pass
    return data


def save_settings(settings: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as exc:  # pragma: no cover - best effort persistence
        _write_crash(f"Failed to save settings: {exc}")


# --------------------------------------------------------------------------- #
# Widgets
# --------------------------------------------------------------------------- #
class Switch(QAbstractButton):
    """A small, clean pill toggle switch (no neon, no animation)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(46, 24)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        checked = self.isChecked()

        painter.setPen(QPen(QColor(BORDER), 1))
        painter.setBrush(QColor(GREEN) if checked else QColor("#334155"))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 12, 12)

        knob_x = self.width() - 21 if checked else 3
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FFFFFF") if checked else QColor("#94A3B8"))
        painter.drawEllipse(knob_x, 3, 18, 18)


class ToggleRow(QWidget):
    """Label + description on the left, a Switch on the right."""

    def __init__(self, title, description="", value=False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        self.title = QLabel(title)
        self.title.setStyleSheet(f"color:{TEXT}; font-weight:600;")
        text_box.addWidget(self.title)
        if description:
            desc = QLabel(description)
            desc.setStyleSheet(f"color:{MUTED}; font-size:11px;")
            desc.setWordWrap(True)
            text_box.addWidget(desc)
        layout.addLayout(text_box, 1)

        self.switch = Switch()
        self.switch.setChecked(bool(value))
        layout.addWidget(self.switch, 0, Qt.AlignVCenter)

    def isChecked(self):
        return self.switch.isChecked()

    def setChecked(self, value):
        self.switch.setChecked(bool(value))


class ConnTestThread(QThread):
    finished_test = pyqtSignal(bool, str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

    def run(self):
        try:
            ok, msg = device_check_connection(self.ip, self.port)
        except Exception as exc:  # pragma: no cover
            ok, msg = False, str(exc)
        self.finished_test.emit(ok, msg)


class ResetAppThread(QThread):
    finished_reset = pyqtSignal(bool, str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

    def run(self):
        try:
            device_reset_app(self.ip, self.port)
            self.finished_reset.emit(True, "App restart command executed")
        except Exception as exc:
            self.finished_reset.emit(False, str(exc))


# --------------------------------------------------------------------------- #
# Main window
# --------------------------------------------------------------------------- #
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        init_fonts()
        self.settings = load_settings()
        self.last_log_seq = 0
        self._conn_thread = None
        self._reset_thread = None

        self.setWindowTitle("Cookie Run Classic Automation")
        icon_path = _resolve_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1240, 840)
        self.setMinimumSize(1080, 720)

        self._build_ui()
        self._apply_settings(self.settings)
        self._apply_mode(self._current_mode())
        self._apply_stylesheet()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start(1000)

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.refresh_logs)
        self.log_timer.start(400)

        self.refresh_status()
        QTimer.singleShot(200, self.test_connection)

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(16)

        outer.addWidget(self._build_header())
        outer.addLayout(self._build_kpi_row())

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._build_config_panel(), 4)
        content.addWidget(self._build_right_panel(), 5)
        outer.addLayout(content, 1)

    def _card(self):
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def _build_header(self):
        header = self._card()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Cookie Run Classic Automation")
        title.setObjectName("H1")
        subtitle = QLabel(f"LDPlayer 14 · 1280×720 · ADB {get_adb_path()}")
        subtitle.setObjectName("Sub")
        subtitle.setToolTip("ADB executable used for device control")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)
        layout.addStretch(1)

        # Prominent dynamic Mode selector
        mode_box = QVBoxLayout()
        mode_box.setSpacing(2)
        mode_label = QLabel("MODE PRESET")
        mode_label.setObjectName("CardTitle")
        mode_label.setStyleSheet(f"color:{MUTED};")
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("ModeCombo")
        for label, mode in MODE_LABELS:
            self.mode_combo.addItem(label, mode)
        self.mode_combo.setFixedWidth(230)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_box.addWidget(mode_label)
        mode_box.addWidget(self.mode_combo)
        layout.addLayout(mode_box)

        # ADB status pill
        self.adb_pill = QFrame()
        self.adb_pill.setObjectName("Pill")
        pill_layout = QHBoxLayout(self.adb_pill)
        pill_layout.setContentsMargins(12, 6, 12, 6)
        pill_layout.setSpacing(8)
        self.adb_dot = QLabel()
        self.adb_dot.setFixedSize(9, 9)
        self.adb_status_label = QLabel("Checking ADB...")
        self.adb_status_label.setStyleSheet(f"color:{MUTED}; font-size:12px; font-weight:600;")
        pill_layout.addWidget(self.adb_dot)
        pill_layout.addWidget(self.adb_status_label)
        self._set_adb_indicator(None)
        layout.addWidget(self.adb_pill)

        # Start / Stop toggle
        self.toggle_btn = QPushButton("Start Bot")
        self.toggle_btn.setObjectName("Primary")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setMinimumHeight(42)
        self.toggle_btn.clicked.connect(self.on_toggle_bot)
        layout.addWidget(self.toggle_btn)

        return header

    def _kpi_card(self, title, value="0", subtitle="", accent=ACCENT):
        frame = self._card()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        header_row = QHBoxLayout()
        title_label = QLabel(title.upper())
        title_label.setObjectName("CardTitle")
        header_row.addWidget(title_label)
        header_row.addStretch(1)
        marker = QLabel("●")
        marker.setStyleSheet(f"color:{accent}; font-size:12px;")
        header_row.addWidget(marker)
        layout.addLayout(header_row)

        value_label = QLabel(value)
        value_label.setObjectName("CardValue")
        value_label.setStyleSheet(f"color:{accent};")
        layout.addWidget(value_label)

        sub_label = QLabel(subtitle)
        sub_label.setObjectName("Sub")
        layout.addWidget(sub_label)

        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return frame, value_label, sub_label

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        c1, self.kpi_coins, self.kpi_coins_sub = self._kpi_card("Total Coins", "0", "this session", AMBER)
        c2, self.kpi_xp, self.kpi_xp_sub = self._kpi_card("Total EXP", "0", "this session", BLUE)
        c3, self.kpi_rounds, self.kpi_rounds_sub = self._kpi_card("Matches / Chests", "0", "0 chests", GREEN)
        c4, self.kpi_uptime, self.kpi_state_sub = self._kpi_card("Uptime / State", "00:00:00", "IDLE", MUTED)

        for card in (c1, c2, c3, c4):
            row.addWidget(card)
        return row

    def _group(self, title):
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background:{CARD}; border:1px solid {BORDER}; border-radius:8px; }}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        label = QLabel(title)
        label.setObjectName("GroupTitle")
        layout.addWidget(label)
        return frame, layout

    def _labeled_row(self, label_text, widget):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet(f"color:{MUTED}; font-size:12px;")
        row.addWidget(label)
        row.addStretch(1)
        row.addWidget(widget)
        return row

    def _build_config_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 8, 0)
        vbox.setSpacing(14)

        # --- Connection (always visible) ---------------------------------- #
        conn, conn_layout = self._group("CONNECTION")
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("127.0.0.1")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setFixedWidth(110)
        ip_row = QHBoxLayout()
        ip_row.addWidget(self.ip_edit, 1)
        ip_row.addWidget(self.port_spin, 0)
        conn_layout.addLayout(ip_row)

        presets = QHBoxLayout()
        presets.setSpacing(6)
        for name, port in [("LDPlayer (5555)", 5555), ("LDPlayer 2 (5554)", 5554), ("MuMu (7555)", 7555)]:
            btn = QPushButton(name)
            btn.setObjectName("Ghost")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, p=port: self.port_spin.setValue(p))
            presets.addWidget(btn)
        presets.addStretch(1)
        conn_layout.addLayout(presets)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setObjectName("Ghost")
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.clicked.connect(self.test_connection)
        self.reset_btn = QPushButton("Restart Game App")
        self.reset_btn.setObjectName("Ghost")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_app)
        action_row.addWidget(self.test_btn)
        action_row.addWidget(self.reset_btn)
        conn_layout.addLayout(action_row)

        self.conn_result = QLabel("")
        self.conn_result.setWordWrap(True)
        self.conn_result.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        conn_layout.addWidget(self.conn_result)
        vbox.addWidget(conn)

        # --- Timing & Automation (Mode 1 / 3) ----------------------------- #
        self.run_settings_group, timing_layout = self._group("TIMING & AUTOMATION")

        self.scan_delay_spin = QSpinBox()
        self.scan_delay_spin.setRange(0, 3600)
        self.scan_delay_spin.setSuffix(" s")
        self.scan_delay_spin.setFixedWidth(120)
        self.scan_delay_spin.setToolTip(
            "During a match the bot skips screen capture & template matching for this many\n"
            "seconds (light 1s loop) to keep CPU usage near 0%."
        )
        timing_layout.addLayout(self._labeled_row("In-Game Scan Delay", self.scan_delay_spin))

        self.heart_spin = QSpinBox()
        self.heart_spin.setRange(1, 1440)
        self.heart_spin.setSuffix(" min")
        self.heart_spin.setFixedWidth(120)
        self.heart_spin.setToolTip("Send hearts every N minutes (lobby only, ±2 min jitter).")
        timing_layout.addLayout(self._labeled_row("Send Hearts Every", self.heart_spin))

        self.relay_delay_spin = QDoubleSpinBox()
        self.relay_delay_spin.setRange(0.0, 60.0)
        self.relay_delay_spin.setSingleStep(0.5)
        self.relay_delay_spin.setDecimals(1)
        self.relay_delay_spin.setSuffix(" s")
        self.relay_delay_spin.setFixedWidth(120)
        self.relay_delay_spin.setToolTip("T2 delay applied after a relay/exit tap when Short Relay Exit is on.")
        timing_layout.addLayout(self._labeled_row("Short Relay Exit Delay (T2)", self.relay_delay_spin))

        self.boost_combo = QComboBox()
        for boost in BOOST_OPTIONS:
            self.boost_combo.addItem(boost["name"], boost["id"])
        timing_layout.addLayout(self._labeled_row("Preferred Buff", self.boost_combo))

        self.relay_guard_toggle = ToggleRow(
            "Smart Relay Guard",
            "Never tap the relay twice in the same round to avoid wasted cookies.",
            True,
        )
        timing_layout.addWidget(self.relay_guard_toggle)

        self.short_relay_toggle = ToggleRow(
            "Short Relay Exit",
            "Use the T2 delay above for a fast relay/exit instead of the humanized wait.",
            False,
        )
        timing_layout.addWidget(self.short_relay_toggle)
        vbox.addWidget(self.run_settings_group)

        # --- Gameplay options (Mode 1 / 3) -------------------------------- #
        self.gameplay_group, gameplay_layout = self._group("GAMEPLAY OPTIONS")
        self.fast_start_toggle = ToggleRow("Fast Start", "Auto-buy & use the Fast Start item.", False)
        self.cookie_relay_toggle = ToggleRow("Cookie Relay", "Auto-buy & use the Relay Cookie.", False)
        self.random_boost_toggle = ToggleRow("Random Boost", "Reroll via Multi-Buy until the preferred buff appears.", False)
        self.send_lives_toggle = ToggleRow("Send Hearts", "Receive & send friend lives on the schedule above.", True)
        self.detect_relic_toggle = ToggleRow("Detect Relic", "Open & claim ancient relic rewards.", True)
        for row in (
            self.fast_start_toggle,
            self.cookie_relay_toggle,
            self.random_boost_toggle,
            self.send_lives_toggle,
            self.detect_relic_toggle,
        ):
            gameplay_layout.addWidget(row)
        vbox.addWidget(self.gameplay_group)

        # --- Treasure Gacha & Salvage (Mode 2 / 3) ------------------------ #
        self.treasure_group, treasure_layout = self._group("TREASURE GACHA & SALVAGE")
        self.gacha_rounds_spin = QSpinBox()
        self.gacha_rounds_spin.setRange(1, 50)
        self.gacha_rounds_spin.setSuffix(" draws")
        self.gacha_rounds_spin.setFixedWidth(120)
        self.gacha_rounds_spin.setToolTip("5,000-coin gacha draws per session.")
        treasure_layout.addLayout(self._labeled_row("Gacha Rounds / Session", self.gacha_rounds_spin))

        self.dismantle_toggle = ToggleRow(
            "Auto-Dismantle Low-Tier",
            "After drawing, open the cabinet and extract unwanted treasures.",
            True,
        )
        treasure_layout.addWidget(self.dismantle_toggle)

        self.rainbow_toggle = ToggleRow(
            "Preserve Rainbow / S-Tier",
            "Never salvage treasures with a rainbow border (S/SS tier).",
            True,
        )
        treasure_layout.addWidget(self.rainbow_toggle)

        self.cookie_toggle = ToggleRow(
            "Preserve Cookie Treasures",
            "Never salvage cookie-specific treasures.",
            True,
        )
        treasure_layout.addWidget(self.cookie_toggle)

        strict_note = QLabel(
            "SMART SELECT: the bot only touches treasures that match your approved "
            "TREASURE_SALVAGE_*.png images — nothing else, so rainbow/cookie treasures "
            "are safe by default."
        )
        strict_note.setWordWrap(True)
        strict_note.setStyleSheet(f"color:{AMBER}; font-size:11px;")
        treasure_layout.addWidget(strict_note)
        vbox.addWidget(self.treasure_group)

        # --- Hybrid loop (Mode 3 only) ------------------------------------ #
        self.hybrid_group, hybrid_layout = self._group("HYBRID LOOP")
        self.gacha_every_spin = QSpinBox()
        self.gacha_every_spin.setRange(1, 200)
        self.gacha_every_spin.setSuffix(" runs")
        self.gacha_every_spin.setFixedWidth(120)
        self.gacha_every_spin.setToolTip("Run a Treasure Gacha session every X completed runs.")
        hybrid_layout.addLayout(self._labeled_row("Gacha Session Every", self.gacha_every_spin))
        hybrid_note = QLabel(
            "Runs normally first, then pauses to run a gacha + salvage session from the lobby."
        )
        hybrid_note.setWordWrap(True)
        hybrid_note.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        hybrid_layout.addWidget(hybrid_note)
        vbox.addWidget(self.hybrid_group)

        # --- Discord (always visible) ------------------------------------- #
        discord, discord_layout = self._group("DISCORD NOTIFICATIONS")
        self.discord_toggle = ToggleRow("Enable Webhook", "Push round summaries, chest drops and alerts to Discord.", False)
        discord_layout.addWidget(self.discord_toggle)
        self.webhook_edit = QLineEdit()
        self.webhook_edit.setPlaceholderText("https://discord.com/api/webhooks/...")
        discord_layout.addWidget(self.webhook_edit)
        discord_actions = QHBoxLayout()
        discord_actions.setSpacing(8)
        test_hook = QPushButton("Save & Test")
        test_hook.setObjectName("Ghost")
        test_hook.setCursor(Qt.PointingHandCursor)
        test_hook.clicked.connect(self.save_discord)
        discord_actions.addWidget(test_hook)
        discord_actions.addStretch(1)
        discord_layout.addLayout(discord_actions)
        self.discord_result = QLabel("")
        self.discord_result.setWordWrap(True)
        self.discord_result.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        discord_layout.addWidget(self.discord_result)
        vbox.addWidget(discord)

        vbox.addStretch(1)
        scroll.setWidget(container)
        return scroll

    def _build_right_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(16)

        # Console
        console_card = self._card()
        console_layout = QVBoxLayout(console_card)
        console_layout.setContentsMargins(16, 14, 16, 16)
        console_layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("CONSOLE LOG")
        title.setObjectName("GroupTitle")
        header.addWidget(title)
        header.addStretch(1)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("Ghost")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(lambda: self.console.clear())
        header.addWidget(clear_btn)
        console_layout.addLayout(header)

        self.console = QTextEdit()
        self.console.setObjectName("Console")
        self.console.setReadOnly(True)
        self.console.setAcceptRichText(True)
        self.console.document().setMaximumBlockCount(600)
        console_layout.addWidget(self.console, 1)
        vbox.addWidget(console_card, 1)

        # Analytics / box breakdown
        stats_card = self._card()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(16, 14, 16, 16)
        stats_layout.setSpacing(12)
        stats_title = QLabel("MYSTERY CHEST BREAKDOWN")
        stats_title.setObjectName("GroupTitle")
        stats_layout.addWidget(stats_title)

        boxes_row = QHBoxLayout()
        boxes_row.setSpacing(10)
        self.box_labels = {}
        for grade, label, color in [
            ("wood", "Wood", "#B45309"),
            ("silver", "Silver", "#94A3B8"),
            ("gold", "Gold", "#EAB308"),
            ("rainbow", "Rainbow", "#A855F7"),
        ]:
            tile = QFrame()
            tile.setStyleSheet(f"QFrame {{ background:#0F172A; border:1px solid {BORDER}; border-radius:8px; }}")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(12, 10, 12, 10)
            tile_layout.setSpacing(2)
            name = QLabel(label)
            name.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600;")
            value = QLabel("0")
            value.setObjectName("CardValue")
            value.setStyleSheet(f"color:{color}; font-size:20px;")
            tile_layout.addWidget(name)
            tile_layout.addWidget(value)
            self.box_labels[grade] = value
            boxes_row.addWidget(tile)
        stats_layout.addLayout(boxes_row)

        self.round_last_label = QLabel("Last round: —")
        self.round_last_label.setObjectName("Mono")
        self.round_last_label.setStyleSheet(f"color:{MUTED}; font-size:12px; font-family:'{MONO_FONT}';")
        stats_layout.addWidget(self.round_last_label)

        self.mode_state_label = QLabel("Mode: —")
        self.mode_state_label.setObjectName("Mono")
        self.mode_state_label.setStyleSheet(f"color:{MUTED}; font-size:12px; font-family:'{MONO_FONT}';")
        stats_layout.addWidget(self.mode_state_label)

        footer = QLabel("Screen resolution must stay 1280 × 720 (landscape).")
        footer.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        stats_layout.addWidget(footer)

        vbox.addWidget(stats_card, 0)
        return panel

    def _apply_stylesheet(self):
        qss = f"""
        QMainWindow, QWidget#Root {{ background: {BG}; }}
        QWidget {{ background: transparent; color: {TEXT}; font-size: 13px; }}
        QFrame#Card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}
        QFrame#Pill {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 14px; }}
        QLabel {{ background: transparent; color: {TEXT}; }}
        QLabel#H1 {{ font-size: 18px; font-weight: 700; color: #F8FAFC; }}
        QLabel#Sub {{ font-size: 12px; color: {MUTED}; }}
        QLabel#CardTitle {{ font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: 1px; }}
        QLabel#CardValue {{ font-family: '{MONO_FONT}'; font-size: 24px; font-weight: 700; color: #F8FAFC; }}
        QLabel#GroupTitle {{ font-size: 12px; font-weight: 700; color: #CBD5E1; letter-spacing: 1px; }}
        QLabel#Mono {{ font-family: '{MONO_FONT}'; }}
        QComboBox#ModeCombo {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px;
            padding: 8px 10px; color: #F1F5F9; font-weight: 600; font-size: 13px; }}
        QComboBox#ModeCombo::drop-down {{ border: none; width: 24px; }}
        QComboBox#ModeCombo QAbstractItemView {{ background: {CARD}; border: 1px solid {BORDER};
            selection-background-color: {BORDER}; color: #F1F5F9; outline: none; }}
        QPushButton#Primary {{ background: {GREEN}; color: #052E16; border: none; border-radius: 8px;
            padding: 10px 22px; font-weight: 700; font-size: 14px; }}
        QPushButton#Primary:hover {{ background: #16A34A; }}
        QPushButton#Ghost {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px;
            padding: 7px 13px; color: #CBD5E1; font-weight: 600; }}
        QPushButton#Ghost:hover {{ border-color: #64748B; color: #F1F5F9; }}
        QPushButton#Ghost:disabled {{ color: #475569; border-color: #1E293B; }}
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{ background: {BG}; border: 1px solid {BORDER};
            border-radius: 6px; padding: 6px 8px; color: #F1F5F9; }}
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{ border: 1px solid {ACCENT}; }}
        QComboBox::drop-down {{ border: none; width: 20px; }}
        QComboBox QAbstractItemView {{ background: {CARD}; border: 1px solid {BORDER};
            selection-background-color: {BORDER}; color: #F1F5F9; outline: none; }}
        QTextEdit#Console {{ background: #0B1220; border: 1px solid {BORDER}; border-radius: 8px;
            color: #CBD5E1; padding: 8px; font-family: '{MONO_FONT}'; font-size: 12px; }}
        QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: {BG}; width: 10px; margin: 0; }}
        QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 26px; }}
        QScrollBar::handle:vertical:hover {{ background: #475569; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QToolTip {{ background: {CARD}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px; }}
        """
        self.setStyleSheet(qss)

    # ------------------------------------------------------------ settings --
    def _current_mode(self):
        idx = self.mode_combo.currentIndex()
        return self.mode_combo.itemData(idx) if idx >= 0 else config.DEFAULT_BOT_MODE

    def on_mode_changed(self, _index):
        self._apply_mode(self._current_mode())

    def _apply_mode(self, mode):
        is_farming = mode == config.MODE_FARMING
        is_gacha = mode == config.MODE_GACHA
        is_hybrid = mode == config.MODE_HYBRID
        # Mode 1 (farming): show run controls, hide gacha/salvage + hybrid.
        # Mode 2 (gacha):    show gacha/salvage, hide run controls + hybrid.
        # Mode 3 (hybrid):   show everything.
        self.run_settings_group.setVisible(is_farming or is_hybrid)
        self.gameplay_group.setVisible(is_farming or is_hybrid)
        self.treasure_group.setVisible(is_gacha or is_hybrid)
        self.hybrid_group.setVisible(is_hybrid)

    def _apply_settings(self, data):
        self.ip_edit.setText(str(data.get("device_ip", "127.0.0.1")))
        self.port_spin.setValue(int(data.get("device_port", 5555)))
        self.scan_delay_spin.setValue(int(data.get("ingame_scan_delay", 100)))
        self.heart_spin.setValue(int(data.get("heart_interval_minutes", 60)))
        self.relay_delay_spin.setValue(float(data.get("short_relay_exit_delay", 2.0)))

        mode = data.get("bot_mode", config.DEFAULT_BOT_MODE)
        idx = self.mode_combo.findData(mode)
        if idx < 0:
            idx = self.mode_combo.findData(config.DEFAULT_BOT_MODE)
        if idx >= 0:
            self.mode_combo.setCurrentIndex(idx)

        boost_id = data.get("desired_boost_id", "double_coins")
        idx = self.boost_combo.findData(boost_id)
        if idx >= 0:
            self.boost_combo.setCurrentIndex(idx)

        self.relay_guard_toggle.setChecked(data.get("smart_relay_guard", True))
        self.short_relay_toggle.setChecked(data.get("short_relay_exit", False))

        self.fast_start_toggle.setChecked(data.get("use_fast_start", False))
        self.cookie_relay_toggle.setChecked(data.get("use_cookie_relay", False))
        self.random_boost_toggle.setChecked(data.get("use_desired_random_boost", False))
        self.send_lives_toggle.setChecked(data.get("send_friend_lives", True))
        self.detect_relic_toggle.setChecked(data.get("detect_relic", True))

        self.gacha_rounds_spin.setValue(int(data.get("gacha_rounds", config.DEFAULT_GACHA_ROUNDS)))
        self.dismantle_toggle.setChecked(data.get("gacha_auto_dismantle", config.DEFAULT_GACHA_AUTO_DISMANTLE))
        self.rainbow_toggle.setChecked(data.get("gacha_preserve_rainbow", config.DEFAULT_GACHA_PRESERVE_RAINBOW))
        self.cookie_toggle.setChecked(data.get("gacha_preserve_cookie", config.DEFAULT_GACHA_PRESERVE_COOKIE))
        self.gacha_every_spin.setValue(int(data.get("gacha_every_n_runs", config.DEFAULT_GACHA_EVERY_N_RUNS)))

        self.discord_toggle.setChecked(discord_notifier.enabled)
        self.webhook_edit.setText(discord_notifier.webhook_url)

    def _collect_settings(self) -> dict:
        data = dict(self.settings)  # keep goal settings etc. that have no UI
        data.update(
            {
                "device_ip": self.ip_edit.text().strip() or "127.0.0.1",
                "device_port": int(self.port_spin.value()),
                "ingame_scan_delay": float(self.scan_delay_spin.value()),
                "heart_interval_minutes": float(self.heart_spin.value()),
                "short_relay_exit_delay": float(self.relay_delay_spin.value()),
                "smart_relay_guard": self.relay_guard_toggle.isChecked(),
                "short_relay_exit": self.short_relay_toggle.isChecked(),
                "use_fast_start": self.fast_start_toggle.isChecked(),
                "use_cookie_relay": self.cookie_relay_toggle.isChecked(),
                "use_desired_random_boost": self.random_boost_toggle.isChecked(),
                "desired_boost_id": self.boost_combo.currentData(),
                "send_friend_lives": self.send_lives_toggle.isChecked(),
                "detect_relic": self.detect_relic_toggle.isChecked(),
                "bot_mode": self._current_mode(),
                "gacha_rounds": int(self.gacha_rounds_spin.value()),
                "gacha_auto_dismantle": self.dismantle_toggle.isChecked(),
                "gacha_preserve_rainbow": self.rainbow_toggle.isChecked(),
                "gacha_preserve_cookie": self.cookie_toggle.isChecked(),
                "gacha_every_n_runs": int(self.gacha_every_spin.value()),
                "gacha_loop_interval": config.GACHA_LOOP_INTERVAL_SECONDS,
            }
        )
        return data

    # ------------------------------------------------------------- actions --
    def on_toggle_bot(self):
        if bot_engine.is_running:
            self.toggle_btn.setEnabled(False)
            try:
                bot_engine.stop()
            except Exception as exc:
                self._append_system(f"Stop failed: {exc}", "error")
            self.toggle_btn.setEnabled(True)
            self.refresh_status()
            return

        cfg = self._collect_settings()
        self.settings = cfg
        save_settings(cfg)
        self._apply_discord_from_ui()
        self.toggle_btn.setEnabled(False)
        try:
            res = bot_engine.start(cfg)
            if not res.get("success"):
                self._append_system(res.get("message", "Failed to start"), "error")
        except Exception as exc:
            self._append_system(f"Failed to start: {exc}", "error")
        self.toggle_btn.setEnabled(True)
        self.refresh_status()

    def test_connection(self):
        ip = self.ip_edit.text().strip() or "127.0.0.1"
        port = int(self.port_spin.value())
        self._set_adb_indicator(None)
        self.conn_result.setText("Testing connection...")
        self.conn_result.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        self.test_btn.setEnabled(False)

        self._conn_thread = ConnTestThread(ip, port)
        self._conn_thread.finished_test.connect(self._on_conn_result)
        self._conn_thread.start()

    def _on_conn_result(self, ok, msg):
        self.test_btn.setEnabled(True)
        self._set_adb_indicator(ok)
        if ok:
            self.conn_result.setText(f"Connected: {msg}")
            self.conn_result.setStyleSheet(f"color:{GREEN}; font-size:11px;")
        else:
            self.conn_result.setText(f"Disconnected: {msg}")
            self.conn_result.setStyleSheet(f"color:{RED}; font-size:11px;")

    def reset_app(self):
        ip = self.ip_edit.text().strip() or "127.0.0.1"
        port = int(self.port_spin.value())
        self.reset_btn.setEnabled(False)
        self.conn_result.setText("Restarting the game app...")
        self.conn_result.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        self._reset_thread = ResetAppThread(ip, port)
        self._reset_thread.finished_reset.connect(self._on_reset_result)
        self._reset_thread.start()

    def _on_reset_result(self, ok, msg):
        self.reset_btn.setEnabled(True)
        color = GREEN if ok else RED
        self.conn_result.setText(msg)
        self.conn_result.setStyleSheet(f"color:{color}; font-size:11px;")

    def _apply_discord_from_ui(self):
        discord_notifier.update_settings(
            {
                "webhook_url": self.webhook_edit.text().strip(),
                "enabled": self.discord_toggle.isChecked(),
            }
        )

    def save_discord(self):
        self._apply_discord_from_ui()
        url = self.webhook_edit.text().strip()
        if not url:
            self.discord_result.setText("Enter a webhook URL first.")
            self.discord_result.setStyleSheet(f"color:{AMBER}; font-size:11px;")
            return
        success, msg = discord_notifier.test_webhook(url)
        color = GREEN if success else RED
        self.discord_result.setText(msg)
        self.discord_result.setStyleSheet(f"color:{color}; font-size:11px;")

    def _set_adb_indicator(self, connected):
        if connected is True:
            color = GREEN
            text = "Connected"
            text_color = GREEN
        elif connected is False:
            color = RED
            text = "Disconnected"
            text_color = RED
        else:
            color = "#64748B"
            text = "Checking ADB..."
            text_color = MUTED
        self.adb_dot.setStyleSheet(f"background:{color}; border-radius:4px;")
        self.adb_status_label.setText(text)
        self.adb_status_label.setStyleSheet(f"color:{text_color}; font-size:12px; font-weight:600;")

    # ------------------------------------------------------------ refresh --
    def refresh_status(self):
        status = bot_engine.get_status()
        running = status["is_running"]

        self.kpi_coins.setText(f"{status['coin_stats']['session_earned']:,}")
        self.kpi_coins_sub.setText(f"last round +{status['coin_stats']['last_round']:,}")
        self.kpi_xp.setText(f"{status['coin_stats']['session_xp_earned']:,}")
        self.kpi_xp_sub.setText(f"last round +{status['coin_stats']['last_round_xp']:,}")
        self.kpi_rounds.setText(str(status["rounds_played"]))
        self.kpi_rounds_sub.setText(f"{status['mystery_boxes']} chests collected")

        self.kpi_uptime.setText(status["uptime"])

        state = status["active_state"] if running else "IDLE"
        color = STATE_COLORS.get(state, MUTED)
        extras = []
        if running and status.get("ingame_hold_remaining", 0) > 0:
            extras.append(f"hold {status['ingame_hold_remaining']}s")
        if running and status.get("heart_interval_remaining", 0) > 0:
            mins = status["heart_interval_remaining"] // 60
            extras.append(f"hearts in {mins}m")
        sub = state + (" · " + " · ".join(extras) if extras else "")
        self.kpi_state_sub.setText(sub)
        self.kpi_state_sub.setStyleSheet(f"color:{color}; font-size:12px; font-weight:700;")
        self.kpi_uptime.setStyleSheet(f"color:{color};")

        # Box breakdown
        boxes = status.get("box_counts", {})
        for grade, label in self.box_labels.items():
            label.setText(str(boxes.get(grade, 0)))

        # Mode + gacha session info
        mode = status.get("bot_mode", config.DEFAULT_BOT_MODE)
        gacha_sessions = status.get("gacha_sessions_done", 0)
        since = status.get("rounds_since_gacha", 0)
        every = status.get("gacha_every_n_runs", 0)
        mode_text = mode.capitalize()
        if mode == config.MODE_GACHA:
            mode_text += f" · {gacha_sessions} session(s)"
        elif mode == config.MODE_HYBRID:
            mode_text += f" · gacha in {max(0, every - since)} run(s) · {gacha_sessions} done"
        self.mode_state_label.setText(f"Mode: {mode_text}")

        history = status.get("round_history") or []
        if history:
            last = history[0]
            self.round_last_label.setText(
                f"Last round #{last.get('round')}: +{last.get('coins', 0):,} coins · "
                f"+{last.get('xp', 0):,} EXP · {last.get('box_count', 0)} chests"
            )
        elif running:
            self.round_last_label.setText("Last round: waiting for first result...")
        else:
            self.round_last_label.setText("Last round: —")

        # Toggle button
        if running:
            self.toggle_btn.setText("Stop Bot")
            self.toggle_btn.setStyleSheet(
                f"QPushButton {{ background:{RED}; color:#FFFFFF; border:none; border-radius:8px;"
                f" padding:10px 22px; font-weight:700; font-size:14px; }}"
                f"QPushButton:hover {{ background:#DC2626; }}"
            )
        else:
            self.toggle_btn.setText("Start Bot")
            self.toggle_btn.setStyleSheet(
                f"QPushButton {{ background:{GREEN}; color:#052E16; border:none; border-radius:8px;"
                f" padding:10px 22px; font-weight:700; font-size:14px; }}"
                f"QPushButton:hover {{ background:#16A34A; }}"
            )

    def refresh_logs(self):
        logs = list(bot_engine.logs)
        for entry in logs:
            seq = entry.get("seq")
            if seq is None or seq <= self.last_log_seq:
                continue
            self._append_log(entry)
            self.last_log_seq = seq
        if logs:
            self.last_log_seq = max(self.last_log_seq, logs[-1].get("seq", self.last_log_seq))

    def _append_log(self, entry):
        level = entry.get("level", "info")
        color = {
            "success": "#4ADE80",
            "warning": "#FBBF24",
            "error": "#F87171",
            "stage": BLUE,
        }.get(level, "#CBD5E1")
        ts = entry.get("time", time.strftime("%H:%M:%S"))
        msg = html.escape(entry.get("message", ""))
        self.console.append(
            f'<span style="color:#64748B">{ts}</span>&nbsp; '
            f'<span style="color:{color}">{msg}</span>'
        )
        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _append_system(self, message, level="info"):
        self._append_log({"time": time.strftime("%H:%M:%S"), "message": message, "level": level})

    # --------------------------------------------------------------- close --
    def closeEvent(self, event):
        try:
            self.status_timer.stop()
            self.log_timer.stop()
            if bot_engine.is_running:
                bot_engine.stop()
        except Exception:
            pass
        event.accept()


def main():
    _set_app_user_model_id()
    app = QApplication(sys.argv)
    app.setApplicationName("Cookie Run Classic Automation")
    icon_path = _resolve_icon_path()
    if icon_path:
        # Window and taskbar icon (also set on Dashboard for per-window coverage).
        app.setWindowIcon(QIcon(icon_path))
    init_fonts()
    app.setFont(QFont(UI_FONT, 10))
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()