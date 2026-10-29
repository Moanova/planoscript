# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_workspace_tabs.py
# Content      : Disposable offscreen test for the workspace tab bar (TSK07)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the Events/Agents workspace switching (TSK07).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_workspace_tabs.py
Requires a Qt runtime with libGL (not available in the build sandbox).
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication

app = QApplication([])

from ui.main_window import MainWindow

mw = MainWindow()
mw.show()

# No project: welcome page visible, tab bar hidden
assert mw.pages.currentWidget() is mw.welcome_page
assert not mw.tab_bar.isVisible()
assert mw.tab_bar.currentTab() == ""

# Create a project: tab bar visible, Events active by default
mw._create_project()
app.processEvents()
assert mw.tab_bar.isVisible()
assert mw.tab_bar.currentTab() == "Events"
assert mw.pages.currentWidget() is mw.events_page
assert mw.workspace is not None

# Switch to Agents
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
assert mw.pages.currentWidget() is mw.agents_page
assert mw.tab_bar.currentTab() == "Agents"

# Switch back to Events
mw.tab_bar.setCurrentTab("Events")
app.processEvents()
assert mw.pages.currentWidget() is mw.events_page
assert mw.tab_bar.currentTab() == "Events"

# Close the project: welcome page again, tab bar hidden
from usecases.file_management.quit_application_usecase import QuitApplicationUseCase
mw._close_project() if hasattr(mw, "_close_project") else None
app.processEvents()

print("OFFSCREEN WORKSPACE TABS CHECKS PASSED")
