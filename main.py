"""
main.py
-------
Entry point for the File System Monitoring System.

Usage
-----
  python main.py                        # use defaults from config.py
  python main.py --path ./my_folder     # watch a custom directory
  python main.py --ext .py .txt         # watch only Python & text files
  python main.py --no-recursive         # top-level directory only
  python main.py --help                 # show all options

Press  Ctrl+C  to stop monitoring gracefully.
"""

import argparse
import io
import os
import sys

# ── Force UTF-8 output so emoji/box-drawing chars work on all Windows consoles ──
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
import signal
from datetime import datetime

from watchdog.observers import Observer

import config
from monitor import FileEventLogger, AlertSystem, FileEventHandler
from detection_engine import detect_ransomware

# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fs-monitor",
        description="🔍  Real-time file system monitoring with JSON logging & alerts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --path C:/Projects/data --ext .csv .json
  python main.py --no-recursive --no-console-alerts
        """,
    )
    parser.add_argument(
        "--path", "-p",
        default=config.WATCH_DIRECTORY,
        help="Directory to monitor  (default: %(default)s)",
    )
    parser.add_argument(
        "--ext", "-e",
        nargs="*",
        default=list(config.ALLOWED_EXTENSIONS) or [],
        metavar="EXT",
        help="File extensions to monitor, e.g. .py .txt  (default: all)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        default=not config.RECURSIVE,
        help="Do NOT watch sub-directories  (default: recursive=%(default)s)",
    )
    parser.add_argument(
        "--no-console-alerts",
        action="store_true",
        default=not config.CONSOLE_ALERTS_ENABLED,
        help="Suppress colour-coded console alerts",
    )
    return parser


# ---------------------------------------------------------------------------
# Pretty banner
# ---------------------------------------------------------------------------

def _print_banner(watch_path: str, recursive: bool, extensions: set[str]) -> None:
    width = 60
    now   = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    ext_s = ", ".join(sorted(extensions)) if extensions else "ALL"

    print("\n" + "═" * width)
    print("  🛡️   FILE SYSTEM MONITORING SYSTEM")
    print("═" * width)
    print(f"  📁  Directory : {watch_path}")
    print(f"  🔁  Recursive : {'Yes' if recursive else 'No'}")
    print(f"  🔎  Extensions: {ext_s}")
    print(f"  🕐  Started   : {now}")
    print("═" * width)
    print("  Press  Ctrl+C  to stop.\n")


# ---------------------------------------------------------------------------
# Graceful shutdown helper
# ---------------------------------------------------------------------------

def _stop(observer: Observer, handler: FileEventHandler) -> None:
    print("\n\n  ⏹️   Stopping monitor …")
    observer.stop()
    observer.join()
    handler._logger.close()

    total = len(handler.event_store)
    c = sum(1 for e in handler.event_store if e["event_type"] == "created")
    m = sum(1 for e in handler.event_store if e["event_type"] == "modified")
    d = sum(1 for e in handler.event_store if e["event_type"] == "deleted")

    print("\n  📊  Session Summary")
    print("  " + "─" * 40)
    print(f"  Total events : {total}")
    print(f"    ✅ Created  : {c}")
    print(f"    ✏️  Modified : {m}")
    print(f"    🗑️  Deleted  : {d}")
    print(f"  📄  Log saved : {handler._logger.log_path}")
    print("  " + "─" * 40 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args      = _build_parser().parse_args()
    watch_dir = os.path.abspath(args.path)
    recursive = not args.no_recursive
    extensions: set[str] = {
        (e if e.startswith(".") else f".{e}").lower()
        for e in (args.ext or [])
    }
    console_alerts = not args.no_console_alerts

    # ── Validate directory ──────────────────────────────────────────────
    if not os.path.isdir(watch_dir):
        print(f"  📁  Directory not found — creating: {watch_dir}")
        os.makedirs(watch_dir, exist_ok=True)

    # ── Banner ──────────────────────────────────────────────────────────
    _print_banner(watch_dir, recursive, extensions)

    # ── Build components ────────────────────────────────────────────────
    logger = FileEventLogger(
        logs_dir=config.LOGS_DIRECTORY,
        prefix=config.LOG_FILE_PREFIX,
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
    )

    email_config = {
        "smtp_host"     : config.EMAIL_SMTP_HOST,
        "smtp_port"     : config.EMAIL_SMTP_PORT,
        "sender"        : config.EMAIL_SENDER,
        "password"      : config.EMAIL_PASSWORD,
        "recipients"    : config.EMAIL_RECIPIENTS,
        "subject_prefix": config.EMAIL_SUBJECT_PREFIX,
    } if config.EMAIL_ALERTS_ENABLED else {}

    alert_system = AlertSystem(
        console_enabled=console_alerts,
        alert_on_events=config.ALERT_ON_EVENTS,
        email_enabled=config.EMAIL_ALERTS_ENABLED,
        email_config=email_config,
    )

    handler = FileEventHandler(
        logger=logger,
        alert_system=alert_system,
        allowed_extensions=extensions,
    )

    # ── Start watchdog observer ─────────────────────────────────────────
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=recursive)
    observer.start()

    # ── Register SIGTERM for graceful shutdown (e.g. Docker / systemd) ──
    signal.signal(signal.SIGTERM, lambda *_: _stop(observer, handler))

      # ── Main loop ───────────────────────────────────────────────────────
    try:
        while observer.is_alive():

            modified_count = len([
                e for e in handler.event_store
                if e["event_type"] == "modified"
            ])
            print(handler.event_store)

            entropy = min(8.0, modified_count / 10)

            analysis_data = {
                "modified_files": modified_count,
                "entropy": entropy
            }

            detect_ransomware(analysis_data)

            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        _stop(observer, handler)
if __name__ == "__main__":
    main()
