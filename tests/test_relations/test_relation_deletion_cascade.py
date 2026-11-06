# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_relation_deletion_cascade.py
# Content      : Unit tests for the relation deletion cascade (TSK35, RG056 extended, RG069)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""TSK35: deleting a relation (arc or agent-state association) must remove
every Journey_node referencing it and recompute the journey sequence;
loading a project prunes orphan journey nodes (files saved by older
versions, e.g. testCase01 with a node referencing a deleted arc)."""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State, Event, Journey_node
from core.models.view_model import RelationType
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase


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


class TestDeleteRelationCascade:
    def test_delete_arc_removes_journey_nodes_and_recomputes(self, narrative_map):
        """RG056 extended: deleting an arc removes the Journey_node(s)
        referencing it; RG069: the sequence is recomputed."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)
        e2 = add_event(narrative_map, 2)
        arc1 = ArcService.create_arc(narrative_map, s1, e1)  # State_to_event
        arc2 = ArcService.create_arc(narrative_map, e1, s2)  # Event_to_state
        arc3 = ArcService.create_arc(narrative_map, s2, e2)  # State_to_event
        assert len(narrative_map.journey_node) == 3
        assert ArcService.delete_relation(
            narrative_map, RelationType.STATE_TO_EVENT, arc3.id)
        assert arc3 not in narrative_map.state_to_event
        assert all(n.state_to_event_id != arc3.id for n in narrative_map.journey_node)
        assert len(narrative_map.journey_node) == 2
        assert all(n.sequence_order <= 2 for n in narrative_map.journey_node)

    def test_delete_association_removes_journey_node(self, project_service, narrative_map):
        """RG056 extended applies to agent-state associations too."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        agent = CreateAgentUseCase(project_service).execute(
            lb="A1", typ="Subject", note=None, content=None)['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(
            agent=agent, state=s1)['association']
        assert any(n.state_agent_rel_id == rel.id for n in narrative_map.journey_node)
        assert ArcService.delete_relation(
            narrative_map, RelationType.STATE_AGENT_REL, rel.id)
        assert rel not in narrative_map.state_agent_rel
        assert all(n.state_agent_rel_id != rel.id for n in narrative_map.journey_node)

    def test_delete_relation_unknown_type_returns_false(self, narrative_map):
        assert ArcService.delete_relation(narrative_map, "bogus", 1) is False

    def test_prune_orphan_journey_nodes(self, narrative_map):
        """A Journey_node referencing a deleted arc (testCase01 node#22)
        is pruned; valid nodes are kept."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        narrative_map.journey_node.append(Journey_node(
            id=narrative_map.get_next_id('journey_node'),
            journey_id=narrative_map.journey[0].id,
            sequence_order=99, state_to_event_id=999))
        assert ArcService.prune_orphan_journey_nodes(narrative_map) == 1
        assert all(n.state_to_event_id != 999 for n in narrative_map.journey_node)
        assert any(n.state_to_event_id == arc.id for n in narrative_map.journey_node)

    def test_load_project_prunes_orphan_nodes(self, project_service, narrative_map, tmp_path):
        """Loading a project saved by an older version prunes orphan journey
        nodes (TSK35) before recomputing the sequence (RG069)."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        ArcService.create_arc(narrative_map, s1, e1)
        narrative_map.journey_node.append(Journey_node(
            id=narrative_map.get_next_id('journey_node'),
            journey_id=narrative_map.journey[0].id,
            sequence_order=99, state_to_event_id=999))
        path = tmp_path / "proj.json"
        assert project_service.save_project(str(path))
        service2 = ProjectService()
        assert service2.load_project(str(path))
        nm2 = service2.current_project.narrative_map[0]
        assert all(n.state_to_event_id != 999 for n in nm2.journey_node)
        assert len(nm2.journey_node) == 1
