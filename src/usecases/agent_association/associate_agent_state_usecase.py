# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : associate_agent_state_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for associating an agent with a state (FN030, RG063).

Creates the agent-state association in the current narrative map.
The association is non-directional and carries an optional note
(not editable in the MVP, SU008).
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Agent, State
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class AssociateAgentStateUseCase:
    """Use Case for associating an agent with a state of the current map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent: Agent, state: State) -> Optional[Dict]:
        """Associate an agent with a state (RG063: unique association).

        Args:
            agent: The Agent entity (carried by the project)
            state: The State entity of the current narrative map

        Returns:
            Dictionary with 'success', 'relation' and
            'already_associated' (True when the association already
            existed and creation was skipped, RG063).
            Or None if the association failed (no project, invalid
            entities, entities not belonging to the current project/map).
        """
        narrative_map = self._validate(agent, state)
        if narrative_map is None:
            return None

        # RG063: a single association may exist between a given agent
        # and a given state; a duplicate request is ignored silently
        # (idempotent) and reported via 'already_associated'
        existing = self.find_association(narrative_map, agent.id, state.id)
        if existing is not None:
            logger.info("Association already exists (RG063): agent %s / state %s",
                        agent.id, state.id)
            return {
                'success': True,
                'relation': existing,
                'already_associated': True
            }

        from core.models.data_model import State_agent_rel
        from core.services.arc_service import ArcService
        relation = State_agent_rel(
            id=narrative_map.get_next_id('state_agent_rel'),
            state_id=state.id,
            agent_id=agent.id
        )
        narrative_map.state_agent_rel.append(relation)
        # RG066 revised: the association is attached to the active journey
        ArcService.attach_to_active_journey(narrative_map, relation)
        self.project_service.set_modified(True)

        logger.info("Agent %s associated with state %s", agent.id, state.id)
        return {
            'success': True,
            'relation': relation,
            'already_associated': False
        }

    @staticmethod
    def find_association(narrative_map, agent_id: int, state_id: int):
        """Return the State_agent_rel between an agent and a state, or None."""
        for rel in narrative_map.state_agent_rel:
            if rel.agent_id == agent_id and rel.state_id == state_id:
                return rel
        return None

    def _validate(self, agent, state) -> Optional:
        """Validate the project, the agent and the state.

        Returns the current narrative map, or None on failure.
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        project = self.project_service.current_project
        if not isinstance(agent, Agent) or agent not in project.agent:
            logger.warning("Invalid agent for association: %s", agent)
            return None

        narrative_map = project.narrative_map[0]
        if not isinstance(state, State) or state not in narrative_map.state:
            logger.warning("Invalid state for association: %s", state)
            return None

        return narrative_map
