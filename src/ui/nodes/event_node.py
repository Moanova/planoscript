# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : event_node.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Event Node for Planoscript.

This module provides the EventNode class, which represents an Event entity
in the visual workspace. It inherits from TypedNode and adds Event-specific
coloring.

Events represent occurrences or happenings in the narrative.
"""

from PySide6.QtGui import QColor

from core.models.data_model import Event
from core.models.view_model import NodeLayout
from ui.nodes.base_node import TypedNode
from ui.utils import theme


class EventNode(TypedNode):
    """
    Visual representation of an Event entity in the workspace.

    Events are displayed with a purple/magenta color scheme to distinguish
    them from Agents (blue/yellow) and States (green).
    """

    # Charter 98: copper outline and type label, shared surface
    # background, white text
    COLORS = {
        'bg': theme.color("bg_surface", theme.BG_SURFACE),
        'border': theme.color("event_color", theme.EVENT_COLOR),
        'text': theme.color("text_primary", theme.TEXT_PRIMARY)
    }
    ENTITY_TYPE_LABEL = "Event"

    def __init__(self, event: Event, layout: NodeLayout):
        super().__init__(event, layout)
        self._update_colors()
