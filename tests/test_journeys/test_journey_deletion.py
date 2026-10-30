# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_journey_deletion.py
# Content      : Unit tests for TSK25 journey deletion (EPC05, FN027, RG018/RG015, RG036, RG055, RG066, RG026, RG029)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the journey deletion (TSK25, FN027).

Covers:
- RG018/RG015: the last journey of the map cannot be deleted (nothing modified)
- RG036: a node whose relation remains attached to another journey is removed
- RG026/RG066: an orphan node (relation no longer attached anywhere else)
  is switched to the default journey - arcs and agent-state associations
  alike; a relation is never left without a journey (1..n)
- RG055: deleting the default journey designates the oldest remaining one
- FN027 revised (10-30-2026): deleting the active journey activates the default
- Components and relations are never deleted by a journey deletion
- Deletion marks the map/project as modified
- Edge cases: foreign journey, no project
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import (
    NarrativeMap, State, Event, Journey,
)
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.journey_management import (
    CreateJourneyUseCase, DeleteJourneyUseCase, AttachRelationToJourneyUseCase,
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


# ---------------------------------------------------------------------
# RG018/RG015: last journey cannot be deleted
# ---------------------------------------------------------------------

class TestLastJourney:
    def test_last_journey_deletion_refused(self, project_service, narrative_map):
        """RG018: deleting the last journey is refused, nothing changes."""
        project_service.set_modified(False)
        only = narrative_map.journey[0]
        result = DeleteJourneyUseCase(project_service).execute(only)
        assert result['success'] is False
        assert result['reason'] == 'last_journey'
        assert narrative_map.journey == [only]
        assert narrative_map.active_journey_id == only.id
        assert project_service.is_modified is False


# ---------------------------------------------------------------------
# RG036: node removed when the relation stays attached elsewhere
# ---------------------------------------------------------------------

class TestSharedRelation:
    def test_node_removed_when_relation_shared(self, project_service, narrative_map):
        """RG036: the arc is attached to both journeys; deleting j2 removes
        only its node, the arc keeps its node in the default journey."""
        default = narrative_map.journey[0]
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)  # attached to default (active)
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        AttachRelationToJourneyUseCase(project_service).execute(arc, j2)
        assert len(narrative_map.journey_node) == 2

        result = DeleteJourneyUseCase(project_service).execute(j2)
        assert result['success'] is True
        assert len(result['removed_nodes']) == 1
        assert result['switched_nodes'] == []
        # the arc itself and its node in the default journey are untouched
        assert len(narrative_map.state_to_event) == 1
        nodes = [n for n in narrative_map.journey_node if n.state_to_event_id == arc.id]
        assert len(nodes) == 1
        assert nodes[0].journey_id == default.id
        assert j2 not in narrative_map.journey


# ---------------------------------------------------------------------
# RG026/RG066: orphan nodes are switched to the default journey
# ---------------------------------------------------------------------

