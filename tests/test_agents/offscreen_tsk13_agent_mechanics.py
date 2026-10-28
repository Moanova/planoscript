# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk13_agent_mechanics.py
# Content      : Disposable offscreen test for TSK13 (agent mechanics review)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for TSK13 (7 TSC points).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_tsk13_agent_mechanics.py
Requires a Qt runtime with libGL (not available in the build sandbox).

Covers:
01) Submenu Project > Components... > Agent (New.../Edit/Delete) with
    AgentSelectionDialog; activation rules (New needs a project, Edit/
    Delete need at least one agent)
02) Journey context menu on empty area offers "New Agent"
03) Creating an event while the Agents view is active switches to the
    Journey tab and selects the new event node (menu and grid menu)
04) Agents view agent card menu: Edit Agent / Delete Agent / Show in
    journey view
05) Agents view state card menu: Edit State / Delete State (disabled
    for the initial state) / Show in journey view (focus in journey view)
06) Agents view grid menu: New Agent / New State / New Event
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

app = QApplication([])

import ui.main_window as main_window_module
from ui.main_window import MainWindow
from ui.nodes.state_node import StateNode
from core.services.arc_service import ArcService
from core.models.data_model import State

mw = MainWindow()
mw._create_project()
app.processEvents()
QTimer.singleShot(0, app.quit)
app.exec()
app.processEvents()

project = mw.project_service.current_project
narrative_map = project.narrative_map[0]
initial_state = narrative_map.state[0]

# ---------------------------------------------------------------------
# 01) Agent submenu structure and activation rules
# ---------------------------------------------------------------------
assert hasattr(mw, 'agent_menu'), "01: agent submenu missing"
actions = [a.text() for a in mw.agent_menu.actions()]
assert actions == ["New...", "Edit", "Delete"], f"01: agent submenu entries: {actions}"

# With no agent yet: New... enabled (project open), Edit/Delete disabled
assert mw.menu_actions['agent_new'].isEnabled(), "01: New... should be enabled"
assert not mw.menu_actions['agent_edit'].isEnabled(), "01: Edit should be disabled (no agent)"
assert not mw.menu_actions['agent_delete'].isEnabled(), "01: Delete should be disabled (no agent)"

# Create one agent through the real use case -> Edit/Delete become enabled
result = mw.create_agent_usecase.execute(lb="Hero", typ="Subject", note="")
assert result and result.get('success')
app.processEvents()
mw._update_menu_state()
assert mw.menu_actions['agent_edit'].isEnabled(), "01: Edit should be enabled (agent exists)"
assert mw.menu_actions['agent_delete'].isEnabled(), "01: Delete should be enabled (agent exists)"

# AgentSelectionDialog: Ok disabled without selection, enabled with one
from ui.dialogs.agent_selection_dialog import AgentSelectionDialog
dlg = AgentSelectionDialog(project.agent)
assert dlg.list_widget.count() == 1
assert not dlg.ok_button.isEnabled(), "01: Ok disabled without selection"
dlg.list_widget.setCurrentRow(0)
assert dlg.ok_button.isEnabled(), "01: Ok enabled with a selection"
assert dlg.get_selected_agent().lb == "Hero"

# _select_agent returns None when no agent exists (cancel path covered
# by the empty-project branch)
mw2_project_agents = project.agent
project.agent.clear()
assert mw._select_agent() is None, "01: no agent -> info message, None"
project.agent.extend(mw2_project_agents)

# _new_agent through a stubbed AgentDialog creates the agent and
# refreshes the matrix (journey view: dialog with a default label,
# editable — TSK13 review)
class StubAgentDialog:
    Accepted = 1
    seen_default_labels = []
    def __init__(self, entity=None, parent=None, default_label=None):
        StubAgentDialog.seen_default_labels.append(default_label)
    def exec(self):
        return self.Accepted
    def get_values(self):
        return {'lb': 'Villain', 'typ': 'Subject', 'note': ''}

orig_dlg = main_window_module.AgentDialog
main_window_module.AgentDialog = StubAgentDialog
rows_before = mw.agents_page.agent_count()
try:
    mw._new_agent()
finally:
    main_window_module.AgentDialog = orig_dlg
