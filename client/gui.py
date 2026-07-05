
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import os
import sys
import json
from datetime import datetime
import requests
import webbrowser
from client.dashboard_service import DashboardService

# نضيف مسار البروجيكت للـ path عشان يعرف يستورد الـ modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from watchdog.observers import Observer
import config
from monitor import FileEventLogger, AlertSystem, FileEventHandler
from detection_engine import classify_threat

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS - الألوان والإعدادات البصرية
# ─────────────────────────────────────────────────────────────────────────────

# لوحة الألوان - Dark Theme احترافي
COLORS = {
    "bg_dark":        "#0D1117",   # خلفية الشاشة الرئيسية
    "bg_panel":       "#161B22",   # خلفية الـ panels
    "bg_card":        "#1C2128",   # خلفية الـ cards
    "bg_input":       "#21262D",   # خلفية حقول الإدخال
    "border":         "#30363D",   # لون الإطار
    "accent_blue":    "#58A6FF",   # أزرق للعناوين
    "accent_green":   "#3FB950",   # أخضر للحالة الآمنة
    "accent_yellow":  "#D29922",   # أصفر للتحذير
    "accent_red":     "#F85149",   # أحمر للخطر
    "accent_orange":  "#E3B341",   # برتقالي للـ suspicious
    "accent_purple":  "#BC8CFF",   # بنفسجي للإحصائيات
    "text_primary":   "#E6EDF3",   # النص الرئيسي
    "text_secondary": "#8B949E",   # النص الثانوي
    "text_muted":     "#484F58",   # النص الخافت
    "btn_start":      "#238636",   # زر البدء
    "btn_start_h":    "#2EA043",   # زر البدء hover
    "btn_stop":       "#B62324",   # زر الإيقاف
    "btn_stop_h":     "#D1242F",   # زر الإيقاف hover
    "btn_clear":      "#1F4068",   # زر المسح
    "btn_exit":       "#2D1B69",   # زر الخروج
}

API_URL = "http://127.0.0.1:8000"
JWT_TOKEN = None

# الخطوط
FONTS = {
    "title":     ("Segoe UI", 22, "bold"),
    "subtitle":  ("Segoe UI", 11),
    "header":    ("Segoe UI", 12, "bold"),
    "body":      ("Segoe UI", 10),
    "mono":      ("Consolas", 9),
    "status":    ("Segoe UI", 13, "bold"),
    "counter":   ("Segoe UI", 24, "bold"),
    "label_sm":  ("Segoe UI", 9),
}

# ─────────────────────────────────────────────────────────────────────────────
#  MONITORING BACKEND BRIDGE
#  الجسر بين الـ GUI والـ Backend
# ─────────────────────────────────────────────────────────────────────────────

class GUIAlertSystem(AlertSystem):
    """
    نسخة معدلة من AlertSystem تبعت الـ alerts للـ GUI queue
    بدل ما تطبعها في الـ console بس

    FIX: dispatch() كانت بتفلتر الـ events قبل ما تبعتها للـ GUI،
         دلوقتي بنبعت كل event بغض النظر عن الـ _triggers
    """

    def __init__(self, gui_queue: queue.Queue, *args, **kwargs):
        # نعطل الـ console alerts عشان الـ GUI هيتولى الأمر
        kwargs["console_enabled"] = False
        super().__init__(*args, **kwargs)
        self._gui_queue = gui_queue

    def dispatch(self, record: dict) -> None:
        """
        FIX: بنبعت كل event للـ GUI Queue بغض النظر عن الـ _triggers
        (الـ base class كانت بتفلتر وتبعت بس اللي في _triggers)
        """
        # كل event بيروح للـ logs
        self._gui_queue.put({"type": "event", "record": record})

        # لو الـ event من النوع اللي بيطلع alert — نبعت alert تاني
        event_type = record.get("event_type", "")
        if event_type in self._triggers:
            self._gui_queue.put({"type": "alert", "record": record})


