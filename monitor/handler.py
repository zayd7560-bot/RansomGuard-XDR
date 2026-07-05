"""
monitor/handler.py
------------------
Watchdog event handler.

FileEventHandler wires together the logger and the alert system.  It is the
single component that watchdog calls for every file-system event, so all
filtering, logging, and alerting happens here in one controlled place.

Raw event data (dicts) are also appended to `self.event_store` so that the
caller can access them programmatically for further processing / analysis.
"""

import os
from typing import Any
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    DirCreatedEvent,
    DirModifiedEvent,
    DirDeletedEvent,
)

from .logger import FileEventLogger
from .alerts import AlertSystem
from .behavior import BehaviorAnalyzer


class FileEventHandler(FileSystemEventHandler):
    """
    Watchdog handler that intercepts create / modify / delete events,
    applies optional extension filtering, logs each event as a structured
    JSON record, fires alerts, and stores the raw event dicts.

    Parameters
    ----------
    logger             : FileEventLogger instance.
    alert_system       : AlertSystem instance.
    allowed_extensions : Set of lower-case extensions to allow (e.g. {".py"}).
                         An empty set means "allow everything".
    """

    def __init__(
        self,
        logger: FileEventLogger,
        alert_system: AlertSystem,
        allowed_extensions: set[str] | None = None,
    ) -> None:
        super().__init__()
        self._logger     = logger
        self._alerts     = alert_system
        self._filter_ext = allowed_extensions or set()
        self._analyzer   = BehaviorAnalyzer()

        # Raw event store — access via handler.event_store
        self.event_store: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Watchdog callbacks
    # ------------------------------------------------------------------

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        self._process(event, "created")

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        self._process(event, "modified")

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent) -> None:
        self._process(event, "deleted")

    # ------------------------------------------------------------------
    # Core processing pipeline
    # ------------------------------------------------------------------

    def _process(self, event: Any, event_type: str) -> None:
        """Filter → Log → Alert → Store."""
        path         = event.src_path
        is_directory = event.is_directory

        # ── 1. Extension filter (skip directories for extension check) ──
        if not is_directory and self._filter_ext:
            ext = os.path.splitext(path)[1].lower()
            if ext not in self._filter_ext:
                return                          # silently skip

        # ── 2. Log the event (returns the raw record dict) ──
        record = self._logger.log_event(event_type, path, is_directory)

        # ── 3. Behavioral Analysis ──
        behavior = self._analyzer.process_event(record)
        if behavior == "Suspicious":
            # Just print a quick inline warning; AlertSystem can also be modified to handle this
            print(f"  ⚠️  [WARNING] Suspicious behavior detected on {path} (High entropy & Mod Rate)!")

        # ── 4. Dispatch alerts ──
        self._alerts.dispatch(record)

        # ── 5. Append to in-memory event store ──
        self.event_store.append(record)

        # ── 6. Print a minimal status line to the console ──
        self._print_status(record)

    # ------------------------------------------------------------------
    # Console status line (always shown, regardless of alert config)
    # ------------------------------------------------------------------

    @staticmethod
    def _print_status(record: dict[str, Any]) -> None:
        icons = {"created": "＋", "modified": "～", "deleted": "－"}
        icon  = icons.get(record["event_type"], "•")
        ts    = record["timestamp"][11:23]          # HH:MM:SS.microsec slice
        kind  = "DIR " if record["is_directory"] else "FILE"
        print(
            f"  {icon} [{ts}] {record['event_type'].upper():<8} "
            f"{kind}  {record['file_path']}"
        )
