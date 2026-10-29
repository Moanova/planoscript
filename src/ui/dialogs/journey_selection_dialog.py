# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_selection_dialog.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK23
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
)

from ui.utils import theme


class JourneySelectionDialog(QDialog):
    """Journey selection dialog (TSK23 review, FN024).

    Lists the journeys of the narrative map and lets the user:
    - "Ok": edit the selected journey (Ok disabled until a journey is
      selected);
    - "New...": create a new journey, then come back to this dialog;
    - "Delete": delete the selected journey (stub until TSK25);
    - "Cancel": close.

    Use get_action() after exec() to know which button was used:
    "ok", "new", "delete", or None (cancel).
    """

    def __init__(self, journeys, parent=None):
        super().__init__(parent)
        self._journeys = list(journeys)
        self._action = None
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        self.setWindowTitle("Select Journey")
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout(self)
        # Dark theme (charter 98)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._selection_changed)
        self.layout.addWidget(self.list_widget, stretch=1)

        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New...")
        self.new_button.clicked.connect(self._on_new)
        self.new_button.setFixedWidth(100)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setFixedWidth(100)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self._on_ok)
        self.ok_button.setFixedWidth(100)
        self.ok_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _refresh_list(self):
        self.list_widget.clear()
        for journey in self._journeys:
            self.list_widget.addItem(journey.lb)

    def _selection_changed(self, current_row):
        has_selection = 0 <= current_row < len(self._journeys)
        self.ok_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _on_ok(self):
        self._action = "ok"
        self.accept()

    def _on_new(self):
        self._action = "new"
        self.accept()

    def _on_delete(self):
        self._action = "delete"
        self.accept()

    def get_action(self):
        """Return the action chosen by the user: "ok", "new", "delete",
        or None when the dialog was cancelled."""
        return self._action

    def refresh(self, journeys, select_id=None):
        """Replace the journey list (after a creation) and keep the dialog open.

        A journey is always selected afterwards (TSK23 review): the row
        of select_id when given (typically the newly created journey),
        otherwise the first row.
        """
        self._journeys = list(journeys)
        self._refresh_list()
        row = 0
        if select_id is not None:
            for i, j in enumerate(self._journeys):
                if j.id == select_id:
                    row = i
                    break
        self.list_widget.setCurrentRow(row)  # fires _selection_changed

    def get_selected_journey(self):
        """Return the selected Journey, or None if there is no selection."""
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._journeys):
            return self._journeys[row]
        return None
