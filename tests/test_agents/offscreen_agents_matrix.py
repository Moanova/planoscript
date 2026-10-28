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
labels, association checkboxes, 120x80 cell grid with centered items
(cards 20 px margins, checkboxes 50/30 px margins), viewport-drawn grid
(extensible rightwards/downwards only), card appearance (state tint on
state cards, event tint on agent cards) and checkbox rendering.
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from ui.views.agents_workspace import (
    AgentsWorkspace, _CELL_WIDTH, _CELL_HEIGHT,
    _CARD_OFFSET_X, _CARD_OFFSET_Y, _CHECK_OFFSET_X, _CHECK_OFFSET_Y,
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

# Cards: one per agent and per state, each centered in its 120x80 cell
# (TSC review 28-10-2026): 20 px margin on every side of a card
assert len(workspace._agent_cards) == 2
assert len(workspace._state_cards) == 3
card_w, card_h = MatrixCardItem.WIDTH, MatrixCardItem.HEIGHT
assert _CELL_WIDTH == 120 and _CELL_HEIGHT == 80
assert _CARD_OFFSET_X == 20 and _CARD_OFFSET_Y == 20
assert _CHECK_OFFSET_X == 50 and _CHECK_OFFSET_Y == 30
state_card = workspace._state_cards[s2.id]
assert abs(state_card.x() - (_CELLS_LEFT + 1 * _CELL_WIDTH
                             + _CARD_OFFSET_X)) < 0.01
assert abs(state_card.y() - _STATES_TOP) < 0.01
agent_card = workspace._agent_cards[sword.id]
assert abs(agent_card.x() - _AGENTS_LEFT) < 0.01
assert abs(agent_card.y() - (_CELLS_TOP + 1 * _CELL_HEIGHT
                             + _CARD_OFFSET_Y)) < 0.01

# Checkboxes: 20x20, centered in their cell (50 px horizontal margin,
# 30 px vertical margin)
check = workspace._check_items[(hero.id, state.id)]
assert check.rect().width() == 20 and check.rect().height() == 20
expected_x = _CELLS_LEFT + _CHECK_OFFSET_X
expected_y = _CELLS_TOP + _CHECK_OFFSET_Y
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

# Background grid (TSC review 28-10-2026): drawn for the visible
# viewport only, lines every 120 px horizontally and 80 px vertically
# from the scene origin (the cells frame the matrix slots), non-
# interactive. The workspace must be shown for the viewport to have a
# size.
from ui.views.agents_workspace import _GridLineItem
workspace.resize(800, 600)
workspace.show()
app.processEvents()
grid_lines = [it for it in workspace.scene.items()
              if isinstance(it, _GridLineItem)]
assert len(grid_lines) > 0, "no grid lines"
v_lines = sorted(set(l.line().x1() for l in grid_lines
                     if l.line().x1() == l.line().x2()))
h_lines = sorted(set(l.line().y1() for l in grid_lines
                     if l.line().y1() == l.line().y2()))
# The grid is aligned on the scene origin: every line is a multiple of
# the cell size (the 100 px margin may draw a first line left/above 0)
assert all(x % _CELL_WIDTH == 0 for x in v_lines), v_lines[:5]
assert all(y % _CELL_HEIGHT == 0 for y in h_lines), h_lines[:5]
assert 0 in v_lines and 0 in h_lines  # origin lines are drawn
assert v_lines[1] - v_lines[0] == _CELL_WIDTH == 120
assert h_lines[1] - h_lines[0] == _CELL_HEIGHT == 80
for line in grid_lines:
    assert line.zValue() == -2
    assert line.shape().isEmpty()  # non-interactive
# Grid lines must not block clicks
from PySide6.QtCore import QPointF
item = workspace.view.itemAt(
    workspace.view.mapFromScene(QPointF(_CELL_WIDTH, 200)))
assert item is None, "grid line blocks clicks"
# The first cell frames the first checkbox, centered
assert abs((_CELLS_LEFT + _CELL_WIDTH / 2)
           - (check.sceneBoundingRect().center().x())) < 0.01
assert abs((_CELLS_TOP + _CELL_HEIGHT / 2)
           - (check.sceneBoundingRect().center().y())) < 0.01
# The scene covers the whole matrix and never extends leftwards nor
# upwards (the matrix stays anchored to the top-left corner)
scene_rect = workspace.scene.sceneRect()
assert scene_rect.left() == 0 and scene_rect.top() == 0
matrix_right = _CELLS_LEFT + 3 * _CELL_WIDTH
matrix_bottom = _CELLS_TOP + 2 * _CELL_HEIGHT
assert scene_rect.right() >= matrix_right
assert scene_rect.bottom() >= matrix_bottom
# Scrolling rightwards/downwards keeps the scene anchored at (0, 0)
workspace.view.horizontalScrollBar().setValue(500)
workspace.view.verticalScrollBar().setValue(300)
app.processEvents()
scene_rect = workspace.scene.sceneRect()
assert scene_rect.left() == 0 and scene_rect.top() == 0
grid_lines = [it for it in workspace.scene.items()
              if isinstance(it, _GridLineItem)]
assert len(grid_lines) > 0, "grid not redrawn on scroll"
v_lines = sorted(set(l.line().x1() for l in grid_lines
                     if l.line().x1() == l.line().x2()))
assert all(x % _CELL_WIDTH == 0 for x in v_lines), v_lines[:5]

# The grid stays visible when scrolling past the matrix content
# (regression TSC 28-10-2026: an empty shape() collapsed the item
# boundingRect, the scene index skipped the lines once the scene rect
# was larger than the items bounding rect, and the grid disappeared)
from PySide6.QtGui import QPainter
from PySide6.QtCore import QRectF


def grid_pixels_in_visible_area():
    visible = workspace.view.mapToScene(
        workspace.view.viewport().rect()).boundingRect()
    img = QImage(792, 592, QImage.Format.Format_ARGB32)
    img.fill(0xFF1E1E1E)
    painter = QPainter(img)
    workspace.scene.render(painter, QRectF(0, 0, 792, 592), visible)
    painter.end()
    bg_r = int(_get_config("bg_primary", "#1E1E1E")[1:3], 16)
    found = 0
    for y in range(img.height()):
        for x in range(img.width()):
            px = img.pixel(x, y)
            r, g, b = (px >> 16 & 0xFF), (px >> 8 & 0xFF), (px & 0xFF)
            if (r > bg_r + 10 and abs(r - g) < 10 and abs(g - b) < 10):
                found += 1
    return found


assert grid_pixels_in_visible_area() > 1000, \
    "grid disappears when scrolling past the matrix content"
workspace.view.horizontalScrollBar().setValue(1500)
workspace.view.verticalScrollBar().setValue(1200)
app.processEvents()
assert grid_pixels_in_visible_area() > 1000, \
    "grid disappears far from the matrix content"
# Grid lines still do not block clicks (empty shape preserved)
item = workspace.view.itemAt(
    workspace.view.mapFromScene(QPointF(1560, 1240)))
assert item is None, "grid line blocks clicks"
# Scroll back to the matrix origin for the rendering checks
workspace.view.horizontalScrollBar().setValue(0)
workspace.view.verticalScrollBar().setValue(0)
app.processEvents()

# Card colors: state tint (gold) on state cards, event tint (copper) on
# agent cards (decision TSC 26-10-2026)
from PySide6.QtGui import QColor
from ui.utils import theme
assert state_card._border_color.name().upper() == QColor(theme.STATE_COLOR).name().upper()
assert agent_card._border_color.name().upper() == QColor(theme.EVENT_COLOR).name().upper()

# Rendering: checkbox painted, state card outline in gold, agent card
# outline in copper, dark background, grid lines rendered
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


# Grid pixels rendered: a horizontal grid line runs at y = _CELL_HEIGHT
# (cell boundary), between the state cards row and the checkbox rows.
# With antialiasing on, a 1 px pen on an integer coordinate renders as
# an antialiased pixel brighter than the background (#1E1E1E ~ 30) in
# the grid color range (#4A4A4A = 74, rendered ~52-63).
bg_r = int(_get_config("bg_primary", "#1E1E1E")[1:3], 16)
found = 0
for x in range(int(_CELLS_LEFT), int(_CELLS_LEFT + 3 * _CELL_WIDTH)):
    p = workspace.view.mapFromScene(x, _CELL_HEIGHT)
    px = render.pixel(p.x() + offset.x(), p.y() + offset.y())
    r, g, b = (px >> 16 & 0xFF), (px >> 8 & 0xFF), (px & 0xFF)
    if (r > bg_r + 10 and abs(r - g) < 10 and abs(g - b) < 10):
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
gap_center_x = _CELLS_LEFT + _CELL_WIDTH  # cell boundary col 0 / col 1
assert ((pixel_at(gap_center_x - 4, _STATES_TOP + card_h / 2)
         >> 16 & 0xFF)
        + (pixel_at(gap_center_x - 4, _STATES_TOP + card_h / 2) >> 8 & 0xFF)
        + (pixel_at(gap_center_x - 4, _STATES_TOP + card_h / 2) & 0xFF)) / 3 < 80, \
    "gap between state cards is not the dark canvas background"

print("OFFSCREEN AGENTS MATRIX CHECKS PASSED (TSK15)")