class TestOrphanNodes:
    def test_orphan_arc_node_switched_to_default(self, project_service, narrative_map):
        """RG026: the arc belongs only to j2; deleting j2 switches its node
        to the default journey (the relation keeps 1..n journeys)."""
        default = narrative_map.journey[0]
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        ArcService.create_arc(narrative_map, s1, e1)  # node in default
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        e2 = add_event(narrative_map, 2)
        arc2 = ArcService.create_arc(narrative_map, s1, e2)  # node in j2 only
        assert len(narrative_map.journey_node) == 2

        result = DeleteJourneyUseCase(project_service).execute(j2)
        assert result['success'] is True
        assert result['removed_nodes'] == []
        assert len(result['switched_nodes']) == 1
        node = result['switched_nodes'][0]
        assert node.journey_id == default.id
        assert node.state_to_event_id == arc2.id
        # the arc is still attached (to the default journey now)
        nodes = [n for n in narrative_map.journey_node if n.state_to_event_id == arc2.id]
        assert len(nodes) == 1 and nodes[0].journey_id == default.id
        assert len(narrative_map.state_to_event) == 2  # arcs not deleted

    def test_orphan_association_node_switched_to_default(self, project_service, narrative_map):
        """RG066: an association left orphan by the deletion is switched to
        the default journey (state_agent_rel_id)."""
        default = narrative_map.journey[0]
        agent = CreateAgentUseCase(project_service).execute()['entity']
        s1 = narrative_map.state[0]
        AssociateAgentStateUseCase(project_service).execute(agent, s1)  # node in default
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        s2 = add_state(narrative_map, 2)
        rel = AssociateAgentStateUseCase(project_service).execute(agent, s2)['relation']
        # rel's node is in j2 (active)
        assert any(n.state_agent_rel_id == rel.id and n.journey_id == j2.id
                   for n in narrative_map.journey_node)

        result = DeleteJourneyUseCase(project_service).execute(j2)
        assert result['success'] is True
        nodes = [n for n in narrative_map.journey_node if n.state_agent_rel_id == rel.id]
        assert len(nodes) == 1
        assert nodes[0].journey_id == default.id
        assert len(narrative_map.state_agent_rel) == 2  # associations not deleted


# ---------------------------------------------------------------------
# RG055 / FN027: default and active reassignment
# ---------------------------------------------------------------------

class TestDefaultAndActive:
    def test_deleting_default_designates_oldest_remaining(self, project_service, narrative_map):
        """RG055: deleting the default journey -> the oldest remaining
        journey (lowest id) becomes the new default."""
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        j3 = CreateJourneyUseCase(project_service).execute(lb="J3")['entity']
        assert default.default is True

        result = DeleteJourneyUseCase(project_service).execute(default)
        assert result['success'] is True
        assert result['new_default'] is j2
        assert j2.default is True
        assert j3.default is False
        defaults = [j for j in narrative_map.journey if j.default]
        assert defaults == [j2]
        # active was j3 (last created): unchanged
        assert narrative_map.active_journey_id == j3.id

    def test_deleting_active_activates_default(self, project_service, narrative_map):
        """FN027 revised: deleting the active journey -> the default journey
        becomes the active one."""
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        assert narrative_map.active_journey_id == j2.id

        DeleteJourneyUseCase(project_service).execute(j2)
        assert narrative_map.active_journey_id == default.id

    def test_deleting_neither_default_nor_active_keeps_both(self, project_service, narrative_map):
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        j3 = CreateJourneyUseCase(project_service).execute(lb="J3")['entity']
        # active = j3, default = J1; delete j2
        DeleteJourneyUseCase(project_service).execute(j2)
        assert default.default is True
        assert narrative_map.active_journey_id == j3.id
        assert narrative_map.journey == [default, j3]


# ---------------------------------------------------------------------
# Modification flag, components/relations preserved, edge cases
# ---------------------------------------------------------------------

class TestMisc:
    def test_deletion_marks_modified(self, project_service, narrative_map):
        project_service.set_modified(False)
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        project_service.set_modified(False)
        DeleteJourneyUseCase(project_service).execute(j2)
        assert project_service.is_modified is True

    def test_components_and_relations_preserved(self, project_service, narrative_map):
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1)
        ArcService.create_arc(narrative_map, s1, e1)
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        DeleteJourneyUseCase(project_service).execute(j2)
        assert narrative_map.state and narrative_map.event
        assert len(narrative_map.state_to_event) == 1
        # the orphan arc node was switched, not removed
        assert len(narrative_map.journey_node) == 1

    def test_foreign_journey_returns_none(self, project_service, narrative_map):
        foreign = Journey(id=99, lb="Foreign")
        assert DeleteJourneyUseCase(project_service).execute(foreign) is None
        assert len(narrative_map.journey) == 1

    def test_no_project_returns_none(self):
        service = ProjectService()
        assert DeleteJourneyUseCase(service).execute(Journey(id=1, lb="J")) is None
