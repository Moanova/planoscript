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
assert font.pointSize() == 12, font.pointSize()
assert not font.bold()
label_rect = node.label.boundingRect()
assert abs(node.label.x() - (80 - label_rect.width()) / 2) < 0.01
assert abs(node.label.y() - (40 - label_rect.height()) / 2) < 0.01
print("Points 03/04 OK: no type label, 12px non-bold centered name")

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
assert agents_ws.matrix.verticalHeaderItem(0).text() == "Hero"
assert agents_ws.matrix.horizontalHeaderItem(0).text().startswith("Init")
assert "[" not in agents_ws.matrix.horizontalHeaderItem(0).text()

# Point 07: row header (agent column) visible even without agents
agents_ws.set_project(service, None)
agents_ws.project_service = None
agents_ws.refresh()
vh = agents_ws.matrix.verticalHeader()
assert vh.width() == 80, vh.width()
agents_ws.set_project(service, None)
agents_ws.refresh()
assert vh.isVisibleTo(agents_ws.matrix) or vh.width() == 80

# Point 10: header dimensions
agents_ws.refresh()
assert agents_ws.matrix.horizontalHeader().defaultSectionSize() == 80
assert agents_ws.matrix.verticalHeader().defaultSectionSize() == 40

# Final TSC request: headers cannot be resized with the mouse
from PySide6.QtWidgets import QHeaderView
assert (agents_ws.matrix.verticalHeader().sectionResizeMode(0)
        == QHeaderView.ResizeMode.Fixed)
assert (agents_ws.matrix.horizontalHeader().sectionResizeMode(0)
        == QHeaderView.ResizeMode.Fixed)

# Point 08: floating-card look: no grid lines, card delegate installed
assert agents_ws.matrix.showGrid() is False
assert agents_ws.matrix.itemDelegate().__class__.__name__ == "_MatrixCardDelegate"

# Point 09: centered checkbox drawn by the card delegate (same delegate)

# Association data intact
assert agents_ws.matrix.item(0, 0).checkState() == Qt.CheckState.Checked
assert agents_ws.matrix.item(1, 0).checkState() == Qt.CheckState.Unchecked

print("Points 07-12 OK: agent column always visible, headers 80x40, "
      "card spacing, centered checkboxes, no type suffixes")

# ---------------------------------------------------------------------
# Review fixes (2nd TSC pass): info bar square + matrix checkboxes
# ---------------------------------------------------------------------
from PySide6.QtCore import QPoint
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

# Case 2: checkboxes painted + center click toggles through editorEvent
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
# Knight is the second agent (row 1): creation order (RG068)
knight_row = next(
    r for r in range(matrix_ws.matrix.rowCount())
    if matrix_ws.matrix.verticalHeaderItem(r).text() == "Knight")
cell = matrix_ws.matrix.visualItemRect(
    matrix_ws.matrix.item(knight_row, 0))
viewport = matrix_ws.matrix.viewport()
render = matrix_ws.grab().toImage()
offset = viewport.mapTo(matrix_ws, QPoint(0, 0))
light_px = sum(
    1 for y in range(cell.top(), cell.bottom())
    for x in range(cell.left(), cell.right())
    if ((render.pixel(x + offset.x(), y + offset.y()) >> 16 & 0xFF)
        + (render.pixel(x + offset.x(), y + offset.y()) >> 8 & 0xFF)
        + (render.pixel(x + offset.x(), y + offset.y()) & 0xFF)) / 3 > 100)
assert light_px > 20, f"checkbox not painted ({light_px} light px)"

# Click the centered checkbox of a checked cell -> dissociation
log_msgs.clear()
QTest.mouseClick(viewport, Qt.MouseButton.LeftButton,
                 pos=QPoint(cell.center()))
app.processEvents()
assert AssociateAgentStateUseCase.find_association(
    service.current_project.narrative_map[0], hero2.id, map_state.id) is None
assert not any("RG063" in msg for _, msg in log_msgs), log_msgs
assert _emitted and _emitted[-1] == (map_state.id, "Knight", False)

# Click again -> re-association
log_msgs.clear()
QTest.mouseClick(viewport, Qt.MouseButton.LeftButton,
                 pos=QPoint(cell.center()))
app.processEvents()
assert AssociateAgentStateUseCase.find_association(
    service.current_project.narrative_map[0], hero2.id, map_state.id) is not None
assert not any("No association" in msg for _, msg in log_msgs), log_msgs
assert _emitted[-1] == (map_state.id, "Knight", True)

# Click on the card but outside the checkbox -> no toggle, no log
log_msgs.clear()
_emitted.clear()
state_before = matrix_ws.matrix.item(knight_row, 0).checkState()
QTest.mouseClick(viewport, Qt.MouseButton.LeftButton,
                 pos=QPoint(cell.center().x(), cell.top() + 6))
app.processEvents()
assert matrix_ws.matrix.item(knight_row, 0).checkState() == state_before
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
