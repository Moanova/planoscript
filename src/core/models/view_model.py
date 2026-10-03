# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : view_model.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
View Model for Planoscript.

This module defines the data structures for visual representation of entities
(nodes, connections) in the workspace. It is completely separate from the business
model (data_model.py) and only references entities by their IDs.

The separation between business model (data_model.py) and view model (this file)
ensures:
- Clean separation of concerns (MVC pattern)
- No breaking changes to existing projects
- Reusability of business logic without UI dependencies
- Flexibility to change UI without affecting business data
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

from config.config_loader import get as _get_config

# Node dimensions sourced from config.json (single source of truth).
_NODE_DEFAULT_WIDTH = _get_config("node_default_width", 80.0)
_NODE_DEFAULT_HEIGHT = _get_config("node_default_height", 40.0)


class NodeType(Enum):
    """
    Enumeration of all possible node types that can be displayed in the workspace.
    Each type corresponds to an entity in the business model (data_model.py).
    """
    AGENT = "Agent"
    STATE = "State"
    EVENT = "Event"
    #JOURNEY = "Journey"


@dataclass
class NodeLayout:
    """
    Represents the visual layout of a single node in the workspace.
    
    This class stores only the visual properties (position, size, style) of a node,
    and references the corresponding business entity via its ID and type.
    
    Attributes:
        node_id: The ID of the business entity (Agent.id, State.id, etc.)
        node_type: The type of the entity (used for deserialization)
        x: X position in pixels (workspace coordinates)
        y: Y position in pixels (workspace coordinates)
        width: Width of the node in pixels
        height: Height of the node in pixels
        color: Optional hex color code (#RRGGBB) for custom styling
        z_index: Z-order for layering (higher values appear on top)
        collapsed: Whether the node is collapsed (hidden content)
        selected: Whether the node is currently selected
    """
    node_id: int
    node_type: NodeType
    x: float
    y: float
    width: float = _NODE_DEFAULT_WIDTH
    height: float = _NODE_DEFAULT_HEIGHT
    color: Optional[str] = None
    z_index: int = 0
    collapsed: bool = False
    selected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'node_id': self.node_id,
            'node_type': self.node_type.value,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color,
            'z_index': self.z_index,
            'collapsed': self.collapsed,
            'selected': self.selected
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeLayout':
        """Create a NodeLayout from a dictionary."""
        return cls(
            node_id=int(data['node_id']),
            node_type=NodeType(data['node_type']),
            x=float(data['x']),
            y=float(data['y']),
            width=float(data.get('width', _NODE_DEFAULT_WIDTH)),
            height=float(data.get('height', _NODE_DEFAULT_HEIGHT)),
            color=data.get('color'),
            z_index=int(data.get('z_index', 0)),
            collapsed=bool(data.get('collapsed', False)),
            selected=bool(data.get('selected', False))
        )


class RelationType(Enum):
    """Enumeration of relation types from the business model."""
    STATE_AGENT_REL = "State_agent_rel"
    EVENT_TO_STATE = "Event_to_state"
    STATE_TO_EVENT = "State_to_event"
    #JOURNEY_NODE = "Journey_node"


class ConnectionStyle(Enum):
    """Enumeration of connection line styles."""
    STRAIGHT = "straight"      # Direct line between nodes
    CURVED = "curved"          # Bezier curve connection
    DOTTED = "dotted"          # Dotted line
    DASHED = "dashed"          # Dashed line
    ARROW = "arrow"            # Straight line with arrowhead
    CURVED_ARROW = "curved_arrow"  # Curved line with arrowhead


class PortPosition(Enum):
    """Enumeration of connection port positions on a node."""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"


