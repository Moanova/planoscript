# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : remove_state_associations_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for cascading agent-state associations on state deletion (RG065).

Removes all agent-state associations referencing a state ID, across all
narrative maps of the project. Called when a state is deleted; the
returned count feeds the information message required by RG065.
"""
import logging
from typing import Optional, Dict

from core.models.data_model import State
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class RemoveStateAssociationsUseCase:
    """Use Case for the RG065 cascade on state deletion."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, state: State) -> Optional[Dict]:
        """Remove all agent-state associations referencing the state.

        Args:
            state: The State entity being deleted

        Returns:
            Dictionary with 'success' and 'deleted_associations'
            (number of associations removed by the cascade).
            Or None if the cascade failed (no project, invalid entity).
        """
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        if not isinstance(state, State):
            logger.warning("Entity is not a State: %s", type(state))
            return None

        project = self.project_service.current_project
        deleted_associations = 0
        for narrative_map in project.narrative_map:
            removed_ids = set()
            remaining = []
            for rel in narrative_map.state_agent_rel:
                if rel.state_id == state.id:
                    deleted_associations += 1
                    removed_ids.add(rel.id)
                else:
                    remaining.append(rel)
            narrative_map.state_agent_rel = remaining
            # RG065 + RG066 revised: drop the journey nodes of removed associations
            if removed_ids:
                narrative_map.journey_node = [
                    node for node in narrative_map.journey_node
                    if node.state_agent_rel_id not in removed_ids
                ]

        if deleted_associations:
            self.project_service.set_modified(True)
            logger.info("State %s deleted: %d agent association(s) removed",
                        state.id, deleted_associations)

        return {
            'success': True,
            'deleted_associations': deleted_associations
        }
