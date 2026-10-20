# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_agent_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for creating an agent of the project (FN031).

The agent is an entity carried by the project (not by a narrative map),
with a project-unique integer ID, a label, a type ("Subject" or "Object")
and an optional note (SU008).
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Agent
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class CreateAgentUseCase:
    """Use Case for creating a new agent in the current project."""

    AGENT_TYPES = ["Subject", "Object"]

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, lb: Optional[str] = None,
                typ: str = "Subject",
                note: Optional[str] = None) -> Optional[Dict]:
        """Create an agent and add it to the current project.

        Args:
            lb: Label of the agent (defaults to "Agent {id}")
            typ: Type of the agent ("Subject" or "Object")
            note: Optional note of the agent

        Returns:
            Dictionary with 'success', 'entity', 'entity_id'
            Or None if the creation failed (no project, invalid type).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        project = self.project_service.current_project

        if typ not in self.AGENT_TYPES:
            logger.warning("Agent creation refused: invalid Agent.typ %s", typ)
            return None

        entity_id = project.get_next_id('agent')
        entity = Agent(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip()
                else f"Agent {entity_id}"),
            typ=typ,
            note=(note if note and note.strip() else None)
        )
        project.agent.append(entity)
        self.project_service.set_modified(True)

        logger.info("Agent created: %s", entity.to_dict())
        return {
            'success': True,
            'entity': entity,
            'entity_id': entity_id
        }
