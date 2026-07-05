import os

BASE_API_URL = "http://127.0.0.1:8000"

CLIENT_VERSION = "1.0.0"

SESSION_DAYS = 30

HEARTBEAT_INTERVAL = 5

WATCH_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "watched_folder"
)