from client.api_client import APIClient
from client.auth_manager import AuthManager
from client.device_manager import DeviceManager


class DashboardService:

    def __init__(self):
        self.api = APIClient()
        self.auth = AuthManager()
        self.device = DeviceManager()

    def heartbeat(
        self,
        protection,
        realtime,
        threats_blocked,
        files_scanned,
        threat_level,
    ):

        print("Heartbeat Called")

        token = self.auth.load_token()

        print("Token:", token)

        if not token:
            print("No Token")
            return

        device_id = self.device.get_device_id()

        print("Device ID:", device_id)

        if not device_id:
            print("No Device ID")
            return

        try:
            print("TOKEN END:", token[-15:])
            response = self.api.heartbeat(
             token,
             device_id,
             protection,
             realtime,
             threats_blocked,
             files_scanned,
             threat_level,
            )

            print("Heartbeat:", response.status_code)
            print(response.text)

        except Exception as e:

            print("Heartbeat Error:", e)