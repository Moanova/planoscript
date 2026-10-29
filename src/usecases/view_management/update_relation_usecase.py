# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : update_relation_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK21 (SU004/FN021)
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for updating the note of an arc (FN021, TSK21).

Applies to State_to_event and Event_to_state arcs of the current
narrative map. The journey attachment is handled separately by
Attach/DetachRelationToJourneyUseCase (TSK22).
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Union

from core.models.data_model import NarrativeMap, State_to_event, Event_to_state
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)

Arc = Union[State_to_event, Event_to_state]


class UpdateRelationUseCase:
    """Use Case for updating the annotation (note) of an arc."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, relation: Arc, note: Optional[str] = None,
                narrative_map: Optional[NarrativeMap] = None) -> Optional[Dict]:
        """Update the note of an arc.

        Args:
            relation: The arc (State_to_event / Event_to_state) to update
            note: New note (empty string clears it to None)
            narrative_map: Target NarrativeMap (optional, uses the first)

        Returns:
            Dictionary with 'success' and 'relation'
            Or None if the update failed (no project, invalid relation).
        """
        if narrative_map is None:
            if not self.project_service or not self.project_service.current_project:
                logger.warning("No project opened")
                return None
            narrative_map = self.project_service.current_project.narrative_map[0]

        if not isinstance(relation, (State_to_event, Event_to_state)):
            logger.warning("Invalid relation for update: %s", relation)
            return None
        if relation not in narrative_map.state_to_event and relation not in narrative_map.event_to_state:
            logger.warning("Relation not in the narrative map: %s", relation)
            return None

        relation.note = note if (note and note.strip()) else None
        relation.modification_date_time = datetime.now()
        if self.project_service:
            self.project_service.set_modified(True)

        logger.info("Relation %s note updated", relation.id)
        return {
            'success': True,
            'relation': relation
        }
