# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_matrix_reorder.py
# Content      : Disposable offscreen test for the matrix reordering (TSK15)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the agents matrix reordering (TSK15, RG068).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_matrix_reorder.py

Validates the drag-and-drop reordering of the graphical matrix: agents
reorder vertically, states horizontally, the initial state stays pinned
to the first column (RG031), the checkboxes follow their cells, and the
new order is persisted into the workspace layout (RG068) and restored
on reload.
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from ui.views.agents_workspace import (
    AgentsWorkspace, _COMPONENT_SPACING, _SCENE_MARGIN,
    _CELLS_LEFT, _CELLS_TOP, _STATES_TOP
)
from ui.nodes.matrix_card import MatrixCardItem
from core.models.data_model import State
from core.models.view_model import WorkspaceLayout

service = ProjectService()
CreateProjectUseCase(service).execute()
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)

hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
sword = create_uc.execute(lb="Sword", typ="Object")['entity']
nm = service.current_project.narrative_map[0]
initial = nm.state[0]
assoc_uc.execute(agent=hero, state=initial)
s2 = State(id=2, lb="Middle state")
s3 = State(id=3, lb="Final state")
nm.state.extend([s2, s3])

card_w, card_h = MatrixCardItem.WIDTH, MatrixCardItem.HEIGHT
spacing = _COMPONENT_SPACING

layout = WorkspaceLayout(narrative_map_id=nm.id)
workspace = AgentsWorkspace()
workspace.set_project(service, layout)
workspace.refresh()

assert [a.lb for a in workspace._agents] == ["Hero", "Sword"]
assert [s.lb for s in workspace._states] == ["Init State", "Middle state", "Final state"]

# ---------------------------------------------------------------------
# Agent reorder: drag Sword (row 1) to row 0
# ---------------------------------------------------------------------
card = workspace._agent_cards[sword.id]
workspace._on_card_released(
    card, QPointF(_SCENE_MARGIN, _CELLS_TOP + card_h / 2))
assert [a.lb for a in workspace._agents] == ["Sword", "Hero"]
# The checkboxes followed their cells
assert workspace.is_associated(0, 0) is False  # Sword x initial: unchecked
assert workspace.is_associated(1, 0) is True   # Hero x initial: checked
# The order was persisted into the workspace layout (RG068)
assert layout.agents_view_row_order == [sword.id, hero.id]

# ---------------------------------------------------------------------
# State reorder: drag "Final state" (column 2) to column 1
# ---------------------------------------------------------------------
card = workspace._state_cards[s3.id]
x_col1 = _CELLS_LEFT + 1 * (card_w + spacing) + card_w / 2
workspace._on_card_released(card, QPointF(x_col1, _STATES_TOP))
assert [s.lb for s in workspace._states] == [
    "Init State", "Final state", "Middle state"]
assert layout.agents_view_column_order == [initial.id, s3.id, s2.id]

# ---------------------------------------------------------------------
# Initial state pinned (RG068/RG031): two rejected moves
# ---------------------------------------------------------------------
rejected_msgs = []
workspace.reorderRejected.connect(lambda msg: rejected_msgs.append(msg))

# Another state dropped onto the first column: rejected (no message:
# the pinned state is not the one being moved)
card = workspace._state_cards[s2.id]
x_col0 = _CELLS_LEFT + card_w / 2
workspace._on_card_released(card, QPointF(x_col0, _STATES_TOP))
assert workspace._states[0].typ == "Initial"
assert not rejected_msgs, rejected_msgs

# The initial state dragged away: rejected, with an info message
card = workspace._state_cards[initial.id]
workspace._on_card_released(card, QPointF(x_col1, _STATES_TOP))
assert workspace._states[0].typ == "Initial"
assert len(rejected_msgs) == 1, rejected_msgs
assert "initial state" in rejected_msgs[0].lower(), rejected_msgs[0]
assert layout.agents_view_column_order == [initial.id, s3.id, s2.id]

# ---------------------------------------------------------------------
# Reload: the saved order is restored (RG068 persistence)
# ---------------------------------------------------------------------
reloaded = AgentsWorkspace()
reloaded.set_project(service, layout)
reloaded.refresh()
assert [a.lb for a in reloaded._agents] == ["Sword", "Hero"]
assert [s.lb for s in reloaded._states] == [
    "Init State", "Final state", "Middle state"]
# Associations still on the right cells after reload
assert reloaded.is_associated(1, 0) is True   # Hero x initial
assert reloaded.is_associated(0, 0) is False  # Sword x initial

print("OFFSCREEN MATRIX REORDER CHECKS PASSED (TSK15)")
