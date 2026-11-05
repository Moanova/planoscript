# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : export_workspace.py
# Version      : 1
# Date         : 01-11-2026
# Content      : Export preview workspace (SU010/FN033, TSK33)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Export preview workspace (TSK33, SU010/FN033).

Third workspace ("Export" tab): a read-only reading preview of the current
narrative map, rendered as an HTML 4 subset in a QTextBrowser.

Decisions (docs/conception/export.md, TSK31):
- strictly read-only, no interaction on the content; links are inert
  (setOpenLinks(False)) — no click changes the journey filter or regenerates
  anything;
- the note of a component is shown as a tooltip on hover: QTextBrowser strips
  anchor titles, so note anchors ("#note-<kind>-<id>") are resolved through a
  note index (anchorAt + QToolTip.showText, pattern of the workspace nodes);
- refresh_preview() never marks the map nor the project as modified.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

from PySide6.QtWidgets import QTextBrowser, QToolTip

if TYPE_CHECKING:
    from core.models.data_model import NarrativeMap, Journey, Agent


class ExportWorkspace(QTextBrowser):
    """Read-only reading preview of the narrative map (Export tab)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenLinks(False)  # links are inert (TSK31 decision)
        self.setOpenExternalLinks(False)
        self._notes: Dict[str, str] = {}  # note anchor href -> note text
        self.setPlaceholderText("Open a project to preview its export.")

    def refresh_preview(self, narrative_map: 'NarrativeMap',
                        journey: Optional['Journey'] = None,
                        agents: Optional[List['Agent']] = None) -> None:
        """Regenerate the preview. Called on tab activation and on model change
        while the tab is active. Never marks the map/project as modified."""
        from core.services.export_service import ExportService
        self._notes = ExportService.build_note_index(narrative_map, agents)
        self.setHtml(ExportService.build_reading_text(narrative_map, journey, agents))

    def mouseMoveEvent(self, event) -> None:
        """Custom tooltip on note anchors (anchorAt + QToolTip)."""
        anchor = self.anchorAt(event.position().toPoint())
        if anchor and anchor.startswith("#note-"):
            note = self._notes.get(anchor)
            if note:
                QToolTip.showText(event.globalPosition().toPoint(), note)
                return
        QToolTip.hideText()
        super().mouseMoveEvent(event)
