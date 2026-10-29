# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_journey_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK22 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for creating a journey of the narrative map (FN023).

RG023: the newly created journey automatically becomes the active journey.
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Journey
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class CreateJourneyUseCase:
    """Use Case for creating a new journey in the current narrative map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, lb: Optional[str] = None,
                note: Optional[str] = None) -> Optional[Dict]:
        """Create a journey and activate it (RG023).

        Args:
            lb: Label of the journey (defaults to "Journey {id}")
            note: Optional note of the journey

        Returns:
            Dictionary with 'success', 'entity', 'entity_id'
            Or None if the creation failed (no project).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        narrative_map = self.project_service.current_project.narrative_map[0]

        entity_id = narrative_map.get_next_id('journey')
        entity = Journey(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip()
                else f"Journey {entity_id}"),
            default=False,
            note=(note if note and note.strip() else None)
        )
        narrative_map.journey.append(entity)
        # RG023: the new journey becomes the active journey
        narrative_map.active_journey_id = entity.id
        self.project_service.set_modified(True)

        logger.info("Journey created and activated: %s", entity.to_dict())
        return {
            'success': True,
            'entity': entity,
            'entity_id': entity_id
        }