assert any(a.lb == "Villain" for a in project.agent), "01: agent not created"
assert mw.agents_page.agent_count() == rows_before + 1, "01: matrix not refreshed"
assert StubAgentDialog.seen_default_labels and \
    StubAgentDialog.seen_default_labels[0].startswith("Agent "), \
    f"01: New Agent dialog should get a default label: {StubAgentDialog.seen_default_labels}"

# _edit_agent through stubs: selection + edition dialog
class StubSelectionDialog:
    Accepted = 1
    def __init__(self, agents, parent=None):
        self._agent = agents[0]
    def exec(self):
        return self.Accepted
    def get_selected_agent(self):
        return self._agent

class StubEditDialog:
    Accepted = 1
    def __init__(self, entity=None, parent=None):
        self.entity = entity
    def exec(self):
        return self.Accepted
    def get_values(self):
        return {'lb': 'Hero renamed', 'typ': 'Subject', 'note': ''}

orig_sel = main_window_module.AgentSelectionDialog
main_window_module.AgentSelectionDialog = StubSelectionDialog
main_window_module.AgentDialog = StubEditDialog
try:
    mw._edit_agent()
finally:
    main_window_module.AgentSelectionDialog = orig_sel
    main_window_module.AgentDialog = orig_dlg
hero = next(a for a in project.agent if a.lb == "Hero renamed")
assert hero is not None, "01: agent not renamed"

# _delete_agent through stubs: selection + confirmation (Yes)
orig_question = main_window_module.QMessageBox.question
main_window_module.QMessageBox.question = staticmethod(
    lambda *a, **k: main_window_module.QMessageBox.Yes)
main_window_module.AgentSelectionDialog = StubSelectionDialog
try:
    mw._delete_agent()
finally:
    main_window_module.AgentSelectionDialog = orig_sel
    main_window_module.QMessageBox.question = orig_question
assert not any(a.lb == "Hero renamed" for a in project.agent), \
    "01: agent not deleted"

# Recreate an agent for the agents view menu tests (04/05/06)
result = mw.create_agent_usecase.execute(lb="Hero", typ="Subject", note="")
assert result and result.get('success')
mw._refresh_agents_view()
app.processEvents()

print("01 agent submenu + selection dialog OK")

# ---------------------------------------------------------------------
# 02) Journey context menu on empty area offers "New Agent"
# ---------------------------------------------------------------------
from ui.views.journey_workspace import JourneyWorkspace
ws = mw.workspace
captured = {}

class StubMenu:
    def __init__(self, parent=None):
        self._actions = []
    def setStyleSheet(self, s):
        pass
    def addAction(self, text):
        action = type("A", (), {"text": lambda self: text})()
        self._actions.append((text, action))
        captured.setdefault('entries', []).append(text)
        return action
    def exec(self, pos):
        return None  # dismiss

orig_menu = main_window_module.QMenu
# The journey workspace builds its own QMenu; patch the class it uses
import ui.views.journey_workspace as jw_module
orig_jw_menu = jw_module.QMenu
jw_module.QMenu = StubMenu
try:
    # right-click in the middle of the empty grid
    from PySide6.QtCore import QPoint
    pos = ws.viewport().rect().center()
    ws.show_context_menu(pos)
finally:
    jw_module.QMenu = orig_jw_menu
assert "New Agent" in captured['entries'], \
    f"02: 'New Agent' missing from journey grid menu: {captured['entries']}"
assert "New State" in captured['entries'] and "New Event" in captured['entries']

print("02 journey grid menu OK")

# ---------------------------------------------------------------------
# 03) Creating an event while the Agents view is active switches to
#     Journey and selects the new event node
# ---------------------------------------------------------------------
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
events_before = len(narrative_map.event)
mw._create_new_node("Event")
app.processEvents()
assert mw.tab_bar.currentTab() == "Journey", \
    "03: tab did not switch back to Journey"
assert len(narrative_map.event) == events_before + 1, "03: event not created"
selected = ws.scene.selectedItems()
assert len(selected) == 1, "03: created event not selected"
from ui.nodes.event_node import EventNode
assert isinstance(selected[0], EventNode), "03: selected item is not the event"

