# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : component_dialog.py
# Version      : 1
# Date         : 10-15-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QPushButton, QHBoxLayout, QLabel)
from core.models.data_model import State, Event


class ComponentDialog(QDialog):
    """
    Component data edition dialog.

    Displays the editable attributes of a narrative map component
    (State or Event) and returns the values entered by the user.

    State: lb, typ, note
    Event: lb, note
    """

    STATE_TYPES = ["Initial", "Action", "Relation", "Final"]

    def __init__(self, entity, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.component_type = "State" if isinstance(entity, State) else "Event"
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle(f"Edit {self.component_type}")
        self.setMinimumWidth(350)
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.layout.addLayout(self.form)
        self._add_buttons()

    def _setup_content(self):
        # Label field
        self.lb_edit = QLineEdit()
        self.lb_edit.setText(getattr(self.entity, 'lb', ''))
        self.form.addRow("Label:", self.lb_edit)

        # Type field (State only)
        if self.component_type == "State":
            self.typ_combo = QComboBox()
            self.typ_combo.addItems(self.STATE_TYPES)
            current_typ = getattr(self.entity, 'typ', 'Action')
            index = self.typ_combo.findText(current_typ)
            if index >= 0:
                self.typ_combo.setCurrentIndex(index)
            self.form.addRow("Type:", self.typ_combo)

        # Note field
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        note = getattr(self.entity, 'note', None) or ""
        self.note_edit.setPlainText(note)
        self.form.addRow("Note:", self.note_edit)

        # Inline validation message (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
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
        """
        Return the values entered by the user.

        Returns:
            Dictionary with keys 'lb', 'typ' (State only) and 'note'
        """
        values = {
            'lb': self.lb_edit.text().strip(),
            'note': self.note_edit.toPlainText()
        }
        if self.component_type == "State":
            values['typ'] = self.typ_combo.currentText()
        return values
