# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agent_association_dialog.py
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

from core.models.data_model import State
from ui.utils import theme
from core.services.project_service import ProjectService
from usecases.agent_association.associate_agent_state_usecase import (
    AssociateAgentStateUseCase
)
from usecases.agent_association.dissociate_agent_state_usecase import (
    DissociateAgentStateUseCase
)
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from ui.dialogs.agent_dialog import AgentDialog


class AgentAssociationDialog(QDialog):
    """Agent association dialog for a state (FN030, SU008).

    Lists all the agents of the project with their current association
    status (checked/unchecked) for the target state. Checking a box
    associates immediately, unchecking dissociates immediately
    (no global OK button; the dialog closes with "Close").
    A "New agent..." button creates an agent and associates it with the
    state in a single operation.
    """

    def __init__(self, project_service: ProjectService, state: State,
                 associate_usecase: AssociateAgentStateUseCase,
                 dissociate_usecase: DissociateAgentStateUseCase,
                 create_agent_usecase: CreateAgentUseCase, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.state = state
        self.associate_usecase = associate_usecase
        self.dissociate_usecase = dissociate_usecase
        self.create_agent_usecase = create_agent_usecase
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        self.setWindowTitle(f"Associate agents with '{self.state.lb}'")
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout(self)
        # Dark theme (charter 98)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.itemChanged.connect(self._item_changed)
        self.layout.addWidget(self.list_widget, stretch=1)

        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.new_button = QPushButton("New agent...")
        self.new_button.clicked.connect(self._new_agent_requested)
        self.new_button.setFixedWidth(120)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setFixedWidth(100)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)

    def _refresh_list(self):
        # itemChanged fires on every flag change: disconnect while
        # rebuilding the list to avoid spurious use case calls
        self.list_widget.itemChanged.disconnect(self._item_changed)
        self.list_widget.clear()
        project = self.project_service.current_project
        narrative_map = project.narrative_map[0]
        for agent in project.agent:
            item = QListWidgetItem(f"{agent.lb} ({agent.typ})")
            item.setData(Qt.ItemDataRole.UserRole, agent)
            associated = AssociateAgentStateUseCase.find_association(
                narrative_map, agent.id, self.state.id) is not None
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if associated else Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        self.list_widget.itemChanged.connect(self._item_changed)

    def _item_changed(self, item):
        agent = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            result = self.associate_usecase.execute(agent=agent, state=self.state)
            if result and result.get('success'):
                if result.get('already_associated'):
                    self.status_label.setText(f"'{agent.lb}' is already associated")
                else:
                    self.status_label.setText(f"'{agent.lb}' associated")
            else:
                self.status_label.setText(f"Cannot associate '{agent.lb}'")
                item.setCheckState(Qt.CheckState.Unchecked)
        else:
            result = self.dissociate_usecase.execute(agent=agent, state=self.state)
            if result and result.get('success'):
                self.status_label.setText(f"'{agent.lb}' dissociated")
            else:
                self.status_label.setText(f"Cannot dissociate '{agent.lb}'")
                item.setCheckState(Qt.CheckState.Checked)

    def _new_agent_requested(self):
        dialog = AgentDialog(parent=self)
        if dialog.exec() != AgentDialog.Accepted:
            return
        values = dialog.get_values()
        result = self.create_agent_usecase.execute(
            lb=values['lb'], typ=values['typ'], note=values['note'])
        if not (result and result.get('success')):
            self.status_label.setText("Cannot create agent: invalid data")
            return
        agent = result['entity']
        associate_result = self.associate_usecase.execute(
            agent=agent, state=self.state)
        if associate_result and associate_result.get('success'):
            self.status_label.setText(f"'{agent.lb}' created and associated")
        else:
            self.status_label.setText(f"'{agent.lb}' created (association failed)")
        self._refresh_list()
