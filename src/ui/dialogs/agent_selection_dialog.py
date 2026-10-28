# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agent_selection_dialog.py
# Version      : 1
# Date         : 28-10-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
)

from core.models.data_model import Agent
from ui.utils import theme


class AgentSelectionDialog(QDialog):
    """Agent selection dialog (TSK13, FN031).

    Lists the agents of the project and returns the selected one.
    Used by the "Edit" and "Delete" entries of the
    "Project > Components... > Agent" submenu: the Ok button stays
    disabled until an agent is selected.
    """

    def __init__(self, agents, parent=None):
        super().__init__(parent)
        self._agents = list(agents)
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        self.setWindowTitle("Select Agent")
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout(self)
        # Dark theme (charter 98)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._selection_changed)
        self.layout.addWidget(self.list_widget, stretch=1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setFixedWidth(100)
        self.ok_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _refresh_list(self):
        self.list_widget.clear()
        for agent in self._agents:
            self.list_widget.addItem(agent.lb)

    def _selection_changed(self, current_row):
        self.ok_button.setEnabled(0 <= current_row < len(self._agents))

    def get_selected_agent(self):
        """Return the selected Agent, or None if there is no selection."""
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._agents):
            return self._agents[row]
        return None