@dataclass
class ConnectionLayout:
    """
    Represents a visual connection between two nodes in the workspace.

    This class stores the visual properties of a connection and references
    the source and target nodes via their IDs. It also maintains links to
    the corresponding business model relation entities.

    The connection is identified by its relation_id (the business arc ID),
    which is used as the key in the WorkspaceLayout sub-dictionaries.

    Attributes:
        source_node_id: ID of the source business entity
        source_port: Connection port on the source node
        target_node_id: ID of the target business entity
        target_port: Connection port on the target node
        style: Visual style of the connection line
        color: Optional hex color code (#RRGGBB)
        thickness: Line thickness in pixels
        z_index: Z-order for layering
        selected: Whether the connection is currently selected
        label: Optional text label for the connection
        relation_id: ID of the business relation entity (e.g., State_to_event.id)
        relation_type: Type of the business relation (e.g., "State_to_event")
    """
    source_node_id: int = -1
    source_port: PortPosition = PortPosition.RIGHT
    target_node_id: int = -1
    target_port: PortPosition = PortPosition.LEFT
    style: ConnectionStyle = ConnectionStyle.STRAIGHT
    color: Optional[str] = None
    thickness: float = 2.0
    z_index: int = 0
    selected: bool = False
    label: Optional[str] = None
    relation_id: Optional[int] = None
    relation_type: Optional[RelationType] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'source_node_id': self.source_node_id,
            'source_port': self.source_port.value,
            'target_node_id': self.target_node_id,
            'target_port': self.target_port.value,
            'style': self.style.value,
            'color': self.color,
            'thickness': self.thickness,
            'z_index': self.z_index,
            'selected': self.selected,
            'label': self.label,
            'relation_id': self.relation_id,
            'relation_type': self.relation_type.value if self.relation_type else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConnectionLayout':
        """Create a ConnectionLayout from a dictionary."""
        relation_type_value = data.get('relation_type')
        relation_type = None
        if relation_type_value is not None:
            try:
                relation_type = RelationType(relation_type_value)
            except ValueError:
                relation_type = None

        return cls(
            source_node_id=int(data['source_node_id']),
            source_port=PortPosition(data.get('source_port', 'right')),
            target_node_id=int(data['target_node_id']),
            target_port=PortPosition(data.get('target_port', 'left')),
            style=ConnectionStyle(data.get('style', 'straight')),
            color=data.get('color'),
            thickness=float(data.get('thickness', 2.0)),
            z_index=int(data.get('z_index', 0)),
            selected=bool(data.get('selected', False)),
            label=data.get('label'),
            relation_id=int(data['relation_id']) if data.get('relation_id') is not None else None,
            relation_type=relation_type
        )


