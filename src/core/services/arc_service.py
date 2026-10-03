# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : arc_service.py
# Version      : 1
# Date         : 03-10-2026
# Content      : Arc Management Service (Event_to_state / State_to_event)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Service dedicated to managing directed arcs between States and Events.

This service centralizes the business logic for creating, querying, and
deleting Event_to_state and State_to_event arcs, ensuring data integrity
and applying business rules:
- Only State and Event entities can be linked via arcs
- A State_to_event arc represents a directed connection State -> Event
- An Event_to_state arc represents a directed connection Event -> State
- A State can be connected to multiple Events, and vice versa
- RG058: direct cycles of length 2 (State <-> Event) are forbidden
"""

from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.data_model import Event_to_state, State_to_event, State, Event, NarrativeMap


class ArcService:
    """
    Service for managing directed arcs between State and Event entities.

    This service ensures that:
    - Only valid connections (State <-> Event) are created
    - Arcs are properly maintained when entities are modified or deleted
    - The narrative map structure remains consistent
    """

    @staticmethod
    def would_create_cycle(
        narrative_map: 'NarrativeMap',
        source_entity: 'State | Event',
        target_entity: 'State | Event'
    ) -> bool:
        """
        Check whether creating a relation from source to target would form a
        direct cycle of length 2 with an already existing relation (RG058).

        A cycle of length 2 occurs when the reverse arc already exists:
        - Creating State S -> Event E is forbidden if Event E -> State S exists.
        - Creating Event E -> State S is forbidden if State S -> Event E exists.

        Args:
            narrative_map: The narrative map containing the arc lists
            source_entity: The source entity (State or Event)
            target_entity: The target entity (State or Event)

        Returns:
            True if the reverse relation already exists, False otherwise
        """
        from core.models.data_model import State, Event

        # State -> Event: forbidden if Event E -> State S already exists
        if isinstance(source_entity, State) and isinstance(target_entity, Event):
            for arc in narrative_map.event_to_state:
                if (arc.event_id == target_entity.id and
                        arc.state_id == source_entity.id):
                    return True

        # Event -> State: forbidden if State S -> Event E already exists
        if isinstance(source_entity, Event) and isinstance(target_entity, State):
            for arc in narrative_map.state_to_event:
                if (arc.state_id == target_entity.id and
                        arc.event_id == source_entity.id):
                    return True

        return False

    @staticmethod
    def create_arc(
        narrative_map: 'NarrativeMap',
        source_entity: 'State | Event',
        target_entity: 'State | Event'
    ) -> Optional['Event_to_state | State_to_event']:
        """
        Create a directed arc between two entities (State or Event).

        Applies business rules:
        - RG058: forbid direct cycles of length 2 (State <-> Event).
        - If source is State and target is Event: creates a State_to_event arc.
        - If source is Event and target is State: creates an Event_to_state arc.
        - If the exact arc already exists (duplicate): returns the existing one.
        - Otherwise: returns None (invalid relation).

        Args:
            narrative_map: The narrative map containing the arc lists
            source_entity: The source entity (State or Event)
            target_entity: The target entity (State or Event)

        Returns:
            The created or existing arc if valid, None otherwise
        """
        from core.models.data_model import State, Event, State_to_event, Event_to_state

        # RG058: forbid direct cycles of length 2 (State <-> Event)
        if ArcService.would_create_cycle(narrative_map, source_entity, target_entity):
            return None

        # Validate entity types
        if isinstance(source_entity, State) and isinstance(target_entity, Event):
            # State -> Event connection: creates a State_to_event arc
            # Check if this exact connection already exists (duplicate)
            for existing_arc in narrative_map.state_to_event:
                if (existing_arc.state_id == source_entity.id and
                    existing_arc.event_id == target_entity.id):
                    return existing_arc  # Connection already exists

            # Create a new State_to_event arc
            arc = State_to_event(
                id=narrative_map.get_next_id('state_to_event'),
                state_id=source_entity.id,
                event_id=target_entity.id
            )
            narrative_map.state_to_event.append(arc)
            return arc

        elif isinstance(source_entity, Event) and isinstance(target_entity, State):
            # Event -> State connection: creates an Event_to_state arc
            # Check if this exact connection already exists (duplicate)
            for existing_arc in narrative_map.event_to_state:
                if (existing_arc.event_id == source_entity.id and
                    existing_arc.state_id == target_entity.id):
                    return existing_arc  # Connection already exists

            # Create a new Event_to_state arc
            arc = Event_to_state(
                id=narrative_map.get_next_id('event_to_state'),
                event_id=source_entity.id,
                state_id=target_entity.id
            )
            narrative_map.event_to_state.append(arc)
            return arc

        # Invalid combination (State-State, Event-Event, or invalid types)
        return None

    @staticmethod
    def get_connected_entities(
        narrative_map: 'NarrativeMap',
        entity_id: int,
        entity_type: str
    ) -> List[Tuple[str, int]]:
        """
        Get all entities connected to a given entity through arcs.

        Args:
            narrative_map: The narrative map to search in
            entity_id: The ID of the entity to check
            entity_type: The type of the entity ('State' or 'Event')

        Returns:
            List of tuples (entity_type, entity_id) representing connected entities
        """
        connections = []

        if entity_type == "State":
            # Outgoing arcs: State -> Event
            for arc in narrative_map.state_to_event:
                if arc.state_id == entity_id:
                    connections.append(("Event", arc.event_id))
            # Incoming arcs: Event -> State
            for arc in narrative_map.event_to_state:
                if arc.state_id == entity_id:
                    connections.append(("Event", arc.event_id))

        elif entity_type == "Event":
            # Outgoing arcs: Event -> State
            for arc in narrative_map.event_to_state:
                if arc.event_id == entity_id:
                    connections.append(("State", arc.state_id))
            # Incoming arcs: State -> Event
            for arc in narrative_map.state_to_event:
                if arc.event_id == entity_id:
                    connections.append(("State", arc.state_id))

        return connections

    @staticmethod
    def delete_related_arcs(
        narrative_map: 'NarrativeMap',
        entity_id: int,
        entity_type: str
    ) -> None:
        """
        Delete all arcs related to a given entity.

        This should be called when:
        - A State is deleted (removes all State_to_event and Event_to_state arcs referencing it)
        - An Event is deleted (removes all State_to_event and Event_to_state arcs referencing it)

        Args:
            narrative_map: The narrative map containing the arc lists
            entity_id: The ID of the entity being deleted
            entity_type: The type of the entity ('State' or 'Event')
        """
        if entity_type == "State":
            narrative_map.state_to_event = [
                arc for arc in narrative_map.state_to_event
                if arc.state_id != entity_id
            ]
            narrative_map.event_to_state = [
                arc for arc in narrative_map.event_to_state
                if arc.state_id != entity_id
            ]
        elif entity_type == "Event":
            narrative_map.state_to_event = [
                arc for arc in narrative_map.state_to_event
                if arc.event_id != entity_id
            ]
            narrative_map.event_to_state = [
                arc for arc in narrative_map.event_to_state
                if arc.event_id != entity_id
            ]

    @staticmethod
    def get_arc_between(
        narrative_map: 'NarrativeMap',
        entity1_id: int,
        entity1_type: str,
        entity2_id: int,
        entity2_type: str
    ) -> Optional['Event_to_state | State_to_event']:
        """
        Find an arc connecting two specific entities.

        Args:
            narrative_map: The narrative map to search in
            entity1_id: ID of the first entity
            entity1_type: Type of the first entity ('State' or 'Event')
            entity2_id: ID of the second entity
            entity2_type: Type of the second entity ('State' or 'Event')

        Returns:
            The arc connecting the two entities, or None if not found
        """
        # Case 1: State -> Event (State_to_event arc)
        if entity1_type == "State" and entity2_type == "Event":
            for arc in narrative_map.state_to_event:
                if arc.state_id == entity1_id and arc.event_id == entity2_id:
                    return arc

        # Case 2: Event -> State (Event_to_state arc)
        elif entity1_type == "Event" and entity2_type == "State":
            for arc in narrative_map.event_to_state:
                if arc.event_id == entity1_id and arc.state_id == entity2_id:
                    return arc

        return None

    @staticmethod
    def can_connect(
        entity1_type: str,
        entity2_type: str
    ) -> bool:
        """
        Check if two entity types can be connected via an arc.

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
