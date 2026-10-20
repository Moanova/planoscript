# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_delete_agent_usecase.py
# Content      : Unit tests for DeleteAgentUseCase (SU008, FN031, RG064)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for agent deletion.

Covers SU008/FN031 (agent deletion with RG064 cascade):
- Agent removed from project.agent, project marked as modified
- RG064 cascade: all State_agent_rel referencing the agent ID are
  removed, associations of other agents are kept
- deleted_associations count (0, 1, n)
- Invalid entity / unknown agent / no project refused
- Persistence: agent and its associations absent after save/load
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import State, State_agent_rel
from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.delete_agent_usecase import DeleteAgentUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


@pytest.fixture
def create_usecase(project_service):
    return CreateAgentUseCase(project_service)


@pytest.fixture
def delete_usecase(project_service):
    return DeleteAgentUseCase(project_service)


def _add_association(project_service, state_id, agent_id):
    narrative_map = project_service.current_project.narrative_map[0]
    rel = State_agent_rel(id=len(narrative_map.state_agent_rel) + 1,
                          state_id=state_id, agent_id=agent_id)
    narrative_map.state_agent_rel.append(rel)
    return rel


class TestDeleteAgentUseCase:

    def test_simple_deletion(self, project_service, create_usecase, delete_usecase):
        agent = create_usecase.execute(lb="Hero")['entity']
        project_service.set_modified(False)
        result = delete_usecase.execute(entity=agent)
        assert result is not None and result['success']
        assert result['deleted_associations'] == 0
        assert project_service.current_project.agent == []
        assert project_service.is_modified

    def test_cascade_rg064(self, project_service, create_usecase, delete_usecase):
        target = create_usecase.execute(lb="Hero")['entity']
        other = create_usecase.execute(lb="Sword")['entity']
        narrative_map = project_service.current_project.narrative_map[0]
        state = narrative_map.state[0]
        rel_target = _add_association(project_service, state.id, target.id)
        rel_other = _add_association(project_service, state.id, other.id)

        result = delete_usecase.execute(entity=target)
        assert result['deleted_associations'] == 1
        remaining = narrative_map.state_agent_rel
        assert rel_target not in remaining
        assert rel_other in remaining
        assert [a.id for a in project_service.current_project.agent] == [other.id]

    def test_cascade_multiple_associations(self, project_service, create_usecase, delete_usecase):
        target = create_usecase.execute(lb="Hero")['entity']
        narrative_map = project_service.current_project.narrative_map[0]
        from core.models.data_model import State as StateEntity
        state2 = StateEntity(id=narrative_map.get_next_id('state'),
                             lb="State 2", typ="Action")
        narrative_map.state.append(state2)
        for state in narrative_map.state:
            _add_association(project_service, state.id, target.id)

        result = delete_usecase.execute(entity=target)
        assert result['deleted_associations'] == 2
        assert narrative_map.state_agent_rel == []

    def test_non_agent_entity_refused(self, delete_usecase):
        assert delete_usecase.execute(entity="not an agent") is None

    def test_unknown_agent_refused(self, project_service, create_usecase, delete_usecase):
        from core.models.data_model import Agent
        agent = create_usecase.execute(lb="Hero")['entity']
        delete_usecase.execute(entity=agent)
        assert delete_usecase.execute(entity=agent) is None

    def test_no_project_refused(self, create_usecase):
        agent = create_usecase.execute(lb="Hero")['entity']
        empty_service = ProjectService()
        assert DeleteAgentUseCase(empty_service).execute(entity=agent) is None

    def test_persistence_after_deletion(self, project_service, create_usecase,
                                        delete_usecase, tmp_path):
        target = create_usecase.execute(lb="Hero")['entity']
        kept = create_usecase.execute(lb="Sword")['entity']
        narrative_map = project_service.current_project.narrative_map[0]
        state = narrative_map.state[0]
        _add_association(project_service, state.id, target.id)
        rel_kept = _add_association(project_service, state.id, kept.id)

        delete_usecase.execute(entity=target)
        file_path = str(tmp_path / "project.json")
        project_service.save_project(file_path)
        loaded = json.load(open(file_path))

        agents = [(a['id'], a['lb']) for a in loaded['agent']]
        assert agents == [(kept.id, "Sword")]
        rels = loaded['narrative_map'][0]['state_agent_rel']
        assert len(rels) == 1
        assert rels[0]['agent_id'] == kept.id
