# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk24_journey_duplicate.py
# Content      : Disposable offscreen test for the journey duplication UI (TSK24, FN025)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the journey duplication UI (TSK24, FN025).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_journeys/offscreen_tsk24_journey_duplicate.py
Requires a Qt runtime with libGL (not available in the build sandbox).

Checks:
- Project > Journeys... > Duplicate... exists and is enabled with a project
- the handler opens the selection dialog then the "Duplicate Journey"
  dialog pre-filled with "{source.lb} (copy)" and the source note
- the copy gets a new id, is not default (RG055), does not become active
  (RG023 revised), and receives a copy of the source journey nodes (FN025)
- the relations themselves are not duplicated; the map is marked modified
- the JourneyList menu reflects the new journey after rebuild
"""
import os
import sys
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication

app = QApplication([])

from ui.main_window import MainWindow
from ui.dialogs.journey_dialog import JourneyDialog
from ui.dialogs.journey_selection_dialog import JourneySelectionDialog
from usecases.journey_management import CreateJourneyUseCase
from core.services.arc_service import ArcService
from core.models.data_model import Event

mw = MainWindow()
mw.show()

mw._create_project()
app.processEvents()

nm = mw.project_service.current_project.narrative_map[0]
default = nm.journey[0]

# Menu entry exists and is enabled (TSK24)
assert 'journey_duplicate' in mw.menu_actions
assert mw.menu_actions['journey_duplicate'].isEnabled()
assert mw.menu_actions['journey_duplicate'].text() == "Duplicate..."

# One arc in the default journey (active at creation, RG052)
s1 = nm.state[0]
e1 = Event(id=1, lb="Event 1")
nm.event.append(e1)
arc1 = ArcService.create_arc(nm, s1, e1)
assert len(nm.journey_node) == 1

# A second journey (becomes active, RG023) with its own arc and note
j2 = CreateJourneyUseCase(mw.project_service).execute(lb="J2", note="note j2")['entity']
e2 = Event(id=2, lb="Event 2")
nm.event.append(e2)
arc2 = ArcService.create_arc(nm, s1, e2)
assert nm.active_journey_id == j2.id
assert len(nm.journey_node) == 2

# Run the handler with the dialogs stubbed; capture the pre-filled values
seen = {}

def fake_selection_exec(self):
    return JourneySelectionDialog.Accepted  # row 0 = default journey

def fake_dialog_exec(self):
    seen['title'] = self.windowTitle()
    seen['label'] = self.lb_edit.text()
    seen['note'] = self.note_edit.toPlainText()
    return JourneyDialog.Accepted

with patch.object(JourneySelectionDialog, 'exec', fake_selection_exec), \
     patch.object(JourneyDialog, 'exec', fake_dialog_exec):
    mw._duplicate_journey()
app.processEvents()

# Dialog was pre-filled for duplication (FN025: distinct label + source note)
assert seen['title'] == "Duplicate Journey"
assert seen['label'] == f"{default.lb} (copy)"
assert seen['note'] == (default.note or "")

# The copy: new id, distinct label, not default, not activated (RG055/RG023)
assert len(nm.journey) == 3
copy = nm.journey[2]
assert copy.id != default.id and copy.lb == f"{default.lb} (copy)"
assert copy.default is False
assert nm.active_journey_id == j2.id
assert mw.project_service.is_modified is True

# FN025: the source journey nodes are copied (same arc references)
copy_nodes = [n for n in nm.journey_node if n.journey_id == copy.id]
source_nodes = [n for n in nm.journey_node if n.journey_id == default.id]
assert len(copy_nodes) == len(source_nodes) == 1
assert copy_nodes[0].id != source_nodes[0].id
assert copy_nodes[0].state_to_event_id == source_nodes[0].state_to_event_id == arc1.id
assert copy_nodes[0].sequence_order == source_nodes[0].sequence_order
assert len(nm.journey_node) == 3  # 1 default + 1 j2 + 1 copy
assert len(nm.state_to_event) == 2  # relations shared, not duplicated

# JourneyList reflects the new journey after rebuild
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
assert len(actions) == 3
assert [a.isChecked() for a in actions] == [False, True, False]

print("OFFSCREEN TSK24 JOURNEY DUPLICATE CHECKS PASSED")
