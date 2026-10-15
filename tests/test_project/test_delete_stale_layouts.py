# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : test_delete_stale_layouts.py
# Content      : Unit tests for LayoutService.delete_stale_layouts
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Unit tests for LayoutService.delete_stale_layouts.

Covers the stale layout cleanup on save-over- Existing project:
- Layouts of the current narrative map(s) are kept
- Layouts of other narrative maps (left over from an overwritten
  project) are deleted
- Missing layouts directory is a no-op
- Empty keep list deletes everything
"""
import sys
import os

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.services.layout_service import LayoutService
from core.models.view_model import WorkspaceLayout


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path / "projects"


@pytest.fixture
def project_file(project_dir):
    project_dir.mkdir(parents=True)
    return str(project_dir / "proj.json")


def _save_layout(project_file, narrative_map_id):
    layout = WorkspaceLayout(narrative_map_id=narrative_map_id)
    assert LayoutService.save_workspace_layout(project_file, narrative_map_id, layout)


def _layout_names(project_file):
    layout_dir = LayoutService.get_layout_dir(project_file)
    return sorted(f.name for f in layout_dir.glob("*.json"))


def test_keeps_layout_of_current_map(project_file):
    _save_layout(project_file, "aaaa-1111")
    deleted = LayoutService.delete_stale_layouts(project_file, ["aaaa-1111"])
    assert deleted == 0
    assert _layout_names(project_file) == ["aaaa-1111.json"]


def test_deletes_stale_layouts_of_overwritten_project(project_file):
    # Project B saved first with map "bbbb-2222"
    _save_layout(project_file, "bbbb-2222")
    # Project A saved over the same file with map "aaaa-1111"
    _save_layout(project_file, "aaaa-1111")
    deleted = LayoutService.delete_stale_layouts(project_file, ["aaaa-1111"])
    assert deleted == 1
    assert _layout_names(project_file) == ["aaaa-1111.json"]


def test_keeps_multiple_maps(project_file):
    _save_layout(project_file, "aaaa-1111")
    _save_layout(project_file, "cccc-3333")
    deleted = LayoutService.delete_stale_layouts(project_file, ["aaaa-1111", "cccc-3333"])
    assert deleted == 0
    assert _layout_names(project_file) == ["aaaa-1111.json", "cccc-3333.json"]


def test_no_layouts_directory_is_noop(tmp_path):
    missing = str(tmp_path / "inexistant.json")
    assert LayoutService.delete_stale_layouts(missing, ["aaaa-1111"]) == 0


def test_empty_keep_list_deletes_everything(project_file):
    _save_layout(project_file, "bbbb-2222")
    _save_layout(project_file, "cccc-3333")
    deleted = LayoutService.delete_stale_layouts(project_file, [])
    assert deleted == 2
    assert _layout_names(project_file) == []


def test_empty_project_filepath_raises(project_file):
    with pytest.raises(ValueError):
        LayoutService.delete_stale_layouts("", ["aaaa-1111"])
