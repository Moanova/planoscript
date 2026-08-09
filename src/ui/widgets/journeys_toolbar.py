# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : journeys_toolbar.py
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
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon
from ui.utils.ui_utils import create_colored_icon
import os

class JourneysToolbar(QWidget):
    """Right toolbar for journeys/relations with SVG icons"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self):
        super().__init__()

        self.setFixedWidth(40)
        self.setStyleSheet("""
            background-color: #f8f8f8;
            border-left: 1px solid #ddd;
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.journey_button_group = QButtonGroup(self)
        self.journey_button_group.setExclusive(True)

        self.del_btn = None

        # Action buttons with icons
        self.add_btn = QPushButton()
        #self.add_btn.setIcon(QIcon(os.path.join(self.BASE_DIR, "asset", "icon", "addJourney.svg")))
        self.add_btn.setIcon(create_colored_icon(
            os.path.join(self.BASE_DIR, "asset", "icon", "addJourney.svg"),
            "#708090" 
        ))
        self.add_btn.setIconSize(QSize(24, 24))
        self.add_btn.setToolTip("Ajouter un nouveau parcours")
        self.add_btn.setStyleSheet(self.action_style)
        self.add_btn.setFixedSize(30, 30)
        layout.addWidget(self.add_btn)
        
        self.del_btn = QPushButton()
        #self.del_btn.setIcon(QIcon(os.path.join(self.BASE_DIR, "asset", "icon", "delJourney.svg")))
        self.del_btn.setIcon(create_colored_icon(
            os.path.join(self.BASE_DIR, "asset", "icon", "delJourney.svg"),
            "#708090"
        ))
        self.del_btn.setIconSize(QSize(24, 24))
        self.del_btn.setToolTip("Supprimer le parcours sélectionné")
        self.del_btn.setStyleSheet(self.action_style)
        #self.del_btn.setStyleSheet(action_style.replace("#4CAF50", "#f44336").replace("#45a049", "#d32f2f"))
        self.del_btn.setFixedSize(30, 30)
        layout.addWidget(self.del_btn)
        self.del_btn.clicked.connect(self.delete_selected_journey)
        self.del_btn.setEnabled(False)

        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(self.separator)
        
        self.add_journey_button("Parcours par défaut", is_default=True)
        
        layout.addStretch()

    def add_journey_button(self, journey_name, is_default=False):
        btn = QPushButton()
        btn.setIcon(create_colored_icon(
            os.path.join(self.BASE_DIR, "asset", "icon", "journey.svg"),
            "#708090"
        ))
        btn.setIconSize(QSize(24, 24))
        btn.setToolTip(journey_name)
        btn.setStyleSheet(self.journey_style)
        btn.setCheckable(True)
        btn.setFixedSize(30, 30)

        self.journey_button_group.addButton(btn)

        main_layout = self.layout()
        main_layout.insertWidget(main_layout.count(), btn)  # Insère avant le stretch

        self.update_delete_button_state()

        return btn

    def update_delete_button_state(self):
        """Active/désactive le bouton Supprimer en fonction du nombre de parcours"""
        journey_count = len(self.journey_button_group.buttons())
        self.del_btn.setEnabled(journey_count > 1)

        # Mise à jour du tooltip pour plus de clarté
        if journey_count <= 1:
            self.del_btn.setToolTip("Supprimer le parcours sélectionné : il doit toujours y avoir au moins un parcours par défaut")
        else:
            self.del_btn.setToolTip("Supprimer le parcours sélectionné")

    def delete_selected_journey(self):
        checked_button = self.journey_button_group.checkedButton()
        if checked_button:
            if len(self.journey_button_group.buttons()) > 1:
                checked_button.setParent(None)
                self.update_delete_button_state()
                buttons = self.journey_button_group.buttons()
                if buttons:
                    buttons[0].setChecked(True)

    def on_journey_selected(self, button):
        journey_name = button.toolTip()
        print(f"Parcours sélectionné: {journey_name}")
        # Ici, vous pouvez émettre un signal ou appeler une méthode pour
        # notifier le reste de l'application du changement de parcours

    def add_new_journey(self):
        # Logique pour générer un nom unique
        journey_count = len(self.journey_button_group.buttons())
        new_name = f"Parcours {journey_count + 1}"
        self.add_journey_button(new_name)

    @property
    def action_style(self):
        return """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ddd;
                color: #708090;
            }
            QPushButton:hover {
                color: #708090;
                background-color: #AABBCC;
                border: 1px solid #ddd;
            }
            QPushButton:pressed {
                color: #708090;
                background-color: #AABBCC;
                border: 2px solid #555555;
            }
        """

    @property
    def journey_style(self):
        return """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ddd;
                color: #708090;
            }
            QPushButton:hover {
                color: #708090;
                background-color: #AABBCC;
            }
            QPushButton:pressed {
                background-color: #AABBCC;
                border: 2px solid #888888;
            }
            QPushButton:checked {
                background-color: #AABBCC;
                color: #708090;
                border: 2px solid #555555;
            }
        """
