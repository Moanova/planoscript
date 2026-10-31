# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : attach_relation_to_journey_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK22 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for attaching a relation (arc or agent-state association)
to a journey (FN019 repositioned on the connection, RG026 revised).

A relation may belong to 1..n journeys: each attachment creates one
Journey_node referencing the relation.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Union

from core.models.data_model import (
    Journey, Journey_node, NarrativeMap,
    State_to_event, Event_to_state, State_agent_rel,
)
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)

Relation = Union[State_to_event, Event_to_state, State_agent_rel]


class AttachRelationToJourneyUseCase:
    """Use Case for attaching a relation to a journey of the current map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, arc_or_association: Relation, journey: Journey,
                narrative_map: Optional[NarrativeMap] = None) -> Optional[Dict]:
        """Attach a relation to a journey.

        Args:
            arc_or_association: The arc (State_to_event / Event_to_state) or
                the agent-state association (State_agent_rel) to attach
            journey: The target Journey entity
            narrative_map: Target NarrativeMap (optional, uses the first)

        Returns:
            Dictionary with 'success', 'node', 'already_attached'
            (True when the relation was already attached to this journey)
            Or None if the attachment failed.
        """
        if narrative_map is None:
            if not self.project_service or not self.project_service.current_project:
                logger.warning("No project opened")
                return None
            narrative_map = self.project_service.current_project.narrative_map[0]

        if not isinstance(journey, Journey) or journey not in narrative_map.journey:
            logger.warning("Invalid journey for attachment: %s", journey)
            return None
        if not isinstance(arc_or_association, (State_to_event, Event_to_state, State_agent_rel)):
            logger.warning("Invalid arc/association for attachment: %s", arc_or_association)
            return None

        if self.find_node(narrative_map, arc_or_association, journey.id) is not None:
            logger.info("Relation already attached to journey %s", journey.id)
            return {
                'success': True,
                'node': self.find_node(narrative_map, arc_or_association, journey.id),
                'already_attached': True
            }

        node = Journey_node.for_relation(narrative_map, journey.id, arc_or_association)
        narrative_map.journey_node.append(node)
        if self.project_service:
            self.project_service.set_modified(True)

        logger.info("Relation %s attached to journey %s (node %s)",
                    arc_or_association.id, journey.id, node.id)
        return {
            'success': True,
            'node': node,
            'already_attached': False
        }

    @staticmethod
    def find_node(narrative_map: NarrativeMap, arc_or_association: Relation,
                  journey_id: int) -> Optional[Journey_node]:
        """Return the Journey_node linking an arc/association to a journey, or None."""
        for node in narrative_map.journey_node:
            if node.journey_id != journey_id:
                continue
            if isinstance(arc_or_association, State_to_event) and node.state_to_event_id == arc_or_association.id:
                return node
            if isinstance(arc_or_association, Event_to_state) and node.event_to_state_id == arc_or_association.id:
                return node
            if isinstance(arc_or_association, State_agent_rel) and node.state_agent_rel_id == arc_or_association.id:
                return node
        return None
