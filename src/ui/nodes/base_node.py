# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : base_node.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Base Node for Planoscript.

This module provides the base class for all visual nodes displayed in the
workspace. It inherits from QGraphicsRectItem and adds functionality for:
- Storing a reference to the business entity and its visual layout
- Managing node appearance and behavior
- Handling selection and movement
- Supporting connection ports

All concrete node types (AgentNode, StateNode, EventNode) should inherit
from this class.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QGraphicsEllipseItem
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from typing import Optional, Any

from core.models.view_model import NodeLayout, NodeType


class BaseNode(QGraphicsRectItem):
    """
    Base class for all visual nodes in the workspace.
    
    This class combines a QGraphicsRectItem with business entity data and
    visual layout information. It serves as the foundation for all node types
    (Agent, State, Event, etc.).
    
    Attributes:
        entity: The business entity this node represents (Agent, State, Event)
        layout: The NodeLayout containing visual properties (position, size, etc.)
        label: QGraphicsTextItem for displaying the entity's name
        ports: Dictionary of connection ports (for future use)
    """
    
    # Default dimensions
    DEFAULT_WIDTH = 120.0
    DEFAULT_HEIGHT = 80.0
    
    # Default colors
    DEFAULT_BG_COLOR = QColor(240, 240, 240)  # Light gray
    DEFAULT_BORDER_COLOR = QColor(128, 128, 128)  # Medium gray
    DEFAULT_TEXT_COLOR = QColor(0, 0, 0)  # Black
    
    # Selection colors
    SELECTED_BG_COLOR = QColor(220, 230, 255)  # Light blue
    SELECTED_BORDER_COLOR = QColor(0, 120, 215)  # Blue
    
    # Font settings
    DEFAULT_FONT = QFont("Arial", 10)
    TITLE_FONT = QFont("Arial", 10, QFont.Bold)
    
    # Port settings
    PORT_SIZE = 8
    PORT_MARGIN = 4
    
    def __init__(self, entity: Any, layout: NodeLayout):
        """
        Initialize a base node with a business entity and its layout.
        
        Args:
            entity: The business entity (Agent, State, Event, etc.)
            layout: The NodeLayout containing visual properties
        """
        # Initialize QGraphicsRectItem with position and size from layout
        width = layout.width if layout.width > 0 else self.DEFAULT_WIDTH
        height = layout.height if layout.height > 0 else self.DEFAULT_HEIGHT
        super().__init__(0, 0, width, height)
        
        # Store references to business and visual models
        self.entity = entity
        self.layout = layout
        
        # Set initial position from layout
        self.setPos(layout.x, layout.y)
        
        # Enable movement and selection
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        # Set acceptance for hover events (useful for visual feedback)
        self.setAcceptHoverEvents(True)
        
        # Initialize appearance
        self._init_appearance()
        
        # Create and add label
        self.label = QGraphicsTextItem(self)
        self._init_label()
        
        # Initialize ports (empty dict, to be populated by subclasses if needed)
        self.ports = {}
        
        # Initialize visual input and output ports
        self.input_port = None  # QGraphicsEllipseItem for input port (left)
        self.output_port = None  # QGraphicsEllipseItem for output port (right)
        self._init_ports()
        
        # Update visual state based on layout
        self.update_from_layout()


    def _init_appearance(self) -> None:
        """Initialize the visual appearance of the node."""
        # Set default pen and brush
        self.setPen(QPen(self.DEFAULT_BORDER_COLOR, 2))
        self.setBrush(QBrush(self.DEFAULT_BG_COLOR))
        
        # Set rounded corners
        self.setRect(0, 0, self.rect().width(), self.rect().height())


    def _init_label(self) -> None:
        """Initialize the label with the entity's name."""
        # Get entity label (lb field is common to all entities)
        label_text = getattr(self.entity, 'lb', 'Unnamed')
        self.label.setPlainText(label_text)
        
        # Set label font and color
        self.label.setFont(self.TITLE_FONT)
        self.label.setDefaultTextColor(self.DEFAULT_TEXT_COLOR)
        
        # Position label at top-left with margin
        self.label.setPos(8, 8)
        
        # Make label non-selectable (selection is handled at node level)
        self.label.setFlag(QGraphicsItem.ItemIsSelectable, False)


    def _init_ports(self) -> None:
        """
        Initialize visual input and output ports as ellipse items.
        
        Creates two ports:
        - Input port (left side, red) for incoming connections
        - Output port (right side, green) for outgoing connections
        """
        port_size = self.PORT_SIZE
        
        # Input port (left side, centered vertically)
        self.input_port = QGraphicsEllipseItem(
            -port_size / 2,  # x: positioned at left edge
            self.rect().height() / 2 - port_size / 2,  # y: centered vertically
            port_size, port_size,
            self
        )
        self.input_port.setBrush(QBrush(QColor(255, 0, 0)))  # Red
        self.input_port.setPen(QPen(QColor(0, 0, 0)))  # Black border
        self.input_port.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.input_port.setFlag(QGraphicsItem.ItemIsMovable, False)
        
        # Output port (right side, centered vertically)
        self.output_port = QGraphicsEllipseItem(
            self.rect().width() - port_size / 2,  # x: positioned at right edge
            self.rect().height() / 2 - port_size / 2,  # y: centered vertically
            port_size, port_size,
            self
        )
        self.output_port.setBrush(QBrush(QColor(0, 255, 0)))  # Green
        self.output_port.setPen(QPen(QColor(0, 0, 0)))  # Black border
        self.output_port.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.output_port.setFlag(QGraphicsItem.ItemIsMovable, False)

    def update_from_layout(self) -> None:
        """
        Update the node's visual properties from its layout.
        
        This method should be called when the layout is modified externally
        or when loading a node from disk.
        """
        # Update position
        self.setPos(self.layout.x, self.layout.y)
        
        # Update size
        if self.layout.width > 0 and self.layout.height > 0:
            self.setRect(0, 0, self.layout.width, self.layout.height)
        
        # Update selection state
        self.setSelected(self.layout.selected)
        
        # Update color if specified
        if self.layout.color:
            try:
                color = QColor(self.layout.color)
                if color.isValid():
                    self.setBrush(QBrush(color))
            except (ValueError, AttributeError):
                pass
        
        # Update port positions when node size changes
        self._update_port_positions()


    def update_layout(self) -> None:
        """
        Update the layout object with the node's current properties.
        
        This should be called when the node is moved or resized to
        persist the changes to the layout model.
        """
        # Update position
        self.layout.x = self.x()
        self.layout.y = self.y()
        
        # Update size
        self.layout.width = self.rect().width()
        self.layout.height = self.rect().height()
        
        # Update selection state
        self.layout.selected = self.isSelected()


    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the node's appearance based on selection state.
        
        Args:
            selected: Whether the node is selected
        """
        if selected:
            self.setPen(QPen(self.SELECTED_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.SELECTED_BG_COLOR))
        else:
            self.setPen(QPen(self.DEFAULT_BORDER_COLOR, 2))
            self.setBrush(QBrush(self.DEFAULT_BG_COLOR))


    # -------------------------------------------------------------------------
    # QGraphicsItem overrides
    # -------------------------------------------------------------------------
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        # Call parent implementation first
        super().mousePressEvent(event)
        
        # Update selection appearance
        self.set_selected_appearance(self.isSelected())


    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release events."""
        super().mouseReleaseEvent(event)
        
        # Update layout after movement
        if self.isSelected():
            self.update_layout()


    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events (during drag)."""
        super().mouseMoveEvent(event)
        
        # Update layout during movement
        if event.buttons() == Qt.LeftButton:
            self.update_layout()


    def hoverEnterEvent(self, event) -> None:
        """Handle hover enter events."""
        # Visual feedback for hover
        self.setPen(QPen(QColor(0, 120, 215), 2))  # Blue border on hover
        super().hoverEnterEvent(event)


    def hoverLeaveEvent(self, event) -> None:
        """Handle hover leave events."""
        # Restore normal appearance
        if not self.isSelected():
            self.setPen(QPen(self.DEFAULT_BORDER_COLOR, 2))
        super().hoverLeaveEvent(event)


    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """
        Handle item changes (e.g., selection, position).
        
        This is called automatically by Qt when certain properties change.
        """
        if change == QGraphicsItem.ItemSelectedChange:
            self.set_selected_appearance(bool(value))
            self.layout.selected = bool(value)
        elif change == QGraphicsItem.ItemPositionChange:
            # Constrains the movement to the limits of the scene (absolute limit)
            new_pos = value
            scene = self.scene()
            if scene:
                scene_rect = scene.sceneRect()
                # Use self.rect() for dimensions (independent of position)
                node_width = self.rect().width()
                node_height = self.rect().height()
                
                # Constraints to keep the node ENTIRELY within the scene
                max_x = scene_rect.right() - node_width
                max_y = scene_rect.bottom() - node_height
                min_x = scene_rect.left()
                min_y = scene_rect.top()
                
                constrained_x = max(min_x, min(new_pos.x(), max_x))
                constrained_y = max(min_y, min(new_pos.y(), max_y))
                
                # Update the layout with the constrained position.
                self.layout.x = constrained_x
                self.layout.y = constrained_y
                
                return QPointF(constrained_x, constrained_y)
        
        return super().itemChange(change, value)


    # -------------------------------------------------------------------------
    # Connection port methods (for future use)
    # -------------------------------------------------------------------------
    
    def get_port_position(self, port_name: str) -> QPointF:
        """
        Get the scene position of a connection port.
        
        This method should be overridden by subclasses to provide
        specific port positions based on their layout.
        
        Args:
            port_name: Name of the port (e.g., 'left', 'right')
            
        Returns:
            Position of the port in scene coordinates
        """
        # Default implementation: return center of the node
        return self.sceneBoundingRect().center()


    def _update_port_positions(self) -> None:
        """
        Update the positions of input and output ports based on current node size.
        
        This should be called whenever the node is resized.
        """
        if self.input_port and self.output_port:
            port_size = self.PORT_SIZE
            node_height = self.rect().height()
            
            # Position input port (left side)
            self.input_port.setRect(
                -port_size / 2,
                node_height / 2 - port_size / 2,
                port_size, port_size
            )
            
            # Position output port (right side)
            self.output_port.setRect(
                self.rect().width() - port_size / 2,
                node_height / 2 - port_size / 2,
                port_size, port_size
            )

    def get_left_port_position(self) -> QPointF:
        """Get the position of the left connection port (input port)."""
        if self.input_port:
            return self.input_port.scenePos()
        rect = self.sceneBoundingRect()
        return QPointF(rect.left(), rect.center().y())


    def get_right_port_position(self) -> QPointF:
        """Get the position of the right connection port (output port)."""
        if self.output_port:
            return self.output_port.scenePos()
        rect = self.sceneBoundingRect()
        return QPointF(rect.right(), rect.center().y())


    def add_port(self, name: str, position: QPointF) -> None:
        """
        Add a connection port to the node.
        
        Args:
            name: Name of the port
            position: Position relative to the node (0-1 in both axes)
        """
        self.ports[name] = position

    def get_port(self, name: str) -> Optional[QPointF]:
        """
        Get the position of a port by name.
        
        Args:
            name: Name of the port
            
        Returns:
            Position of the port in node coordinates, or None if not found
        """
        return self.ports.get(name)


    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    
    def center(self) -> QPointF:
        """Get the center position of the node in scene coordinates."""
        return self.sceneBoundingRect().center()


    def set_entity_label(self, text: str) -> None:
        """
        Update the label text.
        
        Args:
            text: New text for the label
        """
        self.label.setPlainText(text)
        # Update entity's lb if it has one
        if hasattr(self.entity, 'lb'):
            self.entity.lb = text


    def get_entity_label(self) -> str:
        """Get the current label text."""
        return self.label.toPlainText()
