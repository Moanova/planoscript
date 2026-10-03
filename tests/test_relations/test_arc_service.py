# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_arc_service.py
# Content      : Unit tests for ArcService (RG054, RG058)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Unit tests for ArcService.create_arc.

Covers the following business rules:
- RG054: creating a relation creates a single independent arc
  (Event_to_state or State_to_event). No implicit node update logic.
- RG058: direct cycles of length 2 are forbidden.
- Duplicate detection: creating the same arc twice returns the existing one.
- Invalid combinations (State-State, Event-Event) return None.
"""

import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import NarrativeMap, State, Event, Event_to_state, State_to_event
from core.services.arc_service import ArcService


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

def make_narrative_map() -> NarrativeMap:
    """Create an empty narrative map for testing."""
    return NarrativeMap(id="test-uuid", lb="Test map")


def add_state(nm: NarrativeMap, state_id: int, typ: str = "Action") -> State:
    """Add a state to the narrative map."""
    state = State(id=state_id, lb=f"State {state_id}", typ=typ)
    nm.state.append(state)
    return state


def add_event(nm: NarrativeMap, event_id: int) -> Event:
    """Add an event to the narrative map."""
    event = Event(id=event_id, lb=f"Event {event_id}")
    nm.event.append(event)
    return event


def get_state_to_event(nm: NarrativeMap):
    """Return state_to_event tuples for easy comparison."""
    return [(a.state_id, a.event_id) for a in nm.state_to_event]


def get_event_to_state(nm: NarrativeMap):
    """Return event_to_state tuples for easy comparison."""
    return [(a.event_id, a.state_id) for a in nm.event_to_state]


# ---------------------------------------------------------------------
# RG054: State -> Event creates a State_to_event arc
# ---------------------------------------------------------------------

class TestStateToEventArc:
    """Tests for State -> Event relation creating a State_to_event arc."""

    def test_creates_new_arc(self):
        """A State->Event relation should create a State_to_event arc."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1, "Initial")
        e1 = add_event(nm, 1)

        result = ArcService.create_arc(nm, s1, e1)

        assert result is not None
        assert isinstance(result, State_to_event)
        assert result.state_id == 1
        assert result.event_id == 1
        assert len(nm.state_to_event) == 1
        assert len(nm.event_to_state) == 0
        assert get_state_to_event(nm) == [(1, 1)]

    def test_duplicate_returns_existing(self):
        """Creating the same State->Event relation twice returns the
        existing arc without creating a new one."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)

        first = ArcService.create_arc(nm, s1, e1)
        assert len(nm.state_to_event) == 1

        second = ArcService.create_arc(nm, s1, e1)
        assert second is first
        assert len(nm.state_to_event) == 1

    def test_multiple_outgoing_arcs_from_same_state(self):
        """A state can have multiple outgoing arcs to different events."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)
        e2 = add_event(nm, 2)

        ArcService.create_arc(nm, s1, e1)
        ArcService.create_arc(nm, s1, e2)

        assert len(nm.state_to_event) == 2
        assert get_state_to_event(nm) == [(1, 1), (1, 2)]


# ---------------------------------------------------------------------
# RG054: Event -> State creates an Event_to_state arc
# ---------------------------------------------------------------------

