# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agent_node.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Agent Node for Planoscript.

This module provides the AgentNode class, which represents an Agent entity
in the visual workspace. It inherits from BaseNode and adds Agent-specific
features such as type-based styling and agent-specific connection ports.

Agent types:
- Subject: Primary active entities (e.g., main characters)
- Object: Passive or secondary entities (e.g., objects, supporting characters)
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from typing import Optional

from core.models.data_model import Agent
from core.models.view_model import NodeLayout
from ui.nodes.base_node import BaseNode


class AgentNode(BaseNode):
    """
    Visual representation of an Agent entity in the workspace.
    
    This class extends BaseNode to provide Agent-specific visual styling
    and behavior. It distinguishes between Subject and Object agent types
    with different color schemes.
    
    Attributes:
        entity: The Agent business entity
        layout: The NodeLayout containing visual properties
        type_indicator: Optional visual indicator for agent type
    """
    
    # Color schemes for different agent types
    SUBJECT_COLORS = {
        'bg': QColor(220, 245, 255),    # Light blue
        'border': QColor(0, 150, 255),  # Medium blue
        'text': QColor(0, 0, 0)         # Black
    }
    
    OBJECT_COLORS = {
        'bg': QColor(245, 245, 220),    # Light yellow/beige
        'border': QColor(200, 180, 0),   # Gold
        'text': QColor(0, 0, 0)         # Black
    }
    
    # Type indicator settings
    TYPE_INDICATOR_SIZE = 16
    TYPE_INDICATOR_MARGIN = 4
    
    def __init__(self, agent: Agent, layout: NodeLayout):
        """
        Initialize an AgentNode with an Agent entity and its layout.
        
        Args:
            agent: The Agent business entity
            layout: The NodeLayout containing visual properties
        """
        # Store agent-specific reference BEFORE super().__init__()
        # so that update_from_layout() can access it
        self.agent = agent
        
        super().__init__(agent, layout)
        
        # Override default colors based on agent type
        self._update_type_colors()
        
        # Add type indicator (small circle in corner)
        self.type_indicator = None
        self._init_type_indicator()


    def _update_type_colors(self) -> None:
        """Update node colors based on agent type (Subject or Object)."""
        if self.agent.typ == "Subject":
            self.SUBJECT_BG = self.SUBJECT_COLORS['bg']
            self.SUBJECT_BORDER = self.SUBJECT_COLORS['border']
        else:  # Object
            self.SUBJECT_BG = self.OBJECT_COLORS['bg']
            self.SUBJECT_BORDER = self.OBJECT_COLORS['border']
        
        # Apply colors
        self.setBrush(QBrush(self.SUBJECT_BG))
        self.setPen(QPen(self.SUBJECT_BORDER, 2))


    def _init_type_indicator(self) -> None:
        """Initialize the visual type indicator (small colored circle)."""
        if self.type_indicator:
            self.scene().removeItem(self.type_indicator)
        
        # Create indicator circle
        indicator_size = self.TYPE_INDICATOR_SIZE
        self.type_indicator = QGraphicsEllipseItem(
            0, 0, indicator_size, indicator_size, self
        )
        
        # Position in top-right corner
        margin = self.TYPE_INDICATOR_MARGIN
        self.type_indicator.setPos(
            self.rect().width() - indicator_size - margin,
            margin
        )
        
        # Set color based on type
        if self.agent.typ == "Subject":
            self.type_indicator.setBrush(QBrush(QColor(0, 150, 255)))
        else:
            self.type_indicator.setBrush(QBrush(QColor(200, 180, 0)))
        
        self.type_indicator.setPen(QPen(Qt.NoPen))
        
        # Make indicator non-selectable
        self.type_indicator.setFlag(QGraphicsRectItem.ItemIsSelectable, False)


    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.
        Overrides BaseNode to maintain type-specific colors.
        """
        if selected:
            # Use selection colors
            self.setPen(QPen(self.SELECTED_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.SELECTED_BG_COLOR))
        else:
            # Use type-specific colors
            self._update_type_colors()


    def update_from_layout(self) -> None:
        """Update the node's visual properties from its layout."""
        super().update_from_layout()
        # Re-apply type-specific colors
        self._update_type_colors()


    def get_type(self) -> str:
        """Get the agent type (Subject or Object)."""
        return self.agent.typ


    def set_type(self, agent_type: str) -> None:
        """
        Set the agent type and update visual appearance.
        
        Args:
            agent_type: Either "Subject" or "Object"
        """
        if agent_type in ["Subject", "Object"]:
            self.agent.typ = agent_type
            self._update_type_colors()
            self._init_type_indicator()


    # -------------------------------------------------------------------------
    # Agent-specific port methods
    # -------------------------------------------------------------------------
    
    def get_port_position(self, port_name: str) -> QPointF:
        """
        Get the scene position of a connection port.
        
        For AgentNode, provides specific port positions based on the
        agent's role in the narrative.
        
        Args:
            port_name: Name of the port ('left', 'right')
            
        Returns:
            Position of the port in scene coordinates
        """
        port_name = port_name.lower()
        
        if port_name == "left":
            return self.get_left_port_position()
        elif port_name == "right":
            return self.get_right_port_position()


    # -------------------------------------------------------------------------
    # Utility methods for agent-specific operations
    # -------------------------------------------------------------------------
    
    def set_description(self, description: str) -> None:
        """
        Set the agent's description.
        
        Args:
            description: The new description text
        """
        self.agent.desc = description


    def get_description(self) -> Optional[str]:
        """Get the agent's description."""
        return self.agent.desc


    def get_full_info(self) -> str:
        """
        Get a formatted string with all agent information.
        
        Returns:
            Formatted string with agent details
        """
        info = f"Agent: {self.agent.lb}\n"
        info += f"Type: {self.agent.typ}\n"
        if self.agent.desc:
            info += f"Description: {self.agent.desc}\n"
        return info
