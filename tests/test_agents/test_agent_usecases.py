# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_agent_usecases.py
# Content      : Unit tests for CreateAgentUseCase and UpdateAgentUseCase (SU008, FN031)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for agent management use cases.

Covers SU008/FN031 (agent creation and edition):
- Creation: default and provided values, unique project-level IDs,
  addition to project.agent, project marked as modified
- Invalid Agent.typ refused
- Empty label falls back to default label on creation, refused on update
- Update: lb, typ, note, content, modification_date_time, project modified
- Persistence round trip: agents survive save/load
- No project refused
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.data_model import Agent, Project
from core.services.project_service import ProjectService
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.update_agent_usecase import UpdateAgentUseCase


@pytest.fixture
def project_service():
    service = ProjectService()
    service.create_project()
    return service


@pytest.fixture
def create_usecase(project_service):
    return CreateAgentUseCase(project_service)


@pytest.fixture
def update_usecase(project_service):
    return UpdateAgentUseCase(project_service)


class TestCreateAgentUseCase:

    def test_create_with_defaults(self, project_service, create_usecase):
        result = create_usecase.execute()
        assert result is not None and result['success']
        agent = result['entity']
        assert isinstance(agent, Agent)
        assert agent.id == 1
        assert agent.lb == "Agent 1"
        assert agent.typ == "Subject"
        assert agent.note is None
        assert agent.content is None
        assert agent in project_service.current_project.agent

    def test_create_with_provided_values(self, project_service, create_usecase):
        result = create_usecase.execute(lb="Hero", typ="Object", note="A note",
                                        content="Narrative content")
        agent = result['entity']
        assert agent.lb == "Hero"
        assert agent.typ == "Object"
        assert agent.note == "A note"
        assert agent.content == "Narrative content"

    def test_sequential_unique_ids(self, project_service, create_usecase):
        first = create_usecase.execute()
        second = create_usecase.execute()
        assert first['entity_id'] == 1
        assert second['entity_id'] == 2

    def test_empty_label_falls_back_to_default(self, create_usecase):
        result = create_usecase.execute(lb="   ")
        assert result is not None
        assert result['entity'].lb == "Agent 1"

    def test_invalid_typ_refused(self, project_service, create_usecase):
        result = create_usecase.execute(typ="Creature")
        assert result is None
        assert project_service.current_project.agent == []

    def test_project_marked_modified(self, project_service, create_usecase):
        assert not project_service.is_modified
        create_usecase.execute()
        assert project_service.is_modified

    def test_no_project_refused(self):
        service = ProjectService()
        usecase = CreateAgentUseCase(service)
        assert usecase.execute() is None


class TestUpdateAgentUseCase:

    def _make_agent(self, create_usecase):
        result = create_usecase.execute(lb="Hero", typ="Subject", note="Old")
        return result['entity']

    def test_valid_update(self, project_service, create_usecase, update_usecase):
        agent = self._make_agent(create_usecase)
        project_service.set_modified(False)
        result = update_usecase.execute(
            entity=agent, lb="Villain", typ="Object", note="New note",
            content="New content")
        assert result is not None and result['success']
        assert agent.lb == "Villain"
        assert agent.typ == "Object"
        assert agent.note == "New note"
        assert agent.content == "New content"
        assert agent.modification_date_time is not None
        assert project_service.is_modified

    def test_empty_label_refused(self, create_usecase, update_usecase):
        agent = self._make_agent(create_usecase)
        assert update_usecase.execute(entity=agent, lb="   ") is None
        assert agent.lb == "Hero"

    def test_invalid_typ_refused(self, create_usecase, update_usecase):
        agent = self._make_agent(create_usecase)
        assert update_usecase.execute(entity=agent, lb="X", typ="Creature") is None
        assert agent.typ == "Subject"

    def test_non_agent_entity_refused(self, update_usecase):
        assert update_usecase.execute(entity="not an agent", lb="X") is None

    def test_note_none_keeps_current(self, create_usecase, update_usecase):
        agent = self._make_agent(create_usecase)
        update_usecase.execute(entity=agent, lb="Hero 2", note=None)
        assert agent.note == "Old"

    def test_content_none_keeps_current(self, create_usecase, update_usecase):
        agent = self._make_agent(create_usecase)
        agent.content = "Old content"
        update_usecase.execute(entity=agent, lb="Hero 2", content=None)
        assert agent.content == "Old content"

    def test_no_project_refused(self, create_usecase, update_usecase):
        agent = self._make_agent(create_usecase)
        empty_service = ProjectService()
        assert UpdateAgentUseCase(empty_service).execute(entity=agent, lb="X") is None


class TestAgentPersistence:

    def test_round_trip(self, project_service, create_usecase, update_usecase, tmp_path):
        create_usecase.execute(lb="Hero", typ="Subject", note="The hero")
        create_usecase.execute(lb="Sword", typ="Object")
        agent = project_service.current_project.agent[0]
        update_usecase.execute(entity=agent, lb="Villain", typ="Object", note="")

        file_path = str(tmp_path / "project.json")
        project_service.save_project(file_path)
        loaded = Project.from_dict(
            __import__("json").load(open(file_path)))

        assert len(loaded.agent) == 2
        first, second = loaded.agent
        assert (first.lb, first.typ, first.note) == ("Villain", "Object", None)
        assert (second.lb, second.typ) == ("Sword", "Object")
