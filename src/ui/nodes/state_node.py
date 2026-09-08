# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : state_node.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
State Node for Planoscript.

This module provides the StateNode class, which represents a State entity
in the visual workspace. It inherits from TypedNode and adds State-specific
coloring.

States represent conditions or situations in the narrative.
"""

from PySide6.QtGui import QColor

from core.models.data_model import State
from core.models.view_model import NodeLayout
from ui.nodes.base_node import TypedNode


class StateNode(TypedNode):
    """
    Visual representation of a State entity in the workspace.

    States are displayed with a green color scheme to distinguish them
    from Agents and Events.
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

    def __init__(self, state: State, layout: NodeLayout):
        super().__init__(state, layout)
        self._update_colors()
        self._update_port_colors()
