# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : info_bar.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,  QFrame,
    QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon
import os

class InfoBar(QWidget):
    """Bottom-left information bar"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.setStyleSheet("""
            background-color: #f0f0f0;
            border-top: 1px solid #ddd;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        #self.info_label = QLabel("Sélectionnez un composant ou une relation")
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 10pt; color: #666;")
        layout.addWidget(self.info_label)
