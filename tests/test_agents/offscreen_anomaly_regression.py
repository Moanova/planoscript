# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_anomaly_regression.py
# Content      : Disposable offscreen regression test for the 5 anomalies
#                reported after the agents-view session (2026-10-23)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen regression test for the 5 reported anomalies.

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_anomaly_regression.py

Anomaly 1: creating an agent after a save re-enables the "Save" menu.
Anomaly 2: unchecking a cell in the agents view dissociates the agent.
Anomaly 3: checking a cell in the agents view associates the agent.
Anomaly 4: an agent created from the Projects menu appears in the
           agents view matrix.
Anomaly 5: deleting a state linked to an event (in and out) and to an
           agent no longer raises (RemoveStateAssociationsUseCase keyword).
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication

app = QApplication([])

from ui.main_window import MainWindow
from ui.dialogs.agent_dialog import AgentDialog
from core.services.arc_service import ArcService
from usecases.agent_association.associate_agent_state_usecase import (
    AssociateAgentStateUseCase
)
from usecases.agent_association.dissociate_agent_state_usecase import (
    DissociateAgentStateUseCase
)


def make_agent_dialog(lb):
    """Build an AgentDialog stub returning the given label."""
    class StubAgentDialog:
        Accepted = 1

        def __init__(self, entity=None, parent=None, default_label=None):
            pass

        def exec(self):
            return self.Accepted

        def get_values(self):
            return {'lb': lb, 'typ': 'Subject', 'note': ''}

    return StubAgentDialog


mw = MainWindow()
from PySide6.QtCore import QTimer
mw._create_project()
app.processEvents()
QTimer.singleShot(0, app.quit)  # let the offscreen loop settle once
app.exec()
app.processEvents()

project = mw.project_service.current_project
narrative_map = project.narrative_map[0]
initial_state = narrative_map.state[0]

# ---------------------------------------------------------------------
# Anomalies 1 + 4: create an agent from the Projects menu while the
# project is in a saved state and the journey view is displayed
# (TSK13 review: in the agents view, "New..." creates the agent
# directly, without a dialog)
# ---------------------------------------------------------------------
mw.project_service.set_modified(False)
mw.menu_actions['save'].setEnabled(False)  # simulate the post-save state
rows_before = mw.agents_page.agent_count()

import ui.main_window as main_window_module
orig_dlg = main_window_module.AgentDialog
main_window_module.AgentDialog = make_agent_dialog("Hero")
try:
    mw._new_agent()  # TSK13: "Project > Components... > Agent > New..."
finally:
    main_window_module.AgentDialog = orig_dlg

# Anomaly 1: the agent was created (modified flag) and "Save" is enabled
assert mw.project_service.is_modified
assert mw.menu_actions['save'].isEnabled(), "anomaly 1: Save still disabled"

# Anomaly 4: the new agent appears in the agents view matrix
assert mw.agents_page.agent_count() == rows_before + 1, \
    "anomaly 4: new agent row missing in the agents view"
hero = next(a for a in project.agent if a.lb == "Hero")

# ---------------------------------------------------------------------
# Anomalies 2 + 3: toggle a matrix cell through a real Qt click
# ---------------------------------------------------------------------
mw.agents_page.refresh()
app.processEvents()

from PySide6.QtTest import QTest

# TSK12 point 09 behavior preserved in TSK15: only a click on the
# checkbox toggles the association
agents_ws = mw.agents_page
hero_row = next(
    r for r in range(agents_ws.agent_count())
    if agents_ws.agent_label(r) == "Hero")
check = agents_ws._check_items[(hero.id, initial_state.id)]
cell = agents_ws.view.mapFromScene(check.sceneBoundingRect().center())

# Anomaly 3: checking the cell associates the agent with the state
QTest.mouseClick(agents_ws.view.viewport(), Qt.MouseButton.LeftButton,
                 pos=cell)
app.processEvents()
assert AssociateAgentStateUseCase.find_association(
    narrative_map, hero.id, initial_state.id) is not None, \
    "anomaly 3: association not created by the matrix click"
assert agents_ws.is_associated(hero_row, 0) is True

# The association is visible from the journey view (data level)
assert any(rel.agent_id == hero.id and rel.state_id == initial_state.id
           for rel in narrative_map.state_agent_rel)

# Anomaly 2: unchecking the cell dissociates the agent from the state
QTest.mouseClick(agents_ws.view.viewport(), Qt.MouseButton.LeftButton,
                 pos=cell)
