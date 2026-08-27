# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : about_service.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
import json
import os

class ChangeLogService:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def get_changes(self) -> list[dict]:
        """Récupère les changements depuis change_log.json"""
        changelog_path = os.path.join(self.BASE_DIR, "config", "change_log.json")

        try:
            with open(changelog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("changes", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