# Creating a state while the Agents view is active stays in Agents
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
states_before = len(narrative_map.state)
mw._create_new_node("State")
app.processEvents()
assert mw.tab_bar.currentTab() == "Agents", \
    "03: state creation should stay in the Agents view"
assert len(narrative_map.state) == states_before + 1, "03: state not created"

print("03 event creation switch OK")

# ---------------------------------------------------------------------
# 04/05/06) Agents view context menus (stubbed QMenu capturing entries)
# ---------------------------------------------------------------------
import ui.views.agents_workspace as aw_module

def capture_menu(entries_holder):
    class CapMenu:
        def __init__(self, parent=None):
            self._actions = []
        def setStyleSheet(self, s):
            pass
        def addAction(self, text):
            action = type("A", (), {"text": lambda self: text,
                                    "setEnabled": lambda self, v: None})()
            self._actions.append((text, action))
            entries_holder.append(text)
            return action
        def exec(self, pos):
            return None
    return CapMenu

agents_ws = mw.agents_page
# The matrix refresh happens on tab activation and after data changes;
# force a refresh here so the cards exist for the menu tests
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
agents_ws.refresh()
app.processEvents()
assert agents_ws._agent_cards, "test setup: no agent card in the matrix"
assert agents_ws._state_cards, "test setup: no state card in the matrix"
# Back to Journey for the state-creation checks of point 05
mw.tab_bar.setCurrentTab("Journey")
app.processEvents()

# 04) agent card menu
agent_card = next(iter(agents_ws._agent_cards.values()))
entries = []
orig_aw_menu = aw_module.QMenu
aw_module.QMenu = capture_menu(entries)
try:
    agents_ws._on_agent_card_menu(agent_card, mw.mapToGlobal(mw.rect().center()))
finally:
    aw_module.QMenu = orig_aw_menu
assert entries == ["Edit Agent", "Delete Agent", "Show in journey view"], \
    f"04: agent card menu entries: {entries}"

# 05) state card menu: initial state -> Delete State disabled
state_card = agents_ws._state_cards[initial_state.id]
entries = []
disabled = []
class CapMenu2:
    def __init__(self, parent=None):
        pass
    def setStyleSheet(self, s):
        pass
    def addAction(self, text):
        action = type("A", (), {
            "text": lambda self: text,
            "setEnabled": lambda self, v: disabled.append((text, v)),
            "isEnabled": lambda self: True,
        })()
        entries.append(text)
        return action
    def exec(self, pos):
        return None
aw_module.QMenu = CapMenu2
try:
    agents_ws._on_state_card_menu(state_card, mw.mapToGlobal(mw.rect().center()))
finally:
    aw_module.QMenu = orig_aw_menu
assert entries == ["Edit State", "Delete State", "Show in journey view"], \
    f"05: state card menu entries: {entries}"
assert ("Delete State", False) in disabled, \
    f"05: Delete State should be disabled for the initial state: {disabled}"

# 05) non-initial state -> Delete State enabled
other_state_result = mw.create_node_usecase.execute(
    component_type="State", x=400, y=300, narrative_map=narrative_map)
other_state = other_state_result['entity']
mw.workspace.create_node_from_data(other_state_result)
agents_ws.refresh()
app.processEvents()
other_card = agents_ws._state_cards[other_state.id]
entries = []
disabled = []
aw_module.QMenu = CapMenu2
try:
    agents_ws._on_state_card_menu(other_card, mw.mapToGlobal(mw.rect().center()))
finally:
    aw_module.QMenu = orig_aw_menu
assert ("Delete State", True) in disabled or not any(
    t == "Delete State" and v is False for t, v in disabled), \
    "05: Delete State should be enabled for a non-initial state"

# 05) Show in journey view on a state -> focus in the journey view
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
received = []
mw.agents_page.focusStateInJourneyViewRequested.connect(
    lambda sid: received.append(sid))
class ExecMenu:
    """Menu stub that 'chooses' the Show in journey view action."""
    def __init__(self, parent=None):
        self._actions = []
    def setStyleSheet(self, s):
        pass
    def addAction(self, text):
        action = type("A", (), {
            "text": lambda self: text,
            "setEnabled": lambda self, v: None,
        })()
        self._actions.append((text, action))
        return action
    def exec(self, pos):
        return next(a for t, a in self._actions if t == "Show in journey view")
