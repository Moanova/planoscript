# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_journey_duplication.py
# Content      : Unit tests for TSK24 journey duplication (EPC05, FN025, RG020/RG021/RG023 revised/RG055, conception journey_attachment.md)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the journey duplication (TSK24, FN025).

Covers:
- RG020/FN025: the copy gets a new unique id and a distinct default label
  ("{source.lb} (copy)"); the note is inherited unless overridden
- RG055: the copy is not the default journey
- FN025: the journey nodes of the source journey are copied into the copy
  (same referenced arcs/associations, same sequence_order, new node ids);
  the relations themselves are shared, not duplicated
- RG023 revised (10-30-2026): the copy does NOT become the active journey
- Any duplication marks the map/project as modified
- Edge cases: source without nodes, explicit label/note, empty note,
  invalid source, no project
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
    CreateJourneyUseCase, DuplicateJourneyUseCase,
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


def build_source_journey(project_service, narrative_map):
    """Create a journey with two arcs (one per direction) and one
    agent-state association, all attached to it (active journey)."""
    j2 = CreateJourneyUseCase(project_service).execute(lb="Source", note="src note")['entity']
    s1 = narrative_map.state[0]  # initial state created with the project
    s2 = add_state(narrative_map, 2)
    e1 = add_event(narrative_map, 1)
    arc_se = ArcService.create_arc(narrative_map, s1, e1)   # State_to_event
    arc_es = ArcService.create_arc(narrative_map, e1, s2)   # Event_to_state
    agent = CreateAgentUseCase(project_service).execute()['entity']
    rel = AssociateAgentStateUseCase(project_service).execute(agent, s2)['relation']
    return j2, arc_se, arc_es, rel


# ---------------------------------------------------------------------
# FN025 / RG020 / RG021: new id, distinct label, inherited note
# ---------------------------------------------------------------------

class TestDuplicationBasics:
    def test_copy_gets_new_id_and_distinct_label(self, project_service, narrative_map):
        """RG020/FN025: new unique id; default label is "{source.lb} (copy)"."""
        source = narrative_map.journey[0]
        result = DuplicateJourneyUseCase(project_service).execute(source)
        assert result['success'] is True
        copy = result['entity']
        assert copy.id == result['entity_id'] == source.id + 1
        assert copy.id != source.id
        assert copy.lb == f"{source.lb} (copy)"
        assert copy.lb != source.lb

    def test_note_is_inherited_by_default(self, project_service, narrative_map):
        source = narrative_map.journey[0]
        from usecases.journey_management import UpdateJourneyUseCase
        UpdateJourneyUseCase(project_service).execute(source, note="hello")
        copy = DuplicateJourneyUseCase(project_service).execute(source)['entity']
        assert copy.note == "hello"

    def test_explicit_label_and_note(self, project_service, narrative_map):
        source = narrative_map.journey[0]
        copy = DuplicateJourneyUseCase(project_service).execute(
            source, lb="Branch A", note="custom")['entity']
        assert copy.lb == "Branch A"
        assert copy.note == "custom"

    def test_empty_note_clears_the_note(self, project_service, narrative_map):
        source = narrative_map.journey[0]
        from usecases.journey_management import UpdateJourneyUseCase
        UpdateJourneyUseCase(project_service).execute(source, note="hello")
        copy = DuplicateJourneyUseCase(project_service).execute(source, note="  ")['entity']
        assert copy.note is None

    def test_copy_is_not_default(self, project_service, narrative_map):
        """RG055: the copy does not become the default journey."""
        source = narrative_map.journey[0]
        assert source.default is True
        copy = DuplicateJourneyUseCase(project_service).execute(source)['entity']
        assert copy.default is False
        defaults = [j for j in narrative_map.journey if j.default]
        assert defaults == [source]


# ---------------------------------------------------------------------
# FN025: journey nodes are copied; relations are shared, not duplicated
# ---------------------------------------------------------------------

