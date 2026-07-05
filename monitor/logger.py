"""
monitor/logger.py
-----------------
JSON-structured, rotating-file logger for file-system events.

Each line in the log file is a self-contained JSON object (JSON Lines format),
making it trivial to stream, grep, or ingest into any analytics pipeline.

Schema of each log record
--------------------------
{
    "timestamp"  : "2026-05-02T13:45:00.123456+03:00",  // ISO-8601
    "event_type" : "created" | "modified" | "deleted",
    "file_path"  : "/absolute/path/to/file.txt",
    "file_name"  : "file.txt",
    "extension"  : ".txt",
    "size_bytes" : 1024,          // null if file no longer exists (deleted)
    "is_directory": false
}
"""

import json
import os
import logging
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iso_now() -> str:
    """Return current local time as an ISO-8601 string with UTC offset."""
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    return datetime.now(local_tz).isoformat()


def _file_size(path: str) -> int | None:
    """Return file size in bytes, or None if the file doesn't exist."""
    try:
        return os.path.getsize(path)
    except OSError:
        return None


# ---------------------------------------------------------------------------
# FileEventLogger
# ---------------------------------------------------------------------------

class FileEventLogger:
    """
    Writes structured JSON-Lines log records to a rotating log file.

    Parameters
    ----------
    logs_dir    : Directory where log files are stored (created if absent).
    prefix      : Prefix for the log file name.
    max_bytes   : Maximum file size before rotation (default 10 MB).
    backup_count: Number of backup files to retain after rotation.
    """

    def __init__(
        self,
        logs_dir: str,
        prefix: str = "fs_events",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ) -> None:
        os.makedirs(logs_dir, exist_ok=True)

        # Unique log file per run (timestamped)
        run_ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(logs_dir, f"{prefix}_{run_ts}.jsonl")

        # Set up a dedicated Python logger that writes raw JSON lines
        self._logger = logging.getLogger(f"fs_monitor.{run_ts}")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False          # don't bubble up to root logger

        handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        # Formatter emits ONLY the message — we embed all metadata in the JSON
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)

        self.log_path = log_path
        print(f"  📄  Logging events to: {log_path}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_event(
        self,
        event_type: str,
        file_path: str,
        is_directory: bool = False,
    ) -> dict[str, Any]:
        """
        Build a structured record for the given event, write it to the log
        file, and return the record dict (raw data for further processing).

        Parameters
        ----------
        event_type   : One of 'created', 'modified', 'deleted'.
        file_path    : Absolute path of the affected file/directory.
        is_directory : True if the event targets a directory.

        Returns
        -------
        dict  — The raw event record (can be passed to an alert system,
                queued for analysis, sent to a message broker, etc.)
        """
        record: dict[str, Any] = {
            "timestamp"   : _iso_now(),
            "event_type"  : event_type,
            "file_path"   : os.path.normpath(file_path),
            "file_name"   : os.path.basename(file_path),
            "extension"   : os.path.splitext(file_path)[1].lower(),
            "size_bytes"  : _file_size(file_path),
            "is_directory": is_directory,
        }
        self._logger.info(json.dumps(record, ensure_ascii=False))
        return record

    def close(self) -> None:
        """Flush and close all log handlers gracefully."""
        for handler in self._logger.handlers[:]:
            handler.flush()
            handler.close()
            self._logger.removeHandler(handler)