aw_module.QMenu = ExecMenu
try:
    agents_ws._on_state_card_menu(other_card, mw.mapToGlobal(mw.rect().center()))
finally:
    aw_module.QMenu = orig_aw_menu
app.processEvents()
assert received == [other_state.id], f"05: focus request not emitted: {received}"
assert mw.tab_bar.currentTab() == "Journey", "05: did not switch to Journey"
assert ws._focused_state_ids == {other_state.id}, \
    f"05: journey focus not applied: {ws._focused_state_ids}"

# 06) grid menu
entries = []
aw_module.QMenu = capture_menu(entries)
try:
    agents_ws._on_grid_menu(mw.mapToGlobal(mw.rect().center()))
finally:
    aw_module.QMenu = orig_aw_menu
assert entries == ["New Agent", "New State", "New Event"], \
    f"06: grid menu entries: {entries}"

print("04/05/06 agents view context menus OK")

# ---------------------------------------------------------------------
# TSK13 review (TSC feedback): deletion confirmation in the journey
# view (SU003) — state and event with associated data
# ---------------------------------------------------------------------
from core.models.data_model import Event as EventEntity

# Build: connected_state <- event_a, connected_state -> event_b, plus
# a standalone state and a standalone event (no associated data).
# The initial state is not used here: RG031 protects it before the
# SU003 confirmation. Nodes are created in the scene through
# create_node_from_data (the use case alone only creates the entity).
state_result = mw.create_node_usecase.execute(
    component_type="State", x=300, y=300, narrative_map=narrative_map)
connected_state = state_result['entity']
mw.workspace.create_node_from_data(state_result)
state_result = mw.create_node_usecase.execute(
    component_type="State", x=300, y=600, narrative_map=narrative_map)
alone_state = state_result['entity']
mw.workspace.create_node_from_data(state_result)
event_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=100, narrative_map=narrative_map)
event_a = event_result['entity']
mw.workspace.create_node_from_data(event_result)
event_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=500, narrative_map=narrative_map)
event_b = event_result['entity']
mw.workspace.create_node_from_data(event_result)
event_result = mw.create_node_usecase.execute(
    component_type="Event", x=900, y=300, narrative_map=narrative_map)
alone_event = event_result['entity']
mw.workspace.create_node_from_data(event_result)
ArcService.create_arc(narrative_map, event_a, connected_state)   # incoming
ArcService.create_arc(narrative_map, connected_state, event_b)  # outgoing
mw.tab_bar.setCurrentTab("Journey")
app.processEvents()
ws = mw.workspace

# Select the connected state: confirmation shown, No -> nothing deleted
state_node = ws._find_node_by_entity_id_and_type(connected_state.id, State)
ws._select_item_only(state_node)
questions = []
orig_question = main_window_module.QMessageBox.question
def spy_question(parent, title, message, buttons):
    questions.append(message)
    return main_window_module.QMessageBox.No
main_window_module.QMessageBox.question = staticmethod(spy_question)
try:
    mw._delete_selected_component("State")
finally:
    main_window_module.QMessageBox.question = staticmethod(orig_question)
assert len(questions) == 1, f"SU003: expected 1 confirmation, got {len(questions)}"
assert "2 event(s)" in questions[0], f"SU003: message lacks arc count: {questions[0]}"
assert connected_state.id in [s.id for s in narrative_map.state], \
    "SU003: state deleted despite No"
assert ws._find_node_by_entity_id_and_type(connected_state.id, State) is not None, \
    "SU003: node removed despite No"

# Yes -> the state, its arcs and its associations are removed
# (re-select: the No above left the node selected, but re-select to be
# explicit about the precondition)
state_node = ws._find_node_by_entity_id_and_type(connected_state.id, State)
ws._select_item_only(state_node)
main_window_module.QMessageBox.question = staticmethod(
    lambda *a, **k: main_window_module.QMessageBox.Yes)
try:
    mw._delete_selected_component("State")
finally:
    main_window_module.QMessageBox.question = staticmethod(orig_question)
assert connected_state.id not in [s.id for s in narrative_map.state], \
    "SU003: state not deleted after Yes"
assert ws._find_node_by_entity_id_and_type(connected_state.id, State) is None, \
    "SU003: node still in scene after Yes"
