# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_sequence_order.py
# Content      : Unit tests for TSK32 (RG069): real sequence order of Journey_node
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the real sequence order of journey nodes (TSK32, RG069).

Covers:
- linear chain: arcs ranked 1..n in journey order (DFS from the initial state)
- branch: deterministic order by ascending arc id
- arc shared by several journeys: ranks computed independently per journey
- long cycle (allowed: RG058 only forbids cycles of length 2): terminates,
  visited components are memoized
- association node: takes the rank of its attached state (1 for the initial)
- unreachable nodes (incoherent map): ranked afterwards, ascending relation id
- recompute at every graph change point: create_arc, delete_related_arcs,
  attach/detach, dissociation, agent deletion, journey deletion (switched
  nodes), journey duplication
- load: legacy sequence_order values recomputed at load; round-trip preserves
  ranks; recompute is idempotent
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import (
    NarrativeMap, State, Event,
)
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from core.services.journey_sequence_service import JourneySequenceService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.delete_agent_usecase import DeleteAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from usecases.journey_management import (
    CreateJourneyUseCase, AttachRelationToJourneyUseCase,
    DetachRelationFromJourneyUseCase, DeleteJourneyUseCase, DuplicateJourneyUseCase,
)


@pytest.fixture
def project_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


@pytest.fixture
def narrative_map(project_service):
    return project_service.current_project.narrative_map[0]


def add_state(nm, state_id, typ="Action"):
    state = State(id=state_id, lb=f"State {state_id}", typ=typ)
    nm.state.append(state)
    return state


def add_event(nm, event_id):
    event = Event(id=event_id, lb=f"Event {event_id}")
    nm.event.append(event)
    return event


def node_for_stes(nm, arc_id, journey_id=None):
    return next((n for n in nm.journey_node
                 if n.state_to_event_id == arc_id
                 and (journey_id is None or n.journey_id == journey_id)), None)


def node_for_e2s(nm, arc_id, journey_id=None):
    return next((n for n in nm.journey_node
                 if n.event_to_state_id == arc_id
                 and (journey_id is None or n.journey_id == journey_id)), None)


def node_for_rel(nm, rel_id, journey_id=None):
    return next((n for n in nm.journey_node
                 if n.state_agent_rel_id == rel_id
                 and (journey_id is None or n.journey_id == journey_id)), None)


def build_chain(nm, n_steps):
    """Initial state -> E1 -> S2 -> E2 -> ... ; returns the arc lists."""
    s = nm.state[0]  # initial state created with the project (RG031)
    stes, e2s = [], []
    for i in range(1, n_steps + 1):
        e = add_event(nm, i)
        stes.append(ArcService.create_arc(nm, s, e))
        s_new = add_state(nm, i + 1, typ="Final" if i == n_steps else "Action")
        e2s.append(ArcService.create_arc(nm, e, s_new))
        s = s_new
    return stes, e2s


# ---------------------------------------------------------------------
# RG069: linear chain, branch, shared arc, long cycle
# ---------------------------------------------------------------------

class TestDfsRanks:
    def test_linear_chain_ranks(self, narrative_map):
        """DFS from the initial state ranks the arcs 1..n in journey order."""
        stes, e2s = build_chain(narrative_map, 2)
        assert node_for_stes(narrative_map, stes[0].id).sequence_order == 1
        assert node_for_e2s(narrative_map, e2s[0].id).sequence_order == 2
        assert node_for_stes(narrative_map, stes[1].id).sequence_order == 3
        assert node_for_e2s(narrative_map, e2s[1].id).sequence_order == 4

    def test_branch_ordered_by_ascending_arc_id(self, narrative_map):
        """At a branch, branches are explored in ascending arc id order."""
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)
        e2 = add_event(narrative_map, 2)
        s3 = add_state(narrative_map, 3)
        a1 = ArcService.create_arc(narrative_map, s1, e1)  # stes id 1
        a2 = ArcService.create_arc(narrative_map, e1, s2)  # e2s id 1
        a3 = ArcService.create_arc(narrative_map, s1, e2)  # stes id 2 (second branch)
        a4 = ArcService.create_arc(narrative_map, e2, s3)  # e2s id 2
        assert node_for_stes(narrative_map, a1.id).sequence_order == 1
        assert node_for_e2s(narrative_map, a2.id).sequence_order == 2
        assert node_for_stes(narrative_map, a3.id).sequence_order == 3
        assert node_for_e2s(narrative_map, a4.id).sequence_order == 4

    def test_shared_arc_ranks_independent_per_journey(self, project_service, narrative_map):
        """An arc shared by 1..n journeys (RG026) is ranked within each journey."""
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)
        s3 = add_state(narrative_map, 3)
        default = narrative_map.journey[0]
        a1 = ArcService.create_arc(narrative_map, s1, e1)  # default journey
        a2 = ArcService.create_arc(narrative_map, e1, s2)  # default journey
        j2 = CreateJourneyUseCase(project_service).execute()['entity']  # becomes active
        a3 = ArcService.create_arc(narrative_map, e1, s3)  # attached to j2
        AttachRelationToJourneyUseCase(project_service).execute(a1, j2)
        assert node_for_stes(narrative_map, a1.id, journey_id=default.id).sequence_order == 1
        assert node_for_e2s(narrative_map, a2.id, journey_id=default.id).sequence_order == 2
        assert node_for_stes(narrative_map, a1.id, journey_id=j2.id).sequence_order == 1
        assert node_for_e2s(narrative_map, a3.id, journey_id=j2.id).sequence_order == 2

    def test_long_cycle_terminates(self, narrative_map):
        """RG058 only forbids cycles of length 2; a longer cycle must not loop."""
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)
        e2 = add_event(narrative_map, 2)
        a1 = ArcService.create_arc(narrative_map, s1, e1)
        a2 = ArcService.create_arc(narrative_map, e1, s2)
        a3 = ArcService.create_arc(narrative_map, s2, e2)
        a4 = ArcService.create_arc(narrative_map, e2, s1)  # closes a cycle of length 4
        assert node_for_stes(narrative_map, a1.id).sequence_order == 1
        assert node_for_e2s(narrative_map, a2.id).sequence_order == 2
        assert node_for_stes(narrative_map, a3.id).sequence_order == 3
        assert node_for_e2s(narrative_map, a4.id).sequence_order == 4
        # each node ranked exactly once (s1 reached again -> memoized)
        assert sorted(n.sequence_order for n in narrative_map.journey_node) == [1, 2, 3, 4]


