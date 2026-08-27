# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : tree_layout.py
# Version      : 1
# Date         : 22-07-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Tree Layout Model for Planoscript.

This module defines the data structures for visual representation of
relation trees (e.g., State_event_set, Journey) in the workspace.

Unlike WorkspaceLayout which represents the layout of individual nodes and
connections, TreeLayout represents the layout of hierarchical structures
(trees) that group multiple nodes and connections together.

This separation allows for:
- Independent management of tree structures
- Selective loading/saving of trees
- Different visualization rules for trees vs. individual nodes
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class TreeLayout:
    """
    Represents the visual layout of a relation tree (e.g., State_event_set, Journey).
    
    A TreeLayout contains the visual properties of a tree container, including
    its position, size, and references to the node and connection layouts
    that belong to the tree.
    
    Attributes:
        tree_id: The ID of the tree entity (e.g., State_event_set.id)
        tree_type: The type of the tree ("State_event_set", "Journey", etc.)
        x: X position of the tree container in the workspace
        y: Y position of the tree container in the workspace
        width: Width of the tree container
        height: Height of the tree container
        color: Optional background color (hex string)
        title: Optional title displayed in the tree header
        collapsed: Whether the tree is collapsed (only show header)
        z_index: Z-order for layering (trees appear below nodes)
        node_ids: List of entity IDs that belong to this tree
        connection_ids: List of connection IDs that belong to this tree
        child_tree_ids: List of child tree IDs (for hierarchical trees)
    """
    tree_id: int
    tree_type: str
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
    child_tree_ids: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'tree_id': self.tree_id,
            'tree_type': self.tree_type,
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
            'child_tree_ids': self.child_tree_ids
        }


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeLayout':
        """Create a TreeLayout from a dictionary."""
        return cls(
            tree_id=int(data['tree_id']),
            tree_type=str(data['tree_type']),
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
            child_tree_ids=list(data.get('child_tree_ids', []))
        )


    def add_node(self, node_id: int) -> None:
        """Add a node ID to the tree."""
        if node_id not in self.node_ids:
            self.node_ids.append(node_id)


    def remove_node(self, node_id: int) -> bool:
        """Remove a node ID from the tree."""
        if node_id in self.node_ids:
            self.node_ids.remove(node_id)
            return True
        return False


    def add_connection(self, connection_id: str) -> None:
        """Add a connection ID to the tree."""
        if connection_id not in self.connection_ids:
            self.connection_ids.append(connection_id)


    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection ID from the tree."""
        if connection_id in self.connection_ids:
            self.connection_ids.remove(connection_id)
            return True
        return False


    def add_child_tree(self, child_tree_id: int) -> None:
        """Add a child tree ID."""
        if child_tree_id not in self.child_tree_ids:
            self.child_tree_ids.append(child_tree_id)


    def remove_child_tree(self, child_tree_id: int) -> bool:
        """Remove a child tree ID."""
        if child_tree_id in self.child_tree_ids:
            self.child_tree_ids.remove(child_tree_id)
            return True
        return False


    def clear(self) -> None:
        """Clear all node and connection references."""
        self.node_ids.clear()
        self.connection_ids.clear()
        self.child_tree_ids.clear()


    def get_center(self) -> tuple:
        """Get the center coordinates of the tree."""
        return (self.x + self.width / 2, self.y + self.height / 2)
