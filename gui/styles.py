"""
Premium QSS Stylesheet for Qwen3-ASR GUI
Glassmorphism-inspired dark theme with smooth gradients and micro-animations
"""

# Color Palette
COLORS = {
    "bg_primary": "#0d1117",
    "bg_secondary": "#161b22",
    "bg_tertiary": "#21262d",
    "bg_card": "#1c2128",
    "accent_primary": "#58a6ff",
    "accent_secondary": "#a371f7",
    "accent_gradient_start": "#58a6ff",
    "accent_gradient_end": "#a371f7",
    "text_primary": "#f0f6fc",
    "text_secondary": "#8b949e",
    "text_muted": "#6e7681",
    "success": "#3fb950",
    "warning": "#d29922",
    "error": "#f85149",
    "border": "#30363d",
    "border_light": "#484f58",
    "hover": "#1f6feb",
    "pressed": "#388bfd",
}

# Premium Dark Theme Stylesheet
DARK_THEME = f"""
/* ═══════════════════════════════════════════════════════════════
   GLOBAL STYLES
   ═══════════════════════════════════════════════════════════════ */

QWidget {{
    background-color: {COLORS["bg_primary"]};
    color: {COLORS["text_primary"]};
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 14px;
}}

QMainWindow {{
    background-color: {COLORS["bg_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR / NAVIGATION
   ═══════════════════════════════════════════════════════════════ */

QFrame#sidebar {{
    background-color: {COLORS["bg_secondary"]};
    border-right: 1px solid {COLORS["border"]};
    border-radius: 0px;
}}

QLabel#logo {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS["accent_primary"]};
    padding: 20px;
}}

QLabel#version {{
    color: {COLORS["text_muted"]};
    font-size: 11px;
}}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS - Primary Action
   ═══════════════════════════════════════════════════════════════ */

QPushButton {{
    background-color: {COLORS["bg_tertiary"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {COLORS["border"]};
    border-color: {COLORS["border_light"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["bg_secondary"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_tertiary"]};
    color: {COLORS["text_muted"]};
    border-color: {COLORS["border"]};
}}

QPushButton#primaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS["accent_primary"]},
        stop:1 {COLORS["accent_secondary"]});
    color: white;
    border: none;
    font-weight: 600;
    padding: 12px 28px;
}}

QPushButton#primaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS["hover"]},
        stop:1 {COLORS["accent_secondary"]});
}}

QPushButton#primaryButton:disabled {{
    background: {COLORS["bg_tertiary"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#dangerButton {{
    background-color: {COLORS["error"]};
    color: white;
    border: none;
}}

QPushButton#dangerButton:hover {{
    background-color: #da3633;
}}

/* ═══════════════════════════════════════════════════════════════
   DROP ZONE
   ═══════════════════════════════════════════════════════════════ */

QFrame#dropZone {{
    background-color: {COLORS["bg_card"]};
    border: 2px dashed {COLORS["border_light"]};
    border-radius: 16px;
    min-height: 200px;
}}

QFrame#dropZone:hover {{
    border-color: {COLORS["accent_primary"]};
    background-color: rgba(88, 166, 255, 0.05);
}}

QFrame#dropZoneActive {{
    border-color: {COLORS["accent_primary"]};
    border-style: solid;
    background-color: rgba(88, 166, 255, 0.1);
}}

QLabel#dropLabel {{
    color: {COLORS["text_secondary"]};
    font-size: 16px;
}}

QLabel#dropIcon {{
    font-size: 48px;
    color: {COLORS["text_muted"]};
}}

/* ═══════════════════════════════════════════════════════════════
   TEXT AREAS / TRANSCRIPT
   ═══════════════════════════════════════════════════════════════ */

QTextEdit, QPlainTextEdit {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 16px;
    font-family: "Cascadia Code", "Consolas", "Microsoft YaHei", monospace;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: {COLORS["accent_primary"]};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS["accent_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   INPUT FIELDS
   ═══════════════════════════════════════════════════════════════ */

QLineEdit {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
}}

QLineEdit:focus {{
    border-color: {COLORS["accent_primary"]};
    background-color: {COLORS["bg_tertiary"]};
}}

QLineEdit:disabled {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_muted"]};
}}

/* ═══════════════════════════════════════════════════════════════
   SLIDERS
   ═══════════════════════════════════════════════════════════════ */

QSlider::groove:horizontal {{
    height: 6px;
    background: {COLORS["bg_tertiary"]};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {COLORS["accent_primary"]};
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS["hover"]};
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS["accent_primary"]},
        stop:1 {COLORS["accent_secondary"]});
    border-radius: 3px;
}}

/* ═══════════════════════════════════════════════════════════════
   SPINBOX
   ═══════════════════════════════════════════════════════════════ */

QSpinBox {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLORS["bg_tertiary"]};
    border: none;
    width: 20px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLORS["border"]};
}}

/* ═══════════════════════════════════════════════════════════════
   CHECKBOX
   ═══════════════════════════════════════════════════════════════ */

QCheckBox {{
    spacing: 10px;
    color: {COLORS["text_primary"]};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid {COLORS["border"]};
    background-color: {COLORS["bg_card"]};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS["accent_primary"]};
    border-color: {COLORS["accent_primary"]};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS["accent_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════ */

QProgressBar {{
    background-color: {COLORS["bg_tertiary"]};
    border: none;
    border-radius: 8px;
    height: 12px;
    text-align: center;
    color: {COLORS["text_primary"]};
    font-size: 11px;
    font-weight: 600;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS["accent_primary"]},
        stop:1 {COLORS["accent_secondary"]});
    border-radius: 8px;
}}

/* ═══════════════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════════════ */

QLabel {{
    color: {COLORS["text_primary"]};
    background: transparent;
}}

QLabel#heading {{
    font-size: 20px;
    font-weight: 600;
    color: {COLORS["text_primary"]};
}}

QLabel#subheading {{
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}

QLabel#badge {{
    background-color: {COLORS["accent_primary"]};
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}}

QLabel#successBadge {{
    background-color: {COLORS["success"]};
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}}

QLabel#errorLabel {{
    color: {COLORS["error"]};
}}

/* ═══════════════════════════════════════════════════════════════
   CARDS / PANELS
   ═══════════════════════════════════════════════════════════════ */

QFrame#card {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 16px;
}}

QFrame#settingsCard {{
    background-color: {COLORS["bg_secondary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 20px;
}}

/* ═══════════════════════════════════════════════════════════════
   SCROLL BARS
   ═══════════════════════════════════════════════════════════════ */

QScrollBar:vertical {{
    background-color: {COLORS["bg_primary"]};
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["border_light"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["bg_primary"]};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS["border"]};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS["border_light"]};
}}

/* ═══════════════════════════════════════════════════════════════
   GROUP BOX
   ═══════════════════════════════════════════════════════════════ */

QGroupBox {{
    background-color: {COLORS["bg_secondary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding-top: 24px;
    margin-top: 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    color: {COLORS["text_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════════════════════ */

QToolTip {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}}

/* ═══════════════════════════════════════════════════════════════
   STATUS BAR
   ═══════════════════════════════════════════════════════════════ */

QStatusBar {{
    background-color: {COLORS["bg_secondary"]};
    border-top: 1px solid {COLORS["border"]};
    color: {COLORS["text_secondary"]};
    font-size: 12px;
    padding: 4px 12px;
}}

/* ═══════════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════════ */

QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    background-color: {COLORS["bg_card"]};
}}

QTabBar::tab {{
    background-color: {COLORS["bg_tertiary"]};
    color: {COLORS["text_secondary"]};
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["accent_primary"]};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS["border"]};
}}

/* ═══════════════════════════════════════════════════════════════
   COMBOBOX
   ═══════════════════════════════════════════════════════════════ */

QComboBox {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {COLORS["accent_primary"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS["text_secondary"]};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    selection-background-color: {COLORS["accent_primary"]};
    outline: none;
}}
"""

# Light Theme (Optional)
LIGHT_THEME = """
/* Light theme placeholder - can be expanded */
QWidget {
    background-color: #ffffff;
    color: #1f2328;
}
"""


def get_stylesheet(theme: str = "dark") -> str:
    """Return the stylesheet for the specified theme."""
    return DARK_THEME if theme == "dark" else LIGHT_THEME
