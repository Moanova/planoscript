# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_journey_filter.py
# Content      : Unit tests for the journey display filter (TSK29, FN029/RG042, RG026)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the journey display filter (TSK29).

Covers:
- FN029/RG042/RG026 (revised TSK35): derived visibility under the active
  journey — visible relations are the arcs attached to the journey plus
  the associations whose state is visible; visible components get
  membership from arcs only; orphan components and relations of other
  journeys are hidden
- filter disabled ("All journeys"): everything visible (None = no filter)
- a relation attached to 1..n journeys is visible under each of them
- attach/detach (RG027) and arc deletion change the derived visibility
- agent-state associations (State_agent_rel) never give membership to
  their state: visible only on a state already visible (regression TSK35,
  bug seen on the testCase01 project)
- the filter state is a view state: it is not part of the persisted
  project JSON nor of the workspace layout (RG041)
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State, Event
from core.services.project_service import ProjectService
from core.services.arc_service import ArcService
from core.services.journey_filter_service import JourneyFilterService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.journey_management import (
    CreateJourneyUseCase, ActivateJourneyUseCase,
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


def keys_for(nm, journey):
    return JourneyFilterService.visible_relation_keys(nm, journey, True)


def components_for(nm, journey):
    return JourneyFilterService.visible_component_ids(nm, journey, True)


# ---------------------------------------------------------------------
# FN029: derived visibility under the active journey
# ---------------------------------------------------------------------

class TestDerivedVisibility:
    def test_filter_disabled_returns_none(self, narrative_map):
        """Filter off ("All journeys"): no filtering, everything visible."""
        j = narrative_map.journey[0]
        assert JourneyFilterService.visible_relation_keys(narrative_map, j, False) is None
        assert JourneyFilterService.visible_component_ids(narrative_map, j, False) is None

    def test_filter_without_relation_hides_everything(self, narrative_map):
        """No journey node yet: no relation, no component is visible."""
        j = narrative_map.journey[0]
        add_state(narrative_map, 1, typ="Initial")
        add_event(narrative_map, 1)
        assert keys_for(narrative_map, j) == set()
        assert components_for(narrative_map, j) == (set(), set())

    def test_arc_visible_only_under_its_journey(self, project_service, narrative_map):
        """An arc created under the active journey is visible under it
        only; its two components get membership (RG026)."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        j_default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']

        arc = ArcService.create_arc(narrative_map, s1, e1)  # attached to J2 (active)
        assert keys_for(narrative_map, j2) == {('state_to_event', arc.id)}
        assert keys_for(narrative_map, j_default) == set()
        sids, eids = components_for(narrative_map, j2)
        assert sids == {s1.id} and eids == {e1.id}
        sids, eids = components_for(narrative_map, j_default)
        assert sids == set() and eids == set()

    def test_orphan_component_hidden_under_filter(self, project_service, narrative_map):
        """RG026/FN029: an orphan component (no relation) belongs to no
        journey and is hidden under an active filter."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        s2 = add_state(narrative_map, 2)  # orphan
        j = narrative_map.journey[0]
        ArcService.create_arc(narrative_map, s1, e1)
        sids, eids = components_for(narrative_map, j)
        assert sids == {1} and eids == {1}
        assert s2.id not in sids

    def test_relation_shared_by_several_journeys(self, project_service, narrative_map):
        """RG026 revised: a relation may belong to 1..n journeys; it is
        visible under each of them."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        j_default = narrative_map.journey[0]
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']
        arc = ArcService.create_arc(narrative_map, s1, e1)  # in J2
        AttachRelationToJourneyUseCase(project_service).execute(
            arc, j_default, narrative_map=narrative_map)
        assert keys_for(narrative_map, j_default) == {('state_to_event', arc.id)}
        assert keys_for(narrative_map, j2) == {('state_to_event', arc.id)}
        # detach from J2 -> hidden under J2, still visible under default
        DetachRelationFromJourneyUseCase(project_service).execute(
            arc, j2, narrative_map=narrative_map)
        assert keys_for(narrative_map, j2) == set()
        assert keys_for(narrative_map, j_default) == {('state_to_event', arc.id)}

    def test_arc_deletion_makes_components_orphan(self, project_service, narrative_map):
        """Deleting the last relation of a component hides it again under
        the filter (RG056 extended)."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        e1 = add_event(narrative_map, 1)
        j = narrative_map.journey[0]
        ArcService.create_arc(narrative_map, s1, e1)
        ArcService.delete_related_arcs(narrative_map, e1.id, "Event")
        assert keys_for(narrative_map, j) == set()
        assert components_for(narrative_map, j) == (set(), set())

    def test_association_does_not_give_membership(self, project_service, narrative_map):
        """RG026 revised (TSK35): membership derives from arcs only. An
        association on a state with no arc in the journey is hidden and
        does not make its state visible."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        j = narrative_map.journey[0]
        agent = CreateAgentUseCase(project_service).execute(
            lb="A1", typ="Subject", note=None, content=None)['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(
            agent=agent, state=s1)['association']
        # no arc attached to the journey yet: association hidden, no membership
        assert keys_for(narrative_map, j) == set()
        assert components_for(narrative_map, j) == (set(), set())
        # once an arc of the state is attached, the association shows up
        e1 = add_event(narrative_map, 1)
        arc = ArcService.create_arc(narrative_map, s1, e1)
        assert keys_for(narrative_map, j) == {('state_to_event', arc.id),
                                             ('state_agent_rel', rel.id)}
        sids, eids = components_for(narrative_map, j)
        assert sids == {s1.id} and eids == {e1.id}

    def test_association_of_foreign_state_does_not_pull_it_in(self, project_service, narrative_map):
        """Regression TSK35 (bug seen on testCase01): an association attached
        to J1 but sitting on a state whose arcs belong to J2 must neither
        make that state visible under the J1 filter nor stay visible."""
        s1 = add_state(narrative_map, 1, typ="Initial")
        s2 = add_state(narrative_map, 2)
        e1 = add_event(narrative_map, 1)
        e2 = add_event(narrative_map, 2)
        j1 = narrative_map.journey[0]
        arc1 = ArcService.create_arc(narrative_map, s1, e1)  # attached to default J1
        j2 = CreateJourneyUseCase(project_service).execute(lb="J2")['entity']  # J2 active
        ArcService.create_arc(narrative_map, s1, e2)  # in J2
        ArcService.create_arc(narrative_map, e2, s2)  # in J2
        agent = CreateAgentUseCase(project_service).execute(
            lb="A1", typ="Subject", note=None, content=None)['entity']
        rel = AssociateAgentStateUseCase(project_service).execute(
            agent=agent, state=s2)['association']  # node in active J2
        AttachRelationToJourneyUseCase(project_service).execute(
            rel, j1, narrative_map=narrative_map)  # also attached to J1
        # under J1: s2 has no arc in J1 -> hidden; the association is filtered out
        sids, eids = components_for(narrative_map, j1)
        assert sids == {s1.id} and eids == {e1.id}
        assert keys_for(narrative_map, j1) == {('state_to_event', arc1.id)}
        # under J2: s2 visible via its arcs, association visible
        sids, eids = components_for(narrative_map, j2)
        assert sids == {s1.id, s2.id} and eids == {e2.id}
        assert ('state_agent_rel', rel.id) in keys_for(narrative_map, j2)


# ---------------------------------------------------------------------
# RG041: the filter is a view state, never persisted
# ---------------------------------------------------------------------

class TestFilterNotPersisted:
    def test_filter_state_not_in_project_json(self, narrative_map):
        """RG041: the filter state is not business data — it must not
        appear in the serialized project."""
        data = narrative_map.to_dict()
        assert 'journey_filter_active' not in data
        assert 'journey_filter_active' not in json.dumps(data)

    def test_filter_state_not_in_layout_json(self, project_service, narrative_map):
        """RG041: the filter state is not layout data either (like zoom
        and scrollbars)."""
        from core.models.view_model import WorkspaceLayout
        layout = WorkspaceLayout(narrative_map_id=narrative_map.id)
        data = layout.to_dict()
        assert 'journey_filter_active' not in data
        assert 'journey_filter_active' not in json.dumps(data)
