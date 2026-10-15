# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_update_component_usecase.py
# Content      : Unit tests for UpdateComponentUseCase (SU003)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Unit tests for UpdateComponentUseCase.

Covers SU003 (component data edition):
- Valid update of State (lb, typ, note) and Event (lb, note)
- modification_date_time is set on update
- Empty label refused
- Invalid State.typ refused
- Non-editable entity refused
- No project refused
- Project marked as modified
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State, Event
from core.services.project_service import ProjectService
from usecases.view_management.update_component_usecase import UpdateComponentUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    service.create_project()
    return service


@pytest.fixture
def usecase(project_service):
    return UpdateComponentUseCase(project_service)


def _make_state():
    return State(id=1, lb="State 1", typ="Action")


def _make_event():
    return Event(id=1, lb="Event 1")


# ---------------------------------------------------------------------
# Valid updates
# ---------------------------------------------------------------------

def test_update_state_valid(usecase, project_service):
    state = _make_state()
    project_service.current_project.narrative_map[0].state.append(state)

    result = usecase.execute(entity=state, lb="Hero arrives", typ="Initial", note="Opening scene")

    assert result is not None and result['success'] is True
    assert result['entity'] is state
    assert result['component_type'] == "State"
    assert state.lb == "Hero arrives"
    assert state.typ == "Initial"
    assert state.note == "Opening scene"


def test_update_event_valid(usecase, project_service):
    event = _make_event()
    project_service.current_project.narrative_map[0].event.append(event)

    result = usecase.execute(entity=event, lb="Explosion", note="Loud noise")

    assert result is not None and result['success'] is True
    assert result['component_type'] == "Event"
    assert event.lb == "Explosion"
    assert event.note == "Loud noise"


def test_modification_date_time_set(usecase):
    state = _make_state()
    assert state.modification_date_time is None

    usecase.execute(entity=state, lb="Renamed")

    assert state.modification_date_time is not None


def test_label_is_stripped(usecase):
    state = _make_state()
    usecase.execute(entity=state, lb="  Padded label  ")
    assert state.lb == "Padded label"


def test_empty_note_becomes_none(usecase):
    state = _make_state()
    usecase.execute(entity=state, lb="State", note="   ")
    assert state.note is None


def test_none_note_keeps_existing_value(usecase):
    state = _make_state()
    state.note = "Keep me"
    usecase.execute(entity=state, lb="State", note=None)
    assert state.note == "Keep me"


def test_state_typ_defaults_to_current_when_none(usecase):
    state = _make_state()
    state.typ = "Final"
    usecase.execute(entity=state, lb="State", typ=None)
    assert state.typ == "Final"


def test_event_ignores_typ(usecase):
    event = _make_event()
    result = usecase.execute(entity=event, lb="Event", typ="Initial")
    assert result is not None and result['success'] is True
    assert not hasattr(event, "typ") or getattr(event, "typ", None) is None


# ---------------------------------------------------------------------
# Refused updates
# ---------------------------------------------------------------------

def test_empty_label_refused(usecase):
    state = _make_state()
    result = usecase.execute(entity=state, lb="   ")
    assert result is None
    assert state.lb == "State 1"


def test_invalid_state_typ_refused(usecase):
    state = _make_state()
    result = usecase.execute(entity=state, lb="State", typ="Bogus")
    assert result is None
    assert state.typ == "Action"


def test_non_editable_entity_refused(usecase):
    result = usecase.execute(entity="not an entity", lb="Label")
    assert result is None


def test_no_project_refused():
    service = ProjectService()
    usecase = UpdateComponentUseCase(service)
    result = usecase.execute(entity=_make_state(), lb="Label")
    assert result is None


# ---------------------------------------------------------------------
# Modification flag
# ---------------------------------------------------------------------

def test_project_marked_modified(usecase, project_service):
    project_service.set_modified(False)
    state = _make_state()
    usecase.execute(entity=state, lb="Renamed")
    assert project_service.is_modified is True
