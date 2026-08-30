# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : zoom_bar.py
# Version      : 1
# Date         : 01-06-2026
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,  QFrame,
    QVBoxLayout, QPushButton, QSlider
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon
import os

class ZoomBar(QWidget):
    """Bottom-right zoom bar"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.setStyleSheet("""
            background-color: #f0f0f0;
            border-top: 1px solid #ddd;
            border-left: 1px solid #ddd;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        layout.addStretch()
        
        # Zoom out button
        zoom_out = QPushButton("-")
        zoom_out.setFixedWidth(30)
        zoom_out.setStyleSheet("padding: 0px;")
        layout.addWidget(zoom_out)
        
        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 190)
        self.zoom_slider.setValue(100)
        #self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #ddd;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::groove:horizontal::before {
                position: absolute;
                left: 50%;
                width: 1px;
                height: 8px;
                background: #f00;
            }
            QSlider::handle:horizontal {
                background: #555;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -4px 0;
            }
            QSlider::sub-page:horizontal {
                background: #888;
                border-radius: 2px;
            }
        """)

        self.zoom_slider.setToolTip("100%")
        self.zoom_slider.valueChanged.connect(
            lambda v: self.zoom_slider.setToolTip(f"{v}%")
        )
        #self.zoom_slider.setMinimumWidth(100)
        layout.addWidget(self.zoom_slider)

        # Percentage Label
        #self.zoom_label = QLabel("100%")
        #self.zoom_label.setStyleSheet("font-weight: normal; font-size: 9pt; margin-left: 5px;")
        #layout.addWidget(self.zoom_label)
        
        # Zoom in button
        zoom_in = QPushButton("+")
        zoom_in.setFixedWidth(30)
        zoom_in.setStyleSheet("padding: 0px;")
        layout.addWidget(zoom_in)
        
        # Reset button
        #reset_btn = QPushButton("0")
        #reset_btn.setFixedWidth(30)
        #reset_btn.setStyleSheet("padding: 0px;")
        #layout.addWidget(reset_btn)