# ---------------------------------------------------------------------
# RG069: association nodes and unreachable fallback
# ---------------------------------------------------------------------

class TestAssociationAndFallback:
    def test_association_takes_its_state_rank(self, project_service, narrative_map):
        """A node carrying an association takes the rank of its attached state."""
        stes, e2s = build_chain(narrative_map, 1)  # s1 -> e1 (1) -> s2 (2)
        s2 = narrative_map.state[-1]
        agent = CreateAgentUseCase(project_service).execute()['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(agent, s2)['association']
        assert node_for_rel(narrative_map, rel.id).sequence_order == 2  # rank of s2

    def test_association_on_initial_state_has_rank_1(self, project_service, narrative_map):
        s1 = narrative_map.state[0]
        agent = CreateAgentUseCase(project_service).execute()['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(agent, s1)['association']
        assert node_for_rel(narrative_map, rel.id).sequence_order == 1

    def test_unreachable_nodes_ranked_afterwards_by_ascending_id(self, narrative_map):
        """Nodes unreachable from the initial state get ranks after the others."""
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        a1 = ArcService.create_arc(narrative_map, s1, e1)  # reachable -> rank 1
        # isolated chain, attached to the journey but not connected to s1
        s9 = add_state(narrative_map, 9)
        e9 = add_event(narrative_map, 9)
        s10 = add_state(narrative_map, 10)
        a9 = ArcService.create_arc(narrative_map, s9, e9)   # stes id 2
        a10 = ArcService.create_arc(narrative_map, e9, s10)  # e2s id 1
        assert node_for_stes(narrative_map, a1.id).sequence_order == 1
        assert node_for_stes(narrative_map, a9.id).sequence_order == 2  # stes before e2s
        assert node_for_e2s(narrative_map, a10.id).sequence_order == 3

    def test_empty_map_does_not_crash(self):
        nm = NarrativeMap(id="t", lb="t")
        JourneySequenceService.recompute_all(nm)
        assert nm.journey_node == []

    def test_recompute_is_idempotent(self, narrative_map):
        build_chain(narrative_map, 2)
        before = {n.id: n.sequence_order for n in narrative_map.journey_node}
        JourneySequenceService.recompute_all(narrative_map)
        after = {n.id: n.sequence_order for n in narrative_map.journey_node}
        assert before == after


# ---------------------------------------------------------------------
# RG069: recompute at every graph change point
# ---------------------------------------------------------------------

class TestRecomputeAtChangePoints:
    def test_delete_related_arcs_reranks(self, narrative_map):
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)
        e2 = add_event(narrative_map, 2)
        s3 = add_state(narrative_map, 3)
        a1 = ArcService.create_arc(narrative_map, s1, e1)
        ArcService.create_arc(narrative_map, e1, s2)
        ArcService.create_arc(narrative_map, s2, e2)
        a4 = ArcService.create_arc(narrative_map, e2, s3)
        ArcService.delete_related_arcs(narrative_map, s2.id, "State")
        assert node_for_stes(narrative_map, a1.id).sequence_order == 1
        # a4 is now unreachable from the initial state -> fallback rank
        assert node_for_e2s(narrative_map, a4.id).sequence_order == 2

    def test_detach_reranks(self, project_service, narrative_map):
        stes, e2s = build_chain(narrative_map, 2)
        journey = narrative_map.journey[0]
        DetachRelationFromJourneyUseCase(project_service).execute(e2s[0], journey)
        assert node_for_e2s(narrative_map, e2s[0].id) is None
        assert node_for_stes(narrative_map, stes[0].id).sequence_order == 1
        # stes[1] is now unreachable from the initial state -> fallback rank
        assert node_for_stes(narrative_map, stes[1].id).sequence_order == 2

    def test_attach_to_second_journey_reranks_target(self, project_service, narrative_map):
        stes, e2s = build_chain(narrative_map, 1)
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        AttachRelationToJourneyUseCase(project_service).execute(stes[0], j2)
        AttachRelationToJourneyUseCase(project_service).execute(e2s[0], j2)
        assert node_for_stes(narrative_map, stes[0].id, journey_id=j2.id).sequence_order == 1
        assert node_for_e2s(narrative_map, e2s[0].id, journey_id=j2.id).sequence_order == 2
        # the source journey is unchanged
        assert node_for_stes(narrative_map, stes[0].id, journey_id=default.id).sequence_order == 1
        assert node_for_e2s(narrative_map, e2s[0].id, journey_id=default.id).sequence_order == 2

    def test_dissociation_reranks(self, project_service, narrative_map):
        stes, e2s = build_chain(narrative_map, 1)
        s2 = narrative_map.state[-1]
        agent = CreateAgentUseCase(project_service).execute()['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(agent, s2)['association']
        DissociateAgentStateUseCase(project_service).execute(agent, s2)
        assert node_for_rel(narrative_map, rel.id) is None
        assert node_for_stes(narrative_map, stes[0].id).sequence_order == 1
        assert node_for_e2s(narrative_map, e2s[0].id).sequence_order == 2

    def test_agent_deletion_reranks(self, project_service, narrative_map):
        build_chain(narrative_map, 1)
        agent = CreateAgentUseCase(project_service).execute()['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(
            agent, narrative_map.state[0])['association']
        DeleteAgentUseCase(project_service).execute(agent)
        assert node_for_rel(narrative_map, rel.id) is None
        assert sorted(n.sequence_order for n in narrative_map.journey_node) == [1, 2]

    def test_duplicate_journey_keeps_ranks(self, project_service, narrative_map):
        build_chain(narrative_map, 2)
        source = narrative_map.journey[0]
        copy = DuplicateJourneyUseCase(project_service).execute(source)['entity']
        for src_node in [n for n in narrative_map.journey_node if n.journey_id == source.id]:
            copy_node = next(n for n in narrative_map.journey_node
                             if n.journey_id == copy.id
                             and n.state_to_event_id == src_node.state_to_event_id
                             and n.event_to_state_id == src_node.event_to_state_id
                             and n.state_agent_rel_id == src_node.state_agent_rel_id)
            assert copy_node.sequence_order == src_node.sequence_order

    def test_delete_journey_switch_reranks(self, project_service, narrative_map):
        """Nodes switched to the default journey (TSK25) are re-ranked (RG069)."""
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)
        a1 = ArcService.create_arc(narrative_map, s1, e1)  # default journey
        a2 = ArcService.create_arc(narrative_map, e1, s2)  # default journey
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        e9 = add_event(narrative_map, 9)
        a9 = ArcService.create_arc(narrative_map, s1, e9)  # attached to j2 (active)
        assert node_for_stes(narrative_map, a9.id, journey_id=j2.id).sequence_order == 1
        DeleteJourneyUseCase(project_service).execute(j2)
        switched = node_for_stes(narrative_map, a9.id, journey_id=default.id)
        assert switched is not None
        # default journey now holds a1, a2, a9: DFS from s1, branches by arc id
        assert node_for_stes(narrative_map, a1.id).sequence_order == 1
        assert node_for_e2s(narrative_map, a2.id).sequence_order == 2
        assert switched.sequence_order == 3


# ---------------------------------------------------------------------
# RG069: persistence — recompute legacy values at load, round-trip
# ---------------------------------------------------------------------

class TestPersistence:
    def test_load_recomputes_legacy_values(self, project_service, narrative_map, tmp_path):
        """Legacy sequence_order values are recomputed when the project loads."""
        stes, e2s = build_chain(narrative_map, 2)
        path = str(tmp_path / "project.json")
        assert project_service.save_project(path)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for node in data['narrative_map'][0]['journey_node']:
            node['sequence_order'] = 999
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

        service2 = ProjectService()
        assert service2.load_project(path)
        nm2 = service2.current_project.narrative_map[0]
        assert node_for_stes(nm2, stes[0].id).sequence_order == 1
        assert node_for_e2s(nm2, e2s[0].id).sequence_order == 2
        assert node_for_stes(nm2, stes[1].id).sequence_order == 3
        assert node_for_e2s(nm2, e2s[1].id).sequence_order == 4
        assert service2.is_modified is False  # load does not mark the project modified

    def test_round_trip_preserves_ranks(self, project_service, narrative_map, tmp_path):
        build_chain(narrative_map, 2)
        before = {n.id: n.sequence_order for n in narrative_map.journey_node}
        path = str(tmp_path / "project.json")
        assert project_service.save_project(path)
        service2 = ProjectService()
        assert service2.load_project(path)
        nm2 = service2.current_project.narrative_map[0]
        after = {n.id: n.sequence_order for n in nm2.journey_node}
        assert before == after
