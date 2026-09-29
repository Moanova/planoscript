# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_project_usecase.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import Project, State, Journey, State_node
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
        RG052: an isolated state implicitly creates a state node with
        from_event_id=0, state_id=<new state>, to_event_id=0.

        Extracted from execute() so it can be reused by future use cases
        (e.g. CreateNarrativeMapUseCase) without duplication.
        """
        # RG022: create the default journey
        default_journey = Journey(
            id=narrative_map.get_next_id('journey'),
            lb="Journey 1",
            default=True
        )
        narrative_map.journey.append(default_journey)

        # RG031: create the initial state
        initial_state = State(
            id=narrative_map.get_next_id('state'),
            lb="Init State",
            typ="Initial"
        )
        narrative_map.state.append(initial_state)

        # RG052: create the implicit state node for the isolated state
        state_node = State_node(
            id=narrative_map.get_next_id('state_node'),
            from_event_id=0,
            state_id=initial_state.id,
            to_event_id=0
        )
        narrative_map.state_node.append(state_node)