@dataclass
class WorkspaceLayout:
    """
    Represents the complete visual layout of a workspace (tab).

    A WorkspaceLayout contains all the nodes and connections for a specific
    narrative map displayed in a workspace tab. It maintains the visual
    state separately from the business data.

    Attributes:
        narrative_map_id: ID of the associated NarrativeMap from the business model
        state_nodes: Dict keyed by State.id
        event_nodes: Dict keyed by Event.id
        agent_nodes: Dict keyed by Agent.id
        state_to_event_connections: Dict keyed by State_to_event.id
        event_to_state_connections: Dict keyed by Event_to_state.id
        state_agent_rel_connections: Dict keyed by State_agent_rel.id
        zoom_level: Current zoom level of the workspace (1.0 = 100%)
        scroll_position: Current scroll position (x, y) of the workspace
    """
    narrative_map_id: str
    state_nodes: Dict[int, NodeLayout] = field(default_factory=dict)
    event_nodes: Dict[int, NodeLayout] = field(default_factory=dict)
    agent_nodes: Dict[int, NodeLayout] = field(default_factory=dict)
    state_to_event_connections: Dict[int, ConnectionLayout] = field(default_factory=dict)
    event_to_state_connections: Dict[int, ConnectionLayout] = field(default_factory=dict)
    state_agent_rel_connections: Dict[int, ConnectionLayout] = field(default_factory=dict)
    zoom_level: float = 1.0
    scroll_x: float = 0.0
    scroll_y: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'narrative_map_id': self.narrative_map_id,
            'state_nodes': {k: v.to_dict() for k, v in self.state_nodes.items()},
            'event_nodes': {k: v.to_dict() for k, v in self.event_nodes.items()},
            'agent_nodes': {k: v.to_dict() for k, v in self.agent_nodes.items()},
            'state_to_event_connections': {k: v.to_dict() for k, v in self.state_to_event_connections.items()},
            'event_to_state_connections': {k: v.to_dict() for k, v in self.event_to_state_connections.items()},
            'state_agent_rel_connections': {k: v.to_dict() for k, v in self.state_agent_rel_connections.items()},
            'zoom_level': self.zoom_level,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceLayout':
        """Create a WorkspaceLayout from a dictionary."""
        return cls(
            narrative_map_id=str(data['narrative_map_id']),
            state_nodes={int(k): NodeLayout.from_dict(v) for k, v in data.get('state_nodes', {}).items()},
            event_nodes={int(k): NodeLayout.from_dict(v) for k, v in data.get('event_nodes', {}).items()},
            agent_nodes={int(k): NodeLayout.from_dict(v) for k, v in data.get('agent_nodes', {}).items()},
            state_to_event_connections={int(k): ConnectionLayout.from_dict(v) for k, v in data.get('state_to_event_connections', {}).items()},
            event_to_state_connections={int(k): ConnectionLayout.from_dict(v) for k, v in data.get('event_to_state_connections', {}).items()},
            state_agent_rel_connections={int(k): ConnectionLayout.from_dict(v) for k, v in data.get('state_agent_rel_connections', {}).items()},
            zoom_level=float(data.get('zoom_level', 1.0)),
            scroll_x=float(data.get('scroll_x', 0.0)),
            scroll_y=float(data.get('scroll_y', 0.0))
        )

    def get_node_layout(self, node_type: NodeType, node_id: int) -> Optional[NodeLayout]:
        """Get the layout for a specific node by its type and entity ID."""
        if node_type == NodeType.STATE:
            return self.state_nodes.get(node_id)
        elif node_type == NodeType.EVENT:
            return self.event_nodes.get(node_id)
        elif node_type == NodeType.AGENT:
            return self.agent_nodes.get(node_id)
        return None

    def get_connection_layout(self, relation_type: RelationType, relation_id: int) -> Optional[ConnectionLayout]:
        """Get the layout for a specific connection by its relation type and ID."""
        if relation_type == RelationType.STATE_TO_EVENT:
            return self.state_to_event_connections.get(relation_id)
        elif relation_type == RelationType.EVENT_TO_STATE:
            return self.event_to_state_connections.get(relation_id)
        elif relation_type == RelationType.STATE_AGENT_REL:
            return self.state_agent_rel_connections.get(relation_id)
        return None

    def add_node(self, node_layout: NodeLayout) -> None:
        """Add or update a node layout, routed by node type."""
        if node_layout.node_type == NodeType.STATE:
            self.state_nodes[node_layout.node_id] = node_layout
        elif node_layout.node_type == NodeType.EVENT:
            self.event_nodes[node_layout.node_id] = node_layout
        elif node_layout.node_type == NodeType.AGENT:
            self.agent_nodes[node_layout.node_id] = node_layout

    def remove_node(self, node_type: NodeType, node_id: int) -> bool:
        """Remove a node layout and all its connections."""
        node_dict = None
        if node_type == NodeType.STATE:
            node_dict = self.state_nodes
        elif node_type == NodeType.EVENT:
            node_dict = self.event_nodes
        elif node_type == NodeType.AGENT:
            node_dict = self.agent_nodes

        if not node_dict or node_id not in node_dict:
            return False

        # Remove all connections involving this node
        for conn_dict in [self.state_to_event_connections,
                         self.event_to_state_connections,
                         self.state_agent_rel_connections]:
            conn_ids_to_remove = [
                cid for cid, conn in conn_dict.items()
                if conn.source_node_id == node_id or conn.target_node_id == node_id
            ]
            for cid in conn_ids_to_remove:
                del conn_dict[cid]

        # Remove the node
        del node_dict[node_id]
        return True

    def add_connection(self, connection_layout: ConnectionLayout) -> None:
        """Add or update a connection layout, routed by relation_type."""
        if connection_layout.relation_type == RelationType.STATE_TO_EVENT:
            self.state_to_event_connections[connection_layout.relation_id] = connection_layout
        elif connection_layout.relation_type == RelationType.EVENT_TO_STATE:
            self.event_to_state_connections[connection_layout.relation_id] = connection_layout
        elif connection_layout.relation_type == RelationType.STATE_AGENT_REL:
            self.state_agent_rel_connections[connection_layout.relation_id] = connection_layout

    def remove_connection(self, relation_type: RelationType, relation_id: int) -> bool:
        """Remove a connection layout by its relation type and ID."""
        if relation_type == RelationType.STATE_TO_EVENT:
            if relation_id in self.state_to_event_connections:
                del self.state_to_event_connections[relation_id]
                return True
        elif relation_type == RelationType.EVENT_TO_STATE:
            if relation_id in self.event_to_state_connections:
                del self.event_to_state_connections[relation_id]
                return True
        elif relation_type == RelationType.STATE_AGENT_REL:
            if relation_id in self.state_agent_rel_connections:
                del self.state_agent_rel_connections[relation_id]
                return True
        return False

    def clear(self) -> None:
        """Clear all nodes and connections from the layout."""
        self.state_nodes.clear()
        self.event_nodes.clear()
        self.agent_nodes.clear()
        self.state_to_event_connections.clear()
        self.event_to_state_connections.clear()
        self.state_agent_rel_connections.clear()
        self.zoom_level = 1.0
        self.scroll_x = 0.0
        self.scroll_y = 0.0