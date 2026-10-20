# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_matrix_cell_edition.py
# Content      : Disposable offscreen test for matrix cell edition (TSK09)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the matrix cell edition (TSK09).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_matrix_cell_edition.py
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
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from ui.views.agents_workspace import AgentsWorkspace

service = ProjectService()
CreateProjectUseCase(service).execute()
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)
dissoc_uc = DissociateAgentStateUseCase(service)

hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
state = service.current_project.narrative_map[0].state[0]
narrative_map = service.current_project.narrative_map[0]

workspace = AgentsWorkspace()
workspace.set_project(service, None,
                      associate_usecase=assoc_uc,
                      dissociate_usecase=dissoc_uc)
workspace.refresh()

# Track the emitted signal (state_id, agent_lb, associated)
emitted = []
workspace.associationChanged.connect(
    lambda sid, lb, assoc: emitted.append((sid, lb, assoc)))

# Cell (0, 0): Hero x initial state, currently unchecked -> click associates
assert workspace.matrix.item(0, 0).checkState() == Qt.CheckState.Unchecked
workspace._toggle_cell(0, 0)
assert workspace.matrix.item(0, 0).checkState() == Qt.CheckState.Checked
assert AssociateAgentStateUseCase.find_association(
    narrative_map, hero.id, state.id) is not None
assert emitted == [(state.id, "Hero", True)]

# Click again: dissociates
workspace._toggle_cell(0, 0)
assert workspace.matrix.item(0, 0).checkState() == Qt.CheckState.Unchecked
assert AssociateAgentStateUseCase.find_association(
    narrative_map, hero.id, state.id) is None
assert emitted[-1] == (state.id, "Hero", False)

# Simulated use case failure: checkbox restored to the data state
class FailingUsecase:
    def execute(self, agent, state):
        return None

workspace.associate_usecase = FailingUsecase()
workspace._toggle_cell(0, 0)
assert workspace.matrix.item(0, 0).checkState() == Qt.CheckState.Unchecked
assert not any(e[2] for e in emitted[2:])  # no spurious success emitted

print("OFFSCREEN MATRIX CELL EDITION CHECKS PASSED")
