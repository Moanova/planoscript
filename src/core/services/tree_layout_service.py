# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_workspace.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# ---------------------------------------------------------------------
# Version      : 2
# Date         : 2026-08-27
# Content      : Non-functional version (intermediate redesign stage)
# Build        : TSC + Mistral Vibe
# ---------------------------------------------------------------------
"""
Tree Layout Service for Planoscript.

This module provides services for persisting and loading tree layouts
(State_event_set, Journey, etc.) to/from the filesystem.
Tree layouts are stored separately from workspace layouts to allow
independent management of hierarchical structures.

Directory structure:
    {project_file_dir}/
    └── {project_file_stem}/
        ├── layouts/            # WorkspaceLayout files
        │   └── {narrative_map_id}.json
        └── trees/              # TreeLayout files
            ├── State_event_set/
            │   └── {tree_id}.json
            ├── Journey/
            │   └── {tree_id}.json
            └── ...
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.models.tree_layout import TreeLayout


class TreeLayoutService:
    """
    Service for managing the persistence of tree layouts.
    
    Tree layouts are stored in JSON files in a dedicated 'trees' subdirectory,
    organized by tree type (State_event_set, Journey, etc.).
    
    This separation allows for:
    - Independent loading/saving of individual trees
    - Selective backup/restore of tree structures
    - Different visualization rules for different tree types
    """
    
    # Base subdirectory for tree layouts
    TREES_DIR = "trees"
    
    @classmethod
    def _get_trees_dir(cls, project_filepath: str) -> Path:
        """
        Get the base trees directory for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the trees directory (created if it doesn't exist)
        """
        from core.services.layout_service import LayoutService
        
        # Reuse the project directory from LayoutService
        project_dir = LayoutService.get_project_dir(project_filepath)
        trees_dir = project_dir / cls.TREES_DIR
        trees_dir.mkdir(parents=True, exist_ok=True)
        return trees_dir


    @classmethod
    def _get_tree_filepath(
        cls,
        project_filepath: str,
        tree_type: str,
        tree_id: int
    ) -> Path:
        """
        Generate the filepath for a tree layout.
        
        Filepath format: {project_dir}/trees/{tree_type}/{tree_id}.json
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_type: Type of the tree (e.g., "State_event_set")
            tree_id: ID of the tree entity
            
        Returns:
            Path to the tree layout JSON file
        """
        trees_dir = cls._get_trees_dir(project_filepath)
        type_dir = trees_dir / tree_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        return type_dir / f"{tree_id}.json"


    @classmethod
    def save_tree_layout(
        cls,
        project_filepath: str,
        tree_layout: TreeLayout
    ) -> bool:
        """
        Save a tree layout to a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_layout: TreeLayout instance to save
            
        Returns:
            True if the layout was saved successfully, False otherwise
            
        Raises:
            ValueError: If project_filepath is empty or tree_layout is invalid
        """
        if not project_filepath:
            raise ValueError("project_filepath cannot be empty")
        if not tree_layout or not tree_layout.tree_id or not tree_layout.tree_type:
            raise ValueError("Invalid tree_layout: missing tree_id or tree_type")
        
        filepath = cls._get_tree_filepath(
            project_filepath,
            tree_layout.tree_type,
            tree_layout.tree_id
        )
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    tree_layout.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            return True
        except IOError as e:
            print(f"Error saving tree layout to {filepath}: {e}")
            return False


    @classmethod
    def load_tree_layout(
        cls,
        project_filepath: str,
        tree_type: str,
        tree_id: int
    ) -> Optional[TreeLayout]:
        """
        Load a tree layout from a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_type: Type of the tree (e.g., "State_event_set")
            tree_id: ID of the tree entity
            
        Returns:
            TreeLayout instance if the file exists and is valid, None otherwise
        """
        filepath = cls._get_tree_filepath(project_filepath, tree_type, tree_id)
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return TreeLayout.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading tree layout from {filepath}: {e}")
            return None


    @classmethod
    def delete_tree_layout(
        cls,
        project_filepath: str,
        tree_type: str,
        tree_id: int
    ) -> bool:
        """
        Delete a tree layout file.
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_type: Type of the tree
            tree_id: ID of the tree entity
            
        Returns:
            True if the file was deleted or didn't exist, False on error
        """
        filepath = cls._get_tree_filepath(project_filepath, tree_type, tree_id)
        
        if not filepath.exists():
            return True  # Already deleted
        
        try:
            filepath.unlink()
            return True
        except IOError as e:
            print(f"Error deleting tree layout {filepath}: {e}")
            return False


    @classmethod
    def tree_layout_exists(
        cls,
        project_filepath: str,
        tree_type: str,
        tree_id: int
    ) -> bool:
        """
        Check if a tree layout file exists.
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_type: Type of the tree
            tree_id: ID of the tree entity
            
        Returns:
            True if the layout file exists, False otherwise
        """
        filepath = cls._get_tree_filepath(project_filepath, tree_type, tree_id)
        return filepath.exists()


    @classmethod
    def list_tree_layouts(
        cls,
        project_filepath: str,
        tree_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all tree layouts for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_type: Optional tree type filter (e.g., "State_event_set")
            
        Returns:
            List of dictionaries containing tree_type and tree_id for each layout
        """
        trees_dir = cls._get_trees_dir(project_filepath)
        if not trees_dir.exists():
            return []
        
        layouts = []
        
        if tree_type:
            # List only the specified tree type
            type_dir = trees_dir / tree_type
            if type_dir.exists():
                for filepath in type_dir.glob("*.json"):
                    try:
                        tree_id = int(filepath.stem)
                        layouts.append({
                            'tree_type': tree_type,
                            'tree_id': tree_id
                        })
                    except ValueError:
                        continue
        else:
            # List all tree types
            for type_dir in trees_dir.iterdir():
                if type_dir.is_dir():
                    for filepath in type_dir.glob("*.json"):
                        try:
                            tree_id = int(filepath.stem)
                            layouts.append({
                                'tree_type': type_dir.name,
                                'tree_id': tree_id
                            })
                        except ValueError:
                            continue
        
        return layouts


    @classmethod
    def delete_all_tree_layouts(
        cls,
        project_filepath: str,
        tree_type: Optional[str] = None
    ) -> bool:
        """
        Delete all tree layouts for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            tree_type: Optional tree type filter (delete only this type)
            
        Returns:
            True if all layouts were deleted, False on error
        """
        trees_dir = cls._get_trees_dir(project_filepath)
        if not trees_dir.exists():
            return True
        
        try:
            if tree_type:
                # Delete only the specified tree type
                type_dir = trees_dir / tree_type
                if type_dir.exists():
                    for filepath in type_dir.glob("*.json"):
                        filepath.unlink()
                    type_dir.rmdir()
            else:
                # Delete all tree types
                for type_dir in trees_dir.iterdir():
                    if type_dir.is_dir():
                        for filepath in type_dir.glob("*.json"):
                            filepath.unlink()
                        type_dir.rmdir()
                trees_dir.rmdir()
            return True
        except OSError as e:
            print(f"Error deleting tree layouts: {e}")
            return False


    @classmethod
    def create_tree_layout(
        cls,
        tree_id: int,
        tree_type: str,
        x: float = 0.0,
        y: float = 0.0
    ) -> TreeLayout:
        """
        Factory method to create a TreeLayout with sensible defaults.
        
        Args:
            tree_id: ID of the tree entity
            tree_type: Type of the tree ("State_event_set", "Journey", etc.)
            x: X position (default: 0.0)
            y: Y position (default: 0.0)
            
        Returns:
            A new TreeLayout instance
        """
        return TreeLayout(
            tree_id=tree_id,
            tree_type=tree_type,
            x=x,
            y=y
        )
