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
07) Event badges on state nodes: left = source events, right = target
    events, counter, hidden at 0, tooltip lines, dynamic refresh
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
# refreshes the matrix
class StubAgentDialog:
    Accepted = 1
    def __init__(self, entity=None, parent=None):
        pass
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
# 07) Event badges on state nodes
# ---------------------------------------------------------------------
# Build: initial_state <- event_in (source), initial_state -> event_out (target)
event_in_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=100, narrative_map=narrative_map)
event_in = event_in_result['entity']
event_out_result = mw.create_node_usecase.execute(
    component_type="Event", x=600, y=500, narrative_map=narrative_map)
event_out = event_out_result['entity']
ArcService.create_arc(narrative_map, event_in, initial_state)   # incoming
ArcService.create_arc(narrative_map, initial_state, event_out)  # outgoing
mw.workspace.create_node_from_data(event_in_result)
mw.workspace.create_node_from_data(event_out_result)

node = ws._find_node_by_entity_id_and_type(initial_state.id, State)
assert isinstance(node, StateNode)
ws.refresh_event_badges(node)
assert node.event_badge_in.isVisible(), "07: left badge should be visible (1 source)"
assert node.event_badge_out.isVisible(), "07: right badge should be visible (1 target)"
assert node.event_badge_in_text.toPlainText() == "1", "07: left badge count"
assert node.event_badge_out_text.toPlainText() == "1", "07: right badge count"
tooltip = node.toolTip()
assert f"Events (in): {event_in.lb}" in tooltip, f"07: tooltip in line: {tooltip}"
assert f"Events (out): {event_out.lb}" in tooltip, f"07: tooltip out line: {tooltip}"

# Same vertical position as the agent badge
agent_y = node.agent_badge.pos().y()
assert node.event_badge_in.pos().y() == agent_y, "07: left badge vertical position"
assert node.event_badge_out.pos().y() == agent_y, "07: right badge vertical position"

# Visual check: the two event badges render in copper (#D19A66), the
# event type color, left and right at the bottom of the node.
# Render the node item alone (children included) at 2x scale, once
# with the badges and once without: the difference is the badge fill.
# The point-05 focus test above dims unfocused nodes: release the focus
# first so the node (and its badges) render at full brightness.
ws.clear_focus()
app.processEvents()
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QRectF

def render_node(node):
    # Render the whole scene zoomed on the node's bounding rect: the
    # scene render includes the node and its child items (badges)
    img = QImage(300, 300, QImage.Format.Format_ARGB32)
    img.fill(0)
    painter = QPainter(img)
    node.scene().render(
        painter,
        target=QRectF(0, 0, 300, 300),
        source=node.sceneBoundingRect().adjusted(-60, -60, 60, 60))
    painter.end()
    return img

def copper_pixels(img):
    count = 0
    for x in range(img.width()):
        for y in range(img.height()):
            c = img.pixelColor(x, y)
            if (abs(c.red() - 0xD1) < 30 and abs(c.green() - 0x9A) < 30
                    and abs(c.blue() - 0x66) < 30):
                count += 1
    return count

img_with = render_node(node)
copper = copper_pixels(img_with)
# Baseline without badges: hide them and re-render
node.event_badge_in.hide()
node.event_badge_out.hide()
img_without = render_node(node)
copper_without = copper_pixels(img_without)
# The badges add ~2 filled pills of 16 px diameter: at least 100 px
assert copper - copper_without > 100, (
    f"07: event badges not rendered (with={copper}, without={copper_without})")

# Hidden at 0: a state without events
node2 = ws._find_node_by_entity_id_and_type(other_state.id, State)
ws.refresh_event_badges(node2)
assert not node2.event_badge_in.isVisible(), "07: left badge hidden at 0"
assert not node2.event_badge_out.isVisible(), "07: right badge hidden at 0"

# Dynamic refresh on relation creation (through the main window callback):
# connect other_state -> event_out (outgoing arc -> right badge)
from core.models.data_model import Event as EventEntity
mw.tab_bar.setCurrentTab("Journey")
app.processEvents()
node2_src = ws._find_node_by_entity_id_and_type(other_state.id, State)
event_out_node = ws._find_node_by_entity_id_and_type(event_out.id, EventEntity)
mw._create_state_event_relation(node2_src, event_out_node)
assert any(arc.state_id == other_state.id and arc.event_id == event_out.id
           for arc in narrative_map.state_to_event), \
    "07: outgoing arc not created"
# The main window callback refreshes all state badges on relation creation
assert node2.event_badge_out.isVisible(), \
    "07: right badge not refreshed after arc creation"
assert node2.event_badge_in.isVisible() is False, \
    "07: left badge should stay hidden"

print("07 event badges OK")

print("ALL TSK13 OFFSCREEN CHECKS PASSED")
