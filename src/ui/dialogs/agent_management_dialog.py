# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agent_management_dialog.py
# Version      : 1
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel
)

from core.services.project_service import ProjectService
from ui.utils import theme
from ui.dialogs.agent_dialog import AgentDialog


class AgentManagementDialog(QDialog):
    """Agent management dialog (FN031).

    Lists the agents of the current project and offers to create a new
    agent ("New..."), edit the selected agent ("Edit") or delete the
    selected agent ("Delete"). Returns the chosen action via
    get_action(): ("new", None), ("edit", agent), ("delete", agent)
    or (None, None) on close.

    This dialog is the only agent selection surface until the agents view
    exists (EPC03); the agent list is reused by the association dialog
    (TSK04).
    """

    def __init__(self, project_service: ProjectService, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.selected_agent = None
        self.action = None  # "new", "edit", "delete" or None (close)
        self._setup_ui()
        self._refresh_list()
        self.list_widget.currentItemChanged.connect(self._selection_changed)

    def _setup_ui(self):
        self.setWindowTitle("Agents")
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout(self)
        # Dark theme (charter 98)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._edit_requested)
        self.layout.addWidget(self.list_widget, stretch=1)

        self.info_label = QLabel("Double-click an agent to edit it.")
        self.layout.addWidget(self.info_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.new_button = QPushButton("New...")
        self.new_button.clicked.connect(self._new_requested)
        self.new_button.setFixedWidth(100)
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._edit_requested)
        self.edit_button.setFixedWidth(100)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_requested)
        self.delete_button.setFixedWidth(100)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        self.close_button.setFixedWidth(100)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)

    def _refresh_list(self):
        self.list_widget.clear()
        project = self.project_service.current_project
        agents = project.agent if project else []
        for agent in agents:
            item = QListWidgetItem(f"{agent.lb} ({agent.typ})")
            item.setData(Qt.ItemDataRole.UserRole, agent)
            self.list_widget.addItem(item)
        self.edit_button.setEnabled(len(agents) > 0)
        self.delete_button.setEnabled(False)

    def _selected_agent(self):
        current = self.list_widget.currentItem()
        if current is None:
            return None
        return current.data(Qt.ItemDataRole.UserRole)

    def _selection_changed(self, current, previous):
        has_selection = current is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _delete_requested(self):
        agent = self._selected_agent()
        if agent is None:
            return
        self.selected_agent = agent
        self.action = "delete"
        self.accept()

    def _new_requested(self):
        self.selected_agent = None
        self.action = "new"
        self.accept()

    def _edit_requested(self):
        agent = self._selected_agent()
        if agent is None:
            return
        self.selected_agent = agent
        self.action = "edit"
        self.accept()

    def get_action(self):
        """Return the action chosen by the user.

        Returns:
            Tuple (action, agent) where action is "new", "edit" or
            "delete", and agent is the selected Agent (None for "new").
            (None, None) if the dialog was closed.
        """
        return self.action, self.selected_agent
