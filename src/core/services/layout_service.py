# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : layout_service.py
# Version      : 2
# Date         : 22-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Layout Service for Planoscript.

This module provides services for persisting and loading visual layouts
(workspace layouts) to/from the filesystem. It handles the storage of
node positions, connection paths, zoom levels, and scroll positions
separately from the business data model.

Layout files are stored in a subdirectory named after the project file:
    {project_file_dir}/{project_file_stem}/layouts/{narrative_map_id}.json

Example:
    /user/projects/mon_projet.json
    /user/projects/mon_projet/layouts/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv.json

This ensures that:
- All files related to a project are grouped together
- Users can easily identify which layout folder belongs to which project
- Moving the project file and its folder together preserves all data
"""

import json
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.models.view_model import (
    WorkspaceLayout,
    NodeLayout,
    ConnectionLayout
)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be used as a directory name.
    
    Replaces invalid characters (for Windows, Linux, macOS filesystems)
    with underscores. Also trims whitespace and limits length.
    
    Args:
        filename: The filename to sanitize (with or without extension)
        
    Returns:
        A safe string for use as a directory name
    """
    # Characters invalid on Windows, Linux, or macOS
    invalid_chars = r'[<>:"\/|?*\x00-\x1f]'
    # Replace invalid characters with underscore
    safe_name = re.sub(invalid_chars, '_', filename)
    # Remove leading/trailing whitespace and dots
    safe_name = safe_name.strip().strip('.')
    # If empty after sanitization, use a default
    if not safe_name:
        safe_name = "untitled"
    # Limit length to avoid filesystem issues (100 chars is safe for most FS)
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    return safe_name


def get_safe_dir_name(name: str, base_dir: Path) -> Path:
    """
    Generate a unique directory name within base_dir.
    
    If the name already exists, append a numeric suffix (_2, _3, etc.).
    Falls back to a hash-based name if too many conflicts.
    
    Args:
        name: The desired directory name (already sanitized)
        base_dir: The parent directory
        
    Returns:
        A Path to a unique directory that doesn't exist yet
    """
    candidate = base_dir / name
    if not candidate.exists():
        return candidate
    
    # Try numeric suffixes
    counter = 2
    while counter < 1000:
        new_candidate = base_dir / f"{name}_{counter}"
        if not new_candidate.exists():
            return new_candidate
        counter += 1
    
    # Fallback: use hash of the name
    import hashlib
    name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
    return base_dir / f"{name}_{name_hash}"


