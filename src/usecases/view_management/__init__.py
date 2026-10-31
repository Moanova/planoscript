# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : __init__.py
# Version      : 1
# Date         : 23-07-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
"""
Package for workspace view use cases.

Contains the use cases related to manipulating the visual elements of the
workspace (creation, deletion, modification of nodes, connection
management, etc.).
"""
from usecases.view_management.create_node_usecase import CreateNodeUseCase
from usecases.view_management.duplicate_component_usecase import DuplicateComponentUseCase

__all__ = [
    "CreateNodeUseCase",
    "DuplicateComponentUseCase",
]
