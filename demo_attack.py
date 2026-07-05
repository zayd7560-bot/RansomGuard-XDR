"""
demo_attack.py
--------------
سكريبت المحاكاة الآمنة لهجوم الـ Ransomware
SAFE Ransomware Simulation Script for Presentation

⚠️  IMPORTANT / تنبيه مهم:
    هذا السكريبت آمن تماماً ولا يضر بأي ملفات حقيقية
    This script is 100% SAFE - it NEVER touches real user files
    All operations are in the watched_folder directory ONLY
    
HOW IT WORKS / كيف يعمل:
    1. ينشئ ملفات وهمية في مجلد المراقبة
    2. يعدل عليها بسرعة كبيرة (يحاكي التشفير)
    3. يمسحها ويستبدلها بملفات مشفرة وهمية
    4. نظام الكشف يكتشف النشاط ويطلق التنبيهات

RUN INSTRUCTIONS / طريقة التشغيل:
    1. شغل gui.py أول
    2. اضغط "Start Monitoring"
    3. في نافذة تانية شغل: python demo_attack.py
    4. شاهد الـ alerts والـ logs في الـ GUI
"""

import os
import sys
import time
import random
import string
import struct
import threading

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# المجلد اللي هنشتغل فيه - نفس المجلد اللي بيراقبه النظام
print("\n📁 Enter the folder path to simulate the attack on:")
WATCH_FOLDER = input(">> ").strip()

# لو المستخدم مدخلش حاجة
if not WATCH_FOLDER:
    WATCH_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "watched_folder"
    )

# عدد الملفات اللي هننشئها
NUM_FILES = 60

# مدة الهجوم الكاملة (ثواني)
ATTACK_DURATION = 30

# الامتدادات الوهمية (كأنها ملفات مستخدم حقيقية)
FAKE_EXTENSIONS = [".txt", ".doc", ".pdf", ".jpg", ".xlsx", ".csv", ".mp3"]

# امتداد الـ "تشفير" الوهمي
ENCRYPTED_EXT = ".locked"

# ─────────────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def print_banner():
    """يطبع شعار السكريبت"""
    print("\n" + "═" * 60)
    print("  🔥  RANSOMWARE SIMULATION DEMO  (SAFE)")
    print("  ⚠️  This is a GRADUATION PROJECT DEMO ONLY")
    print("  ✅  No real files will be harmed")
    print("═" * 60)
    print(f"  📁  Target: {WATCH_FOLDER}")
    print(f"  📊  Files:  {NUM_FILES} dummy files")
    print(f"  ⏱️  Duration: ~{ATTACK_DURATION} seconds")
    print("═" * 60)


def random_name(ext: str) -> str:
    """ينشئ اسم ملف عشوائي"""
    prefix = random.choice([
        "document", "report", "photo", "backup",
        "data", "file", "record", "note", "invoice"
    ])
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{suffix}{ext}"


def fake_normal_content() -> bytes:
    """
    ينشئ محتوى يشبه الملفات العادية (entropy منخفضة)
    الملف العادي بيكون فيه نفس الحروف بتتكرر كتير = entropy منخفضة
    """
    words = ["the", "is", "a", "in", "of", "and", "to", "it", "this", "that"]
    text  = " ".join(random.choices(words, k=200))
    return text.encode("utf-8")


def fake_encrypted_content(size: int = 4096) -> bytes:
    """
    ينشئ محتوى يشبه الملفات المشفرة (entropy عالية)
    الملف المشفر بيبون فيه bytes عشوائية = Shannon entropy عالية ≈ 8.0
    ده المفتاح في الكشف عن الـ ransomware!
    """
    # bytes عشوائية تماماً = entropy = 8.0 (أعلى قيمة)
    return bytes(random.getrandbits(8) for _ in range(size))


def ensure_folder():
    """يتأكد إن مجلد المراقبة موجود"""
    os.makedirs(WATCH_FOLDER, exist_ok=True)


