# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : config_loader.py
# Version      : 1
# Date         : 2026-09-21
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Minimal configuration loader for Planoscript.

Loads src/config/config.json once at import time and exposes a simple
get(key, default) accessor. If the file is missing or a key is absent,
the provided default is returned, so the application always starts with
sensible values.
"""

import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

_config: dict = {}
try:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as _f:
        _config = json.load(_f)
except (FileNotFoundError, json.JSONDecodeError):
    _config = {}


def get(key: str, default=None):
    """Return the value for *key* from config.json, or *default* if absent."""
    return _config.get(key, default)
