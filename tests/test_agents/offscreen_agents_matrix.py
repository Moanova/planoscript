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
    AgentsWorkspace, _COMPONENT_SPACING, _SCENE_MARGIN,
    _CELLS_LEFT, _CELLS_TOP, _AGENTS_LEFT, _STATES_TOP
)
from ui.nodes.matrix_card import MatrixCardItem, MatrixCheckItem
from core.models.data_model import State
from config.config_loader import get as _get_config

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

# Cards: one per agent and per state, drawn at the matrix positions.
# TSC review 26-10-2026: the state cards start after the agent column
# (x = margin + card width + spacing), the agent cards start after the
# state row (y = margin + card height + spacing)
assert len(workspace._agent_cards) == 2
assert len(workspace._state_cards) == 3
card_w, card_h = MatrixCardItem.WIDTH, MatrixCardItem.HEIGHT
spacing = _COMPONENT_SPACING
assert spacing == 20, spacing
state_card = workspace._state_cards[s2.id]
assert abs(state_card.x() - (_CELLS_LEFT + 1 * (card_w + spacing))) < 0.01
assert abs(state_card.y() - _STATES_TOP) < 0.01
agent_card = workspace._agent_cards[sword.id]
assert abs(agent_card.x() - _AGENTS_LEFT) < 0.01
assert abs(agent_card.y() - (_CELLS_TOP + 1 * (card_h + spacing))) < 0.01

# Checkboxes: 20x20, centered on their cell
check = workspace._check_items[(hero.id, state.id)]
assert check.rect().width() == 20 and check.rect().height() == 20
expected_x = _CELLS_LEFT + (card_w - 20) / 2
expected_y = _CELLS_TOP + (card_h - 20) / 2
assert abs(check.x() - expected_x) < 0.01
assert abs(check.y() - expected_y) < 0.01

# No overlap between the agent cards and the first-column checkboxes
for card in workspace._agent_cards.values():
    card_rect = card.sceneBoundingRect()
    for (aid, sid), chk in workspace._check_items.items():
        if sid == state.id:  # first column (initial state)
            assert not card_rect.intersects(chk.sceneBoundingRect()), \
                "agent card overlaps a first-column checkbox"

# The matrix is anchored to the top-left corner of the viewport
assert int(workspace.view.alignment()) == 33  # AlignLeft | AlignTop

# Background grid (TSC review 26-10-2026): major lines only, offset by
# half the component spacing (10 px), non-interactive
from ui.views.agents_workspace import (
    _GridLineItem, _GRID_OFFSET, _GRID_SIZE
)
grid_lines = [it for it in workspace.scene.items()
              if isinstance(it, _GridLineItem)]
assert len(grid_lines) > 0, "no grid lines"
v_lines = sorted(l.line().x1() for l in grid_lines
                 if l.line().x1() == l.line().x2())
h_lines = sorted(l.line().y1() for l in grid_lines
                 if l.line().y1() == l.line().y2())
assert v_lines[0] == _GRID_OFFSET == 10, v_lines[0]
assert h_lines[0] == _GRID_OFFSET == 10, h_lines[0]
assert v_lines[1] - v_lines[0] == _GRID_SIZE == 80  # major only
assert h_lines[1] - h_lines[0] == _GRID_SIZE == 80
for line in grid_lines:
    assert line.zValue() == -2
    assert line.shape().isEmpty()  # non-interactive
# Grid lines must not block clicks
from PySide6.QtCore import QPointF
item = workspace.view.itemAt(
    workspace.view.mapFromScene(QPointF(_GRID_OFFSET + _GRID_SIZE, 200)))
assert item is None, "grid line blocks clicks"

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


# Grid pixels rendered (config major color on the dark background)
grid_rgb = tuple(int(_get_config("grid_major_color", "#4A4A4A")[i:i + 2], 16)
                 for i in (1, 3, 5))
found = 0
for x in range(0, 400):
    p = workspace.view.mapFromScene(x, 5)
    px = render.pixel(p.x() + offset.x(), p.y() + offset.y())
    r, g, b = (px >> 16 & 0xFF), (px >> 8 & 0xFF), (px & 0xFF)
    # Antialiased grid pixel: between the background and the grid color
    if (grid_rgb[0] - 25 < r < grid_rgb[0] + 25
            and abs(r - g) < 10 and abs(g - b) < 10):
        found += 1
assert found >= 3, f"grid not rendered ({found} px)"

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
gap_center_x = _CELLS_LEFT + card_w + spacing / 2
assert ((pixel_at(gap_center_x - 4, _STATES_TOP + card_h / 2)
         >> 16 & 0xFF)
        + (pixel_at(gap_center_x - 4, _STATES_TOP + card_h / 2) >> 8 & 0xFF)
        + (pixel_at(gap_center_x - 4, _STATES_TOP + card_h / 2) & 0xFF)) / 3 < 80, \
    "gap between state cards is not the dark canvas background"

print("OFFSCREEN AGENTS MATRIX CHECKS PASSED (TSK15)")
