# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : load_project_usecase.py
# Version      : 1
# Date         : 16-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService

class LoadProjectUseCase:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, file_path: str) -> bool:
        """Exécute le chargement du projet"""
        return self.project_service.load_project(file_path)
