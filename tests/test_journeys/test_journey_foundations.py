# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_journey_foundations.py
# Content      : Unit tests for TSK22 journey foundations (EPC05, FN023/FN024/FN026, RG022/RG023/RG055, RG026/RG052 revised, RG056 extended, RG066 revised)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the journey foundations (TSK22).

Covers:
- RG022: a new project has a default journey, activated (active_journey_id)
- RG023: creating a journey activates it
- FN024/RG055: rename, note, single default journey
- FN026: activate an existing journey
- RG052 revised: creating an arc attaches it to the active journey
  (one Journey_node referencing the arc)
- RG066 revised: creating an agent-state association attaches it to the
  active journey (Journey_node.state_agent_rel_id)
- RG026 revised: attach/detach a relation to/from a journey; a relation
  may belong to 1..n journeys (several nodes referencing the same arc)
- RG056 extended: deleting arcs (entity deletion) removes the journey
  nodes referencing them; dissociating an agent removes the node of the
  association
- Persistence: active_journey_id and state_agent_rel_id survive a
  JSON round-trip; old projects without these fields still load
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import (
    NarrativeMap, State, Event, Journey, State_to_event, Event_to_state,
)
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from usecases.journey_management import (
    CreateJourneyUseCase, UpdateJourneyUseCase, ActivateJourneyUseCase,
    AttachRelationToJourneyUseCase, DetachRelationFromJourneyUseCase,
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
# RG022/RG023: default journey created and activated; new journey activated
# ---------------------------------------------------------------------

class TestJourneyActivation:
    def test_new_project_has_active_default_journey(self, narrative_map):
        """RG022: the default journey is created and activated."""
        assert len(narrative_map.journey) == 1
        default = narrative_map.journey[0]
        assert default.default is True
        assert narrative_map.active_journey_id == default.id
        assert narrative_map.get_active_journey() is default

    def test_create_journey_activates_it(self, project_service, narrative_map):
        """RG023/FN023: a newly created journey becomes the active one."""
        result = CreateJourneyUseCase(project_service).execute(lb="J2")
        assert result['success'] is True
        journey = result['entity']
        assert journey.default is False
        assert narrative_map.active_journey_id == journey.id
        assert project_service.is_modified is True

    def test_activate_existing_journey(self, project_service, narrative_map):
        """FN026: activating an existing journey updates active_journey_id."""
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        assert narrative_map.active_journey_id == j2.id
        result = ActivateJourneyUseCase(project_service).execute(default)
        assert result['success'] is True
        assert narrative_map.active_journey_id == default.id

    def test_activate_rejects_foreign_journey(self, project_service):
        foreign = Journey(id=99, lb="Foreign")
        assert ActivateJourneyUseCase(project_service).execute(foreign) is None


# ---------------------------------------------------------------------
# FN024 / RG055: rename, note, single default
# ---------------------------------------------------------------------

class TestJourneyUpdate:
    def test_rename_and_note(self, project_service, narrative_map):
        journey = narrative_map.journey[0]
        result = UpdateJourneyUseCase(project_service).execute(
            journey, lb="Main story", note="act one")
        assert result['success'] is True
        assert journey.lb == "Main story"
        assert journey.note == "act one"
        assert journey.modification_date_time is not None

    def test_single_default_journey(self, project_service, narrative_map):
        """RG055: designating a default clears the previous one."""
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        UpdateJourneyUseCase(project_service).execute(j2, default=True)
        assert j2.default is True
        assert narrative_map.journey[0].default is False
        defaults = [j for j in narrative_map.journey if j.default]
        assert len(defaults) == 1


# ---------------------------------------------------------------------
# RG052 revised: arc creation attaches the arc to the active journey
# ---------------------------------------------------------------------

class TestAutomaticAttachment:
    def test_arc_attached_to_active_journey(self, narrative_map):
        """RG052 revised: create_arc creates a Journey_node in the active journey."""
        s1 = add_state(narrative_map, 1, "Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)

        assert isinstance(arc, State_to_event)
        nodes = [n for n in narrative_map.journey_node
                 if n.state_to_event_id == arc.id]
        assert len(nodes) == 1
        assert nodes[0].journey_id == narrative_map.active_journey_id
        assert nodes[0].sequence_order == 1

    def test_arc_without_journey_creates_no_node(self):
        """No journey in the map: no node, no crash."""
        nm = NarrativeMap(id="t", lb="t")
        s1 = add_state(nm, 1, "Initial")
        e1 = add_event(nm, 1)
        arc = ArcService.create_arc(nm, s1, e1)
        assert arc is not None
        assert nm.journey_node == []

    def test_association_attached_to_active_journey(self, project_service, narrative_map):
        """RG066 revised: a new State_agent_rel gets a node with state_agent_rel_id."""
        agent = CreateAgentUseCase(project_service).execute()['entity']
        state = narrative_map.state[0]  # initial state created with the project
        result = AssociateAgentStateUseCase(project_service).execute(agent, state)
        rel = result['relation']

        nodes = [n for n in narrative_map.journey_node
                 if n.state_agent_rel_id == rel.id]
        assert len(nodes) == 1
        assert nodes[0].journey_id == narrative_map.active_journey_id


# ---------------------------------------------------------------------
# RG026 revised: explicit attach/detach, 1..n journeys per relation
# ---------------------------------------------------------------------

class TestAttachDetach:
    def test_attach_arc_to_second_journey(self, project_service, narrative_map):
        """A relation may belong to 1..n journeys: same arc, two nodes."""
        s1 = add_state(narrative_map, 1, "Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        j2 = CreateJourneyUseCase(project_service).execute()['entity']

        result = AttachRelationToJourneyUseCase(project_service).execute(arc, j2)
        assert result['success'] is True
        assert result['already_attached'] is False

        nodes = [n for n in narrative_map.journey_node
                 if n.state_to_event_id == arc.id]
        assert len(nodes) == 2
        assert {n.journey_id for n in nodes} == {
            narrative_map.journey[0].id, j2.id}

    def test_attach_is_idempotent(self, project_service, narrative_map):
        s1 = add_state(narrative_map, 1, "Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        journey = narrative_map.get_active_journey()

        result = AttachRelationToJourneyUseCase(project_service).execute(arc, journey)
        assert result['already_attached'] is True
        assert len(narrative_map.journey_node) == 1

    def test_detach_keeps_relation_and_other_journeys(self, project_service, narrative_map):
        s1 = add_state(narrative_map, 1, "Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        AttachRelationToJourneyUseCase(project_service).execute(arc, j2)

        result = DetachRelationFromJourneyUseCase(project_service).execute(arc, j2)
        assert result['detached'] is True
        # the arc itself is untouched
        assert len(narrative_map.state_to_event) == 1
        # only the node of j2 is removed
        nodes = [n for n in narrative_map.journey_node
                 if n.state_to_event_id == arc.id]
        assert len(nodes) == 1
        assert nodes[0].journey_id == default.id

    def test_detach_not_attached(self, project_service, narrative_map):
        s1 = add_state(narrative_map, 1, "Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        result = DetachRelationFromJourneyUseCase(project_service).execute(arc, j2)
        assert result['detached'] is False
        assert len(narrative_map.journey_node) == 1


# ---------------------------------------------------------------------
# RG056 extended / RG066 revised: cascades remove the journey nodes
# ---------------------------------------------------------------------

class TestCascades:
    def test_delete_state_cascades_to_journey_nodes(self, narrative_map):
        """RG056 extended: deleting a state removes arcs AND their nodes."""
        s1 = add_state(narrative_map, 1, "Initial")
        s2 = add_state(narrative_map, 2)
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        assert any(n.state_to_event_id == arc.id for n in narrative_map.journey_node)

        ArcService.delete_related_arcs(narrative_map, s1.id, "State")
        assert narrative_map.state_to_event == []
        assert narrative_map.journey_node == []
        # the other state is untouched
        assert s2 in narrative_map.state

    def test_dissociation_removes_association_node(self, project_service, narrative_map):
        """RG066 revised: dissociating removes the node of the association."""
        agent = CreateAgentUseCase(project_service).execute()['entity']
        state = narrative_map.state[0]
        rel = AssociateAgentStateUseCase(project_service).execute(agent, state)['relation']
        assert any(n.state_agent_rel_id == rel.id for n in narrative_map.journey_node)

        DissociateAgentStateUseCase(project_service).execute(agent, state)
        assert narrative_map.state_agent_rel == []
        assert narrative_map.journey_node == []


# ---------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------

class TestPersistence:
    def test_round_trip(self, project_service, narrative_map):
        """active_journey_id and state_agent_rel_id survive a JSON round-trip."""
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        s1 = add_state(narrative_map, 1, "Initial")
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        agent = CreateAgentUseCase(project_service).execute()['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(agent, s1)['relation']

        data = project_service.current_project.to_dict()
        blob = json.dumps(data)
        from core.models.data_model import Project
        restored = Project.from_dict(json.loads(blob))
        nm = restored.narrative_map[0]

        assert nm.active_journey_id == j2.id
        node_arc = [n for n in nm.journey_node if n.state_to_event_id == arc.id]
        node_rel = [n for n in nm.journey_node if n.state_agent_rel_id == rel.id]
        assert len(node_arc) == 1
        assert len(node_rel) == 1

    def test_legacy_project_without_new_fields_loads(self):
        """Retrocompatibility: a project JSON without active_journey_id /
        state_agent_rel_id still loads and falls back to the default journey."""
        from core.models.data_model import Project
        blob = json.dumps({
            'id': 'p1', 'lb': 'P', 'creation_date_time': '2026-10-29T10:00:00',
            'modification_date_time': None,
            'agent': [],
            'narrative_map': [{
                'id': 'm1', 'lb': 'M',
                'creation_date_time': '2026-10-29T10:00:00',
                'modification_date_time': None,
                'state': [], 'event': [],
                'journey': [{'id': 1, 'lb': 'Journey 1', 'default': True,
                             'note': None,
                             'creation_date_time': '2026-10-29T10:00:00',
                             'modification_date_time': None}],
                'state_agent_rel': [], 'event_to_state': [], 'state_to_event': [],
                'journey_node': []
            }]
        })
        project = Project.from_dict(json.loads(blob))
        nm = project.narrative_map[0]
        assert nm.active_journey_id is None
        assert nm.get_active_journey().id == 1
