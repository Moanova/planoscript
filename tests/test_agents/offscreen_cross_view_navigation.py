# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_cross_view_navigation.py
# Content      : Disposable offscreen test for cross-view navigation (TSK10)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the cross-view navigation focus (TSK10, RG067).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_cross_view_navigation.py
Requires a Qt runtime with libGL (not available in the build sandbox).
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication

app = QApplication([])

from ui.main_window import MainWindow
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase

mw = MainWindow()
mw.show()
mw._create_project()
app.processEvents()

create_uc = CreateAgentUseCase(mw.project_service)
assoc_uc = AssociateAgentStateUseCase(mw.project_service)
hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
oracle = create_uc.execute(lb="Oracle", typ="Object")['entity']
narrative_map = mw.project_service.current_project.narrative_map[0]
initial = narrative_map.state[0]
assoc_uc.execute(agent=hero, state=initial)

# --- Events -> Agents: focus the initial state column
mw._focus_state_in_agents_view(initial.id)
app.processEvents()
assert mw.pages.currentWidget() is mw.agents_page
assert mw.agents_page.has_focus()
assert mw.agents_page._focused_state_id == initial.id

# Escape releases the focus (RG067)
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
mw._release_focus()
assert not mw.agents_page.has_focus()

# --- Agents -> Events: focus the states of an associated agent
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
mw._focus_agent_in_events_view(hero.id)
app.processEvents()
assert mw.pages.currentWidget() is mw.events_page
assert mw.workspace.has_focus()
assert initial.id in mw.workspace._focused_state_ids

# Escape releases the events focus
mw._release_focus()
assert not mw.workspace.has_focus()

# --- Agents -> Events: agent without association -> message, no switch
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
mw._focus_agent_in_events_view(oracle.id)
app.processEvents()
assert mw.pages.currentWidget() is mw.agents_page  # no switch
assert not mw.workspace.has_focus()

# The navigation never marked the project as modified (RG067/FN032).
# The agent/association setup above legitimately marks the project as
# modified, so the flag is reset before exercising the navigation.
mw.project_service.set_modified(False)
mw._focus_state_in_agents_view(initial.id)
app.processEvents()
mw._release_focus()
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
mw._focus_agent_in_events_view(hero.id)
app.processEvents()
mw._release_focus()
mw.tab_bar.setCurrentTab("Agents")
app.processEvents()
mw._focus_agent_in_events_view(oracle.id)
app.processEvents()
assert not mw.project_service.is_modified

print("OFFSCREEN CROSS-VIEW NAVIGATION CHECKS PASSED")
