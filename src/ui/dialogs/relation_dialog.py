# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : relation_dialog.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK21 (SU004/FN021, RG027 revised), docs/conception/journey_attachment.md
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QTextEdit, QListWidget,
    QListWidgetItem, QPushButton, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from config.config_loader import get as _get_config
from ui.utils import theme


class RelationDialog(QDialog):
    """Relation edition dialog (TSK21, FN021 + RG027 revised).

    Edits a relation (arc State_to_event / Event_to_state, or agent-state
    association State_agent_rel):
    - "Note": free-text annotation (note field of the relation);
    - "Journeys": multiple-choice list of the journeys of the map; checked
      journeys are those whose Journey_node references the relation.

    get_values() returns {'note': str, 'journey_ids': [int]}.
    """

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)

    def __init__(self, relation, journeys, attached_journey_ids, parent=None):
        """Args:
        - relation: the relation entity (carries .note)
        - journeys: list of Journey entities of the narrative map
        - attached_journey_ids: ids of the journeys the relation is
          currently attached to (checked in the list)
        """
        super().__init__(parent)
        self.relation = relation
        self._journeys = list(journeys)
        self._attached = set(attached_journey_ids or [])
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle("Edit Relation")
        self.setModal(True)
        self.setMinimumSize(525, 360)
        self.layout = QVBoxLayout(self)
        # Dark theme (charter 98)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.layout.addLayout(self.form, stretch=1)
        self.layout.setAlignment(self.form, Qt.AlignTop)
        self._add_buttons()

    def _setup_content(self):
        # Note field (compact area, summary notes - TSK20 convention)
        self.note_edit = QTextEdit()
        note = getattr(self.relation, 'note', None) or ""
        self.note_edit.setPlainText(note)
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
        self.form.addRow("Note:", self.note_edit)

        # Journeys multiple-choice list (RG027 revised: on the relation)
        self.journeys_list = QListWidget()
        for journey in self._journeys:
            item = QListWidgetItem(journey.lb)
            item.setData(Qt.ItemDataRole.UserRole, journey.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked
                               if journey.id in self._attached
                               else Qt.CheckState.Unchecked)
            self.journeys_list.addItem(item)
        self.journeys_list.setMaximumHeight(120)
        self.form.addRow("Journeys:", self.journeys_list)

        # Inline validation message (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {theme.ERROR_COLOR};")
        self.layout.addWidget(self.error_label)

    def _add_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self._validate)
        ok_button.setFixedWidth(100)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _validate(self):
        if not self.get_journey_ids():
            self.error_label.setText("The relation must belong to at least one journey")
            return
        self.accept()

    def get_journey_ids(self):
        """Return the ids of the checked journeys."""
        ids = []
        for i in range(self.journeys_list.count()):
            item = self.journeys_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ids.append(item.data(Qt.ItemDataRole.UserRole))
        return ids

    def get_values(self):
        """Return the values entered by the user.

        Returns:
            Dictionary with keys 'note' (str) and 'journey_ids' ([int])
        """
        return {
            'note': self.note_edit.toPlainText(),
            'journey_ids': self.get_journey_ids()
        }
