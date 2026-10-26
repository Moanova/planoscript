# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : theme.py
# Version      : 1
# Date         : 24-10-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Dark theme helpers for Planoscript (TSK11).

Centralizes the dark palette from the UI charter
(docs/specification/98_layout_revision-FR.md) so that no color is
hard-coded in the UI code (AGENTS.md convention). Colors are read from
config.json via config_loader; the values below are the fallback
defaults matching the charter.

Qt stylesheets do not support CSS variables, so the stylesheet builders
below interpolate the configured values.
"""

from PySide6.QtGui import QColor

from config.config_loader import get as _get_config

# Palette (charter 98)
BG_PRIMARY = _get_config("bg_primary", "#1E1E1E")
BG_SURFACE = _get_config("bg_surface", "#2D2D2D")
BORDER_COLOR = _get_config("border_color", "#383838")
TEXT_PRIMARY = _get_config("text_primary", "#FFFFFF")
TEXT_SECONDARY = _get_config("text_secondary", "#CCCCCC")
STATE_COLOR = _get_config("state_color", "#E5C07B")
EVENT_COLOR = _get_config("event_color", "#D19A66")
ANCHOR_COLOR = _get_config("anchor_color", "#F0F0F0")
HOVER_COLOR = _get_config("hover_color", "#F0F0F0")
CONNECTION_COLOR = _get_config("connection_color", "#CCCCCC")
BADGE_BG_COLOR = _get_config("badge_bg_color", "#E5C07B")
BADGE_BORDER_COLOR = _get_config("badge_border_color", "#F0F0F0")
BADGE_TEXT_COLOR = _get_config("badge_text_color", "#1E1E1E")
MENU_HOVER_BG = _get_config("menu_hover_bg", "#383838")
ERROR_COLOR = _get_config("error_color", "#D19A66")
FOCUS_COLOR = _get_config("focus_color", "#383838")

# Typography (charter 98)
FONT_FAMILY = _get_config("node_font_family", "Segoe UI")
MENU_FONT_SIZE_PX = _get_config("menu_font_size_px", 12)
NODE_FONT_SIZE_PX = _get_config("node_font_size_px", 13)
NODE_LABEL_FONT_SIZE_PX = _get_config("node_label_font_size_px", 12)
NODE_TITLE_FONT_SIZE_PX = _get_config("node_title_font_size_px", 14)


def color(key: str, default: str) -> QColor:
    """Return a QColor from a config.json color key, with fallback."""
    return QColor(_get_config(key, default))


# -------------------------------------------------------------------------
# Stylesheet builders (Qt stylesheets have no CSS variables)
# -------------------------------------------------------------------------

MENU_BAR_STYLESHEET = f"""
    QMenuBar {{
        background-color: {BG_SURFACE};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
        color: {TEXT_PRIMARY};
    }}
    QMenuBar::item:selected {{
        background-color: {MENU_HOVER_BG};
        color: {TEXT_PRIMARY};
    }}
    QMenu {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
        padding: 4px;
        border: 1px solid {BORDER_COLOR};
    }}
    QMenu::item {{
        padding: 6px 20px 6px 10px;
    }}
    QMenu::item:selected {{
        background-color: {MENU_HOVER_BG};
        color: {TEXT_PRIMARY};
    }}
    QMenu::item:disabled {{
        color: #808080;
    }}
    QMenu::separator {{
        background-color: {BORDER_COLOR};
        height: 1px;
        margin: 4px 8px;
    }}
"""

# Context menus inherit the QMenu style when the stylesheet is set on the
# top-level widget; the same rules apply.
CONTEXT_MENU_STYLESHEET = f"""
    QMenu {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
        padding: 4px;
        border: 1px solid {BORDER_COLOR};
    }}
    QMenu::item {{
        padding: 6px 20px 6px 10px;
    }}
    QMenu::item:selected {{
        background-color: {MENU_HOVER_BG};
        color: {TEXT_PRIMARY};
    }}
    QMenu::item:disabled {{
        color: #808080;
    }}
    QMenu::separator {{
        background-color: {BORDER_COLOR};
        height: 1px;
        margin: 4px 8px;
    }}
