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


class NodeType(Enum):
    """
    Enumeration of all possible node types that can be displayed in the workspace.
    Each type corresponds to an entity in the business model (data_model.py).
    """
    TIME_REF = "Time_ref"
    SPACE_REF = "Space_ref"
    AGENT = "Agent"
    STATE = "State"
    EVENT = "Event"
    JOURNEY = "Journey"
    CHAPTER = "Chapter"


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
    width: float = 120.0
    height: float = 80.0
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
            width=float(data.get('width', 120.0)),
            height=float(data.get('height', 80.0)),
            color=data.get('color'),
            z_index=int(data.get('z_index', 0)),
            collapsed=bool(data.get('collapsed', False)),
            selected=bool(data.get('selected', False))
        )


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
    
    Attributes:
        id: Unique identifier for the connection (UUID as string)
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
        relation_id: ID of the business relation entity (e.g., Agent_state_rel.id)
        relation_type: Type of the business relation (e.g., "Agent_state_rel")
    """
    id: str
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
    relation_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
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
            'relation_type': self.relation_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConnectionLayout':
        """Create a ConnectionLayout from a dictionary."""
        return cls(
            id=str(data['id']),
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
            relation_type=data.get('relation_type')
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
        nodes: Dictionary mapping business entity IDs to their NodeLayout
        connections: Dictionary mapping connection IDs to their ConnectionLayout
        zoom_level: Current zoom level of the workspace (1.0 = 100%)
        scroll_position: Current scroll position (x, y) of the workspace
    """
    narrative_map_id: str
    nodes: Dict[int, NodeLayout] = field(default_factory=dict)
    connections: Dict[str, ConnectionLayout] = field(default_factory=dict)
    zoom_level: float = 1.0
    scroll_x: float = 0.0
    scroll_y: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'narrative_map_id': self.narrative_map_id,
            'nodes': {k: v.to_dict() for k, v in self.nodes.items()},
            'connections': {k: v.to_dict() for k, v in self.connections.items()},
            'zoom_level': self.zoom_level,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceLayout':
        """Create a WorkspaceLayout from a dictionary."""
        return cls(
            narrative_map_id=str(data['narrative_map_id']),
            nodes={int(k): NodeLayout.from_dict(v) for k, v in data.get('nodes', {}).items()},
            connections={k: ConnectionLayout.from_dict(v) for k, v in data.get('connections', {}).items()},
            zoom_level=float(data.get('zoom_level', 1.0)),
            scroll_x=float(data.get('scroll_x', 0.0)),
            scroll_y=float(data.get('scroll_y', 0.0))
        )

    def get_node_layout(self, node_id: int) -> Optional[NodeLayout]:
        """Get the layout for a specific node by its business entity ID."""
        return self.nodes.get(node_id)

    def get_connection_layout(self, connection_id: str) -> Optional[ConnectionLayout]:
        """Get the layout for a specific connection by its ID."""
        return self.connections.get(connection_id)

    def add_node(self, node_layout: NodeLayout) -> None:
        """Add or update a node layout."""
        self.nodes[node_layout.node_id] = node_layout

    def remove_node(self, node_id: int) -> bool:
        """Remove a node layout and all its connections."""
        if node_id not in self.nodes:
            return False
        
        # Remove all connections involving this node
        connection_ids_to_remove = [
            conn_id for conn_id, conn in self.connections.items()
            if conn.source_node_id == node_id or conn.target_node_id == node_id
        ]
        for conn_id in connection_ids_to_remove:
            del self.connections[conn_id]
        
        # Remove the node
        del self.nodes[node_id]
        return True

    def add_connection(self, connection_layout: ConnectionLayout) -> None:
        """Add or update a connection layout."""
        self.connections[connection_layout.id] = connection_layout

    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection layout."""
        if connection_id in self.connections:
            del self.connections[connection_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all nodes and connections from the layout."""
        self.nodes.clear()
        self.connections.clear()
        self.zoom_level = 1.0
        self.scroll_x = 0.0
        self.scroll_y = 0.0
