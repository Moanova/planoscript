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
in the visual workspace. It inherits from BaseNode and adds State-specific
features such as reference indicators and state-specific styling.

States represent conditions or situations in the narrative, and can be
linked to time and space references.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from typing import Optional

from core.models.data_model import State
from core.models.view_model import NodeLayout
from ui.nodes.base_node import BaseNode


class StateNode(BaseNode):
    """
    Visual representation of a State entity in the workspace.
    
    This class extends BaseNode to provide State-specific visual styling
    and behavior. States are displayed with a green color scheme to
    distinguish them from Agents and other entity types.
    
    Attributes:
        entity: The State business entity
        layout: The NodeLayout containing visual properties
        time_ref_indicator: Optional indicator for time reference
        space_ref_indicator: Optional indicator for space reference
    """
    
    # Color scheme for states
    STATE_COLORS = {
        'bg': QColor(220, 255, 220),    # Light green
        'border': QColor(0, 180, 0),     # Green
        'text': QColor(0, 0, 0)         # Black
    }
    
    # Selection colors (maintain state theme)
    SELECTED_BG_COLOR = QColor(200, 255, 200)  # Lighter green
    SELECTED_BORDER_COLOR = QColor(0, 200, 0)   # Brighter green
    
    # Indicator settings
    INDICATOR_SIZE = 12
    INDICATOR_MARGIN = 4
    INDICATOR_SPACING = 20
    
    def __init__(self, state: State, layout: NodeLayout):
        """
        Initialize a StateNode with a State entity and its layout.
        
        Args:
            state: The State business entity
            layout: The NodeLayout containing visual properties
        """
        # Store state-specific reference and indicators BEFORE super().__init__()
        # so that update_from_layout() can access them
        self.state = state
        
        super().__init__(state, layout)
        
        # Override default colors for states
        self._update_state_colors()
        
        # Initialize reference indicators (attributes already exist)
        #self._init_reference_indicators()


    def _update_state_colors(self) -> None:
        """Update node colors to use state-specific scheme."""
        self.setBrush(QBrush(self.STATE_COLORS['bg']))
        self.setPen(QPen(self.STATE_COLORS['border'], 2))
        
        # Update label color
        if self.label:
            self.label.setDefaultTextColor(self.STATE_COLORS['text'])


    def _init_reference_indicators(self) -> None:
        """Initialize visual indicators for time and space references."""
        pass


    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.
        Overrides BaseNode to maintain state-specific colors.
        """
        if selected:
            self.setPen(QPen(self.SELECTED_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.SELECTED_BG_COLOR))
        else:
            self._update_state_colors()


    def update_from_layout(self) -> None:
        """Update the node's visual properties from its layout."""
        super().update_from_layout()
        # Re-apply state-specific colors
        self._update_state_colors()
        # Re-initialize indicators in case references changed
        #self._init_reference_indicators()


    # -------------------------------------------------------------------------
    # State-specific methods
    # -------------------------------------------------------------------------
    
    def get_time_ref_id(self) -> Optional[int]:
        """Get the time reference ID."""
        return self.state.time_ref_id if self.state.time_ref_id > 0 else None


    def get_space_ref_id(self) -> Optional[int]:
        """Get the space reference ID."""
        return self.state.space_ref_id if self.state.space_ref_id else None


    #def set_time_ref_id(self, time_ref_id: int) -> None:
    #    """
    #    Set the time reference ID and update indicators.
    #    
    #    Args:
    #        time_ref_id: The new time reference ID
    #    """
    #    self.state.time_ref_id = time_ref_id
    #    self._init_reference_indicators()


    #def set_space_ref_id(self, space_ref_id: Optional[int]) -> None:
    #    """
    #    Set the space reference ID and update indicators.
    #    
    #    Args:
    #        space_ref_id: The new space reference ID (can be None)
    #    """
    #    self.state.space_ref_id = space_ref_id
    #    self._init_reference_indicators()


    def set_description(self, description: str) -> None:
        """
        Set the state's description.
        
        Args:
            description: The new description text
        """
        self.state.desc = description


    def get_description(self) -> Optional[str]:
        """Get the state's description."""
        return self.state.desc


    def get_full_info(self) -> str:
        """
        Get a formatted string with all state information.
        
        Returns:
            Formatted string with state details
        """
        info = f"State: {self.state.lb}\n"
        if self.state.desc:
            info += f"Description: {self.state.desc}\n"
        return info


    # -------------------------------------------------------------------------
    # Port methods
    # -------------------------------------------------------------------------
    
    def get_port_position(self, port_name: str) -> QPointF:
        """
        Get the scene position of a connection port.
        
        Args:
            port_name: Name of the port ('left', 'right', 'top', 'bottom', 'center')
            
        Returns:
            Position of the port in scene coordinates
        """
        port_name = port_name.lower()
        
        if port_name == "left":
            return self.get_left_port_position()
        elif port_name == "right":
            return self.get_right_port_position()