"""

SCROLLBAR_STYLESHEET = f"""
    QScrollBar:horizontal {{
        height: 8px;
        background: {BG_SURFACE};
        border-radius: 4px;
        margin: 0px;
        border: none;
    }}
    QScrollBar:vertical {{
        width: 8px;
        background: {BG_SURFACE};
        border-radius: 4px;
        margin: 0px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER_COLOR};
        border-radius: 4px;
        min-width: 20px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER_COLOR};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:horizontal:hover,
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_SECONDARY};
    }}
    QScrollBar::handle:horizontal:pressed,
    QScrollBar::handle:horizontal:active,
    QScrollBar::handle:vertical:pressed,
    QScrollBar::handle:vertical:active {{
        background: {STATE_COLOR};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        background: {BG_SURFACE};
        border: none;
        height: 0px;
        width: 0px;
    }}
"""

# Application-wide stylesheet (set on the QApplication): global typography
# and the widgets that are not children of a themed window (message boxes,
# orphan popup menus).
APP_STYLESHEET = f"""
    QWidget {{
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
        color: {TEXT_PRIMARY};
    }}
    QMessageBox {{
        background-color: {BG_PRIMARY};
    }}
    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
    }}
    QMessageBox QPushButton {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        border-radius: 3px;
        padding: 4px 12px;
    }}
    QMessageBox QPushButton:hover {{
        border: 1px solid {ANCHOR_COLOR};
    }}
    QMessageBox QPushButton:pressed {{
        background-color: {MENU_HOVER_BG};
    }}
""" + CONTEXT_MENU_STYLESHEET

# Dark theme for the standard item views and controls used by the dialogs
# and the agents matrix (charter 98, point 14).
DIALOG_STYLESHEET = f"""
    QDialog {{
        background-color: {BG_PRIMARY};
    }}
    QLabel {{
        color: {TEXT_PRIMARY};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QLineEdit, QTextEdit, QComboBox {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        border-radius: 3px;
        padding: 2px 4px;
        selection-background-color: {STATE_COLOR};
        selection-color: {BG_PRIMARY};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {ANCHOR_COLOR};
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        selection-background-color: {MENU_HOVER_BG};
    }}
    QPushButton {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        border-radius: 3px;
        padding: 4px 12px;
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QPushButton:hover {{
        border: 1px solid {ANCHOR_COLOR};
    }}
    QPushButton:pressed {{
        background-color: {MENU_HOVER_BG};
    }}
    QPushButton:disabled {{
        color: #808080;
        border: 1px solid {BORDER_COLOR};
    }}
    QListWidget {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QListWidget::item:selected {{
        background-color: {MENU_HOVER_BG};
    }}
    QCheckBox {{
        color: {TEXT_PRIMARY};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {ANCHOR_COLOR};
        border-radius: 3px;
        background-color: {BG_SURFACE};
    }}
    QCheckBox::indicator:checked {{
        background-color: {STATE_COLOR};
        border: 1px solid {ANCHOR_COLOR};
    }}
    QTableWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        gridline-color: {BORDER_COLOR};
        border: 1px solid {BORDER_COLOR};
        selection-background-color: {MENU_HOVER_BG};
        selection-color: {TEXT_PRIMARY};
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QTableWidget::item {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
    }}
    QTableWidget::item:selected {{
        background-color: {MENU_HOVER_BG};
    }}
    QHeaderView::section {{
        background-color: {BG_SURFACE};
        color: {TEXT_SECONDARY};
        border: none;
        border-right: 1px solid {BORDER_COLOR};
        border-bottom: 1px solid {BORDER_COLOR};
        padding: 4px 6px;
        font-family: "{FONT_FAMILY}", system-ui, sans-serif;
        font-size: {MENU_FONT_SIZE_PX}px;
    }}
    QHeaderView::section:hover {{
        color: {TEXT_PRIMARY};
    }}
    QScrollBar:horizontal {{
        height: 8px;
        background: {BG_SURFACE};
        border-radius: 4px;
        margin: 0px;
        border: none;
    }}
    QScrollBar:vertical {{
        width: 8px;
        background: {BG_SURFACE};
        border-radius: 4px;
        margin: 0px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER_COLOR};
        border-radius: 4px;
        min-width: 20px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER_COLOR};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:horizontal:hover,
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_SECONDARY};
    }}
    QScrollBar::handle:horizontal:pressed,
    QScrollBar::handle:horizontal:active,
    QScrollBar::handle:vertical:pressed,
    QScrollBar::handle:vertical:active {{
        background: {STATE_COLOR};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        background: {BG_SURFACE};
        border: none;
        height: 0px;
        width: 0px;
    }}
"""
