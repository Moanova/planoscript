# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_matrix_cell_edition.py
# Content      : Disposable offscreen test for matrix cell edition (TSK15)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the matrix cell edition (TSK15).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_matrix_cell_edition.py

Validates the cell edition of the graphical matrix: real mouse clicks
on the checkboxes toggle the association through the use cases, the
associationChanged signal is emitted, a use case failure restores the
visual state, and a click on a card outside the checkboxes is a no-op.
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
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
workspace.resize(800, 600)
workspace.show()
workspace.refresh()
app.processEvents()

# Track the emitted signal (state_id, agent_lb, associated)
emitted = []
workspace.associationChanged.connect(
    lambda sid, lb, assoc: emitted.append((sid, lb, assoc)))


def click_scene(scene_pos):
    """Simulate a real left click at the given scene position."""
    view_pos = workspace.view.mapFromScene(scene_pos)
    QTest.mouseClick(workspace.view.viewport(), Qt.MouseButton.LeftButton,
                     pos=view_pos)
    app.processEvents()


def checkbox_center(row, column):
    """Scene position of the center of the checkbox of a cell."""
    agent = workspace._agents[row]
    st = workspace._states[column]
    return workspace._check_items[(agent.id, st.id)].sceneBoundingRect().center()


# Cell (0, 0): Hero x initial state, currently unchecked -> the user
# checks it: the association is created
assert workspace.is_associated(0, 0) is False
click_scene(checkbox_center(0, 0))
assert workspace.is_associated(0, 0) is True
assert AssociateAgentStateUseCase.find_association(
    narrative_map, hero.id, state.id) is not None
assert emitted == [(state.id, "Hero", True)]

# The user unchecks it: the association is removed
click_scene(checkbox_center(0, 0))
assert workspace.is_associated(0, 0) is False
assert AssociateAgentStateUseCase.find_association(
    narrative_map, hero.id, state.id) is None
assert emitted[-1] == (state.id, "Hero", False)

# Simulated use case failure: checkbox restored to the data state
class FailingUsecase:
    def execute(self, agent, state):
        return None

workspace.associate_usecase = FailingUsecase()
# The user checks the cell but the use case fails: the checkbox is
# restored to the data state (unchecked)
click_scene(checkbox_center(0, 0))
assert workspace.is_associated(0, 0) is False
assert not any(e[2] for e in emitted[2:])  # no spurious success emitted
workspace.associate_usecase = assoc_uc

# Click on a card but outside the checkboxes: no toggle (TSK12 point 09
# behavior preserved)
workspace.click_cell(0, 0)  # associate Hero again
assert workspace.is_associated(0, 0) is True
emitted.clear()
card = workspace._agent_cards[hero.id]
card_corner = card.sceneBoundingRect().topLeft() + QPointF(4, 4)
click_scene(card_corner)
assert workspace.is_associated(0, 0) is True  # unchanged
assert not emitted

print("OFFSCREEN MATRIX CELL EDITION CHECKS PASSED (TSK15)")
