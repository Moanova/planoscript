# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_component_duplication.py
# Content      : Unit tests for DuplicateComponentUseCase (TSK28, SU003/FN016)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Unit tests for DuplicateComponentUseCase (TSK28).

Covers SU003/FN016 (component duplication):
- RG020: the copy gets a new unique id and a distinct label "{lb} (copy)"
- The copy inherits the editable attributes (typ for State, note, content)
- The copy is placed one grid major step to the right of the source
- RG062: the initial state cannot be duplicated
- RG024/RG052 revised: no Journey_node is created for the copy
  (isolated component, journey attachment happens on relations)
- Relations of the source are NOT duplicated
- Non-component entity / entity not in the map / no project refused
- Project marked as modified
- JSON round-trip of the copy
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State, Event, State_to_event
from core.models.view_model import NodeLayout, NodeType
from core.services.project_service import ProjectService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.view_management.duplicate_component_usecase import DuplicateComponentUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


@pytest.fixture
def usecase(project_service):
    return DuplicateComponentUseCase(project_service)


@pytest.fixture
def narrative_map(project_service):
    return project_service.current_project.narrative_map[0]


def _make_state(narrative_map, typ="Action", lb=None, note=None, content=None):
    state_id = narrative_map.get_next_id('state')
    return State(id=state_id, lb=lb or f"State {state_id}", typ=typ,
                 note=note, content=content)


def _make_event(narrative_map, lb=None, note=None, content=None):
    event_id = narrative_map.get_next_id('event')
    return Event(id=event_id, lb=lb or f"Event {event_id}",
                 note=note, content=content)


# ---------------------------------------------------------------------
# State duplication
# ---------------------------------------------------------------------

class TestDuplicateState:
    def test_new_id_and_distinct_label(self, usecase, narrative_map):
        state = _make_state(narrative_map)
        narrative_map.state.append(state)
        result = usecase.execute(state)
        assert result and result['success']
        copy = result['entity']
        assert isinstance(copy, State)
        assert copy.id != state.id
        assert copy.id == narrative_map.get_next_id('state') - 1
        assert copy.lb == f"{state.lb} (copy)"
        assert copy in narrative_map.state
        assert len(narrative_map.state) == 2 + 1  # + initial state (RG031)

    def test_attributes_inherited(self, usecase, narrative_map):
        state = _make_state(narrative_map, typ="Relation", note="a note", content="some content")
        narrative_map.state.append(state)
        result = usecase.execute(state)
        copy = result['entity']
        assert copy.typ == "Relation"
        assert copy.note == "a note"
        assert copy.content == "some content"

    def test_custom_label(self, usecase, narrative_map):
        state = _make_state(narrative_map)
        narrative_map.state.append(state)
        result = usecase.execute(state, lb="  Copy A  ")
        assert result['entity'].lb == "Copy A"

    def test_empty_custom_label_falls_back_to_suffix(self, usecase, narrative_map):
        state = _make_state(narrative_map)
        narrative_map.state.append(state)
        result = usecase.execute(state, lb="   ")
        assert result['entity'].lb == f"{state.lb} (copy)"

    def test_layout_placed_right_of_source(self, usecase, narrative_map):
        state = _make_state(narrative_map)
        narrative_map.state.append(state)
        source_layout = NodeLayout(node_id=state.id, node_type=NodeType.STATE, x=100, y=200)
        result = usecase.execute(state, source_layout=source_layout)
        layout = result['layout']
        assert layout.node_id == result['entity'].id
        assert layout.node_type == NodeType.STATE
        assert layout.x == 180  # 100 + grid_major_size (80), snapped
        assert layout.y == 200

    def test_initial_state_refused(self, usecase, narrative_map):
        initial = narrative_map.state[0]  # created by CreateProjectUseCase (RG031)
        assert initial.typ == "Initial"
        before = len(narrative_map.state)
        result = usecase.execute(initial)
        assert result is None
        assert len(narrative_map.state) == before

    def test_no_journey_node_created(self, usecase, narrative_map):
        """RG024/RG052 revised: an isolated component has no journey node."""
        state = _make_state(narrative_map)
        narrative_map.state.append(state)
        assert not narrative_map.journey_node
        result = usecase.execute(state)
        assert result and result['success']
        assert not narrative_map.journey_node

    def test_source_relations_not_duplicated(self, usecase, narrative_map):
        state = _make_state(narrative_map)
        event = _make_event(narrative_map)
        narrative_map.state.append(state)
        narrative_map.event.append(event)
        arc = State_to_event(id=narrative_map.get_next_id('state_to_event'),
                             state_id=state.id, event_id=event.id)
        narrative_map.state_to_event.append(arc)
        result = usecase.execute(state)
        assert result and result['success']
        copy = result['entity']
        assert len(narrative_map.state_to_event) == 1
        assert all(a.state_id != copy.id for a in narrative_map.state_to_event)

    def test_project_marked_modified(self, usecase, project_service, narrative_map):
        project_service.set_modified(False)
        state = _make_state(narrative_map)
        narrative_map.state.append(state)
        usecase.execute(state)
        assert project_service.is_modified


# ---------------------------------------------------------------------
# Event duplication
# ---------------------------------------------------------------------

class TestDuplicateEvent:
    def test_new_id_and_distinct_label(self, usecase, narrative_map):
        event = _make_event(narrative_map)
        narrative_map.event.append(event)
        result = usecase.execute(event)
        assert result and result['success']
        copy = result['entity']
        assert isinstance(copy, Event)
        assert copy.id != event.id
        assert copy.lb == f"{event.lb} (copy)"
        assert result['node_type'] == NodeType.EVENT
        assert result['component_type'] == "Event"

    def test_attributes_inherited(self, usecase, narrative_map):
        event = _make_event(narrative_map, note="n", content="c")
        narrative_map.event.append(event)
        result = usecase.execute(event)
        assert result['entity'].note == "n"
        assert result['entity'].content == "c"


# ---------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------

class TestRefusals:
    def test_no_project(self):
        service = ProjectService()
        uc = DuplicateComponentUseCase(service)
        assert uc.execute(State(id=1, lb="S", typ="Action")) is None

    def test_non_component_entity_refused(self, usecase, narrative_map):
        class NotAComponent:
            id = 99
        assert usecase.execute(NotAComponent()) is None

    def test_entity_not_in_map_refused(self, usecase, narrative_map):
        state = State(id=999, lb="Orphan", typ="Action")  # not appended
        assert usecase.execute(state) is None

    def test_copy_json_round_trip(self, usecase, narrative_map):
        state = _make_state(narrative_map, note="n", content="c")
        narrative_map.state.append(state)
        result = usecase.execute(state)
        copy = result['entity']
        restored = State.from_dict(json.loads(json.dumps(copy.to_dict())))
        assert restored.id == copy.id
        assert restored.lb == copy.lb
        assert restored.typ == copy.typ
        assert restored.note == "n"
        assert restored.content == "c"
