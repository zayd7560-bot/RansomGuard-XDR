import requests

from client.client_config import BASE_API_URL
BASE_URL = BASE_API_URL


class APIClient:

    def login(self, username, password):
        return requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

    def register(self, username, email, password, duress_password):
        return requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "duress_password": duress_password,
            },
        )

    def register_device(
        self,
        token,
        device_uuid,
        device_name,
        os_name,
        version,
    ):
        return requests.post(
            f"{BASE_URL}/device/register",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "device_uuid": device_uuid,
                "device_name": device_name,
                "os": os_name,
                "version": version,
            },
        )

    def update_dashboard(
        self,
        token,
        protection,
        realtime,
        threats_blocked,
        files_scanned,
        client_version,
        recent_activity,
    ):
        return requests.post(
            f"{BASE_URL}/dashboard/update",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "protection": protection,
                "realtime": realtime,
                "threats_blocked": threats_blocked,
                "files_scanned": files_scanned,
                "client_version": client_version,
                "recent_activity": recent_activity,
            },
        )
    def heartbeat(
       self,
       token,
       device_id,
       protection,
       realtime,
       threats_blocked,
       files_scanned,
       threat_level,
     ):
        print("URL =", f"{BASE_URL}/device/heartbeat")
        return requests.post(
            f"{BASE_URL}/device/heartbeat",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "device_id": device_id,
                "protection": protection,
                "realtime": realtime,
                "threats_blocked": threats_blocked,
                "files_scanned": files_scanned,
                "threat_level": threat_level,
            },
        )