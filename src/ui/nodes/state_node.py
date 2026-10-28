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
from core.services.event_badge_service import EventBadgeService
from ui.nodes.base_node import TypedNode
from ui.utils import theme


class StateNode(TypedNode):
    """
    Visual representation of a State entity in the workspace.

    States are displayed with a green color scheme to distinguish them
    from Events. When agents are associated with the state, a single
    badge in the bottom-right corner shows the number of associated
    agents (SU008): one badge regardless of the count, hidden when
    no agent is associated, purely informative (clicks select the node).

    Two event badges (TSK13) show the connected events at the bottom of
    the node, at the same vertical position as the agent badge: the
    left badge counts the source events (Event_to_state arcs pointing
    to the state), the right badge the target events (State_to_event
    arcs leaving the state). Same pill + counter style as the agent
    badge, hidden when no event is connected.
    """

    # Charter 98: soft gold outline and type label, shared surface
    # background, white text
    COLORS = {
        'bg': theme.color("bg_surface", theme.BG_SURFACE),
        'border': theme.color("state_color", theme.STATE_COLOR),
        'text': theme.color("text_primary", theme.TEXT_PRIMARY)
    }
    ENTITY_TYPE_LABEL = "State"

    # Badge constants (agent badge bottom-right, event badges bottom-left
    # and bottom-right sides)
    # Charter 98: soft gold fill (state type color), soft white outline,
    # dark text for readability on the light fill. Event badges use the
    # event tint (copper) per the TSK13 decision (same style as the
    # agent badge, left and right badges identical).
    BADGE_DIAMETER = 16.0
    BADGE_MARGIN = 3.0
    BADGE_BG_COLOR = theme.color("badge_bg_color", theme.BADGE_BG_COLOR)
    BADGE_BORDER_COLOR = theme.color("badge_border_color", theme.BADGE_BORDER_COLOR)
    BADGE_TEXT_COLOR = theme.color("badge_text_color", theme.BADGE_TEXT_COLOR)
    EVENT_BADGE_BG_COLOR = theme.color("event_badge_bg_color", theme.EVENT_COLOR)

    def __init__(self, state: State, layout: NodeLayout):
        super().__init__(state, layout)
        self._update_colors()
        self._init_agent_badge()
        self._init_event_badges()

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
        """Place the badge in the bottom-right corner of the node.

        Guard: during BaseNode.__init__, update_from_layout() runs
        before _init_agent_badge() creates the badge items.
        """
        if getattr(self, 'agent_badge', None) is None:
            return
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

    def _init_event_badges(self) -> None:
        """Create the event badge items (left: source events, right:
        target events), hidden by default (TSK13)."""
        diameter = self.BADGE_DIAMETER
        self.event_badge_in = QGraphicsEllipseItem(
            0, 0, diameter, diameter, self)
        self.event_badge_in.setBrush(QBrush(self.EVENT_BADGE_BG_COLOR))
        self.event_badge_in.setPen(QPen(self.BADGE_BORDER_COLOR))
        self.event_badge_in.setFlag(
            QGraphicsEllipseItem.ItemIsSelectable, False)
        self.event_badge_in.setFlag(
            QGraphicsEllipseItem.ItemIsMovable, False)
        self.event_badge_in_text = QGraphicsTextItem(self.event_badge_in)
        font = QFont("Arial", 7)
        font.setBold(True)
        self.event_badge_in_text.setFont(font)
        self.event_badge_in_text.setDefaultTextColor(self.BADGE_TEXT_COLOR)

        self.event_badge_out = QGraphicsEllipseItem(
            0, 0, diameter, diameter, self)
        self.event_badge_out.setBrush(QBrush(self.EVENT_BADGE_BG_COLOR))
        self.event_badge_out.setPen(QPen(self.BADGE_BORDER_COLOR))
        self.event_badge_out.setFlag(
            QGraphicsEllipseItem.ItemIsSelectable, False)
        self.event_badge_out.setFlag(
            QGraphicsEllipseItem.ItemIsMovable, False)
        self.event_badge_out_text = QGraphicsTextItem(self.event_badge_out)
        self.event_badge_out_text.setFont(font)
        self.event_badge_out_text.setDefaultTextColor(self.BADGE_TEXT_COLOR)

        self.event_badge_in.hide()
        self.event_badge_out.hide()
        self._position_event_badges()

    def _position_event_badges(self) -> None:
        """Place the event badges on the bottom-left and bottom-right
        sides of the node, at the same vertical position as the agent
        badge (TSK13: same vertical position as the journey agent badge).

        Guard: during BaseNode.__init__, update_from_layout() runs
        before _init_event_badges() creates the badge items.
        """
        if getattr(self, 'event_badge_in', None) is None:
            return
        diameter = self.BADGE_DIAMETER
        rect = self.rect()
        y = rect.height() - diameter - self.BADGE_MARGIN
        # Left badge (source events): flush to the left edge
        self.event_badge_in.setPos(self.BADGE_MARGIN, y)
        text_rect = self.event_badge_in_text.boundingRect()
        self.event_badge_in_text.setPos(
            (diameter - text_rect.width()) / 2,
            (diameter - text_rect.height()) / 2
        )
        # Right badge (target events): flush to the right edge; the
        # agent badge sits inside it (bottom-right corner), so the event
        # badge is placed at the corner position minus its diameter to
        # stay on the same baseline without overlapping the corner
        x = rect.width() - diameter - self.BADGE_MARGIN - diameter
        self.event_badge_out.setPos(x, y)
        text_rect = self.event_badge_out_text.boundingRect()
        self.event_badge_out_text.setPos(
            (diameter - text_rect.width()) / 2,
            (diameter - text_rect.height()) / 2
        )

    def refresh_event_badges(self, in_count: int, out_count: int,
                             in_labels=None, out_labels=None) -> None:
        """
        Refresh the event badges from the connected event counts (TSK13).

        The left badge counts the source events (Event_to_state arcs
        pointing to the state), the right badge the target events
        (State_to_event arcs leaving the state). Badges are hidden at 0;
        they show the count ('9+' beyond 9). The tooltip event lines are
        updated from the event labels when provided.

        Args:
            in_count: Number of source events connected to the state
            out_count: Number of target events connected to the state
            in_labels: Optional list of the source events' labels
            out_labels: Optional list of the target events' labels
        """
        self._source_event_labels = list(in_labels or [])
        self._target_event_labels = list(out_labels or [])
        for badge, text_item, count in (
                (self.event_badge_in, self.event_badge_in_text, in_count),
                (self.event_badge_out, self.event_badge_out_text, out_count)):
            if EventBadgeService.badge_visible(count):
                text_item.setPlainText(EventBadgeService.badge_text(count))
                badge.show()
            else:
                badge.hide()
        self._position_event_badges()
        # Refresh the tooltip so the events lines stay in sync
        self.update_entity_data()

    def get_source_event_labels(self):
        """Return the labels of the source events connected to the state."""
        return list(getattr(self, '_source_event_labels', []))

    def get_target_event_labels(self):
        """Return the labels of the target events connected to the state."""
        return list(getattr(self, '_target_event_labels', []))

    def update_entity_data(self) -> None:
        """Refresh label and tooltip, including the associated agents line
        and the events lines."""
        super().update_entity_data()
        tooltip = self.toolTip()
        agents_line = AgentBadgeService.tooltip_agents_line(
            self.get_associated_agent_labels())
        if agents_line:
            tooltip = tooltip + "\n" + agents_line if tooltip else agents_line
        events_in_line = EventBadgeService.tooltip_events_line(
            "in", self.get_source_event_labels())
        if events_in_line:
            tooltip = tooltip + "\n" + events_in_line if tooltip else events_in_line
        events_out_line = EventBadgeService.tooltip_events_line(
            "out", self.get_target_event_labels())
        if events_out_line:
            tooltip = tooltip + "\n" + events_out_line if tooltip else events_out_line
        self.setToolTip(tooltip)

    def update_from_layout(self) -> None:
        """Update visual properties, repositioning the badges after resize."""
        super().update_from_layout()
        self._position_agent_badge()
        self._position_event_badges()
