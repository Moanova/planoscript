# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : events_workspace.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# ---------------------------------------------------------------------
# Version      : 2
# Date         : 30-08-2026
# Content      : Rework in progress
# Build        : TSC
# ---------------------------------------------------------------------
import logging

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsItem,
    QFrame, QMenu
)
from PySide6.QtCore import Qt, QPointF, Signal, QObject, QEvent
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPainterPath

from core.models.view_model import NodeType, ConnectionLayout, WorkspaceLayout, RelationType
from core.models.data_model import State, Event
from core.services.layout_service import LayoutService
from ui.nodes.state_node import StateNode
from ui.nodes.event_node import EventNode
from ui.nodes.connection import Connection
from ui.utils import theme
from config.config_loader import get as _get_config

_GRID_MINOR_SIZE = _get_config("grid_minor_size", 20)
_GRID_MAJOR_SIZE = _get_config("grid_major_size", 80)
_GRID_MINOR_COLOR = _get_config("grid_minor_color", theme.BG_PRIMARY.replace("1E1E1E", "333333"))
_GRID_MAJOR_COLOR = _get_config("grid_major_color", "#333333")
_TEMP_CONNECTION_COLOR = _get_config("temp_connection_color", theme.CONNECTION_COLOR)
_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)

logger = logging.getLogger(__name__)