assert not any(arc.state_id == connected_state.id
               for arc in narrative_map.state_to_event), \
    "SU003: outgoing arcs not cleaned"
assert not any(arc.state_id == connected_state.id
               for arc in narrative_map.event_to_state), \
    "SU003: incoming arcs not cleaned"

# A state without any associated data: no confirmation, direct deletion
questions.clear()
main_window_module.QMessageBox.question = staticmethod(spy_question)
try:
    alone_node = ws._find_node_by_entity_id_and_type(alone_state.id, State)
    ws._select_item_only(alone_node)
    mw._delete_selected_component("State")
finally:
    main_window_module.QMessageBox.question = staticmethod(orig_question)
assert questions == [], f"SU003: unexpected confirmation for isolated state"
assert alone_state.id not in [s.id for s in narrative_map.state], \
    "SU003: isolated state not deleted"

# A connected event: confirmation shown with the arc count.
# Connect event_a to the initial state (an arc that survives the state
# deletion above): confirm with No -> nothing deleted.
ArcService.create_arc(narrative_map, event_a, initial_state)
questions.clear()
main_window_module.QMessageBox.question = staticmethod(spy_question)
try:
    event_a_node = ws._find_node_by_entity_id_and_type(event_a.id, EventEntity)
    ws._select_item_only(event_a_node)
    mw._delete_selected_component("Event")
finally:
    main_window_module.QMessageBox.question = staticmethod(orig_question)
assert len(questions) == 1 and "1 event(s)" in questions[0], \
    f"SU003: event confirmation missing or wrong: {questions}"
assert event_a.id in [e.id for e in narrative_map.event], \
    "SU003: event deleted despite No"

# An isolated event: no confirmation, direct deletion
questions.clear()
main_window_module.QMessageBox.question = staticmethod(spy_question)
try:
    alone_event_node = ws._find_node_by_entity_id_and_type(
        alone_event.id, EventEntity)
    ws._select_item_only(alone_event_node)
    mw._delete_selected_component("Event")
finally:
    main_window_module.QMessageBox.question = staticmethod(orig_question)
assert questions == [], f"SU003: unexpected confirmation for isolated event"
assert alone_event.id not in [e.id for e in narrative_map.event], \
    "SU003: isolated event not deleted"

print("SU003 journey deletion confirmation OK")

# ---------------------------------------------------------------------
# TSK13 review: card selection in the agents view + view-dependent
# Agent menu (creation/edition/deletion aligned on the selection)
# ---------------------------------------------------------------------
from ui.nodes.matrix_card import MatrixCardItem
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt as _Qt

mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
agents_ws = mw.agents_page
agents_ws.refresh()
app.processEvents()

# A fresh agent for the selection checks
result = mw.create_agent_usecase.execute(lb="Spy", typ="Object", note="")
assert result and result.get('success')
agents_ws.refresh()
app.processEvents()
spy = next(a for a in project.agent if a.lb == "Spy")

# No card selected: Edit/Delete disabled in the agents view
mw._update_menu_state()
assert not mw.menu_actions['agent_edit'].isEnabled(), \
    "review: Edit should be disabled without a selected agent card"
assert not mw.menu_actions['agent_delete'].isEnabled(), \
    "review: Delete should be disabled without a selected agent card"
assert mw.menu_actions['agent_new'].isEnabled(), \
    "review: New... should stay enabled with a project open"

# Select the agent card: single selection, dashed outline in the type
# color (charter 98), Edit/Delete enabled
spy_card = agents_ws._agent_cards[spy.id]
agents_ws.scene.clearSelection()
spy_card.setSelected(True)
app.processEvents()
assert agents_ws.selected_agent() is spy, "review: selected_agent() mismatch"
assert agents_ws.selected_state() is None, "review: no state card selected"
assert len(agents_ws.scene.selectedItems()) == 1, "review: single selection"
pen = spy_card.pen()
# Qt reports a custom dash pattern as CustomDashLine (the charter's
# dotted selection outline uses DashLine with a 6/4 pattern)
assert pen.style() in (_Qt.DashLine, _Qt.CustomDashLine), \
    f"review: selected card outline not dashed: {pen.style()}"
