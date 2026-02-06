"""
Main Window for Qwen3-ASR GUI
Modern minimal interface with unified single/batch transcription workflow
State-driven layout: Empty state shows drop zone, Populated state shows file table
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
    QStackedWidget,
    QMessageBox,
    QAbstractItemView,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QBrush, QColor

from .transcription_panel import TranscriptionPanel
from .settings_panel import SettingsPanel
from .worker_thread import TranscriptionWorker, BatchTranscriptionWorker
from .styles import get_stylesheet


SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".aac",  # Audio
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv",  # Video
}


class DropZone(QFrame):
    """Large drag-and-drop zone for empty state."""

    file_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the drop zone UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 60, 40, 60)

        # Main text
        self.text_label = QLabel("Drop audio/video files here")
        self.text_label.setObjectName("dropLabel")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.text_label.font()
        font.setPointSize(16)
        self.text_label.setFont(font)
        layout.addWidget(self.text_label)

        # Subtext
        self.subtext_label = QLabel("or click Browse to select files")
        self.subtext_label.setObjectName("subheading")
        self.subtext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtext_label)

        # Browse buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.browse_files_btn = QPushButton("Browse Files")
        self.browse_files_btn.setMinimumWidth(120)
        btn_layout.addWidget(self.browse_files_btn)

        self.browse_folder_btn = QPushButton("Browse Folder")
        self.browse_folder_btn.setMinimumWidth(120)
        btn_layout.addWidget(self.browse_folder_btn)

        layout.addLayout(btn_layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._is_supported_file(url.toLocalFile()) for url in urls):
                event.acceptProposedAction()
                self.setObjectName("dropZoneActive")
                self.style().unpolish(self)
                self.style().polish(self)

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self.setObjectName("dropZone")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        """Handle file drop."""
        self.setObjectName("dropZone")
        self.style().unpolish(self)
        self.style().polish(self)

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


class FileTableWidget(QFrame):
    """Enhanced file table with status, size, and progress columns."""

    file_selected = pyqtSignal(int, str)  # index, path
    files_changed = pyqtSignal(list)

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_ERROR = "error"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fileTableFrame")
        self.setAcceptDrops(True)
        self._files: List[dict] = []
        self._results: dict = {}  # file_idx -> result dict
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the file table UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("fileToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)

        # Add file button
        self.add_btn = QPushButton("+ Add Files")
        self.add_btn.setObjectName("ghostButton")
        toolbar_layout.addWidget(self.add_btn)

        # Add folder button
        self.add_folder_btn = QPushButton("+ Add Folder")
        self.add_folder_btn.setObjectName("ghostButton")
        toolbar_layout.addWidget(self.add_folder_btn)

        toolbar_layout.addStretch()

        # Stats label
        self.stats_label = QLabel("0 files")
        self.stats_label.setObjectName("subheading")
        toolbar_layout.addWidget(self.stats_label)

        toolbar_layout.addStretch()

        # Clear button
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setObjectName("ghostButton")
        self.clear_btn.clicked.connect(self.clear)
        toolbar_layout.addWidget(self.clear_btn)

        layout.addWidget(toolbar)

        # File tree widget
        self.tree = QTreeWidget()
        self.tree.setObjectName("fileTree")
        self.tree.setHeaderLabels(["Filename", "Status", "Size", "Progress"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemClicked.connect(self._on_item_clicked)

        # Configure columns
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 80)
        self.tree.setColumnWidth(3, 100)

        layout.addWidget(self.tree, 1)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter on the table area."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._is_supported_file(url.toLocalFile()) for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop on the table area."""
        urls = event.mimeData().urls()
        if urls:
            valid_files = [
                url.toLocalFile() for url in urls
                if self._is_supported_file(url.toLocalFile())
            ]
            if valid_files:
                self.add_files(valid_files)

    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in SUPPORTED_EXTENSIONS

    def add_files(self, file_paths: List[str]):
        """Add files to the table."""
        for path in file_paths:
            if not any(f["path"] == path for f in self._files):
                size = os.path.getsize(path) if os.path.exists(path) else 0
                self._files.append({
                    "path": path,
                    "size": size,
                    "status": self.STATUS_PENDING,
                    "progress": 0,
                })
        self._refresh_table()
        self._update_stats()
        self.files_changed.emit(self.get_all_files())

        # Auto-select first file if none selected
        if self.tree.currentItem() is None and self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
            self._on_item_clicked(self.tree.topLevelItem(0), 0)

    def get_all_files(self) -> List[str]:
        """Return all file paths."""
        return [f["path"] for f in self._files]

    def get_file_count(self) -> int:
        """Return number of files."""
        return len(self._files)

    def set_file_status(self, index: int, status: str):
        """Update status for a file by index."""
        if 0 <= index < len(self._files):
            self._files[index]["status"] = status
            self._update_item(index)

    def set_file_progress(self, index: int, progress: int):
        """Update progress for a file by index."""
        if 0 <= index < len(self._files):
            self._files[index]["progress"] = progress
            self._update_item(index)

    def set_file_result(self, index: int, result: dict):
        """Store result for a file."""
        self._results[index] = result

    def get_file_result(self, index: int) -> Optional[dict]:
        """Get stored result for a file."""
        return self._results.get(index)

    def get_all_results(self) -> dict:
        """Get all stored results."""
        return self._results

    def clear(self):
        """Clear all files from the table."""
        self._files.clear()
        self._results.clear()
        self.tree.clear()
        self._update_stats()
        self.files_changed.emit([])

    def reset_statuses(self):
        """Reset all file statuses to pending."""
        for f in self._files:
            f["status"] = self.STATUS_PENDING
            f["progress"] = 0
        self._results.clear()
        self._refresh_table()

    def _update_stats(self):
        """Update stats label."""
        count = len(self._files)
        if count == 0:
            self.stats_label.setText("0 files")
        else:
            total_size = sum(f["size"] for f in self._files)
            size_str = self._format_size(total_size)
            done = sum(1 for f in self._files if f["status"] == self.STATUS_DONE)
            if done > 0:
                self.stats_label.setText(f"{done}/{count} files ({size_str})")
            else:
                self.stats_label.setText(f"{count} files ({size_str})")

    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        if size_bytes >= 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        elif size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes} B"

    def _refresh_table(self):
        """Refresh the entire table."""
        self.tree.clear()
        for i, f in enumerate(self._files):
            item = self._create_item(i, f)
            self.tree.addTopLevelItem(item)

    def _update_item(self, index: int):
        """Update a single item in the table."""
        item = self.tree.topLevelItem(index)
        if item and index < len(self._files):
            f = self._files[index]
            status_text, status_color = self._get_status_display(f["status"])
            item.setText(1, status_text)
            item.setForeground(1, QBrush(QColor(status_color)))
            item.setText(3, f"{f['progress']}%" if f["progress"] > 0 else "")
            self._update_stats()

    def _create_item(self, index: int, file_info: dict) -> QTreeWidgetItem:
        """Create a tree item for a file."""
        filename = os.path.basename(file_info["path"])
        status_text, status_color = self._get_status_display(file_info["status"])
        size_str = self._format_size(file_info["size"])
        progress = f"{file_info['progress']}%" if file_info["progress"] > 0 else ""

        item = QTreeWidgetItem([filename, status_text, size_str, progress])
        item.setData(0, Qt.ItemDataRole.UserRole, index)
        item.setForeground(1, QBrush(QColor(status_color)))
        return item

    def _get_status_display(self, status: str) -> tuple:
        """Get status text and color."""
        status_map = {
            self.STATUS_PENDING: ("Pending", "#71717a"),
            self.STATUS_PROCESSING: ("Running", "#3b82f6"),
            self.STATUS_DONE: ("Done", "#22c55e"),
            self.STATUS_ERROR: ("Error", "#ef4444"),
        }
        return status_map.get(status, ("", "#71717a"))

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click - emit selection signal."""
        index = item.data(0, Qt.ItemDataRole.UserRole)
        if index is not None and index < len(self._files):
            self.file_selected.emit(index, self._files[index]["path"])

    def select_file(self, index: int):
        """Programmatically select a file by index."""
        if 0 <= index < self.tree.topLevelItemCount():
            item = self.tree.topLevelItem(index)
            self.tree.setCurrentItem(item)
            self._on_item_clicked(item, 0)


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
        self.setMinimumSize(900, 600)
        self.resize(1100, 750)

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
        # Sidebar (narrower, cleaner)
        # ─────────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(16)

        # Logo
        logo = QLabel("Qwen3-ASR")
        logo.setObjectName("logo")
        sidebar_layout.addWidget(logo)

        # Version
        version = QLabel("Toolkit v1.0")
        version.setObjectName("version")
        sidebar_layout.addWidget(version)

        sidebar_layout.addSpacing(16)

        # Navigation buttons
        self.nav_transcribe_btn = QPushButton("Transcribe")
        self.nav_transcribe_btn.setObjectName("navButton")
        self.nav_transcribe_btn.setCheckable(True)
        self.nav_transcribe_btn.setChecked(True)
        self.nav_transcribe_btn.clicked.connect(lambda: self._switch_page(0))
        sidebar_layout.addWidget(self.nav_transcribe_btn)

        self.nav_settings_btn = QPushButton("Settings")
        self.nav_settings_btn.setObjectName("navButton")
        self.nav_settings_btn.setCheckable(True)
        self.nav_settings_btn.clicked.connect(lambda: self._switch_page(1))
        sidebar_layout.addWidget(self.nav_settings_btn)

        sidebar_layout.addStretch()

        # Status card
        self.status_frame = QFrame()
        self.status_frame.setObjectName("card")
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(12, 12, 12, 12)
        status_layout.setSpacing(4)

        self.stats_label = QLabel("Ready")
        self.stats_label.setObjectName("subheading")
        self.stats_label.setWordWrap(True)
        status_layout.addWidget(self.stats_label)

        sidebar_layout.addWidget(self.status_frame)

        main_layout.addWidget(sidebar)

        # ─────────────────────────────────────────────────────────────
        # Main Content Area
        # ─────────────────────────────────────────────────────────────
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(0)

        # Stacked widget for pages
        self.page_stack = QStackedWidget()

        # ═══════════════════════════════════════════════════════════
        # Page 0: Transcription - State-Driven Layout
        # ═══════════════════════════════════════════════════════════
        transcribe_page = QWidget()
        transcribe_layout = QVBoxLayout(transcribe_page)
        transcribe_layout.setContentsMargins(0, 0, 0, 0)
        transcribe_layout.setSpacing(0)

        # State stack: Empty state vs Populated state
        self.state_stack = QStackedWidget()

        # ─── Empty State: Large Drop Zone ───
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_files_selected)
        self.drop_zone.browse_files_btn.clicked.connect(self._browse_files)
        self.drop_zone.browse_folder_btn.clicked.connect(self._browse_folder)
        self.state_stack.addWidget(self.drop_zone)

        # ─── Populated State: File Table + Result Panel ───
        populated_widget = QWidget()
        populated_layout = QVBoxLayout(populated_widget)
        populated_layout.setContentsMargins(0, 0, 0, 0)
        populated_layout.setSpacing(0)

        # Splitter for file table and result panel
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)

        # File table (top)
        self.file_table = FileTableWidget()
        self.file_table.file_selected.connect(self._on_file_selected)
        self.file_table.files_changed.connect(self._on_files_changed)
        self.file_table.add_btn.clicked.connect(self._browse_files)
        self.file_table.add_folder_btn.clicked.connect(self._browse_folder)
        self.main_splitter.addWidget(self.file_table)

        # Result panel (bottom)
        self.transcription_panel = TranscriptionPanel()
        self.main_splitter.addWidget(self.transcription_panel)

        # Set initial splitter sizes (40% table, 60% results)
        self.main_splitter.setSizes([300, 450])

        populated_layout.addWidget(self.main_splitter, 1)

        # ─── Footer Control Bar ───
        footer = QFrame()
        footer.setObjectName("footerBar")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 10, 12, 10)
        footer_layout.setSpacing(12)

        # Global progress
        self.progress_label = QLabel("Ready")
        self.progress_label.setObjectName("subheading")
        footer_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setVisible(False)
        footer_layout.addWidget(self.progress_bar)

        footer_layout.addStretch()

        # Control buttons
        self.cancel_btn = QPushButton("Stop")
        self.cancel_btn.setObjectName("dangerButton")
        self.cancel_btn.clicked.connect(self._cancel_transcription)
        self.cancel_btn.setVisible(False)
        footer_layout.addWidget(self.cancel_btn)

        self.export_btn = QPushButton("Export All")
        self.export_btn.clicked.connect(self._export_all_results)
        self.export_btn.setEnabled(False)
        footer_layout.addWidget(self.export_btn)

        self.transcribe_btn = QPushButton("Start Transcription")
        self.transcribe_btn.setObjectName("primaryButton")
        self.transcribe_btn.clicked.connect(self._start_transcription)
        self.transcribe_btn.setEnabled(False)
        footer_layout.addWidget(self.transcribe_btn)

        populated_layout.addWidget(footer)

        self.state_stack.addWidget(populated_widget)

        transcribe_layout.addWidget(self.state_stack)
        self.page_stack.addWidget(transcribe_page)

        # ═══════════════════════════════════════════════════════════
        # Page 1: Settings (with scroll area)
        # ═══════════════════════════════════════════════════════════
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QFrame.Shape.NoFrame)

        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(0, 0, 8, 0)
        settings_layout.setSpacing(16)

        settings_title = QLabel("Settings")
        settings_title.setObjectName("heading")
        settings_layout.addWidget(settings_title)

        self.settings_panel = SettingsPanel()
        settings_layout.addWidget(self.settings_panel, 1)

        settings_scroll.setWidget(settings_page)
        self.page_stack.addWidget(settings_scroll)

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
        """Handle file selection - switch to populated state."""
        self.current_files = file_paths
        self.file_table.add_files(file_paths)

        # Switch to populated state
        self.state_stack.setCurrentIndex(1)

        # Update sidebar stats
        count = len(self.file_table.get_all_files())
        self.stats_label.setText(f"{count} files loaded")

        self.transcribe_btn.setEnabled(True)
        self.transcription_panel.clear()

    def _on_files_changed(self, files: List[str]):
        """Handle file table changes."""
        self.current_files = files
        count = len(files)
        self.transcribe_btn.setEnabled(count > 0)

        if count == 0:
            # Switch back to empty state
            self.state_stack.setCurrentIndex(0)
            self.stats_label.setText("Ready")
        else:
            self.stats_label.setText(f"{count} files loaded")

    def _on_file_selected(self, index: int, path: str):
        """Handle file selection in table - show result in panel."""
        result = self.file_table.get_file_result(index)
        if result:
            # Show stored result
            self.transcription_panel.set_full_result(
                result.get("full_text", ""),
                result.get("language", ""),
                result.get("segments", [])
            )
            self.transcription_panel.set_input_file(path)
        else:
            # No result yet - show placeholder
            self.transcription_panel.clear()
            self.transcription_panel.set_input_file(path)
            filename = os.path.basename(path)
            self.transcription_panel.set_status(f"Selected: {filename}")

    def _start_transcription(self):
        """Start the transcription process."""
        files_to_process = self.file_table.get_all_files()
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

        # Reset statuses and clear panel
        self.file_table.reset_statuses()
        self.transcription_panel.clear()

        # Update UI state
        self.transcribe_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.file_table.add_btn.setEnabled(False)
        self.file_table.add_folder_btn.setEnabled(False)
        self.file_table.clear_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Always use batch mode (even for single file)
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
            self.progress_label.setText("Cancelling...")
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.cancel()
            self.progress_label.setText("Cancelling...")

    def _on_progress(self, current: int, total: int, message: str):
        """Handle progress update."""
        self.progress_bar.setValue(current)
        self.progress_label.setText(message)

    def _on_status_update(self, status: str):
        """Handle status text update."""
        self.progress_label.setText(status)
        self.transcription_panel.set_status(status)

    def _on_segment_completed(self, idx: int, text: str, start: float, end: float):
        """Handle individual segment completion."""
        self.transcription_panel.append_segment(idx, text, start, end)

    def _on_transcription_finished(self, full_text: str, language: str, segments: list):
        """Handle successful transcription completion."""
        self.transcription_panel.set_full_result(full_text, language, segments)
        self.progress_label.setText(f"Done - {len(segments)} segments")

    def _on_batch_file_started(self, file_idx: int, filename: str):
        """Handle batch file started."""
        self.file_table.set_file_status(file_idx, FileTableWidget.STATUS_PROCESSING)
        self.file_table.select_file(file_idx)
        self.progress_label.setText(f"Processing: {filename}")

    def _on_batch_file_progress(self, file_idx: int, current: int, total: int, msg: str):
        """Handle batch file progress."""
        self.progress_bar.setValue(current)
        self.file_table.set_file_progress(file_idx, current)

    def _on_batch_file_completed(self, file_idx: int, text: str, lang: str, segs: list):
        """Handle batch file completed."""
        self.file_table.set_file_status(file_idx, FileTableWidget.STATUS_DONE)
        self.file_table.set_file_progress(file_idx, 100)

        # Store result for later viewing
        self.file_table.set_file_result(file_idx, {
            "full_text": text,
            "language": lang,
            "segments": segs,
        })

        # Show result in panel
        self.transcription_panel.set_full_result(text, lang, segs)

    def _on_batch_file_error(self, file_idx: int, error_msg: str):
        """Handle batch file error."""
        self.file_table.set_file_status(file_idx, FileTableWidget.STATUS_ERROR)
        self.file_table.set_file_result(file_idx, {"error": error_msg})

    def _on_batch_progress(self, completed: int, total: int):
        """Handle overall batch progress."""
        pct = int((completed / total) * 100)
        self.progress_label.setText(f"Progress: {completed}/{total} files")
        self.stats_label.setText(f"{completed}/{total} done")

    def _on_batch_finished(self, results: list):
        """Handle batch transcription finished."""
        success = sum(1 for r in results if not r.get("error"))
        failed = len(results) - success
        self.progress_label.setText(f"Complete: {success} done, {failed} failed")
        self.stats_label.setText(f"{success}/{len(results)} done")
        self.export_btn.setEnabled(success > 0)

    def _on_error(self, error_msg: str):
        """Handle transcription error."""
        QMessageBox.critical(self, "Transcription Error", error_msg)
        self.progress_label.setText("Error occurred")

    def _on_worker_finished(self):
        """Reset UI after worker finishes."""
        self.transcribe_btn.setEnabled(True)
        self.file_table.add_btn.setEnabled(True)
        self.file_table.add_folder_btn.setEnabled(True)
        self.file_table.clear_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.worker = None
        self.batch_worker = None

    def _export_all_results(self):
        """Export all transcription results."""
        results = self.file_table.get_all_results()
        if not results:
            QMessageBox.information(self, "No Results", "No transcription results to export.")
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Export Folder",
            "",
        )
        if not folder:
            return

        exported = 0
        for idx, result in results.items():
            if result.get("error"):
                continue

            files = self.file_table.get_all_files()
            if idx < len(files):
                base_name = os.path.splitext(os.path.basename(files[idx]))[0]
                txt_path = os.path.join(folder, f"{base_name}.txt")

                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(f"{result.get('language', '')}\n")
                        f.write(f"{result.get('full_text', '')}\n")
                    exported += 1
                except Exception as e:
                    print(f"Error exporting {base_name}: {e}")

        QMessageBox.information(
            self,
            "Export Complete",
            f"Exported {exported} transcription(s) to:\n{folder}"
        )

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
