# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agents_workspace.py
# Version      : 5
# Date         : 28-10-2026
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

Each card and each checkbox is centered in a 120x80 cell of the
background grid (TSC review 28-10-2026): the card margins are 20 px on
every side, the checkbox margins are 50 px horizontally and 30 px
vertically. The grid is drawn for the visible viewport only (journey
workspace pattern) over a scene that grows rightwards and downwards
only: the matrix stays anchored to the top-left corner.

Behavior preserved from the previous QTableWidget implementation
(TSK08/TSK09/TSK10): cell edition through the association use cases,
associationChanged signal, cross-view focus (RG067), manual reordering
of rows and columns persisted in the workspace layout (RG068), initial
state pinned to the first column (RG031).
"""

import logging

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame, QGraphicsItem, QGraphicsLineItem, QGraphicsRectItem,
    QGraphicsScene, QGraphicsView, QMenu, QVBoxLayout, QWidget
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
_CHECK_SIZE = _get_config("agents_view_checkbox_size", 20)
_STATE_COLOR = theme.color("state_color", theme.STATE_COLOR)
_AGENT_COLOR = theme.color("event_color", theme.EVENT_COLOR)
_FOCUS_COLOR = theme.color("focus_color", theme.FOCUS_COLOR)

# Matrix background grid (TSC review 28-10-2026): one 120x80 cell per
# matrix slot, the cards and checkboxes are centered in their cell.
# The grid is drawn for the visible viewport only (journey workspace
# pattern) and its lines are non-interactive (they must not block
# clicks on the cards and checkboxes).
_CELL_WIDTH = _get_config("agents_view_cell_width", 120)
_CELL_HEIGHT = _get_config("agents_view_cell_height", 80)
_GRID_COLOR = _get_config("grid_major_color", "#4A4A4A")


class _GridLineItem(QGraphicsLineItem):
    """Non-interactive grid line: painted normally but invisible to
    hit-testing (empty shape), so it never blocks clicks on the cards
    and checkboxes.

    boundingRect() is overridden to cover the painted line: with an
    empty shape(), the default boundingRect() collapses to an empty
    rect and Qt's scene indexing skips the item entirely when the scene
    rect is larger than the items bounding rect (the grid then
    disappears as soon as the view scrolls past the matrix content,
    unlike the journey workspace where the grid follows the viewport).
    """

    def shape(self):
        return QPainterPath()

    def boundingRect(self):
        # Cover the painted line (plus the pen width), so the scene
        # index keeps the item even though its shape is empty. The rect
        # is in item coordinates: the line runs from line().p1() to
        # line().p2(), the default QGraphicsLineItem rect is degenerate
        # for axis-aligned lines (zero width or height).
        line = self.line()
        left = min(line.x1(), line.x2())
        top = min(line.y1(), line.y2())
        right = max(line.x1(), line.x2())
        bottom = max(line.y1(), line.y2())
        return QRectF(left - 1, top - 1, right - left + 2, bottom - top + 2)

# Geometry (TSC review 28-10-2026): every matrix slot is a cell of the
# background grid. The state cards occupy the cells of the first row
# (columns), the agent cards the cells of the first column (rows), the
# checkboxes the remaining cells. Cards (80x40) are centered in their
# cell with a 20 px margin on every side; checkboxes (20x20) are
# centered with a 50 px horizontal and 30 px vertical margin. The
# top-left cell (agent column x state row) stays empty.
_CARD_WIDTH = MatrixCardItem.WIDTH
_CARD_HEIGHT = MatrixCardItem.HEIGHT
_CARD_OFFSET_X = (_CELL_WIDTH - _CARD_WIDTH) / 2   # 20 px
_CARD_OFFSET_Y = (_CELL_HEIGHT - _CARD_HEIGHT) / 2  # 20 px
_CHECK_OFFSET_X = (_CELL_WIDTH - _CHECK_SIZE) / 2   # 50 px
_CHECK_OFFSET_Y = (_CELL_HEIGHT - _CHECK_SIZE) / 2  # 30 px
_AGENTS_LEFT = _CARD_OFFSET_X  # agent cards column x
_STATES_TOP = _CARD_OFFSET_Y  # state cards row y
_CELLS_LEFT = _CELL_WIDTH  # checkboxes area x (after the agent column)
_CELLS_TOP = _CELL_HEIGHT  # checkboxes area y (after the state row)
# Minimal scene size: the scene grows rightwards/downwards only
_SCENE_MIN_SIZE = 4000


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

    # Emitted when a reorder attempt is rejected (initial state pinned,
    # RG068/RG031): the main window reports it in the info bar
    reorderRejected = Signal(str)  # message

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
        # Background grid lines (redrawn on refresh)
        self._grid_lines = []

        self.scene.setBackgroundBrush(QBrush(QColor(_BG_PRIMARY)))

        # Minimal scene size; grows rightwards/downwards only (TSC
        # review 28-10-2026: the matrix stays anchored to the top-left
        # corner, the workspace extends like the journey workspace)
        self.scene.setSceneRect(0, 0, _SCENE_MIN_SIZE, _SCENE_MIN_SIZE)
        self._draw_grid()

        # Redraw the grid for the visible viewport on scroll/resize
        # (journey workspace pattern)
        self.view.horizontalScrollBar().valueChanged.connect(
            self._draw_grid)
        self.view.verticalScrollBar().valueChanged.connect(
            self._draw_grid)

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
        self._grid_lines.clear()

        if not self.project_service or not self.project_service.current_project:
            self._agents = []
            self._states = []
            self._update_scene_rect()
            self._draw_grid()
            return

        self._resolve_entities()
        narrative_map = self.project_service.current_project.narrative_map[0]

        # State cards: one cell per state, along the first row
        # (columns), centered in their cell
        for column, state in enumerate(self._states):
            x = _CELLS_LEFT + column * _CELL_WIDTH + _CARD_OFFSET_X
            card = MatrixCardItem(state, 'state', _STATE_COLOR)
            card.setPos(x, _STATES_TOP)
            self.scene.addItem(card)
            self._state_cards[state.id] = card

        # Agent cards: one cell per agent, down the first column
        # (rows), centered in their cell
        for row, agent in enumerate(self._agents):
            y = _CELLS_TOP + row * _CELL_HEIGHT + _CARD_OFFSET_Y
            card = MatrixCardItem(agent, 'agent', _AGENT_COLOR)
            card.setPos(_AGENTS_LEFT, y)
            self.scene.addItem(card)
            self._agent_cards[agent.id] = card

        # Checkboxes at each intersection, centered in their cell
        for row, agent in enumerate(self._agents):
            for column, state in enumerate(self._states):
                x = _CELLS_LEFT + column * _CELL_WIDTH + _CHECK_OFFSET_X
                y = _CELLS_TOP + row * _CELL_HEIGHT + _CHECK_OFFSET_Y
                associated = AssociateAgentStateUseCase.find_association(
                    narrative_map, agent.id, state.id) is not None
                check = MatrixCheckItem(agent, state, associated)
                check.setPos(x, y)
                check.toggled = self._on_check_toggled
                self.scene.addItem(check)
                self._check_items[(agent.id, state.id)] = check

        self._update_scene_rect()
        self._draw_grid()

    def _update_scene_rect(self):
        """Grow the scene rightwards/downwards so the whole matrix is
        inside the scene rect (TSC review 28-10-2026: the matrix stays
        anchored to the top-left corner, the scene never shrinks below
        the minimal size nor extends leftwards/upwards)."""
        width = _CELL_WIDTH + max(len(self._states), 1) * _CELL_WIDTH
        height = _CELL_HEIGHT + max(len(self._agents), 1) * _CELL_HEIGHT
        self._expand_scene_right_down(width, height)

    def _expand_scene_right_down(self, right, bottom):
        """Extend the scene rect to include (right, bottom); never
        towards the left nor the top (the matrix is anchored to the
        top-left corner)."""
        rect = self.scene.sceneRect()
        new_right = max(rect.right(), right)
        new_bottom = max(rect.bottom(), bottom)
        if (new_right, new_bottom) != (rect.right(), rect.bottom()):
            self.scene.setSceneRect(0, 0, new_right, new_bottom)

    def _draw_grid(self, *args):
        """Draw the background grid for the visible viewport only
        (journey workspace pattern, TSC review 28-10-2026): one line
        every 120 px horizontally and 80 px vertically, from the scene
        origin (the cells frame the matrix slots exactly).

        The lines are non-interactive: their shape is empty so they
        never block clicks on the cards and checkboxes (the focus
        highlight band and the viewport's empty-area click still work).
        """
        for line in self._grid_lines:
            self.scene.removeItem(line)
        self._grid_lines.clear()

        pen = QPen(QColor(_GRID_COLOR))
        pen.setWidth(1)

        viewport_rect = self.view.viewport().rect()
        visible = self.view.mapToScene(viewport_rect).boundingRect()
        margin = 100
        visible.adjust(-margin, -margin, margin, margin)

        start_x = int(visible.left() - (visible.left() % _CELL_WIDTH))
        for x in range(start_x, int(visible.right()) + _CELL_WIDTH,
                       _CELL_WIDTH):
            line = _GridLineItem(x, visible.top(), x, visible.bottom())
            line.setPen(pen)
            line.setZValue(-2)
            self.scene.addItem(line)
            self._grid_lines.append(line)

        start_y = int(visible.top() - (visible.top() % _CELL_HEIGHT))
        for y in range(start_y, int(visible.bottom()) + _CELL_HEIGHT,
                       _CELL_HEIGHT):
            line = _GridLineItem(visible.left(), y, visible.right(), y)
            line.setPen(pen)
            line.setZValue(-2)
            self.scene.addItem(line)
            self._grid_lines.append(line)

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

        States are constrained to their cell row (horizontal move),
        agents to their cell column (vertical move): the card stays
        centered in its cell on the perpendicular axis.
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
        target_column = round(
            (scene_pos.x() - _CELLS_LEFT - _CARD_OFFSET_X) / _CELL_WIDTH)
        target_column = max(0, min(target_column, len(self._states) - 1))

        current_column = self._states.index(card.entity)
        # RG068/RG031: the initial state (first column) cannot be moved,
        # and no other state can take the first column
        if current_column == 0 or target_column == 0:
            if current_column == 0 and target_column != current_column:
                self.reorderRejected.emit(
                    f"State '{card.entity.lb}' is the initial state "
                    "and cannot be moved")
            self._relayout()
            return
        if target_column == current_column:
            self._relayout()
            return

        state = self._states.pop(current_column)
        self._states.insert(target_column, state)
        self._persist_visual_order()
        self._relayout()

    def _reorder_agents(self, card, scene_pos):
        target_row = round(
            (scene_pos.y() - _CELLS_TOP - _CARD_OFFSET_Y) / _CELL_HEIGHT)
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
        """Reposition all cards and checkboxes from the ordered lists
        (each item centered in its cell)."""
        for column, state in enumerate(self._states):
            card = self._state_cards.get(state.id)
            if card is not None:
                card.setPos(
                    _CELLS_LEFT + column * _CELL_WIDTH + _CARD_OFFSET_X,
                    _STATES_TOP)
        for row, agent in enumerate(self._agents):
            card = self._agent_cards.get(agent.id)
            if card is not None:
                card.setPos(
                    _AGENTS_LEFT,
                    _CELLS_TOP + row * _CELL_HEIGHT + _CARD_OFFSET_Y)
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
                _CELLS_LEFT + column * _CELL_WIDTH + _CHECK_OFFSET_X,
                _CELLS_TOP + row * _CELL_HEIGHT + _CHECK_OFFSET_Y)

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
        x = _CELLS_LEFT + column * _CELL_WIDTH

        if self._focus_highlight is None:
            self._focus_highlight = QGraphicsRectItem()
            self._focus_highlight.setPen(QPen(Qt.PenStyle.NoPen))
            self._focus_highlight.setZValue(-1)
            self.scene.addItem(self._focus_highlight)
        color = QColor(_FOCUS_COLOR)
        color.setAlpha(120)
        self._focus_highlight.setBrush(QBrush(color))
        top = 0
        bottom = _CELLS_TOP + len(self._agents) * _CELL_HEIGHT
        self._focus_highlight.setRect(
            QRectF(x, top, _CELL_WIDTH, bottom - top))

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

    def resizeEvent(self, event):
        """Redraw the grid for the new visible area (journey workspace
        pattern)."""
        super().resizeEvent(event)
        self._workspace._draw_grid()

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
