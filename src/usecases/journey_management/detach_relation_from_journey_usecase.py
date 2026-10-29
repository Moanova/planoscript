# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : detach_relation_from_journey_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK22 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for detaching a relation (arc or agent-state association)
from a journey (RG026 revised).

Detaching removes the Journey_node linking the relation to the journey;
the relation itself is left untouched (it may belong to other journeys).
"""
import logging
from typing import Optional, Dict, Union

from core.models.data_model import (
    Journey, NarrativeMap,
    State_to_event, Event_to_state, State_agent_rel,
)
from core.services.project_service import ProjectService
from usecases.journey_management.attach_relation_to_journey_usecase import (
    AttachRelationToJourneyUseCase,
)

logger = logging.getLogger(__name__)

Relation = Union[State_to_event, Event_to_state, State_agent_rel]


class DetachRelationFromJourneyUseCase:
    """Use Case for detaching a relation from a journey of the current map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, relation: Relation, journey: Journey,
                narrative_map: Optional[NarrativeMap] = None) -> Optional[Dict]:
        """Detach a relation from a journey.

        Args:
            relation: The arc (State_to_event / Event_to_state) or the
                agent-state association (State_agent_rel) to detach
            journey: The Journey entity to detach from
            narrative_map: Target NarrativeMap (optional, uses the first)

        Returns:
            Dictionary with 'success' and 'detached' (False when the
            relation was not attached to this journey)
            Or None if the operation failed.
        """
        if narrative_map is None:
            if not self.project_service or not self.project_service.current_project:
                logger.warning("No project opened")
                return None
            narrative_map = self.project_service.current_project.narrative_map[0]

        if not isinstance(journey, Journey) or journey not in narrative_map.journey:
            logger.warning("Invalid journey for detachment: %s", journey)
            return None

        node = AttachRelationToJourneyUseCase.find_node(narrative_map, relation, journey.id)
        if node is None:
            logger.info("Relation %s not attached to journey %s", relation.id, journey.id)
            return {
                'success': True,
                'detached': False
            }

        narrative_map.journey_node.remove(node)
        if self.project_service:
            self.project_service.set_modified(True)

        logger.info("Relation %s detached from journey %s (node %s removed)",
                    relation.id, journey.id, node.id)
        return {
            'success': True,
            'detached': True
        }
