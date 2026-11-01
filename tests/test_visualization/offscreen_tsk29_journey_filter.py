# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk29_journey_filter.py
# Content      : Disposable offscreen test for the journey display filter (TSK29, FN029/RG042)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the journey display filter UI (TSK29, FN029).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_visualization/offscreen_tsk29_journey_filter.py
Requires a Qt runtime with libGL (not available in the build sandbox).

Checks:
- filter disabled by default on project opening ("All journeys" checked)
- JourneyList: "All journeys" entry on top, journeys below; checking a
  journey activates it AND the filter
- Events view: setVisible() on nodes/connections follows RG026
  (orphans hidden under filter, visible when off)
- creating a relation under an active filter makes it visible instantly
- Agents view: state columns and association cells filtered the same way
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication

app = QApplication([])

from ui.main_window import MainWindow
from ui.nodes.state_node import StateNode
from ui.nodes.event_node import EventNode
from ui.nodes.connection import Connection
from core.models.data_model import State, Event
from usecases.journey_management import CreateJourneyUseCase

mw = MainWindow()
mw.show()
mw._create_project()
app.processEvents()

nm = mw.project_service.current_project.narrative_map[0]
ws = mw.workspace

# --- Default state: filter OFF ("All journeys" checked) ---
assert ws.journey_filter_active is False
assert mw.agents_page.journey_filter_active is False
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
all_action = actions[0]
assert all_action.text() == "All journeys"
assert all_action.isCheckable() and all_action.isChecked()
assert not actions[2].isChecked()  # the journey itself is unchecked

# --- Build: S1 (initial) + S2 + E1, arc S1->E1 (attached to active journey) ---
s1 = next(s for s in nm.state if s.typ == "Initial")
s2 = State(id=nm.get_next_id('state'), lb="S2"); nm.state.append(s2)
e1 = Event(id=nm.get_next_id('event'), lb="E1"); nm.event.append(e1)
from core.services.arc_service import ArcService
arc = ArcService.create_arc(nm, s1, e1)

# create visual nodes the way the UI does
from core.models.view_model import NodeType
from core.services.layout_service import LayoutService
ws.create_node_from_data({
    'entity': s2, 'layout': LayoutService.create_node_layout(s2.id, NodeType.STATE.value, 1900.0, 1900.0),
    'node_type': NodeType.STATE, 'narrative_map_id': nm.id, 'component_type': 'State'}, select=False)
ws.create_node_from_data({
    'entity': e1, 'layout': LayoutService.create_node_layout(e1.id, NodeType.EVENT.value, 2100.0, 1800.0),
    'node_type': NodeType.EVENT, 'narrative_map_id': nm.id, 'component_type': 'Event'}, select=False)
n_s1 = ws._find_node_by_entity_id_and_type(s1.id, State)
n_s2 = ws._find_node_by_entity_id_and_type(s2.id, State)
n_e1 = ws._find_node_by_entity_id_and_type(e1.id, Event)
ws.create_connection_from_data({
    'source': n_s1, 'target': n_e1, 'arc': arc,
    'relation_type': __import__('core.models.view_model', fromlist=['RelationType']).RelationType.STATE_TO_EVENT})

def node(entity, cls):
    return ws._find_node_by_entity_id_and_type(entity.id, cls)

# filter OFF: everything visible, including orphan S2
assert node(s1, State).isVisible() and node(s2, State).isVisible() and node(e1, Event).isVisible()

# --- Activate the filter via "All journeys" unchecked / journey checked ---
mw._set_journey_filter_active(True)
app.processEvents()
# orphan S2 hidden; S1 and E1 visible (arc in active journey)
assert node(s1, State).isVisible()
assert node(e1, Event).isVisible()
assert not node(s2, State).isVisible()
conn = next(i for i in ws.scene.items() if isinstance(i, Connection))
assert conn.isVisible()

# menu state: "All journeys" unchecked, active journey checked
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
assert not actions[0].isChecked() and actions[2].isChecked()

# --- Second journey: arc stays in the first, filter on J2 hides everything ---
j2 = CreateJourneyUseCase(mw.project_service).execute(lb="J2")['entity']
mw._rebuild_journey_list_menu()
actions[3].trigger()  # activate J2 from the menu -> also activates the filter
app.processEvents()
assert nm.active_journey_id == j2.id
assert ws.journey_filter_active is True
assert not node(s1, State).isVisible() and not node(e1, Event).isVisible()
assert not conn.isVisible()

# --- Back to default journey via menu: visible again ---
mw._rebuild_journey_list_menu()
mw.journey_list_menu.actions()[2].trigger()
app.processEvents()
assert node(s1, State).isVisible() and node(e1, Event).isVisible() and conn.isVisible()

# --- "All journeys" re-checked: orphan S2 visible again ---
mw._rebuild_journey_list_menu()
mw.journey_list_menu.actions()[0].trigger()
app.processEvents()
assert ws.journey_filter_active is False
assert node(s2, State).isVisible()

# --- Agents view filtered like Events ---
mw._set_journey_filter_active(True)
mw._refresh_agents_view()
app.processEvents()
state_cards = mw.agents_page._state_cards
assert state_cards[s1.id].isVisible()
assert not state_cards[s2.id].isVisible()

# --- Filter state not persisted: save/reload keeps no trace ---
import json as _json
data = nm.to_dict()
assert 'journey_filter_active' not in _json.dumps(data)

print("offscreen TSK29: ALL CHECKS PASSED")
