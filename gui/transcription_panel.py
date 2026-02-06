"""
Transcription Panel for Qwen3-ASR GUI
Displays transcription results with real-time updates and export capabilities
Master-detail pattern: shows result for currently selected file
"""

from typing import List, Dict, Optional
from datetime import timedelta

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
    QFileDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class TranscriptionPanel(QWidget):
    """Panel for displaying and exporting transcription results."""

    export_requested = pyqtSignal(str)  # format: "txt", "srt", "clipboard"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments: List[Dict] = []
        self.full_text: str = ""
        self.detected_language: str = ""
        self.input_file_path: str = ""
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.title_label = QLabel("Transcription Result")
        self.title_label.setObjectName("subheading")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Language badge
        self.language_badge = QLabel("")
        self.language_badge.setObjectName("badge")
        self.language_badge.setVisible(False)
        header_layout.addWidget(self.language_badge)

        layout.addLayout(header_layout)

        # Transcript text area
        self.transcript_edit = QTextEdit()
        self.transcript_edit.setReadOnly(True)
        self.transcript_edit.setPlaceholderText(
            "Select a file from the list above to view its transcription.\n\n"
            "Click 'Start Transcription' to begin processing."
        )

        # Set modern monospace font
        font = QFont("Cascadia Code", 13)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.transcript_edit.setFont(font)

        layout.addWidget(self.transcript_edit, 1)

        # Export buttons row
        export_layout = QHBoxLayout()
        export_layout.setSpacing(8)

        # Status info
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("subheading")
        export_layout.addWidget(self.status_label)

        export_layout.addStretch()

        # Copy to clipboard
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setToolTip("Copy transcription to clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        export_layout.addWidget(self.copy_btn)

        # Save as TXT
        self.save_txt_btn = QPushButton("Save TXT")
        self.save_txt_btn.setToolTip("Save as plain text file")
        self.save_txt_btn.clicked.connect(self._save_txt)
        self.save_txt_btn.setEnabled(False)
        export_layout.addWidget(self.save_txt_btn)

        # Save as SRT
        self.save_srt_btn = QPushButton("Save SRT")
        self.save_srt_btn.setToolTip("Save as subtitle file")
        self.save_srt_btn.clicked.connect(self._save_srt)
        self.save_srt_btn.setEnabled(False)
        export_layout.addWidget(self.save_srt_btn)

        layout.addLayout(export_layout)

    def set_input_file(self, file_path: str):
        """Store input file path for default save location."""
        self.input_file_path = file_path

    def clear(self):
        """Clear all transcription data."""
        self.segments = []
        self.full_text = ""
        self.detected_language = ""
        self.transcript_edit.clear()
        self.language_badge.setVisible(False)
        self.status_label.setText("Ready")
        self.title_label.setText("Transcription Result")
        self._set_export_buttons_enabled(False)

    def append_segment(self, index: int, text: str, start: float, end: float):
        """Add a single segment result (called in real-time as segments complete)."""
        segment = {
            "index": index,
            "text": text,
            "start": start,
            "end": end,
        }
        self.segments.append(segment)

        # Format with timestamp
        start_str = self._format_time(start)
        end_str = self._format_time(end)
        formatted = f"[{start_str} → {end_str}]\n{text}\n\n"

        # Append to display
        self.transcript_edit.append(formatted)

    def set_full_result(self, full_text: str, language: str, segments: List[Dict]):
        """Set the complete transcription result."""
        import os

        self.full_text = full_text
        self.detected_language = language
        self.segments = segments

        # Update title with filename if available
        if self.input_file_path:
            filename = os.path.basename(self.input_file_path)
            self.title_label.setText(f"Result: {filename}")

        # Update language badge
        if language:
            self.language_badge.setText(language)
            self.language_badge.setVisible(True)

        # Build formatted display
        display_text = ""
        for seg in sorted(segments, key=lambda x: x["index"]):
            start_str = self._format_time(seg["start"])
            end_str = self._format_time(seg["end"])
            display_text += f"[{start_str} → {end_str}]\n{seg['text']}\n\n"

        self.transcript_edit.setText(display_text.strip())

        # Enable export buttons
        self._set_export_buttons_enabled(True)
        self.status_label.setText(f"Complete - {len(segments)} segments")

    def set_status(self, status: str):
        """Update status label."""
        self.status_label.setText(status)

    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS.mmm or MM:SS.mmm."""
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        millis = int((seconds - total_seconds) * 1000)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
        return f"{minutes:02d}:{secs:02d}.{millis:03d}"

    def _set_export_buttons_enabled(self, enabled: bool):
        """Enable/disable export buttons."""
        self.copy_btn.setEnabled(enabled)
        self.save_txt_btn.setEnabled(enabled)
        self.save_srt_btn.setEnabled(enabled and len(self.segments) > 0)

    def _copy_to_clipboard(self):
        """Copy full text to system clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.full_text)
        self.status_label.setText("Copied to clipboard")
        self.export_requested.emit("clipboard")

    def _save_txt(self):
        """Save transcription as TXT file."""
        import os

        # Suggest default filename
        default_name = ""
        if self.input_file_path:
            base = os.path.splitext(self.input_file_path)[0]
            default_name = base + ".txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            default_name,
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"{self.detected_language}\n")
                    f.write(f"{self.full_text}\n")
                self.status_label.setText(f"Saved to {os.path.basename(file_path)}")
                self.export_requested.emit("txt")
            except Exception as e:
                self.status_label.setText(f"Save failed: {str(e)}")

    def _save_srt(self):
        """Save transcription as SRT subtitle file."""
        import os

        try:
            import srt
        except ImportError:
            self.status_label.setText("srt module not installed")
            return

        # Suggest default filename
        default_name = ""
        if self.input_file_path:
            base = os.path.splitext(self.input_file_path)[0]
            default_name = base + ".srt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Subtitles",
            default_name,
            "Subtitle Files (*.srt);;All Files (*)",
        )

        if file_path:
            try:
                subtitles = []
                for seg in sorted(self.segments, key=lambda x: x["index"]):
                    subtitles.append(
                        srt.Subtitle(
                            index=seg["index"] + 1,
                            start=timedelta(seconds=seg["start"]),
                            end=timedelta(seconds=seg["end"]),
                            content=seg["text"],
                        )
                    )

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(srt.compose(subtitles))

                self.status_label.setText(f"Saved to {os.path.basename(file_path)}")
                self.export_requested.emit("srt")
            except Exception as e:
                self.status_label.setText(f"Save failed: {str(e)}")
