# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_export_service.py
# Content      : Unit tests for TSK33 (SU010/FN033): ExportService reading preview
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the export reading preview service (TSK33, SU010/FN033).

Covers ExportService.build_reading_text / build_note_index:
- flow centered on states from the initial state, in the real succession
  order (RG069), each state listed once, with predecessor events and
  associated agents annotated with their journey
- summary: all journeys vs single filtered journey (FN029)
- agent-state associations restricted to the filtered journey
- pending events listed at the end of the flow with a marker
- orphan components section
- HTML escaping of user content
- note anchors (#note-<kind>-<id>) and the note index (tooltip on hover)
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State, Event
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from core.services.export_service import ExportService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.journey_management import CreateJourneyUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


@pytest.fixture
def narrative_map(project_service):
    return project_service.current_project.narrative_map[0]


def add_state(nm, state_id, typ="Action", lb=None):
    state = State(id=state_id, lb=lb or f"State {state_id}", typ=typ)
    nm.state.append(state)
    return state


def add_event(nm, event_id, lb=None):
    event = Event(id=event_id, lb=lb or f"Event {event_id}")
    nm.event.append(event)
    return event


def build_chain(nm):
    """Initial -> E1 -> S2 -> E2 -> S3(Final); returns (states, events, arcs)."""
    s1 = nm.state[0]
    s1.lb = "Init"
    e1 = add_event(nm, 1, "E1")
    s2 = add_state(nm, 2, lb="S2")
    e2 = add_event(nm, 2, "E2")
    s3 = add_state(nm, 3, typ="Final", lb="End")
    ArcService.create_arc(nm, s1, e1)
    ArcService.create_arc(nm, e1, s2)
    ArcService.create_arc(nm, s2, e2)
    ArcService.create_arc(nm, e2, s3)
    return [s1, s2, s3], [e1, e2]


class TestFlow:
    def test_states_in_succession_order_each_once(self, narrative_map):
        """RG069 order: Init -> S2 -> End, each state listed once."""
        build_chain(narrative_map)
        html = ExportService.build_reading_text(narrative_map)
        i_init, i_s2, i_end = html.index("Init"), html.index("S2"), html.index("End")
        assert i_init < i_s2 < i_end
        assert html.count("<h3>State") == 3  # each state listed once

    def test_predecessor_events_and_content(self, narrative_map):
        states, events = build_chain(narrative_map)
        events[0].content = "what happens first"
        html = ExportService.build_reading_text(narrative_map)
        assert "Event E1" in html
        assert "what happens first" in html
        # S2's section lists its predecessor event E1 annotated with the journey
        s2_section = html[html.index("S2"):]
        assert "E1" in s2_section and "Journey 1" in s2_section

    def test_summary_all_journeys_vs_filtered(self, project_service, narrative_map):
        build_chain(narrative_map)
        j2 = CreateJourneyUseCase(project_service).execute(lb="Second")["entity"]
        html_all = ExportService.build_reading_text(narrative_map)
        assert 'href="#journey-%d"' % narrative_map.journey[0].id in html_all
        assert 'href="#journey-%d"' % j2.id in html_all
        html_f = ExportService.build_reading_text(narrative_map, journey=j2)
        assert 'href="#journey-%d"' % j2.id in html_f
        assert 'href="#journey-%d"' % narrative_map.journey[0].id not in html_f
        assert 'id="journey-%d"' % narrative_map.journey[0].id not in html_f  # no flow of j1


class TestFilterAndAssociations:
    def test_association_restricted_to_filtered_journey(self, project_service, narrative_map):
        states, _ = build_chain(narrative_map)
        agent = CreateAgentUseCase(project_service).execute(lb="Hero")["entity"]
        AssociateAgentStateUseCase(project_service).execute(agent, states[1])  # on S2, default journey
        j2 = CreateJourneyUseCase(project_service).execute(lb="Other")["entity"]

        html_default = ExportService.build_reading_text(
            narrative_map, journey=narrative_map.journey[0], agents=project_service.current_project.agent)
        assert "Hero" in html_default
        # under filter j2 (no association on it): agent absent from flow and section
        html_j2 = ExportService.build_reading_text(
            narrative_map, journey=j2, agents=project_service.current_project.agent)
        assert "Hero" not in html_j2
        # no filter: all project agents listed
        html_all = ExportService.build_reading_text(
            narrative_map, agents=project_service.current_project.agent)
        assert "Hero" in html_all


class TestPendingAndOrphans:
    def test_pending_event_listed_at_end_with_marker(self, narrative_map):
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1, "Dangling")
        ArcService.create_arc(narrative_map, s1, e1)  # incoming arc, no outgoing
        html = ExportService.build_reading_text(narrative_map)
        assert "pending" in html
        assert "Dangling" in html
        # listed after the flow (marker section), not as a state predecessor
        assert html.index("Pending events") > html.index("Journeys")

    def test_orphan_components_section(self, project_service, narrative_map):
        build_chain(narrative_map)
        add_state(narrative_map, 9, lb="Lonely")  # isolated state
        agent = CreateAgentUseCase(project_service).execute(lb="Free agent")["entity"]
        html = ExportService.build_reading_text(
            narrative_map, agents=project_service.current_project.agent)
        orphans = html[html.index("Orphan components"):]
        assert "Lonely" in orphans
        assert "Free agent" in orphans


class TestEscapingAndNotes:
    def test_html_escaping(self, narrative_map):
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1, lb="<script>alert(1)</script>")
        ArcService.create_arc(narrative_map, s1, e1)
        html = ExportService.build_reading_text(narrative_map)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_note_anchors_and_index(self, narrative_map):
        states, _ = build_chain(narrative_map)
        states[1].note = "a secret note"
        html = ExportService.build_reading_text(narrative_map)
        assert 'href="#note-state-%d"' % states[1].id in html
        index = ExportService.build_note_index(narrative_map)
        assert index[f"#note-state-{states[1].id}"] == "a secret note"


class TestSharedArc:
    def test_shared_arc_annotated_in_each_journey(self, project_service, narrative_map):
        from usecases.journey_management import AttachRelationToJourneyUseCase
        s1 = narrative_map.state[0]
        e1 = add_event(narrative_map, 1, "SharedE")
        arc = ArcService.create_arc(narrative_map, s1, e1)  # default journey
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")["entity"]
        AttachRelationToJourneyUseCase(project_service).execute(arc, j2)
        html = ExportService.build_reading_text(narrative_map)
        # the shared event appears in both journey flows, annotated with each journey
        assert html.count("SharedE") >= 2
        assert "Journey 1" in html and "J2" in html
