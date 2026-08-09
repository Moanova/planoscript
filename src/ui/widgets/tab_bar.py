# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : tab_bar.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class TabBar(QWidget):
    """Barre des onglets pour basculer entre les vues"""

    tabChanged = Signal(int)  # Émet le nom de l'onglet sélectionné

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.setStyleSheet("""
            background-color: #f8f8f8;
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Créer les 3 onglets
        self.tabs = {}
        tab_configs = [
            ("Parcours", 0),
            ("Relations", 1),
            ("Chapitres", 2)
        ]

        for name, is_active in tab_configs:
            btn = QPushButton(name)
            btn.setCheckable(True)
            #btn.setChecked(is_active)
            btn.setFixedHeight(30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f8f8f8;
                    border: none;
                    border-bottom: 2px solid transparent;
                    font-family: Arial;
                    font-size: 9pt;
                    padding: 0 8px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    margin-right: 4px;
                }}
                QPushButton:hover {{
                    background-color: #e0e0e0;
                }}
                QPushButton:checked {{
                    background-color: #ffffff;
                    font-weight: bold;
                }}
            """)
            btn.setFixedWidth(200)
            btn.clicked.connect(lambda checked=False, idx=is_active: self._on_tab_clicked(idx))
            layout.addWidget(btn)
            self.tabs[name] = btn

        layout.addStretch()
        self.tabs["Parcours"].setChecked(True)


    def _on_tab_clicked(self, idx):
        """Active l'onglet par index et émet le signal"""
        for tab_idx, btn in enumerate(self.tabs.values()):
            btn.setChecked(tab_idx == idx)
        self.tabChanged.emit(idx)
