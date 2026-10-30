# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : duplicate_journey_usecase.py
# Version      : 1
# Date         : 10-30-2026
# Conception   : TSK24 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for duplicating a journey of the narrative map (FN025).

RG020: the copy gets a new unique id. RG023 (revised 10-30-2026): the copy
does NOT become the active journey. RG055: the copy is not the default
journey. The journey nodes of the source journey are copied into the copy
(same referenced arcs/associations, same sequence_order); the relations
themselves are shared, not duplicated (conception journey_attachment.md).
"""
import logging
from typing import Optional, Dict

from core.models.data_model import Journey, Journey_node, NarrativeMap
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class DuplicateJourneyUseCase:
    """Use Case for duplicating a journey of the current narrative map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, source: Journey,
                lb: Optional[str] = None,
                note: Optional[str] = None,
                narrative_map: Optional[NarrativeMap] = None) -> Optional[Dict]:
        """Duplicate a journey and its journey nodes (FN025).

        Args:
            source: The Journey entity to duplicate
            lb: Label of the copy (defaults to "{source.lb} (copy)")
            note: Note of the copy (None = inherit the source note,
                empty string = no note)
            narrative_map: Target NarrativeMap (optional, uses the first)

        Returns:
            Dictionary with 'success', 'entity', 'entity_id', 'copied_nodes'
            Or None if the duplication failed (no project / invalid source).
        """
        if narrative_map is None:
            if not self.project_service or not self.project_service.current_project:
                logger.warning("No project opened")
                return None
            narrative_map = self.project_service.current_project.narrative_map[0]

        if not isinstance(source, Journey) or source not in narrative_map.journey:
            logger.warning("Invalid source journey for duplication: %s", source)
            return None

        entity_id = narrative_map.get_next_id('journey')
        if note is None:
            copy_note = source.note
        elif note.strip():
            copy_note = note
        else:
            copy_note = None
        entity = Journey(
            id=entity_id,
            lb=(lb.strip() if isinstance(lb, str) and lb.strip()
                else f"{source.lb} (copy)"),
            default=False,  # RG055: only one default journey per map
            note=copy_note
        )
        narrative_map.journey.append(entity)

        # FN025: copy the journey nodes of the source journey into the copy
        copied_nodes = []
        for node in [n for n in narrative_map.journey_node
                     if n.journey_id == source.id]:
            copy = Journey_node(
                id=narrative_map.get_next_id('journey_node'),
                journey_id=entity_id,
                sequence_order=node.sequence_order,
                event_to_state_id=node.event_to_state_id,
                state_to_event_id=node.state_to_event_id,
                state_agent_rel_id=node.state_agent_rel_id,
            )
            narrative_map.journey_node.append(copy)
            copied_nodes.append(copy)

        # RG023 (revised 10-30-2026): the copy does not become the active journey
        self.project_service.set_modified(True)

        logger.info("Journey duplicated: %s (from journey %s, %d nodes copied)",
                    entity.to_dict(), source.id, len(copied_nodes))
        return {
            'success': True,
            'entity': entity,
            'entity_id': entity_id,
            'copied_nodes': copied_nodes
        }
