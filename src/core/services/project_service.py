# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : project_service.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
import json
import logging
from uuid import uuid4
from datetime import datetime
from core.models.data_model import Project, NarrativeMap

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self):
        self._current_project: Project = None
        self._is_modified = False
        # Optional observer hook (TSK33): callable invoked on every
        # set_modified(True). Keeps core Qt-free: the UI layer registers a
        # callback here and re-emits it as a Qt signal.
        self.on_modified = None


    def create_project(self) -> Project:
        """Create an initialization project with an ID, LB, and a default narrative map."""
        # Create a default narrative map
        narrative_map = NarrativeMap(
            id=str(uuid4()),
            lb="Main narrative map",
            creation_date_time=datetime.now(),
            modification_date_time=None  # Mandatory field (no default value in the dataclass)
        )
        
        self._current_project = Project(
            id=str(uuid4()),
            lb="New Project",
            creation_date_time=datetime.now(),
            modification_date_time=None,
            narrative_map=[narrative_map]
        )
        self._is_modified = False
        return self._current_project


    def load_project(self, file_path: str) -> bool:
        """Loads a project from a JSON file
           Args:
               file_path: Path to the .json file
           Returns:
               bool: True if loading was successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_dict = json.load(f)
                self._current_project = Project.from_dict(project_dict)
                # TSK35/RG056 extended: drop journey nodes referencing deleted
                # relations (repairs projects saved by older versions), then
                # RG069: recompute legacy sequence_order values at load
                from core.services.arc_service import ArcService
                from core.services.journey_sequence_service import JourneySequenceService
                for narrative_map in self._current_project.narrative_map:
                    ArcService.prune_orphan_journey_nodes(narrative_map)
                    JourneySequenceService.recompute_all(narrative_map)
                self._current_project.file_path = file_path
                self._is_modified = False
                return True
        except (IOError, OSError, json.JSONDecodeError, KeyError) as e:
            logger.error("Loading error: %s", e)
            return False


    def save_project(self, file_path: str) -> bool:
        """Saves the project
           Args:
               file_path: Path to the destination file
           Returns:
               bool: True if the save was successful
        """
        if not self._current_project:
            return False

        # Prepare the dict with updated metadata without mutating the project
        now = datetime.now()
        project_dict = self._current_project.to_dict()
        project_dict['file_path'] = file_path
        project_dict['modification_date_time'] = now.isoformat()

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_dict, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            logger.error("Saving error: %s", e)
            return False

        # Update metadata only after successful write
        self._current_project.file_path = file_path
        self._current_project.modification_date_time = now
        self._is_modified = False
        return True


    @property
    def current_project(self) -> Project:
        return self._current_project

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    def set_modified(self, modified: bool) -> None:
        self._is_modified = modified
        if modified and callable(self.on_modified):
            self.on_modified()
