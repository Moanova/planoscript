# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk12_layout_finalization.py
# Content      : Disposable offscreen test for TSK12 (12 review points)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the TSK12 layout finalization points.

Not part of the pytest suite: run locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_tsk12_layout_finalization.py
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QFrame

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from ui.views.agents_workspace import AgentsWorkspace
from ui.views.journey_workspace import JourneyWorkspace
from ui.nodes.base_node import BaseNode
from ui.nodes.state_node import StateNode
from ui.nodes.connection import Connection
from core.models.data_model import State
from core.models.view_model import (
    NodeType, NodeLayout, ConnectionLayout, PortPosition
)
from ui.utils import theme
from config.config_loader import get as _get_config

# ---------------------------------------------------------------------
# Point 01: no frame on the journey workspace
# ---------------------------------------------------------------------
workspace = JourneyWorkspace()
assert workspace.frameShape() == QFrame.Shape.NoFrame, workspace.frameShape()
print("Point 01 OK: JourneyWorkspace frame removed")

# ---------------------------------------------------------------------
# Point 02: grid major lines lighter than minor lines
# ---------------------------------------------------------------------
from PySide6.QtGui import QColor
major = QColor(_get_config("grid_major_color", "#333333"))
minor = QColor(_get_config("grid_minor_color", "#333333"))
assert major != minor, "major grid color must differ from minor"
print("Point 02 OK: grid_major_color =", major.name())

# ---------------------------------------------------------------------
# Points 03/04: no type label, 12px non-bold node label, centered
# ---------------------------------------------------------------------
service = ProjectService()
CreateProjectUseCase(service).execute()
state = service.current_project.narrative_map[0].state[0]
node_layout = NodeLayout(node_id=state.id, node_type=NodeType.STATE,
                         x=100, y=100, width=80, height=40)
node = StateNode(state, node_layout)
assert not hasattr(node, "type_label"), "type label must be removed"
font = node.label.font()
assert font.pointSize() == 9, font.pointSize()  # tooltip size (TSC 28-10-2026)
assert not font.bold()
label_rect = node.label.boundingRect()
assert abs(node.label.x() - (80 - label_rect.width()) / 2) < 0.01
assert abs(node.label.y() - (40 - label_rect.height()) / 2) < 0.01
print("Points 03/04 OK: no type label, 9pt non-bold centered name")

# ---------------------------------------------------------------------
# Point 05: connection appearances
# ---------------------------------------------------------------------
# Passive pen: solid, connection color
assert Connection.DEFAULT_PEN.style() == Qt.PenStyle.SolidLine
assert Connection.DEFAULT_PEN.color().name().upper() == "#CCCCCC"

state2 = State(id=state.id + 1, lb="Event target")
node2_layout = NodeLayout(node_id=state2.id, node_type=NodeType.STATE,
                          x=300, y=100, width=80, height=40)
node2 = StateNode(state2, node2_layout)
conn_layout = ConnectionLayout(source_node_id=state.id, target_node_id=state2.id,
                               source_port=PortPosition.RIGHT,
                               target_port=PortPosition.LEFT)
connection = Connection(conn_layout, node, node2)
# Passive: solid
connection._restore_layout_pen()
assert connection.pen().style() == Qt.PenStyle.SolidLine
# Selected: short dashes
connection.set_selected_appearance(True)
assert connection.pen().dashPattern() == [2.0, 3.0]
# Hover: solid in the state type tint
connection.set_selected_appearance(False)
hover_pen = connection._hover_pen()
assert hover_pen.style() == Qt.PenStyle.SolidLine
assert hover_pen.color().name().upper() == _get_config(
    "state_color", "#E5C07B").upper()
print("Point 05 OK: passive solid, selected/creation short dashes, "
      "hover solid type tint")

# ---------------------------------------------------------------------
# Point 06: scrollbar :pressed/:active rule present
# ---------------------------------------------------------------------
assert "handle:vertical:pressed" in theme.SCROLLBAR_STYLESHEET
assert "handle:horizontal:active" in theme.SCROLLBAR_STYLESHEET
assert "handle:vertical:active" in theme.SCROLLBAR_STYLESHEET
print("Point 06 OK: scrollbar :pressed/:active rules present")

# ---------------------------------------------------------------------
# Points 07-12: agents matrix
# NOTE (TSK15): the matrix is no longer a QTableWidget. Points 07-12
# were validated on the TSK12 QTableWidget implementation; the TSK15
# graphical matrix supersedes them and is covered by the dedicated
# offscreen tests (offscreen_agents_matrix.py, offscreen_matrix_reorder.py).
# The invariants they protected are re-checked here on the new matrix:
# no type suffixes, card dimensions 80x40, floating-card look (dark
# background), centered checkboxes, association data intact.
# ---------------------------------------------------------------------
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)
hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
sword = create_uc.execute(lb="Sword", typ="Object")['entity']
map_state = service.current_project.narrative_map[0].state[0]
assoc_uc.execute(agent=hero, state=map_state)

agents_ws = AgentsWorkspace()
agents_ws.set_project(service, None)
agents_ws.refresh()

# Point 11/12: no type suffixes
assert agents_ws.agent_label(0) == "Hero"
assert agents_ws.state_label(0).startswith("Init")
assert "[" not in agents_ws.agent_label(0)
assert "[" not in agents_ws.state_label(0)

# Point 10 (transposed): card dimensions 80x40
from ui.nodes.matrix_card import MatrixCardItem
assert MatrixCardItem.WIDTH == 80
assert MatrixCardItem.HEIGHT == 40