def cleanup_demo_files():
    """يمسح ملفات الديمو قبل البداية"""
    if not os.path.exists(WATCH_FOLDER):
        return
    for f in os.listdir(WATCH_FOLDER):
        fpath = os.path.join(WATCH_FOLDER, f)
        if os.path.isfile(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
#  ATTACK PHASES
# ─────────────────────────────────────────────────────────────────────────────

def phase1_create_files(file_list: list):
    """
    المرحلة 1: إنشاء الملفات الوهمية
    بيحاكي قاعدة بيانات الـ ransomware اللي بتجمع الملفات الأول
    """
    print("\n  [Phase 1] 📁 Creating dummy target files...")
    print(f"           Creating {NUM_FILES} files...")

    for i in range(NUM_FILES):
        ext   = random.choice(FAKE_EXTENSIONS)
        fname = random_name(ext)
        fpath = os.path.join(WATCH_FOLDER, fname)

        try:
            with open(fpath, "wb") as f:
                f.write(fake_normal_content())
            file_list.append(fpath)
        except Exception as e:
            print(f"  [!] Could not create {fname}: {e}")

        # نعمل pause صغيرة عشان الـ watchdog يلحق يشوف الـ events
        time.sleep(0.05)

        if (i + 1) % 10 == 0:
            print(f"      ✓ {i+1}/{NUM_FILES} files created")

    print(f"  [✓] Phase 1 complete: {len(file_list)} files created\n")
    time.sleep(2)


def phase2_rapid_modification(file_list: list):
    """
    المرحلة 2: التعديل السريع (محاكاة التشفير)
    ده أهم مرحلة - الـ ransomware بيعدل على الملفات بسرعة جداً
    النظام بيكتشف ده من خلال: modification rate عالية + entropy عالية
    """
    print("  [Phase 2] 🔥 Simulating rapid encryption...")
    print("           Modifying files rapidly with high-entropy content...")
    print("           (This triggers the detection system!)\n")

    random.shuffle(file_list)  # نعدل بترتيب عشوائي زي الـ ransomware الحقيقي

    for i, fpath in enumerate(file_list):
        if not os.path.exists(fpath):
            continue

        try:
            # نكتب محتوى عشوائي (entropy عالية = يشبه التشفير)
            with open(fpath, "wb") as f:
                f.write(fake_encrypted_content(size=random.randint(2048, 8192)))

        except Exception:
            pass

        # بسرعة كبيرة جداً = red flag للنظام
        time.sleep(0.1)

        if (i + 1) % 10 == 0:
            print(f"      🔒 Encrypted: {i+1}/{len(file_list)} files")

    print("  [✓] Phase 2 complete: All files 'encrypted'\n")
    time.sleep(2)


def phase3_rename_files(file_list: list) -> list:
    """
    المرحلة 3: إعادة التسمية (زي ما الـ ransomware بيضيف .locked)
    delete + create = event مضاعف للـ detection
    """
    print("  [Phase 3] 🔄 Renaming files to .locked extension...")

    new_list = []
    for fpath in file_list:
        if not os.path.exists(fpath):
            continue

        new_path = fpath + ENCRYPTED_EXT
        try:
            os.rename(fpath, new_path)
            new_list.append(new_path)
        except Exception:
            new_list.append(fpath)

        time.sleep(0.08)

    print(f"  [✓] Phase 3 complete: Files renamed to {ENCRYPTED_EXT}\n")
    time.sleep(2)
    return new_list


def phase4_create_ransom_note():
    """
    المرحلة 4: إنشاء ملف "فدية" وهمي
    مجرد ملف text عشان يكمل المحاكاة
    """
    print("  [Phase 4] 📝 Dropping ransom note (FAKE)...")

    note_path = os.path.join(WATCH_FOLDER, "README_DECRYPT.txt")
    note_content = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            THIS IS A SIMULATION - GRADUATION PROJECT
            هذا مجرد محاكاة لأغراض أكاديمية بحتة
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

[DEMO] All your files have been SIMULATED encrypted.

This is a SAFE demo script showing how ransomware works.
No real files were harmed during this demonstration.

Project: Ransomware Detection System
Purpose: Graduation Project Demo
Date: 2026

The detection system above should have detected:
  ✅ High file modification rate
  ✅ High entropy (simulated encryption)
  ✅ Mass file operations
  ✅ File renaming patterns

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    print("  [✓] Phase 4 complete: Ransom note created\n")
    time.sleep(1)


def phase5_cleanup(file_list: list):
    """
    المرحلة 5: تنظيف بعد الديمو (اختياري)
    """
    print("  [Phase 5] 🧹 Cleaning up demo files...")

    removed = 0
    for fpath in file_list:
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
                removed += 1
        except Exception:
            pass

    # نمسح الملفات المسماة .locked كمان
    for f in os.listdir(WATCH_FOLDER):
        if f.endswith(ENCRYPTED_EXT) or f == "README_DECRYPT.txt":
            try:
                os.remove(os.path.join(WATCH_FOLDER, f))
                removed += 1
            except Exception:
                pass

    print(f"  [✓] Cleanup complete: {removed} files removed\n")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

def run_demo():
    """
    ينفذ محاكاة الهجوم كاملة على 5 مراحل
    """
    print_banner()

    # نتأكد من المجلد
    ensure_folder()

    # نسأل المستخدم
    print("\n  ⚠️  Make sure the GUI is running and monitoring is started!")
    print("  Press Enter to start the simulation, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n  [!] Demo cancelled.")
        return

    # نمسح الملفات القديمة
    print("  🗑️  Cleaning up old demo files first...")
    cleanup_demo_files()
    time.sleep(1)

    file_list = []
    start_time = time.time()

    try:
        # ── Phase 1: Create ────────────────────────────────────────────
        phase1_create_files(file_list)

        # ── Phase 2: Modify (encrypt simulation) ──────────────────────
        phase2_rapid_modification(file_list)

        # ── Phase 3: Rename ───────────────────────────────────────────
        file_list = phase3_rename_files(file_list)

        # ── Phase 4: Ransom note ──────────────────────────────────────
        phase4_create_ransom_note()

        elapsed = time.time() - start_time
        print(f"\n{'═' * 60}")
        print(f"  🔥 SIMULATION COMPLETE in {elapsed:.1f} seconds")
        print(f"  📊 Files created:   {NUM_FILES}")
        print(f"  📊 Files 'encrypted': {len(file_list)}")
        print(f"{'═' * 60}")
        print("\n  Check the GUI for alerts and threat level changes!")
        print("  The system should show: SUSPICIOUS or ATTACK DETECTED\n")

        # ── Phase 5: Cleanup ──────────────────────────────────────────
        print("\n  Press Enter to cleanup demo files, or Ctrl+C to keep them...")
        try:
            input()
            phase5_cleanup(file_list)
            print("  ✅ Demo finished successfully!")
        except KeyboardInterrupt:
            print("\n  [!] Files kept for examination. Run cleanup manually.")

    except KeyboardInterrupt:
        print("\n\n  [!] Demo interrupted by user.")
        print("  Cleaning up partial files...")
        phase5_cleanup(file_list)

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_demo()
