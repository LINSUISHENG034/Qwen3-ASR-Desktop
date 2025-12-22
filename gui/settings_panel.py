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
        api_group = QGroupBox("🔑 API Configuration")
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(12)

        api_desc = QLabel("Enter your DashScope API key for Qwen-ASR access")
        api_desc.setObjectName("subheading")
        api_layout.addWidget(api_desc)

        api_input_layout = QHBoxLayout()
        api_input_layout.setSpacing(10)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        api_input_layout.addWidget(self.api_key_input, 1)

        self.toggle_visibility_btn = QPushButton("👁")
        self.toggle_visibility_btn.setFixedWidth(40)
        self.toggle_visibility_btn.setCheckable(True)
        self.toggle_visibility_btn.toggled.connect(self._toggle_api_visibility)
        self.toggle_visibility_btn.setToolTip("Show/hide API key")
        api_input_layout.addWidget(self.toggle_visibility_btn)

        api_layout.addLayout(api_input_layout)

        # API status indicator
        self.api_status = QLabel("⚪ No API key configured")
        self.api_status.setObjectName("subheading")
        api_layout.addWidget(self.api_status)

        layout.addWidget(api_group)

        # ─────────────────────────────────────────────────────────────
        # Processing Settings
        # ─────────────────────────────────────────────────────────────
        processing_group = QGroupBox("⚙️ Processing Settings")
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
        output_group = QGroupBox("📁 Output Settings")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(12)

        # Auto-save options
        self.save_txt_checkbox = QCheckBox("Auto-save TXT file")
        self.save_txt_checkbox.setChecked(True)
        output_layout.addWidget(self.save_txt_checkbox)

        self.save_srt_checkbox = QCheckBox("Auto-save SRT subtitle file")
        self.save_srt_checkbox.setChecked(False)
        output_layout.addWidget(self.save_srt_checkbox)

        # Temp directory
        temp_layout = QHBoxLayout()
        temp_layout.setSpacing(10)

        temp_label = QLabel("Cache Directory")
        temp_layout.addWidget(temp_label)

        self.temp_dir_input = QLineEdit()
        self.temp_dir_input.setPlaceholderText(os.path.join(os.path.expanduser("~"), "qwen3-asr-cache"))
        self.temp_dir_input.setText(os.path.join(os.path.expanduser("~"), "qwen3-asr-cache"))
        temp_layout.addWidget(self.temp_dir_input, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_temp_dir)
        temp_layout.addWidget(browse_btn)

        output_layout.addLayout(temp_layout)

        layout.addWidget(output_group)

        # Spacer
        layout.addStretch()

    def _on_api_key_changed(self, text: str):
        """Handle API key input change."""
        self._api_key = text.strip()
        if self._api_key:
            self.api_status.setText("🟢 API key configured")
        else:
            self.api_status.setText("⚪ No API key configured")
        self.settings_changed.emit()

    def _on_thread_changed(self, value: int):
        """Handle thread slider change."""
        self.thread_value_label.setText(str(value))
        self.settings_changed.emit()

    def _toggle_api_visibility(self, checked: bool):
        """Toggle API key visibility."""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_btn.setText("👁")

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

    def get_temp_dir(self) -> str:
        """Get temp directory path."""
        return self.temp_dir_input.text() or os.path.join(os.path.expanduser("~"), "qwen3-asr-cache")
