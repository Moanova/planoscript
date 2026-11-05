# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_sequence_service.py
# Version      : 1
# Date         : 01-11-2026
# Content      : Real sequence order of journey nodes (RG069, TSK32)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Service recomputing the real sequence order of journey nodes (RG069, TSK32).

Journey_node.sequence_order materializes the actual position of the
referenced relation in its journey sequence. It is recomputed per journey,
depth-first from the initial state (RG031), following only the arcs
attached to that journey (the arcs referenced by its Journey_node entries):

- each arc visited in journey order gets an increasing rank (1, 2, 3...);
- at a branch, branches are explored in ascending arc id order
  (deterministic);
- long cycles (allowed: RG058 only forbids cycles of length 2) are handled
  by memoizing already visited components;
- a node carrying an agent-state association (state_agent_rel_id) takes the
  rank of the state the association is attached to: the rank of that state's
  incoming arc in the journey, 1 for the initial state;
- nodes unreachable from the initial state (incoherent map, RG031) are
  ranked afterwards, by ascending relation id, from the highest rank + 1.

The recomputation is global (all journeys) at every graph change point:
narrative maps are small and this keeps arcs shared by 1..n journeys
(RG026) consistent. The JSON key sequence_order is kept (retrocompatible):
legacy values are recomputed at load.
"""

from typing import Dict, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.data_model import NarrativeMap, Journey_node


class JourneySequenceService:
    """Recompute Journey_node.sequence_order per journey (RG069)."""

    @staticmethod
    def recompute_all(narrative_map: 'NarrativeMap') -> None:
        """Recompute sequence_order of the nodes of every journey (RG069)."""
        for journey in narrative_map.journey:
            JourneySequenceService.recompute_journey(narrative_map, journey.id)

    @staticmethod
    def recompute_journey(narrative_map: 'NarrativeMap', journey_id: int) -> None:
        """Recompute sequence_order of all the nodes of the given journey (RG069)."""
        nodes: List['Journey_node'] = [
            n for n in narrative_map.journey_node if n.journey_id == journey_id
        ]
        if not nodes:
            return
        for n in nodes:
            n.sequence_order = 0

        # Arcs attached to this journey, per arc type (ids are unique per
        # type only: a State_to_event id must not match an Event_to_state id)
        stes_ids: Set[int] = {n.state_to_event_id for n in nodes
                              if n.state_to_event_id is not None}
        e2s_ids: Set[int] = {n.event_to_state_id for n in nodes
                             if n.event_to_state_id is not None}
        # Outgoing arcs per component, restricted to the journey arcs, ascending id
        out_stes: Dict[int, list] = {}
        for arc in sorted(narrative_map.state_to_event, key=lambda a: a.id):
            if arc.id in stes_ids:
                out_stes.setdefault(arc.state_id, []).append(arc)
        out_e2s: Dict[int, list] = {}
        for arc in sorted(narrative_map.event_to_state, key=lambda a: a.id):
            if arc.id in e2s_ids:
                out_e2s.setdefault(arc.event_id, []).append(arc)

        rel_by_id = {r.id: r for r in narrative_map.state_agent_rel}

        rank = 0
        state_rank: Dict[int, int] = {}
        # Component ids are unique per type only: key visited by (kind, id)
        visited: Set[tuple] = set()

        def assign(arc_id: int, field: str, value: int) -> None:
            for n in nodes:
                if getattr(n, field) == arc_id:
                    n.sequence_order = value

        def visit_event(event_id: int) -> None:
            nonlocal rank
            if ('event', event_id) in visited:
                return
            visited.add(('event', event_id))
            for arc in out_e2s.get(event_id, []):
                rank += 1
                assign(arc.id, 'event_to_state_id', rank)
                state_rank.setdefault(arc.state_id, rank)
                visit_state(arc.state_id)

        def visit_state(state_id: int) -> None:
            nonlocal rank
            if ('state', state_id) in visited:
                return
            visited.add(('state', state_id))
            for arc in out_stes.get(state_id, []):
                rank += 1
                assign(arc.id, 'state_to_event_id', rank)
                visit_event(arc.event_id)

        # RG031: depth-first from the initial state; its rank is 1 by convention
        initial = next((s for s in narrative_map.state if s.typ == "Initial"), None)
        if initial is not None:
            state_rank[initial.id] = 1
            visit_state(initial.id)

        # Association nodes take the rank of the state they are attached to
        for n in nodes:
            if n.state_agent_rel_id is not None:
                rel = rel_by_id.get(n.state_agent_rel_id)
                if rel is not None and rel.state_id in state_rank:
                    n.sequence_order = state_rank[rel.state_id]

        # Fallback (RG069): nodes unreachable from the initial state are ranked
        # afterwards, by ascending relation id (per relation type: ids are
        # unique per type only), continuing from the last rank
        def ref_key(n: 'Journey_node'):
            if n.state_to_event_id is not None:
                return (0, n.state_to_event_id)
            if n.event_to_state_id is not None:
                return (1, n.event_to_state_id)
            if n.state_agent_rel_id is not None:
                return (2, n.state_agent_rel_id)
            return (3, n.id)

        for n in sorted((n for n in nodes if n.sequence_order == 0), key=ref_key):
            rank += 1
            n.sequence_order = rank
