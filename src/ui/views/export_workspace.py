# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : export_workspace.py
# Version      : 2
# Date         : 01-11-2026
# Content      : Export preview workspace (SU010/FN033, TSK33)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Export preview workspace (TSK33, SU010/FN033).

Third workspace ("Export" tab): a read-only reading preview of the current
narrative map, rendered as an HTML 4 subset in a QTextBrowser.

Decisions (docs/conception/export.md, TSK31):
- strictly read-only, no interaction on the content; links stay inert for the
  application state (no click changes the journey filter or regenerates
  anything) — but internal anchors (#journey-*, #agent-*) scroll to their
  section (passive navigation, RG041);
- the note of a component is shown as a tooltip on hover: QTextBrowser strips
  anchor titles, so note anchors ("#note-<kind>-<id>") are resolved through a
  note index (anchorAt + QToolTip.showText, pattern of the workspace nodes);
- refresh_preview() never marks the map nor the project as modified;
- dark theme like the other workspaces (charter 98): the app-wide stylesheet
  sets a white text color, so the browser background must be set explicitly
  to the workspace background (BG_PRIMARY), otherwise the text is invisible.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

from PySide6.QtWidgets import QTextBrowser, QToolTip
from PySide6.QtCore import QUrl

from config.config_loader import get as _get_config
from ui.utils import theme

if TYPE_CHECKING:
    from core.models.data_model import NarrativeMap, Journey, Agent

_LINK_COLOR = _get_config("link_color", "#E5C07B")

# The browser must carry the workspace background explicitly: the app-wide
# stylesheet (APP_STYLESHEET) already sets the white text color on every
# QWidget, and QTextBrowser's default background is white.
_EXPORT_BROWSER_STYLESHEET = f"""
    QTextBrowser {{
        background-color: {theme.BG_PRIMARY};
        color: {theme.TEXT_PRIMARY};
        border: none;
        font-family: "{theme.FONT_FAMILY}", system-ui, sans-serif;
        font-size: {theme.MENU_FONT_SIZE_PX}px;
    }}
    QTextBrowser a {{
        color: {_LINK_COLOR};
    }}
"""


class ExportWorkspace(QTextBrowser):
    """Read-only reading preview of the narrative map (Export tab)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(theme.SCROLLBAR_STYLESHEET + _EXPORT_BROWSER_STYLESHEET)
        self.setReadOnly(True)
        self.setOpenLinks(False)  # no link opens anything (TSK31 decision)
        self.setOpenExternalLinks(False)
        self.anchorClicked.connect(self._on_anchor_clicked)
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

    def _on_anchor_clicked(self, url: QUrl) -> None:
        """Internal anchors only: passive scroll to the target section
        (#journey-*, #agent-*). Note anchors (#note-*) are hover tooltips.
        Links stay inert for the application state (TSK31 decision)."""
        href = url.toString() if hasattr(url, "toString") else str(url)
        if href.startswith("#"):
            name = href[1:]
            if name.startswith(("journey-", "agent-")):
                self.scrollToAnchor(name)

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
