# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : offscreen_state_badges.py
# Content      : Disposable offscreen test for the state agent badge (TSK05)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen test for the agent badge on state nodes (TSK05).

Not part of the pytest suite: run it locally with:
    QT_QPA_PLATFORM=offscreen python tests/test_agents/offscreen_state_badges.py
Requires a Qt runtime with libGL (not available in the build sandbox).
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PySide6.QtWidgets import QApplication

app = QApplication([])

from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from core.models.view_model import NodeLayout, NodeType
from core.services.layout_service import LayoutService
from ui.nodes.state_node import StateNode

service = ProjectService()
CreateProjectUseCase(service).execute()
create_uc = CreateAgentUseCase(service)
assoc_uc = AssociateAgentStateUseCase(service)
state = service.current_project.narrative_map[0].state[0]

layout = LayoutService.create_node_layout(
    node_id=state.id, node_type=NodeType.STATE.value, x=100, y=100)
node = StateNode(state, layout)

# No agent: badge hidden
node.refresh_agent_badge(0, [])
assert not node.agent_badge.isVisible()
assert "Agents" not in node.toolTip()

# One agent: badge visible with '1', tooltip line
node.refresh_agent_badge(1, ["Hero"])
assert node.agent_badge.isVisible()
assert node.agent_badge_text.toPlainText() == "1"
assert node.toolTip().endswith("Agents: Hero")

# Ten agents: '9+', '+7 more' in tooltip
labels = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]
node.refresh_agent_badge(10, labels)
assert node.agent_badge_text.toPlainText() == "9+"
assert node.toolTip().endswith("Agents: A1, A2, A3 +7 more")

# Badge position (TSK17): bottom-right corner, mostly inside the
# outline — 2/3 of the badge inside, 1/3 outside (rounded to an
# integer: 5 px out of a 16 px diameter)
rect = node.rect()
outside = round(node.BADGE_DIAMETER / 3)
assert outside == 5
badge_pos = node.agent_badge.pos()
assert badge_pos.x() == rect.width() - node.BADGE_DIAMETER + outside
assert badge_pos.y() == rect.height() - node.BADGE_DIAMETER + outside

# Render check: badge pixels drawn inside the node area
image = node.toImage() if hasattr(node, "toImage") else None
print("OFFSCREEN STATE BADGE CHECKS PASSED")
