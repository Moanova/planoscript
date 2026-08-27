# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : about_dialog.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

class AboutDialog(QDialog):
    """About Dialog'"""

    def __init__(self, about_service: AboutService, parent=None):
        super().__init__(parent)
        self.about_service = about_service
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle(self.about_service.get_about_info()["title"])
        self.setMinimumSize(400, 200)
        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        self._add_ok_button()

    def _setup_content(self):
        html = f"""
        <html><body style='font-family: Arial; font-size: 10pt;'>
        <h2>Planoscript</h2>
        <p><strong>Version</strong> {self.about_service.get_about_info()["version"]}</p>
        <p>{self.about_service.get_about_info()["year"]} (c){self.about_service.get_about_info()["author"]}</p>
        <p>{self.about_service.get_about_info()["built_by"]}</p>
        </body></html>
        """
        self.text_edit.setHtml(html)

    def _add_ok_button(self):
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedWidth(100)
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
