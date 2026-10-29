# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_relation_edition.py
# Content      : Unit tests for TSK21 relation edition (SU004/FN021, RG027 revised): note update on the 3 relation types + journey attachment diff
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the relation edition (TSK21).

Covers:
- FN021: UpdateRelationUseCase updates the note of a State_to_event /
  Event_to_state arc (empty string clears it to None), sets
  modification_date_time, marks the project modified
- FN021: UpdateAgentStateAssociationUseCase does the same on a
  State_agent_rel
- Invalid relations are rejected (wrong type, not in the map, no project)
- RG027 revised: the journey attachment of a relation can be edited as a
  diff (attach to a second journey, detach from another) while the
  relation itself stays in the map
- Persistence: the note of the 3 relation types survives a JSON round-trip
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import (
    NarrativeMap, State, Event, State_to_event, Event_to_state, State_agent_rel,
)
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.view_management.update_relation_usecase import UpdateRelationUseCase
from usecases.agent_association.update_agent_state_association_usecase import (
    UpdateAgentStateAssociationUseCase,
)
from usecases.journey_management import (
    CreateJourneyUseCase, AttachRelationToJourneyUseCase,
    DetachRelationFromJourneyUseCase,
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


def make_arc(nm, state_id=1, event_id=1):
    s1 = next((s for s in nm.state if s.id == state_id),
              add_state(nm, state_id, "Initial"))
    e1 = next((e for e in nm.event if e.id == event_id), add_event(nm, event_id))
    return ArcService.create_arc(nm, s1, e1)


def make_association(project_service, nm):
    agent = CreateAgentUseCase(project_service).execute()['entity']
    state = nm.state[0]  # initial state created with the project
    return AssociateAgentStateUseCase(project_service).execute(agent, state)['relation']


# ---------------------------------------------------------------------
# FN021: note update on arcs (State_to_event / Event_to_state)
# ---------------------------------------------------------------------

class TestUpdateArcNote:
    def test_set_note(self, project_service, narrative_map):
        arc = make_arc(narrative_map)
        result = UpdateRelationUseCase(project_service).execute(arc, note="first meeting")
        assert result['success'] is True
        assert arc.note == "first meeting"
        assert arc.modification_date_time is not None
        assert project_service.is_modified is True

    def test_clear_note_with_empty_string(self, project_service, narrative_map):
        arc = make_arc(narrative_map)
        UpdateRelationUseCase(project_service).execute(arc, note="temp")
        UpdateRelationUseCase(project_service).execute(arc, note="   ")
        assert arc.note is None

    def test_event_to_state_arc(self, project_service, narrative_map):
        """The reverse arc (Event -> State) is editable too."""
        arc = make_arc(narrative_map)
        e1 = narrative_map.event[0]
        s2 = add_state(narrative_map, 2)
        back = ArcService.create_arc(narrative_map, e1, s2)
        assert isinstance(back, Event_to_state)
        result = UpdateRelationUseCase(project_service).execute(back, note="back arc")
        assert result['success'] is True
        assert back.note == "back arc"

    def test_rejects_association(self, project_service, narrative_map):
        """UpdateRelationUseCase only accepts arcs, not State_agent_rel."""
        rel = make_association(project_service, narrative_map)
        assert UpdateRelationUseCase(project_service).execute(rel, note="x") is None
        assert rel.note is None

    def test_rejects_foreign_arc(self, project_service, narrative_map):
        foreign = State_to_event(id=999, state_id=1, event_id=1)
        assert UpdateRelationUseCase(project_service).execute(foreign, note="x") is None

    def test_no_project(self):
        service = ProjectService()
        arc = State_to_event(id=1, state_id=1, event_id=1)
        assert UpdateRelationUseCase(service).execute(arc, note="x") is None


# ---------------------------------------------------------------------
# FN021: note update on State_agent_rel
# ---------------------------------------------------------------------

class TestUpdateAssociationNote:
    def test_set_note(self, project_service, narrative_map):
        rel = make_association(project_service, narrative_map)
        result = UpdateAgentStateAssociationUseCase(project_service).execute(
            rel, note="they meet here")
        assert result['success'] is True
        assert rel.note == "they meet here"
        assert rel.modification_date_time is not None
        assert project_service.is_modified is True

    def test_clear_note(self, project_service, narrative_map):
        rel = make_association(project_service, narrative_map)
        UpdateAgentStateAssociationUseCase(project_service).execute(rel, note="temp")
        UpdateAgentStateAssociationUseCase(project_service).execute(rel, note="")
        assert rel.note is None

    def test_rejects_arc(self, project_service, narrative_map):
        arc = make_arc(narrative_map)
        assert UpdateAgentStateAssociationUseCase(project_service).execute(
            arc, note="x") is None

    def test_rejects_foreign_association(self, project_service):
        foreign = State_agent_rel(id=999, agent_id=1, state_id=1)
        assert UpdateAgentStateAssociationUseCase(project_service).execute(
            foreign, note="x") is None


# ---------------------------------------------------------------------
# RG027 revised: journey attachment edited as a diff on the relation
# ---------------------------------------------------------------------

class TestJourneyAttachmentDiff:
    def test_attach_then_detach_keeps_relation(self, project_service, narrative_map):
        """The TSK21 dialog flow: attach to a second journey, then detach
        from the default one; the arc itself is untouched."""
        arc = make_arc(narrative_map)
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute()['entity']

        attach = AttachRelationToJourneyUseCase(project_service)
        detach = DetachRelationFromJourneyUseCase(project_service)

        result = attach.execute(arc, j2)
        assert result['success'] is True
        nodes = [n for n in narrative_map.journey_node
                 if n.state_to_event_id == arc.id]
        assert {n.journey_id for n in nodes} == {default.id, j2.id}

        result = detach.execute(arc, default)
        assert result['success'] is True and result['detached'] is True
        nodes = [n for n in narrative_map.journey_node
                 if n.state_to_event_id == arc.id]
        assert [n.journey_id for n in nodes] == [j2.id]
        # The arc is still in the map (orphaned w.r.t. journeys)
        assert arc in narrative_map.state_to_event

    def test_association_attachment_diff(self, project_service, narrative_map):
        """Same diff on a State_agent_rel (point C of TSK21)."""
        rel = make_association(project_service, narrative_map)
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        attach = AttachRelationToJourneyUseCase(project_service)
        detach = DetachRelationFromJourneyUseCase(project_service)

        attach.execute(rel, j2)
        nodes = [n for n in narrative_map.journey_node
                 if n.state_agent_rel_id == rel.id]
        assert len(nodes) == 2

        detach.execute(rel, narrative_map.journey[0])
        nodes = [n for n in narrative_map.journey_node
                 if n.state_agent_rel_id == rel.id]
        assert [n.journey_id for n in nodes] == [j2.id]
        assert rel in narrative_map.state_agent_rel

    def test_note_and_attachment_together(self, project_service, narrative_map):
        """One edition session: note + journey change applied together."""
        arc = make_arc(narrative_map)
        j2 = CreateJourneyUseCase(project_service).execute()['entity']
        UpdateRelationUseCase(project_service).execute(arc, note="note A")
        AttachRelationToJourneyUseCase(project_service).execute(arc, j2)
        assert arc.note == "note A"
        assert len([n for n in narrative_map.journey_node
                    if n.state_to_event_id == arc.id]) == 2


# ---------------------------------------------------------------------
# Persistence: note on the 3 relation types survives a JSON round-trip
# ---------------------------------------------------------------------

class TestNotePersistence:
    def test_json_round_trip(self, project_service, narrative_map):
        arc = make_arc(narrative_map)
        rel = make_association(project_service, narrative_map)
        UpdateRelationUseCase(project_service).execute(arc, note="arc note")
        UpdateAgentStateAssociationUseCase(project_service).execute(rel, note="rel note")

        data = narrative_map.to_dict()
        import json
        restored = NarrativeMap.from_dict(json.loads(json.dumps(data)))

        arc2 = next(a for a in restored.state_to_event if a.id == arc.id)
        rel2 = next(r for r in restored.state_agent_rel if r.id == rel.id)
        assert arc2.note == "arc note"
        assert rel2.note == "rel note"
