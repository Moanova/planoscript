# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : quit_application_usecase.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService

class QuitApplicationUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def should_ask_confirmation(self) -> bool:
        """Décide si une confirmation est nécessaire (logique pure)"""
        return self.project_service.is_modified
