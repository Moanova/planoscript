# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : update_component_usecase.py
# Version      : 1
# Date         : 10-15-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Use Case for updating the data of a narrative map component (State or Event).

This use case handles the modification of business entity attributes and
the project modification flag, but DOES NOT handle any Qt graphic objects.

Responsibilities:
- Validate the new attribute values (label, type, note)
- Update the business entity (State or Event) and its modification timestamp
- Mark the project as modified

Separation of responsibilities:
- This use case: business logic and data
- ComponentDialog: user input
- MainWindow: coordination between dialog, use case and workspace
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from core.models.data_model import State, Event
from core.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class UpdateComponentUseCase:
    """
    Use Case for updating the editable attributes of an existing component.

    Editable attributes:
    - State: lb, typ, note
    - Event: lb, note

    Attributes:
        project_service: Service for managing the current project
    """

    STATE_TYPES = ["Initial", "Action", "Relation", "Final"]

    def __init__(self, project_service: ProjectService):
        """
        Initialize the use case with the project service.

        Args:
            project_service: Service managing the current project
        """
        self.project_service = project_service

    def execute(self, entity: Any, lb: str, note: Optional[str] = None,
                typ: Optional[str] = None) -> Optional[Dict]:
        """
        Execute the update of a component's data.

        Args:
            entity: The business entity to update (State or Event)
            lb: New label value
            note: New note value (None keeps the current value)
            typ: New type value (State only; ignored for Event)

        Returns:
            Dictionary containing:
                - 'success': bool (True if update successful)
                - 'entity': the updated business entity
                - 'entity_id': ID of the entity
                - 'component_type': "State" or "Event"

            Or None if the update failed (invalid entity, empty label,
            invalid type, no project).
        """
        # 1. Check that a project is opened
        if not self.project_service or not self.project_service.current_project:
            logger.warning("No project opened")
            return None

        # 2. Check that the entity is an editable component
        if isinstance(entity, State):
            component_type = "State"
        elif isinstance(entity, Event):
            component_type = "Event"
        else:
            logger.warning("Entity is not an editable component: %s", type(entity))
            return None

        # 3. Validate the label
        new_lb = lb.strip() if isinstance(lb, str) else ""
        if not new_lb:
            logger.warning("Update refused: empty label for %s %s",
                           component_type, entity.id)
            return None

        # 4. Validate the type (State only)
        new_typ = None
        if component_type == "State":
            new_typ = typ if typ is not None else entity.typ
            if new_typ not in self.STATE_TYPES:
                logger.warning("Update refused: invalid State.typ %s", typ)
                return None
            # RG061: the initial state type can never be modified
            if entity.typ == "Initial" and new_typ != "Initial":
                logger.warning("Update refused: initial state type cannot be modified (RG061)")
                return None
            # RG062: the "Initial" type is reserved for the initial state
            if entity.typ != "Initial" and new_typ == "Initial":
                logger.warning("Update refused: type 'Initial' is not selectable (RG062)")
                return None

        # 5. Update the entity attributes
        entity.lb = new_lb
        if note is not None:
            entity.note = note if note.strip() else None
        if component_type == "State":
            entity.typ = new_typ
        entity.modification_date_time = datetime.now()

        # 6. Mark project as modified
        self.project_service.set_modified(True)

        # 7. Return the updated data
        result = {
            'success': True,
            'entity': entity,
            'entity_id': entity.id,
            'component_type': component_type
        }
        logger.debug("Component updated (%s): %s", component_type,
                     entity.to_dict() if hasattr(entity, 'to_dict') else entity)
        return result
