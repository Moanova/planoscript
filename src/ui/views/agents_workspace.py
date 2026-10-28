# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agents_workspace.py
# Version      : 4
# Date         : 26-10-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Agents workspace: agents x states matrix (TSK15, SU009).

Second workspace dedicated to the agent-state associations. The matrix
is a QGraphicsView (like the journey workspace): one card per state
along the top (columns), one card per agent down the left side (rows),
and a checkbox at each intersection materializing the association.
Cards are drawn like the journey nodes (surface background, type-colored
outline, rounded corners); agents use the event tint (copper).

Behavior preserved from the previous QTableWidget implementation
(TSK08/TSK09/TSK10): cell edition through the association use cases,
associationChanged signal, cross-view focus (RG067), manual reordering
of rows and columns persisted in the workspace layout (RG068), initial
state pinned to the first column (RG031).
"""

import logging

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QMenu,
    QVBoxLayout, QWidget
)

from config.config_loader import get as _get_config
from core.services.layout_service import resolve_matrix_order
from ui.nodes.matrix_card import MatrixCardItem, MatrixCheckItem
from ui.utils import theme
from usecases.agent_association.associate_agent_state_usecase import (
    AssociateAgentStateUseCase
)

logger = logging.getLogger(__name__)

_BG_PRIMARY = _get_config("bg_primary", theme.BG_PRIMARY)
# Gap between the matrix components: horizontal for the states
# (columns), vertical for the agents (rows)
_COMPONENT_SPACING = _get_config("agents_view_component_spacing", 20)
_CHECK_SIZE = _get_config("agents_view_checkbox_size", 20)
_STATE_COLOR = theme.color("state_color", theme.STATE_COLOR)
_AGENT_COLOR = theme.color("event_color", theme.EVENT_COLOR)
_FOCUS_COLOR = theme.color("focus_color", theme.FOCUS_COLOR)

# Margins around the matrix content inside the scene
_SCENE_MARGIN = _COMPONENT_SPACING
# The state cards start after the agent column (one card width + the
# gap), the agent cards start after the state row (one card height +
# the gap): the first state is at x = card width + spacing from the
# left edge, the first agent at y = card height + spacing from the top
# edge (TSC review 26-10-2026: the header row/column stays visible and
# the agent cards no longer overlap the first state column checkboxes)
_CARD_WIDTH = MatrixCardItem.WIDTH
_CARD_HEIGHT = MatrixCardItem.HEIGHT
_AGENTS_LEFT = _SCENE_MARGIN  # agent cards column x
_STATES_TOP = _SCENE_MARGIN  # state cards row y
_CELLS_LEFT = _AGENTS_LEFT + _CARD_WIDTH + _COMPONENT_SPACING
_CELLS_TOP = _STATES_TOP + _CARD_HEIGHT + _COMPONENT_SPACING


class AgentsWorkspace(QWidget):
    """Agents x states matrix workspace (TSK15 graphical matrix).

    Public contract (unchanged since TSK08/TSK09/TSK10):
    set_project(), refresh(), set_focus(), clear_focus(), has_focus()
    and the signals associationChanged / focusAgentInJourneyViewRequested.
    """

    # Emitted after a cell edition changed the data (SU008): the journey
    # view refreshes the state badge and the info bar shows a message.
    associationChanged = Signal(int, str, bool)  # state_id, agent_lb, associated

    # Emitted when the user requests to show the states of an agent in
    # the journey view (TSK10, cross-view navigation)
    focusAgentInJourneyViewRequested = Signal(int)  # agent_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_service = None
        self.layout_data = None  # WorkspaceLayout of the current map
        self.associate_usecase = None
        self.dissociate_usecase = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = _MatrixGraphicsView(self)
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        layout.addWidget(self.view, 1)

        # Ordered entity lists (RG068); the visual order follows them
        self._agents = []   # Agent entities, display order (rows)
        self._states = []   # State entities, display order (columns)
        self._agent_cards = {}   # agent_id -> MatrixCardItem
        self._state_cards = {}   # state_id -> MatrixCardItem
        self._check_items = {}   # (agent_id, state_id) -> MatrixCheckItem
        self._focus_highlight = None  # QGraphicsRectItem column tint
        self._focused_state_id = None
        # Drag state (RG068 reordering)
        self._dragged_card = None
        self._drag_press_pos = None

        self.scene.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))

    def set_project(self, project_service, layout_data,
                    associate_usecase=None, dissociate_usecase=None):
        """Attach the current project, workspace layout data and the
        association use cases (TSK09)."""
        self.project_service = project_service
        self.layout_data = layout_data
        self.associate_usecase = associate_usecase
        self.dissociate_usecase = dissociate_usecase

    # ------------------------------------------------------------------
    # Data resolution (RG068)
    # ------------------------------------------------------------------

    def _resolve_entities(self):
        """Resolve the ordered agent and state lists (RG068).

        Rows: project agents, creation order by default, custom order
        allowed. Columns: map states, creation order by default, the
        initial state pinned to the first column (RG031).
        """
        project = self.project_service.current_project
        narrative_map = project.narrative_map[0]

        saved_rows = (self.layout_data.agents_view_row_order
                      if self.layout_data else [])
        self._agents = resolve_matrix_order(project.agent, saved_rows)

        saved_columns = (self.layout_data.agents_view_column_order
                         if self.layout_data else [])
        initial_state = next(
            (s for s in narrative_map.state if s.typ == "Initial"), None)
        self._states = resolve_matrix_order(
            narrative_map.state, saved_columns,
            pinned_first_id=initial_state.id if initial_state else None)

    # ------------------------------------------------------------------
    # Build / refresh
    # ------------------------------------------------------------------

    def refresh(self):
        """Rebuild the whole matrix from the current project data."""
        self.clear_focus()
        self.scene.clear()
        self._agent_cards.clear()
        self._state_cards.clear()
        self._check_items.clear()
        self._focus_highlight = None

        if not self.project_service or not self.project_service.current_project:
            self._agents = []
            self._states = []
            self._update_scene_rect()
            return

        self._resolve_entities()
        narrative_map = self.project_service.current_project.narrative_map[0]

        card_w = MatrixCardItem.WIDTH
        card_h = MatrixCardItem.HEIGHT
        spacing = _COMPONENT_SPACING

        # State cards: one column per state, along the top, starting
        # after the agent column (header row, TSC review 26-10-2026)
        for column, state in enumerate(self._states):
            x = _CELLS_LEFT + column * (card_w + spacing)
            card = MatrixCardItem(state, 'state', _STATE_COLOR)
            card.setPos(x, _STATES_TOP)
            self.scene.addItem(card)
            self._state_cards[state.id] = card

        # Agent cards: one row per agent, down the left side, starting
        # after the state row (header column)
        for row, agent in enumerate(self._agents):
            y = _CELLS_TOP + row * (card_h + spacing)
            card = MatrixCardItem(agent, 'agent', _AGENT_COLOR)
            card.setPos(_AGENTS_LEFT, y)
            self.scene.addItem(card)
            self._agent_cards[agent.id] = card

        # Checkboxes at each intersection
        for row, agent in enumerate(self._agents):
            for column, state in enumerate(self._states):
                x = _CELLS_LEFT + column * (card_w + spacing)
                y = _CELLS_TOP + row * (card_h + spacing)
                associated = AssociateAgentStateUseCase.find_association(
                    narrative_map, agent.id, state.id) is not None
                check = MatrixCheckItem(agent, state, associated)
                check.setPos(x + (card_w - _CHECK_SIZE) / 2,
                             y + (card_h - _CHECK_SIZE) / 2)
                check.toggled = self._on_check_toggled
                self.scene.addItem(check)
                self._check_items[(agent.id, state.id)] = check

        self._update_scene_rect()

    def _update_scene_rect(self):
        """Size the scene to the matrix content (plus margins)."""
        card_w = MatrixCardItem.WIDTH
        card_h = MatrixCardItem.HEIGHT
        spacing = _COMPONENT_SPACING
        # The matrix occupies the cells area plus the header row and
        # column, surrounded by the scene margin on every side
        width = (_SCENE_MARGIN + card_w + spacing
                 + max(len(self._states), 1) * card_w
                 + max(len(self._states) - 1, 0) * spacing
                 + _SCENE_MARGIN)
        height = (_SCENE_MARGIN + card_h + spacing
                  + max(len(self._agents), 1) * card_h
                  + max(len(self._agents) - 1, 0) * spacing
                  + _SCENE_MARGIN)
        self.scene.setSceneRect(0, 0, width, height)

    # ------------------------------------------------------------------
    # Cell edition (TSK09, SU008)
    # ------------------------------------------------------------------

    def _on_check_toggled(self, agent, state, new_checked):
        """Toggle the association of a checkbox cell (TSK09, SU008).

        Checking associates the agent with the state, unchecking
        dissociates them, via the association use cases. On use case
        failure the checkbox is restored to the data state.
        """
        if self.associate_usecase is None or self.dissociate_usecase is None:
            return

        check = self._check_items.get((agent.id, state.id))
        if check is None:
            return

        if new_checked:
            result = self.associate_usecase.execute(agent=agent, state=state)
            if result and result.get('success'):
                check.set_checked(True)
                self.associationChanged.emit(state.id, agent.lb, True)
            else:
                # Failure: restore the visual state to the data state
                check.set_checked(False)
        else:
            result = self.dissociate_usecase.execute(agent=agent, state=state)
            if result and result.get('success'):
                check.set_checked(False)
                self.associationChanged.emit(state.id, agent.lb, False)
            else:
                # Failure: restore the visual state to the data state
                check.set_checked(True)

    # ------------------------------------------------------------------
    # Reordering (RG068)
    # ------------------------------------------------------------------

    def _on_card_dragged(self, card, scene_pos):
        """Move the dragged card with the cursor (RG068 reordering).

        States are constrained to their row (horizontal move), agents
        to their column (vertical move).
        """
        if card.kind == 'state':
            card.setPos(scene_pos.x() - MatrixCardItem.WIDTH / 2,
                        _STATES_TOP)
        else:
            card.setPos(_AGENTS_LEFT,
                        scene_pos.y() - MatrixCardItem.HEIGHT / 2)

    def _on_card_released(self, card, scene_pos):
        """Apply a manual reorder on drag release (RG068).

        States reorder horizontally (columns), agents vertically (rows).
        The initial state stays pinned to the first column (RG031): a
        drop that would move it (or place another state first) is
        rejected and the layout snaps back. The new visual order is
        persisted into the workspace layout (RG068).
        """
        if card.kind == 'state':
            self._reorder_states(card, scene_pos)
        else:
            self._reorder_agents(card, scene_pos)
        self._dragged_card = None
        self._drag_press_pos = None

    def _reorder_states(self, card, scene_pos):
        card_w = MatrixCardItem.WIDTH
        spacing = _COMPONENT_SPACING
        target_column = round(
            (scene_pos.x() - _CELLS_LEFT) / (card_w + spacing))
        target_column = max(0, min(target_column, len(self._states) - 1))

        current_column = self._states.index(card.entity)
        # RG068/RG031: the initial state (first column) cannot be moved,
        # and no other state can take the first column
        if current_column == 0 or target_column == 0 \
                or target_column == current_column:
            self._relayout()
            return

        state = self._states.pop(current_column)
        self._states.insert(target_column, state)
        self._persist_visual_order()
        self._relayout()

    def _reorder_agents(self, card, scene_pos):
        card_h = MatrixCardItem.HEIGHT
        spacing = _COMPONENT_SPACING
        target_row = round(
            (scene_pos.y() - _CELLS_TOP) / (card_h + spacing))
        target_row = max(0, min(target_row, len(self._agents) - 1))

        current_row = self._agents.index(card.entity)
        if target_row == current_row:
            self._relayout()
            return

        agent = self._agents.pop(current_row)
        self._agents.insert(target_row, agent)
        self._persist_visual_order()
        self._relayout()

    def _persist_visual_order(self):
        """Persist the current visual order into the workspace layout
        (RG068: layout data, no modification flag)."""
        if not self.layout_data:
            return
        self.layout_data.agents_view_column_order = [
            s.id for s in self._states]
        self.layout_data.agents_view_row_order = [
            a.id for a in self._agents]

    def _relayout(self):
        """Reposition all cards and checkboxes from the ordered lists."""
        card_w = MatrixCardItem.WIDTH
        card_h = MatrixCardItem.HEIGHT
        spacing = _COMPONENT_SPACING

        for column, state in enumerate(self._states):
            card = self._state_cards.get(state.id)
            if card is not None:
                card.setPos(_CELLS_LEFT + column * (card_w + spacing),
                            _STATES_TOP)
        for row, agent in enumerate(self._agents):
            card = self._agent_cards.get(agent.id)
            if card is not None:
                card.setPos(_AGENTS_LEFT,
                            _CELLS_TOP + row * (card_h + spacing))
        for (agent_id, state_id), check in self._check_items.items():
            column = next(
                (i for i, s in enumerate(self._states) if s.id == state_id),
                None)
            row = next(
                (i for i, a in enumerate(self._agents) if a.id == agent_id),
                None)
            if column is None or row is None:
                continue
            check.setPos(
                _CELLS_LEFT + column * (card_w + spacing)
                + (card_w - _CHECK_SIZE) / 2,
                _CELLS_TOP + row * (card_h + spacing)
                + (card_h - _CHECK_SIZE) / 2)

        self._update_scene_rect()
        if self._focused_state_id is not None:
            self._apply_focus_highlight()

    # ------------------------------------------------------------------
    # Cross-view navigation focus (TSK10, RG067)
    # ------------------------------------------------------------------

    def set_focus(self, state_id) -> None:
        """
        Highlight the column of the given state and scroll to it
        (TSK10, RG067).

        Temporary visual state: no modification flag, no persistence
        (RG067).
        """
        self.clear_focus()
        if state_id not in self._state_cards:
            return
        self._focused_state_id = state_id
        self._apply_focus_highlight()
        card = self._state_cards[state_id]
        self.view.centerOn(card.sceneBoundingRect().center())

    def clear_focus(self) -> None:
        """
        Release the focus and restore the normal appearance (RG067).
        """
        if self._focus_highlight is not None:
            self.scene.removeItem(self._focus_highlight)
            self._focus_highlight = None
        for card in self._state_cards.values():
            card.set_highlighted(False)
        for check in self._check_items.values():
            check.set_highlighted(False)
        self._focused_state_id = None

    def has_focus(self) -> bool:
        """
        Return True if a navigation focus is currently active.
        """
        return self._focused_state_id is not None

    def _apply_focus_highlight(self):
        """Tint the focused state column: a translucent band behind the
        cards and checkboxes of the column, plus the raised surface on
        the state card."""
        if self._focused_state_id is None:
            return
        card = self._state_cards.get(self._focused_state_id)
        if card is None:
            return
        column = next(
            (i for i, s in enumerate(self._states)
             if s.id == self._focused_state_id), None)
        if column is None:
            return
        card_w = MatrixCardItem.WIDTH
        card_h = MatrixCardItem.HEIGHT
        spacing = _COMPONENT_SPACING
        x = _CELLS_LEFT + column * (card_w + spacing)

        if self._focus_highlight is None:
            self._focus_highlight = QGraphicsRectItem()
            self._focus_highlight.setPen(QPen(Qt.PenStyle.NoPen))
            self._focus_highlight.setZValue(-1)
            self.scene.addItem(self._focus_highlight)
        color = QColor(_FOCUS_COLOR)
        color.setAlpha(120)
        self._focus_highlight.setBrush(QBrush(color))
        top = _STATES_TOP
        bottom = (_CELLS_TOP
                  + len(self._agents) * (card_h + spacing))
        self._focus_highlight.setRect(
            QRectF(x - spacing / 2, top,
                   card_w + spacing, bottom - top))

        card.set_highlighted(True)
        for check in self._check_items.values():
            if check.state.id == self._focused_state_id:
                check.set_highlighted(True)

    # ------------------------------------------------------------------
    # Agent card context menu (TSK10)
    # ------------------------------------------------------------------

    def _on_agent_card_menu(self, card, global_pos):
        """Context menu of an agent card (TSK10): offers to show the
        states of the agent in the journey view."""
        if not self.project_service or not self.project_service.current_project:
            return
        project = self.project_service.current_project
        agent = next(
            (a for a in project.agent if a.id == card.entity.id), None)
        if agent is None:
            return
        menu = QMenu(self)
        # Dark theme for the context menu (charter 98)
        menu.setStyleSheet(theme.CONTEXT_MENU_STYLESHEET)
        action = menu.addAction("Show in journey view")
        chosen = menu.exec(global_pos)
        if chosen is action:
            self.focusAgentInJourneyViewRequested.emit(agent.id)

    # ------------------------------------------------------------------
    # Accessors used by the offscreen tests
    # ------------------------------------------------------------------

    def agent_count(self) -> int:
        """Number of agent rows currently displayed."""
        return len(self._agents)

    def state_count(self) -> int:
        """Number of state columns currently displayed."""
        return len(self._states)

    def agent_label(self, row: int) -> str:
        """Display label of the agent card of the given row."""
        return MatrixCardItem.display_label(self._agents[row].lb)

    def state_label(self, column: int) -> str:
        """Display label of the state card of the given column."""
        return MatrixCardItem.display_label(self._states[column].lb)

    def is_associated(self, row: int, column: int) -> bool:
        """Association state of the cell (row, column)."""
        agent = self._agents[row]
        state = self._states[column]
        check = self._check_items.get((agent.id, state.id))
        return check.is_checked() if check is not None else False

    def click_cell(self, row: int, column: int) -> None:
        """Simulate a click on the checkbox of the cell (row, column).

        Programmatic equivalent of a user click on the checkbox: goes
        through the same edition path as a real mouse click.
        """
        agent = self._agents[row]
        state = self._states[column]
        check = self._check_items.get((agent.id, state.id))
        if check is not None:
            self._on_check_toggled(agent, state, not check.is_checked())


class _MatrixGraphicsView(QGraphicsView):
    """Graphics view of the agents matrix.

    Swallows Qt's delayed automatic tooltip event (card tooltips are
    shown immediately by the items, AGENTS.md pattern). Empty-area
    clicks release the cross-view focus (RG067); left-button presses on
    cards start a drag (RG068 reordering); right-clicks on agent cards
    open the context menu (TSK10).
    """

    def __init__(self, workspace):
        super().__init__(workspace)
        self._workspace = workspace
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(theme.WORKSPACE_STYLESHEET)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        # The matrix is anchored to the top-left corner of the viewport,
        # not centered (TSC review 26-10-2026)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft
                          | Qt.AlignmentFlag.AlignTop)

    def viewportEvent(self, event):
        """Swallow Qt's delayed automatic tooltip event (see
        JourneyWorkspace.viewportEvent)."""
        if event.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(event)

    def _card_at(self, pos):
        """Return the MatrixCardItem at the viewport position, walking
        up the parent chain (the label is a child of the card)."""
        item = self.itemAt(pos)
        while item is not None:
            if isinstance(item, MatrixCardItem):
                return item
            item = item.parentItem()
        return None

    def mousePressEvent(self, event):
        """Left press on a card starts a drag (RG068); a press in the
        empty area releases the cross-view focus (RG067)."""
        if event.button() == Qt.MouseButton.LeftButton:
            card = self._card_at(event.pos())
            if card is not None:
                self._workspace._dragged_card = card
                self._workspace._drag_press_pos = self.mapToScene(event.pos())
                event.accept()
                return
            if self._workspace.has_focus():
                self._workspace.clear_focus()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        card = self._workspace._dragged_card
        if card is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._workspace._on_card_dragged(
                card, self.mapToScene(event.pos()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        card = self._workspace._dragged_card
        if card is not None:
            self._workspace._on_card_released(
                card, self.mapToScene(event.pos()))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Right-click on an agent card opens its context menu
        (TSK10)."""
        card = self._card_at(event.pos())
        if card is not None and card.kind == 'agent':
            self._workspace._on_agent_card_menu(card, event.globalPos())
        event.accept()
