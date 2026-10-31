# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : duplicate_component_usecase.py
# Version      : 1
# Date         : 31-10-2026
# Conception   : TSK28 / SU003, FN016
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Use Case for duplicating a narrative map component (State or Event) (FN016).

RG020: the copy gets a new unique id. The copy gets a distinct label
("{source.lb} (copy)" by default) and inherits the editable attributes
of the source (typ for State, note, content).

RG024/RG052 (revised, conception journey_attachment.md): the copy is an
isolated component at creation time, so no Journey_node is created for it;
journey attachment happens on relations, not on components.

RG062: the "Initial" type is reserved for the initial state of the map,
so the initial state cannot be duplicated.

This use case handles business data only; the EventsWorkspace creates the
visual node from the returned data (same contract as CreateNodeUseCase).
"""
import logging
from typing import Optional, Dict, Any

from core.models.data_model import State, Event, NarrativeMap
from core.models.view_model import NodeType
from core.services.project_service import ProjectService
from core.services.layout_service import LayoutService
from config.config_loader import get as _get_config

logger = logging.getLogger(__name__)

_GRID_MAJOR_SIZE = _get_config("grid_major_size", 80)


class DuplicateComponentUseCase:
    """
    Use Case for duplicating a State or Event of the current narrative map.

    Attributes:
        project_service: Service for managing the current project
    """

    COMPONENT_MAPPING = {
        "State": {
            'entity_class': State,
            'node_type': NodeType.STATE,
            'entity_type_key': 'state',
        },
        "Event": {
            'entity_class': Event,
            'node_type': NodeType.EVENT,
            'entity_type_key': 'event',
        },
    }

    def __init__(self, project_service: ProjectService):
        """
        Initialize the use case with the project service.

        Args:
            project_service: Service managing the current project
        """
        self.project_service = project_service

    def execute(
        self,
        entity: Any,
        source_layout=None,
        lb: Optional[str] = None,
        narrative_map: Optional[NarrativeMap] = None
    ) -> Optional[Dict]:
        """
        Duplicate a component (State or Event).

        Args:
            entity: The business entity to duplicate (must belong to the map)
            source_layout: Optional NodeLayout of the source node; the copy
                is placed one grid major step to the right of it
            lb: Label of the copy (defaults to "{entity.lb} (copy)")
            narrative_map: Target NarrativeMap (optional, uses the first)

        Returns:
            Dictionary with 'success', 'entity', 'entity_id', 'layout',
            'node_type', 'narrative_map_id', 'component_type'
            (same contract as CreateNodeUseCase).
            Or None if duplication failed (no project, invalid entity,
            initial state, unknown type).
        """
        # 1. Check that a project is opened
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        # 2. Use the provided NarrativeMap, or the first by default
        if narrative_map is None:
            project = self.project_service.current_project
            if not project.narrative_map:
                return None
            narrative_map = project.narrative_map[0]

        # 3. Determine the component type of the source entity
        if isinstance(entity, State):
            component_type = "State"
        elif isinstance(entity, Event):
            component_type = "Event"
        else:
            logger.warning("Entity is not a duplicable component: %s", type(entity))
            return None

        component_config = self.COMPONENT_MAPPING[component_type]
        entity_class = component_config['entity_class']
        node_type = component_config['node_type']
        entity_type_key = component_config['entity_type_key']

        # 4. The source must belong to the narrative map
        source_list = getattr(narrative_map, entity_type_key)
        if entity not in source_list:
            logger.warning("%s %s does not belong to the narrative map",
                           component_type, entity.id)
            return None

        # 5. RG062: the "Initial" type is reserved for the initial state
        if component_type == "State" and entity.typ == "Initial":
            logger.warning("Duplication refused: the initial state cannot be "
                           "duplicated (RG062)")
            return None

        # 6. Generate a unique ID and create the copy (RG020)
        entity_id = narrative_map.get_next_id(entity_type_key)
        copy_lb = (lb.strip() if isinstance(lb, str) and lb.strip()
                   else f"{entity.lb} (copy)")
        if component_type == "State":
            copy = entity_class(
                id=entity_id, lb=copy_lb, typ=entity.typ,
                note=entity.note, content=entity.content)
        else:
            copy = entity_class(
                id=entity_id, lb=copy_lb,
                note=entity.note, content=entity.content)
        source_list.append(copy)

        # 7. Create the NodeLayout next to the source (one grid major step
        #    to the right, snapped to the grid, RG040); RG044 overlap
        #    adjustment is applied by the workspace on display
        if source_layout is not None:
            x = LayoutService.snap_to_grid(source_layout.x + _GRID_MAJOR_SIZE)
            y = LayoutService.snap_to_grid(source_layout.y)
        else:
            x, y = 100.0, 100.0
        layout = LayoutService.create_node_layout(
            node_id=entity_id,
            node_type=node_type.value,
            x=x,
            y=y
        )

        # 8. RG024/RG052 revised: no Journey_node for an isolated component

        # 9. Mark project as modified
        self.project_service.set_modified(True)

        logger.info("Component duplicated (%s): %s (from %s %s)",
                    component_type, copy.to_dict(), component_type, entity.id)
        return {
            'success': True,
            'entity': copy,
            'entity_id': entity_id,
            'layout': layout,
            'node_type': node_type,
            'narrative_map_id': narrative_map.id,
            'component_type': component_type
        }