class EventsWorkspace(QGraphicsView, QObject):
    """Central workspace with infinite scrolling and dynamic grid"""
    
    # Signal emitted when a relation is created between two nodes
    relation_created = Signal(object, object)

    # Signal emitted when a node is moved (for project modification tracking)
    workspace_modified = Signal()
    # Emitted when the user requests to show a state in the agents view
    # (TSK10, cross-view navigation)
    focusStateInAgentsViewRequested = Signal(int)  # state_id
    
    def __init__(self, initial_width=2000, initial_height=1600, narrative_map=None, info_bar=None, main_window=None):
        super().__init__()

        # No frame: the default QFrame StyledPanel border was drawn in
        # light gray (e.g. bottom-left corner above the info bar)
        self.setFrameShape(QFrame.NoFrame)

        self.narrative_map = narrative_map
        self.info_bar = info_bar
        self.main_window = main_window

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Canvas background: dark theme primary (charter 98)
        self.scene.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))

        # Store grid lines for selective removal
        self.grid_lines = []

        # Scrollbars: dark theme (charter 98). The stylesheet also
        # fills the view frame (area uncovered by the rounded
        # scrollbars and the corner between them) with the canvas
        # color — otherwise the default light window color shows
        # through at the bottom-left corner, above the info bar
        # (TSK12 point 01)
        self.setStyleSheet(theme.WORKSPACE_STYLESHEET)
        # A plain QWidget subclass does not paint its stylesheet
        # background unless WA_StyledBackground is set
        self.setAttribute(Qt.WA_StyledBackground, True)


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
        
        grid_size = _GRID_MINOR_SIZE
        subgrid_size = _GRID_MAJOR_SIZE

        pen_main = QPen(QColor(_GRID_MINOR_COLOR))
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

        pen_sub = QPen(QColor(_GRID_MAJOR_COLOR))
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


    def viewportEvent(self, event):
        """
        Swallow Qt's delayed automatic tooltip event.

        Node tooltips are shown instantly by the items themselves (see
        BaseNode.hoverEnterEvent). Letting the automatic mechanism run
        would pop a second tooltip at the cursor position when the
        mouse rests, on top of the one already displayed.
        """
        if event.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(event)


    # ------------------------------------------------------------------
    # Cross-view navigation focus (TSK10, RG067)
    # ------------------------------------------------------------------

    def set_focus(self, state_ids) -> None:
        """
        Highlight the nodes of the given states and dim the rest
        (TSK10, RG067).

        The focus is a temporary visual state: it does not select the
        nodes (the selection stays untouched, RG043), does not mark the
        project as modified and is not persisted (RG067).

        Args:
            state_ids: Iterable of State IDs to highlight
        """
        self.clear_focus()
        self._focused_state_ids = set(state_ids)
        for item in self.scene.items():
            # Entity IDs are unique per type, not globally (State.id=1
            # and Event.id=1 can coexist): only state nodes may stay
            # highlighted, so the lookup must filter on StateNode
            if isinstance(item, StateNode) and item.entity.id in self._focused_state_ids:
                item.setOpacity(1.0)
            else:
                item.setOpacity(0.25)

    def clear_focus(self) -> None:
        """
        Release the focus and restore normal appearances (RG067).
        """
        self._focused_state_ids = set()
        for item in self.scene.items():
            item.setOpacity(1.0)

    def has_focus(self) -> bool:
        """
        Return True if a navigation focus is currently active.
        """
        return bool(getattr(self, '_focused_state_ids', set()))

    def mousePressEvent(self, event):
        """
        Manages selection and relation creation.
        - Normal mode: select items
        - Relation mode: handle port selection for rubber band connection
        """
        item = self.itemAt(event.position().toPoint())
        
        # RG067: clicking empty space releases the navigation focus
        if item is None and self.has_focus():
            self.clear_focus()
        
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
        Only allows connections from output port (right) to input port (left).
        """
        port_clicked = False
        parent_node = None
        is_output_port = False
        
        # Debug: Print what was clicked
        if item:
            logger.debug("Clicked on item of type %s", type(item).__name__)
        else:
            logger.debug("Clicked on empty space (no item)")
        
        # Get all items at the click position (from bottom to top)
        # This allows us to ignore the temp connection and find ports/nodes below it
        all_items = self.items(event.position().toPoint())
        
        # Find the first relevant item (port or node), ignoring the temp connection
        target_item = None
        for candidate in reversed(all_items):  # Check from top to bottom
            if candidate == self.temp_connection:
                continue  # Skip the temporary connection line
            
            if isinstance(candidate, QGraphicsEllipseItem):
                parent = candidate.parentItem()
                if parent and hasattr(parent, 'entity') and hasattr(parent, 'output_port') and hasattr(parent, 'input_port'):
                    target_item = candidate
                    break
            elif hasattr(candidate, 'entity') and hasattr(candidate, 'output_port') and hasattr(candidate, 'input_port'):
                target_item = candidate
                break
        
        # If we clicked directly on a port or node, use it
        if target_item:
            item = target_item
        # Otherwise, the click might be on temp connection covering a port - check all nodes for proximity
        elif item:
            # The original item might be the temp connection - check all nodes for proximity to ports
            logger.debug("Checking all nodes for port proximity (temp connection may be covering port)")
            mouse_scene_pos = self.mapToScene(event.position().toPoint())
            for scene_item in self.scene.items():
                if scene_item == self.temp_connection:
                    continue
                if hasattr(scene_item, 'entity') and hasattr(scene_item, 'output_port') and hasattr(scene_item, 'input_port'):
                    if scene_item.output_port and scene_item.input_port:
                        output_port_pos = scene_item.get_right_port_position()
                        input_port_pos = scene_item.get_left_port_position()
                        threshold = 15
                        
                        if (mouse_scene_pos - output_port_pos).manhattanLength() < threshold:
                            item = scene_item
                            parent_node = scene_item
                            is_output_port = True
                            port_clicked = True
                            break
                        elif (mouse_scene_pos - input_port_pos).manhattanLength() < threshold:
                            item = scene_item
                            parent_node = scene_item
                            is_output_port = False
                            port_clicked = True
                            break
        
        # Check if clicked item is a port (QGraphicsEllipseItem child of a node)
        # OR if a node was clicked and the click is near one of its ports
        if item and not (port_clicked and parent_node):
            # Case 1: item is directly a port
            if isinstance(item, QGraphicsEllipseItem):
                parent = item.parentItem()
                if parent and hasattr(parent, 'entity') and hasattr(parent, 'output_port') and hasattr(parent, 'input_port'):
                    parent_node = parent
                    # Check if this is the output port (right side, green)
                    if item == parent.output_port:
                        is_output_port = True
                        port_clicked = True
                    elif item == parent.input_port:
                        is_output_port = False
                        port_clicked = True
            
            # Case 2: item is a node, check if click is near one of its ports
            elif hasattr(item, 'entity') and hasattr(item, 'output_port') and hasattr(item, 'input_port'):
                # Check if ports exist
                if not item.output_port or not item.input_port:
                    # Node doesn't have valid ports
                    pass
                else:
                    mouse_scene_pos = self.mapToScene(event.position().toPoint())
                    output_port_pos = item.get_right_port_position()
                    input_port_pos = item.get_left_port_position()
                    
                    # Threshold distance to consider a port click (in pixels)
                    threshold = 15
                    
                    # Check distance to output port
                    if (mouse_scene_pos - output_port_pos).manhattanLength() < threshold:
                        parent_node = item
                        is_output_port = True
                        port_clicked = True
                    # Check distance to input port
                    elif (mouse_scene_pos - input_port_pos).manhattanLength() < threshold:
                        parent_node = item
                        is_output_port = False
                        port_clicked = True
        
        if port_clicked and parent_node:
            if self.waiting_for_source:
                # First port clicked must be an OUTPUT port (right side)
                if is_output_port:
                    self.source_node = parent_node
                    self.waiting_for_source = False
                    self.waiting_for_target = True
                    
                    # Create temporary connection from source output port
                    mouse_scene_pos = self.mapToScene(event.position().toPoint())
                    self._create_temp_connection(
                        self.source_node.get_right_port_position(),
                        mouse_scene_pos
                    )
                else:
                    # Clicked on input port first - invalid, cancel
                    if self.info_bar:
                        self.info_bar.show_message("Please click on an output port (green) first")
                    self.exit_relation_creation_mode()
                    
            elif self.waiting_for_target and self.source_node:
                # Second port clicked must be an INPUT port (left side)
                if not is_output_port:
                    # Second port clicked = target node
                    target_node = parent_node
                    
                    if target_node != self.source_node:
                        # Emit signal to create the relation
                        logger.debug("Emitting relation_created signal with source=%s, target=%s",
                                     self.source_node.entity.lb, target_node.entity.lb)
                        self.relation_created.emit(self.source_node, target_node)
                    else:
                        # Clicked on the same node - invalid
                        self.info_bar.show_message("Cannot connect a node to itself")
                    
                    # Clean up
                    self.exit_relation_creation_mode()
                else:
                    # Clicked on output port second - invalid, cancel
                    if self.info_bar:
                        self.info_bar.show_message("Please click on an input port (red) for the target")
                    self.exit_relation_creation_mode()
        else:
            # Click on grid or non-port element -> cancel relation creation
            if self.info_bar:
                if self.waiting_for_source:
                    self.info_bar.show_message("Relation creation cancelled - click on an output port (green)")
                elif self.waiting_for_target:
                    self.info_bar.show_message("Relation creation cancelled - click on an input port (red)")
                else:
                    self.info_bar.show_message("Relation creation cancelled")
            self.exit_relation_creation_mode()


    def _create_temp_connection(self, start_pos: QPointF, end_pos: QPointF):
        """Create a temporary connection for rubber band effect."""
        self._clear_temp_connection()
        
        # Create a simple QGraphicsPathItem for temporary connection (no need for full Connection class)
        path = QPainterPath()
        path.moveTo(start_pos)
        path.lineTo(end_pos)
        
        # Dashed line style for rubber band effect
        pen = QPen(QColor(_TEMP_CONNECTION_COLOR), 2, Qt.DashLine)
        pen.setDashPattern(Connection.DASH_PATTERN)
        self.temp_connection = self.scene.addPath(path, pen)
        self.temp_connection.setZValue(100)  # Ensure it's on top


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


    def create_node_from_data(self, node_data: dict,
                              skip_overlap_check: bool = False,
                              select: bool = True):
        """
        Creates a visual node from the data returned by the use case.

        Args:
            node_data: Dictionary with 'entity', 'layout', 'node_type' keys
            skip_overlap_check: Skip RG044 non-overlapping adjustment
                (used when loading saved positions)
            select: Select the newly created node (False when loading
                multiple nodes to avoid spurious selectionChanged signals)
        """
        entity = node_data['entity']
        layout = node_data['layout']
        node_type = node_data['node_type']

        NODE_CLASS_MAPPING = {
            NodeType.STATE: StateNode,
            NodeType.EVENT: EventNode
        }

        node_class = NODE_CLASS_MAPPING.get(node_type)
        if not node_class:
            logger.warning("Unknown node type: %s", node_type)
            return None

        node = node_class(entity, layout)

        if not skip_overlap_check:
            # RG044: adjust position to avoid overlapping existing nodes
            existing_rects = []
            for item in self.scene.items():
                if hasattr(item, 'entity') and item is not node:
                    r = item.rect()
                    pos = item.pos()
                    existing_rects.append((pos.x(), pos.y(), r.width(), r.height()))
            adjusted_x, adjusted_y = LayoutService.find_non_overlapping_position(
                layout.x, layout.y, layout.width, layout.height, existing_rects
            )
            layout.x = adjusted_x
            layout.y = adjusted_y

        self.add_item_at(layout.x, layout.y, node)
        # RG059: register workspace as position observer so that moving
        # this node re-routes connections it is not part of.
        node.register_position_observer(lambda n=node: self._on_node_moved(n))
        if select:
            self._select_item_only(node)

        # TSK05: initialize the agent badge of state nodes
        if isinstance(node, StateNode):
            self.refresh_state_badge(node)

        return node

    def refresh_state_badge(self, state_node: StateNode) -> None:
        """
        Refresh the agent badge of a state node (TSK05, SU008).

        Computes the agents associated with the state from the current
        project data and updates the badge count and tooltip line.
        """
        if not self.narrative_map or not self.main_window:
            return
        project = getattr(self.main_window, 'project_service', None)
        current = project.current_project if project else None
        if not current:
            return
        from usecases.agent_association.associate_agent_state_usecase import (
            AssociateAgentStateUseCase
        )
        associated_labels = []
        for agent in current.agent:
            if AssociateAgentStateUseCase.find_association(
                    self.narrative_map, agent.id, state_node.entity.id) is not None:
                associated_labels.append(agent.lb)
        state_node.refresh_agent_badge(len(associated_labels), associated_labels)

    def refresh_all_state_badges(self) -> None:
        """Refresh the agent badge of every state node in the scene
        (TSK05)."""
        for item in self.scene.items():
            if isinstance(item, StateNode):
                self.refresh_state_badge(item)


    def create_connection_from_data(self, connection_data: dict):
        """
        Creates a visual connection from 'source', 'target' and
        'relation' (visual nodes and business entity).
        """
        source_node = connection_data.get('source')
        target_node = connection_data.get('target')
        relation_entity = connection_data.get('relation')

        if not (source_node and target_node):
            logger.warning("Invalid connection data format")
            return None

        from core.models.view_model import ConnectionLayout, RelationType
        connection_layout = ConnectionLayout(
            source_node_id=source_node.entity.id,
            target_node_id=target_node.entity.id,
            relation_id=relation_entity.id if relation_entity else None,
            relation_type=connection_data.get('relation_type', RelationType.STATE_TO_EVENT)
        )
        connection = Connection(connection_layout, source_node, target_node, relation_entity)
        self.scene.addItem(connection)
        connection.update_path()
        self._select_item_only(connection)
        return connection

    def _find_node_by_entity_id_and_type(self, entity_id: int, entity_class) -> object:
        """
        Find a node in the scene by its entity_id AND entity class.

        Needed because entity IDs are unique per type, not globally
        (State.id=1 and Event.id=1 can coexist).
        """
        for item in self.scene.items():
            if (hasattr(item, 'entity') and item.entity.id == entity_id
                    and isinstance(item.entity, entity_class)):
                return item
        return None

    def has_connection_between(self, source_node, target_node) -> bool:
        """Check if a visual connection already exists between two nodes (RG054)."""
        for item in self.scene.items():
            if isinstance(item, Connection):
                if (item.source_node is source_node and
                        item.target_node is target_node):
                    return True
        return False

    def _on_node_moved(self, moved_node):
        """
        Re-route connections affected by a node that is not their endpoint
        (RG059).

        Called via the position-observer mechanism whenever *moved_node*
        changes position.  Connections whose source or target IS the moved
        node already update themselves through their own observer; this
        method handles the remaining connections that may need to detour
        around (or no longer detour around) the moved node.
        """
        for item in self.scene.items():
            if not isinstance(item, Connection):
                continue
            if item.source_node is moved_node or item.target_node is moved_node:
                continue
            item.update_path()
        # Notify that the workspace has been visually modified
        self.workspace_modified.emit()


    def _select_item_only(self, item):
        """Selects only the specified item and deselects all others."""
        for existing_item in self.scene.items():
            if (existing_item != item and 
                existing_item.flags() & QGraphicsItem.ItemIsSelectable and
                existing_item.isEnabled()):
                existing_item.setSelected(False)
        
        if item.flags() & QGraphicsItem.ItemIsSelectable:
            item.setSelected(True)


    def remove_connection(self, connection: Connection) -> bool:
        """
        Remove a connection from the scene.

        Args:
            connection: The Connection item to remove

        Returns:
            True if the connection was removed, False otherwise
        """
        if connection is None:
            return False
        self.scene.removeItem(connection)
        return True

    def remove_node(self, node) -> bool:
        """
        Remove a node and all its attached connections from the scene.

        Args:
            node: The BaseNode (or subclass) to remove

        Returns:
            True if the node was removed, False otherwise
        """
        if node is None:
            return False

        # Collect all connections attached to this node before removing it
        connections_to_remove = []
        for item in self.scene.items():
            if isinstance(item, Connection):
                if item.source_node is node or item.target_node is node:
                    connections_to_remove.append(item)

        for connection in connections_to_remove:
            self.scene.removeItem(connection)

        self.scene.removeItem(node)
        return True


    # -------------------------------------------------------------------------
    # Visual layout persistence
    # -------------------------------------------------------------------------

    def collect_workspace_layout(self) -> WorkspaceLayout:
        """
        Collect the current visual layout of the workspace for persistence.

        Iterates over all items in the scene, extracting NodeLayout and
        ConnectionLayout objects from visual nodes and connections.

        Returns:
            A WorkspaceLayout ready for serialization
        """
        layout = WorkspaceLayout(narrative_map_id=self.narrative_map.id)

        for item in self.scene.items():
            if isinstance(item, Connection):
                layout.add_connection(item.layout)
            elif hasattr(item, 'entity') and hasattr(item, 'layout'):
                layout.add_node(item.layout)

        layout.zoom_level = self.transform().m11()
        layout.scroll_x = float(self.horizontalScrollBar().value())
        layout.scroll_y = float(self.verticalScrollBar().value())

        return layout


    def populate_from_layout(self, workspace_layout: WorkspaceLayout,
                              narrative_map) -> int:
        """
        Rebuild visual nodes and connections from a saved WorkspaceLayout.

        Args:
            workspace_layout: The saved layout to restore
            narrative_map: The NarrativeMap containing business entities

        Returns:
            Number of nodes created
        """
        node_count = 0

        # Create state nodes (sorted by entity ID for deterministic order)
        for node_id in sorted(workspace_layout.state_nodes.keys()):
            node_layout = workspace_layout.state_nodes[node_id]
            entity = next((s for s in narrative_map.state
                           if s.id == node_layout.node_id), None)
            if not entity:
                logger.warning("State entity not found for node_id=%s", node_layout.node_id)
                continue
            self.create_node_from_data({
                'entity': entity,
                'layout': node_layout,
                'node_type': NodeType.STATE,
                'narrative_map_id': narrative_map.id,
                'component_type': 'State'
            }, skip_overlap_check=True, select=False)
            node_count += 1

        # Create event nodes (sorted by entity ID)
        for node_id in sorted(workspace_layout.event_nodes.keys()):
            node_layout = workspace_layout.event_nodes[node_id]
            entity = next((e for e in narrative_map.event
                           if e.id == node_layout.node_id), None)
            if not entity:
                logger.warning("Event entity not found for node_id=%s", node_layout.node_id)
                continue
            self.create_node_from_data({
                'entity': entity,
                'layout': node_layout,
                'node_type': NodeType.EVENT,
                'narrative_map_id': narrative_map.id,
                'component_type': 'Event'
            }, skip_overlap_check=True, select=False)
            node_count += 1

        # Create connections from each sub-dictionary
        # Use relation_type to determine entity class, since entity IDs
        # are unique per type, not globally (State.id=1 and Event.id=1
        # can coexist).
        from core.models.data_model import State as StateEntity, Event as EventEntity, Agent as AgentEntity

        RELATION_ENTITY_MAP = {
            RelationType.STATE_TO_EVENT: ('state_to_event', StateEntity, EventEntity),
            RelationType.EVENT_TO_STATE: ('event_to_state', EventEntity, StateEntity),
            RelationType.STATE_AGENT_REL: ('state_agent_rel', StateEntity, AgentEntity),
        }

        conn_subdicts = [
            (workspace_layout.state_to_event_connections, RelationType.STATE_TO_EVENT),
            (workspace_layout.event_to_state_connections, RelationType.EVENT_TO_STATE),
            (workspace_layout.state_agent_rel_connections, RelationType.STATE_AGENT_REL),
        ]

        for conn_dict, rel_type in conn_subdicts:
            attr_name, source_class, target_class = RELATION_ENTITY_MAP[rel_type]

            for conn_layout in conn_dict.values():
                source_node = self._find_node_by_entity_id_and_type(
                    conn_layout.source_node_id, source_class
                )
                target_node = self._find_node_by_entity_id_and_type(
                    conn_layout.target_node_id, target_class
                )

                if not source_node or not target_node:
                    logger.warning("Source or target node not found for connection")
                    continue

                relation_entity = next(
                    (r for r in getattr(narrative_map, attr_name)
                     if r.id == conn_layout.relation_id),
                    None
                )

                self.create_connection_from_data({
                    'source': source_node,
                    'target': target_node,
                    'relation': relation_entity,
                    'relation_type': rel_type
                })

        # Restore zoom level
        if workspace_layout.zoom_level != 1.0:
            self.resetTransform()
            self.scale(workspace_layout.zoom_level, workspace_layout.zoom_level)

        # Restore scroll position
        self.horizontalScrollBar().setValue(int(workspace_layout.scroll_x))
        self.verticalScrollBar().setValue(int(workspace_layout.scroll_y))

        # TSK13: initialize the event badges now that all arcs exist
        # (create_node_from_data initializes them too, but arcs loaded
        # after their state node would leave stale counts)
        self.refresh_all_state_badges()

        # Clear selection (no item should be selected after load)
        self._clear_all_selections()

        return node_count


    def populate_default(self, narrative_map) -> int:
        """
        Create visual nodes and connections with default positions.

        Used when no saved layout exists. States are placed in a column
        on the left, events in a column on the right.

        Args:
            narrative_map: The NarrativeMap containing business entities

        Returns:
            Number of nodes created
        """
        node_count = 0

        state_x = 1800.0
        event_x = 2200.0
        start_y = 1800.0
        step_y = 120.0

        # Create state nodes
        for i, state in enumerate(narrative_map.state):
            layout = LayoutService.create_node_layout(
                node_id=state.id,
                node_type=NodeType.STATE.value,
                x=state_x,
                y=start_y + i * step_y
            )
            self.create_node_from_data({
                'entity': state,
                'layout': layout,
                'node_type': NodeType.STATE,
                'narrative_map_id': narrative_map.id,
                'component_type': 'State'
            }, skip_overlap_check=True, select=False)
            node_count += 1

        # Create event nodes
        for i, event in enumerate(narrative_map.event):
            layout = LayoutService.create_node_layout(
                node_id=event.id,
                node_type=NodeType.EVENT.value,
                x=event_x,
                y=start_y + i * step_y
            )
            self.create_node_from_data({
                'entity': event,
                'layout': layout,
                'node_type': NodeType.EVENT,
                'narrative_map_id': narrative_map.id,
                'component_type': 'Event'
            }, skip_overlap_check=True, select=False)
            node_count += 1

        # Create connections from State_to_event arcs
        for arc in narrative_map.state_to_event:
            source_node = self._find_node_by_entity_id_and_type(arc.state_id, State)
            target_node = self._find_node_by_entity_id_and_type(arc.event_id, Event)
            if source_node and target_node:
                self.create_connection_from_data({
                    'source': source_node,
                    'target': target_node,
                    'relation': arc,
                    'relation_type': RelationType.STATE_TO_EVENT
                })

        # Create connections from Event_to_state arcs
        for arc in narrative_map.event_to_state:
            source_node = self._find_node_by_entity_id_and_type(arc.event_id, Event)
            target_node = self._find_node_by_entity_id_and_type(arc.state_id, State)
            if source_node and target_node:
                self.create_connection_from_data({
                    'source': source_node,
                    'target': target_node,
                    'relation': arc,
                    'relation_type': RelationType.EVENT_TO_STATE
                })

        # TSK13: initialize the event badges now that all arcs exist
        self.refresh_all_state_badges()

        # Clear selection
        self._clear_all_selections()

        return node_count


    def _clear_all_selections(self):
        """Deselects all selectable items in the scene."""
        for item in self.scene.items():
            if (item.flags() & QGraphicsItem.ItemIsSelectable and 
                item.isEnabled()):
                item.setSelected(False)

    def show_context_menu(self, pos):
        """Show context menu for nodes, connections, or empty area."""
        # No context menu while a relation creation is in progress
        if self.relation_creation_mode:
            return

        # Convert click position to scene coordinates.
        # customContextMenuRequested delivers view coordinates while
        # mapToScene expects viewport coordinates.
        scene_pos = self.mapToScene(self.viewport().mapFrom(self, pos))
        item = self.scene.itemAt(scene_pos, self.transform())

        # If the clicked item is a child of a node (e.g., a port), get the parent node
        if item and not isinstance(item, (StateNode, EventNode, Connection)):
            parent = item.parentItem()
            if isinstance(parent, (StateNode, EventNode)):
                item = parent

        # Select the item under the cursor so menu actions operate on
        # the item the user actually clicked on
        if isinstance(item, (StateNode, EventNode, Connection)):
            self._select_item_only(item)
        else:
            self._clear_all_selections()

        menu = QMenu(self)
        # Dark theme for the context menu (charter 98)
        menu.setStyleSheet(theme.CONTEXT_MENU_STYLESHEET)
        handlers = {}

        if isinstance(item, StateNode):
            # Context menu for State nodes
            handlers[menu.addAction("Edit State")] = lambda: self.main_window._edit_selected_component("State")
            handlers[menu.addAction("Associate agents...")] = lambda: self.main_window._associate_agents_to_state(item.entity)
            # TSK10: "Show in agents view" is disabled when the state
            # has no agent association to show
            show_action = menu.addAction("Show in agents view")
            state_has_association = any(
                rel.state_id == item.entity.id
                for rel in self.narrative_map.state_agent_rel)
            show_action.setEnabled(state_has_association)
            handlers[show_action] = lambda: self.focusStateInAgentsViewRequested.emit(item.entity.id)
            # RG031: the initial state can never be deleted, so the Delete
            # State entry stays disabled when the initial state is selected
            delete_state = menu.addAction("Delete State")
            if getattr(item.entity, 'typ', None) == "Initial":
                delete_state.setEnabled(False)
            handlers[delete_state] = lambda: self.main_window._delete_selected_component("State")

        elif isinstance(item, EventNode):
            # Context menu for Event nodes
            handlers[menu.addAction("Edit Event")] = lambda: self.main_window._edit_selected_component("Event")
            handlers[menu.addAction("Delete Event")] = lambda: self.main_window._delete_selected_component("Event")

        elif isinstance(item, Connection):
            # Context menu for Connections
            handlers[menu.addAction("Edit Relation")] = lambda: self.main_window._edit_selected_relation()
            handlers[menu.addAction("Delete Relation")] = lambda: self.main_window._delete_selected_relation()

        else:
            # Context menu for empty area
            handlers[menu.addAction("New State")] = lambda: self.main_window._create_new_node("State")
            handlers[menu.addAction("New Event")] = lambda: self.main_window._create_new_node("Event")
            # TSK13: agents are project entities managed from the menus
            handlers[menu.addAction("New Agent")] = lambda: self.main_window._new_agent()
            handlers[menu.addAction("Connect State and Event")] = lambda: self.main_window._start_state_event_relation_creation()

        # Show the menu at the cursor position and run the handler matching
        # the chosen action (None if the menu was dismissed)
        chosen = menu.exec(self.mapToGlobal(pos))
        handler = handlers.get(chosen)
        if handler:
            handler()
