# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_matrix_order.py
# Content      : Unit tests for the agents view matrix order (TSK08, RG068)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the agents view matrix order logic.

Covers RG068 (pure logic, no Qt):
- Default order: creation order (ascending ID)
- Custom order respected; unknown IDs ignored; duplicates ignored
- Pinned entity (initial state) always first
- Entities missing from the saved order appended by ascending ID
- WorkspaceLayout round trip with custom orders (persistence)
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.models.view_model import WorkspaceLayout
from core.services.layout_service import resolve_matrix_order


class FakeEntity:
    """Minimal entity with an id attribute (Agent/State stand-in)."""

    def __init__(self, entity_id):
        self.id = entity_id


ENTITIES = [FakeEntity(i) for i in (1, 2, 3, 4, 5)]


class TestResolveMatrixOrder:

    def test_default_creation_order(self):
        result = resolve_matrix_order(ENTITIES, [])
        assert [e.id for e in result] == [1, 2, 3, 4, 5]

    def test_custom_order_respected(self):
        result = resolve_matrix_order(ENTITIES, [3, 1, 5])
        assert [e.id for e in result] == [3, 1, 5, 2, 4]

    def test_pinned_first(self):
        result = resolve_matrix_order(ENTITIES, [3, 1], pinned_first_id=4)
        assert result[0].id == 4
        assert [e.id for e in result] == [4, 3, 1, 2, 5]

    def test_pinned_not_included_in_saved_tail(self):
        # The pinned entity appears first even if also present later in
        # the saved order (no duplicate)
        result = resolve_matrix_order(ENTITIES, [2, 4, 1], pinned_first_id=4)
        assert [e.id for e in result] == [4, 2, 1, 3, 5]

    def test_unknown_ids_ignored(self):
        result = resolve_matrix_order(ENTITIES, [99, 3, 98])
        assert [e.id for e in result] == [3, 1, 2, 4, 5]

    def test_empty_entities(self):
        assert resolve_matrix_order([], [1, 2]) == []

    def test_new_entity_appended_at_end(self):
        # Simulate a newly created entity (id 6) not present in the
        # saved order: it appears at the end (RG068)
        entities = ENTITIES + [FakeEntity(6)]
        result = resolve_matrix_order(entities, [3, 1, 2, 4, 5])
        assert [e.id for e in result] == [3, 1, 2, 4, 5, 6]


class TestWorkspaceLayoutOrderPersistence:

    def test_round_trip_with_custom_orders(self):
        layout = WorkspaceLayout(
            narrative_map_id="map-1",
            agents_view_column_order=[2, 1, 3],
            agents_view_row_order=[5, 4])
        data = layout.to_dict()
        assert data['agents_view_column_order'] == [2, 1, 3]
        assert data['agents_view_row_order'] == [5, 4]

        restored = WorkspaceLayout.from_dict(data)
        assert restored.agents_view_column_order == [2, 1, 3]
        assert restored.agents_view_row_order == [5, 4]

    def test_round_trip_defaults_empty(self):
        layout = WorkspaceLayout(narrative_map_id="map-1")
        restored = WorkspaceLayout.from_dict(layout.to_dict())
        assert restored.agents_view_column_order == []
        assert restored.agents_view_row_order == []

    def test_legacy_layout_without_keys(self):
        # Layout files saved before TSK08 have no matrix order keys:
        # they must load with empty (creation) orders
        data = {'narrative_map_id': 'map-1', 'zoom_level': 1.0}
        restored = WorkspaceLayout.from_dict(data)
        assert restored.agents_view_column_order == []
        assert restored.agents_view_row_order == []
