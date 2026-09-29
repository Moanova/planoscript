# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : user_state_loader.py
# Version      : 1
# Date         : 2026-09-29
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
User state loader for Planoscript.

Manages src/config/user_state.json, a mutable store for runtime user
state such as the last project directory.  This is deliberately kept
separate from config.json, which holds immutable application defaults.

Exposes get(key, default) and set(key, value).  set() updates the
in-memory dict and persists to disk immediately.
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

_STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_state.json")

_state: dict = {}
try:
    with open(_STATE_PATH, "r", encoding="utf-8") as _f:
        _state = json.load(_f)
except (FileNotFoundError, json.JSONDecodeError):
    _state = {}


def get(key: str, default=None):
    """Return the value for *key* from user_state.json, or *default*."""
    return _state.get(key, default)


def set(key: str, value) -> None:
    """
    Update *key* in the user state and persist to disk immediately.

    On write failure, the in-memory value is still updated so the
    current session remains consistent, but the error is logged.
    """
    _state[key] = value
    try:
        with open(_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(_state, f, indent=2, ensure_ascii=False)
    except (IOError, OSError) as e:
        logger.error("Cannot persist user state: %s", e)
