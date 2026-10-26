# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : info_bar.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from config.config_loader import get as _get_config
from ui.utils import theme


class InfoBar(QWidget):
    """Bottom-left information bar"""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        # A plain QWidget subclass does not paint its stylesheet
        # background unless WA_StyledBackground is set: without it the
        # default light window color showed through the layout's left
        # margin (light square at the bottom-left corner of the window)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            background-color: {theme.BG_SURFACE};
            border-top: 1px solid {theme.BORDER_COLOR};
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        self.info_label = QLabel()
        self.info_label.setStyleSheet(
            f"font-size: {theme.MENU_FONT_SIZE_PX}px; color: {theme.TEXT_SECONDARY};")
        layout.addWidget(self.info_label)
        self.clear()

    def show_message(self, message: str):
        """Displays a message in the information bar."""
        self.info_label.setText(message)

    def clear(self):
        """Resets the information bar to its default (empty) message."""
        self.info_label.setText(_get_config("info_bar_default_message", ""))
