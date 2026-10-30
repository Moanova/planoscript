# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk25_journey_delete.py
# Content      : Disposable offscreen test for the journey deletion UI (TSK25, FN027; UX review 30-10-2026: dedicated Delete... entry)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the journey deletion UI (TSK25, FN027).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_journeys/offscreen_tsk25_journey_delete.py
Requires a Qt runtime with libGL.

UX review 30-10-2026: deletion goes through the dedicated
"Project > Journeys... > Delete..." entry (Ok/Cancel selection dialog,
then confirmation) - no Delete button in the Edit selection dialog.

Checks:
- Project > Journeys... > Delete... exists and is enabled with a project
- the selection dialog is Ok/Cancel only (no Delete button)
- deleting a journey removes it, switches its orphan nodes to the default
  journey (RG036/RG066), keeps shared relations attached (RG026 1..n),
  reactivates the default journey if the deleted one was active (FN027),
  preserves components/relations, marks the project modified
- the last journey of the map is refused without confirmation (RG018)
- the JourneyList menu reflects the deletion after rebuild
"""
import os
import sys
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication, QMessageBox

app = QApplication([])

from ui.main_window import MainWindow
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

# Menu entry exists and is enabled (TSK25, dedicated Delete... entry)
assert 'journey_delete' in mw.menu_actions
assert mw.menu_actions['journey_delete'].isEnabled()
assert mw.menu_actions['journey_delete'].text() == "Delete..."

# Selection dialog is Ok/Cancel only (no Delete button, UX review)
dlg = JourneySelectionDialog(nm.journey, parent=mw)
assert not hasattr(dlg, 'delete_button')
assert dlg.ok_button.isEnabled()

# One arc in the default journey (active at creation, RG052)
s1 = nm.state[0]
e1 = Event(id=1, lb="Event 1")
nm.event.append(e1)
arc1 = ArcService.create_arc(nm, s1, e1)

# A second journey (becomes active, RG023) with its own arc (orphan node)
j2 = CreateJourneyUseCase(mw.project_service).execute(lb="J2")['entity']
e2 = Event(id=2, lb="Event 2")
nm.event.append(e2)
arc2 = ArcService.create_arc(nm, s1, e2)
assert nm.active_journey_id == j2.id
assert len(nm.journey_node) == 2

# Run Delete... with the selection dialog stubbed on j2, confirmation Yes
with patch.object(JourneySelectionDialog, 'exec',
                  lambda self: JourneySelectionDialog.Accepted), \
     patch.object(JourneySelectionDialog, 'get_selected_journey', lambda self: j2), \
     patch('ui.main_window.QMessageBox.question', return_value=QMessageBox.Yes) as confirm:
    mw._delete_journey()
app.processEvents()

# The confirmation was asked exactly once
assert confirm.call_count == 1

# j2 is deleted; default is still there and still default (RG055)
assert nm.journey == [default]
assert default.default is True

# arc2's node was switched to the default journey (RG036/RG026), not removed
nodes_arc2 = [n for n in nm.journey_node if n.state_to_event_id == arc2.id]
assert len(nodes_arc2) == 1 and nodes_arc2[0].journey_id == default.id
# arc1's node untouched
assert any(n.state_to_event_id == arc1.id and n.journey_id == default.id
           for n in nm.journey_node)
assert len(nm.journey_node) == 2

# Relations and components preserved; active back on default (FN027 revised)
assert len(nm.state_to_event) == 2
assert nm.active_journey_id == default.id
assert mw.project_service.is_modified is True

# JourneyList reflects the deletion after rebuild
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
assert len(actions) == 1 and actions[0].isChecked()

# Last journey: refused without asking confirmation (RG018)
with patch.object(JourneySelectionDialog, 'exec',
                  lambda self: JourneySelectionDialog.Accepted), \
     patch.object(JourneySelectionDialog, 'get_selected_journey', lambda self: default), \
     patch('ui.main_window.QMessageBox.question',
           side_effect=AssertionError("confirmation must not be asked")):
    mw._delete_journey()
assert nm.journey == [default]

print("OFFSCREEN TSK25 JOURNEY DELETE CHECKS PASSED")
