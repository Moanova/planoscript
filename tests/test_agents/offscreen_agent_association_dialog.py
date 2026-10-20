# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_agent_association_dialog.py
# Content      : Disposable offscreen test for AgentAssociationDialog (TSK04)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the agent association dialog (TSK04, FN030/SU008).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_agent_association_dialog.py
Requires a Qt runtime with libGL (not available in the build sandbox).
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from ui.dialogs.agent_association_dialog import AgentAssociationDialog

service = ProjectService()
CreateProjectUseCase(service).execute()
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)
dissoc_uc = DissociateAgentStateUseCase(service)

hero = create_uc.execute(lb="Hero", typ="Subject")['entity']
sword = create_uc.execute(lb="Sword", typ="Object")['entity']
state = service.current_project.narrative_map[0].state[0]
narrative_map = service.current_project.narrative_map[0]

# Pre-existing association: Hero is already associated with the state
assoc_uc.execute(agent=hero, state=state)

dialog = AgentAssociationDialog(service, state, assoc_uc, dissoc_uc, create_uc)

# Initial checkbox states: Hero checked, Sword unchecked
assert dialog.list_widget.count() == 2
hero_item = dialog.list_widget.item(0)
sword_item = dialog.list_widget.item(1)
assert hero_item.text() == "Hero (Subject)" and hero_item.checkState() == Qt.CheckState.Checked
assert sword_item.text() == "Sword (Object)" and sword_item.checkState() == Qt.CheckState.Unchecked

# Check Sword -> immediate association
sword_item.setCheckState(Qt.CheckState.Checked)
assert assoc_uc.find_association(narrative_map, sword.id, state.id) is not None
assert "'Sword' associated" in dialog.status_label.text()

# Uncheck Hero -> immediate dissociation
hero_item.setCheckState(Qt.CheckState.Unchecked)
assert assoc_uc.find_association(narrative_map, hero.id, state.id) is None
assert "'Hero' dissociated" in dialog.status_label.text()

# Re-check Hero (already_associated path is only hit on data-level duplicates;
# normal re-check goes through the associate use case successfully)
hero_item.setCheckState(Qt.CheckState.Checked)
assert assoc_uc.find_association(narrative_map, hero.id, state.id) is not None

# New agent creation is UI-driven (AgentDialog); simulate the use case path
result = create_uc.execute(lb="Mentor", typ="Subject")
assoc_uc.execute(agent=result['entity'], state=state)
dialog._refresh_list()
assert dialog.list_widget.count() == 3

print("OFFSCREEN AGENT ASSOCIATION DIALOG CHECKS PASSED")
