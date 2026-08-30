# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_workspace.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# ---------------------------------------------------------------------
# Version      : 2
# Date         : 30-08-2026
# Content      : Rework in progress
# Build        : TSC
# ---------------------------------------------------------------------
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QFrame,
    QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon

from core.models.view_model import NodeType
from ui.nodes.agent_node import AgentNode
from ui.nodes.state_node import StateNode
from ui.nodes.event_node import EventNode

class JourneyWorkspace(QGraphicsView):
    """Central workspace with infinite scrolling and dynamic grid"""
    
    def __init__(self, initial_width=2000, initial_height=1600, narrative_map=None):
        super().__init__()

        self.narrative_map = narrative_map

        self.initial_width = initial_width
        self.initial_height = initial_height
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Store grid lines for selective removal
        self.grid_lines = []

        self.setStyleSheet("""
            /* Barres de défilement */
            QScrollBar:horizontal {
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
                margin: 0px;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f0f0f0;
                border-radius: 4px;
                margin: 0px;
                border: none;
            }

            /* Poignée (slider) */
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 4px;
                min-width: 20px;
            } 
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }

            /* Boutons +/- (flèches de défilement) */
            QScrollBar::add-line, QScrollBar::sub-line {
                background: #e0e0e0;
                border: none;
                border-radius: 4px;
                height: 4px;  /* Height for vertical the bar */
                width: 4px;   /* Width for the norizontal bar */
            }

            /* Flèches pour les boutons */
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 4px;
                height: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height:4px;
                width: 4px;
            }

            /* Positionnement des flèches */
            QScrollBar::sub-line:horizontal {
                subcontrol-position: left;
            }
            QScrollBar::add-line:horizontal {
                subcontrol-position: right;
            }
            QScrollBar::sub-line:vertical {
                subcontrol-position: top;
            }
            QScrollBar::add-line:vertical {
                subcontrol-position: bottom;
            }

            /* Style des flèches (icônes) */
            QScrollBar::add-line, QScrollBar::sub-line {
                background: #e0e0e0;
            }
            QScrollBar::add-line:hover, QScrollBar::sub-line:hover {
                background: #d0d0d0;
            }
            QScrollBar::add-line:pressed, QScrollBar::sub-line:pressed {
                background: #b0b0b0;
            }
        """)


        # Initial scene size - fixed to 4000x4000 to ensure scrollbars are active by default
        self.scene_rect_margin = 200  # Margin around items when expanding scene
        self.setSceneRect(0, 0, 4000, 4000)
        self._draw_grid()

        # Always show scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Center the view on the initial workspace
        self.centerOn(2000, 2000)
        
        # Connect scroll events to redraw grid
        self.horizontalScrollBar().valueChanged.connect(self._draw_grid)
        self.verticalScrollBar().valueChanged.connect(self._draw_grid)

        # Enable drag-and-drop for items
        self.setAcceptDrops(True)

        # Deactivate RubberBandDrag to avoid multiple selection
        self.setDragMode(QGraphicsView.NoDrag)

        # Track scene boundaries
        self.min_scene_size = QSizeF(800, 600)

        # Style
        self.setRenderHint(QPainter.Antialiasing)


    def _draw_grid(self):
        """Draw grid lines only for the visible viewport area"""
        # Clear only the grid lines, not all scene items
        for line in self.grid_lines:
            if self.scene.items().count(line):  # Check if line still exists in scene
                self.scene.removeItem(line)
        self.grid_lines.clear()
        
        # Get the visible area in scene coordinates
        viewport_rect = self.viewport().rect()
        scene_rect = self.mapToScene(viewport_rect).boundingRect()
        
        # Add margin to avoid artifacts at edges
        margin = 100
        scene_rect.adjust(-margin, -margin, margin, margin)
        
        grid_size = 20
        subgrid_size = 80

        # Main grid (20px)
        pen_main = QPen(QColor("#e0e0e0"))
        pen_main.setWidth(1)
        
        # Vertical lines
        start_x = int(scene_rect.left() - (scene_rect.left() % grid_size))
        for x in range(start_x, int(scene_rect.right()) + grid_size, grid_size):
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen_main)
            line.setZValue(-1)  # Draw below nodes
            self.grid_lines.append(line)
        
        # Horizontal lines
        start_y = int(scene_rect.top() - (scene_rect.top() % grid_size))
        for y in range(start_y, int(scene_rect.bottom()) + grid_size, grid_size):
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen_main)
            line.setZValue(-1)  # Draw below nodes
            self.grid_lines.append(line)

        # Subgrid (80px)
        pen_sub = QPen(QColor("#808080"))
        pen_sub.setWidth(1)
        
        # Vertical subgrid lines
        start_x = int(scene_rect.left() - (scene_rect.left() % subgrid_size))
        for x in range(start_x, int(scene_rect.right()) + subgrid_size, subgrid_size):
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen_sub)
            line.setZValue(-1)  # Drow below nodes
            self.grid_lines.append(line)
        
        # Horizontal subgrid lines
        start_y = int(scene_rect.top() - (scene_rect.top() % subgrid_size))
        for y in range(start_y, int(scene_rect.bottom()) + subgrid_size, subgrid_size):
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen_sub)
            line.setZValue(-1)  # Draw below nodes
            self.grid_lines.append(line)


    def resizeEvent(self, event):
        """Handle window resize: redraw grid for new visible area"""
        super().resizeEvent(event)
        self._draw_grid()


    def _expand_scene_to_include(self, x: float, y: float, margin: int = None):
        """
        Dynamically expands sceneRect to include the point (x, y). 
        Expansion occurs ONLY in the direction(s) where the point extends beyond the current bounds. 

        Args:
            x: X-coordinate of the point to include
            y: Y-coordinate of the point to include
            margin: Margin to apply (uses self.scene_rect_margin if None)
        """
        if margin is None:
            margin = self.scene_rect_margin
            
        current_rect = self.sceneRect()
        new_rect = current_rect
        expanded = False
        
        # Extend to the LEFT if x - margin < current_rect.left()
        if x - margin < new_rect.left():
            new_rect.setLeft(x - margin)
            expanded = True
        
        # Extend to the RIGHT if x + margin > current_rect.right()
        if x + margin > new_rect.right():
            new_rect.setRight(x + margin)
            expanded = True
        
        # Expand UPWARDS if y - margin < current_rect.top()
        if y - margin < new_rect.top():
            new_rect.setTop(y - margin)
            expanded = True
        
        # Expand downwards if y + margin > current_rect.bottom()
        if y + margin > new_rect.bottom():
            new_rect.setBottom(y + margin)
            expanded = True
        
        # Apply the new size if necessary
        if expanded:
            self.setSceneRect(new_rect)


    def ensure_visible(self, x: float, y: float, margin: int = 200):
        """
        Infinite scrolling: simply center the view if (x, y) is outside visible area.
        Does not modify scene boundaries.
        """
        # Convert scene coordinates to viewport coordinates
        viewport_rect = self.viewport().rect()
        viewport_pos = self.mapFromScene(QPointF(x, y))
        
        # If the point is outside the visible viewport, center on it
        if not viewport_rect.contains(viewport_pos):
            self.centerOn(x, y)


    def add_item_at(self, x: float, y: float, item: QGraphicsItem):
        """Add an item to the scene and expand scene if needed"""
        self.scene.addItem(item)
        item.setPos(x, y)
        self._expand_scene_to_include(x, y)
        self.ensure_visible(x, y)


    def mouseMoveEvent(self, event):
        # 1. Let Qt handle the node movement FIRST.
        super().mouseMoveEvent(event)

        # 2. Auto-scrolling + constraint + dynamic scene expansion
        if event.buttons() == Qt.LeftButton:
            # Auto-scrolling when the mouse is near the viewport edges
            viewport_rect = self.viewport().rect()
            mouse_viewport_pos = event.position().toPoint()
            scroll_margin = 50
            scroll_speed = 20

            # Check the edges
            near_left = mouse_viewport_pos.x() < scroll_margin
            near_right = mouse_viewport_pos.x() > viewport_rect.width() - scroll_margin
            near_top = mouse_viewport_pos.y() < scroll_margin
            near_bottom = mouse_viewport_pos.y() > viewport_rect.height() - scroll_margin

            # Auto-scroll
            if near_left:
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - scroll_speed
                )
            elif near_right:
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() + scroll_speed
                )

            if near_top:
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - scroll_speed
                )
            elif near_bottom:
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() + scroll_speed
                )
            # 3. Dynamically expand the scene if an item exceeds the boundaries
            # For each selected and movable item, check and expand if necessary
            for item in self.scene.selectedItems():
                if not (item.flags() & QGraphicsItem.ItemIsMovable):
                    continue
                
                # Current position of the item in scene coordinates
                item_pos = item.scenePos()
                # _expand_scene_to_include uses self.sceneRect() in real time
                # and checks for itself whether expansion is necessary
                self._expand_scene_to_include(item_pos.x(), item_pos.y())


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)


    def mousePressEvent(self, event):
        """
        Manages the single selection of components and connections. 
            - If a selectable item (node ​​or connection) is clicked → select it and deselect all others
            - If empty space is clicked → deselect everything
        """
        # Retrieve the item under the cursor
        item = self.itemAt(event.position().toPoint())
        
        # Call the parent method first so that Qt handles the click normally
        super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            if item is None:
                # Click on empty space: deselect all
                self._clear_all_selections()
            elif item.isEnabled() and item.isVisible():
                # Check if it is a selectable item (node ​​or connection)
                if item.flags() & QGraphicsItem.ItemIsSelectable:
                    # Select only this item
                    self._select_item_only(item)


    def create_node_from_data(self, node_data: dict):
        """
        Creates a visual node from the data returned by the use case. 

        Args:
            node_data: Dictionary containing:
            - 'entity': the business entity
            - 'layout': NodeLayout
            - 'node_type': NodeType
            - 'component_type': str (optional)
        """
        entity = node_data['entity']
        layout = node_data['layout']
        node_type = node_data['node_type']

        # Mapping NodeType -> Visual node class
        NODE_CLASS_MAPPING = {
            NodeType.AGENT: AgentNode,
            NodeType.STATE: StateNode,
            NodeType.EVENT: EventNode
        }

        node_class = NODE_CLASS_MAPPING.get(node_type)
        if not node_class:
            print(f"Unknown node type: {node_type}")
            return None

        # Create the visual node
        node = node_class(entity, layout)

        # Add to the scene
        self.add_item_at(layout.x, layout.y, node)
        
        # Select the new node and deselect the others
        self._select_item_only(node)

        return node


    def create_connection_from_data(self, connection_data: dict):
        """
        Creates a visual connection based on the data returned by the use case. 

        Args:
            connection_data: Dictionary containing:
            - 'connection_layout': ConnectionLayout
            - 'source_entity': source entity
            - 'target_entity': target entity
        """
        from ui.nodes.connection import Connection  # Check if this class exists

        connection_layout = connection_data['connection_layout']
        source_entity = connection_data['source_entity']
        target_entity = connection_data['target_entity']

        # Find the corresponding visual nodes in the scene
        source_node = self._find_node_by_entity_id(source_entity.id)
        target_node = self._find_node_by_entity_id(target_entity.id)

        if not source_node or not target_node:
            print("Source or target node not found")
            return None

        # Create the visual connection
        connection = Connection(connection_layout)

        # Position the connection
        self.scene.addItem(connection)
        connection.update_path(source_node, target_node)
        
        # Select the new connection and deselect the others
        self._select_item_only(connection)

        return connection


    def _find_node_by_entity_id(self, entity_id: int):
        """Find a node in the scene by its entity_id."""
        for item in self.scene.items():
            if hasattr(item, 'entity') and item.entity.id == entity_id:
                return item
        return None


    def _select_item_only(self, item):
        """
        Selects only the specified item and deselects all others. 

        Args:
            item: The QGraphicsItem to select.
        """
        # Deselect all selectable items
        for existing_item in self.scene.items():
            if (existing_item != item and 
                existing_item.flags() & QGraphicsItem.ItemIsSelectable and
                existing_item.isEnabled()):
                existing_item.setSelected(False)
        
        # Select the specified item
        if item.flags() & QGraphicsItem.ItemIsSelectable:
            item.setSelected(True)


    def _clear_all_selections(self):
        """
        Deselects all selectable items in the scene.
        """
        for item in self.scene.items():
            if (item.flags() & QGraphicsItem.ItemIsSelectable and 
                item.isEnabled()):
                item.setSelected(False)
