# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : update_journey_usecase.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK22 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for updating a journey of the narrative map (FN024).

Renames the journey and/or edits its note. RG055: designating another
journey as default is handled by setting 'default'.
"""
import logging
from datetime import datetime
from typing import Optional, Dict

from core.models.data_model import Journey
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class UpdateJourneyUseCase:
    """Use Case for updating an existing journey."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey,
                lb: Optional[str] = None,
                note: Optional[str] = None,
                default: Optional[bool] = None) -> Optional[Dict]:
        """Update the label, note and/or default flag of a journey.

        Args:
            journey: The Journey entity to update (must belong to the
                current narrative map)
            lb: New label (None = unchanged)
            note: New note (None = unchanged; empty string clears it)
            default: New default flag (None = unchanged). RG055: at most
                one default journey per map; setting one clears the others.

        Returns:
            Dictionary with 'success' and 'entity'
            Or None if the update failed (no project, invalid journey).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        narrative_map = self.project_service.current_project.narrative_map[0]
        if not isinstance(journey, Journey) or journey not in narrative_map.journey:
            logger.warning("Invalid journey for update: %s", journey)
            return None

        if lb is not None:
            journey.lb = lb.strip() if isinstance(lb, str) else lb
        if note is not None:
            journey.note = note if note.strip() else None
        if default is not None and default:
            # RG055: a single default journey per narrative map
            for j in narrative_map.journey:
                if j is not journey:
                    j.default = False
            journey.default = True
        elif default is not None:
            journey.default = False
        journey.modification_date_time = datetime.now()
        self.project_service.set_modified(True)

        logger.info("Journey updated: %s", journey.to_dict())
        return {
            'success': True,
            'entity': journey
        }
