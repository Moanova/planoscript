# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : event_node.py
# Version      : 1
# Date         : 22-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Event Node for Planoscript.

This module provides the EventNode class, which represents an Event entity
in the visual workspace. It inherits from BaseNode and adds Event-specific
features such as reference indicators and event-specific styling.

Events represent occurrences or happenings in the narrative, and can be
linked to time and space references, similar to States.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from typing import Optional

from core.models.data_model import Event
from core.models.view_model import NodeLayout
from ui.nodes.base_node import BaseNode


class EventNode(BaseNode):
    """
    Visual representation of an Event entity in the workspace.
    
    This class extends BaseNode to provide Event-specific visual styling
    and behavior. Events are displayed with a purple/magenta color scheme
    to distinguish them from Agents (blue/yellow) and States (green).
    
    Attributes:
        entity: The Event business entity
        layout: The NodeLayout containing visual properties
        time_ref_indicator: Optional indicator for time reference
        space_ref_indicator: Optional indicator for space reference
    """
    
    # Color scheme for events
    EVENT_COLORS = {
        'bg': QColor(240, 220, 255),    # Light lavender/purple
        'border': QColor(180, 0, 200),    # Purple
        'text': QColor(0, 0, 0)         # Black
    }
    
    # Selection colors (maintain event theme)
    SELECTED_BG_COLOR = QColor(220, 200, 255)  # Lighter lavender
    SELECTED_BORDER_COLOR = QColor(200, 0, 255)   # Brighter purple
    
    # Indicator settings
    INDICATOR_SIZE = 12
    INDICATOR_MARGIN = 4
    INDICATOR_SPACING = 20
    
    def __init__(self, event: Event, layout: NodeLayout):
        """
        Initialize an EventNode with an Event entity and its layout.
        
        Args:
            event: The Event business entity
            layout: The NodeLayout containing visual properties
        """
        # Store event-specific reference and indicators BEFORE super().__init__()
        # so that update_from_layout() can access them
        self.event = event
        self.time_ref_indicator = None
        self.space_ref_indicator = None
        
        super().__init__(event, layout)
        
        # Override default colors for events
        self._update_event_colors()
        
        # Initialize reference indicators (attributes already exist)
        self._init_reference_indicators()

    def _update_event_colors(self) -> None:
        """Update node colors to use event-specific scheme."""
        self.setBrush(QBrush(self.EVENT_COLORS['bg']))
        self.setPen(QPen(self.EVENT_COLORS['border'], 2))
        
        # Update label color
        if self.label:
            self.label.setDefaultTextColor(self.EVENT_COLORS['text'])

    def _init_reference_indicators(self) -> None:
        """Initialize visual indicators for time and space references."""
        # Remove existing indicators if any
        if self.time_ref_indicator:
            if self.time_ref_indicator.scene():
                self.time_ref_indicator.scene().removeItem(self.time_ref_indicator)
        if self.space_ref_indicator:
            if self.space_ref_indicator.scene():
                self.space_ref_indicator.scene().removeItem(self.space_ref_indicator)
        
        # Create time reference indicator if event has a time reference
        if self.event.time_ref_id and self.event.time_ref_id > 0:
            self.time_ref_indicator = QGraphicsEllipseItem(
                0, 0, self.INDICATOR_SIZE, self.INDICATOR_SIZE, self
            )
            self.time_ref_indicator.setPos(
                self.rect().width() - self.INDICATOR_SIZE - self.INDICATOR_MARGIN,
                self.INDICATOR_MARGIN
            )
            self.time_ref_indicator.setBrush(QBrush(QColor(180, 0, 200)))  # Purple
            self.time_ref_indicator.setPen(QPen(Qt.NoPen))
            self.time_ref_indicator.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.time_ref_indicator.setToolTip(f"Time Ref: {self.event.time_ref_id}")
        
        # Create space reference indicator if event has a space reference
        if self.event.space_ref_id and self.event.space_ref_id > 0:
            self.space_ref_indicator = QGraphicsEllipseItem(
                0, 0, self.INDICATOR_SIZE, self.INDICATOR_SIZE, self
            )
            # Position below time indicator, or at same position if no time ref
            y_pos = self.INDICATOR_MARGIN
            if self.time_ref_indicator:
                y_pos += self.INDICATOR_SIZE + self.INDICATOR_SPACING
            
            self.space_ref_indicator.setPos(
                self.rect().width() - self.INDICATOR_SIZE - self.INDICATOR_MARGIN,
                y_pos
            )
            self.space_ref_indicator.setBrush(QBrush(QColor(100, 150, 255)))  # Blue
            self.space_ref_indicator.setPen(QPen(Qt.NoPen))
            self.space_ref_indicator.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.space_ref_indicator.setToolTip(f"Space Ref: {self.event.space_ref_id}")

    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.
        Overrides BaseNode to maintain event-specific colors.
        """
        if selected:
            self.setPen(QPen(self.SELECTED_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.SELECTED_BG_COLOR))
        else:
            self._update_event_colors()

    def update_from_layout(self) -> None:
        """Update the node's visual properties from its layout."""
        super().update_from_layout()
        # Re-apply event-specific colors
        self._update_event_colors()
        # Re-initialize indicators in case references changed
        self._init_reference_indicators()

    # -------------------------------------------------------------------------
    # Event-specific methods
    # -------------------------------------------------------------------------
    
    def get_time_ref_id(self) -> Optional[int]:
        """Get the time reference ID."""
        return self.event.time_ref_id if self.event.time_ref_id > 0 else None

    def get_space_ref_id(self) -> Optional[int]:
        """Get the space reference ID."""
        return self.event.space_ref_id if self.event.space_ref_id else None

    def set_time_ref_id(self, time_ref_id: int) -> None:
        """
        Set the time reference ID and update indicators.
        
        Args:
            time_ref_id: The new time reference ID
        """
        self.event.time_ref_id = time_ref_id
        self._init_reference_indicators()

    def set_space_ref_id(self, space_ref_id: Optional[int]) -> None:
        """
        Set the space reference ID and update indicators.
        
        Args:
            space_ref_id: The new space reference ID (can be None)
        """
        self.event.space_ref_id = space_ref_id
        self._init_reference_indicators()

    def set_description(self, description: str) -> None:
        """
        Set the event's description.
        
        Args:
            description: The new description text
        """
        self.event.desc = description

    def get_description(self) -> Optional[str]:
        """Get the event's description."""
        return self.event.desc

    def get_full_info(self) -> str:
        """
        Get a formatted string with all event information.
        
        Returns:
            Formatted string with event details
        """
        info = f"Event: {self.event.lb}\n"
        if self.event.time_ref_id and self.event.time_ref_id > 0:
            info += f"Time Ref: {self.event.time_ref_id}\n"
        if self.event.space_ref_id:
            info += f"Space Ref: {self.event.space_ref_id}\n"
        if self.event.desc:
            info += f"Description: {self.event.desc}\n"
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
