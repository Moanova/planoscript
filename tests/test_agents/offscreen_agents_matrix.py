# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_agents_matrix.py
# Content      : Disposable offscreen test for the agents matrix (TSK08)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the agents x states matrix (TSK08).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_agents_matrix.py
Requires a Qt runtime with libGL (not available in the build sandbox).
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from ui.views.agents_workspace import AgentsWorkspace

service = ProjectService()
CreateProjectUseCase(service).execute()
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)

hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
sword = create_uc.execute(lb="Sword", typ="Object")['entity']
state = service.current_project.narrative_map[0].state[0]  # initial state
assoc_uc.execute(agent=hero, state=state)

workspace = AgentsWorkspace()
workspace.set_project(service, None)  # no saved layout: creation order
workspace.refresh()

# Rows: 2 agents; columns: 1 state (initial)
assert workspace.matrix.rowCount() == 2
assert workspace.matrix.columnCount() == 1
assert workspace.matrix.verticalHeaderItem(0).text() == "Hero"
assert workspace.matrix.verticalHeaderItem(1).text() == "Sword"
assert workspace.matrix.horizontalHeaderItem(0).text().startswith("Init")
assert "[" not in workspace.matrix.horizontalHeaderItem(0).text()

# Hero associated with the state: cell checked; Sword: unchecked
assert workspace.matrix.item(0, 0).checkState() == Qt.CheckState.Checked
assert workspace.matrix.item(1, 0).checkState() == Qt.CheckState.Unchecked

# Read-only in TSK08: no edit triggers
from PySide6.QtWidgets import QTableWidget
assert workspace.matrix.editTriggers() == QTableWidget.NoEditTriggers

print("OFFSCREEN AGENTS MATRIX CHECKS PASSED")
