# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : create_project_usecase.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import Project
from core.services.project_service import ProjectService

class CreateProjectUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self) -> Project:
        return self.project_service.create_project()
