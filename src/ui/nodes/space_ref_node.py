# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : space_ref_node.py
# Version      : 1
# Date         : 22-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Space Reference Node for Planoscript.

This module provides the SpaceRefNode class, which represents a Space_ref entity
in the visual workspace. It inherits from BaseNode and adds Space_ref-specific
features such as space-specific styling.

Space references represent spatial locations or areas in the narrative structure,
and can be linked to States and Events.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from typing import Optional

from core.models.data_model import Space_ref
from core.models.view_model import NodeLayout
from ui.nodes.base_node import BaseNode


class SpaceRefNode(BaseNode):
    """
    Visual representation of a Space_ref entity in the workspace.
    
    This class extends BaseNode to provide Space_ref-specific visual styling
    and behavior. Space references are displayed with a teal/turquoise color scheme
    to distinguish them from other entity types.
    
    Attributes:
        entity: The Space_ref business entity
        layout: The NodeLayout containing visual properties
    """
    
    # Color scheme for space references
    SPACE_REF_COLORS = {
        'bg': QColor(220, 255, 255),    # Light teal/turquoise
        'border': QColor(0, 180, 180),    # Teal
        'text': QColor(0, 0, 0)         # Black
    }
    
    # Selection colors (maintain space theme)
    SELECTED_BG_COLOR = QColor(200, 255, 255)  # Lighter teal
    SELECTED_BORDER_COLOR = QColor(0, 200, 200)   # Brighter teal
    
    def __init__(self, space_ref: Space_ref, layout: NodeLayout):
        """
        Initialize a SpaceRefNode with a Space_ref entity and its layout.
        
        Args:
            space_ref: The Space_ref business entity
            layout: The NodeLayout containing visual properties
        """
        # Store space_ref-specific reference BEFORE super().__init__()
        # so that update_from_layout() can access it
        self.space_ref = space_ref
        
        super().__init__(space_ref, layout)
        
        # Override default colors for space references
        self._update_space_ref_colors()

    def _update_space_ref_colors(self) -> None:
        """Update node colors to use space_ref-specific scheme."""
        self.setBrush(QBrush(self.SPACE_REF_COLORS['bg']))
        self.setPen(QPen(self.SPACE_REF_COLORS['border'], 2))
        
        # Update label color
        if self.label:
            self.label.setDefaultTextColor(self.SPACE_REF_COLORS['text'])

    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.
        Overrides BaseNode to maintain space_ref-specific colors.
        """
        if selected:
            self.setPen(QPen(self.SELECTED_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.SELECTED_BG_COLOR))
        else:
            self._update_space_ref_colors()

    def update_from_layout(self) -> None:
        """Update the node's visual properties from its layout."""
        super().update_from_layout()
        # Re-apply space_ref-specific colors
        self._update_space_ref_colors()

    # -------------------------------------------------------------------------
    # Space_ref-specific methods
    # -------------------------------------------------------------------------
    
    def set_description(self, description: str) -> None:
        """
        Set the space reference's description.
        
        Args:
            description: The new description text
        """
        self.space_ref.desc = description

    def get_description(self) -> Optional[str]:
        """Get the space reference's description."""
        return self.space_ref.desc

    def get_full_info(self) -> str:
        """
        Get a formatted string with all space reference information.
        
        Returns:
            Formatted string with space reference details
        """
        info = f"Space Ref: {self.space_ref.lb}\n"
        if self.space_ref.desc:
            info += f"Description: {self.space_ref.desc}\n"
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
