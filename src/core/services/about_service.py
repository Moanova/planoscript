# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : about_service.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
import json
import os

class AboutService:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def get_about_info(self) -> dict:
        config_path = os.path.join(self.BASE_DIR, "config", "about.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "title": "Planoscript",
                "version": "0.1.0-alpha",
                "year": "AA-MM-AAAA",
                "author": "TSC",
                "built_by": "Mistral Vibe"
            }
