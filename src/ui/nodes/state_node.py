# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : state_node.py
# Version      : 2
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""State Node for Planoscript.

This module provides the StateNode class, which represents a State entity
in the visual workspace. It inherits from TypedNode and adds State-specific
coloring and the agent association badge (TSK05, FN030/SU008).

States represent conditions or situations in the narrative.
"""

from PySide6.QtGui import QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem

from core.models.data_model import State
from core.models.view_model import NodeLayout
from core.services.agent_badge_service import AgentBadgeService
from ui.nodes.base_node import TypedNode


class StateNode(TypedNode):
    """
    Visual representation of a State entity in the workspace.

    States are displayed with a green color scheme to distinguish them
    from Events. When agents are associated with the state, a single
    badge in the bottom-right corner shows the number of associated
    agents (SU008): one badge regardless of the count, hidden when
    no agent is associated, purely informative (clicks select the node).
    """

    COLORS = {
        'bg': QColor(220, 255, 220),    # Light green
        'border': QColor(0, 180, 0),     # Green
        'text': QColor(0, 0, 0)         # Black
    }
    SELECTED_BG_COLOR = QColor(200, 255, 200)  # Lighter green
    SELECTED_BORDER_COLOR = QColor(0, 200, 0)   # Brighter green
    INPUT_PORT_COLOR = QColor(150, 0, 0)   # Dark red
    OUTPUT_PORT_COLOR = QColor(0, 150, 0)  # Dark green
    ENTITY_TYPE_LABEL = "State"

    # Agent badge constants (single badge, bottom-right corner)
    BADGE_DIAMETER = 16.0
    BADGE_MARGIN = 3.0
    BADGE_BG_COLOR = QColor(70, 130, 180)    # Steel blue
    BADGE_BORDER_COLOR = QColor(0, 0, 0)      # Black
    BADGE_TEXT_COLOR = QColor(255, 255, 255)  # White

    def __init__(self, state: State, layout: NodeLayout):
        super().__init__(state, layout)
        self._update_colors()
        self._update_port_colors()
        self._init_agent_badge()

    def _init_agent_badge(self) -> None:
        """Create the agent badge items, hidden by default."""
        diameter = self.BADGE_DIAMETER
        self.agent_badge = QGraphicsEllipseItem(0, 0, diameter, diameter, self)
        self.agent_badge.setBrush(QBrush(self.BADGE_BG_COLOR))
        self.agent_badge.setPen(QPen(self.BADGE_BORDER_COLOR))
        self.agent_badge.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
        self.agent_badge.setFlag(QGraphicsEllipseItem.ItemIsMovable, False)

        self.agent_badge_text = QGraphicsTextItem(self.agent_badge)
        font = QFont("Arial", 7)
        font.setBold(True)
        self.agent_badge_text.setFont(font)
        self.agent_badge_text.setDefaultTextColor(self.BADGE_TEXT_COLOR)

        self.agent_badge.hide()
        self._position_agent_badge()

    def _position_agent_badge(self) -> None:
        """Place the badge in the bottom-right corner of the node."""
        diameter = self.BADGE_DIAMETER
        rect = self.rect()
        x = rect.width() - diameter - self.BADGE_MARGIN
        y = rect.height() - diameter - self.BADGE_MARGIN
        self.agent_badge.setPos(x, y)
        # Center the text in the badge
        text_rect = self.agent_badge_text.boundingRect()
        self.agent_badge_text.setPos(
            (diameter - text_rect.width()) / 2,
            (diameter - text_rect.height()) / 2
        )

    def refresh_agent_badge(self, count: int, agent_labels=None) -> None:
        """
        Refresh the agent badge from the number of associated agents.

        The badge is hidden when no agent is associated; it shows the
        count ('9+' beyond 9). The tooltip agents line is updated from
        the agent labels when provided.

        Args:
            count: Number of agents associated with the state
            agent_labels: Optional list of the associated agents' labels
        """
        self._associated_agent_labels = list(agent_labels or [])
        if AgentBadgeService.badge_visible(count):
            self.agent_badge_text.setPlainText(
                AgentBadgeService.badge_text(count))
            self._position_agent_badge()
            self.agent_badge.show()
        else:
            self.agent_badge.hide()
        # Refresh the tooltip so the agents line stays in sync
        self.update_entity_data()

    def get_associated_agent_labels(self):
        """Return the labels of the agents associated with the state."""
        return list(getattr(self, '_associated_agent_labels', []))

    def update_entity_data(self) -> None:
        """Refresh label and tooltip, including the associated agents line."""
        super().update_entity_data()
        agents_line = AgentBadgeService.tooltip_agents_line(
            self.get_associated_agent_labels())
        if agents_line:
            tooltip = self.toolTip()
            self.setToolTip(tooltip + "\n" + agents_line if tooltip else agents_line)

    def update_from_layout(self) -> None:
        """Update visual properties, repositioning the badge after resize."""
        super().update_from_layout()
        self._position_agent_badge()
