# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : update_agent_state_association_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK21 (SU004/FN021)
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for updating the note of an agent-state association (FN021, TSK21).

Applies to State_agent_rel of the current narrative map.
"""
import logging
from datetime import datetime
from typing import Optional, Dict

from core.models.data_model import NarrativeMap, State_agent_rel
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class UpdateAgentStateAssociationUseCase:
    """Use Case for updating the annotation (note) of a State_agent_rel."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, relation: State_agent_rel, note: Optional[str] = None,
                narrative_map: Optional[NarrativeMap] = None) -> Optional[Dict]:
        """Update the note of an agent-state association.

        Args:
            relation: The State_agent_rel to update
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

        if not isinstance(relation, State_agent_rel) or relation not in narrative_map.state_agent_rel:
            logger.warning("Invalid association for update: %s", relation)
            return None

        relation.note = note if (note and note.strip()) else None
        relation.modification_date_time = datetime.now()
        if self.project_service:
            self.project_service.set_modified(True)

        logger.info("Association %s note updated", relation.id)
        return {
            'success': True,
            'relation': relation
        }
