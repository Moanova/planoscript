# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_filter_service.py
# Version      : 1
# Date         : 01-11-2026
# Content      : Journey display filter visibility (FN029, RG026, RG042)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Service computing the derived visibility of a narrative map under the
journey display filter (FN029, RG042).

The visibility is derived from the model (RG026 revised), never stored:
- filter active (active journey J): visible relations are the arcs
  (State_to_event / Event_to_state) referenced by at least one
  Journey_node of J, plus the agent-state associations (State_agent_rel)
  of J whose state is itself visible; visible components (State/Event)
  get their membership from arcs only (an association does not make its
  state belong to the journey). Orphan components (no arc at
  all) and relations of other journeys are hidden.
- filter disabled ("All journeys"): everything is visible.

The filter is a purely visual state (RG041): it is not persisted and
does not mark the map as modified.
"""

from typing import Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.data_model import NarrativeMap, Journey


class JourneyFilterService:
    """Derived visibility sets for the journey display filter (FN029)."""

    @staticmethod
    def visible_relation_keys(
        narrative_map: 'NarrativeMap',
        journey: Optional['Journey'],
        filter_active: bool
    ) -> Optional[Set[Tuple[str, int]]]:
        """Return the keys of the visible relations, or None when no
        filter is applied (everything visible).

        Keys are (relation_list_name, relation_id) tuples:
        ('state_to_event', id), ('event_to_state', id),
        ('state_agent_rel', id).

        RG026 revised: an agent-state association is visible only when its
        state belongs to the journey (membership derives from arcs only),
        so it never pulls a foreign component into the filtered view.

        Args:
            narrative_map: The narrative map to inspect
            journey: The journey the filter applies to (active journey)
            filter_active: False means "All journeys" -> no filtering

        Returns:
            None when the filter is disabled; otherwise the set of
            visible relation keys under the given journey.
        """
        if not filter_active or journey is None:
            return None
        keys: Set[Tuple[str, int]] = set()
        for node in narrative_map.journey_node:
            if node.journey_id != journey.id:
                continue
            if node.state_to_event_id is not None:
                keys.add(('state_to_event', node.state_to_event_id))
            if node.event_to_state_id is not None:
                keys.add(('event_to_state', node.event_to_state_id))
            if node.state_agent_rel_id is not None:
                keys.add(('state_agent_rel', node.state_agent_rel_id))
        state_ids, _ = JourneyFilterService._arc_component_ids(
            narrative_map, keys)
        rels = {r.id: r for r in narrative_map.state_agent_rel}
        return {key for key in keys
                if key[0] != 'state_agent_rel'
                or (key[1] in rels and rels[key[1]].state_id in state_ids)}

    @staticmethod
    def _arc_component_ids(
        narrative_map: 'NarrativeMap',
        relation_keys: Set[Tuple[str, int]]
    ) -> Tuple[Set[int], Set[int]]:
        """(state_ids, event_ids) of the components whose arc is in
        relation_keys. Dangling arc references (deleted arc) are ignored."""
        stes = {a.id: a for a in narrative_map.state_to_event}
        e2s = {a.id: a for a in narrative_map.event_to_state}
        state_ids: Set[int] = set()
        event_ids: Set[int] = set()
        for kind, rid in relation_keys:
            if kind == 'state_to_event' and rid in stes:
                state_ids.add(stes[rid].state_id)
                event_ids.add(stes[rid].event_id)
            elif kind == 'event_to_state' and rid in e2s:
                event_ids.add(e2s[rid].event_id)
                state_ids.add(e2s[rid].state_id)
        return state_ids, event_ids

    @staticmethod
    def visible_component_ids(
        narrative_map: 'NarrativeMap',
        journey: Optional['Journey'],
        filter_active: bool
    ) -> Optional[Tuple[Set[int], Set[int]]]:
        """Return the visible (state_ids, event_ids), or None when no
        filter is applied (everything visible).

        Membership is derived from arcs only (RG026 revised): a component
        belongs to the journey iff at least one of its arcs is attached to
        it. Orphan components belong to no journey and are hidden under an
        active filter.
        """
        relation_keys = JourneyFilterService.visible_relation_keys(
            narrative_map, journey, filter_active)
        if relation_keys is None:
            return None
        return JourneyFilterService._arc_component_ids(narrative_map, relation_keys)
