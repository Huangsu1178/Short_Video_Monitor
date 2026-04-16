"""
Main window for the dual-platform monitor.
"""
import html
import os

from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_AI_MODEL
from ui.components.theme import (
    ACCENT,
    BG_APP,
    BORDER,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    WARNING,
    global_stylesheet,
    nav_button_style,
    sidebar_style,
)
from ui.pages.ai_report.ai_report_page import AIReportPage
from ui.pages.dashboard.dashboard_page import DashboardPage
from ui.pages.data_view.data_view_page import DataViewPage
from ui.pages.influencer.influencer_page import InfluencerPage
from ui.pages.settings.settings_page import SettingsPage


class WorkerSignals(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)


class FetchWorker(QThread):
    def __init__(self, fetch_func, *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.fetch_func = fetch_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.fetch_func(*self.args, progress_callback=self.signals.progress.emit, **self.kwargs)
            self.signals.finished.emit(result if isinstance(result, dict) else {"status": "done"})
        except BaseException as exc:
            self.signals.error.emit(str(exc))


class MainWindow(QMainWindow):
    scheduler_status_signal = pyqtSignal(str)
    scheduled_fetch_finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.scheduler_status_signal.connect(self._apply_scheduler_status)
        self.scheduled_fetch_finished.connect(self._on_scheduled_fetch_done)

        self.setWindowTitle("Short Video Monitor - TikTok / Douyin")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)

        self._current_worker = None
        self._init_core()
        self._build_ui()
        self._start_scheduler()

    def _init_core(self):
        from core.ai_analyzer import AIAnalyzer
        from core.scheduler import MonitorScheduler
        from core.scraper import FetchTask, MultiPlatformScraper
        from data.database import init_database
        from skills import initialize_skills

        init_database()

        print("[MainWindow] Initializing core modules...")

        proxy_url = os.environ.get("PROXY_URL", os.environ.get("HTTP_PROXY", ""))
        print(f"[MainWindow] Proxy: {proxy_url or 'not set'}")
        self.scraper = MultiPlatformScraper(proxy_url=proxy_url, headless=True)
        self.fetch_task = FetchTask(self.scraper)

        api_key = os.environ.get("GEMINI_API_KEY", "")
        model = os.environ.get("GEMINI_MODEL", DEFAULT_AI_MODEL)
        print(f"[MainWindow] AI config: api_key={'set' if api_key else 'not set'}, model={model}")

        self.ai_analyzer = AIAnalyzer(api_key=api_key, api_base="", model=model)
        self.skill_registry = initialize_skills(api_key, "", model)

        auto_fetch_enabled = os.environ.get("AUTO_FETCH_ENABLED", "0") == "1"
        fetch_interval = float(os.environ.get("FETCH_INTERVAL", "1"))
        print(f"[MainWindow] Scheduler: auto_fetch={auto_fetch_enabled}, interval={fetch_interval}h")

        self.scheduler = MonitorScheduler()
        self.scheduler.set_status_callback(self._on_scheduler_status)

    def _build_ui(self):
        self.setStyleSheet(global_stylesheet())

        central = QWidget()
        central.setObjectName("main_content")
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"QStackedWidget {{ background-color: {BG_APP}; }}")
        layout.addWidget(self.stack, 1)

        self.dashboard_page = DashboardPage(self)
        self.influencer_page = InfluencerPage(self)
        self.data_view_page = DataViewPage(self)
        self.ai_report_page = AIReportPage(self)
        self.settings_page = SettingsPage(self)

        for page in [
            self.dashboard_page,
            self.influencer_page,
            self.data_view_page,
            self.ai_report_page,
            self.settings_page,
        ]:
            self.stack.addWidget(page)

        self._nav_btns[0].setChecked(True)
        self.stack.setCurrentIndex(0)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(232)
        sidebar.setStyleSheet(sidebar_style())

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(8, 0, 8, 0)

        logo_icon = QLabel("SV")
        logo_icon.setFont(QFont("Segoe UI", 21, 700))
        logo_icon.setStyleSheet(f"color: {ACCENT}; font-weight: 800; letter-spacing: 1px;")
        logo_layout.addWidget(logo_icon)

        logo_text = QLabel("Short Video\nMonitor")
        logo_text.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 17px; font-weight: 800; line-height: 1.2;"
        )
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        layout.addWidget(logo_widget)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {BORDER}; margin: 12px 0;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        nav_items = [
            ("Dashboard", 0),
            ("Accounts", 1),
            ("Data View", 2),
            ("AI Reports", 3),
            ("Settings", 4),
        ]

        self._nav_btns = []
        for text, idx in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setStyleSheet(nav_button_style())
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            layout.addWidget(btn)
            self._nav_btns.append(btn)

        layout.addStretch()

        status_title = QLabel("Runtime Status")
        status_title.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1px; padding: 0 8px 4px 8px;"
        )
        layout.addWidget(status_title)

        status_panel = QFrame()
        status_panel.setStyleSheet(
            f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            """
        )
        status_layout = QVBoxLayout(status_panel)
        status_layout.setContentsMargins(10, 10, 10, 10)
        status_layout.setSpacing(0)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.status_label.setWordWrap(True)
        self.status_label.setTextFormat(Qt.TextFormat.RichText)
        self.status_label.setMinimumHeight(72)
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_panel)

        version_label = QLabel("v2.0 Dual Platform")
        version_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 4px 8px;")
        layout.addWidget(version_label)

        self.set_idle_status()
        return sidebar

    def _format_status_html(self, title: str, detail: str = "", color: str = TEXT_PRIMARY) -> str:
        safe_title = html.escape((title or "Ready").strip())
        safe_detail = html.escape((detail or "").strip()).replace("\n", "<br/>")
        detail_block = (
            f"<div style='color:{TEXT_MUTED}; font-size:11px; line-height:1.45; margin-top:6px;'>{safe_detail}</div>"
            if safe_detail
            else ""
        )
        return (
            f"<div style='color:{color}; font-size:12px; font-weight:700; line-height:1.4;'>{safe_title}</div>"
            f"{detail_block}"
        )

    def _apply_status_panel(self, title: str, detail: str = "", color: str = TEXT_PRIMARY):
        self.status_label.setText(self._format_status_html(title, detail, color))

    def update_runtime_status(self, title: str, detail: str = "", color: str = WARNING):
        self._apply_status_panel(title, detail, color)

    def set_idle_status(self, detail: str = ""):
        auto_fetch = os.environ.get("AUTO_FETCH_ENABLED", "0") == "1"
        if auto_fetch:
            interval = float(os.environ.get("FETCH_INTERVAL", "1"))
            self._apply_status_panel("Auto Monitoring", detail or f"Auto fetch every {interval:g}h", SUCCESS)
            return
        self._apply_status_panel("Ready", detail or "Waiting for the next action", TEXT_PRIMARY)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.dashboard_page.refresh()
        elif index == 1:
            self.influencer_page.refresh()
        elif index == 2:
            self.data_view_page.refresh()
        elif index == 3:
            self.ai_report_page.refresh()

    def _start_scheduler(self):
        auto_fetch = os.environ.get("AUTO_FETCH_ENABLED", "0") == "1"
        if auto_fetch:
            interval = float(os.environ.get("FETCH_INTERVAL", "1"))
            self.scheduler.start()
            self.scheduler.add_global_fetch_job(self.fetch_all_active, interval)
            self.set_idle_status(f"Auto fetch every {interval:g}h")

    def fetch_all_active(self):
        from core.platforms import platform_label
        from data.database import get_active_influencers

        influencers = get_active_influencers()
        max_videos = int(os.environ.get("MAX_VIDEOS_PER_FETCH", "20"))
        total = len(influencers)
        results = []

        if total == 0:
            self.scheduler_status_signal.emit("No active accounts to monitor")
            return {"status": "done", "results": results}

        for index, influencer in enumerate(influencers, 1):
            username = influencer.get("username", "")
            platform = platform_label(influencer.get("platform"))
            self.scheduler_status_signal.emit(f"Auto fetch {index}/{total}\n{platform} | @{username}")

            def emit_progress(message: str, current=index, total_count=total):
                self.scheduler_status_signal.emit(f"Auto fetch {current}/{total_count}\n{message}")

            results.append(self.fetch_task.run(influencer, max_videos, progress_callback=emit_progress))

        self.scheduled_fetch_finished.emit(results)
        return {"status": "done", "results": results}

    def fetch_single(self, influencer: dict):
        from core.platforms import format_account_identity, platform_label

        max_videos = int(os.environ.get("MAX_VIDEOS_PER_FETCH", "20"))
        account_text = format_account_identity(
            influencer.get("platform"),
            influencer.get("username", ""),
            influencer.get("profile_url", ""),
        )
        self.update_runtime_status(
            "Fetching Data",
            f"{platform_label(influencer.get('platform'))} | {account_text}",
            WARNING,
        )

        worker = FetchWorker(self.fetch_task.run, influencer, max_videos)
        worker.signals.finished.connect(self._on_fetch_done)
        worker.signals.error.connect(self._on_fetch_error)
        worker.signals.progress.connect(self._on_fetch_progress)
        worker.start()
        self._current_worker = worker

    def _on_fetch_progress(self, message: str):
        self.update_runtime_status("Fetch Progress", message, WARNING)

    def _on_fetch_done(self, result: dict):
        if result.get("status") == "error":
            self._on_fetch_error(result.get("error", "Unknown error"))
            return

        videos_new = result.get("videos_new", 0)
        self.update_runtime_status("Fetch Complete", f"Added {videos_new} new videos", SUCCESS)

        self.influencer_page.refresh()
        self.data_view_page.refresh()
        self.dashboard_page.refresh()
        self.ai_report_page.refresh()

    def _on_fetch_error(self, error: str):
        self.update_runtime_status("Fetch Failed", error, ACCENT)

    def _on_scheduler_status(self, msg: str):
        self.scheduler_status_signal.emit(msg)

    def _apply_scheduler_status(self, msg: str):
        color = ACCENT if any(token in msg.lower() for token in ("error", "failed")) else SUCCESS
        self.update_runtime_status("Scheduler", msg, color)

    def _on_scheduled_fetch_done(self, results):
        self.influencer_page.refresh()
        self.data_view_page.refresh()
        self.dashboard_page.refresh()
        self.ai_report_page.refresh()

        videos_new = sum(int((item or {}).get("videos_new", 0) or 0) for item in results or [])
        self.update_runtime_status(
            "Auto Fetch Complete",
            f"Processed {len(results or [])} accounts and added {videos_new} new videos",
            SUCCESS,
        )

    def update_skills_config(self, api_key: str, api_base: str = "", model: str = ""):
        if hasattr(self, "skill_registry"):
            self.skill_registry.update_all_configs(api_key, api_base, model)
            self.ai_analyzer.update_config(api_key, api_base, model)

    def navigate_to(self, page_index: int):
        self._nav_btns[page_index].setChecked(True)
        self._switch_page(page_index)

    def closeEvent(self, event):
        self.scheduler.stop()
        event.accept()
