# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_tsk23_journey_menu.py
# Content      : Disposable offscreen test for the journey menus (TSK23, FN023/FN024/FN026)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the journey management UI (TSK23).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_journeys/offscreen_tsk23_journey_menu.py
Requires a Qt runtime with libGL (not available in the build sandbox).

Checks:
- Display > Journey > JourneyList exists (replaces Display > Events)
- the default journey is listed and checked after project creation (RG022)
- creating a journey via the use case adds a checked item (RG023)
- activating another journey moves the check (FN026)
- Project > Journeys... New.../Edit exist, Delete is a stub (TSK25)
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication

app = QApplication([])

from ui.main_window import MainWindow
from usecases.journey_management import CreateJourneyUseCase, ActivateJourneyUseCase

mw = MainWindow()
mw.show()

# No project: journey menus disabled
assert not mw.journeys_menu.isEnabled()
assert not mw.journey_menu.isEnabled()

mw._create_project()
app.processEvents()

# Menus enabled with a project
assert mw.journeys_menu.isEnabled()
assert mw.journey_menu.isEnabled()
assert mw.menu_actions['journey_new'].isEnabled()
assert mw.menu_actions['journey_edit'].isEnabled()

nm = mw.project_service.current_project.narrative_map[0]

# JourneyList: default journey checked (RG022)
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
assert len(actions) == 1
assert actions[0].isCheckable() and actions[0].isChecked()
assert nm.active_journey_id == nm.journey[0].id

# Create a second journey via the use case: it becomes active (RG023)
j2 = CreateJourneyUseCase(mw.project_service).execute(lb="J2")['entity']
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
assert len(actions) == 2
assert [a.isChecked() for a in actions] == [False, True]
assert nm.active_journey_id == j2.id

# Activate the first journey back (FN026)
ActivateJourneyUseCase(mw.project_service).execute(nm.journey[0])
mw._rebuild_journey_list_menu()
actions = mw.journey_list_menu.actions()
assert [a.isChecked() for a in actions] == [True, False]

# Triggering the JourneyList action activates that journey
actions[1].trigger()
app.processEvents()
assert nm.active_journey_id == j2.id

# Old Display > Events menu is gone
assert not hasattr(mw, 'events_menu')
assert 'list_events' not in mw.menu_actions

# Selection dialog (TSK23 review): Delete/Ok/Cancel, no New... button
from ui.dialogs.journey_selection_dialog import JourneySelectionDialog
dlg = JourneySelectionDialog(nm.journey, parent=mw)
assert not hasattr(dlg, 'new_button')
assert dlg.get_action() is None
# a journey is always selected: row 0 at construction
assert dlg.list_widget.currentRow() == 0
assert dlg.ok_button.isEnabled() and dlg.delete_button.isEnabled()

print("OFFSCREEN TSK23 JOURNEY MENU CHECKS PASSED")
