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
from config.config_loader import get as _get_config
from ui.nodes.base_node import TypedNode
from ui.utils import theme


class StateNode(TypedNode):
    """
    Visual representation of a State entity in the workspace.

    States are displayed with a green color scheme to distinguish them
    from Events. When agents are associated with the state, a single
    badge shows the number of associated agents (SU008): one badge
    regardless of the count, hidden when no agent is associated,
    purely informative (clicks select the node). The badge sits in
    the bottom-right corner of the node outline, mostly inside:
    two thirds of the badge inside the outline, one third outside
    (TSK17, TSC 28-10-2026).
    """

    # Charter 98: soft gold outline and type label, shared surface
    # background, white text
    COLORS = {
        'bg': theme.color("bg_surface", theme.BG_SURFACE),
        'border': theme.color("state_color", theme.STATE_COLOR),
        'text': theme.color("text_primary", theme.TEXT_PRIMARY)
    }
    ENTITY_TYPE_LABEL = "State"

    # Badge constants (agent badge in the bottom-right corner, mostly
    # inside the outline: 2/3 in, 1/3 out)
    # Charter 98: soft gold fill (state type color), soft white outline,
    # dark text for readability on the light fill.
    # TSK16: diameter sourced from config.json (events view)
    BADGE_DIAMETER = _get_config("events_view_badge_diameter_px", 16.0)
    BADGE_BG_COLOR = theme.color("badge_bg_color", theme.BADGE_BG_COLOR)
    BADGE_BORDER_COLOR = theme.color("badge_border_color", theme.BADGE_BORDER_COLOR)
    BADGE_TEXT_COLOR = theme.color("badge_text_color", theme.BADGE_TEXT_COLOR)

    def __init__(self, state: State, layout: NodeLayout):
        super().__init__(state, layout)
        self._update_colors()
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
        """Place the badge in the bottom-right corner of the node,
        mostly inside the outline: two thirds of the badge inside,
        one third outside (TSK17, TSC 28-10-2026). The outside part
        is one third of the diameter, rounded to an integer.

        Guard: during BaseNode.__init__, update_from_layout() runs
        before _init_agent_badge() creates the badge items.
        """
        if getattr(self, 'agent_badge', None) is None:
            return
        diameter = self.BADGE_DIAMETER
        outside = round(diameter / 3)
        rect = self.rect()
        x = rect.width() - diameter + outside
        y = rect.height() - diameter + outside
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
        tooltip = self.toolTip()
        agents_line = AgentBadgeService.tooltip_agents_line(
            self.get_associated_agent_labels())
        if agents_line:
            tooltip = tooltip + "\n" + agents_line if tooltip else agents_line
        self.setToolTip(tooltip)

    def update_from_layout(self) -> None:
        """Update visual properties, repositioning the badges after resize."""
        super().update_from_layout()
        self._position_agent_badge()
