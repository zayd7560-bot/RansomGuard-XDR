import json
import os
from datetime import datetime, timedelta


SESSION_FILE = "session.json"

# مدة Remember Me
from client.client_config import SESSION_DAYS


class AuthManager:

    def save_token(self, token):

        data = {
            "token": token,
            "saved_at": datetime.now().isoformat()
        }

        with open(
            SESSION_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

    def load_token(self):

        if not os.path.exists(SESSION_FILE):
            return None

        try:

            with open(
                SESSION_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            token = data.get("token")
            saved_at = data.get("saved_at")

            if not token or not saved_at:
                self.logout()
                return None

            saved_time = datetime.fromisoformat(saved_at)

            if datetime.now() - saved_time > timedelta(days=SESSION_DAYS):
                self.logout()
                return None

            return token

        except Exception:
            self.logout()
            return None

    def logout(self):

        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)