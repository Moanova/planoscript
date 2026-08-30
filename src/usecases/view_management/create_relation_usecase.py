# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_relation_usecase.py
# Version      : 1
# Date         : 07-23-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Use Case for creating relations between nodes in the workspace.

This use case handles the creation of relation entities (State_agent_rel, State_node, Journey_node)
and their visual layouts (ConnectionLayout), but DOES NOT handle the creation of Qt
graphic objects (QGraphicsLineItem).

Responsibilities:
- Create a relation entity with unique IDs
- Add the relation entity to the project's NarrativeMap
- Create a ConnectionLayout for visual representation
- Return all data needed to create the visual connection

Separation of responsibilities:
- This use case: business logic and data
- JourneyWorkspace: creation and display of QGraphicsLineItem
"""

from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from uuid import uuid4

from core.models.data_model import (
    State_agent_rel,
    NarrativeMap
)
from core.models.view_model import ConnectionLayout, NodeType
from core.services.project_service import ProjectService
from core.services.layout_service import LayoutService


class CreateRelationUseCase:
    """
    Use Case for creating a new relation between two nodes in the narrative map.
    
    This use case coordinates the creation of the relation entity, its addition to the project,
    and the preparation of data needed for displaying the connection.
    
    Attributes:
        project_service: Service for managing the current project
    """

    # Mapping of relation types to entity classes
    # Note: Only State_agent_rel exists in the new data model
    # State-Event relations are handled directly via StateNodeService
    RELATION_MAPPING = {
        "State to Agent": {
            'entity_class': State_agent_rel,
            'relation_type_key': 'state_agent_rel',
            'source_id_attr': 'state_id',
            'target_id_attr': 'agent_id'
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
        source_entity: Any,
        target_entity: Any,
        relation_type: str,
        narrative_map: Optional[NarrativeMap] = None
    ) -> Optional[Dict]:
        """
        Execute creation of a relation of the specified type between two entities.
        
        Args:
            source_entity: Source entity (Agent, State, Event)
            target_entity: Target entity (Agent, State, Event)
            relation_type: Relation type (e.g., "Satet to Agent", "Satet to Event", "Event to State")
            narrative_map: Target NarrativeMap (optional, uses the first by default)
            
        Returns:
            Dictionary containing:
                - 'success': bool (True if creation successful)
                - 'relation_entity': the created relation entity
                - 'connection_layout': ConnectionLayout for visual representation
                - 'relation_type': Relation type
                - 'narrative_map_id': ID of the narrative map
                
            Or None if failure (unknown type, no project, etc.)
        """
        # 1. Check that a project is opened
        if not self.project_service or not self.project_service.current_project:
            print("CreateRelationUseCase: No project opened")
            return None
        
        project = self.project_service.current_project
        
        # 2. Use the provided NarrativeMap, or the first by default
        if narrative_map is None:
            if not project or not project.narrative_map:
                return None
            narrative_map = project.narrative_map[0]
        
        # 3. Check that the relation type is valid
        if relation_type not in self.RELATION_MAPPING:
            print(f"CreateRelationUseCase: Unknown relation type: {relation_type}")
            return None
        
        relation_config = self.RELATION_MAPPING[relation_type]
        relation_class = relation_config['entity_class']
        relation_type_key = relation_config['relation_type_key']
        source_id_attr = relation_config['source_id_attr']
        target_id_attr = relation_config['target_id_attr']
        
        # 4. Generate a unique ID via the NarrativeMap
        relation_id = narrative_map.get_next_id(relation_type_key)
        
        # 5. Create the relation entity with source and target IDs
        relation_entity = self._create_relation_entity(
            relation_class=relation_class,
            relation_id=relation_id,
            source_entity=source_entity,
            target_entity=target_entity,
            source_id_attr=source_id_attr,
            target_id_attr=target_id_attr
        )
        
        if relation_entity is None:
            return None
        
        # 6. Add the relation entity to the NarrativeMap
        self._add_relation_to_narrative_map(narrative_map, relation_entity, relation_type_key)
        
        # 7. Create ConnectionLayout via LayoutService
        connection_layout = LayoutService.create_connection_layout(
            source_node_id=source_entity.id,
            target_node_id=target_entity.id
        )
        
        # 8. Mark project as modified
        self.project_service.set_modified(True)
        
        # 9. Return all data needed to create the visual connection
        return {
            'success': True,
            'relation_entity': relation_entity,
            'relation_id': relation_id,
            'connection_layout': connection_layout,
            'relation_type': relation_type,
            'source_entity': source_entity,
            'target_entity': target_entity,
            'narrative_map_id': narrative_map.id
        }


    def _create_relation_entity(
        self,
        relation_class,
        relation_id: int,
        source_entity: Any,
        target_entity: Any,
        source_id_attr: str,
        target_id_attr: str
    ) -> Any:
        """
        Create a relation entity with source and target IDs.
        
        Args:
            relation_class: Relation entity class
            relation_id: Unique ID for the relation
            source_entity: Source entity
            target_entity: Target entity
            source_id_attr: Attribute name for source ID
            target_id_attr: Attribute name for target ID
            
        Returns:
            Instance of the created relation entity
        """
        from core.models.data_model import State_agent_rel
        
        # Create a dictionary with base attributes
        relation_data = {
            'id': relation_id,
            'creation_date_time': datetime.now(),
            'modification_date_time': None
        }
        
        # Add source and target IDs
        relation_data[source_id_attr] = source_entity.id
        relation_data[target_id_attr] = target_entity.id
        
        # Add optional specific attributes for State_agent_rel
        if relation_class == State_agent_rel:
            relation_data['note'] = None
        
        # Create and return the entity
        return relation_class(**relation_data)


    def _add_relation_to_narrative_map(
        self,
        narrative_map: NarrativeMap,
        relation_entity,
        relation_type_key: str
    ) -> None:
        """
        Add a relation entity to the NarrativeMap based on its type.
        
        Args:
            narrative_map: The narrative map to update
            relation_entity: The relation entity to add
            relation_type_key: Relation type key
        """
        # Mapping of keys to NarrativeMap attribute names
        attr_mapping = {
            'state_agent_rel': 'state_agent_rel',
        }
        
        attr_name = attr_mapping.get(relation_type_key)
        if attr_name and hasattr(narrative_map, attr_name):
            relation_list = getattr(narrative_map, attr_name)
            relation_list.append(relation_entity)
