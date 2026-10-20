# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : update_agent_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for updating the editable attributes of a project agent (FN031).

Editable attributes of an agent: lb, typ, note (SU008).
"""
import logging
from datetime import datetime
from typing import Optional, Dict

from core.models.data_model import Agent
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class UpdateAgentUseCase:
    """Use Case for updating an existing agent of the project."""

    AGENT_TYPES = ["Subject", "Object"]

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, entity: Agent, lb: str,
                typ: Optional[str] = None,
                note: Optional[str] = None) -> Optional[Dict]:
        """Update the data of an agent.

        Args:
            entity: The Agent entity to update
            lb: New label value
            typ: New type value ("Subject" or "Object"; None keeps current)
            note: New note value (None keeps the current value)

        Returns:
            Dictionary with 'success', 'entity', 'entity_id'
            Or None if the update failed (invalid entity, empty label,
            invalid type, no project).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        if not isinstance(entity, Agent):
            logger.warning("Entity is not an Agent: %s", type(entity))
            return None

        new_lb = lb.strip() if isinstance(lb, str) else ""
        if not new_lb:
            logger.warning("Agent update refused: empty label for Agent %s",
                           entity.id)
            return None

        new_typ = typ if typ is not None else entity.typ
        if new_typ not in self.AGENT_TYPES:
            logger.warning("Agent update refused: invalid Agent.typ %s", typ)
            return None

        entity.lb = new_lb
        entity.typ = new_typ
        if note is not None:
            entity.note = note if note.strip() else None
        entity.modification_date_time = datetime.now()
        self.project_service.set_modified(True)

        logger.info("Agent updated: %s", entity.to_dict())
        return {
            'success': True,
            'entity': entity,
            'entity_id': entity.id
        }
