# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : change_log_dialog.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from core.services.change_log_service import ChangeLogService

class ChangeLogDialog(QDialog):
    def __init__(self, change_log_service: ChangeLogService, parent=None):
        super().__init__(parent)
        self.change_log_service = change_log_service
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Change Log")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        # Zone de texte
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit.setStyleSheet("""
            QScrollBar:vertical {
                width: 8px; background: #f0f0f0; border-radius: 4px; margin: 0px; border: none;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0; border-radius: 4px; min-height: 20px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none; border: none; height: 0px; width: 0px;
            }
        """)
        layout.addWidget(self.text_edit)

        # Bouton OK
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self._load_changes()

    def _load_changes(self):
        changes = self.change_log_service.get_changes()

        html_content = """
        <html><body style='font-family: Arial; font-size: 10pt;'>
        <h2>Change Log</h2>
        """

        for change in changes:
            html_content += f"""
            <p><strong>{change.get('version', 'N/A')}</strong> - {change.get('build_date', 'Unknown Date')}</p>
            <p>{change.get('object', '')}</p>
            <p>{change.get('content', '').replace('\n', '<br>')}</p>
            <hr>
            """
        html_content += "</body></html>"

        self.text_edit.setHtml(html_content)
