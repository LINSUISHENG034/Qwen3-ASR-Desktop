"""
Main Window for Qwen3-ASR GUI
Premium glassmorphism-inspired interface with drag-drop, progress visualization, and modern UX
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QProgressBar,
    QFileDialog,
    QSplitter,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont

from .transcription_panel import TranscriptionPanel
from .settings_panel import SettingsPanel
from .worker_thread import TranscriptionWorker
from .styles import get_stylesheet


SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac",  # Audio
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv",  # Video
}


class DropZone(QFrame):
    """Drag-and-drop zone for file upload."""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the drop zone UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Icon
        self.icon_label = QLabel("🎵")
        self.icon_label.setObjectName("dropIcon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(48)
        self.icon_label.setFont(font)
        layout.addWidget(self.icon_label)

        # Text
        self.text_label = QLabel("Drag & Drop Audio/Video File Here")
        self.text_label.setObjectName("dropLabel")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)

        # Subtext
        self.subtext_label = QLabel("or click 'Browse' below")
        self.subtext_label.setObjectName("subheading")
        self.subtext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtext_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self._is_supported_file(urls[0].toLocalFile()):
                event.acceptProposedAction()
                self.setObjectName("dropZoneActive")
                self.setStyleSheet(self.styleSheet())  # Refresh style

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self.setObjectName("dropZone")
        self.setStyleSheet(self.styleSheet())

    def dropEvent(self, event: QDropEvent):
        """Handle file drop."""
        self.setObjectName("dropZone")
        self.setStyleSheet(self.styleSheet())

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self._is_supported_file(file_path):
                self.file_dropped.emit(file_path)

    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in SUPPORTED_EXTENSIONS

    def set_file(self, file_path: str):
        """Update display with selected file."""
        if file_path:
            filename = os.path.basename(file_path)
            self.icon_label.setText("✅")
            self.text_label.setText(filename)
            self.subtext_label.setText(file_path)
        else:
            self.icon_label.setText("🎵")
            self.text_label.setText("Drag & Drop Audio/Video File Here")
            self.subtext_label.setText("or click 'Browse' below")


class MainWindow(QMainWindow):
    """Main application window for Qwen3-ASR GUI."""

    def __init__(self):
        super().__init__()
        self.worker: Optional[TranscriptionWorker] = None
        self.current_file: str = ""
        self._setup_window()
        self._setup_ui()
        self._apply_theme()

    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("Qwen3-ASR Toolkit")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Center on screen
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _setup_ui(self):
        """Initialize the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─────────────────────────────────────────────────────────────
        # Sidebar
        # ─────────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 24, 20, 24)
        sidebar_layout.setSpacing(24)

        # Logo
        logo = QLabel("✨ Qwen3-ASR")
        logo.setObjectName("logo")
        sidebar_layout.addWidget(logo)

        # Version
        version = QLabel("Toolkit v1.0 • GUI Edition")
        version.setObjectName("version")
        sidebar_layout.addWidget(version)

        sidebar_layout.addSpacing(20)

        # Navigation buttons
        self.nav_transcribe_btn = QPushButton("🎙️  Transcribe")
        self.nav_transcribe_btn.setObjectName("primaryButton")
        self.nav_transcribe_btn.setCheckable(True)
        self.nav_transcribe_btn.setChecked(True)
        self.nav_transcribe_btn.clicked.connect(lambda: self._switch_page(0))
        sidebar_layout.addWidget(self.nav_transcribe_btn)

        self.nav_settings_btn = QPushButton("⚙️  Settings")
        self.nav_settings_btn.setCheckable(True)
        self.nav_settings_btn.clicked.connect(lambda: self._switch_page(1))
        sidebar_layout.addWidget(self.nav_settings_btn)

        sidebar_layout.addStretch()

        # Quick stats
        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(8)

        self.stats_label = QLabel("Ready to transcribe")
        self.stats_label.setObjectName("subheading")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        sidebar_layout.addWidget(stats_frame)

        main_layout.addWidget(sidebar)

        # ─────────────────────────────────────────────────────────────
        # Main Content Area
        # ─────────────────────────────────────────────────────────────
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)

        # Stacked widget for pages
        self.page_stack = QStackedWidget()

        # ═══════════════════════════════════════════════════════════
        # Page 0: Transcription
        # ═══════════════════════════════════════════════════════════
        transcribe_page = QWidget()
        transcribe_layout = QVBoxLayout(transcribe_page)
        transcribe_layout.setContentsMargins(0, 0, 0, 0)
        transcribe_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        page_title = QLabel("Audio Transcription")
        page_title.setObjectName("heading")
        header_layout.addWidget(page_title)

        header_layout.addStretch()

        transcribe_layout.addLayout(header_layout)

        # Drop zone + controls
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(16)

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file_selected)
        input_layout.addWidget(self.drop_zone)

        # File controls row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.browse_btn = QPushButton("📂 Browse...")
        self.browse_btn.clicked.connect(self._browse_file)
        controls_layout.addWidget(self.browse_btn)

        controls_layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(200)
        controls_layout.addWidget(self.progress_bar)

        self.cancel_btn = QPushButton("✖ Cancel")
        self.cancel_btn.setObjectName("dangerButton")
        self.cancel_btn.clicked.connect(self._cancel_transcription)
        self.cancel_btn.setVisible(False)
        controls_layout.addWidget(self.cancel_btn)

        self.transcribe_btn = QPushButton("🚀 Transcribe")
        self.transcribe_btn.setObjectName("primaryButton")
        self.transcribe_btn.clicked.connect(self._start_transcription)
        self.transcribe_btn.setEnabled(False)
        controls_layout.addWidget(self.transcribe_btn)

        input_layout.addLayout(controls_layout)

        transcribe_layout.addWidget(input_frame)

        # Transcription results
        self.transcription_panel = TranscriptionPanel()
        transcribe_layout.addWidget(self.transcription_panel, 1)

        self.page_stack.addWidget(transcribe_page)

        # ═══════════════════════════════════════════════════════════
        # Page 1: Settings
        # ═══════════════════════════════════════════════════════════
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(20)

        settings_title = QLabel("Settings")
        settings_title.setObjectName("heading")
        settings_layout.addWidget(settings_title)

        self.settings_panel = SettingsPanel()
        settings_layout.addWidget(self.settings_panel, 1)

        self.page_stack.addWidget(settings_page)

        content_layout.addWidget(self.page_stack)

        main_layout.addWidget(content_area, 1)

    def _apply_theme(self):
        """Apply the premium dark theme."""
        self.setStyleSheet(get_stylesheet("dark"))

    def _switch_page(self, index: int):
        """Switch between pages."""
        self.page_stack.setCurrentIndex(index)

        # Update nav button states
        self.nav_transcribe_btn.setChecked(index == 0)
        self.nav_settings_btn.setChecked(index == 1)

    def _browse_file(self):
        """Open file browser dialog."""
        file_filter = (
            "Media Files (*.mp3 *.wav *.m4a *.flac *.ogg *.mp4 *.mkv *.avi *.mov *.webm);;"
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.wma *.aac);;"
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.wmv *.flv);;"
            "All Files (*)"
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio/Video File",
            "",
            file_filter,
        )
        if file_path:
            self._on_file_selected(file_path)

    def _on_file_selected(self, file_path: str):
        """Handle file selection."""
        self.current_file = file_path
        self.drop_zone.set_file(file_path)
        self.transcribe_btn.setEnabled(True)
        self.transcription_panel.set_input_file(file_path)
        self.transcription_panel.clear()

        # Update stats
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        self.stats_label.setText(f"📁 {os.path.basename(file_path)}\n💾 {size_mb:.1f} MB")

    def _start_transcription(self):
        """Start the transcription process."""
        if not self.current_file:
            return

        # Check API key
        api_key = self.settings_panel.get_api_key()
        if not api_key and "DASHSCOPE_API_KEY" not in os.environ:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Please enter your DashScope API key in Settings.\n\n"
                "Get your key at: dashscope.console.aliyun.com/apiKey",
            )
            self._switch_page(1)  # Switch to settings
            return

        # Clear previous results
        self.transcription_panel.clear()

        # Update UI state
        self.transcribe_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create worker
        self.worker = TranscriptionWorker(
            input_file=self.current_file,
            api_key=api_key,
            num_threads=self.settings_panel.get_num_threads(),
            vad_threshold=self.settings_panel.get_vad_threshold(),
            context=self.settings_panel.get_context(),
            save_srt=self.settings_panel.get_save_srt(),
            tmp_dir=self.settings_panel.get_temp_dir(),
        )

        # Connect signals
        self.worker.progress.connect(self._on_progress)
        self.worker.status_update.connect(self._on_status_update)
        self.worker.segment_completed.connect(self._on_segment_completed)
        self.worker.finished_transcription.connect(self._on_transcription_finished)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_worker_finished)

        # Start
        self.worker.start()

    def _cancel_transcription(self):
        """Cancel the ongoing transcription."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.stats_label.setText("⚠️ Cancelling...")

    def _on_progress(self, current: int, total: int, message: str):
        """Handle progress update."""
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current}% - {message}")

    def _on_status_update(self, status: str):
        """Handle status text update."""
        self.stats_label.setText(status)
        self.transcription_panel.set_status(status)

    def _on_segment_completed(self, idx: int, text: str, start: float, end: float):
        """Handle individual segment completion."""
        self.transcription_panel.append_segment(idx, text, start, end)

    def _on_transcription_finished(self, full_text: str, language: str, segments: list):
        """Handle successful transcription completion."""
        self.transcription_panel.set_full_result(full_text, language, segments)
        self.stats_label.setText(f"✅ Done!\n🌐 {language}\n📝 {len(segments)} segments")

    def _on_error(self, error_msg: str):
        """Handle transcription error."""
        QMessageBox.critical(self, "Transcription Error", error_msg)
        self.stats_label.setText(f"❌ Error occurred")

    def _on_worker_finished(self):
        """Reset UI after worker finishes."""
        self.transcribe_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.worker = None

    def load_config(self, env_path: str):
        """Load configuration from .asr_env file."""
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("\"'")
                            if key in ("DASHSCOPE_API", "DASHSCOPE_API_KEY"):
                                self.settings_panel.set_api_key(value)
                                os.environ["DASHSCOPE_API_KEY"] = value
            except Exception as e:
                print(f"Error loading config: {e}")
