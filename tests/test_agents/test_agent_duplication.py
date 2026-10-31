# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_agent_duplication.py
# Content      : Unit tests for DuplicateAgentUseCase (TSK28 evolution, SU003/FN016)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Unit tests for DuplicateAgentUseCase (TSK28 evolution).

Covers agent duplication (FN016, agents are project-level components, SU008):
- RG020: the copy gets a new project-unique id and a distinct label
  "{lb} (copy)"
- The copy inherits the editable attributes (typ, note, content)
- Decision TSC 31-10-2026: the agent-state associations of the source are
  NOT copied (the copy starts unassociated, same principle as component
  duplication: relations are not duplicated, RG024)
- Custom label; empty label falls back to the "(copy)" suffix
- No project / invalid source refused
- Project marked as modified
- JSON round-trip of the copy
"""
import json
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import Agent, State
from core.services.project_service import ProjectService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.duplicate_agent_usecase import DuplicateAgentUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


@pytest.fixture
def usecase(project_service):
    return DuplicateAgentUseCase(project_service)


@pytest.fixture
def project(project_service):
    return project_service.current_project


# ---------------------------------------------------------------------
# Duplication
# ---------------------------------------------------------------------

class TestDuplicateAgent:
    def test_new_id_and_distinct_label(self, usecase, project):
        agent = Agent(id=project.get_next_id('agent'), lb="Hero", typ="Subject")
        project.agent.append(agent)
        result = usecase.execute(agent)
        assert result and result['success']
        copy = result['entity']
        assert isinstance(copy, Agent)
        assert copy.id != agent.id
        assert copy.id == project.get_next_id('agent') - 1
        assert copy.lb == "Hero (copy)"
        assert copy in project.agent
        assert len(project.agent) == 2

    def test_attributes_inherited(self, usecase, project):
        agent = Agent(id=project.get_next_id('agent'), lb="Hero",
                      typ="Object", note="a note", content="some content")
        project.agent.append(agent)
        result = usecase.execute(agent)
        copy = result['entity']
        assert copy.typ == "Object"
        assert copy.note == "a note"
        assert copy.content == "some content"

    def test_custom_label(self, usecase, project):
        agent = Agent(id=project.get_next_id('agent'), lb="Hero")
        project.agent.append(agent)
        result = usecase.execute(agent, lb="  Sidekick  ")
        assert result['entity'].lb == "Sidekick"

    def test_empty_custom_label_falls_back_to_suffix(self, usecase, project):
        agent = Agent(id=project.get_next_id('agent'), lb="Hero")
        project.agent.append(agent)
        result = usecase.execute(agent, lb="   ")
        assert result['entity'].lb == "Hero (copy)"

    def test_associations_not_copied(self, usecase, project_service, project):
        """TSC 31-10-2026: the copy does not inherit the agent-state
        associations of the source (same principle as component duplication:
        relations are not duplicated, RG024)."""
        agent = Agent(id=project.get_next_id('agent'), lb="Hero")
        project.agent.append(agent)
        nm = project.narrative_map[0]
        state = nm.state[0]  # initial state (RG031)
        assoc = AssociateAgentStateUseCase(project_service).execute(agent, state)
        assert assoc and assoc['success']
        assert len(nm.state_agent_rel) == 1

        result = usecase.execute(agent)
        assert result and result['success']
        copy = result['entity']
        # No association references the copy
        assert len(nm.state_agent_rel) == 1
        assert all(r.agent_id != copy.id for r in nm.state_agent_rel)

    def test_project_marked_modified(self, usecase, project_service, project):
        project_service.set_modified(False)
        agent = Agent(id=project.get_next_id('agent'), lb="Hero")
        project.agent.append(agent)
        usecase.execute(agent)
        assert project_service.is_modified

    def test_copy_json_round_trip(self, usecase, project):
        agent = Agent(id=project.get_next_id('agent'), lb="Hero",
                      typ="Object", note="n", content="c")
        project.agent.append(agent)
        copy = usecase.execute(agent)['entity']
        restored = Agent.from_dict(json.loads(json.dumps(copy.to_dict())))
        assert restored.id == copy.id
        assert restored.lb == copy.lb
        assert restored.typ == copy.typ
        assert restored.note == "n"
        assert restored.content == "c"


# ---------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------

class TestRefusals:
    def test_no_project(self):
        uc = DuplicateAgentUseCase(ProjectService())
        assert uc.execute(Agent(id=1, lb="A")) is None

    def test_agent_not_in_project_refused(self, usecase, project):
        orphan = Agent(id=999, lb="Orphan")
        assert usecase.execute(orphan) is None

    def test_non_agent_refused(self, usecase, project):
        class NotAnAgent:
            id = 1
        assert usecase.execute(NotAnAgent()) is None
