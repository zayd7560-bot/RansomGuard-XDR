import os
import json
import uuid
import platform
from client.client_config import CLIENT_VERSION


DEVICE_FILE = os.path.join(
    os.path.dirname(__file__),
    "device.json"
)


class DeviceManager:

    def __init__(self):

        if not os.path.exists(DEVICE_FILE):

            self.create_device()

    def create_device(self):

        data = {
            "device_uuid": str(uuid.uuid4()),
            "device_name": platform.node(),
            "os": platform.platform(),
            "version": CLIENT_VERSION
        }

        with open(
            DEVICE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

    def load(self):

        with open(
            DEVICE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)
    def save_device_id(self, device_id):

        data = self.load()

        data["device_id"] = device_id

        with open(
            DEVICE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

    def get_device_id(self):

        data = self.load()

        return data.get("device_id")