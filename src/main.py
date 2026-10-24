# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : main.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe + TSC
# ---------------------------------------------------------------------
import logging
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from config.config_loader import get
from ui.utils.theme import APP_STYLESHEET
from ui.main_window import MainWindow

# Logging configuration driven by config.json ("log_level").
# "DEBUG" -> diagnostic logs are shown ; "WARNING" -> masked (default).
_log_level_name = get("log_level", "WARNING")
logging.basicConfig(
    level=getattr(logging, _log_level_name, logging.WARNING),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

APP_KEY = "planoscript-single-instance"

app = QApplication(sys.argv)

# Dark theme (charter 98): application-wide stylesheet for the widgets
# outside the themed windows (message boxes, orphan popup menus)
app.setStyleSheet(APP_STYLESHEET)

# Single-instance guard: if another instance is already running, exit silently.
socket = QLocalSocket()
socket.connectToServer(APP_KEY)
if socket.waitForConnected(200):
    socket.close()
    sys.exit(0)

# Clean up any socket residue from a previous crash, then become the server.
QLocalServer.removeServer(APP_KEY)
server = QLocalServer()
server.listen(APP_KEY)

window = MainWindow()
window.show()
exit_code = app.exec()
server.close()
sys.exit(exit_code)
