# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : connection.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
# Version      : 2
# Date         : 2026-08-27
# Content      : Non-functional version (intermediate redesign stage)
# Build        : TSC + Mistral Vibe
# ---------------------------------------------------------------------
"""
Connection for Planoscript.

This module provides the Connection class, which represents a visual connection
between two nodes in the workspace. It inherits from QGraphicsPathItem and
supports various connection styles (straight, curved, arrows, etc.).

The connection automatically updates its path when the connected nodes are moved,
and maintains synchronization with the business model relation entities
(e.g., Agent_state_rel, Agent_event_rel, etc.) or direct reference fields
(for Time_ref and Space_ref connections).
"""

from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtCore import QPointF, Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath
from typing import Optional, Any, Dict, Tuple
from datetime import datetime
import math

from core.models.view_model import ConnectionLayout, ConnectionStyle, PortPosition, NodeType
from core.models.data_model import (
    Agent_state_rel,
    Agent_event_rel,
    State_event_rel,
    Event_state_rel,
    Agent_rel_hist,
    Time_ref,
    Space_ref,
    State,
    Event,
    Agent
)
from ui.nodes.base_node import BaseNode


# Types of relations that are separate entities (n-n cardinality)
ENTITY_RELATION_TYPES = {
    "State_agent_rel",
    "State_node", 
    "Journey_node"
}

# Types of relations that are direct fields (1-n cardinality)
# Format: (source_type, target_type) -> (target_field_name, source_field_name)
DIRECT_RELATION_FIELDS = {
    #(NodeType.TIME_REF, NodeType.STATE): ("time_ref_id", None),
    #(NodeType.TIME_REF, NodeType.EVENT): ("time_ref_id", None),
    #(NodeType.SPACE_REF, NodeType.STATE): ("space_ref_id", None),
    #(NodeType.SPACE_REF, NodeType.EVENT): ("space_ref_id", None),
    # Reverse mappings (for consistency)
    #(NodeType.STATE, NodeType.TIME_REF): (None, "time_ref_id"),
    #(NodeType.EVENT, NodeType.TIME_REF): (None, "time_ref_id"),
    #(NodeType.STATE, NodeType.SPACE_REF): (None, "space_ref_id"),
    #(NodeType.EVENT, NodeType.SPACE_REF): (None, "space_ref_id"),
}


def get_relation_type(source_type: NodeType, target_type: NodeType) -> Optional[str]:
    """
    Determine the business relation type based on node types.
    
    For entity relations (n-n cardinality), returns the relation class name.
    For direct field relations (1-n cardinality), returns the field name with
    a special prefix to indicate it's a direct field.
    
    Args:
        source_type: NodeType of the source node
        target_type: NodeType of the target node
        
    Returns:
        String representing the relation type:
        - For entity relations: "Agent_state_rel", "Agent_event_rel", etc.
        - For direct fields: "direct:time_ref_id", "direct:space_ref_id"
        - None if no valid relation exists
    """
    # First check if this is a direct field relation
    if (source_type, target_type) in DIRECT_RELATION_FIELDS:
        target_field, _ = DIRECT_RELATION_FIELDS[(source_type, target_type)]
        if target_field:
            return f"direct:{target_field}"
    
    # Check reverse
    if (target_type, source_type) in DIRECT_RELATION_FIELDS:
        _, source_field = DIRECT_RELATION_FIELDS[(target_type, source_type)]
        if source_field:
            return f"direct:{source_field}"
    
    # Check entity relations
    relation_mapping = {
        #(NodeType.AGENT, NodeType.STATE): "Agent_state_rel",
        #(NodeType.AGENT, NodeType.EVENT): "Agent_event_rel",
        #(NodeType.AGENT, NodeType.AGENT): "Agent_rel_hist",
        (NodeType.STATE, NodeType.EVENT): "State_event_rel",
        (NodeType.EVENT, NodeType.STATE): "Event_state_rel",
        # Reverse mappings for consistency
        (NodeType.STATE, NodeType.AGENT): "Agent_state_rel",
        (NodeType.EVENT, NodeType.AGENT): "Agent_event_rel",
        #(NodeType.TIME_REF, NodeType.TIME_REF): None,
        #(NodeType.SPACE_REF, NodeType.SPACE_REF): None,
    }
    
    return relation_mapping.get((source_type, target_type))


