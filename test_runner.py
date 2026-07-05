"""
test_runner.py
--------------
Quick test script:
  1. Starts the monitor in a background thread.
  2. Creates, modifies, and deletes files in watched_folder/.
  3. Waits for events to be captured.
  4. Prints a formatted report of all captured events.
  5. Shows the contents of the generated log file.
"""

import sys
import io
import os
import time
import threading
import json

# Force UTF-8 on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from watchdog.observers import Observer
import config
from monitor import FileEventLogger, AlertSystem, FileEventHandler


WATCH_DIR = os.path.join(os.path.dirname(__file__), "watched_folder")
os.makedirs(WATCH_DIR, exist_ok=True)

# ── Build components ─────────────────────────────────────────────────────────
logger = FileEventLogger(
    logs_dir=config.LOGS_DIRECTORY,
    prefix="test_run",
)
alert_system = AlertSystem(
    console_enabled=True,
    alert_on_events={"created", "modified", "deleted"},   # alert on ALL for testing
)
handler = FileEventHandler(
    logger=logger,
    alert_system=alert_system,
    allowed_extensions=set(),   # monitor everything
)

observer = Observer()
observer.schedule(handler, WATCH_DIR, recursive=True)
observer.start()

print("\n" + "=" * 60)
print("  FILE SYSTEM MONITOR - TEST RUN")
print("=" * 60)
print(f"  Watching : {WATCH_DIR}")
print("=" * 60)

# ── Simulate file events ─────────────────────────────────────────────────────
print("\n  [*] Starting test actions ...\n")
time.sleep(0.5)

# 1. CREATE
f1 = os.path.join(WATCH_DIR, "hello.txt")
with open(f1, "w", encoding="utf-8") as fh:
    fh.write("Hello, Monitoring System!\n")
print("  [ACTION] Created  : hello.txt")
time.sleep(1)

# 2. MODIFY
with open(f1, "a", encoding="utf-8") as fh:
    fh.write(f"Modified at {time.strftime('%H:%M:%S')}\n")
print("  [ACTION] Modified : hello.txt")
time.sleep(1)

# 3. CREATE a second file
f2 = os.path.join(WATCH_DIR, "data.json")
with open(f2, "w", encoding="utf-8") as fh:
    json.dump({"status": "ok", "value": 42}, fh)
print("  [ACTION] Created  : data.json")
time.sleep(1)

# 4. DELETE first file
os.remove(f1)
print("  [ACTION] Deleted  : hello.txt")
time.sleep(1)

# 5. DELETE second file
os.remove(f2)
print("  [ACTION] Deleted  : data.json")
time.sleep(1)

# ── Stop observer ─────────────────────────────────────────────────────────────
observer.stop()
observer.join()
logger.close()

# ── Print captured events report ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("  CAPTURED EVENTS REPORT")
print("=" * 60)

icons = {"created": "[+]", "modified": "[~]", "deleted": "[-]"}

for i, record in enumerate(handler.event_store, 1):
    icon  = icons.get(record["event_type"], "[?]")
    ts    = record["timestamp"][11:23]
    etype = record["event_type"].upper()
    fname = record["file_name"]
    size  = f"{record['size_bytes']:,} B" if record["size_bytes"] is not None else "N/A"

    print(f"  {i:02}. {icon} {etype:<8}  {ts}  {fname:<20} ({size})")

print("=" * 60)
print(f"\n  Total events captured : {len(handler.event_store)}")

# ── Show raw log file ─────────────────────────────────────────────────────────
print(f"\n  Log file : {logger.log_path}")
print("  " + "-" * 58)
with open(logger.log_path, encoding="utf-8") as lf:
    for line in lf:
        record = json.loads(line)
        print(f"  {line.strip()}")

print("\n  Test complete!\n")