class LayoutService:
    """
    Service for managing the persistence of workspace layouts.
    
    Layouts are stored in JSON files in a subdirectory named after the project file.
    Each layout file corresponds to a specific narrative map within a project.
    
    Directory structure:
        {project_file_dir}/
        └── {project_file_stem}/
            └── layouts/
                └── {narrative_map_id}.json
    
    Example:
        /user/docs/mon_projet.json
        /user/docs/mon_projet/layouts/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv.json
    """
    
    # Subdirectory name for layouts within project directory
    LAYOUT_SUBDIR = "layouts"
    
    @classmethod
    def _get_project_dir(cls, project_filepath: str) -> Path:
        """
        Get the directory for a project based on its filepath.
        
        The project directory is named after the project file (without extension).
        Example: "/path/to/mon_projet.json" -> "/path/to/mon_projet/"
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the project directory (created if it doesn't exist)
        """
        filepath = Path(project_filepath).resolve()
        base_dir = filepath.parent
        safe_stem = sanitize_filename(filepath.stem)
        
        # Get a unique directory name
        project_dir = get_safe_dir_name(safe_stem, base_dir)
        return project_dir

    @classmethod
    def _get_layout_dir(cls, project_filepath: str) -> Path:
        """
        Get the layouts directory for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the layouts directory (created if it doesn't exist)
        """
        project_dir = cls._get_project_dir(project_filepath)
        layout_dir = project_dir / cls.LAYOUT_SUBDIR
        layout_dir.mkdir(parents=True, exist_ok=True)
        return layout_dir

    @classmethod
    def _get_layout_filepath(
        cls, 
        project_filepath: str,
        narrative_map_id: str
    ) -> Path:
        """
        Generate the filepath for a workspace layout.
        
        New structure: {project_dir}/{stem}/layouts/{narrative_map_id}.json
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            
        Returns:
            Path to the layout JSON file
        """
        layout_dir = cls._get_layout_dir(project_filepath)
        safe_map_id = narrative_map_id.replace("/", "_").replace("\\", "_")
        return layout_dir / f"{safe_map_id}.json"

    @classmethod
    def get_project_dir(cls, project_filepath: str) -> Path:
        """
        Public method to get the project directory (for external use).
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the project directory
        """
        return cls._get_project_dir(project_filepath)

    @classmethod
    def get_layout_dir(cls, project_filepath: str) -> Path:
        """
        Public method to get the layouts directory (for external use).
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the layouts directory
        """
        return cls._get_layout_dir(project_filepath)

    @classmethod
    def save_workspace_layout(
        cls,
        project_filepath: str,
        narrative_map_id: str,
        layout: WorkspaceLayout
    ) -> bool:
        """
        Save a workspace layout to a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            layout: WorkspaceLayout instance to save
            
        Returns:
            True if the layout was saved successfully, False otherwise
            
        Raises:
            ValueError: If project_filepath is empty or narrative_map_id is empty
            IOError: If the file cannot be written
        """
        if not project_filepath:
            raise ValueError("project_filepath cannot be empty")
        if not narrative_map_id:
            raise ValueError("narrative_map_id cannot be empty")
        
        filepath = cls._get_layout_filepath(project_filepath, narrative_map_id)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    layout.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            return True
        except IOError as e:
            print(f"Error saving layout to {filepath}: {e}")
            return False

    @classmethod
    def load_workspace_layout(
        cls,
        project_filepath: str,
        narrative_map_id: str
    ) -> Optional[WorkspaceLayout]:
        """
        Load a workspace layout from a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            
        Returns:
            WorkspaceLayout instance if the file exists and is valid,
            None otherwise
        """
        filepath = cls._get_layout_filepath(project_filepath, narrative_map_id)
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return WorkspaceLayout.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading layout from {filepath}: {e}")
            return None

    @classmethod
    def delete_workspace_layout(
        cls,
        project_filepath: str,
        narrative_map_id: str
    ) -> bool:
        """
        Delete a workspace layout file.
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            
        Returns:
            True if the file was deleted or didn't exist, False on error
        """
        filepath = cls._get_layout_filepath(project_filepath, narrative_map_id)
        
        if not filepath.exists():
            return True  # Already deleted
        
        try:
            filepath.unlink()
            return True
        except IOError as e:
            print(f"Error deleting layout {filepath}: {e}")
            return False

    @classmethod
    def workspace_layout_exists(
        cls,
        project_filepath: str,
        narrative_map_id: str
    ) -> bool:
        """
        Check if a workspace layout file exists.
        
        Args:
            project_filepath: Full path to the project JSON file
            narrative_map_id: UUID of the narrative map
            
        Returns:
            True if the layout file exists, False otherwise
        """
        filepath = cls._get_layout_filepath(project_filepath, narrative_map_id)
        return filepath.exists()

    @classmethod
    def list_project_layouts(
        cls,
        project_filepath: str
    ) -> List[str]:
        """
        List all narrative map IDs that have saved layouts for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            List of narrative_map_id strings that have saved layouts
        """
        layout_dir = cls._get_layout_dir(project_filepath)
        if not layout_dir.exists():
            return []
        
        layouts = []
        for filepath in layout_dir.glob("*.json"):
            # Le nom du fichier est directement l'UUID de la NarrativeMap
            narrative_map_id = filepath.stem
            # Revert sanitization (replace underscores with hyphens for UUIDs)
            narrative_map_id = narrative_map_id.replace("_", "-")
            layouts.append(narrative_map_id)
        
        return layouts

    @classmethod
    def delete_project_layouts(
        cls,
        project_filepath: str
    ) -> bool:
        """
        Delete all layout files for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            True if all layouts were deleted or directory didn't exist, False on error
        """
        layout_dir = cls._get_layout_dir(project_filepath)
        if not layout_dir.exists():
            return True
        
        try:
            # Delete all JSON files in the layouts directory
            for filepath in layout_dir.glob("*.json"):
                filepath.unlink()
            # Remove the layouts directory if empty
            layout_dir.rmdir()
            
            # Try to remove the project directory if empty
            project_dir = cls._get_project_dir(project_filepath)
            try:
                project_dir.rmdir()
            except OSError:
                # Directory not empty (maybe other files), that's ok
                pass
            
            return True
        except IOError as e:
            print(f"Error deleting project layouts {layout_dir}: {e}")
            return False

    @classmethod
    def generate_connection_id(cls) -> str:
        """
        Generate a unique ID for a new connection.
        
        Returns:
            A unique string ID (UUID4)
        """
        return str(uuid.uuid4())

    @classmethod
    def create_empty_layout(
        cls,
        narrative_map_id: str
    ) -> WorkspaceLayout:
        """
        Create an empty WorkspaceLayout with default values.
        
        Args:
            narrative_map_id: UUID of the narrative map
            
        Returns:
            A new empty WorkspaceLayout instance
        """
        return WorkspaceLayout(
            narrative_map_id=narrative_map_id,
            nodes={},
            connections={},
            zoom_level=1.0,
            scroll_x=0.0,
            scroll_y=0.0
        )

    @classmethod
    def create_node_layout(
        cls,
        node_id: int,
        node_type: str,
        x: float = 100.0,
        y: float = 100.0,
        width: float = 120.0,
        height: float = 80.0
    ) -> NodeLayout:
        """
        Factory method to create a NodeLayout with sensible defaults.
        
        Args:
            node_id: The business entity ID
            node_type: The type of the node (string from NodeType enum)
            x: X position (default: 100.0)
            y: Y position (default: 100.0)
            width: Node width (default: 120.0)
            height: Node height (default: 80.0)
            
        Returns:
            A new NodeLayout instance
            
        Raises:
            ValueError: If node_type is not a valid NodeType
        """
        from core.models.view_model import NodeType
        
        try:
            node_type_enum = NodeType(node_type)
        except ValueError:
            raise ValueError(f"Invalid node_type: {node_type}. Must be one of {list(NodeType)}")
        
        return NodeLayout(
            node_id=node_id,
            node_type=node_type_enum,
            x=x,
            y=y,
            width=width,
            height=height
        )

    @classmethod
    def create_connection_layout(
        cls,
        source_node_id: int,
        target_node_id: int,
        connection_id: Optional[str] = None
    ) -> ConnectionLayout:
        """
        Factory method to create a ConnectionLayout with sensible defaults.
        
        Args:
            source_node_id: Business entity ID of the source node
            target_node_id: Business entity ID of the target node
            connection_id: Optional unique ID (generated if None)
            
        Returns:
            A new ConnectionLayout instance
        """
        if connection_id is None:
            connection_id = cls.generate_connection_id()
        
        return ConnectionLayout(
            id=connection_id,
            source_node_id=source_node_id,
            source_port="right",
            target_node_id=target_node_id,
            target_port="left",
            style="straight",
            color=None,
            thickness=2.0
        )
