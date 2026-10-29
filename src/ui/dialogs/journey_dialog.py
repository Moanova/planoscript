# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journey_dialog.py
# Version      : 1
# Date         : 10-29-2026
# Conception   : TSK22/TSK23, docs/conception/journey_attachment.md
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from core.models.data_model import Journey
from config.config_loader import get as _get_config
from ui.utils import theme


class JourneyDialog(QDialog):
    """Journey data edition dialog (FN023/FN024, TSK23).

    Displays the editable attributes of a journey and returns the
    values entered by the user.
    Journey: lb, note

    Works in both modes:
    - creation: entity is None, form prefilled with default_label
      (editable)
    - edition: entity is a Journey, form prefilled from the entity
    """

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)

    def __init__(self, entity=None, parent=None, default_label=None):
        super().__init__(parent)
        self.entity = entity
        self.default_label = default_label
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle("Edit Journey" if self.entity else "New Journey")
        self.setModal(True)
        self.setMinimumSize(525, 300)
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

        # Note field (compact area, summary notes - TSK20 convention)
        self.note_edit = QTextEdit()
        note = getattr(self.entity, 'note', None) or ""
        self.note_edit.setPlainText(note)
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
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
            Dictionary with keys 'lb' and 'note'
        """
        return {
            'lb': self.lb_edit.text().strip(),
            'note': self.note_edit.toPlainText()
        }
