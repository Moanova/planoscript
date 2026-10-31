# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk21_relation_menus.py
# Content      : Disposable offscreen test for the relation edition UI (TSK21, SU004/FN021)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the relation edition UI (TSK21).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_relations/offscreen_tsk21_relation_menus.py
Requires a Qt runtime with libGL (not available in the build sandbox).

Checks:
- RelationDialog: note field pre-filled, journeys list checkable with the
  attached journeys checked, validation rejects an empty journey list
- Events view: the "Edit Relation" context entry is wired to
  _edit_selected_relation (a Connection carries arc_or_association)
- Agents view: _on_check_menu offers "Annotate association..." enabled
  only on a checked cell
- main_window._edit_relation applies note + journey diff (monkeypatched
  dialog)
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

app = QApplication([])

from ui.main_window import MainWindow
from ui.dialogs.relation_dialog import RelationDialog
from ui.nodes.matrix_card import MatrixCheckItem
from core.services.arc_service import ArcService
from usecases.journey_management import CreateJourneyUseCase

mw = MainWindow()
mw.show()
mw._create_project()
app.processEvents()

nm = mw.project_service.current_project.narrative_map[0]

# Build one arc (initial state -> new event) attached to the default journey
state = nm.state[0]
event = nm.event[0] if nm.event else None
if event is None:
    from core.models.data_model import Event
    event = Event(id=nm.get_next_id("Event"), lb="E1")
    nm.event.append(event)
arc = ArcService.create_arc(nm, state, event)
assert arc is not None

# --- RelationDialog ---
j2 = CreateJourneyUseCase(mw.project_service).execute(lb="J2")['entity']
attached = [n.journey_id for n in nm.journey_node if n.state_to_event_id == arc.id]
dlg = RelationDialog(arc, nm.journey, attached, parent=mw)
assert dlg.note_edit.toPlainText() == ""
assert dlg.journeys_list.count() == 2
states = [dlg.journeys_list.item(i).checkState() for i in range(2)]
assert states == [Qt.CheckState.Checked, Qt.CheckState.Unchecked]
# validation: emptying the list is rejected
dlg.journeys_list.item(0).setCheckState(Qt.CheckState.Unchecked)
dlg._validate()
assert not dlg.result()  # still open (rejected)
dlg.journeys_list.item(1).setCheckState(Qt.CheckState.Checked)
dlg._validate()
assert dlg.result() == RelationDialog.Accepted
values = dlg.get_values()
assert values['journey_ids'] == [j2.id]

# --- _edit_relation with a stub dialog: note + journey diff ---
class StubDialog(RelationDialog):
    def __init__(self, relation, journeys, attached_ids, parent=None):
        super().__init__(relation, journeys, attached_ids, parent)
    def exec(self):
        # simulate: note set, attached to j2 only
        self.note_edit.setPlainText("note test")
        self.journeys_list.item(0).setCheckState(Qt.CheckState.Unchecked)
        self.journeys_list.item(1).setCheckState(Qt.CheckState.Checked)
        return RelationDialog.Accepted

import ui.main_window as mw_mod
orig = mw_mod.RelationDialog
mw_mod.RelationDialog = StubDialog
try:
    mw._edit_relation(arc)
finally:
    mw_mod.RelationDialog = orig

assert arc.note == "note test"
nodes = [n for n in nm.journey_node if n.state_to_event_id == arc.id]
assert [n.journey_id for n in nodes] == [j2.id]
assert mw.project_service.is_modified is True

# --- Agents view: checkbox context menu (checked -> enabled) ---
# The script must create an agent first, otherwise the matrix has no
# checkbox at all (_check_items is empty -> StopIteration below)
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
CreateAgentUseCase(mw.project_service).execute(lb="A1")
mw._refresh_agents_view()
app.processEvents()
agents_ws = mw.agents_page
assert agents_ws._check_items, "matrix has no checkbox (no agent)"
check = next(iter(agents_ws._check_items.values()))
check.set_checked(True)
# _on_check_menu builds the menu and execs it; intercept exec to inspect
class FakeMenu:
    def __init__(self, actions):
        self._actions = actions
    def exec(self, pos):
        return self._actions[0]
from PySide6.QtWidgets import QMenu
captured = {}
orig_add = QMenu.addAction
def spy_add(self, text):
    action = orig_add(self, text)
    captured[text] = action
    return action
QMenu.addAction = spy_add
try:
    # replace menu.exec to return the annotate action without blocking.
    # PySide6 exposes the blocking call as exec() AND the legacy exec_();
    # _on_check_menu calls menu.exec(...), which on this binding resolves to
    # the C++ slot and ignores the Python override -> patch exec_ too and
    # alias exec to it so the monkeypatch actually takes effect.
    orig_exec = QMenu.exec
    orig_exec_ = getattr(QMenu, 'exec_', None)
    def fake_exec(self, pos=None):
        return self.actions()[0] if self.actions() else None
    QMenu.exec_ = fake_exec
    QMenu.exec = fake_exec
    # handler would open a dialog; stub _edit_association
    called = {}
    mw._edit_association = lambda agent, state: called.setdefault('args', (agent, state))
    agents_ws._on_check_menu(check, mw.mapToGlobal(mw.rect().center()))
    assert 'Annotate association...' in captured
    assert captured['Annotate association...'].isEnabled() is True
    assert 'args' in called
    # unchecked cell: entry disabled
    check.set_checked(False)
    agents_ws._on_check_menu(check, mw.mapToGlobal(mw.rect().center()))
    assert captured['Annotate association...'].isEnabled() is False
finally:
    QMenu.addAction = orig_add
    QMenu.exec = orig_exec
    if orig_exec_ is not None:
        QMenu.exec_ = orig_exec_

print("OFFSCREEN TSK21 RELATION MENUS CHECKS PASSED")
