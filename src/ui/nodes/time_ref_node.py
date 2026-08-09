# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : time_ref_node.py
# Version      : 1
# Date         : 22-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Time Reference Node for Planoscript.

This module provides the TimeRefNode class, which represents a Time_ref entity
in the visual workspace. It inherits from BaseNode and adds Time_ref-specific
features such as reference indicators and time-specific styling.

Time references represent temporal points or periods in the narrative structure,
and can be linked to States and Events.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from typing import Optional

from core.models.data_model import Time_ref
from core.models.view_model import NodeLayout
from ui.nodes.base_node import BaseNode


class TimeRefNode(BaseNode):
    """
    Visual representation of a Time_ref entity in the workspace.
    
    This class extends BaseNode to provide Time_ref-specific visual styling
    and behavior. Time references are displayed with an orange/amber color scheme
    to distinguish them from other entity types.
    
    Attributes:
        entity: The Time_ref business entity
        layout: The NodeLayout containing visual properties
        prev_indicator: Optional indicator for previous time reference
    """
    
    # Color scheme for time references
    TIME_REF_COLORS = {
        'bg': QColor(255, 240, 220),    # Light orange/amber
        'border': QColor(255, 150, 0),   # Orange
        'text': QColor(0, 0, 0)         # Black
    }
    
    # Selection colors (maintain time theme)
    SELECTED_BG_COLOR = QColor(255, 220, 180)  # Lighter orange
    SELECTED_BORDER_COLOR = QColor(255, 180, 0)   # Brighter orange
    
    # Indicator settings
    INDICATOR_SIZE = 12
    INDICATOR_MARGIN = 4
    
    def __init__(self, time_ref: Time_ref, layout: NodeLayout):
        """
        Initialize a TimeRefNode with a Time_ref entity and its layout.
        
        Args:
            time_ref: The Time_ref business entity
            layout: The NodeLayout containing visual properties
        """
        # Store time_ref-specific reference and indicator BEFORE super().__init__()
        # so that update_from_layout() can access them
        self.time_ref = time_ref
        self.prev_indicator = None
        
        super().__init__(time_ref, layout)
        
        # Override default colors for time references
        self._update_time_ref_colors()
        
        # Initialize previous reference indicator (attribute already exists)
        self._init_prev_indicator()

    def _update_time_ref_colors(self) -> None:
        """Update node colors to use time_ref-specific scheme."""
        self.setBrush(QBrush(self.TIME_REF_COLORS['bg']))
        self.setPen(QPen(self.TIME_REF_COLORS['border'], 2))
        
        # Update label color
        if self.label:
            self.label.setDefaultTextColor(self.TIME_REF_COLORS['text'])

    def _init_prev_indicator(self) -> None:
        """Initialize visual indicator for previous time reference."""
        # Remove existing indicator if any
        if self.prev_indicator:
            if self.prev_indicator.scene():
                self.prev_indicator.scene().removeItem(self.prev_indicator)
        
        # Create indicator if this time_ref has a previous time_ref
        if self.time_ref.prev_id and self.time_ref.prev_id > 0:
            self.prev_indicator = QGraphicsEllipseItem(
                0, 0, self.INDICATOR_SIZE, self.INDICATOR_SIZE, self
            )
            self.prev_indicator.setPos(
                self.rect().width() - self.INDICATOR_SIZE - self.INDICATOR_MARGIN,
                self.INDICATOR_MARGIN
            )
            self.prev_indicator.setBrush(QBrush(QColor(255, 200, 0)))  # Gold
            self.prev_indicator.setPen(QPen(Qt.NoPen))
            self.prev_indicator.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.prev_indicator.setToolTip(f"Previous Time Ref: {self.time_ref.prev_id}")

    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.
        Overrides BaseNode to maintain time_ref-specific colors.
        """
        if selected:
            self.setPen(QPen(self.SELECTED_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.SELECTED_BG_COLOR))
        else:
            self._update_time_ref_colors()

    def update_from_layout(self) -> None:
        """Update the node's visual properties from its layout."""
        super().update_from_layout()
        # Re-apply time_ref-specific colors
        self._update_time_ref_colors()
        # Re-initialize indicators in case references changed
        self._init_prev_indicator()

    # -------------------------------------------------------------------------
    # Time_ref-specific methods
    # -------------------------------------------------------------------------
    
    def get_prev_id(self) -> Optional[int]:
        """Get the previous time reference ID."""
        return self.time_ref.prev_id if self.time_ref.prev_id > 0 else None

    def set_prev_id(self, prev_id: int) -> None:
        """
        Set the previous time reference ID and update indicators.
        
        Args:
            prev_id: The new previous time reference ID
        """
        self.time_ref.prev_id = prev_id
        self._init_prev_indicator()

    def set_description(self, description: str) -> None:
        """
        Set the time reference's description.
        
        Args:
            description: The new description text
        """
        self.time_ref.desc = description

    def get_description(self) -> Optional[str]:
        """Get the time reference's description."""
        return self.time_ref.desc

    def get_full_info(self) -> str:
        """
        Get a formatted string with all time reference information.
        
        Returns:
            Formatted string with time reference details
        """
        info = f"Time Ref: {self.time_ref.lb}\n"
        if self.time_ref.prev_id and self.time_ref.prev_id > 0:
            info += f"Previous: {self.time_ref.prev_id}\n"
        if self.time_ref.desc:
            info += f"Description: {self.time_ref.desc}\n"
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
        elif port_name == "top":
            return self.get_top_port_position()
        elif port_name == "bottom":
            return self.get_bottom_port_position()
        else:
            return self.get_center_port_position()