app.processEvents()
assert AssociateAgentStateUseCase.find_association(
    narrative_map, hero.id, initial_state.id) is None, \
    "anomaly 2: dissociation not done by the matrix click"
assert agents_ws.is_associated(hero_row, 0) is False

# ---------------------------------------------------------------------
# Anomaly 5: delete a state linked to an incoming event, an outgoing
# event and an agent
# ---------------------------------------------------------------------
state_result = mw.create_node_usecase.execute(
    component_type="State", x=400, y=300, narrative_map=narrative_map)
event_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=300, narrative_map=narrative_map)
target = state_result['entity']
event = event_result['entity']

ArcService.create_arc(narrative_map, event, target)   # incoming event
out_event_result = mw.create_node_usecase.execute(
    component_type="Event", x=800, y=300, narrative_map=narrative_map)
out_event = out_event_result['entity']
ArcService.create_arc(narrative_map, target, out_event)  # outgoing event
AssociateAgentStateUseCase(mw.project_service).execute(
    agent=hero, state=target)

mw.workspace.create_node_from_data(state_result)
mw.workspace.create_node_from_data(event_result)
mw.workspace.create_node_from_data(out_event_result)

target_item = next(
    item for item in mw.workspace.scene.items()
    if getattr(item, 'entity', None) is target)
mw.workspace.scene.clearSelection()
target_item.setSelected(True)
app.processEvents()

# The state has arcs and an association: SU003 confirmation is expected
# (TSK13 review); auto-confirm with Yes
import ui.main_window as main_window_module
orig_question = main_window_module.QMessageBox.question
main_window_module.QMessageBox.question = staticmethod(
    lambda *a, **k: main_window_module.QMessageBox.Yes)
try:
    mw._delete_selected_component("State")  # raised TypeError before the fix
finally:
    main_window_module.QMessageBox.question = orig_question

assert target not in narrative_map.state, "anomaly 5: state not deleted"
assert not any(rel.state_id == target.id
               for rel in narrative_map.state_agent_rel), \
    "anomaly 5: agent associations not cascaded"
assert not any(arc.state_id == target.id
               for arc in narrative_map.state_to_event), \
    "anomaly 5: outgoing arc not removed"
assert not any(arc.state_id == target.id
               for arc in narrative_map.event_to_state), \
    "anomaly 5: incoming arc not removed"

# ---------------------------------------------------------------------
# ID collision regression (session 2026-10-23): entity IDs are unique
# per type, not globally. State.id=1 and Event.id=1 coexist.
# ---------------------------------------------------------------------
mw2 = MainWindow()
mw2._create_project()
app.processEvents()
nm2 = mw2.project_service.current_project.narrative_map[0]
initial2 = nm2.state[0]                      # id=1
mw2._create_new_node("State")                # state id=2
mw2._create_new_node("Event")                # event id=1 -> collides
mw2._create_new_node("State")                # state id=3
mw2._create_new_node("Event")                # event id=2 -> collides
app.processEvents()
state2 = nm2.state[1]                        # id=2
assert initial2.id == 1
assert nm2.event[0].id == 1
assert state2.id == 2
assert nm2.event[1].id == 2

# Vulnerability 1: association on the initial state from the agents
# view must not raise AttributeError (EventNode has no badge)
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
hero2 = CreateAgentUseCase(mw2.project_service).execute(lb="Hero")['entity']
AssociateAgentStateUseCase(mw2.project_service).execute(
    agent=hero2, state=initial2)
mw2._on_matrix_association_changed(initial2.id, hero2.lb, True)

# Vulnerability 2: focusing state id=2 must not keep the event id=2
# highlighted (only state nodes may stay at full opacity)
from ui.nodes.state_node import StateNode
from ui.nodes.event_node import EventNode
mw2.workspace.set_focus([state2.id])
app.processEvents()
state2_node = next(
    item for item in mw2.workspace.scene.items()
    if isinstance(item, StateNode) and item.entity.id == state2.id)
event2_node = next(
    item for item in mw2.workspace.scene.items()
    if isinstance(item, EventNode) and item.entity.id == state2.id)
assert state2_node.opacity() == 1.0, "focused state must stay highlighted"
assert event2_node.opacity() == 0.25, \
    "event sharing the focused state ID must be dimmed"

print("OFFSCREEN ANOMALY REGRESSION CHECKS PASSED")
