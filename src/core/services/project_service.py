# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : project_servcice.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
import json
from uuid import uuid4
from datetime import datetime
from core.models.data_model import Project, NarrativeMap

class ProjectService:
    def __init__(self):
        self._current_project: Project = None
        self._is_modified = False


    def create_project(self) -> Project:
        """Crée un projet d'initialisation avec id, lb et une carte narrative par défaut"""
        # Créer une NarrativeMap par défaut
        narrative_map = NarrativeMap(
            id=str(uuid4()),
            lb="Carte narrative principale",
            creation_date_time=datetime.now(),
            modification_date_time=None  # Champ obligatoire (héritage de BaseEntity)
        )
        
        self._current_project = Project(
            id=str(uuid4()),
            lb="Nouveau projet",
            creation_date_time=datetime.now(),
            modification_date_time=None,
            narrative_map=[narrative_map]
        )
        self._is_modified = False
        return self._current_project


    def load_project(self, file_path: str) -> bool:
        """Charge un projet depuis un fichier JSON
        Args:
            file_path: Chemin du fichier .json
        Returns:
            bool: True si chargement réussi
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_dict = json.load(f)
                self._current_project = Project.from_dict(project_dict)
                self._current_project.file_path = file_path
                self._is_modified = False
                return True
        except (IOError, OSError, json.JSONDecodeError, KeyError) as e:
            print(f"Erreur lors du chargement: {e}")
            return False


    def save_project(self, file_path: str) -> bool:
        """Sauvegarde le projet (FN008 et FN009)
        Args:
            file_path: Chemin du fichier de destination
        Returns:
            bool: True si sauvegarde réussie
        """
        if not self._current_project:
            return False

        # Mise à jour des métadonnées
        self._current_project.file_path = file_path
        self._current_project.modification_date_time = datetime.now()

        project_dict = self._current_project.to_dict()

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_dict, f, indent=2, ensure_ascii=False)
            self._is_modified = False
            return True
        except (IOError, OSError) as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False


    @property
    def current_project(self) -> Project:
        return self._current_project

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    def set_modified(self, modified: bool) -> None:
        self._is_modified = modified
