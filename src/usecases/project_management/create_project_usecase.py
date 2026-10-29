# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_project_usecase.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import Project, State, Journey
from core.services.project_service import ProjectService

class CreateProjectUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self) -> Project:
        project = self.project_service.create_project()
        self._initialize_narrative_map(project.narrative_map[0])
        return project

    def _initialize_narrative_map(self, narrative_map) -> None:
        """
        Apply RG031 and RG022 invariants to a newly created narrative map.

        RG022: a default journey is automatically created and activated.
        RG031: each narrative map has one and only one initial state, created
        automatically, present in all journeys, and never deletable.
        Extracted from execute() so it can be reused by future use cases
        (e.g. CreateNarrativeMapUseCase) without duplication.
        """
        # RG022: create the default journey and activate it
        default_journey = Journey(
            id=narrative_map.get_next_id('journey'),
            lb="Journey 1",
            default=True
        )
        narrative_map.journey.append(default_journey)
        narrative_map.active_journey_id = default_journey.id

        # RG031: create the initial state
        initial_state = State(
            id=narrative_map.get_next_id('state'),
            lb="Init State",
            typ="Initial"
        )
        narrative_map.state.append(initial_state)