def is_direct_relation(relation_type: Optional[str]) -> bool:
    """
    Check if a relation type represents a direct field reference.
    
    Args:
        relation_type: The relation type string
        
    Returns:
        True if this is a direct field relation, False otherwise
    """
    return relation_type is not None and relation_type.startswith("direct:")


def get_field_name_from_relation_type(relation_type: str) -> Optional[str]:
    """
    Extract the field name from a direct relation type.
    
    Args:
        relation_type: The relation type string (e.g., "direct:time_ref_id")
        
    Returns:
        The field name (e.g., "time_ref_id"), or None if not a direct relation
    """
    if is_direct_relation(relation_type):
        return relation_type[7:]  # Remove "direct:" prefix
    return None


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
    ARROW_ANGLE = math.pi / 6  # 30 degrees
    
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
            relation_entity: Optional business relation entity (e.g., Agent_state_rel)
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
        Connect to the nodes' position change signals.
        
        This ensures the connection updates when either node moves.
        """
        # Enable position change notifications for both nodes
        self.source_node.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.target_node.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        # Store original itemChange method references
        self._source_item_change = self.source_node.itemChange
        self._target_item_change = self.target_node.itemChange
        
        # Replace itemChange methods to detect position changes
        self.source_node.itemChange = self._source_item_change_wrapper
        self.target_node.itemChange = self._target_item_change_wrapper

    def _source_item_change_wrapper(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """Wrapper for source node's itemChange method."""
        result = self._source_item_change(change, value)
        if change == QGraphicsItem.ItemPositionChange:
            self.update_path()
        return result

    def _target_item_change_wrapper(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        """Wrapper for target node's itemChange method."""
        result = self._target_item_change(change, value)
        if change == QGraphicsItem.ItemPositionChange:
            self.update_path()
        return result

    def update_path(self) -> None:
        """
        Update the connection path based on current node positions.
        
        This method calculates the path between the source and target nodes
        based on their current positions and the connection style.
        """
        if not self.source_node or not self.target_node:
            return
        
        # Get port positions
        source_pos = self._get_port_position(self.source_node, self.source_port)
        target_pos = self._get_port_position(self.target_node, self.target_port)
        
        # Create path based on style
        if self.layout.style == ConnectionStyle.STRAIGHT:
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
        elif port_name == "top":
            return node.get_top_port_position()
        elif port_name == "bottom":
            return node.get_bottom_port_position()
        else:
            return node.get_center_port_position()

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

    def paint(self, painter, option, widget=None) -> None:
        """
        Paint the connection with optional arrowhead.
        
        This overrides the default paint method to add arrowheads
        when the style includes arrows.
        """
        # Draw the line
        super().paint(painter, option, widget)
        
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

    def set_selected_appearance(self, selected: bool) -> None:
        """
        Update the connection's appearance based on selection state.
        
        Args:
            selected: Whether the connection is selected
        """
        if selected:
            # Use selected pen (thicker and blue)
            current_pen = self.pen()
            selected_pen = QPen(
                self.DEFAULT_SELECTED_PEN.color(),
                current_pen.width() + 1
            )
            self.setPen(selected_pen)
        else:
            # Restore normal pen
            self._init_appearance()

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

    def _update_relation_type(self) -> None:
        """Update the relation type based on source and target node types."""
        if not self.source_node or not self.target_node:
            self.layout.relation_type = None
            return
        
        self.layout.relation_type = get_relation_type(
            self.source_node.layout.node_type,
            self.target_node.layout.node_type
        )

    def set_relation_entity(self, entity: Any) -> None:
        """
        Set the business relation entity for this connection.
        
        Args:
            entity: The business relation entity (e.g., Agent_state_rel instance)
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
        
        For entity relations (n-n cardinality like Agent-State), creates a new
        relation entity. For direct field relations (1-n cardinality like
        Time_ref-State), updates the target entity's reference field.
        
        Args:
            narrative_map: The NarrativeMap to add the relation to
            
        Returns:
            The created relation entity (for entity relations) or None (for direct fields)
        """
        if not self.source_node or not self.target_node or not self.layout.relation_type:
            return None
        
        relation_type = self.layout.relation_type
        source_id = self.source_node.entity.id
        target_id = self.target_node.entity.id
        
        # Handle direct field relations (Time_ref -> State/Event, Space_ref -> State/Event)
        if is_direct_relation(relation_type):
            field_name = get_field_name_from_relation_type(relation_type)
            if field_name:
                # For direct relations, update the target entity's field
                # The connection is from Time_ref/Space_ref to State/Event
                target_entity = self.target_node.entity
                if hasattr(target_entity, field_name):
                    setattr(target_entity, field_name, source_id)
                    # Mark as modified if the narrative map has a modification flag
                    if hasattr(narrative_map, 'set_modified'):
                        narrative_map.set_modified(True)
                return None  # No entity created for direct relations
        
        # Handle entity relations (n-n cardinality)
        if relation_type == "Agent_state_rel":
            relation = Agent_state_rel(
                id=narrative_map.get_next_id("agent_state_rel"),
                agent_id=source_id,
                state_id=target_id,
                note=self.layout.label,
                creation_date_time=datetime.now()
            )
            narrative_map.agent_state_rel.append(relation)
            self.set_relation_entity(relation)
            
        elif relation_type == "Agent_event_rel":
            relation = Agent_event_rel(
                id=narrative_map.get_next_id("agent_event_rel"),
                agent_id=source_id,
                event_id=target_id,
                note=self.layout.label,
                creation_date_time=datetime.now()
            )
            narrative_map.agent_event_rel.append(relation)
            self.set_relation_entity(relation)
            
        elif relation_type == "State_event_rel":
            relation = State_event_rel(
                id=narrative_map.get_next_id("state_event_rel"),
                state_id=source_id,
                event_id=target_id,
                note=self.layout.label,
                creation_date_time=datetime.now()
            )
            narrative_map.state_event_rel.append(relation)
            self.set_relation_entity(relation)
            
        elif relation_type == "Event_state_rel":
            relation = Event_state_rel(
                id=narrative_map.get_next_id("event_state_rel"),
                event_id=source_id,
                state_id=target_id,
                note=self.layout.label,
                creation_date_time=datetime.now()
            )
            narrative_map.event_state_rel.append(relation)
            self.set_relation_entity(relation)
            
        elif relation_type == "Agent_rel_hist":
            relation = Agent_rel_hist(
                id=narrative_map.get_next_id("agent_rel_hist"),
                agent_1_id=source_id,
                agent_2_id=target_id,
                desc=self.layout.label,
                creation_date_time=datetime.now()
            )
            narrative_map.agent_rel_hist.append(relation)
            self.set_relation_entity(relation)
        else:
            return None
        
        return self.relation_entity

    def delete_relation_entity(self, narrative_map: Any) -> bool:
        """
        Delete the business relation entity associated with this connection.
        
        For entity relations, removes the entity from the narrative map.
        For direct field relations, clears the reference field in the target entity.
        
        Args:
            narrative_map: The NarrativeMap containing the relation
            
        Returns:
            True if the relation was deleted, False otherwise
        """
        if not self.layout.relation_type:
            return False
        
        # Handle direct field relations
        if is_direct_relation(self.layout.relation_type):
            field_name = get_field_name_from_relation_type(self.layout.relation_type)
            if field_name and self.target_node and hasattr(self.target_node.entity, field_name):
                # Clear the reference field in the target entity
                setattr(self.target_node.entity, field_name, None)
                if hasattr(narrative_map, 'set_modified'):
                    narrative_map.set_modified(True)
                self.layout.relation_id = None
                return True
            return False
        
        # Handle entity relations
        if not self.layout.relation_id:
            return False
        
        relation_id = self.layout.relation_id
        
        if self.layout.relation_type == "Agent_state_rel":
            narrative_map.agent_state_rel = [
                rel for rel in narrative_map.agent_state_rel if rel.id != relation_id
            ]
        elif self.layout.relation_type == "Agent_event_rel":
            narrative_map.agent_event_rel = [
                rel for rel in narrative_map.agent_event_rel if rel.id != relation_id
            ]
        elif self.layout.relation_type == "State_event_rel":
            narrative_map.state_event_rel = [
                rel for rel in narrative_map.state_event_rel if rel.id != relation_id
            ]
        elif self.layout.relation_type == "Event_state_rel":
            narrative_map.event_state_rel = [
                rel for rel in narrative_map.event_state_rel if rel.id != relation_id
            ]
        elif self.layout.relation_type == "Agent_rel_hist":
            narrative_map.agent_rel_hist = [
                rel for rel in narrative_map.agent_rel_hist if rel.id != relation_id
            ]
        else:
            return False
        
        self.relation_entity = None
        self.layout.relation_id = None
        if hasattr(narrative_map, 'set_modified'):
            narrative_map.set_modified(True)
        return True
