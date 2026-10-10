# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : connection.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
# Version      : 2
# Date         : 30-08-2026
# Content      : Rework in progress
# Build        : TSC
# ---------------------------------------------------------------------
"""
Connection for Planoscript.

This module provides the Connection class, which represents a visual connection
between two nodes in the workspace. It inherits from QGraphicsPathItem and
supports various connection styles (straight, curved, arrows, etc.).

The connection automatically updates its path when the connected nodes are moved,
and maintains synchronization with the business model relation entities
(e.g., State_agent_rel, Event_to_state, State_to_event, Journey_node).
"""
from datetime import datetime
import math

from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPen, QColor, QPainterPath, QPainterPathStroker
from typing import Optional, Any

from core.models.view_model import ConnectionLayout, ConnectionStyle, PortPosition, RelationType
from core.models.data_model import State_agent_rel
from core.services.layout_service import LayoutService
from ui.nodes.base_node import BaseNode


class Connection(QGraphicsPathItem):
    """
    Visual representation of a connection between two nodes.
    
    This class creates a line (or curve) between a source node and a target node,
    with support for different styles (straight, curved, arrows, etc.).
    It maintains synchronization with business model relation entities or
    direct reference fields.
    
    Attributes:
        layout: The ConnectionLayout containing visual properties
        source_node: The source BaseNode
        target_node: The target BaseNode
        source_port: The port name on the source node
        target_port: The port name on the target node
        relation_entity: Reference to the business relation entity (if any)
    """
    
    # Default settings
    DEFAULT_PEN = QPen(QColor(128, 128, 128), 2)  # Gray line, 2px thick
    DEFAULT_SELECTED_PEN = QPen(QColor(0, 120, 215), 3)  # Blue line, 3px thick
    
    # Arrow settings
    ARROW_SIZE = 10.0

    # Width (pixels) of the invisible clickable area around the line (see shape())
    HIT_AREA_WIDTH = 12.0

    # RG059: clearance (pixels) between a routed connection and an obstacle node
    ROUTE_MARGIN = 20.0

    # RG059: radius of the rounded corners on orthogonal detour paths
    CORNER_RADIUS = 15.0
    
    def __init__(
        self,
        layout: ConnectionLayout,
        source_node: BaseNode,
        target_node: BaseNode,
        relation_entity: Optional[Any] = None
    ):
        """
        Initialize a Connection with its layout, connected nodes, and optional relation entity.
        
        Args:
            layout: The ConnectionLayout containing visual properties
            source_node: The source BaseNode
            target_node: The target BaseNode
            relation_entity: Optional business relation entity (e.g., State_agent_rel)
        """
        super().__init__()
        
        # Store references
        self.layout = layout
        self.source_node = source_node
        self.target_node = target_node
        self.source_port = layout.source_port
        self.target_port = layout.target_port
        self.relation_entity = relation_entity
        
        # Set appearance from layout
        self._init_appearance()
        
        # Enable selection
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        # Enable hover events (blue line feedback, same as nodes)
        self.setAcceptHoverEvents(True)
        
        # Set z-value to ensure connections are behind nodes
        self.setZValue(-1)
        
        # Update initial path
        self.update_path()
        
        # Connect to node movement signals
        self._connect_node_signals()


    def _init_appearance(self) -> None:
        """Initialize the visual appearance from the layout."""
        # Set pen from layout
        if self.layout.color and self.layout.thickness > 0:
            try:
                color = QColor(self.layout.color)
                if color.isValid():
                    self.setPen(QPen(color, self.layout.thickness))
                else:
                    self.setPen(self.DEFAULT_PEN)
            except (ValueError, AttributeError):
                self.setPen(self.DEFAULT_PEN)
        else:
            self.setPen(self.DEFAULT_PEN)
        
        # Set selected state
        self.setSelected(self.layout.selected)


    def _connect_node_signals(self) -> None:
        """
        Register as a position observer on both nodes.

        This ensures the connection updates its path when either node moves.
        """
        self.source_node.register_position_observer(self.update_path)
        self.target_node.register_position_observer(self.update_path)


    def update_path(self) -> None:
        """
        Update the connection path based on current node positions.

        RG059: before falling back to the style-based path (straight, curved,
        arrow), the method checks whether the straight segment between the
        two port positions crosses a third-party node.  If it does, an
        orthogonal detour path is produced instead.
        """
        if not self.source_node or not self.target_node:
            return

        # Get port positions
        source_pos = self._get_port_position(self.source_node, self.source_port)
        target_pos = self._get_port_position(self.target_node, self.target_port)

        # RG059: detect obstacle nodes and route around them if needed
        obstacle_rects = self._get_obstacle_rects()
        if obstacle_rects and self._segment_blocked(source_pos, target_pos, obstacle_rects):
            path = self._create_routed_path(source_pos, target_pos, obstacle_rects)
        elif self.layout.style == ConnectionStyle.STRAIGHT:
            path = self._create_straight_path(source_pos, target_pos)
        elif self.layout.style == ConnectionStyle.CURVED:
            path = self._create_curved_path(source_pos, target_pos)
        elif self.layout.style in [ConnectionStyle.ARROW, ConnectionStyle.CURVED_ARROW]:
            path = self._create_arrow_path(source_pos, target_pos)
        else:  # Default to straight
            path = self._create_straight_path(source_pos, target_pos)

        self.setPath(path)


    def _get_port_position(self, node: BaseNode, port: PortPosition) -> QPointF:
        """
        Get the scene position of a port on a node.
        
        Args:
            node: The node
            port: The port position (from PortPosition enum)
            
        Returns:
            The position in scene coordinates
        """
        port_name = port.value if isinstance(port, PortPosition) else str(port).lower()
        
        if port_name == "left":
            return node.get_left_port_position()
        elif port_name == "right":
            return node.get_right_port_position()


    def _create_straight_path(self, start: QPointF, end: QPointF) -> QPainterPath:
        """
        Create a straight line path between two points.
        
        Args:
            start: Start point in scene coordinates
            end: End point in scene coordinates
            
        Returns:
            QPainterPath for the straight line
        """
        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(end)
        return path


    def _create_curved_path(self, start: QPointF, end: QPointF) -> QPainterPath:
        """
        Create a smooth curved path between two points using Bezier curves.
        
        Args:
            start: Start point in scene coordinates
            end: End point in scene coordinates
            
        Returns:
            QPainterPath for the curved line
        """
        path = QPainterPath()
        path.moveTo(start)
        
        # Calculate control points for a smooth curve
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # For a natural curve, control points are about 1/3 and 2/3 along the line
        # with a vertical or horizontal offset based on the direction
        if abs(dx) > abs(dy):  # More horizontal
            offset = dy * 0.3
            cp1 = QPointF(start.x() + dx * 0.3, start.y() + offset)
            cp2 = QPointF(start.x() + dx * 0.7, end.y() - offset)
        else:  # More vertical
            offset = dx * 0.3
            cp1 = QPointF(start.x() + offset, start.y() + dy * 0.3)
            cp2 = QPointF(end.x() - offset, start.y() + dy * 0.7)
        
        path.cubicTo(cp1, cp2, end)
        return path


    def _create_arrow_path(self, start: QPointF, end: QPointF) -> QPainterPath:
        """
        Create a path with an arrowhead at the target end.
        
        Args:
            start: Start point in scene coordinates
            end: End point in scene coordinates
            
        Returns:
            QPainterPath for the line with arrowhead
        """
        # For now, use straight line with arrow - can be enhanced later
        path = self._create_straight_path(start, end)
        return path


    # -------------------------------------------------------------------------
    # RG059: obstacle detection and orthogonal routing
    # -------------------------------------------------------------------------

    def _get_obstacle_rects(self) -> list:
        """
        Return the scene bounding rects of all nodes in the scene that are
        neither the source nor the target of this connection.
        """
        scene = self.scene()
        if not scene:
            return []
        rects = []
        for item in scene.items():
            if not hasattr(item, 'entity'):
                continue
            if item is self.source_node or item is self.target_node:
                continue
            rects.append(item.sceneBoundingRect())
        return rects

    @staticmethod
    def _segment_blocked(start: QPointF, end: QPointF,
                         obstacle_rects: list) -> bool:
        """Return True if the straight segment start->end crosses any rect."""
        straight = QPainterPath()
        straight.moveTo(start)
        straight.lineTo(end)
        for rect in obstacle_rects:
            if straight.intersects(rect):
                return True
        return False

    def _create_routed_path(self, start: QPointF, end: QPointF,
                            obstacle_rects: list) -> QPainterPath:
        """
        Build an orthogonal path with rounded corners that detours above or
        below the blocking obstacles (RG059).

        The path exits the source horizontally, bridges at *detour_y*
        (above or below the combined obstacle band), then re-enters the
        target horizontally.  Waypoints are pushed to the side of the
        obstacle that is consistent with the connection direction, so the
        path never traverses its own endpoint nodes.
        """
        # Combined bounding rect of all blocking obstacles
        combined = obstacle_rects[0].normalized()
        for rect in obstacle_rects[1:]:
            combined = combined.united(rect.normalized())

        # Choose detour direction: above or below, whichever is closer
        mid_y = (start.y() + end.y()) / 2
        if mid_y <= combined.center().y():
            detour_y = combined.top() - self.ROUTE_MARGIN
        else:
            detour_y = combined.bottom() + self.ROUTE_MARGIN

        # Snap detour_y to grid for visual consistency (RG040)
        detour_y = LayoutService.snap_to_grid(detour_y)

        # Connection direction determines which side of the obstacle each
        # waypoint is pushed to, so the path never backtracks through its
        # own endpoint nodes.
        goes_right = end.x() >= start.x()

        # Source-side waypoint
        wp1_x = start.x()
        if combined.left() <= wp1_x <= combined.right():
            if goes_right:
                wp1_x = combined.right() + self.ROUTE_MARGIN
            else:
                wp1_x = combined.left() - self.ROUTE_MARGIN

        # Target-side waypoint
        wp2_x = end.x()
        if combined.left() <= wp2_x <= combined.right():
            if goes_right:
                wp2_x = combined.left() - self.ROUTE_MARGIN
            else:
                wp2_x = combined.right() + self.ROUTE_MARGIN

        # Clamp corner radius to half the shortest segment so rounded
        # corners never overlap each other on very short segments.
        segments = [
            abs(wp1_x - start.x()),
            abs(detour_y - start.y()),
            abs(wp2_x - wp1_x),
            abs(end.y() - detour_y),
            abs(end.x() - wp2_x),
        ]
        min_seg = min((s for s in segments if s > 0), default=0)
        r = min(self.CORNER_RADIUS, min_seg / 2) if min_seg else 0

        # Direction sign of each segment: -1, 0, or 1
        def _sign(v):
            return (v > 0) - (v < 0)

        s_h1 = _sign(wp1_x - start.x())     # start  → wp1  (horizontal)
        s_v1 = _sign(detour_y - start.y())   # wp1   → detour (vertical)
        s_h2 = _sign(wp2_x - wp1_x)         # wp1   → wp2  (horizontal)
        s_v2 = _sign(end.y() - detour_y)     # wp2   → end  (vertical)
        s_h3 = _sign(end.x() - wp2_x)       # wp2   → end  (horizontal)

        path = QPainterPath()
        path.moveTo(start)

        # Segment 1 → corner 1 (horizontal → vertical)
        path.lineTo(QPointF(wp1_x - r * s_h1, start.y()))
        path.quadTo(QPointF(wp1_x, start.y()),
                    QPointF(wp1_x, start.y() + r * s_v1))

        # Segment 2 → corner 2 (vertical → horizontal)
        path.lineTo(QPointF(wp1_x, detour_y - r * s_v1))
        path.quadTo(QPointF(wp1_x, detour_y),
                    QPointF(wp1_x + r * s_h2, detour_y))

        # Segment 3 → corner 3 (horizontal → vertical)
        path.lineTo(QPointF(wp2_x - r * s_h2, detour_y))
        path.quadTo(QPointF(wp2_x, detour_y),
                    QPointF(wp2_x, detour_y + r * s_v2))

        # Segment 4 → corner 4 (vertical → horizontal)
        path.lineTo(QPointF(wp2_x, end.y() - r * s_v2))
        path.quadTo(QPointF(wp2_x, end.y()),
                    QPointF(wp2_x + r * s_h3, end.y()))

        # Segment 5 → end
        path.lineTo(end)

        return path


    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """
        Handle item changes (e.g., selection).

        Wired the same way as BaseNode: the connection switches to the
        selection pen as soon as its selection state changes, so the
        user gets immediate visual feedback.
        """
        if change == QGraphicsItem.ItemSelectedChange:
            self.layout.selected = bool(value)
            self.set_selected_appearance(bool(value))
        return super().itemChange(change, value)


    def shape(self) -> QPainterPath:
        """
        Return a wider hit area than the visual line.

        The default shape of a QGraphicsPathItem only covers the pen
        width (2 px), which makes a connection nearly impossible to
        click. Stroke the path with a generous, invisible width instead:
        this drives hit testing (selection and context menu) while the
        on-screen appearance is unchanged.
        """
        stroker = QPainterPathStroker()
        stroker.setWidth(self.HIT_AREA_WIDTH)
        stroker.setJoinStyle(Qt.RoundJoin)
        stroker.setCapStyle(Qt.RoundCap)
        return stroker.createStroke(self.path()).simplified()


    def boundingRect(self) -> QRectF:
        """
        Extend the default bounding rect so the wider hit area (see
        shape()) stays within it. The scene indexes items by bounding
        rect and would otherwise miss clicks in the outer band.
        """
        margin = self.HIT_AREA_WIDTH / 2
        rect = super().boundingRect()
        return rect.adjusted(-margin, -margin, margin, margin)


    def paint(self, painter, option, widget=None) -> None:
        """
        Paint the connection with optional arrowhead.

        The line is drawn manually instead of calling
        QGraphicsPathItem::paint: the default implementation adds a
        dashed selection rectangle around the whole bounding box, which
        hugs a rectangular node's contour but not a line. The dashed
        selection feedback is therefore applied to the line itself (see
        set_selected_appearance), matching the node behaviour.
        """
        # Draw the line
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self.path())

        # Draw arrowhead if needed
        if self.layout.style in [ConnectionStyle.ARROW, ConnectionStyle.CURVED_ARROW]:
            self._draw_arrowhead(painter)


    def _draw_arrowhead(self, painter) -> None:
        """
        Draw an arrowhead at the target end of the connection.
        
        Args:
            painter: The QPainter to use for drawing
        """
        if not self.path() or self.path().elementCount() < 2:
            return
        
        # For simplicity, get the last segment's end point and direction
        start_point = self._get_port_position(self.source_node, self.source_port)
        end_point = self._get_port_position(self.target_node, self.target_port)
        
        # Calculate the direction vector
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        
        # Normalize the direction vector
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return
        
        ux = dx / length
        uy = dy / length
        
        # Calculate arrow points
        arrow_length = self.ARROW_SIZE
        arrow_width = self.ARROW_SIZE * 0.6
        
        # Point 1: end point
        p1 = end_point
        
        # Point 2: left side of arrow
        p2 = QPointF(
            end_point.x() - ux * arrow_length - uy * arrow_width,
            end_point.y() - uy * arrow_length + ux * arrow_width
        )
        
        # Point 3: right side of arrow
        p3 = QPointF(
            end_point.x() - ux * arrow_length + uy * arrow_width,
            end_point.y() - uy * arrow_length - ux * arrow_width
        )
        
        # Draw the arrow triangle
        arrow_path = QPainterPath()
        arrow_path.moveTo(p1)
        arrow_path.lineTo(p2)
        arrow_path.lineTo(p3)
        arrow_path.closeSubpath()
        
        # Fill the arrow with the line color
        pen = self.pen()
        painter.setPen(Qt.NoPen)
        painter.setBrush(pen.color())
        painter.drawPath(arrow_path)


    def _restore_layout_pen(self) -> None:
        """
        Restore the normal pen from the layout properties.

        Do not call _init_appearance() here: it calls setSelected(),
        which would recurse while itemChange(ItemSelectedChange) is
        being processed.
        """
        if self.layout.color and self.layout.thickness > 0:
            color = QColor(self.layout.color)
            if color.isValid():
                self.setPen(QPen(color, self.layout.thickness))
            else:
                self.setPen(self.DEFAULT_PEN)
        else:
            self.setPen(self.DEFAULT_PEN)


    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the connection's appearance based on selection state.

        Selected: dashed line in the connection's original color (the
        selection keeps the item's own color, like the node contours;
        blue appears on hover only). Deselected: normal pen.

        Args:
            selected: Whether the connection is selected
        """
        if selected:
            # Original-color dashed pen, same width as the normal line
            # for a finer rendering. Rebuild the pen from the layout
            # (not from the current pen, which may be the hover pen) so
            # it stays stable across hover/selection sequences.
            self._restore_layout_pen()
            selected_pen = QPen(self.pen())
            selected_pen.setStyle(Qt.DashLine)
            self.setPen(selected_pen)
        else:
            self._restore_layout_pen()


    def hoverEnterEvent(self, event) -> None:
        """
        Handle hover enter events: draw the line in blue while not
        selected (same feedback as the nodes' blue border on hover).
        """
        if not self.isSelected():
            width = self.layout.thickness or self.DEFAULT_PEN.width()
            self.setPen(QPen(self.DEFAULT_SELECTED_PEN.color(), width))
        super().hoverEnterEvent(event)


    def hoverLeaveEvent(self, event) -> None:
        """
        Handle hover leave events: restore the normal pen, or keep the
        dashed selected pen if the connection is selected.
        """
        if self.isSelected():
            self.set_selected_appearance(True)
        else:
            self._restore_layout_pen()
        super().hoverLeaveEvent(event)


    def update_layout(self) -> None:
        """
        Update the layout object with the connection's current properties.
        
        This should be called when the connection is modified to
        persist the changes to the layout model.
        """
        self.layout.selected = self.isSelected()


    def set_source_node(self, node: BaseNode, port: PortPosition = PortPosition.RIGHT) -> None:
        """
        Set the source node and port.
        
        Args:
            node: The new source node
            port: The port to use on the source node
        """
        self.source_node = node
        self.source_port = port
        self.layout.source_node_id = node.entity.id
        self.layout.source_port = port
        
        # Update relation type if nodes are set
        if self.target_node:
            self._update_relation_type()
        
        self.update_path()


    def set_target_node(self, node: BaseNode, port: PortPosition = PortPosition.LEFT) -> None:
        """
        Set the target node and port.
        
        Args:
            node: The new target node
            port: The port to use on the target node
        """
        self.target_node = node
        self.target_port = port
        self.layout.target_node_id = node.entity.id
        self.layout.target_port = port
        
        # Update relation type if nodes are set
        if self.source_node:
            self._update_relation_type()
        
        self.update_path()


    def set_relation_entity(self, entity: Any) -> None:
        """
        Set the business relation entity for this connection.
        
        Args:
            entity: The business relation entity
        """
        self.relation_entity = entity
        if entity:
            self.layout.relation_id = entity.id
            # Set label from entity's note/desc if available
            if hasattr(entity, 'note') and entity.note:
                self.layout.label = entity.note
            elif hasattr(entity, 'desc') and entity.desc:
                self.layout.label = entity.desc
        else:
            self.layout.relation_id = None


    def set_style(self, style: ConnectionStyle) -> None:
        """
        Set the connection style and update the path.
        
        Args:
            style: The new connection style
        """
        self.layout.style = style
        self.update_path()


    def set_color(self, color: str) -> None:
        """
        Set the connection color.
        
        Args:
            color: Hex color string (e.g., "#FF0000")
        """
        self.layout.color = color
        try:
            qcolor = QColor(color)
            if qcolor.isValid():
                current_pen = self.pen()
                self.setPen(QPen(qcolor, current_pen.width()))
        except (ValueError, AttributeError):
            pass


    def set_thickness(self, thickness: float) -> None:
        """
        Set the connection thickness.
        
        Args:
            thickness: The new thickness in pixels
        """
        self.layout.thickness = thickness
        current_pen = self.pen()
        self.setPen(QPen(current_pen.color(), thickness))


    def set_label(self, text: str) -> None:
        """
        Set the connection label.
        
        Args:
            text: The new label text
        """
        self.layout.label = text
        # Also update the relation entity's note if it exists
        if self.relation_entity:
            if hasattr(self.relation_entity, 'note'):
                self.relation_entity.note = text
            elif hasattr(self.relation_entity, 'desc'):
                self.relation_entity.desc = text


    def get_source_node(self) -> Optional[BaseNode]:
        """Get the source node."""
        return self.source_node


    def get_target_node(self) -> Optional[BaseNode]:
        """Get the target node."""
        return self.target_node


    def get_label(self) -> Optional[str]:
        """Get the connection label."""
        return self.layout.label


    def get_relation_entity(self) -> Optional[Any]:
        """Get the business relation entity."""
        return self.relation_entity


    def get_relation_id(self) -> Optional[int]:
        """Get the relation entity ID."""
        return self.layout.relation_id


    def get_relation_type(self) -> Optional[str]:
        """Get the relation type."""
        return self.layout.relation_type


    # -------------------------------------------------------------------------
    # Business relation helper methods
    # -------------------------------------------------------------------------
    
    def create_relation_entity(self, narrative_map: Any) -> Optional[Any]:
        """
        Create a business relation entity based on the connected nodes.

        Args:
            narrative_map: The NarrativeMap to add the relation to

        Returns:
            The created relation entity, or None if the relation type
            does not support creation via this method.
        """
        if not self.source_node or not self.target_node or not self.layout.relation_type:
            return None

        relation_type = self.layout.relation_type
        source_id = self.source_node.entity.id
        target_id = self.target_node.entity.id

        # State_agent_rel is a simple State <-> Agent relation
        if relation_type == RelationType.STATE_AGENT_REL:
            relation = State_agent_rel(
                id=narrative_map.get_next_id("state_agent_rel"),
                state_id=source_id,
                agent_id=target_id,
                note=self.layout.label,
                creation_date_time=datetime.now()
            )
            narrative_map.state_agent_rel.append(relation)
            self.set_relation_entity(relation)
        else:
            # Event_to_state and State_to_event arcs are created via
            # ArcService, not via this method.
            return None

        return self.relation_entity


    def delete_relation_entity(self, narrative_map: Any) -> bool:
        """
        Delete the business relation entity associated with this connection.

        Removes the entity from the narrative map's relation list.

        Args:
            narrative_map: The NarrativeMap containing the relation

        Returns:
            True if the relation was deleted, False otherwise
        """
        if not self.layout.relation_type:
            return False

        if not self.layout.relation_id:
            return False

        relation_id = self.layout.relation_id
        relation_type = self.layout.relation_type

        if relation_type == RelationType.STATE_AGENT_REL:
            narrative_map.state_agent_rel = [
                rel for rel in narrative_map.state_agent_rel if rel.id != relation_id
            ]
        elif relation_type == RelationType.EVENT_TO_STATE:
            narrative_map.event_to_state = [
                rel for rel in narrative_map.event_to_state if rel.id != relation_id
            ]
        elif relation_type == RelationType.STATE_TO_EVENT:
            narrative_map.state_to_event = [
                rel for rel in narrative_map.state_to_event if rel.id != relation_id
            ]
        else:
            return False

        self.relation_entity = None
        self.layout.relation_id = None
        if hasattr(narrative_map, 'set_modified'):
            narrative_map.set_modified(True)
        return True
