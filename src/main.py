# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : main.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe + TSC
# ---------------------------------------------------------------------
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
