#!/usr/bin/env python3
"""
Qwen3-ASR GUI Launcher
Premium graphical interface for the Qwen3-ASR Toolkit
"""

import sys
import os

# Add project root to path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow


def main():
    """Launch the Qwen3-ASR GUI application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Qwen3-ASR Toolkit")
    app.setOrganizationName("QwenLM")
    app.setApplicationVersion("1.0.0")

    # Set default font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Create main window
    window = MainWindow()

    # Load configuration from .asr_env if exists
    env_file = os.path.join(project_root, ".asr_env")
    window.load_config(env_file)

    # Show window
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
