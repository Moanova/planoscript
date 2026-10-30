# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : delete_journey_usecase.py
# Version      : 1
# Date         : 10-30-2026
# Conception   : TSK25 / docs/conception/journey_attachment.md
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""Use Case for deleting a journey of the narrative map (FN027).

RG018/RG015: the last journey of the map cannot be deleted.
RG036: the journey nodes of the deleted journey are processed - removed
when the referenced relation remains attached to another journey,
switched to the default journey otherwise (RG066 for agent-state
associations, RG026 1..n for arcs: a relation is never left orphan).
RG055: if the deleted journey was the default, the oldest remaining
journey becomes the new default. If it was the active journey, the
default journey becomes the active one (FN027 revised 10-30-2026).
Relations and components are never deleted by a journey deletion.
"""
import logging
from typing import Optional, Dict, List

from core.models.data_model import Journey, Journey_node, NarrativeMap
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class DeleteJourneyUseCase:
    """Use Case for deleting a journey of the current narrative map."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey,
                narrative_map: Optional[NarrativeMap] = None) -> Optional[Dict]:
        """Delete a journey and process its journey nodes (FN027).

        Args:
            journey: The Journey entity to delete
            narrative_map: Target NarrativeMap (optional, uses the first)

        Returns:
            Dictionary with 'success', 'entity_id', 'removed_nodes',
            'switched_nodes', 'new_default'.
            {'success': False, 'reason': 'last_journey'} when the journey
            is the last one of the map (RG018) - nothing is modified.
            Or None if the deletion failed (no project / invalid journey).
        """
        if narrative_map is None:
            if not self.project_service or not self.project_service.current_project:
                logger.warning("No project opened")
                return None
            narrative_map = self.project_service.current_project.narrative_map[0]

        if not isinstance(journey, Journey) or journey not in narrative_map.journey:
            logger.warning("Invalid journey for deletion: %s", journey)
            return None

        # RG018/RG015: the last journey of the map cannot be deleted
        if len(narrative_map.journey) <= 1:
            logger.warning("Cannot delete the last journey of the map (RG018): %s",
                           journey.id)
            return {'success': False, 'reason': 'last_journey',
                    'entity_id': journey.id}

        # RG055: unique default journey; if the deleted one is the default,
        # the oldest remaining journey becomes the new default
        if journey.default:
            remaining = [j for j in narrative_map.journey if j.id != journey.id]
            new_default = min(remaining, key=lambda j: j.id)
            new_default.default = True
        else:
            new_default = next((j for j in narrative_map.journey if j.default), None)
            if new_default is None:  # safety net (RG029: a default always exists)
                new_default = min(narrative_map.journey, key=lambda j: j.id)

        # RG036/RG066/RG026: process the nodes of the deleted journey
        removed_nodes: List[Journey_node] = []
        switched_nodes: List[Journey_node] = []
        for node in [n for n in narrative_map.journey_node
                     if n.journey_id == journey.id]:
            if self._relation_has_other_node(narrative_map, node, journey.id):
                narrative_map.journey_node.remove(node)
                removed_nodes.append(node)
            else:
                # orphan node: switch it to the default journey so the
                # relation keeps 1..n journeys (RG026/RG066)
                node.journey_id = new_default.id
                switched_nodes.append(node)

        narrative_map.journey.remove(journey)

        # FN027 (revised 10-30-2026): if the deleted journey was active,
        # the default journey becomes the active one
        if narrative_map.active_journey_id == journey.id:
            narrative_map.active_journey_id = new_default.id

        self.project_service.set_modified(True)

        logger.info("Journey deleted: %s (removed nodes: %d, switched to default %s: %d)",
                    journey.id, len(removed_nodes), new_default.id, len(switched_nodes))
        return {
            'success': True,
            'entity_id': journey.id,
            'removed_nodes': removed_nodes,
            'switched_nodes': switched_nodes,
            'new_default': new_default if journey.default else None,
        }

    @staticmethod
    def _relation_has_other_node(narrative_map: NarrativeMap,
                                 node: Journey_node,
                                 deleted_journey_id: int) -> bool:
        """Return True if the relation referenced by the node is also
        referenced by a node of another (remaining) journey."""
        for other in narrative_map.journey_node:
            if other is node or other.journey_id == deleted_journey_id:
                continue
            if node.state_to_event_id is not None \
                    and other.state_to_event_id == node.state_to_event_id:
                return True
            if node.event_to_state_id is not None \
                    and other.event_to_state_id == node.event_to_state_id:
                return True
            if node.state_agent_rel_id is not None \
                    and other.state_agent_rel_id == node.state_agent_rel_id:
                return True
        return False
