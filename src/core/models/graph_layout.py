# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : graph_layout.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Graph Layout Model for Planoscript.

This module defines the data structures for visual representation of
relation graphs (e.g., State_node, Journey_node) in the workspace.

Unlike WorkspaceLayout which represents the layout of individual nodes and
connections, GraphLayout represents the layout of graph structures
(graphs) that group multiple nodes and connections together.

This separation allows for:
- Independent management of graph structures
- Selective loading/saving of graphs
- Different visualization rules for graphs vs. individual nodes
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class GraphLayout:
    """
    Represents the visual layout of a relation graph (e.g., State_node, Journey_node).
    
    A GraphLayout contains the visual properties of a graph container, including
    its position, size, and references to the node and connection layouts
    that belong to the graph.
    
    Attributes:
        graph_id: The ID of the graph entity (e.g., State_node.id, Journey.id)
        graph_type: The type of the graph ("State_node", "Journey_node")
        x: X position of the graph container in the workspace
        y: Y position of the graph container in the workspace
        width: Width of the graph container
        height: Height of the graph container
        color: Optional background color (hex string)
        title: Optional title displayed in the graph header
        collapsed: Whether the graph is collapsed (only show header)
        z_index: Z-order for layering (graphs appear below nodes)
        node_ids: List of entity IDs that belong to this graph
        connection_ids: List of connection IDs that belong to this graph
        child_graph_ids: List of child graph IDs (for hierarchical graphs)
    """
    graph_id: int
    graph_type: str
    x: float = 0.0
    y: float = 0.0
    width: float = 400.0
    height: float = 300.0
    color: Optional[str] = None
    title: Optional[str] = None
    collapsed: bool = False
    z_index: int = -10
    node_ids: List[int] = field(default_factory=list)
    connection_ids: List[str] = field(default_factory=list)
    child_graph_ids: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'graph_id': self.graph_id,
            'graph_type': self.graph_type,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color,
            'title': self.title,
            'collapsed': self.collapsed,
            'z_index': self.z_index,
            'node_ids': self.node_ids,
            'connection_ids': self.connection_ids,
            'child_graph_ids': self.child_graph_ids
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphLayout':
        """Create a GraphLayout from a dictionary."""
        return cls(
            graph_id=int(data['graph_id']),
            graph_type=str(data['graph_type']),
            x=float(data.get('x', 0.0)),
            y=float(data.get('y', 0.0)),
            width=float(data.get('width', 400.0)),
            height=float(data.get('height', 300.0)),
            color=data.get('color'),
            title=data.get('title'),
            collapsed=bool(data.get('collapsed', False)),
            z_index=int(data.get('z_index', -10)),
            node_ids=list(data.get('node_ids', [])),
            connection_ids=list(data.get('connection_ids', [])),
            child_graph_ids=list(data.get('child_graph_ids', []))
        )

    def add_node(self, node_id: int) -> None:
        """Add a node ID to the graph."""
        if node_id not in self.node_ids:
            self.node_ids.append(node_id)

    def remove_node(self, node_id: int) -> bool:
        """Remove a node ID from the graph."""
        if node_id in self.node_ids:
            self.node_ids.remove(node_id)
            return True
        return False

    def add_connection(self, connection_id: str) -> None:
        """Add a connection ID to the graph."""
        if connection_id not in self.connection_ids:
            self.connection_ids.append(connection_id)

    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection ID from the graph."""
        if connection_id in self.connection_ids:
            self.connection_ids.remove(connection_id)
            return True
        return False

    def add_child_graph(self, child_graph_id: int) -> None:
        """Add a child graph ID."""
        if child_graph_id not in self.child_graph_ids:
            self.child_graph_ids.append(child_graph_id)

    def remove_child_graph(self, child_graph_id: int) -> bool:
        """Remove a child graph ID."""
        if child_graph_id in self.child_graph_ids:
            self.child_graph_ids.remove(child_graph_id)
            return True
        return False

    def clear(self) -> None:
        """Clear all node and connection references."""
        self.node_ids.clear()
        self.connection_ids.clear()
        self.child_graph_ids.clear()

    def get_center(self) -> tuple:
        """Get the center coordinates of the graph."""
        return (self.x + self.width / 2, self.y + self.height / 2)
