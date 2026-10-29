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
    """Journey selection dialog (TSK23, FN024).

    Lists the journeys of the narrative map and returns the selected
    one. Used by the "Edit" entry of the "Project > Journeys..."
    submenu: the Ok button stays disabled until a journey is selected.
    """

    def __init__(self, journeys, parent=None):
        super().__init__(parent)
        self._journeys = list(journeys)
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
        button_layout.addStretch()
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.accept)
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
        self.ok_button.setEnabled(0 <= current_row < len(self._journeys))

    def get_selected_journey(self):
        """Return the selected Journey, or None if there is no selection."""
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._journeys):
            return self._journeys[row]
        return None
