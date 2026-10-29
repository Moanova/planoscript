# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : tab_bar.py
# Version      : 1
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Tab bar for switching between workspaces (TSK07, SU009).

Displays one tab button per workspace ('Events', 'Agents') and emits
currentChanged(name) when the user activates a tab. Single instance
placed above the stacked workspace area (single source of truth for
the active tab).
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

from ui.utils import theme


class TabBar(QWidget):
    """Horizontal bar of workspace tabs."""

    HEIGHT = 40
    # Charter 98: both tabs share the exact same neutral appearance
    # (surface, border, secondary text); no dedicated active marker.
    STYLESHEET = f"""
        QWidget#TabBar {{
            background-color: {theme.BG_PRIMARY};
            border-bottom: 1px solid {theme.BORDER_COLOR};
        }}
        QPushButton {{
            background-color: {theme.BG_SURFACE};
            color: {theme.TEXT_SECONDARY};
            border: 1px solid {theme.BORDER_COLOR};
            border-radius: 3px;
            padding: 0 20px;
            margin: 4px 2px;
            font-family: "{theme.FONT_FAMILY}", system-ui, sans-serif;
            font-size: {theme.MENU_FONT_SIZE_PX}px;
            text-align: center;
        }}
        QPushButton:hover {{
            color: {theme.TEXT_PRIMARY};
            border: 1px solid {theme.HOVER_COLOR};
        }}
        QPushButton:checked {{
            background-color: {theme.BG_SURFACE};
            color: {theme.TEXT_PRIMARY};
            border: 1px solid {theme.BORDER_COLOR};
            font-weight: bold;
        }}
    """

    currentChanged = Signal(str)

    def __init__(self, tab_names, parent=None):
        """Create the tab bar.

        Args:
            tab_names: Ordered list of tab names (e.g. ['Events', 'Agents'])
        """
        super().__init__(parent)
        self.setObjectName("TabBar")
        self.setFixedHeight(self.HEIGHT)
        self.setStyleSheet(self.STYLESHEET)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tab_buttons = {}
        for name in tab_names:
            button = QPushButton(name)
            button.setCheckable(True)
            button.setFixedHeight(self.HEIGHT)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, n=name: self.setCurrentTab(n))
            layout.addWidget(button)
            self._tab_buttons[name] = button
        layout.addStretch()

    def setCurrentTab(self, name: str) -> None:
        """Activate a tab and emit currentChanged (no-op if already active)."""
        if name not in self._tab_buttons:
            return
        for tab_name, button in self._tab_buttons.items():
            button.setChecked(tab_name == name)
        self.currentChanged.emit(name)

    def currentTab(self) -> str:
        """Return the name of the active tab, or an empty string."""
        for name, button in self._tab_buttons.items():
            if button.isChecked():
                return name
        return ""

    def forceCurrentTab(self, name: str) -> None:
        """Set the active tab without emitting currentChanged.

        Used when restoring the default tab ('Events') on project
        opening, where the stacked widget already shows that page.
        """
        if name not in self._tab_buttons:
            return
        for tab_name, button in self._tab_buttons.items():
            button.setChecked(tab_name == name)
