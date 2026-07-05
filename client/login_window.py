import os
import threading
import customtkinter as ctk
from PIL import Image

from client.api_client import APIClient
from client.auth_manager import AuthManager
from client import gui
import webbrowser
from client.device_manager import DeviceManager


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginWindow:

    def __init__(self):

        self.api = APIClient()
        self.auth = AuthManager()
        self.device = DeviceManager()

        self.root = ctk.CTk()

        self.root.title("RansomGuard XDR")

        self.root.geometry("1200x700")

        self.root.resizable(False, False)

        self.root.grid_columnconfigure((0, 1), weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        assets = os.path.join(
            os.path.dirname(__file__),
            "assets"
        )

        self.logo = ctk.CTkImage(
            Image.open(os.path.join(assets, "logo.png")),
            size=(120,120)
        )

        self.background = ctk.CTkImage(
            Image.open(os.path.join(assets, "login_background.png")),
            size=(600, 700)
        )

        self.eye = ctk.CTkImage(
            Image.open(os.path.join(assets, "eye.png")),
            size=(22, 22)
        )

        self.eye_hide = ctk.CTkImage(
            Image.open(os.path.join(assets, "eye_hide.png")),
            size=(22, 22)
        )

        token = self.auth.load_token()

        if token:

            self.root.destroy()

            gui.main()

            return

        self.build_ui()


    def build_ui(self):

        left = ctk.CTkFrame(
            self.root,
            corner_radius=0
        )

        left.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        right = ctk.CTkFrame(
            self.root,
            corner_radius=0
        )

        right.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        bg = ctk.CTkLabel(
            left,
            text="",
            image=self.background
        )

        bg.place(
            relwidth=1,
            relheight=1
        )

        logo = ctk.CTkLabel(
            left,
            text="",
            image=self.logo
        )

        logo.pack(
            pady=(60, 15)
        )

        ctk.CTkLabel(

            left,

            text="RansomGuard XDR",

            font=("Segoe UI",40,"bold")

        ).pack()

        ctk.CTkLabel(

            left,

            text="AI Powered Endpoint Protection",

            font=("Segoe UI", 18)

        ).pack(pady=(10, 40))

        features = [

            "✔ Real-Time Protection",

            "✔ AI Threat Detection",

            "✔ Behavior Monitoring",

            "✔ Cloud Security"

        ]

        for item in features:

            ctk.CTkLabel(

                left,

                text=item,

                font=("Segoe UI", 18),

                anchor="w"

            ).pack(
                pady=8
            )

        ctk.CTkLabel(

            right,

            text="Welcome Back",

            font=("Segoe UI", 34, "bold")

        ).pack(
            pady=(70, 10)
        )

        ctk.CTkLabel(

            right,

            text="Sign in to continue",

            font=("Segoe UI", 18)

        ).pack(
            pady=(0, 40)
        )

        self.username = ctk.CTkEntry(

            right,

            width=420,

            height=48,

            placeholder_text="Username"

        )

        self.username.pack(
            pady=10
        )

        password_frame = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        password_frame.pack(pady=10)

        self.password = ctk.CTkEntry(
            password_frame,
            width=370,
            height=48,
            placeholder_text="Password",
            show="*"
        )

        self.password.pack(side="left")

        self.show_password = False

        self.eye_button = ctk.CTkButton(
            password_frame,
            text="",
            image=self.eye,
            width=34,
            height=34,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#1F6AA5",
            command=self.toggle_password
        )

        self.eye_button.pack(
            side="left",
            padx=(0, 0)
        )


        self.remember = ctk.BooleanVar(value=True)

        self.remember_check = ctk.CTkCheckBox(

            right,

            text="Remember Me",

            variable=self.remember

        )

        self.remember_check.pack(pady=(0, 25))


        self.login_button = ctk.CTkButton(

    right,

    text="LOGIN",

    width=420,

    height=55,

    font=("Segoe UI", 20, "bold"),

    fg_color="#0078D7",

    hover_color="#0063C9",

    border_width=2,

    border_color="#F9F9F9",

    corner_radius=12,

    command=self.login

)
        self.login_button.pack(pady=10)


        self.status = ctk.CTkLabel(

            right,

            text="",

            font=("Segoe UI", 14)

        )

        self.status.pack(pady=(10, 15))


        self.create_account = ctk.CTkLabel(

         right,

         text="Create Account",

         text_color="#4EA1FF",

         cursor="hand2",

         font=("Segoe UI",16,"underline")

         )

        self.create_account.pack(pady=(20,5))

        self.create_account.bind(

         "<Button-1>",

          lambda e: webbrowser.open("http://localhost:5173/register")

        )



        ctk.CTkLabel(

            right,

            text="© 2026 RansomGuard XDR",

            font=("Segoe UI", 12)

        ).pack(side="bottom", pady=20)
    def toggle_password(self):

         self.show_password = not self.show_password

         if self.show_password:

            self.password.configure(show="")

            self.eye_button.configure(image=self.eye_hide)

         else:

            self.password.configure(show="*")

            self.eye_button.configure(image=self.eye)
    def login(self):

        username = self.username.get().strip()
        password = self.password.get().strip()

        if not username or not password:

            self.status.configure(
                text="Please enter username and password.",
                text_color="red"
            )

            return

        self.login_button.configure(
            state="disabled",
            text="⏳ Authenticating..."
        )

        self.status.configure(
            text="Connecting to server...",
            text_color="#00BFFF"
        )
        threading.Thread(
            target=self._login_thread,
            daemon=True
        ).start()


    def _login_thread(self):

        try:

            response = self.api.login(

                self.username.get(),

                self.password.get()

            )

            self.root.after(

                0,

                lambda: self._handle_login(response)

            )

        except Exception as e:

            self.root.after(

                0,

                lambda: self._login_error(str(e))

            )


    def _handle_login(self, response):

        self.login_button.configure(

            state="normal",

            text="LOGIN"

        )

        if response.status_code != 200:

            try:
                msg = response.json()["detail"]
            except:
                msg = "Login Failed"

            self.status.configure(

                text=msg,

                text_color="red"

            )

            return  
        data = response.json()

        token = data["access_token"]

        device = self.device.load()

        try:
            response = self.api.register_device(
                token,
                device["device_uuid"],
                device["device_name"],
                device["os"],
                device["version"],
            )
            device_data = response.json()

            device_id = device_data["device_id"]

            self.device.save_device_id(device_id)
            print("Device Register:", response.status_code)
            print(response.text)

        except Exception as e:
            print("Register Error:", e)

        # احفظ الـ Session دائمًا
        self.auth.save_token(token)

        self.status.configure(
            text="✅ Access Granted",
            text_color="lime"
        )

        self.root.after(
            700,
            self.open_dashboard
        )


    def _login_error(self, error):

        self.login_button.configure(

            state="normal",

            text="LOGIN"

        )

        self.status.configure(

            text="Cannot connect to server",

            text_color="red"

        )


    def open_dashboard(self):

        self.root.withdraw()

        gui.main()

        self.root.destroy()

    def run(self):

        self.root.mainloop()


def main():

    app = LoginWindow()

    app.run()


if __name__ == "__main__":

    main()