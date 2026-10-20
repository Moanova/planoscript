# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agents_workspace.py
# Version      : 3
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Agents workspace: agents x states matrix (TSK08/TSK09, SU009).

Second workspace dedicated to the agent-state associations. Displays
the agents x states matrix: one row per project agent, one column per
state of the current narrative map, a checked cell materializing each
existing association. Cell edition (TSK09): clicking a cell toggles
the association via the association use cases.

Column and row order follows RG068: creation order by default, manual
reordering allowed and persisted in the project graphical metadata
(WorkspaceLayout); the initial state is pinned to the first column and
cannot be moved.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

from ui.nodes.base_node import BaseNode
from usecases.agent_association.associate_agent_state_usecase import (
    AssociateAgentStateUseCase
)


class AgentsWorkspace(QWidget):
    """Agents x states matrix workspace (TSK08 display, TSK09 edition)."""

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

        self.matrix = QTableWidget()
        # Edition (TSK09): a single cellClicked handler toggles the
        # association — one edition point, no double signal
        self.matrix.setEditTriggers(QTableWidget.NoEditTriggers)
        self.matrix.cellClicked.connect(self._toggle_cell)
        # Cross-view navigation (TSK10): context menu on rows
        self.matrix.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.matrix.customContextMenuRequested.connect(self._show_context_menu)
        self._focused_state_id = None
        self.matrix.verticalHeader().setSectionsMovable(True)
        self.matrix.horizontalHeader().setSectionsMovable(True)
        self.matrix.horizontalHeader().sectionMoved.connect(self._column_moved)
        self.matrix.verticalHeader().sectionMoved.connect(self._row_moved)
        layout.addWidget(self.matrix, 1)

    def set_project(self, project_service, layout_data,
                    associate_usecase=None, dissociate_usecase=None):
        """Attach the current project, workspace layout data and the
        association use cases (TSK09)."""
        self.project_service = project_service
        self.layout_data = layout_data
        self.associate_usecase = associate_usecase
        self.dissociate_usecase = dissociate_usecase

    def refresh(self):
        """Rebuild the whole matrix from the current project data."""
        if not self.project_service or not self.project_service.current_project:
            self.matrix.setRowCount(0)
            self.matrix.setColumnCount(0)
            return

        project = self.project_service.current_project
        narrative_map = project.narrative_map[0]

        from core.services.layout_service import resolve_matrix_order

        # Rows: project agents (RG068: default creation order, custom
        # order allowed); no pinned entity
        saved_rows = (self.layout_data.agents_view_row_order
                      if self.layout_data else [])
        agents = resolve_matrix_order(project.agent, saved_rows)

        # Columns: map states (RG068: initial state pinned to the first
        # column, RG031)
        saved_columns = (self.layout_data.agents_view_column_order
                         if self.layout_data else [])
        initial_state = next(
            (s for s in narrative_map.state if s.typ == "Initial"), None)
        states = resolve_matrix_order(
            narrative_map.state, saved_columns,
            pinned_first_id=initial_state.id if initial_state else None)

        self.matrix.setRowCount(len(agents))
        self.matrix.setColumnCount(len(states))

        for row, agent in enumerate(agents):
            header = QTableWidgetItem(f"{agent.lb} ({agent.typ})")
            header.setData(Qt.ItemDataRole.UserRole, ('agent', agent.id))
            self.matrix.setVerticalHeaderItem(row, header)
        for column, state in enumerate(states):
            label = BaseNode.format_label_for_display(state.lb)
            header = QTableWidgetItem(f"{label} [{state.typ}]")
            header.setData(Qt.ItemDataRole.UserRole, ('state', state.id))
            self.matrix.setHorizontalHeaderItem(column, header)

        for row, agent in enumerate(agents):
            for column, state in enumerate(states):
                item = QTableWidgetItem()
                associated = AssociateAgentStateUseCase.find_association(
                    narrative_map, agent.id, state.id) is not None
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(
                    Qt.CheckState.Checked if associated
                    else Qt.CheckState.Unchecked)
                self.matrix.setItem(row, column, item)

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
        self._focused_state_id = state_id
        for column in range(self.matrix.columnCount()):
            data = self.matrix.horizontalHeaderItem(column).data(
                Qt.ItemDataRole.UserRole)
            if data and data[0] == 'state' and data[1] == state_id:
                self.matrix.setColumnHidden(column, False)
                # Tint the whole column cells
                for row in range(self.matrix.rowCount()):
                    item = self.matrix.item(row, column)
                    if item is not None:
                        item.setBackground(self._focus_color())
                # Scroll to the column (first cell)
                first_item = self.matrix.item(0, column)
                if first_item is not None:
                    self.matrix.scrollToItem(first_item)
                self._focused_column = column
                return
        self._focused_column = None

    def clear_focus(self) -> None:
        """
        Release the focus and restore the normal appearance (RG067).
        """
        if getattr(self, '_focused_state_id', None) is None:
            return
        for column in range(self.matrix.columnCount()):
            for row in range(self.matrix.rowCount()):
                item = self.matrix.item(row, column)
                if item is not None:
                    item.setBackground(None)
        self._focused_state_id = None
        self._focused_column = None

    def has_focus(self) -> bool:
        """
        Return True if a navigation focus is currently active.
        """
        return getattr(self, '_focused_state_id', None) is not None

    def _focus_color(self):
        """Background color of the focused column (light blue tint)."""
        from PySide6.QtGui import QColor
        return QColor(220, 235, 255)

    def _show_context_menu(self, pos):
        """
        Context menu of the matrix rows (TSK10): offers to show the
        states of the row agent in the journey view.
        """
        index = self.matrix.indexAt(pos)
        if not index.isValid():
            # RG067: clicking empty space releases the focus
            if self.has_focus():
                self.clear_focus()
            return
        row = index.row()
        row_header = self.matrix.verticalHeaderItem(row)
        if row_header is None:
            return
        data = row_header.data(Qt.ItemDataRole.UserRole)
        if not data or data[0] != 'agent':
            return
        agent = next(
            (a for a in self.project_service.current_project.agent
             if a.id == data[1]), None)
        if agent is None:
            return
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        action = menu.addAction("Show in journey view")
        chosen = menu.exec(self.matrix.viewport().mapToGlobal(pos))
        if chosen is action:
            self.focusAgentInJourneyViewRequested.emit(agent.id)

    def _entities_at(self, row, column):
        """Resolve the Agent and State of a matrix cell (TSK09).

        Returns:
            Tuple (agent, state), or (None, None) if the cell cannot be
            resolved (no project, unknown header data).
        """
        if not self.project_service or not self.project_service.current_project:
            return None, None
        project = self.project_service.current_project
        narrative_map = project.narrative_map[0]

        row_header = self.matrix.verticalHeaderItem(row)
        column_header = self.matrix.horizontalHeaderItem(column)
        if row_header is None or column_header is None:
            return None, None
        row_data = row_header.data(Qt.ItemDataRole.UserRole)
        column_data = column_header.data(Qt.ItemDataRole.UserRole)
        if not row_data or not column_data:
            return None, None

        agent = next(
            (a for a in project.agent if a.id == row_data[1]), None)
        state = next(
            (s for s in narrative_map.state if s.id == column_data[1]), None)
        return agent, state

    def _toggle_cell(self, row, column):
        """Toggle the association of the clicked cell (TSK09, SU008).

        Checking associates the row agent with the column state,
        unchecking dissociates them, via the association use cases. On
        use case failure the checkbox is restored to the data state.
        """
        agent, state = self._entities_at(row, column)
        if agent is None or state is None:
            return
        if self.associate_usecase is None or self.dissociate_usecase is None:
            return

        item = self.matrix.item(row, column)
        if item is None:
            return

        if item.checkState() == Qt.CheckState.Checked:
            # Currently checked: dissociate
            result = self.dissociate_usecase.execute(agent=agent, state=state)
            if result and result.get('success'):
                item.setCheckState(Qt.CheckState.Unchecked)
                self.associationChanged.emit(state.id, agent.lb, False)
            else:
                # Failure: keep the checkbox aligned with the data
                item.setCheckState(Qt.CheckState.Checked)
        else:
            # Currently unchecked: associate
            result = self.associate_usecase.execute(agent=agent, state=state)
            if result and result.get('success'):
                item.setCheckState(Qt.CheckState.Checked)
                self.associationChanged.emit(state.id, agent.lb, True)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

    def _column_moved(self, logical_index, old_visual_index, new_visual_index):
        """Record a manual column reorder (RG068), keeping the initial
        state pinned to the first column."""
        header = self.matrix.horizontalHeader()
        # RG068/RG031: the initial state (column 0) cannot be moved
        if old_visual_index == 0:
            header.moveSection(new_visual_index, 0)
            return
        if new_visual_index == 0:
            # A column was moved onto the pinned slot: push it back
            header.moveSection(0, 1)
        self._save_visual_order()

    def _row_moved(self, logical_index, old_visual_index, new_visual_index):
        """Record a manual row reorder (RG068)."""
        self._save_visual_order()

    def _save_visual_order(self):
        """Persist the current visual order into the workspace layout."""
        if not self.layout_data:
            return
        column_ids = []
        for column in range(self.matrix.columnCount()):
            data = self.matrix.horizontalHeaderItem(column).data(
                Qt.ItemDataRole.UserRole)
            if data and data[0] == 'state':
                column_ids.append(data[1])
        self.layout_data.agents_view_column_order = column_ids

        row_ids = []
        for row in range(self.matrix.rowCount()):
            data = self.matrix.verticalHeaderItem(row).data(
                Qt.ItemDataRole.UserRole)
            if data and data[0] == 'agent':
                row_ids.append(data[1])
        self.layout_data.agents_view_row_order = row_ids