assert pen.color().name().lower() == "#d19a66", \
    f"review: selected card outline should be the agent (copper) tint: {pen.color().name()}"
mw._update_menu_state()
assert mw.menu_actions['agent_edit'].isEnabled(), \
    "review: Edit should be enabled with a selected agent card"
assert mw.menu_actions['agent_delete'].isEnabled(), \
    "review: Delete should be enabled with a selected agent card"

# Selecting a state card clears the agent selection (single selection
# across kinds): Edit/Delete disabled again
state_card = next(iter(agents_ws._state_cards.values()))
agents_ws.scene.clearSelection()
state_card.setSelected(True)
app.processEvents()
assert agents_ws.selected_agent() is None, "review: agent selection not cleared"
assert agents_ws.selected_state() is state_card.entity, "review: selected_state() mismatch"
mw._update_menu_state()
assert not mw.menu_actions['agent_edit'].isEnabled(), \
    "review: Edit should be disabled when a state card is selected"

# _new_agent in the agents view: direct creation, no dialog, default label
agents_before = len(project.agent)
rows_before = agents_ws.agent_count()
main_window_module.AgentDialog = StubAgentDialog  # must NOT be called
dialog_calls_before = len(StubAgentDialog.seen_default_labels)
try:
    mw._new_agent()
finally:
    main_window_module.AgentDialog = orig_dlg
assert len(project.agent) == agents_before + 1, "review: agent not created directly"
new_agent = project.agent[-1]
assert new_agent.lb.startswith("Agent "), \
    f"review: direct creation should use a default label: {new_agent.lb}"
assert len(StubAgentDialog.seen_default_labels) == dialog_calls_before, \
    "review: no dialog should open in the agents view"
assert agents_ws.agent_count() == rows_before + 1, "review: matrix not refreshed"

# _edit_agent in the agents view: edition dialog directly on the
# selected agent card (no selection dialog). The direct creation
# above refreshed the matrix, so the new card replaces the old one.
agents_ws.scene.clearSelection()
new_card = agents_ws._agent_cards[new_agent.id]
new_card.setSelected(True)
app.processEvents()
assert agents_ws.selected_agent() is new_agent, \
    "review: new agent card not selected"
class StubEditDialog2:
    Accepted = 1
    def __init__(self, entity=None, parent=None, default_label=None):
        assert entity is new_agent, "review: edit dialog not opened on the selected agent"
    def exec(self):
        return self.Accepted
    def get_values(self):
        return {'lb': 'Spy renamed', 'typ': 'Object', 'note': ''}

selection_dialog_called = []
class SpySelectionDialog:
    def __init__(self, agents, parent=None):
        selection_dialog_called.append(True)
    def exec(self):
        return 1
    def get_selected_agent(self):
        return agents[0]

orig_sel2 = main_window_module.AgentSelectionDialog
main_window_module.AgentSelectionDialog = SpySelectionDialog
main_window_module.AgentDialog = StubEditDialog2
try:
    mw._edit_agent()
finally:
    main_window_module.AgentSelectionDialog = orig_sel2
    main_window_module.AgentDialog = orig_dlg
renamed = next((a for a in project.agent if a.lb == "Spy renamed"), None)
assert renamed is not None, "review: selected agent not renamed"
assert not selection_dialog_called, \
    "review: no selection dialog in the agents view"

# The edition refreshes the matrix, which rebuilds the cards: re-select
# the renamed agent's card before deleting it
renamed_card = agents_ws._agent_cards[renamed.id]
agents_ws.scene.clearSelection()
renamed_card.setSelected(True)
app.processEvents()
assert agents_ws.selected_agent() is renamed, \
    "review: renamed agent card not selected"

# _delete_agent in the agents view: confirmation on the selected card
orig_question = main_window_module.QMessageBox.question
main_window_module.QMessageBox.question = staticmethod(
    lambda *a, **k: main_window_module.QMessageBox.Yes)
try:
    mw._delete_agent()
finally:
    main_window_module.QMessageBox.question = orig_question
assert renamed.id not in [a.id for a in project.agent], \
    "review: selected agent not deleted"
assert agents_ws.agent_count() == rows_before, \
    "review: matrix not refreshed after deletion"

