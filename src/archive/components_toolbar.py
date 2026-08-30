# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : components_toolbar.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,  QFrame,
    QVBoxLayout, QPushButton, QButtonGroup
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF, Signal, QObject
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon
from ui.utils.ui_utils import create_colored_icon
import os

class ComponentsToolbar(QWidget):
    """Left toolbar for component types with SVG icons"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    component_selected = Signal(str)  # Émet le type de composant sélectionné
    relation_selected = Signal()  # Signal spécifique pour les relations

    def __init__(self):
        super().__init__()
        self.setFixedWidth(40)
        self.setStyleSheet("""
            background-color: #f8f8f8;
            border-right: 1px solid #ddd;
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Component buttons with SVG icons
        component_types = [
            ("Référence temporelle", "calendar.svg", "#AABBCC"),
            ("Référence spatiale", "map.svg", "#AABBCC"),
            ("Agent", "agent.svg", "#AABBCC"),
            ("État", "state.svg", "#AABBCC"),
            ("Évènement", "event.svg", "#AABBCC"),
            ("Relation", "relation.svg", "#AABBCC"),
        ]

        # Factory pour capturer correctement btn dans la closure
        def make_click_handler(button):
            return lambda: self.on_button_clicked(button)

        for name, icon_file, color in component_types:
            btn = QPushButton()
            icon_path = os.path.join(self.BASE_DIR, "asset", "icon", icon_file)
            btn.setIcon(create_colored_icon(icon_path, "#708090"))
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(30, 30)
            btn.setToolTip(name)
            btn.setCheckable(False)
            btn.clicked.connect(make_click_handler(btn))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    color: {color};
                }}
                QPushButton:hover {{
                    color: #FFFFFF;
                    background-color: {color};
                    border: 1px solid {color};
                }}
                QPushButton:pressed {{
                    color: #FFFFFF;
                    background-color: {color};
                    border: 2px solid #555555;
                }}
                QPushButton:checked {{
                    color: #FFFFFF;
                    background-color: {color};
                    border: 2px solid {color};
                }}
            """)
            layout.addWidget(btn)

        layout.addStretch()

    def on_button_clicked(self, button):
        component_type = button.toolTip()
        print(f"Sélectionné: {component_type}")
        
        # Émettre le signal approprié
        if component_type == "Relation":
            self.relation_selected.emit()
        else:
            self.component_selected.emit(component_type)


