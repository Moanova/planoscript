# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : tree_visual.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Tree Visual for Planoscript.

This module provides the TreeVisual class, which represents a visual container
for relation trees (e.g., State_event_set, Journey) in the workspace.

A TreeVisual groups multiple nodes and connections together into a single
visual container with a title, border, and background. It maintains references
to the business model tree entity and its visual layout.

The tree container automatically resizes to fit its contents and can be
moved, selected, and collapsed/expanded by the user.
"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath
from typing import Optional, Dict, List, Any

from core.models.tree_layout import TreeLayout
from core.models.data_model import State_event_set, State_event_subset
from ui.nodes.base_node import BaseNode
from ui.nodes.connection import Connection


class TreeVisual(QGraphicsRectItem):
    """
    Visual container for a relation tree (e.g., State_event_set, Journey).
    
    This class represents a group of nodes and connections as a single
    visual entity with a title, border, and background. The tree can be
    moved, selected, and collapsed/expanded.
    
    Attributes:
        tree_entity: The business tree entity (State_event_set, Journey, etc.)
        layout: The TreeLayout containing visual properties
        title_item: QGraphicsTextItem for the tree title
        nodes: Dictionary of node_id -> BaseNode
        connections: Dictionary of connection_id -> Connection
        is_collapsed: Whether the tree content is hidden
    """
    
    # Visual settings
    TITLE_HEIGHT = 30
    PADDING = 15
    BORDER_RADIUS = 8
    BORDER_WIDTH = 2
    
    # Colors
    DEFAULT_BG_COLOR = QColor(240, 248, 255)  # Alice blue
    DEFAULT_BORDER_COLOR = QColor(100, 149, 237)  # Cornflower blue
    TITLE_BG_COLOR = QColor(173, 216, 230)  # Light blue
    TITLE_TEXT_COLOR = QColor(0, 0, 0)
    SELECTED_BORDER_COLOR = QColor(0, 100, 200)
    COLLAPSED_BG_COLOR = QColor(220, 230, 241)
    
    # Font
    TITLE_FONT = QFont("Arial", 11, QFont.Bold)
    COLLAPSE_BUTTON_SIZE = 20
    
    def __init__(self, tree_entity: Any, layout: TreeLayout):
        """
        Initialize a TreeVisual with a tree entity and its layout.
        
        Args:
            tree_entity: The business tree entity (State_event_set, Journey, etc.)
            layout: The TreeLayout containing visual properties
        """
        # Initialize with default size from layout
        width = layout.width if layout.width > 0 else 400
        height = layout.height if layout.height > 0 else 300
        super().__init__(0, 0, width, height)
        
        # Store references
        self.tree_entity = tree_entity
        self.layout = layout
        self.is_collapsed = layout.collapsed
        
        # Set position from layout
        self.setPos(layout.x, layout.y)
        
        # Set z-value (trees appear behind nodes)
        self.setZValue(layout.z_index if layout.z_index < 0 else -10)
        
        # Enable selection and movement
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Set appearance
        self._init_appearance()
        
        # Create title
        self.title_item = QGraphicsTextItem(self)
        self._init_title()
        
        # Create collapse/expand button
        self.collapse_button = QGraphicsRectItem(self)
        self._init_collapse_button()
        
        # Store nodes and connections
        self.nodes: Dict[int, BaseNode] = {}
        self.connections: Dict[str, Connection] = {}
        
        # Set background brush with rounded corners
        self.set_rounded_corners()

    def _init_appearance(self) -> None:
        """Initialize the visual appearance from the layout."""
        # Set colors
        if self.layout.color:
            try:
                bg_color = QColor(self.layout.color)
                if bg_color.isValid():
                    self.DEFAULT_BG_COLOR = bg_color
            except (ValueError, AttributeError):
                pass
        
        # Set background
        self.setBrush(QBrush(self.DEFAULT_BG_COLOR))
        self.setPen(QPen(self.DEFAULT_BORDER_COLOR, self.BORDER_WIDTH))

    def set_rounded_corners(self) -> None:
        """Set a rounded rectangle shape for the tree container."""
        path = QPainterPath()
        path.addRoundedRect(
            self.rect(),
            self.BORDER_RADIUS,
            self.BORDER_RADIUS
        )
        self.setPath(path)

    def _init_title(self) -> None:
        """Initialize the title text item."""
        self._update_title()
        
        # Set font and color
        self.title_item.setFont(self.TITLE_FONT)
        self.title_item.setDefaultTextColor(self.TITLE_TEXT_COLOR)
        
        # Position at top-left with padding
        self.title_item.setPos(self.PADDING, (self.TITLE_HEIGHT - self.title_item.boundingRect().height()) / 2)
        
        # Make title non-selectable
        self.title_item.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def _init_collapse_button(self) -> None:
        """Initialize the collapse/expand button."""
        button_size = self.COLLAPSE_BUTTON_SIZE
        
        # Position at top-right
        self.collapse_button.setRect(
            self.rect().width() - button_size - self.PADDING,
            (self.TITLE_HEIGHT - button_size) / 2,
            button_size,
            button_size
        )
        
        # Set appearance
        self.collapse_button.setPen(QPen(self.DEFAULT_BORDER_COLOR))
        self.collapse_button.setBrush(QBrush(self.TITLE_BG_COLOR))
        
        # Make button non-selectable (handled by tree selection)
        self.collapse_button.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.collapse_button.setFlag(QGraphicsItem.ItemIsMovable, False)
        
        # Update button text
        self._update_collapse_button()

    def _update_title(self) -> None:
        """Update the title based on tree entity and type."""
        if self.tree_entity and hasattr(self.tree_entity, 'id'):
            if isinstance(self.tree_entity, State_event_set):
                title = f"Arbre État-Événement #{self.tree_entity.id}"
            elif isinstance(self.tree_entity, Journey):
                title = f"Arbre Parcours #{self.tree_entity.id}"
            else:
                title = f"Arbre {self.layout.tree_type} #{self.tree_entity.id}"
        else:
            title = self.layout.title if self.layout.title else f"Nouvel Arbre ({self.layout.tree_type})"
        
        self.title_item.setPlainText(title)

    def _update_collapse_button(self) -> None:
        """Update the collapse/expand button text."""
        if self.is_collapsed:
            self.collapse_button.setPlainText("+")
        else:
            self.collapse_button.setPlainText("−")
        
        # Center text in button
        text_item = self.collapse_button.findChild(QGraphicsTextItem)
        if not text_item:
            text_item = QGraphicsTextItem(self.collapse_button)
            text_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        text_item.setPlainText(self.collapse_button.plainText())
        text_item.setPos(
            (self.collapse_button.rect().width() - text_item.boundingRect().width()) / 2,
            (self.collapse_button.rect().height() - text_item.boundingRect().height()) / 2
        )

    def add_node(self, node: BaseNode) -> None:
        """
        Add a node to the tree.
        
        Args:
            node: The BaseNode to add
        """
        if node.entity.id not in self.nodes:
            self.nodes[node.entity.id] = node
            node.setParentItem(self)
            self.layout.add_node(node.entity.id)
            self._resize_to_fit()

    def remove_node(self, node_id: int) -> bool:
        """
        Remove a node from the tree.
        
        Args:
            node_id: The ID of the node to remove
            
        Returns:
            True if the node was removed, False otherwise
        """
        if node_id in self.nodes:
            node = self.nodes.pop(node_id)
            node.setParentItem(None)
            self.layout.remove_node(node_id)
            self._resize_to_fit()
            return True
        return False

    def get_node(self, node_id: int) -> Optional[BaseNode]:
        """Get a node by its ID."""
        return self.nodes.get(node_id)

    def add_connection(self, connection: Connection) -> None:
        """
        Add a connection to the tree.
        
        Args:
            connection: The Connection to add
        """
        if connection.layout.id not in self.connections:
            self.connections[connection.layout.id] = connection
            connection.setParentItem(self)
            self.layout.add_connection(connection.layout.id)
            self._resize_to_fit()

    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection from the tree.
        
        Args:
            connection_id: The ID of the connection to remove
            
        Returns:
            True if the connection was removed, False otherwise
        """
        if connection_id in self.connections:
            connection = self.connections.pop(connection_id)
            connection.setParentItem(None)
            self.layout.remove_connection(connection_id)
            self._resize_to_fit()
            return True
        return False

    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get a connection by its ID."""
        return self.connections.get(connection_id)

    def _resize_to_fit(self) -> None:
        """
        Resize the tree container to fit all its contents.
        
        If the tree is collapsed, only show the title bar.
        """
        if not self.nodes and not self.connections:
            # No content, use default size
            self.setRect(0, 0, self.layout.width, self.layout.height)
            return
        
        if self.is_collapsed:
            # Only show title bar
            self.setRect(
                0, 0,
                max(self.layout.width, 200),
                self.TITLE_HEIGHT
            )
            return
        
        # Calculate bounding rect of all children (nodes and connections)
        children_rect = self.childrenBoundingRect()
        
        if children_rect.isNull():
            # No children or children not positioned yet
            self.setRect(0, 0, self.layout.width, self.layout.height)
            return
        
        # Add padding and title height
        new_width = max(
            children_rect.width() + 2 * self.PADDING,
            self.layout.width,
            200  # Minimum width
        )
        new_height = max(
            children_rect.height() + self.TITLE_HEIGHT + 2 * self.PADDING,
            self.layout.height,
            self.TITLE_HEIGHT + 2 * self.PADDING  # Minimum height (title bar)
        )
        
        # Set new size
        self.setRect(0, 0, new_width, new_height)
        
        # Update layout
        self.layout.width = new_width
        self.layout.height = new_height
        
        # Reposition collapse button
        self._init_collapse_button()

    def toggle_collapse(self) -> None:
        """Toggle the collapsed state of the tree."""
        self.is_collapsed = not self.is_collapsed
        self.layout.collapsed = self.is_collapsed
        self._update_collapse_button()
        
        # Show/hide children
        for child in self.childItems():
            if child != self.title_item and child != self.collapse_button:
                child.setVisible(not self.is_collapsed)
        
        # Resize to fit
        self._resize_to_fit()

    def update_layout(self) -> None:
        """
        Update the layout object with the tree's current properties.
        
        This should be called when the tree is moved or resized to
        persist the changes to the layout model.
        """
        self.layout.x = self.x()
        self.layout.y = self.y()
        self.layout.width = self.rect().width()
        self.layout.height = self.rect().height()
        self.layout.collapsed = self.is_collapsed

    def set_title(self, title: str) -> None:
        """
        Set the tree title.
        
        Args:
            title: The new title
        """
        self.layout.title = title
        self._update_title()

    def get_title(self) -> str:
        """Get the tree title."""
        return self.title_item.toPlainText()

    # -------------------------------------------------------------------------
    # QGraphicsItem overrides
    # -------------------------------------------------------------------------
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        # Check if collapse button was clicked
        if self.collapse_button.contains(self.collapse_button.mapFromScene(event.scenePos())):
            self.toggle_collapse()
            event.accept()
            return
        
        # Otherwise, handle normally
        super().mousePressEvent(event)

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

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """
        Handle item changes (e.g., selection, position).
        """
        if change == QGraphicsItem.ItemSelectedChange:
            # Update border color based on selection
            if value:
                self.setPen(QPen(self.SELECTED_BORDER_COLOR, self.BORDER_WIDTH))
            else:
                self.setPen(QPen(self.DEFAULT_BORDER_COLOR, self.BORDER_WIDTH))
        
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None) -> None:
        """
        Paint the tree container with rounded corners and title background.
        """
        # Draw the main shape (already set via path in set_rounded_corners)
        super().paint(painter, option, widget)
        
        # Draw title background
        title_rect = QRectF(
            0, 0,
            self.rect().width(),
            self.TITLE_HEIGHT
        )
        
        # Create a rounded rectangle for the title bar
        title_path = QPainterPath()
        title_path.addRoundedRect(
            title_rect,
            self.BORDER_RADIUS,
            self.BORDER_RADIUS
        )
        
        # Fill title bar
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.TITLE_BG_COLOR))
        painter.drawPath(title_path)
        
        # Draw border between title and content
        painter.setPen(QPen(self.DEFAULT_BORDER_COLOR))
        painter.drawLine(
            0, self.TITLE_HEIGHT,
            self.rect().width(), self.TITLE_HEIGHT
        )

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    
    def contains_node(self, node_id: int) -> bool:
        """Check if the tree contains a specific node."""
        return node_id in self.nodes

    def contains_connection(self, connection_id: str) -> bool:
        """Check if the tree contains a specific connection."""
        return connection_id in self.connections

    def get_all_nodes(self) -> List[BaseNode]:
        """Get all nodes in the tree."""
        return list(self.nodes.values())

    def get_all_connections(self) -> List[Connection]:
        """Get all connections in the tree."""
        return list(self.connections.values())

    def clear(self) -> None:
        """Remove all nodes and connections from the tree."""
        # Remove all nodes
        for node_id, node in list(self.nodes.items()):
            self.remove_node(node_id)
        
        # Remove all connections
        for conn_id, connection in list(self.connections.items()):
            self.remove_connection(conn_id)
        
        # Clear layout references
        self.layout.clear()
        
        # Resize to default
        self.setRect(0, 0, 400, self.TITLE_HEIGHT if self.is_collapsed else 300)
