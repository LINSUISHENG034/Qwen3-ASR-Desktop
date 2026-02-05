"""
Main Window for Qwen3-ASR GUI
Premium glassmorphism-inspired interface with drag-drop, progress visualization, and modern UX
"""

import os
from typing import Optional, List

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
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont

from .transcription_panel import TranscriptionPanel
from .settings_panel import SettingsPanel
from .worker_thread import TranscriptionWorker, BatchTranscriptionWorker
from .styles import get_stylesheet


SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac",  # Audio
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv",  # Video
}


class DropZone(QFrame):
    """Drag-and-drop zone for file upload."""

    file_dropped = pyqtSignal(list)  # List[str] - supports multiple files

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
            # Accept if any file is supported
            if any(self._is_supported_file(url.toLocalFile()) for url in urls):
                event.acceptProposedAction()
                self.setObjectName("dropZoneActive")
                self.setStyleSheet(self.styleSheet())

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
            valid_files = [
                url.toLocalFile() for url in urls
                if self._is_supported_file(url.toLocalFile())
            ]
            if valid_files:
                self.file_dropped.emit(valid_files)

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

    def set_files(self, file_paths: List[str]):
        """Update display for multiple files."""
        count = len(file_paths)
        if count > 0:
            self.icon_label.setText("📁")
            self.text_label.setText(f"{count} file{'s' if count > 1 else ''} selected")
            self.subtext_label.setText("Ready for batch transcription")
        else:
            self.icon_label.setText("🎵")
            self.text_label.setText("Drag & Drop Audio/Video Files Here")
            self.subtext_label.setText("or click 'Browse' below")


class FileQueueWidget(QWidget):
    """Widget for displaying and managing a queue of files for batch processing."""

    files_changed = pyqtSignal(list)  # Emitted when file selection changes

    # Status constants
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_ERROR = "error"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: List[dict] = []  # [{path, size, status, checked}]
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the file queue UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QLabel("File Queue")
        header.setObjectName("subheading")
        layout.addWidget(header)

        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(120)
        self.file_list.setMaximumHeight(200)
        self.file_list.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.file_list)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        btn_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        btn_layout.addWidget(self.deselect_all_btn)

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def add_files(self, file_paths: List[str]):
        """Add files to the queue."""
        for path in file_paths:
            if not any(f["path"] == path for f in self._files):
                size = os.path.getsize(path) if os.path.exists(path) else 0
                self._files.append({
                    "path": path,
                    "size": size,
                    "status": self.STATUS_PENDING,
                    "checked": True,
                })
        self._refresh_list()
        self.files_changed.emit(self.get_selected_files())

    def get_selected_files(self) -> List[str]:
        """Return list of checked file paths."""
        return [f["path"] for f in self._files if f["checked"]]

    def get_all_files(self) -> List[str]:
        """Return all file paths."""
        return [f["path"] for f in self._files]

    def set_file_status(self, index: int, status: str):
        """Update status for a file by index."""
        if 0 <= index < len(self._files):
            self._files[index]["status"] = status
            self._refresh_list()

    def clear(self):
        """Clear all files from the queue."""
        self._files.clear()
        self._refresh_list()
        self.files_changed.emit([])

    def _refresh_list(self):
        """Refresh the list widget display."""
        self.file_list.clear()
        for f in self._files:
            item = self._create_list_item(f)
            self.file_list.addItem(item)

    def _create_list_item(self, file_info: dict) -> QListWidgetItem:
        """Create a list item for a file."""
        filename = os.path.basename(file_info["path"])
        size_mb = file_info["size"] / (1024 * 1024)
        status = file_info["status"]

        # Status icons
        status_icons = {
            self.STATUS_PENDING: "⏳",
            self.STATUS_PROCESSING: "🔄",
            self.STATUS_DONE: "✅",
            self.STATUS_ERROR: "❌",
        }
        icon = status_icons.get(status, "⏳")

        text = f"{icon} {filename}  ({size_mb:.1f} MB)"
        item = QListWidgetItem(text)
        item.setCheckState(
            Qt.CheckState.Checked if file_info["checked"] else Qt.CheckState.Unchecked
        )
        return item

    def _select_all(self):
        """Check all files."""
        for f in self._files:
            f["checked"] = True
        self._refresh_list()
        self.files_changed.emit(self.get_selected_files())

    def _deselect_all(self):
        """Uncheck all files."""
        for f in self._files:
            f["checked"] = False
        self._refresh_list()
        self.files_changed.emit(self.get_selected_files())

    def _remove_selected(self):
        """Remove selected items from the list."""
        selected_rows = [
            self.file_list.row(item)
            for item in self.file_list.selectedItems()
        ]
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self._files):
                del self._files[row]
        self._refresh_list()
        self.files_changed.emit(self.get_selected_files())

    def _on_item_changed(self, item: QListWidgetItem):
        """Handle checkbox state change."""
        row = self.file_list.row(item)
        if 0 <= row < len(self._files):
            is_checked = item.checkState() == Qt.CheckState.Checked
            self._files[row]["checked"] = is_checked
            self.files_changed.emit(self.get_selected_files())