class TestNodeCopy:
    def test_nodes_are_copied_with_same_references(self, project_service, narrative_map):
        """FN025: each node of the source journey is copied into the copy
        (new node id, same arc/association references, same sequence_order)."""
        source, arc_se, arc_es, rel = build_source_journey(project_service, narrative_map)
        source_nodes = [n for n in narrative_map.journey_node if n.journey_id == source.id]
        assert len(source_nodes) == 3

        result = DuplicateJourneyUseCase(project_service).execute(source)
        copy = result['entity']
        copied = result['copied_nodes']
        assert len(copied) == 3
        assert all(n.journey_id == copy.id for n in copied)
        assert all(n.id not in {s.id for s in source_nodes} for n in copied)
        # same references, same order
        refs = lambda nodes: {
            (n.state_to_event_id, n.event_to_state_id, n.state_agent_rel_id,
             n.sequence_order) for n in nodes}
        assert refs(copied) == refs(source_nodes)
        assert {n.state_to_event_id for n in copied
                if n.state_to_event_id is not None} == {arc_se.id}
        assert {n.event_to_state_id for n in copied
                if n.event_to_state_id is not None} == {arc_es.id}
        assert {n.state_agent_rel_id for n in copied
                if n.state_agent_rel_id is not None} == {rel.id}

    def test_relations_are_not_duplicated(self, project_service, narrative_map):
        """The arcs and the association are shared between source and copy."""
        source, arc_se, arc_es, rel = build_source_journey(project_service, narrative_map)
        DuplicateJourneyUseCase(project_service).execute(source)
        assert len(narrative_map.state_to_event) == 1
        assert len(narrative_map.event_to_state) == 1
        assert len(narrative_map.state_agent_rel) == 1
        # one node per relation in each journey: 3 + 3 nodes
        assert len(narrative_map.journey_node) == 6

    def test_other_journeys_nodes_are_untouched(self, project_service, narrative_map):
        source, arc_se, arc_es, rel = build_source_journey(project_service, narrative_map)
        default = narrative_map.journey[0]
        before = [n for n in narrative_map.journey_node if n.journey_id == default.id]
        DuplicateJourneyUseCase(project_service).execute(source)
        after = [n for n in narrative_map.journey_node if n.journey_id == default.id]
        assert before == after

    def test_duplicate_journey_without_nodes(self, project_service, narrative_map):
        """A journey with no relation yet duplicates to an empty journey."""
        source = CreateJourneyUseCase(project_service).execute(lb="Empty")['entity']
        result = DuplicateJourneyUseCase(project_service).execute(source)
        assert result['success'] is True
        assert result['copied_nodes'] == []
        assert [n for n in narrative_map.journey_node
                if n.journey_id == result['entity_id']] == []


# ---------------------------------------------------------------------
# RG023 revised: the copy is not activated; modification is marked
# ---------------------------------------------------------------------

class TestActiveAndModified:
    def test_copy_does_not_become_active(self, project_service, narrative_map):
        """RG023 revised (10-30-2026): duplicating does not change the
        active journey."""
        default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        assert narrative_map.active_journey_id == j2.id
        DuplicateJourneyUseCase(project_service).execute(j2)
        assert narrative_map.active_journey_id == j2.id
        DuplicateJourneyUseCase(project_service).execute(default)
        assert narrative_map.active_journey_id == j2.id

    def test_duplication_marks_modified(self, project_service, narrative_map):
        project_service.set_modified(False)
        DuplicateJourneyUseCase(project_service).execute(narrative_map.journey[0])
        assert project_service.is_modified is True


# ---------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------

class TestEdgeCases:
    def test_foreign_source_returns_none(self, project_service, narrative_map):
        foreign = Journey(id=99, lb="Foreign")
        assert DuplicateJourneyUseCase(project_service).execute(foreign) is None
        assert len(narrative_map.journey) == 1

    def test_no_project_returns_none(self):
        service = ProjectService()
        source = Journey(id=1, lb="J")
        assert DuplicateJourneyUseCase(service).execute(source) is None
