"""
Settings Panel for Qwen3-ASR GUI
Configuration interface for API key, threads, VAD threshold, and output options
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSlider,
    QCheckBox,
    QFrame,
    QGroupBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsPanel(QWidget):
    """Configuration panel for transcription settings."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_key: str = ""
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # ─────────────────────────────────────────────────────────────
        # API Key Section
        # ─────────────────────────────────────────────────────────────
        api_group = QGroupBox("API Configuration")
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(12)

        # API key row with inline status
        api_row = QHBoxLayout()
        api_row.setSpacing(12)

        api_label = QLabel("DashScope API Key")
        api_label.setMinimumWidth(130)
        api_row.addWidget(api_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        api_row.addWidget(self.api_key_input, 1)

        self.toggle_visibility_btn = QPushButton("Show")
        self.toggle_visibility_btn.setObjectName("ghostButton")
        self.toggle_visibility_btn.setFixedWidth(60)
        self.toggle_visibility_btn.setCheckable(True)
        self.toggle_visibility_btn.toggled.connect(self._toggle_api_visibility)
        self.toggle_visibility_btn.setToolTip("Show/hide API key")
        api_row.addWidget(self.toggle_visibility_btn)

        api_layout.addLayout(api_row)

        # Status row with link
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        self.api_status = QLabel("Not configured")
        self.api_status.setObjectName("apiStatusLabel")
        status_row.addWidget(self.api_status)

        status_row.addStretch()

        api_link = QLabel('<a href="https://dashscope.console.aliyun.com/apiKey" style="color: #3b82f6;">Get API Key</a>')
        api_link.setOpenExternalLinks(True)
        api_link.setObjectName("linkLabel")
        status_row.addWidget(api_link)

        api_layout.addLayout(status_row)

        layout.addWidget(api_group)

        # ─────────────────────────────────────────────────────────────
        # Processing Settings
        # ─────────────────────────────────────────────────────────────
        processing_group = QGroupBox("Processing Settings")
        processing_layout = QVBoxLayout(processing_group)
        processing_layout.setSpacing(16)

        # Thread count
        thread_layout = QHBoxLayout()
        thread_layout.setSpacing(12)

        thread_label = QLabel("Parallel Threads")
        thread_label.setMinimumWidth(120)
        thread_layout.addWidget(thread_label)

        self.thread_slider = QSlider(Qt.Orientation.Horizontal)
        self.thread_slider.setMinimum(1)
        self.thread_slider.setMaximum(16)
        self.thread_slider.setValue(4)
        self.thread_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.thread_slider.setTickInterval(1)
        self.thread_slider.valueChanged.connect(self._on_thread_changed)
        thread_layout.addWidget(self.thread_slider, 1)

        self.thread_value_label = QLabel("4")
        self.thread_value_label.setMinimumWidth(30)
        self.thread_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thread_layout.addWidget(self.thread_value_label)

        processing_layout.addLayout(thread_layout)

        # VAD threshold
        vad_layout = QHBoxLayout()
        vad_layout.setSpacing(12)

        vad_label = QLabel("Segment Duration (s)")
        vad_label.setMinimumWidth(120)
        vad_label.setToolTip("Target duration for each audio segment (VAD-based splitting)")
        vad_layout.addWidget(vad_label)

        self.vad_spinbox = QSpinBox()
        self.vad_spinbox.setMinimum(30)
        self.vad_spinbox.setMaximum(180)
        self.vad_spinbox.setValue(120)
        self.vad_spinbox.setSuffix("s")
        self.vad_spinbox.valueChanged.connect(lambda: self.settings_changed.emit())
        vad_layout.addWidget(self.vad_spinbox)

        vad_layout.addStretch()

        processing_layout.addLayout(vad_layout)

        # Context hint
        context_layout = QVBoxLayout()
        context_layout.setSpacing(8)

        context_label = QLabel("Recognition Context (Optional)")
        context_label.setToolTip("Provide domain-specific terms to improve recognition accuracy")
        context_layout.addWidget(context_label)

        self.context_input = QLineEdit()
        self.context_input.setPlaceholderText("e.g., Qwen-ASR, DashScope, FFmpeg...")
        self.context_input.textChanged.connect(lambda: self.settings_changed.emit())
        context_layout.addWidget(self.context_input)

        processing_layout.addLayout(context_layout)

        layout.addWidget(processing_group)

        # ─────────────────────────────────────────────────────────────
        # Output Settings
        # ─────────────────────────────────────────────────────────────
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(16)

        # Export formats section
        format_label = QLabel("Auto-save Formats")
        format_label.setObjectName("settingLabel")
        output_layout.addWidget(format_label)

        # Format checkboxes in horizontal layout
        format_row = QHBoxLayout()
        format_row.setSpacing(20)

        self.save_txt_checkbox = QCheckBox("TXT")
        self.save_txt_checkbox.setChecked(True)
        self.save_txt_checkbox.setToolTip("Plain text transcription")
        format_row.addWidget(self.save_txt_checkbox)

        self.save_srt_checkbox = QCheckBox("SRT")
        self.save_srt_checkbox.setChecked(False)
        self.save_srt_checkbox.setToolTip("Subtitle file with timestamps")
        format_row.addWidget(self.save_srt_checkbox)

        self.save_json_checkbox = QCheckBox("JSON")
        self.save_json_checkbox.setChecked(False)
        self.save_json_checkbox.setToolTip("Structured data with segments")
        format_row.addWidget(self.save_json_checkbox)

        format_row.addStretch()
        output_layout.addLayout(format_row)

        # Temp directory
        temp_label = QLabel("Cache Directory")
        temp_label.setObjectName("settingLabel")
        output_layout.addWidget(temp_label)

        temp_row = QHBoxLayout()
        temp_row.setSpacing(10)

        self.temp_dir_input = QLineEdit()
        self.temp_dir_input.setPlaceholderText(os.path.join(os.path.expanduser("~"), "qwen3-asr-cache"))
        self.temp_dir_input.setText(os.path.join(os.path.expanduser("~"), "qwen3-asr-cache"))
        temp_row.addWidget(self.temp_dir_input, 1)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_temp_dir)
        temp_row.addWidget(browse_btn)

        output_layout.addLayout(temp_row)

        layout.addWidget(output_group)

        # Spacer
        layout.addStretch()

    def _on_api_key_changed(self, text: str):
        """Handle API key input change."""
        self._api_key = text.strip()
        if self._api_key:
            # Show masked key length
            key_len = len(self._api_key)
            self.api_status.setText(f"Configured ({key_len} chars)")
            self.api_status.setStyleSheet("color: #22c55e;")
        else:
            self.api_status.setText("Not configured")
            self.api_status.setStyleSheet("color: #71717a;")
        self.settings_changed.emit()

    def _on_thread_changed(self, value: int):
        """Handle thread slider change."""
        self.thread_value_label.setText(str(value))
        self.settings_changed.emit()

    def _toggle_api_visibility(self, checked: bool):
        """Toggle API key visibility."""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_btn.setText("Show")

    def _browse_temp_dir(self):
        """Open folder browser for temp directory."""
        current = self.temp_dir_input.text() or os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Cache Directory",
            current,
        )
        if folder:
            self.temp_dir_input.setText(folder)
            self.settings_changed.emit()

    def set_api_key(self, api_key: str):
        """Set API key programmatically (e.g., from .asr_env)."""
        self._api_key = api_key
        self.api_key_input.setText(api_key)

    def get_api_key(self) -> str:
        """Get current API key."""
        return self._api_key

    def get_num_threads(self) -> int:
        """Get thread count setting."""
        return self.thread_slider.value()

    def get_vad_threshold(self) -> int:
        """Get VAD segment threshold in seconds."""
        return self.vad_spinbox.value()

    def get_context(self) -> str:
        """Get recognition context hint."""
        return self.context_input.text().strip()

    def get_save_srt(self) -> bool:
        """Check if SRT auto-save is enabled."""
        return self.save_srt_checkbox.isChecked()

    def get_save_json(self) -> bool:
        """Check if JSON auto-save is enabled."""
        return self.save_json_checkbox.isChecked()

    def get_save_txt(self) -> bool:
        """Check if TXT auto-save is enabled."""
        return self.save_txt_checkbox.isChecked()

    def get_temp_dir(self) -> str:
        """Get temp directory path."""
        return self.temp_dir_input.text() or os.path.join(os.path.expanduser("~"), "qwen3-asr-cache")
