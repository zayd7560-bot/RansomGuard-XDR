import os

BASE_API_URL = "https://ransomguard-xdr-production.up.railway.app"

CLIENT_VERSION = "1.0.0"

SESSION_DAYS = 30

HEARTBEAT_INTERVAL = 5

WATCH_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "watched_folder"
)