# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : delete_agent_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for deleting an agent of the project (FN031, RG064).

Deletes the agent from the project and cascades the deletion to all
agent-state associations referencing its ID (RG064). The confirmation
is a UI responsibility: this use case executes without confirming.
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Agent
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class DeleteAgentUseCase:
    """Use Case for deleting an existing agent of the project."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, entity: Agent) -> Optional[Dict]:
        """Delete an agent and cascade to its associations (RG064).

        Args:
            entity: The Agent entity to delete

        Returns:
            Dictionary with 'success', 'entity_id' and
            'deleted_associations' (number of agent-state associations
            removed by the cascade).
            Or None if the deletion failed (invalid entity, no project,
            agent not in the project).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        if not isinstance(entity, Agent):
            logger.warning("Entity is not an Agent: %s", type(entity))
            return None

        project = self.project_service.current_project
        if entity not in project.agent:
            logger.warning("Agent %s not found in the project", entity.id)
            return None

        # RG064: cascade the deletion to all agent-state associations
        # referencing the agent ID, across all narrative maps
        deleted_associations = 0
        for narrative_map in project.narrative_map:
            remaining = []
            for rel in narrative_map.state_agent_rel:
                if rel.agent_id == entity.id:
                    deleted_associations += 1
                else:
                    remaining.append(rel)
            narrative_map.state_agent_rel = remaining

        project.agent = [a for a in project.agent if a is not entity]
        self.project_service.set_modified(True)

        logger.info("Agent %s deleted (%d association(s) removed)",
                    entity.id, deleted_associations)
        return {
            'success': True,
            'entity_id': entity.id,
            'deleted_associations': deleted_associations
        }
