"""
Premium QSS Stylesheet for Qwen3-ASR GUI
Modern minimal dark theme with clean typography and subtle depth
"""

# Color Palette - Modern Dark Mode (OLED-friendly)
COLORS = {
    # Backgrounds - layered depth
    "bg_base": "#0a0a0a",        # Deepest background
    "bg_primary": "#0f0f0f",     # Main background
    "bg_secondary": "#161616",   # Sidebar, elevated surfaces
    "bg_card": "#1a1a1a",        # Cards, panels
    "bg_elevated": "#1f1f1f",    # Hover states, elevated elements

    # Accent colors - blue gradient
    "accent_primary": "#3b82f6",   # Primary blue
    "accent_secondary": "#60a5fa", # Lighter blue
    "accent_hover": "#2563eb",     # Darker blue for hover

    # Text hierarchy
    "text_primary": "#fafafa",     # Primary text
    "text_secondary": "#a1a1aa",   # Secondary text
    "text_muted": "#71717a",       # Muted/disabled text

    # Semantic colors
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",

    # Borders
    "border": "#27272a",
    "border_light": "#3f3f46",
    "border_focus": "#3b82f6",
}

# Premium Dark Theme Stylesheet
DARK_THEME = f"""
/* ═══════════════════════════════════════════════════════════════
   GLOBAL STYLES
   ═══════════════════════════════════════════════════════════════ */

* {{
    outline: none;
}}

QWidget {{
    background-color: {COLORS["bg_primary"]};
    color: {COLORS["text_primary"]};
    font-family: "Segoe UI", "SF Pro Display", "Microsoft YaHei", sans-serif;
    font-size: 13px;
    selection-background-color: {COLORS["accent_primary"]};
    selection-color: white;
}}

QMainWindow {{
    background-color: {COLORS["bg_base"]};
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR / NAVIGATION
   ═══════════════════════════════════════════════════════════════ */

QFrame#sidebar {{
    background-color: {COLORS["bg_secondary"]};
    border-right: 1px solid {COLORS["border"]};
}}

QLabel#logo {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS["text_primary"]};
    padding: 0;
}}

QLabel#version {{
    color: {COLORS["text_muted"]};
    font-size: 11px;
}}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════ */

QPushButton {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 18px;
}}

QPushButton:hover {{
    background-color: {COLORS["bg_elevated"]};
    border-color: {COLORS["border_light"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["bg_secondary"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_muted"]};
    border-color: {COLORS["border"]};
}}

QPushButton:checked {{
    background-color: {COLORS["accent_primary"]};
    color: white;
    border-color: {COLORS["accent_primary"]};
}}

QPushButton#primaryButton {{
    background-color: {COLORS["accent_primary"]};
    color: white;
    border: none;
    font-weight: 600;
    padding: 10px 24px;
}}

QPushButton#primaryButton:hover {{
    background-color: {COLORS["accent_hover"]};
}}

QPushButton#primaryButton:disabled {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#dangerButton {{
    background-color: {COLORS["error"]};
    color: white;
    border: none;
}}

QPushButton#dangerButton:hover {{
    background-color: #dc2626;
}}

QPushButton#ghostButton {{
    background-color: transparent;
    border: none;
    color: {COLORS["text_secondary"]};
    padding: 6px 12px;
}}

QPushButton#ghostButton:hover {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
}}

QPushButton#navButton {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    color: {COLORS["text_secondary"]};
}}

QPushButton#navButton:hover {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["text_primary"]};
}}

QPushButton#navButton:checked {{
    background-color: {COLORS["bg_elevated"]};
    color: {COLORS["accent_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   DROP ZONE
   ═══════════════════════════════════════════════════════════════ */

QFrame#dropZone {{
    background-color: {COLORS["bg_card"]};
    border: 2px dashed {COLORS["border_light"]};
    border-radius: 16px;
    min-height: 300px;
}}

QFrame#dropZone:hover {{
    border-color: {COLORS["accent_primary"]};
    background-color: rgba(59, 130, 246, 0.05);
}}

QFrame#dropZoneActive {{
    border-color: {COLORS["accent_primary"]};
    border-style: solid;
    background-color: rgba(59, 130, 246, 0.1);
}}

QLabel#dropIcon {{
    color: {COLORS["text_muted"]};
}}

QLabel#dropLabel {{
    color: {COLORS["text_secondary"]};
    font-size: 14px;
}}

/* ═══════════════════════════════════════════════════════════════
   TEXT AREAS
   ═══════════════════════════════════════════════════════════════ */

QTextEdit, QPlainTextEdit {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 12px;
    font-family: "Cascadia Code", "JetBrains Mono", "Consolas", monospace;
    font-size: 13px;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS["border_focus"]};
}}

/* ═══════════════════════════════════════════════════════════════
   INPUT FIELDS
   ═══════════════════════════════════════════════════════════════ */

QLineEdit {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}}

QLineEdit:focus {{
    border-color: {COLORS["border_focus"]};
}}

QLineEdit:disabled {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_muted"]};
}}

/* ═══════════════════════════════════════════════════════════════
   SLIDERS
   ═══════════════════════════════════════════════════════════════ */

QSlider::groove:horizontal {{
    height: 4px;
    background: {COLORS["bg_elevated"]};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {COLORS["accent_primary"]};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS["accent_hover"]};
}}

QSlider::sub-page:horizontal {{
    background: {COLORS["accent_primary"]};
    border-radius: 2px;
}}

/* ═══════════════════════════════════════════════════════════════
   SPINBOX
   ═══════════════════════════════════════════════════════════════ */

QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS["bg_elevated"]};
    border: none;
    width: 18px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLORS["border_light"]};
}}

/* ═══════════════════════════════════════════════════════════════
   CHECKBOX - Modern Style
   ═══════════════════════════════════════════════════════════════ */

QCheckBox {{
    spacing: 8px;
    color: {COLORS["text_primary"]};
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {COLORS["border_light"]};
    background-color: {COLORS["bg_card"]};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS["accent_primary"]};
    border-color: {COLORS["accent_primary"]};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjAgNiA5IDE3IDQgMTIiPjwvcG9seWxpbmU+PC9zdmc+);
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS["accent_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════ */

QProgressBar {{
    background-color: {COLORS["bg_elevated"]};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: {COLORS["text_primary"]};
    font-size: 10px;
}}

QProgressBar::chunk {{
    background-color: {COLORS["accent_primary"]};
    border-radius: 4px;
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
    font-size: 13px;
    color: {COLORS["text_secondary"]};
}}

QLabel#badge {{
    background-color: {COLORS["accent_primary"]};
    color: white;
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#successBadge {{
    background-color: {COLORS["success"]};
    color: white;
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
}}

/* ═══════════════════════════════════════════════════════════════
   CARDS / PANELS
   ═══════════════════════════════════════════════════════════════ */

QFrame#card {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

QFrame#settingsCard {{
    background-color: {COLORS["bg_secondary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

/* ═══════════════════════════════════════════════════════════════
   SCROLL AREA
   ═══════════════════════════════════════════════════════════════ */

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ═══════════════════════════════════════════════════════════════
   SCROLL BARS
   ═══════════════════════════════════════════════════════════════ */

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["border_light"]};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["text_muted"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS["border_light"]};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS["text_muted"]};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}

/* ═══════════════════════════════════════════════════════════════
   LIST WIDGET
   ═══════════════════════════════════════════════════════════════ */

QListWidget {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 2px 0;
}}

QListWidget::item:selected {{
    background-color: {COLORS["bg_elevated"]};
}}

QListWidget::item:hover {{
    background-color: {COLORS["bg_elevated"]};
}}

/* ═══════════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════════ */

QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    background-color: {COLORS["bg_card"]};
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS["text_secondary"]};
    padding: 8px 16px;
    margin-right: 4px;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLORS["accent_primary"]};
    border-bottom: 2px solid {COLORS["accent_primary"]};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS["text_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   COMBOBOX
   ═══════════════════════════════════════════════════════════════ */

QComboBox {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    min-width: 80px;
}}

QComboBox:hover {{
    border-color: {COLORS["border_light"]};
}}

QComboBox:focus {{
    border-color: {COLORS["border_focus"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {COLORS["text_secondary"]};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    selection-background-color: {COLORS["accent_primary"]};
    outline: none;
    padding: 4px;
}}

/* ═══════════════════════════════════════════════════════════════
   GROUP BOX
   ═══════════════════════════════════════════════════════════════ */

QGroupBox {{
    background-color: {COLORS["bg_secondary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding-top: 20px;
    margin-top: 8px;
    font-weight: 500;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {COLORS["text_primary"]};
}}

/* ═══════════════════════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════════════════════ */

QToolTip {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ═══════════════════════════════════════════════════════════════
   SPLITTER
   ═══════════════════════════════════════════════════════════════ */

QSplitter::handle {{
    background-color: {COLORS["border"]};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* ═══════════════════════════════════════════════════════════════
   FILE TABLE / TREE WIDGET
   ═══════════════════════════════════════════════════════════════ */

QFrame#fileTableFrame {{
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

QFrame#fileToolbar {{
    background-color: {COLORS["bg_secondary"]};
    border-bottom: 1px solid {COLORS["border"]};
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

QTreeWidget#fileTree {{
    background-color: {COLORS["bg_card"]};
    border: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    outline: none;
}}

QTreeWidget#fileTree::item {{
    padding: 6px 8px;
    border-bottom: 1px solid {COLORS["border"]};
}}

QTreeWidget#fileTree::item:selected {{
    background-color: {COLORS["accent_primary"]};
    color: white;
}}

QTreeWidget#fileTree::item:hover:!selected {{
    background-color: {COLORS["bg_elevated"]};
}}

QHeaderView::section {{
    background-color: {COLORS["bg_secondary"]};
    color: {COLORS["text_secondary"]};
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {COLORS["border"]};
    font-weight: 500;
    font-size: 12px;
}}

/* ═══════════════════════════════════════════════════════════════
   FOOTER BAR
   ═══════════════════════════════════════════════════════════════ */

QFrame#footerBar {{
    background-color: {COLORS["bg_secondary"]};
    border-top: 1px solid {COLORS["border"]};
}}

/* ═══════════════════════════════════════════════════════════════
   SETTINGS PANEL
   ═══════════════════════════════════════════════════════════════ */

QLabel#settingLabel {{
    color: {COLORS["text_secondary"]};
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 4px;
}}

QLabel#apiStatusLabel {{
    color: {COLORS["text_muted"]};
    font-size: 12px;
}}

QLabel#linkLabel {{
    font-size: 12px;
}}

QLabel#linkLabel a {{
    color: {COLORS["accent_primary"]};
    text-decoration: none;
}}

QLabel#linkLabel a:hover {{
    text-decoration: underline;
}}
"""


def get_stylesheet(theme: str = "dark") -> str:
    """Return the stylesheet for the specified theme."""
    return DARK_THEME