class TestEventToStateArc:
    """Tests for Event -> State relation creating an Event_to_state arc."""

    def test_creates_new_arc(self):
        """An Event->State relation should create an Event_to_state arc."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1, "Initial")
        e1 = add_event(nm, 1)

        result = ArcService.create_arc(nm, e1, s1)

        assert result is not None
        assert isinstance(result, Event_to_state)
        assert result.event_id == 1
        assert result.state_id == 1
        assert len(nm.event_to_state) == 1
        assert len(nm.state_to_event) == 0
        assert get_event_to_state(nm) == [(1, 1)]

    def test_duplicate_returns_existing(self):
        """Creating the same Event->State relation twice returns the
        existing arc."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)

        first = ArcService.create_arc(nm, e1, s1)
        assert len(nm.event_to_state) == 1

        second = ArcService.create_arc(nm, e1, s1)
        assert second is first
        assert len(nm.event_to_state) == 1

    def test_multiple_incoming_arcs_to_same_state(self):
        """A state can have multiple incoming arcs from different events."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)
        e2 = add_event(nm, 2)

        ArcService.create_arc(nm, e1, s1)
        ArcService.create_arc(nm, e2, s1)

        assert len(nm.event_to_state) == 2
        assert get_event_to_state(nm) == [(1, 1), (2, 1)]


# ---------------------------------------------------------------------
# Full scenario from testProjectData_20261003.md (adapted)
# ---------------------------------------------------------------------

class TestFullScenario:
    """Reproduces the scenario from the test report to verify
    that the arc lists match the expected outcome."""

    def test_full_scenario_arcs(self):
        nm = make_narrative_map()

        # Step 1: create project with initial state
        s1 = add_state(nm, 1, "Initial")
        assert len(nm.state_to_event) == 0
        assert len(nm.event_to_state) == 0

        # Step 2: create event E1 (no implicit arc)
        e1 = add_event(nm, 1)
        assert len(nm.state_to_event) == 0
        assert len(nm.event_to_state) == 0

        # Step 3: relation S1 -> E1 creates State_to_event(1, 1)
        ArcService.create_arc(nm, s1, e1)
        assert get_state_to_event(nm) == [(1, 1)]
        assert len(nm.event_to_state) == 0

        # Step 4: create state S2 (no implicit arc)
        s2 = add_state(nm, 2)
        assert len(nm.state_to_event) == 1
        assert len(nm.event_to_state) == 0

        # Step 5: relation E1 -> S2 creates Event_to_state(1, 2)
        ArcService.create_arc(nm, e1, s2)
        assert get_state_to_event(nm) == [(1, 1)]
        assert get_event_to_state(nm) == [(1, 2)]

        # Step 6: create event E2 (no implicit arc)
        e2 = add_event(nm, 2)
        assert len(nm.state_to_event) == 1
        assert len(nm.event_to_state) == 1

        # Step 7: relation S2 -> E2 creates State_to_event(2, 2)
        ArcService.create_arc(nm, s2, e2)
        assert get_state_to_event(nm) == [(1, 1), (2, 2)]
        assert get_event_to_state(nm) == [(1, 2)]

        # Step 8: create event E3 and relation S2 -> E3
        e3 = add_event(nm, 3)
        ArcService.create_arc(nm, s2, e3)
        assert get_state_to_event(nm) == [(1, 1), (2, 2), (2, 3)]
        assert get_event_to_state(nm) == [(1, 2)]


# ---------------------------------------------------------------------
# RG058: cycle prevention
# ---------------------------------------------------------------------

class TestRG058CyclePrevention:
    """RG058: direct cycles of length 2 are forbidden."""

    def test_state_to_event_then_event_to_state_blocked(self):
        """If S -> E exists, creating E -> S is forbidden."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)

        result = ArcService.create_arc(nm, s1, e1)
        assert result is not None

        result = ArcService.create_arc(nm, e1, s1)
        assert result is None

    def test_event_to_state_then_state_to_event_blocked(self):
        """If E -> S exists, creating S -> E is forbidden."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)

        result = ArcService.create_arc(nm, e1, s1)
        assert result is not None

        result = ArcService.create_arc(nm, s1, e1)
        assert result is None

    def test_cycle_check_across_different_states(self):
        """S -> E1 is fine even if E1 -> S2 exists (different states)."""
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        s2 = add_state(nm, 2)
        e1 = add_event(nm, 1)

        # E1 -> S2
        ArcService.create_arc(nm, e1, s2)
        # S1 -> E1 should be OK (different state)
        result = ArcService.create_arc(nm, s1, e1)
        assert result is not None


# ---------------------------------------------------------------------
# Invalid combinations
# ---------------------------------------------------------------------

class TestInvalidCombinations:
    """Invalid entity combinations return None."""

    def test_state_to_state_returns_none(self):
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        s2 = add_state(nm, 2)
        assert ArcService.create_arc(nm, s1, s2) is None

    def test_event_to_event_returns_none(self):
        nm = make_narrative_map()
        e1 = add_event(nm, 1)
        e2 = add_event(nm, 2)
        assert ArcService.create_arc(nm, e1, e2) is None


# ---------------------------------------------------------------------
# can_connect
# ---------------------------------------------------------------------

class TestCanConnect:
    """Tests for ArcService.can_connect."""

    def test_state_to_event_valid(self):
        assert ArcService.can_connect("State", "Event") is True

    def test_event_to_state_valid(self):
        assert ArcService.can_connect("Event", "State") is True

    def test_state_to_state_invalid(self):
        assert ArcService.can_connect("State", "State") is False

    def test_event_to_event_invalid(self):
        assert ArcService.can_connect("Event", "Event") is False


# ---------------------------------------------------------------------
# get_connected_entities
# ---------------------------------------------------------------------

class TestGetConnectedEntities:
    """Tests for ArcService.get_connected_entities."""

    def test_get_connections_for_state(self):
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        e1 = add_event(nm, 1)
        e2 = add_event(nm, 2)

        # S1 -> E1 (outgoing)
        ArcService.create_arc(nm, s1, e1)
        # E2 -> S1 (incoming)
        ArcService.create_arc(nm, e2, s1)

        connections = ArcService.get_connected_entities(nm, 1, "State")
        assert ("Event", 1) in connections
        assert ("Event", 2) in connections
        assert len(connections) == 2

    def test_get_connections_for_event(self):
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        s2 = add_state(nm, 2)
        e1 = add_event(nm, 1)

        # S1 -> E1 (incoming to event)
        ArcService.create_arc(nm, s1, e1)
        # E1 -> S2 (outgoing from event)
        ArcService.create_arc(nm, e1, s2)

        connections = ArcService.get_connected_entities(nm, 1, "Event")
        assert ("State", 1) in connections
        assert ("State", 2) in connections
        assert len(connections) == 2


# ---------------------------------------------------------------------
# delete_related_arcs
# ---------------------------------------------------------------------

class TestDeleteRelatedArcs:
    """Tests for ArcService.delete_related_arcs."""

    def test_delete_arcs_for_state(self):
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        s2 = add_state(nm, 2)
        e1 = add_event(nm, 1)

        ArcService.create_arc(nm, s1, e1)
        ArcService.create_arc(nm, e1, s2)

        ArcService.delete_related_arcs(nm, 1, "State")

        # S1's arcs should be removed: State_to_event(1,1) gone
        assert len(nm.state_to_event) == 0
        # Event_to_state(1,2) should remain (references s2, not s1)
        assert len(nm.event_to_state) == 1
        assert get_event_to_state(nm) == [(1, 2)]

    def test_delete_arcs_for_event(self):
        nm = make_narrative_map()
        s1 = add_state(nm, 1)
        s2 = add_state(nm, 2)
        e1 = add_event(nm, 1)

        ArcService.create_arc(nm, s1, e1)
        ArcService.create_arc(nm, e1, s2)

        ArcService.delete_related_arcs(nm, 1, "Event")

        # Both arcs reference e1, so both should be removed
        assert len(nm.state_to_event) == 0
        assert len(nm.event_to_state) == 0
