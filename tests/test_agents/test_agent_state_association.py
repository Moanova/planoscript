# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_agent_state_association.py
# Content      : Unit tests for agent-state association use cases (SU008, FN030, RG063, RG065)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for agent-state association use cases.

Covers SU008/FN030:
- Association: State_agent_rel created, project marked as modified
- RG063: duplicate association ignored (idempotent), no duplicate in
  state_agent_rel, 'already_associated' reported
- Dissociation: removal, refused when no association exists
- RG065: state deletion cascade removes only the associations of that
  state
- Persistence after save/load
- Rejections: no project, invalid entities, entities not in the project
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State
from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from usecases.agent_association.remove_state_associations_usecase import RemoveStateAssociationsUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


@pytest.fixture
def create_agent_usecase(project_service):
    return CreateAgentUseCase(project_service)


@pytest.fixture
def associate_usecase(project_service):
    return AssociateAgentStateUseCase(project_service)


@pytest.fixture
def dissociate_usecase(project_service):
    return DissociateAgentStateUseCase(project_service)


@pytest.fixture
def cascade_usecase(project_service):
    return RemoveStateAssociationsUseCase(project_service)


@pytest.fixture
def state(project_service):
    return project_service.current_project.narrative_map[0].state[0]


class TestAssociateAgentState:

    def test_association_created(self, project_service, create_agent_usecase,
                                 associate_usecase, state):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        project_service.set_modified(False)
        result = associate_usecase.execute(agent=agent, state=state)
        assert result is not None and result['success']
        assert result['already_associated'] is False
        narrative_map = project_service.current_project.narrative_map[0]
        assert len(narrative_map.state_agent_rel) == 1
        rel = narrative_map.state_agent_rel[0]
        assert rel.agent_id == agent.id and rel.state_id == state.id
        assert project_service.is_modified

    def test_rg063_duplicate_ignored(self, project_service, create_agent_usecase,
                                     associate_usecase, state):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        first = associate_usecase.execute(agent=agent, state=state)
        project_service.set_modified(False)
        second = associate_usecase.execute(agent=agent, state=state)
        assert second is not None and second['success']
        assert second['already_associated'] is True
        assert second['association'] is first['association']
        narrative_map = project_service.current_project.narrative_map[0]
        assert len(narrative_map.state_agent_rel) == 1

    def test_multiple_agents_multiple_states(self, project_service,
                                             create_agent_usecase,
                                             associate_usecase):
        narrative_map = project_service.current_project.narrative_map[0]
        state2 = State(id=narrative_map.get_next_id('state'), lb="S2", typ="Action")
        narrative_map.state.append(state2)
        agent1 = create_agent_usecase.execute(lb="Hero")['entity']
        agent2 = create_agent_usecase.execute(lb="Sword")['entity']

        assert associate_usecase.execute(agent=agent1, state=narrative_map.state[0])['success']
        assert associate_usecase.execute(agent=agent1, state=state2)['success']
        assert associate_usecase.execute(agent=agent2, state=narrative_map.state[0])['success']
        assert len(narrative_map.state_agent_rel) == 3

    def test_invalid_entities_refused(self, project_service, create_agent_usecase,
                                      associate_usecase, state):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        assert associate_usecase.execute(agent="not an agent", state=state) is None
        assert associate_usecase.execute(agent=agent, state="not a state") is None
        # Agent not registered in the project
        stranger = create_agent_usecase.execute(lb="Stranger")['entity']
        project_service.current_project.agent.remove(stranger)
        assert associate_usecase.execute(agent=stranger, state=state) is None

    def test_no_project_refused(self, create_agent_usecase, state):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        empty_service = ProjectService()
        assert AssociateAgentStateUseCase(empty_service).execute(
            agent=agent, state=state) is None


class TestDissociateAgentState:

    def test_dissociation(self, project_service, create_agent_usecase,
                          associate_usecase, dissociate_usecase, state):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        associate_usecase.execute(agent=agent, state=state)
        project_service.set_modified(False)
        result = dissociate_usecase.execute(agent=agent, state=state)
        assert result is not None and result['success']
        narrative_map = project_service.current_project.narrative_map[0]
        assert narrative_map.state_agent_rel == []
        assert project_service.is_modified

    def test_dissociation_without_association_refused(self, project_service,
                                                      create_agent_usecase,
                                                      dissociate_usecase, state):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        assert dissociate_usecase.execute(agent=agent, state=state) is None

    def test_other_associations_kept(self, project_service, create_agent_usecase,
                                     associate_usecase, dissociate_usecase):
        narrative_map = project_service.current_project.narrative_map[0]
        state2 = State(id=narrative_map.get_next_id('state'), lb="S2", typ="Action")
        narrative_map.state.append(state2)
        agent1 = create_agent_usecase.execute(lb="Hero")['entity']
        agent2 = create_agent_usecase.execute(lb="Sword")['entity']
        associate_usecase.execute(agent=agent1, state=narrative_map.state[0])
        associate_usecase.execute(agent=agent2, state=narrative_map.state[0])
        associate_usecase.execute(agent=agent1, state=state2)

        dissociate_usecase.execute(agent=agent1, state=narrative_map.state[0])
        remaining = {(rel.agent_id, rel.state_id)
                     for rel in narrative_map.state_agent_rel}
        assert remaining == {(agent2.id, narrative_map.state[0].id),
                              (agent1.id, state2.id)}


class TestRemoveStateAssociations:

    def test_rg065_cascade(self, project_service, create_agent_usecase,
                           associate_usecase, cascade_usecase):
        narrative_map = project_service.current_project.narrative_map[0]
        state2 = State(id=narrative_map.get_next_id('state'), lb="S2", typ="Action")
        narrative_map.state.append(state2)
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        associate_usecase.execute(agent=agent, state=narrative_map.state[0])
        associate_usecase.execute(agent=agent, state=state2)

        result = cascade_usecase.execute(state=narrative_map.state[0])
        assert result['deleted_associations'] == 1
        remaining = [(rel.agent_id, rel.state_id)
                     for rel in narrative_map.state_agent_rel]
        assert remaining == [(agent.id, state2.id)]

    def test_rg065_no_association(self, project_service, cascade_usecase, state):
        result = cascade_usecase.execute(state=state)
        assert result['deleted_associations'] == 0

    def test_non_state_refused(self, cascade_usecase):
        assert cascade_usecase.execute(state="not a state") is None

    def test_no_project_refused(self):
        assert RemoveStateAssociationsUseCase(ProjectService()).execute(
            state=State(id=1, lb="S", typ="Action")) is None


class TestAssociationPersistence:

    def test_round_trip(self, project_service, create_agent_usecase,
                        associate_usecase, tmp_path):
        agent = create_agent_usecase.execute(lb="Hero")['entity']
        state = project_service.current_project.narrative_map[0].state[0]
        associate_usecase.execute(agent=agent, state=state)

        file_path = str(tmp_path / "project.json")
        project_service.save_project(file_path)
        loaded = json.load(open(file_path))
        rels = loaded['narrative_map'][0]['state_agent_rel']
        assert len(rels) == 1
        assert rels[0]['agent_id'] == agent.id
        assert rels[0]['state_id'] == state.id
