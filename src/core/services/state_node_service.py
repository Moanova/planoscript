# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : state_node_service.py
# Version      : 1
# Date         : 27-08-2026
# Content      : State Node Management Service
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Service dedicated to managing State_node entities (State-Event relations).

This service centralizes the business logic for creating, querying, and deleting
State_node entities, ensuring data integrity and applying business rules:
- Only State and Event entities can be linked
- A State_node represents a connection between State and Event (bidirectional)
- A State can be connected to multiple Events, and vice versa
"""

from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.data_model import State_node, State, Event, NarrativeMap


class StateNodeService:
    """
    Service for managing State_node entities (relations between State and Event).
    
    This service ensures that:
    - Only valid connections (State <-> Event) are created
    - State_node entities are properly maintained when entities are modified or deleted
    - The narrative map structure remains consistent
    """

    @staticmethod
    def create_state_node(
        narrative_map: 'NarrativeMap',
        source_entity: 'State | Event',
        target_entity: 'State | Event'
    ) -> Optional['State_node']:
        """
        Create a State_node between two entities (State or Event).
        
        Applies business rules:
        - If source is State and target is Event: state_id=source.id, to_event_id=target.id
        - If source is Event and target is State: from_event_id=source.id, state_id=target.id
        - Otherwise: returns None (invalid relation)
        
        Args:
            narrative_map: The narrative map containing the State_node list
            source_entity: The source entity (State or Event)
            target_entity: The target entity (State or Event)
            
        Returns:
            The created State_node if valid, None otherwise
        """
        from core.models.data_model import State, Event, State_node
        
        # Validate entity types
        if isinstance(source_entity, State) and isinstance(target_entity, Event):
            # State -> Event connection
            # Check if this connection already exists
            for existing_node in narrative_map.state_node:
                if (existing_node.state_id == source_entity.id and 
                    existing_node.to_event_id == target_entity.id):
                    return existing_node  # Connection already exists
            
            state_node = State_node(
                id=narrative_map.get_next_id('state_node'),
                from_event_id=0,  # No predecessor
                state_id=source_entity.id,
                to_event_id=target_entity.id
            )
            narrative_map.state_node.append(state_node)
            return state_node
            
        elif isinstance(source_entity, Event) and isinstance(target_entity, State):
            # Event -> State connection
            # Check if this connection already exists
            for existing_node in narrative_map.state_node:
                if (existing_node.from_event_id == source_entity.id and 
                    existing_node.state_id == target_entity.id):
                    return existing_node  # Connection already exists
            
            state_node = State_node(
                id=narrative_map.get_next_id('state_node'),
                from_event_id=source_entity.id,
                state_id=target_entity.id,
                to_event_id=0  # No successor
            )
            narrative_map.state_node.append(state_node)
            return state_node
        
        # Invalid combination (State-State, Event-Event, or invalid types)
        return None

    @staticmethod
    def get_connected_entities(
        narrative_map: 'NarrativeMap',
        entity_id: int,
        entity_type: str
    ) -> List[Tuple[str, int]]:
        """
        Get all entities connected to a given entity through State_node relations.
        
        Args:
            narrative_map: The narrative map to search in
            entity_id: The ID of the entity to check
            entity_type: The type of the entity ('State' or 'Event')
            
        Returns:
            List of tuples (entity_type, entity_id) representing connected entities
        """
        connections = []
        
        for node in narrative_map.state_node:
            if entity_type == "State" and node.state_id == entity_id:
                # This State is connected to Events
                if node.from_event_id != 0:
                    connections.append(("Event", node.from_event_id))
                if node.to_event_id != 0:
                    connections.append(("Event", node.to_event_id))
            elif entity_type == "Event":
                # This Event is connected to States
                if node.from_event_id == entity_id:
                    connections.append(("State", node.state_id))
                if node.to_event_id == entity_id:
                    connections.append(("State", node.state_id))
        
        return connections

    @staticmethod
    def delete_related_nodes(
        narrative_map: 'NarrativeMap',
        entity_id: int,
        entity_type: str
    ) -> None:
        """
        Delete all State_node entities related to a given entity.
        
        This should be called when:
        - A State is deleted
        - An Event is deleted
        
        Args:
            narrative_map: The narrative map containing the State_node list
            entity_id: The ID of the entity being deleted
            entity_type: The type of the entity ('State' or 'Event')
        """
        to_delete = []
        
        for node in narrative_map.state_node:
            if entity_type == "State" and node.state_id == entity_id:
                to_delete.append(node)
            elif entity_type == "Event":
                if node.from_event_id == entity_id or node.to_event_id == entity_id:
                    to_delete.append(node)
        
        # Remove all marked nodes
        for node in to_delete:
            narrative_map.state_node.remove(node)

    @staticmethod
    def get_state_node_between(
        narrative_map: 'NarrativeMap',
        entity1_id: int,
        entity1_type: str,
        entity2_id: int,
        entity2_type: str
    ) -> Optional['State_node']:
        """
        Find a State_node connecting two specific entities.
        
        Args:
            narrative_map: The narrative map to search in
            entity1_id: ID of the first entity
            entity1_type: Type of the first entity ('State' or 'Event')
            entity2_id: ID of the second entity
            entity2_type: Type of the second entity ('State' or 'Event')
            
        Returns:
            The State_node connecting the two entities, or None if not found
        """
        from core.models.data_model import State_node
        
        # Case 1: State -> Event
        if entity1_type == "State" and entity2_type == "Event":
            for node in narrative_map.state_node:
                if node.state_id == entity1_id and node.to_event_id == entity2_id:
                    return node
        
        # Case 2: Event -> State
        elif entity1_type == "Event" and entity2_type == "State":
            for node in narrative_map.state_node:
                if node.from_event_id == entity1_id and node.state_id == entity2_id:
                    return node
        
        return None

    @staticmethod
    def can_connect(
        entity1_type: str,
        entity2_type: str
    ) -> bool:
        """
        Check if two entity types can be connected via a State_node.
        
        Args:
            entity1_type: Type of the first entity
            entity2_type: Type of the second entity
            
        Returns:
            True if the connection is valid, False otherwise
        """
        valid_connections = {
            ("State", "Event"),
            ("Event", "State")
        }
        return (entity1_type, entity2_type) in valid_connections