class MonitoringThread:
    """
    بيشغل نظام المراقبة في background thread
    ومش بيأثر على الـ GUI أبداً
    """

    def __init__(self, gui_queue: queue.Queue, watch_directory=None):
        self._queue    = gui_queue
        self._observer = None
        self._handler  = None
        self._logger   = None
        self._thread   = None
        self._running  = False
        self.watch_directory = watch_directory or config.WATCH_DIRECTORY

    def start(self):
        """يبدأ المراقبة في thread منفصل"""
        if self._running:
            return

        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """يوقف المراقبة بشكل آمن"""
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=3)
        if self._logger:
            self._logger.close()

    def get_event_store(self):
        """بيرجع قائمة الـ events المسجلة"""
        if self._handler:
            return self._handler.event_store
        return []

    def _run(self):
        """الـ main loop للـ monitoring thread"""
        try:
            watch_dir = self.watch_directory
            os.makedirs(watch_dir, exist_ok=True)

            # FIX: نحاول ننشئ الـ logs folder، ولو Permission Denied نرجع للـ temp folder
            logs_dir = config.LOGS_DIRECTORY
            try:
                os.makedirs(logs_dir, exist_ok=True)
                # نتحقق إننا نقدر نكتب فيه فعلاً
                test_file = os.path.join(logs_dir, ".write_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except PermissionError:
                # fallback: مجلد temp الخاص بالمستخدم — دايمًا متاح
                import tempfile
                logs_dir = os.path.join(tempfile.gettempdir(), "ransomware_detector", "logs")
                os.makedirs(logs_dir, exist_ok=True)
                self._queue.put({
                    "type": "status",
                    "message": f"⚠️ Permission denied على logs الأصلي، بنكتب في: {logs_dir}"
                })

            self._logger = FileEventLogger(
                logs_dir=logs_dir,
                prefix=config.LOG_FILE_PREFIX,
                max_bytes=config.LOG_MAX_BYTES,
                backup_count=config.LOG_BACKUP_COUNT,
            )

            # الـ AlertSystem المخصص للـ GUI
            alert_system = GUIAlertSystem(
                gui_queue=self._queue,
                alert_on_events={"created", "modified", "deleted"},
                email_enabled=False,
            )

            # FIX: كنا بنعدي logger=None بسبب: alert_system._ecfg and None or self._logger
            # _ecfg هو {} (dict فاضي) وده falsy، فكان التعبير دايمًا يرجع None
            # الحل: نعدي self._logger مباشرة
            self._handler = FileEventHandler(
                logger=self._logger,          # ← FIX: مباشرة بدون الـ expression الغلط
                alert_system=alert_system,
                allowed_extensions=set(),
            )

            self._observer = Observer()
            self._observer.schedule(self._handler, watch_dir, recursive=config.RECURSIVE)
            self._observer.start()

            # نبعت رسالة إن المراقبة بدأت
            self._queue.put({
                "type": "status",
                "message": f"✅ المراقبة بدأت على: {watch_dir}",
                "log_path": self._logger.log_path
            })

            # الـ loop الرئيسي - بيتحقق كل 5 ثواني ويحلل
            while self._running and self._observer.is_alive():
                time.sleep(5)

                if not self._running:
                    break

                # نحسب التحليل وابعته للـ GUI
                events      = self._handler.event_store
                modified    = sum(1 for e in events if e["event_type"] == "modified")
                created     = sum(1 for e in events if e["event_type"] == "created")
                deleted     = sum(1 for e in events if e["event_type"] == "deleted")
                entropy_est = min(8.0, modified / 10)

                threat = classify_threat(modified, entropy_est)

                self._queue.put({
                    "type":     "analysis",
                    "threat":   threat,
                    "modified": modified,
                    "created":  created,
                    "deleted":  deleted,
                    "entropy":  round(entropy_est, 2),
                    "total":    len(events),
                })

        except Exception as exc:
            self._queue.put({"type": "error", "message": str(exc)})
        finally:
            self._running = False
            self._queue.put({"type": "stopped"})


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER WIDGETS
# ─────────────────────────────────────────────────────────────────────────────

def make_frame(parent, bg=None, **kwargs):
    """Helper لعمل Frame بالألوان الصح"""
    return tk.Frame(parent, bg=bg or COLORS["bg_panel"], **kwargs)

def make_label(parent, text, font=None, fg=None, bg=None, **kwargs):
    """Helper لعمل Label بالستايل الصح"""
    return tk.Label(
        parent,
        text=text,
        font=font or FONTS["body"],
        fg=fg or COLORS["text_primary"],
        bg=bg or COLORS["bg_panel"],
        **kwargs
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN GUI CLASS
# ─────────────────────────────────────────────────────────────────────────────

class RansomwareDetectorGUI:
    """
    الكلاس الرئيسي للـ GUI
    بيتحكم في كل الشاشة والـ widgets والربط مع الـ backend
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()

        # الـ Queue اللي بتربط الـ backend بالـ GUI بشكل thread-safe
        self._queue = queue.Queue()

        # الـ monitoring thread
        self._monitor = MonitoringThread(self._queue)
        self.dashboard = DashboardService()

        # متغيرات الحالة
        self._is_monitoring = False
        self._alert_count   = 0
        self._log_count     = 0
        self._threat_level = "NORMAL"
        threading.Thread(
           target=self._heartbeat_loop,
           daemon=True,
         ).start()

        # Dynamic selected folder
        self.selected_folder = config.WATCH_DIRECTORY

        # بناء الـ UI
        self._build_ui()

        # تشغيل الـ update loop (بيتكرر كل 300ms)
        self._poll_queue()

    # ──────────────────────────────────────────────────────────────────────
    #  WINDOW SETUP
    # ──────────────────────────────────────────────────────────────────────

    def _setup_window(self):
        """إعدادات الشاشة الرئيسية"""
        self.root.title("🛡️  Ransomware Detection System  |  نظام كشف الفدية")
        self.root.geometry("1280x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=COLORS["bg_dark"])

        # نحاول نحط أيقونة (لو فشلت مش مشكلة)
        try:
            self.root.iconbitmap("shield.ico")
        except Exception:
            pass

        # لما يضغط X، نسأله
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Grid config للـ responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    # ──────────────────────────────────────────────────────────────────────
    #  UI BUILDER - بناء الواجهة كاملاً
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """ينشئ كل عناصر الواجهة"""
        self._build_header()
        self._build_main_content()
        self._build_footer()

    # ─── HEADER ───────────────────────────────────────────────────────────

    def _build_header(self):
        """
        الهيدر العلوي:
        - عنوان البروجيكت
        - مؤشر الحالة الكبير
        - أزرار التحكم
        """
        header = make_frame(self.root, bg=COLORS["bg_panel"], pady=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.columnconfigure(1, weight=1)

        # ── شريط ملون أعلى الهيدر ──────────────────────────────────────
        top_strip = tk.Frame(header, bg=COLORS["accent_blue"], height=3)
        top_strip.grid(row=0, column=0, columnspan=3, sticky="ew")

        # ── الـ Logo / Title section ────────────────────────────────────
        title_frame = make_frame(header, bg=COLORS["bg_panel"])
        title_frame.grid(row=1, column=0, padx=20, pady=12, sticky="w")

        tk.Label(
            title_frame,
            text="🛡️",
            font=("Segoe UI", 28),
            bg=COLORS["bg_panel"],
            fg=COLORS["accent_blue"]
        ).pack(side="left", padx=(0, 10))

        title_text = make_frame(title_frame, bg=COLORS["bg_panel"])
        title_text.pack(side="left")

        tk.Label(
            title_text,
            text="Ransomware Detection System",
            font=FONTS["title"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_primary"]
        ).pack(anchor="w")

        tk.Label(
            title_text,
            text="نظام كشف وتحليل برمجيات الفدية  •  Graduation Project 2026",
            font=FONTS["subtitle"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_secondary"]
        ).pack(anchor="w")

        # ── مؤشر الحالة الكبير في المنتصف ──────────────────────────────
        status_frame = make_frame(header, bg=COLORS["bg_panel"])
        status_frame.grid(row=1, column=1, pady=12)

        tk.Label(
            status_frame,
            text="SYSTEM STATUS",
            font=FONTS["label_sm"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_muted"]
        ).pack()

        self._status_dot = tk.Label(
            status_frame,
            text="●",
            font=("Segoe UI", 18),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_muted"]
        )
        self._status_dot.pack(side="left", padx=5)

        self._status_label = tk.Label(
            status_frame,
            text="IDLE",
            font=FONTS["status"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_muted"]
        )
        self._status_label.pack(side="left")

        
        # ── Folder Selection ─────────────────────────────────────────
        folder_frame = make_frame(header, bg=COLORS["bg_panel"])
        folder_frame.grid(row=1, column=1, pady=12)

        self._folder_label = tk.Label(
            folder_frame,
            text=f"📂 {os.path.basename(self.selected_folder)}",
            font=FONTS["body"],
            bg=COLORS["bg_panel"],
            fg=COLORS["accent_blue"],
            wraplength=400,
        )
        self._folder_label.pack(side="left", padx=10)

        select_btn = tk.Button(
            folder_frame,
            text="Browse Folder",
            font=FONTS["body"],
            bg=COLORS["btn_clear"],
            fg=COLORS["text_primary"],
            relief="flat",
            cursor="hand2",
            command=self._select_folder
        )
        select_btn.pack(side="left", padx=10)


        # ── أزرار التحكم ────────────────────────────────────────────────
        btn_frame = make_frame(header, bg=COLORS["bg_panel"])
        btn_frame.grid(row=1, column=2, padx=20, pady=12, sticky="e")

        # زر Start
        self._btn_start = self._make_button(
            btn_frame,
            text="▶  Start Monitoring",
            bg=COLORS["btn_start"],
            hover=COLORS["btn_start_h"],
            command=self._on_start,
            width=16,
        )
        self._btn_start.pack(side="left", padx=5)

        # زر Stop
        self._btn_stop = self._make_button(
            btn_frame,
            text="■  Stop",
            bg=COLORS["btn_stop"],
            hover=COLORS["btn_stop_h"],
            command=self._on_stop,
            width=10,
            state="disabled"
        )
        self._btn_stop.pack(side="left", padx=5)

        # زر Clear
        self._btn_clear = self._make_button(
            btn_frame,
            text="🗑  Clear",
            bg=COLORS["btn_clear"],
            hover="#2A5298",
            command=self._on_clear,
            width=8,
        )
        self._btn_clear.pack(side="left", padx=5)

        # زر Exit
        self._make_button(
            btn_frame,
            text="✕  Exit",
            bg=COLORS["btn_exit"],
            hover="#3D2490",
            command=self._on_exit,
            width=8,
        ).pack(side="left", padx=5)

        # ── خط فاصل تحت الهيدر ──────────────────────────────────────────
        tk.Frame(header, bg=COLORS["border"], height=1).grid(
            row=2, column=0, columnspan=3, sticky="ew"
        )

    # ─── MAIN CONTENT ─────────────────────────────────────────────────────

    def _build_main_content(self):
        """
        المحتوى الرئيسي:
        - العمود الأيسر: Statistics + System Info
        - العمود الأيمن: Alerts + Logs
        """
        main = make_frame(self.root, bg=COLORS["bg_dark"])
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main.columnconfigure(0, weight=1)  # عمود يسار
        main.columnconfigure(1, weight=3)  # عمود يمين (أكبر)
        main.rowconfigure(0, weight=1)

        # ── العمود الأيسر ────────────────────────────────────────────────
        left_col = make_frame(main, bg=COLORS["bg_dark"])
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_col.rowconfigure(1, weight=1)
        left_col.columnconfigure(0, weight=1)

        self._build_stats_panel(left_col)
        self._build_info_panel(left_col)
        self._build_threat_panel(left_col)

        # ── العمود الأيمن ────────────────────────────────────────────────
        right_col = make_frame(main, bg=COLORS["bg_dark"])
        right_col.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_col.columnconfigure(0, weight=1)
        right_col.rowconfigure(0, weight=1)
        right_col.rowconfigure(1, weight=2)

        self._build_alerts_panel(right_col)
        self._build_logs_panel(right_col)

    # ─── STATISTICS PANEL ─────────────────────────────────────────────────

    def _build_stats_panel(self, parent):
        """بطاقات الإحصائيات (Created / Modified / Deleted / Total)"""
        panel = self._make_card(parent, title="📊  Statistics")
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        grid = make_frame(panel, bg=COLORS["bg_card"])
        grid.pack(fill="x", padx=12, pady=8)
        grid.columnconfigure((0, 1), weight=1)

        # الـ counters
        self._stat_created  = self._make_stat_box(grid, "Created",  "0", COLORS["accent_green"],  0, 0)
        self._stat_modified = self._make_stat_box(grid, "Modified", "0", COLORS["accent_yellow"], 0, 1)
        self._stat_deleted  = self._make_stat_box(grid, "Deleted",  "0", COLORS["accent_red"],    1, 0)
        self._stat_total    = self._make_stat_box(grid, "Total",    "0", COLORS["accent_blue"],   1, 1)

    def _make_stat_box(self, parent, label, value, color, row, col):
        """يعمل بطاقة إحصائية صغيرة"""
        box = tk.Frame(parent, bg=COLORS["bg_input"], relief="flat")
        box.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        num_var = tk.StringVar(value=value)

        tk.Label(
            box,
            textvariable=num_var,
            font=FONTS["counter"],
            bg=COLORS["bg_input"],
            fg=color
        ).pack(pady=(8, 2))

        tk.Label(
            box,
            text=label,
            font=FONTS["label_sm"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_secondary"]
        ).pack(pady=(0, 8))

        return num_var

    # ─── SYSTEM INFO PANEL ────────────────────────────────────────────────

    def _build_info_panel(self, parent):
        """معلومات النظام - مسار المجلد المراقب والـ log file"""
        panel = self._make_card(parent, title="⚙️  System Info")
        panel.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        parent.rowconfigure(1, weight=0)

        info_frame = make_frame(panel, bg=COLORS["bg_card"])
        info_frame.pack(fill="both", expand=True, padx=12, pady=8)

        def info_row(label_text, value_text):
            row = make_frame(info_frame, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label_text, font=FONTS["label_sm"],
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                     width=14, anchor="w").pack(side="left")
            tk.Label(row, text=value_text, font=FONTS["mono"],
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                     anchor="w", wraplength=160).pack(side="left", fill="x", expand=True)

        watch_path = config.WATCH_DIRECTORY
        short_path = "..." + watch_path[-20:] if len(watch_path) > 22 else watch_path

        info_row("📁 Watch Dir:", short_path)
        info_row("🔁 Recursive:", "Yes" if config.RECURSIVE else "No")
        info_row("🔎 Extensions:", "ALL (any file)")

        # مسار الـ log file - بيتحدث لما تبدأ المراقبة
        log_row = make_frame(info_frame, bg=COLORS["bg_card"])
        log_row.pack(fill="x", pady=3)
        tk.Label(log_row, text="📄 Log File:", font=FONTS["label_sm"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                 width=14, anchor="w").pack(side="left")
        self._log_path_label = tk.Label(
            log_row, text="Not started yet",
            font=FONTS["mono"], bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"], anchor="w"
        )
        self._log_path_label.pack(side="left")

    # ─── THREAT LEVEL PANEL ───────────────────────────────────────────────

    def _build_threat_panel(self, parent):
        """
        بطاقة مستوى التهديد الكبيرة
        بتتغير لونها حسب الـ threat level
        """
        panel = self._make_card(parent, title="🎯  Threat Level")
        panel.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        parent.rowconfigure(2, weight=0)

        threat_frame = make_frame(panel, bg=COLORS["bg_card"])
        threat_frame.pack(fill="x", padx=12, pady=8)

        # الـ icon الكبير
        self._threat_icon = tk.Label(
            threat_frame,
            text="🔵",
            font=("Segoe UI", 32),
            bg=COLORS["bg_card"]
        )
        self._threat_icon.pack()

        # اسم مستوى التهديد
        self._threat_label = tk.Label(
            threat_frame,
            text="IDLE",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self._threat_label.pack()

        # تفاصيل entropy
        detail_frame = make_frame(threat_frame, bg=COLORS["bg_card"])
        detail_frame.pack(fill="x", pady=(8, 0))

        def detail_row(label, var):
            r = make_frame(detail_frame, bg=COLORS["bg_input"])
            r.pack(fill="x", pady=2, padx=4)
            tk.Label(r, text=label, font=FONTS["label_sm"],
                     bg=COLORS["bg_input"], fg=COLORS["text_muted"]).pack(side="left", padx=8, pady=4)
            tk.Label(r, textvariable=var, font=FONTS["mono"],
                     bg=COLORS["bg_input"], fg=COLORS["accent_blue"]).pack(side="right", padx=8)

        self._entropy_var  = tk.StringVar(value="0.00")
        self._modified_var = tk.StringVar(value="0")
        detail_row("Entropy Score:", self._entropy_var)
        detail_row("Modified Files:", self._modified_var)

    # ─── ALERTS PANEL ─────────────────────────────────────────────────────

    def _build_alerts_panel(self, parent):
        """
        قسم التنبيهات اللحظية
        بيعرض كل alert بلونه المناسب
        """
        panel = self._make_card(parent, title="🚨  Real-Time Alerts")
        panel.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        panel.pack_propagate(False)
        parent.rowconfigure(0, weight=1)

        # رأس القسم - عداد التنبيهات
        header_row = make_frame(panel, bg=COLORS["bg_card"])
        header_row.pack(fill="x", padx=12, pady=(0, 4))
        self._alert_count_label = tk.Label(
            header_row, text="0 alerts",
            font=FONTS["label_sm"], bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self._alert_count_label.pack(side="right")

        # منطقة التنبيهات - scrollable
        alert_container = make_frame(panel, bg=COLORS["bg_card"])
        alert_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self._alerts_text = scrolledtext.ScrolledText(
            alert_container,
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            font=FONTS["mono"],
            state="disabled",
            relief="flat",
            padx=10,
            pady=8,
            height=8,
            wrap="word",
        )
        self._alerts_text.pack(fill="both", expand=True)

        # Tags للألوان المختلفة للتنبيهات
        self._alerts_text.tag_configure("created",  foreground=COLORS["accent_green"])
        self._alerts_text.tag_configure("modified", foreground=COLORS["accent_yellow"])
        self._alerts_text.tag_configure("deleted",  foreground=COLORS["accent_red"])
        self._alerts_text.tag_configure("danger",   foreground=COLORS["accent_red"],    font=("Consolas", 9, "bold"))
        self._alerts_text.tag_configure("warning",  foreground=COLORS["accent_orange"], font=("Consolas", 9, "bold"))
        self._alerts_text.tag_configure("info",     foreground=COLORS["accent_blue"])
        self._alerts_text.tag_configure("timestamp",foreground=COLORS["text_muted"])

    # ─── LOGS PANEL ───────────────────────────────────────────────────────

    def _build_logs_panel(self, parent):
        """
        قسم اللوجز اللحظي
        بيعرض كل event بشكل JSON منسق أو نص سهل القراءة
        """
        panel = self._make_card(parent, title="📋  Real-Time Logs")
        panel.grid(row=1, column=0, sticky="nsew")
        parent.rowconfigure(1, weight=2)

        # رأس القسم - عداد اللوجز + toggle
        header_row = make_frame(panel, bg=COLORS["bg_card"])
        header_row.pack(fill="x", padx=12, pady=(0, 4))

        self._log_count_label = tk.Label(
            header_row, text="0 events logged",
            font=FONTS["label_sm"], bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self._log_count_label.pack(side="right")

        # منطقة اللوجز - scrollable
        log_container = make_frame(panel, bg=COLORS["bg_card"])
        log_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self._logs_text = scrolledtext.ScrolledText(
            log_container,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"],
            font=FONTS["mono"],
            state="disabled",
            relief="flat",
            padx=10,
            pady=8,
            height=14,
            wrap="none",
        )
        self._logs_text.pack(fill="both", expand=True)

        # Tags للوجز
        self._logs_text.tag_configure("created",   foreground=COLORS["accent_green"])
        self._logs_text.tag_configure("modified",  foreground=COLORS["accent_yellow"])
        self._logs_text.tag_configure("deleted",   foreground=COLORS["accent_red"])
        self._logs_text.tag_configure("timestamp", foreground=COLORS["text_muted"])
        self._logs_text.tag_configure("path",      foreground=COLORS["accent_blue"])
        self._logs_text.tag_configure("size",      foreground=COLORS["accent_purple"])
        self._logs_text.tag_configure("suspicious",foreground=COLORS["accent_orange"], font=("Consolas", 9, "bold"))
        self._logs_text.tag_configure("system",    foreground=COLORS["accent_blue"],   font=("Consolas", 9, "bold"))

    # ─── FOOTER ───────────────────────────────────────────────────────────

    def _build_footer(self):
        """الـ Footer - شريط المعلومات السفلي"""
        footer = make_frame(self.root, bg=COLORS["bg_panel"], height=28)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.columnconfigure(1, weight=1)

        tk.Frame(footer, bg=COLORS["border"], height=1).pack(fill="x", side="top")

        # وقت آخر تحديث
        self._footer_time = tk.Label(
            footer,
            text="Last update: --:--:--",
            font=FONTS["label_sm"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_muted"]
        )
        self._footer_time.pack(side="left", padx=15, pady=4)

        # اسم البروجيكت في المنتصف
        tk.Label(
            footer,
            text="🛡️  Ransomware Detection System  |  Graduation Project 2026",
            font=FONTS["label_sm"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_muted"]
        ).pack(side="left", expand=True)

        # حالة المراقبة
        self._footer_status = tk.Label(
            footer,
            text="● Idle",
            font=FONTS["label_sm"],
            bg=COLORS["bg_panel"],
            fg=COLORS["text_muted"]
        )
        self._footer_status.pack(side="right", padx=15, pady=4)

    # ──────────────────────────────────────────────────────────────────────
    #  HELPER - MAKE CARD
    # ──────────────────────────────────────────────────────────────────────

    def _make_card(self, parent, title: str) -> tk.Frame:
        """يعمل بطاقة (card) بإطار وعنوان"""
        outer = tk.Frame(parent, bg=COLORS["border"], bd=0)

        inner = tk.Frame(outer, bg=COLORS["bg_card"], padx=0, pady=0)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        # عنوان البطاقة
        header = make_frame(inner, bg=COLORS["bg_card"])
        header.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(
            header,
            text=title,
            font=FONTS["header"],
            bg=COLORS["bg_card"],
            fg=COLORS["accent_blue"]
        ).pack(side="left")

        # خط رفيع تحت العنوان
        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill="x", padx=12)

        return outer

    def _make_button(self, parent, text, bg, hover, command, width=12, state="normal"):
        """يعمل زر احترافي مع hover effect"""
        btn = tk.Button(
            parent,
            text=text,
            font=FONTS["body"],
            bg=bg,
            fg=COLORS["text_primary"],
            activebackground=hover,
            activeforeground=COLORS["text_primary"],
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=command,
            width=width,
            state=state,
        )

        # Hover effects
        def on_enter(e): btn.configure(bg=hover)
        def on_leave(e): btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    # ──────────────────────────────────────────────────────────────────────
    #  BUTTON HANDLERS - معالجات الأزرار
    # ──────────────────────────────────────────────────────────────────────


    # ──────────────────────────────────────────────────────────────────────
    #  SELECT FOLDER
    # ──────────────────────────────────────────────────────────────────────

    def _select_folder(self):
        """يسمح للمستخدم باختيار فولدر للمراقبة"""

        folder = filedialog.askdirectory(
            title="Select Folder To Monitor"
        )

        if folder:
         self.selected_folder = folder

         try:
            folder_name = os.path.basename(folder)

            self._folder_label.config(
            text=f"📁 {folder_name}"
           )

         except:
          pass

         self._append_log(
        f"[{self._now()}] Monitoring folder changed to: {folder}\n",
        tag="system"
        )
    def _on_start(self):
        """
        زر Start Monitoring
        - يبدأ الـ backend monitoring thread
        - يغير حالة الـ GUI
        """
        if self._is_monitoring:
            return

        self._is_monitoring = True
        self._btn_start.configure(state="disabled")
        self._btn_stop.configure(state="normal")

        # نحدث الحالة للـ "Monitoring"
        self._set_status("MONITORING", COLORS["accent_blue"])
        self._footer_status.configure(text="● Monitoring", fg=COLORS["accent_blue"])

        # نسجل في اللوجز
        self._append_log(
            f"[{self._now()}] System monitoring started\n",
            tag="system"
        )

        # نشغل الـ backend
        self._monitor = MonitoringThread(
            self._queue,
            watch_directory=self.selected_folder
        )

        self._monitor.start()

    def _on_stop(self):
        """
        زر Stop
        - يوقف الـ monitoring بشكل آمن
        - يحفظ الإحصائيات
        """
        if not self._is_monitoring:
            return

        self._is_monitoring = False
        self._btn_start.configure(state="normal")
        self._btn_stop.configure(state="disabled")

        # نوقف الـ backend
        self._monitor.stop()

        self._set_status("STOPPED", COLORS["text_secondary"])
        self._footer_status.configure(text="● Stopped", fg=COLORS["text_secondary"])

        self._append_log(
            f"[{self._now()}] Monitoring stopped by user\n",
            tag="system"
        )

        # ننشئ monitor جديد للمرة الجاية
        self._monitor = MonitoringThread(self._queue)

    def _on_clear(self):
        """
        زر Clear
        - يمسح اللوجز والـ alerts من الشاشة (مش من الملف)
        - يصفر العدادات
        """
        # مسح الـ alerts
        self._alerts_text.configure(state="normal")
        self._alerts_text.delete("1.0", "end")
        self._alerts_text.configure(state="disabled")

        # مسح اللوجز
        self._logs_text.configure(state="normal")
        self._logs_text.delete("1.0", "end")
        self._logs_text.configure(state="disabled")

        # تصفير العدادات
        self._alert_count = 0
        self._log_count   = 0
        self._alert_count_label.configure(text="0 alerts")
        self._log_count_label.configure(text="0 events logged")

        self._append_log(
            f"[{self._now()}] Display cleared (log files preserved)\n",
            tag="system"
        )

    def _on_exit(self):
        """زر Exit - يسأل ويخرج بشكل آمن"""
        if self._is_monitoring:
            if not messagebox.askyesno(
                "Confirm Exit",
                "Monitoring is still running.\nDo you want to stop and exit?"
            ):
                return
            self._monitor.stop()

        self.root.destroy()

    # ──────────────────────────────────────────────────────────────────────
    #  QUEUE POLLER - الـ loop اللي بيربط الـ backend بالـ GUI
    # ──────────────────────────────────────────────────────────────────────

    def _poll_queue(self):
        """
        بيتشغل كل 300ms ويقرأ الـ events من الـ queue
        ده أمن تماماً لأن بيشتغل في الـ main thread
        """
        try:
            # نقرأ كل الـ messages المتاحة في الـ queue دلوقتي
            while True:
                msg = self._queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass
        except Exception as exc:
            self._append_log(f"[GUI Error] {exc}\n", tag="system")

        # نجدول نفسنا تاني بعد 300ms
        self.root.after(300, self._poll_queue)

    def _handle_message(self, msg: dict):
        """يعالج رسالة من الـ queue ويحدث الـ GUI"""
        mtype = msg.get("type")

        if mtype == "event":
            # حدث ملف جديد - نضيفه للـ logs
            self._handle_event(msg["record"])

        elif mtype == "alert":
            # تنبيه - نضيفه للـ alerts
            self._handle_alert(msg["record"])

        elif mtype == "analysis":
            # تحليل التهديد - نحدث الـ threat level
            self._handle_analysis(msg)

        elif mtype == "status":
            # رسالة حالة من الـ backend
            self._append_log(f"[{self._now()}] {msg['message']}\n", tag="system")
            if "log_path" in msg:
                short = "..." + msg["log_path"][-25:]
                self._log_path_label.configure(text=short)

        elif mtype == "error":
            # خطأ في الـ backend
            self._append_alert(
                f"[{self._now()}] ⚠️  BACKEND ERROR: {msg['message']}\n",
                tag="danger"
            )
            self._set_status("ERROR", COLORS["accent_red"])

        elif mtype == "stopped":
            # الـ backend وقف
            if not self._is_monitoring:
                self._set_status("STOPPED", COLORS["text_secondary"])

        # نحدث الوقت في الـ footer
        self._footer_time.configure(text=f"Last update: {self._now()}")

    def _handle_event(self, record: dict):
        """يضيف event للـ logs area"""
        self._log_count += 1
        self._log_count_label.configure(text=f"{self._log_count} events logged")

        etype    = record.get("event_type", "?")
        fname    = record.get("file_name", "?")
        fpath    = record.get("file_path", "?")
        size     = record.get("size_bytes")
        ts       = record.get("timestamp", "?")[11:23]  # نأخذ الوقت بس
        is_dir   = record.get("is_directory", False)
        # FIX: استخدام .get() بدل [] لأن behavior_classification مش دايمًا موجود
        behavior = record.get("behavior_classification", "")

        icons = {"created": "＋", "modified": "～", "deleted": "－"}
        icon  = icons.get(etype, "•")
        kind  = "DIR" if is_dir else "FILE"
        size_str = f"  [{size:,}B]" if size else ""

        # نبني الـ log line
        line = f"{icon} [{ts}] {etype.upper():<8} {kind}  {fname}{size_str}\n"
        if behavior == "Suspicious":
            line += f"    ⚠️  SUSPICIOUS BEHAVIOR DETECTED on {fpath}\n"

        # نحدث عداد الإحصائيات
        if etype == "created":
            val = int(self._stat_created.get()) + 1
            self._stat_created.set(str(val))
        elif etype == "modified":
            val = int(self._stat_modified.get()) + 1
            self._stat_modified.set(str(val))
        elif etype == "deleted":
            val = int(self._stat_deleted.get()) + 1
            self._stat_deleted.set(str(val))

        total = int(self._stat_total.get()) + 1
        self._stat_total.set(str(total))

        # نكتب في الـ logs
        tag = "suspicious" if behavior == "Suspicious" else etype
        self._append_log(line, tag=tag)

    def _handle_alert(self, record: dict):
        """يضيف alert للـ alerts area"""
        print(record)
        print("Event Type =", record.get("event_type"))
        self._alert_count += 1
        self._alert_count_label.configure(text=f"{self._alert_count} alerts")

        etype = record.get("event_type", "?")
        fname = record.get("file_name", "?")
        fpath = record.get("file_path", "?")
        ts    = record.get("timestamp", "?")[11:23]

        icons = {"created": "✅", "modified": "✏️", "deleted": "🗑️"}
        icon  = icons.get(etype, "📌")

        line = f"{icon} [{ts}] {etype.upper():8}  {fname}\n    📂 {fpath}\n"

        tag = etype
        self._append_alert(line, tag=tag)

    def _handle_analysis(self, msg: dict):
        """يحدث Threat Level بناءً على نتيجة التحليل"""
        threat   = msg.get("threat", "NORMAL")
        modified = msg.get("modified", 0)
        entropy  = msg.get("entropy", 0.0)

        self._entropy_var.set(f"{entropy:.2f}")
        self._modified_var.set(str(modified))

        self.dashboard.heartbeat(
          protection=True,
          realtime=self._is_monitoring,
          threats_blocked=self._alert_count,
          files_scanned=self._log_count,
          threat_level=self._threat_level,
        )  
        if threat == "DANGEROUS":
            self._set_status("ATTACK DETECTED", COLORS["accent_red"])
            self._set_threat("DANGEROUS", "🔴", COLORS["accent_red"])
            self._append_alert(
                f"[{self._now()}] 🚨 ATTACK DETECTED! Modified={modified}, Entropy={entropy:.2f}\n",
                tag="danger"
            )
            self._threat_level = "DANGEROUS"
        elif threat == "SUSPICIOUS":
            self._set_status("SUSPICIOUS ACTIVITY", COLORS["accent_orange"])
            self._set_threat("SUSPICIOUS", "🟠", COLORS["accent_orange"])
            self._append_alert(
                f"[{self._now()}] ⚠️  SUSPICIOUS ACTIVITY! Modified={modified}, Entropy={entropy:.2f}\n",
                tag="warning"
            )
            self._threat_level = "SUSPICIOUS"
        else:
            if self._is_monitoring:
                self._set_status("MONITORING - SAFE", COLORS["accent_green"])
                self._set_threat("NORMAL", "🟢", COLORS["accent_green"])
                self._threat_level = "NORMAL"
    

    # ──────────────────────────────────────────────────────────────────────
    #  UI UPDATERS
    # ──────────────────────────────────────────────────────────────────────

    def _set_status(self, text: str, color: str):
        """يغير مؤشر الحالة الكبير في الهيدر"""
        self._status_label.configure(text=text, fg=color)
        self._status_dot.configure(fg=color)

    def _set_threat(self, text: str, icon: str, color: str):
        """يغير بطاقة الـ Threat Level"""
        self._threat_label.configure(text=text, fg=color)
        self._threat_icon.configure(text=icon)

    def _append_log(self, text: str, tag: str = ""):
        """يضيف سطر للـ logs area"""
        self._logs_text.configure(state="normal")
        if tag:
            self._logs_text.insert("end", text, tag)
        else:
            self._logs_text.insert("end", text)
        self._logs_text.see("end")  # auto-scroll
        self._logs_text.configure(state="disabled")

    def _append_alert(self, text: str, tag: str = ""):
        """يضيف سطر للـ alerts area"""
        self._alerts_text.configure(state="normal")
        if tag:
            self._alerts_text.insert("end", text, tag)
        else:
            self._alerts_text.insert("end", text)
        self._alerts_text.see("end")  # auto-scroll
        self._alerts_text.configure(state="disabled")

    @staticmethod
    def _now() -> str:
        """الوقت الحالي بصيغة HH:MM:SS"""
        return datetime.now().strftime("%H:%M:%S")

    def _heartbeat_loop(self):

     while True:

        try:

            self.dashboard.heartbeat(
                protection=True,
                realtime=self._is_monitoring,
                threats_blocked=self._alert_count,
                files_scanned=self._log_count,
                threat_level=self._threat_level,
            )

        except Exception as e:

            print("Heartbeat Loop Error:", e)

        time.sleep(5)


def main():
    root = tk.Tk()

    # نستخدم الـ style المتاح
    style = ttk.Style(root)
    style.theme_use("clam")

    # نشغل الـ GUI
    app = RansomwareDetectorGUI(root)

    # نبدأ الـ main loop
    root.mainloop()


if __name__ == "__main__":
    main()