class MainWindow(QMainWindow):
    """Main application window for Qwen3-ASR GUI."""

    def __init__(self):
        super().__init__()
        self.worker: Optional[TranscriptionWorker] = None
        self.batch_worker: Optional[BatchTranscriptionWorker] = None
        self.current_file: str = ""
        self.current_files: List[str] = []
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
        self.drop_zone.file_dropped.connect(self._on_files_selected)
        input_layout.addWidget(self.drop_zone)

        # File queue widget
        self.file_queue = FileQueueWidget()
        self.file_queue.files_changed.connect(self._on_queue_changed)
        self.file_queue.setVisible(False)
        input_layout.addWidget(self.file_queue)

        # File controls row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.browse_btn = QPushButton("📂 Browse Files...")
        self.browse_btn.clicked.connect(self._browse_files)
        controls_layout.addWidget(self.browse_btn)

        self.browse_folder_btn = QPushButton("📁 Browse Folder...")
        self.browse_folder_btn.clicked.connect(self._browse_folder)
        controls_layout.addWidget(self.browse_folder_btn)

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

    def _browse_files(self):
        """Open multi-file browser dialog."""
        file_filter = (
            "Media Files (*.mp3 *.wav *.m4a *.flac *.ogg *.mp4 *.mkv *.avi *.mov *.webm);;"
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.wma *.aac);;"
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.wmv *.flv);;"
            "All Files (*)"
        )
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio/Video Files",
            "",
            file_filter,
        )
        if file_paths:
            self._on_files_selected(file_paths)

    def _browse_folder(self):
        """Open folder browser and select all media files."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Media Files",
            "",
        )
        if folder:
            files = self._scan_folder_for_media(folder)
            if files:
                self._on_files_selected(files)
            else:
                QMessageBox.information(
                    self,
                    "No Media Files",
                    "No supported media files found in the selected folder.",
                )

    def _scan_folder_for_media(self, folder: str) -> List[str]:
        """Scan folder for supported media files."""
        files = []
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    files.append(filepath)
        return sorted(files)

    def _on_files_selected(self, file_paths: List[str]):
        """Handle file selection (single or multiple)."""
        self.current_files = file_paths
        self.file_queue.add_files(file_paths)

        if len(file_paths) == 1:
            # Single file mode
            self.current_file = file_paths[0]
            self.drop_zone.set_file(file_paths[0])
            self.file_queue.setVisible(False)
            self.transcription_panel.set_input_file(file_paths[0])
            size_mb = os.path.getsize(file_paths[0]) / (1024 * 1024)
            self.stats_label.setText(
                f"📁 {os.path.basename(file_paths[0])}\n💾 {size_mb:.1f} MB"
            )
        else:
            # Batch mode
            self.current_file = ""
            self.drop_zone.set_files(file_paths)
            self.file_queue.setVisible(True)
            total_size = sum(os.path.getsize(f) for f in file_paths)
            size_mb = total_size / (1024 * 1024)
            self.stats_label.setText(
                f"📁 {len(file_paths)} files\n💾 {size_mb:.1f} MB total"
            )

        self.transcribe_btn.setEnabled(True)
        self.transcription_panel.clear()

    def _on_queue_changed(self, selected_files: List[str]):
        """Handle file queue selection changes."""
        self.current_files = selected_files
        self.transcribe_btn.setEnabled(len(selected_files) > 0)

    def _start_transcription(self):
        """Start the transcription process."""
        # Check if we have files to process
        files_to_process = self.current_files if self.current_files else (
            [self.current_file] if self.current_file else []
        )
        if not files_to_process:
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
            self._switch_page(1)
            return

        # Clear previous results
        self.transcription_panel.clear()

        # Update UI state
        self.transcribe_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.browse_folder_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        if len(files_to_process) == 1:
            self._start_single_transcription(files_to_process[0], api_key)
        else:
            self._start_batch_transcription(files_to_process, api_key)

    def _start_single_transcription(self, file_path: str, api_key: str):
        """Start single file transcription."""
        self.worker = TranscriptionWorker(
            input_file=file_path,
            api_key=api_key,
            num_threads=self.settings_panel.get_num_threads(),
            vad_threshold=self.settings_panel.get_vad_threshold(),
            context=self.settings_panel.get_context(),
            save_srt=self.settings_panel.get_save_srt(),
            tmp_dir=self.settings_panel.get_temp_dir(),
        )

        self.worker.progress.connect(self._on_progress)
        self.worker.status_update.connect(self._on_status_update)
        self.worker.segment_completed.connect(self._on_segment_completed)
        self.worker.finished_transcription.connect(self._on_transcription_finished)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_worker_finished)

        self.worker.start()

    def _start_batch_transcription(self, file_paths: List[str], api_key: str):
        """Start batch transcription for multiple files."""
        self.batch_worker = BatchTranscriptionWorker(
            input_files=file_paths,
            api_key=api_key,
            num_threads=self.settings_panel.get_num_threads(),
            vad_threshold=self.settings_panel.get_vad_threshold(),
            context=self.settings_panel.get_context(),
            save_srt=self.settings_panel.get_save_srt(),
            tmp_dir=self.settings_panel.get_temp_dir(),
        )

        self.batch_worker.file_started.connect(self._on_batch_file_started)
        self.batch_worker.file_progress.connect(self._on_batch_file_progress)
        self.batch_worker.file_completed.connect(self._on_batch_file_completed)
        self.batch_worker.file_error.connect(self._on_batch_file_error)
        self.batch_worker.batch_progress.connect(self._on_batch_progress)
        self.batch_worker.batch_finished.connect(self._on_batch_finished)
        self.batch_worker.finished.connect(self._on_worker_finished)

        self.batch_worker.start()

    def _cancel_transcription(self):
        """Cancel the ongoing transcription."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.stats_label.setText("⚠️ Cancelling...")
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.cancel()
            self.stats_label.setText("⚠️ Cancelling batch...")

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

    def _on_batch_file_started(self, file_idx: int, filename: str):
        """Handle batch file started."""
        self.file_queue.set_file_status(file_idx, FileQueueWidget.STATUS_PROCESSING)
        self.stats_label.setText(f"🔄 Processing {filename}...")

    def _on_batch_file_progress(self, file_idx: int, current: int, total: int, msg: str):
        """Handle batch file progress."""
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"File {file_idx + 1}: {current}% - {msg}")

    def _on_batch_file_completed(self, file_idx: int, text: str, lang: str, segs: list):
        """Handle batch file completed."""
        self.file_queue.set_file_status(file_idx, FileQueueWidget.STATUS_DONE)
        self.transcription_panel.add_batch_result(file_idx, text, lang, segs)

    def _on_batch_file_error(self, file_idx: int, error_msg: str):
        """Handle batch file error."""
        self.file_queue.set_file_status(file_idx, FileQueueWidget.STATUS_ERROR)

    def _on_batch_progress(self, completed: int, total: int):
        """Handle overall batch progress."""
        pct = int((completed / total) * 100)
        self.stats_label.setText(f"📊 Batch: {completed}/{total} files\n({pct}% complete)")

    def _on_batch_finished(self, results: list):
        """Handle batch transcription finished."""
        success = sum(1 for r in results if not r.get("error"))
        failed = len(results) - success
        self.stats_label.setText(f"✅ Batch done!\n{success} succeeded, {failed} failed")
        self.transcription_panel.set_batch_complete(results)

    def _on_error(self, error_msg: str):
        """Handle transcription error."""
        QMessageBox.critical(self, "Transcription Error", error_msg)
        self.stats_label.setText(f"❌ Error occurred")

    def _on_worker_finished(self):
        """Reset UI after worker finishes."""
        self.transcribe_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.browse_folder_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.worker = None
        self.batch_worker = None

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
