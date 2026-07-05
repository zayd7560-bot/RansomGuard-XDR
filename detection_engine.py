import psutil
from datetime import datetime

MODIFIED_FILES_THRESHOLD = 50
ENTROPY_THRESHOLD = 7.0

ENABLE_PROCESS_KILL = False


def show_alert(level, message):

    print("\n" + "=" * 50)
    print(f"[{level}] {message}")
    print(f"Time: {datetime.now()}")
    print("=" * 50 + "\n")


def classify_threat(modified_files, entropy):

    if (
        modified_files >= MODIFIED_FILES_THRESHOLD
        and entropy >= ENTROPY_THRESHOLD
    ):
        return "DANGEROUS"

    elif modified_files >= 20 and entropy >= 6:
        return "SUSPICIOUS"

    else:
        return "NORMAL"


def detect_ransomware(analysis_data):

    modified_files = analysis_data["modified_files"]
    entropy = analysis_data["entropy"]

    threat_level = classify_threat(
        modified_files,
        entropy
    )

    print("------ ANALYSIS RESULT ------")
    print(f"Modified Files : {modified_files}")
    print(f"Entropy        : {entropy}")
    print(f"Threat Level   : {threat_level}")
    print("-----------------------------")

    if threat_level == "DANGEROUS":

        show_alert(
            "ALERT",
            "Possible ransomware attack detected!"
        )

        if ENABLE_PROCESS_KILL:
            kill_suspicious_processes()

    elif threat_level == "SUSPICIOUS":

        show_alert(
            "WARNING",
            "Suspicious file activity detected!"
        )

    else:

        print("[INFO] System behavior is normal.\n")


def list_running_processes():

    print("\nRunning Processes:\n")

    for process in psutil.process_iter(['pid', 'name']):

        try:
            print(process.info)

        except:
            pass


def kill_suspicious_processes():

    suspicious_names = [
        "test_ransomware.exe",
        "fake_encryptor.exe",
        "malware.exe"
    ]

    print("\n[PROCESS RESPONSE] Checking processes...\n")

    for process in psutil.process_iter(['pid', 'name']):

        try:

            process_name = process.info['name']

            if process_name in suspicious_names:

                process.kill()

                print(
                    f"[KILLED] {process_name} "
                    f"(PID: {process.info['pid']})"
                )

        except:
            pass


if __name__ == "__main__":

    analysis_data = {

        "modified_files": 70,
        "entropy": 7.8
    }

    detect_ransomware(analysis_data)

    list_running_processes()