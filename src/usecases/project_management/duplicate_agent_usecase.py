# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : duplicate_agent_usecase.py
# Version      : 1
# Date         : 31-10-2026
# Conception   : TSK28 evolution / SU003, FN016
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for duplicating an agent of the project (FN016, TSK28 evolution).

The agent is a project-level component (SU008): the copy gets a new
project-unique integer id (RG020), a distinct label ("{source.lb} (copy)"
by default) and inherits the editable attributes (typ, note, content).

The agent-state associations of the source are NOT copied (decision TSC
31-10-2026): the copy is a new agent with no association, same principle
as component duplication (relations are not duplicated, RG024).
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Agent, Project
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class DuplicateAgentUseCase:
    """Use Case for duplicating an agent of the current project."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, source: Agent,
                lb: Optional[str] = None,
                project: Optional[Project] = None) -> Optional[Dict]:
        """Duplicate an agent.

        Args:
            source: The Agent entity to duplicate (must belong to the project)
            lb: Label of the copy (defaults to "{source.lb} (copy)")
            project: Target project (optional, uses the current one)

        Returns:
            Dictionary with 'success', 'entity', 'entity_id'
            Or None if the duplication failed (no project, invalid source).
        """
        if project is None:
            if not self.project_service or not self.project_service.current_project:
                logger.warning("No project opened")
                return None
            project = self.project_service.current_project

        if not isinstance(source, Agent) or source not in project.agent:
            logger.warning("Invalid source agent for duplication: %s", source)
            return None

        entity_id = project.get_next_id('agent')
        copy = Agent(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip()
                else f"{source.lb} (copy)"),
            typ=source.typ,
            note=source.note,
            content=source.content
        )
        project.agent.append(copy)
        # No agent-state association is copied: the copy starts unassociated
        self.project_service.set_modified(True)

        logger.info("Agent duplicated: %s (from agent %s)",
                    copy.to_dict(), source.id)
        return {
            'success': True,
            'entity': copy,
            'entity_id': entity_id
        }