# Back to the journey view: Edit/Delete need an agent, not a selection
mw.tab_bar.setCurrentTab("Journey")
app.processEvents()
mw._update_menu_state()
assert mw.menu_actions['agent_edit'].isEnabled(), \
    "review: Edit should be enabled in the journey view (agents exist)"
assert mw.menu_actions['agent_delete'].isEnabled(), \
    "review: Delete should be enabled in the journey view (agents exist)"

print("TSK13 review agents-view selection + view-dependent menu OK")

# ---------------------------------------------------------------------
# TSK13 (revue TSC 28-10-2026, correction retour n°1): the event badges
# live on the state cards of the AGENTS view (left = source events,
# right = target events); the journey view keeps only the agent badge
# ---------------------------------------------------------------------
from ui.nodes.connection import Connection

mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
agents_ws = mw.agents_page
agents_ws.refresh()
app.processEvents()

# Rebuild a connected state: one incoming event, one outgoing event,
# one associated agent (mirrors the TSC example)
state_result = mw.create_node_usecase.execute(
    component_type="State", x=300, y=900, narrative_map=narrative_map)
badge_state = state_result['entity']
mw.workspace.create_node_from_data(state_result)
ev_in_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=700, narrative_map=narrative_map)
ev_in = ev_in_result['entity']
mw.workspace.create_node_from_data(ev_in_result)
ev_out_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=1100, narrative_map=narrative_map)
ev_out = ev_out_result['entity']
mw.workspace.create_node_from_data(ev_out_result)
ArcService.create_arc(narrative_map, ev_in, badge_state)    # incoming
ArcService.create_arc(narrative_map, badge_state, ev_out)   # outgoing
agent_result = mw.create_agent_usecase.execute(
    lb="Watcher", typ="Subject", note="")
watcher = agent_result['entity']
from usecases.agent_association.associate_agent_state_usecase import (
    AssociateAgentStateUseCase
)
AssociateAgentStateUseCase(mw.project_service).execute(
    agent=watcher, state=badge_state)

# Refresh the matrix: the event badges are computed at refresh time
agents_ws.refresh()
app.processEvents()
card = agents_ws._state_cards[badge_state.id]
assert card.event_badge_in.isVisible(), "badges: left badge should show (1 source)"
assert card.event_badge_out.isVisible(), "badges: right badge should show (1 target)"
assert card.event_badge_in_text.toPlainText() == "1", "badges: left count"
assert card.event_badge_out_text.toPlainText() == "1", "badges: right count"
tooltip = card.toolTip()
assert f"Events (in): {ev_in.lb}" in tooltip, f"badges: tooltip in: {tooltip}"
assert f"Events (out): {ev_out.lb}" in tooltip, f"badges: tooltip out: {tooltip}"

# Badge positions: centered vertically, straddling the left/right edges
# — the same coordinates as the journey connection ports (TSC 28-10-2026)
d = card.EVENT_BADGE_DIAMETER
y = card.rect().height() / 2 - d / 2
assert card.event_badge_in.pos().y() == y, "badges: left badge vertical position"
assert card.event_badge_out.pos().y() == y, "badges: right badge vertical position"
assert card.event_badge_in.pos().x() == -d / 2, "badges: left straddling the left edge"
assert card.event_badge_out.pos().x() == \
    card.rect().width() - d / 2, \
    "badges: right straddling the right edge"
# Same centers as the journey ports: (0, h/2) and (w, h/2) in the
# card's local frame (the card's sceneBoundingRect includes the 2 px pen
# margin, so compare against the local rect edges)
card_rect = card.rect()
assert card.event_badge_in.sceneBoundingRect().center().x() == \
    card.mapToScene(card_rect.left(), 0).x(), \
    "badges: left badge center on the left edge"
assert card.event_badge_out.sceneBoundingRect().center().x() == \
    card.mapToScene(card_rect.right(), 0).x(), \
    "badges: right badge center on the right edge"
assert card.event_badge_in.sceneBoundingRect().center().y() == \
    card.mapToScene(0, card_rect.height() / 2).y(), \
    "badges: left badge centered vertically"

# Agent cards carry no event badges
agent_card = agents_ws._agent_cards[watcher.id]
assert agent_card.event_badge_in is None, "badges: agent card has no event badge"
assert agent_card.event_badge_out is None, "badges: agent card has no event badge"

