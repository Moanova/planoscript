# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : graph_layout_service.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# ---------------------------------------------------------------------
"""
Graph Layout Service for Planoscript.

This module provides services for persisting and loading graph layouts
(State_event_set, Journey_node, etc.) to/from the filesystem.
Graph layouts are stored separately from workspace layouts to allow
independent management of graph structures.

Directory structure:
    {project_file_dir}/
    \u2514\u2500\u2500 {project_file_stem}/\n        \u251c\u2500\u2500 layouts/            # WorkspaceLayout files
        \u2514\u2500\u2500 {narrative_map_id}.json
        \u2514\u2500\u2500 graphs/              # GraphLayout files
            \u251c\u2500\u2500 State_event_set/
            \u2502   \u2514\u2500\u2500 {graph_id}.json
            \u251c\u2500\u2500 Journey_node/
            \u2502   \u2514\u2500\u2500 {graph_id}.json
            \u2514\u2500\u2500 ...
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.models.graph_layout import GraphLayout


class GraphLayoutService:
    """
    Service for managing the persistence of graph layouts.
    
    Graph layouts are stored in JSON files in a dedicated 'graphs' subdirectory,
    organized by graph type (State_event_set, Journey_node, etc.).
    
    This separation allows for:
    - Independent loading/saving of individual graphs
    - Selective backup/restore of graph structures
    - Different visualization rules for different graph types
    """
    
    # Base subdirectory for graph layouts
    GRAPHS_DIR = "graphs"
    
    @classmethod
    def _get_graphs_dir(cls, project_filepath: str) -> Path:
        """
        Get the base graphs directory for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            
        Returns:
            Path to the graphs directory (created if it doesn't exist)
        """
        from core.services.layout_service import LayoutService
        
        # Reuse the project directory from LayoutService
        project_dir = LayoutService.get_project_dir(project_filepath)
        graphs_dir = project_dir / cls.GRAPHS_DIR
        graphs_dir.mkdir(parents=True, exist_ok=True)
        return graphs_dir


    @classmethod
    def _get_graph_filepath(
        cls,
        project_filepath: str,
        graph_type: str,
        graph_id: int
    ) -> Path:
        """
        Generate the filepath for a graph layout.
        
        Filepath format: {project_dir}/graphs/{graph_type}/{graph_id}.json
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_type: Type of the graph (e.g., "State_event_set")
            graph_id: ID of the graph entity
            
        Returns:
            Path to the graph layout JSON file
        """
        graphs_dir = cls._get_graphs_dir(project_filepath)
        type_dir = graphs_dir / graph_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        return type_dir / f"{graph_id}.json"


    @classmethod
    def save_graph_layout(
        cls,
        project_filepath: str,
        graph_layout: GraphLayout
    ) -> bool:
        """
        Save a graph layout to a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_layout: GraphLayout instance to save
            
        Returns:
            True if the layout was saved successfully, False otherwise
            
        Raises:
            ValueError: If project_filepath is empty or graph_layout is invalid
        """
        if not project_filepath:
            raise ValueError("project_filepath cannot be empty")
        if not graph_layout or not graph_layout.graph_id or not graph_layout.graph_type:
            raise ValueError("Invalid graph_layout: missing graph_id or graph_type")
        
        filepath = cls._get_graph_filepath(
            project_filepath,
            graph_layout.graph_type,
            graph_layout.graph_id
        )
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    graph_layout.to_dict(),
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            return True
        except IOError as e:
            print(f"Error saving graph layout to {filepath}: {e}")
            return False


    @classmethod
    def load_graph_layout(
        cls,
        project_filepath: str,
        graph_type: str,
        graph_id: int
    ) -> Optional[GraphLayout]:
        """
        Load a graph layout from a JSON file.
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_type: Type of the graph (e.g., "State_event_set")
            graph_id: ID of the graph entity
            
        Returns:
            GraphLayout instance if the file exists and is valid, None otherwise
        """
        filepath = cls._get_graph_filepath(project_filepath, graph_type, graph_id)
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return GraphLayout.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading graph layout from {filepath}: {e}")
            return None


    @classmethod
    def delete_graph_layout(
        cls,
        project_filepath: str,
        graph_type: str,
        graph_id: int
    ) -> bool:
        """
        Delete a graph layout file.
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_type: Type of the graph
            graph_id: ID of the graph entity
            
        Returns:
            True if the file was deleted or didn't exist, False on error
        """
        filepath = cls._get_graph_filepath(project_filepath, graph_type, graph_id)
        
        if not filepath.exists():
            return True  # Already deleted
        
        try:
            filepath.unlink()
            return True
        except IOError as e:
            print(f"Error deleting graph layout {filepath}: {e}")
            return False


    @classmethod
    def graph_layout_exists(
        cls,
        project_filepath: str,
        graph_type: str,
        graph_id: int
    ) -> bool:
        """
        Check if a graph layout file exists.
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_type: Type of the graph
            graph_id: ID of the graph entity
            
        Returns:
            True if the layout file exists, False otherwise
        """
        filepath = cls._get_graph_filepath(project_filepath, graph_type, graph_id)
        return filepath.exists()


    @classmethod
    def list_graph_layouts(
        cls,
        project_filepath: str,
        graph_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all graph layouts for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_type: Optional graph type filter (e.g., "State_event_set")
            
        Returns:
            List of dictionaries containing graph_type and graph_id for each layout
        """
        graphs_dir = cls._get_graphs_dir(project_filepath)
        if not graphs_dir.exists():
            return []
        
        layouts = []
        
        if graph_type:
            # List only the specified graph type
            type_dir = graphs_dir / graph_type
            if type_dir.exists():
                for filepath in type_dir.glob("*.json"):
                    try:
                        graph_id = int(filepath.stem)
                        layouts.append({
                            'graph_type': graph_type,
                            'graph_id': graph_id
                        })
                    except ValueError:
                        continue
        else:
            # List all graph types
            for type_dir in graphs_dir.iterdir():
                if type_dir.is_dir():
                    for filepath in type_dir.glob("*.json"):
                        try:
                            graph_id = int(filepath.stem)
                            layouts.append({
                                'graph_type': type_dir.name,
                                'graph_id': graph_id
                            })
                        except ValueError:
                            continue
        
        return layouts


    @classmethod
    def delete_all_graph_layouts(
        cls,
        project_filepath: str,
        graph_type: Optional[str] = None
    ) -> bool:
        """
        Delete all graph layouts for a project.
        
        Args:
            project_filepath: Full path to the project JSON file
            graph_type: Optional graph type filter (delete only this type)
            
        Returns:
            True if all layouts were deleted, False on error
        """
        graphs_dir = cls._get_graphs_dir(project_filepath)
        if not graphs_dir.exists():
            return True
        
        try:
            if graph_type:
                # Delete only the specified graph type
                type_dir = graphs_dir / graph_type
                if type_dir.exists():
                    for filepath in type_dir.glob("*.json"):
                        filepath.unlink()
                    type_dir.rmdir()
            else:
                # Delete all graph types
                for type_dir in graphs_dir.iterdir():
                    if type_dir.is_dir():
                        for filepath in type_dir.glob("*.json"):
                            filepath.unlink()
                        type_dir.rmdir()
                graphs_dir.rmdir()
            return True
        except OSError as e:
            print(f"Error deleting graph layouts: {e}")
            return False


    @classmethod
    def create_graph_layout(
        cls,
        graph_id: int,
        graph_type: str,
        x: float = 0.0,
        y: float = 0.0
    ) -> GraphLayout:
        """
        Factory method to create a GraphLayout with sensible defaults.
        
        Args:
            graph_id: ID of the graph entity
            graph_type: Type of the graph ("State_event_set", "Journey_node", etc.)
            x: X position (default: 0.0)
            y: Y position (default: 0.0)
            
        Returns:
            A new GraphLayout instance
        """
        return GraphLayout(
            graph_id=graph_id,
            graph_type=graph_type,
            x=x,
            y=y
        )
