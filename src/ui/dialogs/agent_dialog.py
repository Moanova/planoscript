# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : agent_dialog.py
# Version      : 1
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QPushButton, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from core.models.data_model import Agent
from ui.utils import theme


class AgentDialog(QDialog):
    """Agent data edition dialog (FN031).

    Displays the editable attributes of a project agent and returns the
    values entered by the user.
    Agent: lb, typ, note

    Works in both modes:
    - creation: entity is None, form prefilled with default_label
      (editable), type defaults to "Subject"
    - edition: entity is an Agent, form prefilled from the entity
    """

    AGENT_TYPES = ["Subject", "Object"]

    def __init__(self, entity=None, parent=None, default_label=None):
        super().__init__(parent)
        self.entity = entity
        # TSK13 review: default label in creation mode, like the state
        # and event creation ("State {id}" / "Event {id}")
        self.default_label = default_label
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle("Edit Agent" if self.entity else "New Agent")
        self.setModal(True)
        self.setMinimumSize(525, 420)
        self.layout = QVBoxLayout(self)
        # Dark theme (charter 98)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.layout.addLayout(self.form, stretch=1)
        self.layout.setAlignment(self.form, Qt.AlignTop)
        self._add_buttons()

    def _setup_content(self):
        # Label field
        self.lb_edit = QLineEdit()
        if self.entity is not None:
            self.lb_edit.setText(getattr(self.entity, 'lb', ''))
        elif self.default_label:
            self.lb_edit.setText(self.default_label)
        self.form.addRow("Label:", self.lb_edit)

        # Type field
        self.typ_combo = QComboBox()
        self.typ_combo.addItems(self.AGENT_TYPES)
        entity_typ = getattr(self.entity, 'typ', 'Subject')
        index = self.typ_combo.findText(entity_typ)
        if index >= 0:
            self.typ_combo.setCurrentIndex(index)
        self.form.addRow("Type:", self.typ_combo)

        # Note field
        self.note_edit = QTextEdit()
        note = getattr(self.entity, 'note', None) or ""
        self.note_edit.setPlainText(note)
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.form.addRow("Note:", self.note_edit)

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
        if not self.get_values()['lb']:
            self.error_label.setText("Label cannot be empty")
            return
        self.accept()

    def get_values(self):
        """Return the values entered by the user.

        Returns:
            Dictionary with keys 'lb', 'typ' and 'note'
        """
        return {
            'lb': self.lb_edit.text().strip(),
            'typ': self.typ_combo.currentText(),
            'note': self.note_edit.toPlainText()
        }
