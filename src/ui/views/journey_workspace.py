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
    QVBoxLayout, QPushButton, QGraphicsPathItem
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF, QRectF, Signal, QObject
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon, QPainterPath

from core.models.view_model import NodeType, ConnectionLayout, ConnectionStyle, PortPosition
from ui.nodes.agent_node import AgentNode
from ui.nodes.state_node import StateNode
from ui.nodes.event_node import EventNode
from ui.nodes.connection import Connection


class JourneyWorkspace(QGraphicsView, QObject):
    """Central workspace with infinite scrolling and dynamic grid"""
    
    # Signal emitted when a relation is created between two nodes
    relation_created = Signal(object, object)
    
    def __init__(self, initial_width=2000, initial_height=1600, narrative_map=None):
        super().__init__()
        QObject.__init__(self)

        self.narrative_map = narrative_map

        self.initial_width = initial_width
        self.initial_height = initial_height
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Store grid lines for selective removal
        self.grid_lines = []

        self.setStyleSheet("""
            /* Barres de d\u00e9filement */
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

            /* Poign\u00e9e (slider) */
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

            /* Boutons +/- (fl\u00e8ches de d\u00e9filement) */
            QScrollBar::add-line, QScrollBar::sub-line {
                background: #e0e0e0;
                border: none;
                border-radius: 4px;
                height: 4px;
                width: 4px;
            }

            /* Fl\u00e8ches pour les boutons */
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 4px;
                height: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height:4px;
                width: 4px;
            }

            /* Positionnement des fl\u00e8ches */
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

            /* Style des fl\u00e8ches (ic\u00f4nes) */
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
        self.scene_rect_margin = 200
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
        
        # Relation creation mode attributes
        self.relation_creation_mode = False
        self.temp_connection = None
        self.source_node = None
        self.waiting_for_source = False
        self.waiting_for_target = False
        
        # Style
        self.setRenderHint(QPainter.Antialiasing)


    def _draw_grid(self):
        """Draw grid lines only for the visible viewport area"""
        for line in self.grid_lines:
            if self.scene.items().count(line):
                self.scene.removeItem(line)
        self.grid_lines.clear()
        
        viewport_rect = self.viewport().rect()
        scene_rect = self.mapToScene(viewport_rect).boundingRect()
        
        margin = 100
        scene_rect.adjust(-margin, -margin, margin, margin)
        
        grid_size = 20
        subgrid_size = 80

        pen_main = QPen(QColor("#e0e0e0"))
        pen_main.setWidth(1)
        
        start_x = int(scene_rect.left() - (scene_rect.left() % grid_size))
        for x in range(start_x, int(scene_rect.right()) + grid_size, grid_size):
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen_main)
            line.setZValue(-1)
            self.grid_lines.append(line)
        
        start_y = int(scene_rect.top() - (scene_rect.top() % grid_size))
        for y in range(start_y, int(scene_rect.bottom()) + grid_size, grid_size):
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen_main)
            line.setZValue(-1)
            self.grid_lines.append(line)

        pen_sub = QPen(QColor("#808080"))
        pen_sub.setWidth(1)
        
        start_x = int(scene_rect.left() - (scene_rect.left() % subgrid_size))
        for x in range(start_x, int(scene_rect.right()) + subgrid_size, subgrid_size):
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen_sub)
            line.setZValue(-1)
            self.grid_lines.append(line)
        
        start_y = int(scene_rect.top() - (scene_rect.top() % subgrid_size))
        for y in range(start_y, int(scene_rect.bottom()) + subgrid_size, subgrid_size):
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen_sub)
            line.setZValue(-1)
            self.grid_lines.append(line)


    def resizeEvent(self, event):
        """Handle window resize: redraw grid for new visible area"""
        super().resizeEvent(event)
        self._draw_grid()


    def _expand_scene_to_include(self, x: float, y: float, margin: int = None):
        """
        Dynamically expands sceneRect to include the point (x, y).
        """
        if margin is None:
            margin = self.scene_rect_margin
            
        current_rect = self.sceneRect()
        new_rect = current_rect
        expanded = False
        
        if x - margin < new_rect.left():
            new_rect.setLeft(x - margin)
            expanded = True
        if x + margin > new_rect.right():
            new_rect.setRight(x + margin)
            expanded = True
        if y - margin < new_rect.top():
            new_rect.setTop(y - margin)
            expanded = True
        if y + margin > new_rect.bottom():
            new_rect.setBottom(y + margin)
            expanded = True
        
        if expanded:
            self.setSceneRect(new_rect)


    def ensure_visible(self, x: float, y: float, margin: int = 200):
        """Infinite scrolling: center the view if (x, y) is outside visible area."""
        viewport_rect = self.viewport().rect()
        viewport_pos = self.mapFromScene(QPointF(x, y))
        
        if not viewport_rect.contains(viewport_pos):
            self.centerOn(x, y)


    def add_item_at(self, x: float, y: float, item: QGraphicsItem):
        """Add an item to the scene and expand scene if needed"""
        self.scene.addItem(item)
        item.setPos(x, y)
        self._expand_scene_to_include(x, y)
        self.ensure_visible(x, y)


    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        # Handle rubber band connection in relation creation mode
        if self.relation_creation_mode and self.temp_connection and self.source_node:
            mouse_scene_pos = self.mapToScene(event.position().toPoint())
            self._update_temp_connection(mouse_scene_pos)

        # Auto-scrolling when mouse is near viewport edges
        if event.buttons() == Qt.LeftButton:
            viewport_rect = self.viewport().rect()
            mouse_viewport_pos = event.position().toPoint()
            scroll_margin = 50
            scroll_speed = 20

            near_left = mouse_viewport_pos.x() < scroll_margin
            near_right = mouse_viewport_pos.x() > viewport_rect.width() - scroll_margin
            near_top = mouse_viewport_pos.y() < scroll_margin
            near_bottom = mouse_viewport_pos.y() > viewport_rect.height() - scroll_margin

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
            
            for item in self.scene.selectedItems():
                if not (item.flags() & QGraphicsItem.ItemIsMovable):
                    continue
                item_pos = item.scenePos()
                self._expand_scene_to_include(item_pos.x(), item_pos.y())


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)


    def mousePressEvent(self, event):
        """
        Manages selection and relation creation.
        - Normal mode: select items
        - Relation mode: handle port selection for rubber band connection
        """
        item = self.itemAt(event.position().toPoint())
        
        # In relation creation mode, handle port selection
        if self.relation_creation_mode and event.button() == Qt.LeftButton:
            self._handle_relation_port_selection(item, event)
            return
        
        super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            if item is None:
                self._clear_all_selections()
            elif item.isEnabled() and item.isVisible():
                if item.flags() & QGraphicsItem.ItemIsSelectable:
                    self._select_item_only(item)

    # -------------------------------------------------------------------------
    # Relation creation methods
    # -------------------------------------------------------------------------

    def enter_relation_creation_mode(self):
        """Enter relation creation mode to create connections between nodes."""
        self.relation_creation_mode = True
        self.waiting_for_source = True
        self.waiting_for_target = False
        self.source_node = None
        self._clear_temp_connection()
        self.setCursor(Qt.CrossCursor)


    def exit_relation_creation_mode(self):
        """Exit relation creation mode and clean up."""
        self.relation_creation_mode = False
        self.waiting_for_source = False
        self.waiting_for_target = False
        self.source_node = None
        self._clear_temp_connection()
        self.setCursor(Qt.ArrowCursor)


    def _handle_relation_port_selection(self, item, event):
        """
        Handle port selection during relation creation.
        Detects clicks on input/output ports and manages the connection flow.
        """
        port_clicked = False
        parent_node = None
        
        # Check if clicked item is a port (QGraphicsEllipseItem child of a node)
        if item and isinstance(item, QGraphicsEllipseItem):
            parent = item.parentItem()
            if parent and hasattr(parent, 'entity'):
                parent_node = parent
                port_clicked = True
        
        if port_clicked and parent_node:
            if self.waiting_for_source:
                # First port clicked = source node
                self.source_node = parent_node
                self.waiting_for_source = False
                self.waiting_for_target = True
                
                # Create temporary connection from source port
                mouse_scene_pos = self.mapToScene(event.position().toPoint())
                self._create_temp_connection(
                    self.source_node.get_right_port_position(),
                    mouse_scene_pos
                )
                
            elif self.waiting_for_target and self.source_node:
                # Second port clicked = target node
                target_node = parent_node
                
                if target_node != self.source_node:
                    # Emit signal to create the relation
                    self.relation_created.emit(self.source_node, target_node)
                
                # Clean up
                self.exit_relation_creation_mode()
        elif event.button() == Qt.RightButton:
            # Right click cancels relation creation
            self.exit_relation_creation_mode()


    def _create_temp_connection(self, start_pos: QPointF, end_pos: QPointF):
        """Create a temporary connection for rubber band effect."""
        self._clear_temp_connection()
        
        # Create temporary connection layout
        temp_layout = ConnectionLayout(
            id="temp_connection",
            source_node_id=-1,
            source_port=PortPosition.RIGHT,
            target_node_id=-1,
            target_port=PortPosition.LEFT,
            style=ConnectionStyle.STRAIGHT,
            color="#808080",
            thickness=2.0,
            z_index=100,
            selected=False
        )
        
        # Create the temporary connection
        self.temp_connection = Connection(temp_layout)
        self.scene.addItem(self.temp_connection)
        self.temp_connection.setZValue(100)
        
        # Set initial path
        self._update_temp_connection(end_pos)


    def _update_temp_connection(self, end_pos: QPointF):
        """Update temporary connection path to follow mouse position."""
        if self.temp_connection and self.source_node:
            start_pos = self.source_node.get_right_port_position()
            path = QPainterPath()
            path.moveTo(start_pos)
            path.lineTo(end_pos)
            self.temp_connection.setPath(path)


    def _clear_temp_connection(self):
        """Remove temporary connection if it exists."""
        if self.temp_connection:
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None


    def create_node_from_data(self, node_data: dict):
        """
        Creates a visual node from the data returned by the use case.
        """
        entity = node_data['entity']
        layout = node_data['layout']
        node_type = node_data['node_type']

        NODE_CLASS_MAPPING = {
            NodeType.AGENT: AgentNode,
            NodeType.STATE: StateNode,
            NodeType.EVENT: EventNode
        }

        node_class = NODE_CLASS_MAPPING.get(node_type)
        if not node_class:
            print(f"Unknown node type: {node_type}")
            return None

        node = node_class(entity, layout)
        self.add_item_at(layout.x, layout.y, node)
        self._select_item_only(node)

        return node


    def create_connection_from_data(self, connection_data: dict):
        """
        Creates a visual connection based on the data returned by the use case.
        """
        connection_layout = connection_data['connection_layout']
        source_entity = connection_data['source_entity']
        target_entity = connection_data['target_entity']

        source_node = self._find_node_by_entity_id(source_entity.id)
        target_node = self._find_node_by_entity_id(target_entity.id)

        if not source_node or not target_node:
            print("Source or target node not found")
            return None

        connection = Connection(connection_layout)
        self.scene.addItem(connection)
        connection.update_path(source_node, target_node)
        self._select_item_only(connection)

        return connection


    def _find_node_by_entity_id(self, entity_id: int):
        """Find a node in the scene by its entity_id."""
        for item in self.scene.items():
            if hasattr(item, 'entity') and item.entity.id == entity_id:
                return item
        return None


    def _select_item_only(self, item):
        """Selects only the specified item and deselects all others."""
        for existing_item in self.scene.items():
            if (existing_item != item and 
                existing_item.flags() & QGraphicsItem.ItemIsSelectable and
                existing_item.isEnabled()):
                existing_item.setSelected(False)
        
        if item.flags() & QGraphicsItem.ItemIsSelectable:
            item.setSelected(True)


    def _clear_all_selections(self):
        """Deselects all selectable items in the scene."""
        for item in self.scene.items():
            if (item.flags() & QGraphicsItem.ItemIsSelectable and 
                item.isEnabled()):
                item.setSelected(False)