# The journey view state node carries only the agent badge (counter 1),
# no event badge. The badge is refreshed on association changes through
# the main window callback; trigger it explicitly here.
mw.tab_bar.setCurrentTab("Journey")
app.processEvents()
mw._refresh_all_state_badges()
app.processEvents()
journey_node = ws._find_node_by_entity_id_and_type(badge_state.id, State)
assert journey_node.agent_badge.isVisible(), "badges: journey agent badge visible"
assert journey_node.agent_badge_text.toPlainText() == "1", \
    "badges: journey agent badge count"
assert not hasattr(journey_node, 'event_badge_in'), \
    "badges: journey node has no event badge"
assert not hasattr(journey_node, 'event_badge_out'), \
    "badges: journey node has no event badge"

# A state without events: badges hidden in the agents view. Create a
# dedicated isolated state (other pre-existing states may carry arcs
# from the earlier sections of this test).
iso_result = mw.create_node_usecase.execute(
    component_type="State", x=300, y=1200, narrative_map=narrative_map)
mw.workspace.create_node_from_data(iso_result)
agents_ws.refresh()
app.processEvents()
iso_state = iso_result['entity']
other_card = agents_ws._state_cards[iso_state.id]
other_state = iso_state
assert not other_card.event_badge_in.isVisible(), "badges: left hidden at 0"
assert not other_card.event_badge_out.isVisible(), "badges: right hidden at 0"

# Dynamic refresh through the main window callback: delete the outgoing
# arc via the relation deletion path, the right badge must disappear.
# The visual connection must exist: create it through the app path
# (the arcs above were created directly on the data model).
mw.tab_bar.setCurrentTab("Journey")
app.processEvents()
ev_out_node = ws._find_node_by_entity_id_and_type(ev_out.id, EventEntity)
badge_node = ws._find_node_by_entity_id_and_type(badge_state.id, State)
conn = next(
    (it for it in ws.scene.items()
     if isinstance(it, Connection)
     and {getattr(it, 'source_node', None), getattr(it, 'target_node', None)}
     == {badge_node, ev_out_node}),
    None)
if conn is None:
    mw._create_state_event_relation(badge_node, ev_out_node)
    app.processEvents()
    conn = next(
        (it for it in ws.scene.items()
         if isinstance(it, Connection)
         and {getattr(it, 'source_node', None), getattr(it, 'target_node', None)}
         == {badge_node, ev_out_node}),
        None)
assert conn is not None, "badges: outgoing connection not found"
ws._select_item_only(conn)
main_window_module.QMessageBox.question = staticmethod(
    lambda *a, **k: main_window_module.QMessageBox.Yes)
try:
    mw._delete_selected_relation()
finally:
    main_window_module.QMessageBox.question = staticmethod(orig_question)
assert not any(arc.state_id == badge_state.id and arc.event_id == ev_out.id
               for arc in narrative_map.state_to_event), \
    "badges: outgoing arc not deleted"
# Re-fetch the card: the badge refresh above may have rebuilt the
# matrix items (deleted C++ objects must not be accessed)
card = agents_ws._state_cards[badge_state.id]
assert not card.event_badge_out.isVisible(), \
    "badges: right badge not refreshed after arc deletion"
assert card.event_badge_in.isVisible(), \
    "badges: left badge should stay visible"

# And on arc creation: connect the isolated state -> the badge appears
ev_in_node = ws._find_node_by_entity_id_and_type(ev_in.id, EventEntity)
other_node = ws._find_node_by_entity_id_and_type(other_state.id, State)
mw._create_state_event_relation(other_node, ev_in_node)
assert any(arc.state_id == other_state.id and arc.event_id == ev_in.id
           for arc in narrative_map.state_to_event), \
    "badges: outgoing arc not created"
other_card = agents_ws._state_cards[other_state.id]
assert other_card.event_badge_out.isVisible(), \
    "badges: right badge not refreshed after arc creation"
assert other_card.event_badge_out_text.toPlainText() == "1", \
    "badges: right badge count after arc creation"

print("TSK13 event badges on agents-view state cards OK")

print("ALL TSK13 OFFSCREEN CHECKS PASSED")
