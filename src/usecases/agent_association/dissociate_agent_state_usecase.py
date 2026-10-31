# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : dissociate_agent_state_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for dissociating an agent from a state (FN030, SU008).

Removes the agent-state association from the current narrative map.
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Agent, State
from core.services.project_service import ProjectService
from usecases.agent_association.associate_agent_state_usecase import (
    AssociateAgentStateUseCase
)

logger = logging.getLogger(__name__)


class DissociateAgentStateUseCase:
    """Use Case for dissociating an agent from a state of the current map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent: Agent, state: State) -> Optional[Dict]:
        """Dissociate an agent from a state.

        Args:
            agent: The Agent entity (carried by the project)
            state: The State entity of the current narrative map

        Returns:
            Dictionary with 'success' and 'association' (the removed
            association).
            Or None if the dissociation failed (no project, invalid
            entities, or no existing association between them).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        project = self.project_service.current_project
        if not isinstance(agent, Agent) or agent not in project.agent:
            logger.warning("Invalid agent for dissociation: %s", agent)
            return None

        narrative_map = project.narrative_map[0]
        if not isinstance(state, State) or state not in narrative_map.state:
            logger.warning("Invalid state for dissociation: %s", state)
            return None

        existing = AssociateAgentStateUseCase.find_association(
            narrative_map, agent.id, state.id)
        if existing is None:
            logger.warning("No association between agent %s and state %s",
                           agent.id, state.id)
            return None

        narrative_map.state_agent_rel = [
            rel for rel in narrative_map.state_agent_rel
            if rel is not existing
        ]
        # RG066 revised: drop the journey nodes referencing the removed association
        narrative_map.journey_node = [
            node for node in narrative_map.journey_node
            if node.state_agent_rel_id != existing.id
        ]
        self.project_service.set_modified(True)

        logger.info("Agent %s dissociated from state %s", agent.id, state.id)
        return {
            'success': True,
            'association': existing
        }
