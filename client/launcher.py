import os
import sys
import time
import socket
import subprocess

from client.login_window import main


def backend_running():

    sock = socket.socket()

    sock.settimeout(1)

    try:

        sock.connect(("127.0.0.1", 8000))

        sock.close()

        return True

    except:

        return False


def start_backend():

    if backend_running():

        print("Backend Already Running")

        return

    root = os.path.dirname(
        os.path.dirname(__file__)
    )

    backend_path = os.path.join(
        root,
        "backend"
    )

    subprocess.Popen(

        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000"

        ],

        cwd=backend_path,

        stdout=subprocess.DEVNULL,

        stderr=subprocess.DEVNULL

    )

    print("Starting Backend...")

    for _ in range(10):

        if backend_running():

            print("Backend Started")

            return

        time.sleep(1)

    raise RuntimeError("Backend Failed To Start")


if __name__ == "__main__":

    start_backend()

    main()