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


class EventNode(TypedNode):
    """
    Visual representation of an Event entity in the workspace.

    Events are displayed with a purple/magenta color scheme to distinguish
    them from Agents (blue/yellow) and States (green).
    """

    COLORS = {
        'bg': QColor(240, 220, 255),    # Light lavender/purple
        'border': QColor(180, 0, 200),    # Purple
        'text': QColor(0, 0, 0)         # Black
    }
    SELECTED_BG_COLOR = QColor(220, 200, 255)  # Lighter lavender
    SELECTED_BORDER_COLOR = QColor(200, 0, 255)   # Brighter purple
    INPUT_PORT_COLOR = QColor(128, 0, 128)  # Purple
    OUTPUT_PORT_COLOR = QColor(0, 128, 128)  # Turquoise
    ENTITY_TYPE_LABEL = "Event"

    def __init__(self, event: Event, layout: NodeLayout):
        super().__init__(event, layout)
        self._update_colors()
        self._update_port_colors()
