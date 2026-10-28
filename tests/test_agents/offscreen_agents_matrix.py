# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_agents_matrix.py
# Content      : Disposable offscreen test for the agents matrix (TSK15)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the agents x states matrix (TSK15).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_agents_matrix.py

Validates the graphical matrix (QGraphicsView, TSK15): structure
(rows = agents, columns = states, initial state pinned first), display
labels, association checkboxes, spacing (20 px), card appearance (state
tint on state cards, event tint on agent cards) and checkbox rendering.
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtWidgets import QApplication

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from ui.views.agents_workspace import (
    AgentsWorkspace, _COMPONENT_SPACING, _SCENE_MARGIN
)
from ui.nodes.matrix_card import MatrixCardItem, MatrixCheckItem
from core.models.data_model import State

service = ProjectService()
CreateProjectUseCase(service).execute()
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)

hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
sword = create_uc.execute(lb="Sword", typ="Object")['entity']
state = service.current_project.narrative_map[0].state[0]  # initial state
assoc_uc.execute(agent=hero, state=state)

# Extra states to exercise the column order
s2 = State(id=2, lb="Middle state")
s3 = State(id=3, lb="Final state")
service.current_project.narrative_map[0].state.extend([s2, s3])

workspace = AgentsWorkspace()
workspace.set_project(service, None)  # no saved layout: creation order
workspace.refresh()

# Rows: 2 agents; columns: 3 states (initial state pinned first, RG068)
assert workspace.agent_count() == 2
assert workspace.state_count() == 3
assert workspace.agent_label(0) == "Hero"
assert workspace.agent_label(1) == "Sword"
assert workspace.state_label(0).startswith("Init")
assert workspace.state_label(1) == "Middle s"
assert workspace.state_label(2) == "Final st"

# Hero associated with the initial state: cell checked; Sword: unchecked
assert workspace.is_associated(0, 0) is True
assert workspace.is_associated(1, 0) is False
assert workspace.is_associated(0, 1) is False

# Cards: one per agent and per state, drawn at the matrix positions
assert len(workspace._agent_cards) == 2
assert len(workspace._state_cards) == 3
card_w, card_h = MatrixCardItem.WIDTH, MatrixCardItem.HEIGHT
spacing = _COMPONENT_SPACING
assert spacing == 20, spacing
state_card = workspace._state_cards[s2.id]
assert abs(state_card.x() - (_SCENE_MARGIN + 1 * (card_w + spacing))) < 0.01
agent_card = workspace._agent_cards[sword.id]
agents_top = _SCENE_MARGIN + card_h + spacing
assert abs(agent_card.y() - (agents_top + 1 * (card_h + spacing))) < 0.01

# Checkboxes: 20x20, centered on their cell
check = workspace._check_items[(hero.id, state.id)]
assert check.rect().width() == 20 and check.rect().height() == 20
expected_x = _SCENE_MARGIN + (card_w - 20) / 2
expected_y = agents_top + (card_h - 20) / 2
assert abs(check.x() - expected_x) < 0.01
assert abs(check.y() - expected_y) < 0.01

# Card colors: state tint (gold) on state cards, event tint (copper) on
# agent cards (decision TSC 26-10-2026)
from PySide6.QtGui import QColor
from ui.utils import theme
assert state_card._border_color.name().upper() == QColor(theme.STATE_COLOR).name().upper()
assert agent_card._border_color.name().upper() == QColor(theme.EVENT_COLOR).name().upper()

# Rendering: checkbox painted, state card outline in gold, agent card
# outline in copper, dark background without grid
workspace.resize(800, 600)
workspace.show()
app.processEvents()
render = workspace.grab().toImage()
vp = workspace.view.viewport()
offset = vp.mapTo(workspace, QPoint(0, 0))


def pixel_at(scene_x, scene_y):
    p = workspace.view.mapFromScene(scene_x, scene_y)
    return render.pixel(p.x() + offset.x(), p.y() + offset.y())


def count_pixels(rect, predicate):
    count = 0
    for y in range(int(rect.top()), int(rect.bottom())):
        for x in range(int(rect.left()), int(rect.right())):
            if predicate(pixel_at(x, y)):
                count += 1
    return count


# Checked checkbox: light check mark pixels inside the box
r = check.sceneBoundingRect()
light_px = count_pixels(r, lambda px: (
    ((px >> 16 & 0xFF) + (px >> 8 & 0xFF) + (px & 0xFF)) / 3 > 100))
assert light_px > 5, f"checkbox not painted ({light_px} light px)"

# Unchecked checkbox: the box is drawn EMPTY (outline only) — check a
# strict inner area of the painted box (well inside the outline, away
# from the antialiased pen) for light pixels
unchecked = workspace._check_items[(sword.id, state.id)]
r = unchecked.sceneBoundingRect().adjusted(8, 8, -8, -8)
light_px = count_pixels(r, lambda px: (
    ((px >> 16 & 0xFF) + (px >> 8 & 0xFF) + (px & 0xFF)) / 3 > 100))
assert light_px == 0, f"unchecked checkbox has light pixels ({light_px})"

# State card outline: gold pixels
gold_px = count_pixels(
    state_card.sceneBoundingRect(),
    lambda px: ((px >> 16 & 0xFF) > 180
                and 120 < (px >> 8 & 0xFF) < 220
                and (px & 0xFF) < 160))
assert gold_px > 5, f"state card outline not gold ({gold_px} px)"

# Agent card outline: copper pixels
copper_px = count_pixels(
    agent_card.sceneBoundingRect(),
    lambda px: (180 < (px >> 16 & 0xFF) < 240
                and 120 < (px >> 8 & 0xFF) < 190
                and 60 < (px & 0xFF) < 140))
assert copper_px > 5, f"agent card outline not copper ({copper_px} px)"

# Background: dark canvas color in the middle of the gap between two
# state cards (the card outline is ~2 px wide on each side of the gap)
gap_center_x = _SCENE_MARGIN + card_w + spacing / 2
assert ((pixel_at(gap_center_x - 4, _SCENE_MARGIN + card_h / 2)
         >> 16 & 0xFF)
        + (pixel_at(gap_center_x - 4, _SCENE_MARGIN + card_h / 2) >> 8 & 0xFF)
        + (pixel_at(gap_center_x - 4, _SCENE_MARGIN + card_h / 2) & 0xFF)) / 3 < 80, \
    "gap between state cards is not the dark canvas background"

print("OFFSCREEN AGENTS MATRIX CHECKS PASSED (TSK15)")
