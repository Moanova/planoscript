# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : activate_journey_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK22 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for activating a journey of the narrative map (FN026).

The active journey is the one new relations are attached to (RG052
revised, docs/conception/journey_attachment.md).
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Journey
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ActivateJourneyUseCase:
    """Use Case for setting the active journey of the current narrative map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey) -> Optional[Dict]:
        """Activate a journey (FN026).

        Args:
            journey: The Journey entity to activate (must belong to the
                current narrative map)

        Returns:
            Dictionary with 'success' and 'entity'
            Or None if the activation failed (no project, invalid journey).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        narrative_map = self.project_service.current_project.narrative_map[0]
        if not isinstance(journey, Journey) or journey not in narrative_map.journey:
            logger.warning("Invalid journey for activation: %s", journey)
            return None

        narrative_map.active_journey_id = journey.id
        self.project_service.set_modified(True)

        logger.info("Journey %s activated", journey.id)
        return {
            'success': True,
            'entity': journey
        }
