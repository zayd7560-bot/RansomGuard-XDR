"""
config.py
---------
Central configuration for the File System Monitoring System.
Edit the values here to customise behaviour without touching the core code.
"""

import os

# ---------------------------------------------------------------------------
# DIRECTORY TO MONITOR
# ---------------------------------------------------------------------------
# Absolute or relative path of the folder to watch.
# Defaults to a "watched_folder" directory next to this file.
WATCH_DIRECTORY: str = os.path.join(os.path.dirname(__file__), "watched_folder")

# Watch sub-directories recursively?
RECURSIVE: bool = True

# ---------------------------------------------------------------------------
# FILE-TYPE FILTER
# ---------------------------------------------------------------------------
# Only events for files whose extension is in this set will be processed.
# Use an empty set/list to monitor ALL file types.
# Example: {".txt", ".py", ".csv", ".log"}
ALLOWED_EXTENSIONS: set[str] = set()   # empty = monitor everything

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
## FIX: استخدام مجلد temp الخاص بالمستخدم عشان نتجنب مشكلة الـ Permission Denied
## على Windows، الكتابة جوه D:\project\logs ممكن تحتاج Admin
## بدل كده بنكتب في %TEMP%\ransomware_detector\logs اللي دايمًا متاح
_DEFAULT_LOGS = os.path.join(os.path.dirname(__file__), "logs")
LOGS_DIRECTORY: str = os.environ.get(
    "RDS_LOGS_DIR",
    os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "ransomware_detector", "logs")
    if os.name == "nt" else _DEFAULT_LOGS
)

# Log file name (a new file is created each run using the start timestamp).
LOG_FILE_PREFIX: str = "fs_events"

# Maximum size (bytes) before the logger rotates to a new file (10 MB).
LOG_MAX_BYTES: int = 10 * 1024 * 1024

# How many backup log files to keep.
LOG_BACKUP_COUNT: int = 5

# ---------------------------------------------------------------------------
# ALERT SYSTEM
# ---------------------------------------------------------------------------
# Print colour-coded alerts to the console?
CONSOLE_ALERTS_ENABLED: bool = True

# Which event types trigger an alert?  Options: "created", "modified", "deleted"
ALERT_ON_EVENTS: set[str] = {"created", "deleted"}

# --- Email alerts (optional) ------------------------------------------------
EMAIL_ALERTS_ENABLED: bool = False          # Set True to enable
EMAIL_SMTP_HOST: str    = "smtp.gmail.com"
EMAIL_SMTP_PORT: int    = 587
EMAIL_SENDER: str       = "your_email@gmail.com"
EMAIL_PASSWORD: str     = "your_app_password"   # Use an App Password, not your real password
EMAIL_RECIPIENTS: list[str] = ["recipient@example.com"]
EMAIL_SUBJECT_PREFIX: str   = "[FS-Monitor]"
