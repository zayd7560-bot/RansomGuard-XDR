"""
monitor/alerts.py
-----------------
Alert dispatcher for file-system events.

Supports two channels:
  1. Console  — colour-coded output using ANSI escape codes.
  2. E-mail   — optional; configured in config.py.

The AlertSystem is intentionally decoupled from the logger and handler so it
can be swapped / extended (e.g. Slack webhook, SMS) without touching core logic.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any


# ---------------------------------------------------------------------------
# ANSI colour helpers (Windows 10+ supports VT100 via conhost / Windows Terminal)
# ---------------------------------------------------------------------------

class _Colour:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GREY   = "\033[90m"


_EVENT_COLOUR = {
    "created" : _Colour.GREEN,
    "modified": _Colour.YELLOW,
    "deleted" : _Colour.RED,
}

_EVENT_ICON = {
    "created" : "✅",
    "modified": "✏️ ",
    "deleted" : "🗑️ ",
}


# ---------------------------------------------------------------------------
# AlertSystem
# ---------------------------------------------------------------------------

class AlertSystem:
    """
    Dispatches alerts for file-system events to one or more channels.

    Parameters
    ----------
    console_enabled  : Print colour-coded alerts to stdout.
    alert_on_events  : Set of event types that trigger an alert.
    email_enabled    : Send e-mail notifications.
    email_config     : Dict with SMTP credentials & recipients (see config.py).
    """

    def __init__(
        self,
        console_enabled: bool = True,
        alert_on_events: set[str] | None = None,
        email_enabled: bool = False,
        email_config: dict[str, Any] | None = None,
    ) -> None:
        self._console  = console_enabled
        self._triggers = alert_on_events or {"created", "deleted"}
        self._email    = email_enabled
        self._ecfg     = email_config or {}

        # Enable ANSI colours on Windows (no-op on other platforms)
        _enable_windows_ansi()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dispatch(self, record: dict[str, Any]) -> None:
        """
        Evaluate the event record and fire the appropriate alert channels.

        Parameters
        ----------
        record : Raw event dict produced by FileEventLogger.log_event().
        """
        event_type = record.get("event_type", "")
        if event_type not in self._triggers:
            return

        if self._console:
            self._console_alert(record)

        if self._email:
            self._email_alert(record)

    # ------------------------------------------------------------------
    # Console channel
    # ------------------------------------------------------------------

    def _console_alert(self, record: dict[str, Any]) -> None:
        event_type = record["event_type"]
        colour     = _EVENT_COLOUR.get(event_type, _Colour.WHITE)
        icon       = _EVENT_ICON.get(event_type, "📌")
        ts         = record["timestamp"]
        path       = record["file_path"]
        size       = record.get("size_bytes")
        size_str   = f"  ({size:,} bytes)" if size is not None else ""

        tag = f"{colour}{_Colour.BOLD}[{event_type.upper():^8}]{_Colour.RESET}"
        print(
            f"\n  {icon}  {tag}  "
            f"{_Colour.GREY}{ts}{_Colour.RESET}\n"
            f"      {_Colour.CYAN}Path :{_Colour.RESET} {path}{size_str}"
        )

    # ------------------------------------------------------------------
    # E-mail channel
    # ------------------------------------------------------------------

    def _email_alert(self, record: dict[str, Any]) -> None:
        try:
            cfg     = self._ecfg
            subject = (
                f"{cfg.get('subject_prefix', '[FS-Monitor]')} "
                f"{record['event_type'].upper()} — {record['file_name']}"
            )
            body = (
                f"File System Event Detected\n"
                f"{'=' * 40}\n"
                f"Event     : {record['event_type']}\n"
                f"Timestamp : {record['timestamp']}\n"
                f"File Path : {record['file_path']}\n"
                f"File Name : {record['file_name']}\n"
                f"Extension : {record['extension']}\n"
                f"Size      : {record.get('size_bytes', 'N/A')} bytes\n"
            )
            msg = MIMEMultipart()
            msg["From"]    = cfg["sender"]
            msg["To"]      = ", ".join(cfg["recipients"])
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
                server.starttls()
                server.login(cfg["sender"], cfg["password"])
                server.sendmail(cfg["sender"], cfg["recipients"], msg.as_string())
        except Exception as exc:                        # never crash the monitor
            print(f"  ⚠️  Email alert failed: {exc}")


# ---------------------------------------------------------------------------
# Windows ANSI helper
# ---------------------------------------------------------------------------

def _enable_windows_ansi() -> None:
    """Enable VT100 ANSI escape codes on Windows consoles (safe no-op elsewhere)."""
    try:
        import ctypes, sys
        if sys.platform == "win32":
            kernel32 = ctypes.windll.kernel32      # type: ignore[attr-defined]
            kernel32.SetConsoleMode(
                kernel32.GetStdHandle(-11),        # STD_OUTPUT_HANDLE
                7,                                 # ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            )
    except Exception:
        pass