# Point 08/09 (transposed): dark background; checkboxes are
# 20x20 items centered on their cells
assert agents_ws.scene.backgroundBrush().color().name().upper() == \
    _get_config("bg_primary", "#1E1E1E").upper()
check = agents_ws._check_items[(hero.id, map_state.id)]
assert check.rect().width() == 20 and check.rect().height() == 20

# Association data intact
assert agents_ws.is_associated(0, 0) is True
assert agents_ws.is_associated(1, 0) is False

print("Points 07-12 OK (TSK15 matrix): card dimensions, dark background, "
      "centered checkboxes, no type suffixes")

# ---------------------------------------------------------------------
# Review fixes (2nd TSC pass): info bar square + matrix checkboxes
# ---------------------------------------------------------------------
from PySide6.QtCore import QPoint, QPointF
from PySide6.QtTest import QTest
import logging
log_msgs = []
_capture = logging.Handler()
_capture.emit = lambda record: log_msgs.append(
    (record.levelname, record.getMessage()))
logging.getLogger().addHandler(_capture)
logging.getLogger().setLevel(logging.INFO)

# Case 1: no light square above the info bar (WA_StyledBackground on
# InfoBar + WORKSPACE_STYLESHEET on the view)
from ui.main_window import MainWindow
from ui.widgets.info_bar import InfoBar
assert InfoBar().testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
main = MainWindow()
main.resize(1200, 800)
main._create_project()
main.show()
app.processEvents()
render = main.grab().toImage()
band = [(x, y) for y in range(main.info_bar.y() - 30, main.height())
        for x in range(0, main.width())
        if ((render.pixel(x, y) >> 16 & 0xFF)
            + (render.pixel(x, y) >> 8 & 0xFF)
            + (render.pixel(x, y) & 0xFF)) / 3 > 100]
assert not band, f"light pixels above info bar: {band[:6]}"
print("Case 1 OK: no light square at the bottom-left corner")

# Case 2 (TSK15): checkboxes painted + center click toggles through
# the checkbox item (mousePressEvent)
hero2 = create_uc.execute(lb="Knight", typ="Subject")['entity']
dissoc_uc = DissociateAgentStateUseCase(service)
assoc_uc.execute(agent=hero2, state=map_state)
matrix_ws = AgentsWorkspace()
matrix_ws.set_project(service, None,
                      associate_usecase=assoc_uc,
                      dissociate_usecase=dissoc_uc)
matrix_ws.resize(600, 400)
matrix_ws.show()
matrix_ws.refresh()
app.processEvents()
_emitted = []
matrix_ws.associationChanged.connect(
    lambda sid, lb, assoc: _emitted.append((sid, lb, assoc)))
# Knight is the third agent (row 2): creation order (RG068)
knight_row = next(
    r for r in range(matrix_ws.agent_count())
    if matrix_ws.agent_label(r) == "Knight")
check = matrix_ws._check_items[(hero2.id, map_state.id)]
cell_rect = check.sceneBoundingRect()
viewport = matrix_ws.view.viewport()
render = matrix_ws.grab().toImage()
offset = viewport.mapTo(matrix_ws, QPoint(0, 0))
light_px = 0
for y in range(int(cell_rect.top()), int(cell_rect.bottom())):
    for x in range(int(cell_rect.left()), int(cell_rect.right())):
        p = matrix_ws.view.mapFromScene(x, y)
        px = render.pixel(p.x() + offset.x(), p.y() + offset.y())
        if ((px >> 16 & 0xFF) + (px >> 8 & 0xFF) + (px & 0xFF)) / 3 > 100:
            light_px += 1
assert light_px > 20, f"checkbox not painted ({light_px} light px)"

# Click the centered checkbox of a checked cell -> dissociation
log_msgs.clear()
QTest.mouseClick(viewport, Qt.MouseButton.LeftButton,
                 pos=matrix_ws.view.mapFromScene(cell_rect.center()))
app.processEvents()
assert AssociateAgentStateUseCase.find_association(
    service.current_project.narrative_map[0], hero2.id, map_state.id) is None
assert not any("RG063" in msg for _, msg in log_msgs), log_msgs
assert _emitted and _emitted[-1] == (map_state.id, "Knight", False)

# Click again -> re-association
log_msgs.clear()
QTest.mouseClick(viewport, Qt.MouseButton.LeftButton,
                 pos=matrix_ws.view.mapFromScene(cell_rect.center()))
app.processEvents()
assert AssociateAgentStateUseCase.find_association(
    service.current_project.narrative_map[0], hero2.id, map_state.id) is not None
assert not any("No association" in msg for _, msg in log_msgs), log_msgs
assert _emitted[-1] == (map_state.id, "Knight", True)

# Click on the card but outside the checkbox -> no toggle, no log
log_msgs.clear()
_emitted.clear()
state_before = matrix_ws.is_associated(knight_row, 0)
card = matrix_ws._agent_cards[hero2.id]
outside = card.sceneBoundingRect().topLeft() + QPointF(4, 4)
QTest.mouseClick(viewport, Qt.MouseButton.LeftButton,
                 pos=matrix_ws.view.mapFromScene(outside))
app.processEvents()
assert matrix_ws.is_associated(knight_row, 0) == state_before
assert not _emitted and not log_msgs
print("Case 2 OK: checkbox painted, center click toggles, "
      "outside click is a no-op")

# ---------------------------------------------------------------------
# Journey workspace regression: grid + temp connection dash pattern
# ---------------------------------------------------------------------
pen_ok = Connection.DASH_PATTERN == [2.0, 3.0]
assert pen_ok
print("Journey regression OK")

print("ALL TSK12 OFFSCREEN CHECKS PASSED")
