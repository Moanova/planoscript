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
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from ui.main_window import MainWindow

APP_KEY = "planoscript-single-instance"

app = QApplication(sys.argv)

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
