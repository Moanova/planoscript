# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_node_usecase.py
# Version      : 1
# Date         : 07-23-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Use Case for creating nodes in the workspace.

This use case handles the creation of business entities and their visual layouts,
but DOES NOT handle the creation of Qt graphic objects (QGraphicsItem).

Responsibilities:
- Create a business entity (Agent, State, Event) with a unique ID
- Add the entity to the project's NarrativeMap
- Create a NodeLayout for visual representation
- Return all data needed to create the visual node

Separation of responsibilities:
- This use case: business logic and data
- JourneyWorkspace: creation and display of QGraphicsItem
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from core.models.data_model import (
    Agent, State, Event, NarrativeMap, Project
)
from core.models.view_model import NodeLayout, NodeType
from core.services.project_service import ProjectService
from core.services.layout_service import LayoutService


class CreateNodeUseCase:
    """
    Use Case for creating a new node in the narrative map.
    
    This use case coordinates the creation of the business entity, its addition to the project,
    and the preparation of data needed for display.
    
    Attributes:
        project_service: Service for managing the current project
    """

    COMPONENT_MAPPING = {
        "Agent": {
            'entity_class': Agent,
            'node_type': NodeType.AGENT,
            'entity_type_key': 'agent',
            'default_label': 'Agent'
        },
        "State": {
            'entity_class': State,
            'node_type': NodeType.STATE,
            'entity_type_key': 'state',
            'default_label': 'State'
        },
        "Event": {
            'entity_class': Event,
            'node_type': NodeType.EVENT,
            'entity_type_key': 'event',
            'default_label': 'Event'
        },
    }


    def __init__(self, project_service: ProjectService):
        """
        Initialize the use case with the project service.
        
        Args:
            project_service: Service managing the current project
        """
        self.project_service = project_service


    def execute(
        self,
        component_type: str,
        x: float,
        y: float,
        narrative_map: Optional[NarrativeMap] = None
    ) -> Optional[Dict]:
        """
        Execute creation of a node of the specified type.
        
        Args:
            component_type: Type of component to create (e.g., "Agent", "State", "Event")
            x: X coordinate for node positioning
            y: Y coordinate for node positioning
            narrative_map: Target NarrativeMap (optional, uses the first by default)
            
        Returns:
            Dictionary containing:
                - 'success': bool (True if creation successful)
                - 'entity': the created business entity (Agent, State, Event)
                - 'entity_id': ID of the entity
                - 'layout': NodeLayout for visual representation
                - 'node_type': NodeType enum to know which type of node to create
                - 'narrative_map_id': ID of the narrative map
                - 'component_type': Component type
            
            Or None if failure (unknown type, no project, etc.)
        """
        # 1. Check that a project is opened
        if not self.project_service or not self.project_service.current_project:
            print("CreateNodeUseCase: No project opened")
            return None
        
        project = self.project_service.current_project
        
        # 2. Use the provided NarrativeMap, or the first by default
        if narrative_map is None:
            if not project or not project.narrative_map:
                return None
            narrative_map = project.narrative_map[0]
        
        # 3. Check that the component type is valid
        if component_type not in self.COMPONENT_MAPPING:
            print(f"CreateNodeUseCase: Unknown component type: {component_type}")
            return None
        
        component_config = self.COMPONENT_MAPPING[component_type]
        entity_class = component_config['entity_class']
        node_type = component_config['node_type']
        entity_type_key = component_config['entity_type_key']
        default_label = component_config['default_label']
        
        # 4. Generate a unique ID via the NarrativeMap or Project
        if entity_type_key == 'agent':
            entity_id = project.get_next_id('agent')
        else:
            entity_id = narrative_map.get_next_id(entity_type_key)
        
        # 5. Create business entity with default values
        entity = self._create_entity(entity_class, entity_id, default_label)
        
        # 6. Add entity to the NarrativeMap or Project
        self._add_entity_to_narrative_map(narrative_map, entity, entity_type_key, project)
        
        # 7. Create NodeLayout via LayoutService
        layout = LayoutService.create_node_layout(
            node_id=entity_id,
            node_type=node_type.value,
            x=x,
            y=y
        )
        
        # 8. Mark project as modified
        self.project_service.set_modified(True)
        
        # 9. Return all data needed to create the visual node
        return {
            'success': True,
            'entity': entity,
            'entity_id': entity_id,
            'layout': layout,
            'node_type': node_type,
            'narrative_map_id': narrative_map.id,
            'component_type': component_type
        }


    def _create_entity(self, entity_class, entity_id: int, default_label: str):
        """
        Create a business entity with default values.
        
        Args:
            entity_class: Entity class (Agent, State, Event)
            entity_id: Unique ID for the entity
            default_label: Default label
            
        Returns:
            Instance of the created entity
        """
        from core.models.data_model import Agent, State, Event
        
        # Create with base attributes + specific required fields
        if entity_class == Agent:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                typ="Subject"  # Required field (even if it has a default value in the model)
            )
        elif entity_class == State:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}",
                typ="Action"  # Required field with default value
            )
        elif entity_class == Event:
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}"
            )
        else:
            # Generic creation for any other entity type
            entity = entity_class(
                id=entity_id,
                lb=f"{default_label} {entity_id}"
            )
        
        return entity


    def _add_entity_to_narrative_map(
        self,
        narrative_map: NarrativeMap,
        entity,
        entity_type_key: str,
        project: Project = None
    ) -> None:
        """
        Add an entity to the NarrativeMap or Project based on its type.
        
        Args:
            narrative_map: The narrative map to update (for State, Event, Journey)
            entity: The entity to add
            entity_type_key: Entity type key ('agent', 'state', 'event')
            project: The project to update (for Agent entities)
        """
        # Agents are now managed at Project level, not NarrativeMap
        if entity_type_key == 'agent':
            if project is not None:
                project.agent.append(entity)
        else:
            # Mapping of keys to NarrativeMap attribute names
            attr_mapping = {
                'state': 'state',
                'event': 'event',
                'journey': 'journey'
            }
            
            attr_name = attr_mapping.get(entity_type_key)
            if attr_name and hasattr(narrative_map, attr_name):
                entity_list = getattr(narrative_map, attr_name)
                entity_list.append(entity)
