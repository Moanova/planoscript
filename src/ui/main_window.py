# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : main_window.py
# Version      : 1
# Date         : 01-06-2026
# Conception   : TSC
# Construction : Mistral Vibe
# ---------------------------------------------------------------------
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QLabel, QPushButton, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QFrame,
    QMessageBox, QStatusBar, QDialog, QTextEdit, QVBoxLayout, QPushButton,
    QGridLayout, QStackedWidget, QFileDialog
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon

import sys
import os

from ui.views.journey_workspace import JourneyWorkspace
from ui.widgets.tab_bar import TabBar
from ui.widgets.components_toolbar import ComponentsToolbar
from ui.widgets.journeys_toolbar import JourneysToolbar
from ui.widgets.info_bar import InfoBar
from ui.widgets.zoom_bar import ZoomBar
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.change_log_dialog import ChangeLogDialog
from core.services.project_service import ProjectService
from core.services.about_service import AboutService
from core.services.change_log_service import ChangeLogService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.file_management.load_project_usecase import LoadProjectUseCase
from usecases.file_management.save_project_usecase import SaveProjectUseCase
from usecases.file_management.quit_application_usecase import QuitApplicationUseCase
from usecases.view_management.create_node_usecase import CreateNodeUseCase
from usecases.view_management.create_relation_usecase import CreateRelationUseCase

class MainWindow(QMainWindow):
    """Main application window"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def __init__(self):
        super().__init__()

        self.current_narrative_map_index = 0

        # Track if project is opened or modified
        self.project_opened = False
        
        # Compteur de nœuds pour activer/désactiver le bouton Relation
        self.node_count = 0
        # Variables pour la création de relations
        self.relation_type = None
        self.waiting_for_source = False
        self.waiting_for_target = False
        self.source_node = None

        # Initialisation des dépendances
        self.project_service = ProjectService()
        self.create_project_usecase = CreateProjectUseCase(self.project_service)
        self.load_project_usecase = LoadProjectUseCase(self.project_service)
        self.save_project_usecase = SaveProjectUseCase(self.project_service)
        self.quit_usecase = QuitApplicationUseCase(self.project_service)
        self.about_service = AboutService()
        self.change_log_service = ChangeLogService()
        self.create_node_usecase = CreateNodeUseCase(self.project_service)
        self.create_relation_usecase = CreateRelationUseCase(self.project_service)

        self.setGeometry(100, 100, 1280, 720)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Menu bar
        self._create_menu_bar()

        # Middle section
        self.middle_section = QWidget()
        self.middle_layout = QGridLayout(self.middle_section)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.setSpacing(0)
        main_layout.addWidget(self.middle_section, 1)

        # Initialisation différée des éléments de workspace
        self.tab_bar = None
        self.stacked_workspaces = None
        self._show_welcome_message()

        # Bottom section
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        # Info bar (75%)
        self.info_bar = InfoBar()
        bottom_layout.addWidget(self.info_bar, 4)  # 75%
        
        # Zoom bar (25%)
        #self.zoom_bar = ZoomBar()
        #bottom_layout.addWidget(self.zoom_bar, 1)  # 25%
        
        main_layout.addLayout(bottom_layout)
        
        # Status bar
        #self.status_bar = QStatusBar()
        #self.setStatusBar(self.status_bar)
        self.setWindowTitle("Nouveau Projet - Planoscript")


    def _create_menu_bar(self):
        """Create menu bar based on menu-FR.yaml specification"""
        self.menu_actions = {}
        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #ffffff;
                font-family: Arial;
                font-size: 9pt;
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #404040;
                color: #ffffff;
            }
            QMenu {
                background-color: #ffffff;
                color: #000000;
                font-family: Arial;
                font-size: 9pt;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px 6px 10 px;
            }
            QMenu::item:selected {
                background-color: #404040;
                color: #ffffff;
            }
            QMenu::item:disabled {
                color: #808080;
            }
        """)
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("Fichiers")

        # RG007: Actions à désactiver sans projet
        self.menu_actions['new'] = self.file_menu.addAction("Nouveau projet...", self._create_project, "Ctrl+N")
        self.menu_actions['open'] = self.file_menu.addAction("Ouvrir...", self._open_project, "Ctrl+O")
        self.menu_actions['close'] = self.file_menu.addAction("Fermer", self._close_project, "Ctrl+W")
        self.menu_actions['save'] = self.file_menu.addAction("Enregistrer", self._save_project, "Ctrl+S")  # RG006
        self.menu_actions['save_as'] = self.file_menu.addAction("Enregistrer sous...", self._save_project_as, "Ctrl+Shift+S")
        self.menu_actions['export_map'] = self.file_menu.addAction("Exporter carte", lambda: None)
        self.file_menu.addSeparator()
        self.menu_actions['import_map'] = self.file_menu.addAction("Importer carte", lambda: None)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Projets récents...", lambda: None)
        self.file_menu.addSeparator()
        quit_action = self.file_menu.addAction("Quitter", self._on_quit, "Ctrl+Q")

        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Édition")
        self.menu_actions['undo'] = self.edit_menu.addAction("Annuler", lambda: None, "Ctrl+Z")
        self.menu_actions['redo'] = self.edit_menu.addAction("Rétablir", lambda: None, "Ctrl+Y")
        self.menu_actions['history'] = self.edit_menu.addAction("Historique", lambda: None)
        self.edit_menu.addSeparator()
        self.menu_actions['cut'] = self.edit_menu.addAction("Couper", lambda: None, "Ctrl+X")
        self.menu_actions['copy'] = self.edit_menu.addAction("Copier", lambda: None, "Ctrl+C")
        self.menu_actions['paste'] = self.edit_menu.addAction("Coller", lambda: None, "Ctrl+V")
        self.menu_actions['delete'] = self.edit_menu.addAction("Supprimer", lambda: None, "Del")

        # View menu
        self.view_menu = self.menu_bar.addMenu("Affichage")
        self.journey_menu = self.view_menu.addMenu("Parcours")
        self.menu_actions['list_journeys'] = self.journey_menu.addAction("ListeParcours", lambda: None)
        self.zoom_menu = self.view_menu.addMenu("Zoom")
        self.menu_actions['zoom_in'] = self.zoom_menu.addAction("Zoom avant", lambda: None, "Ctrl+=")
        self.menu_actions['zoom_out'] = self.zoom_menu.addAction("Zoom arrière", lambda: None, "Ctrl+-")
        self.menu_actions['zoom_reset'] = self.zoom_menu.addAction("Restaurer zoom", lambda: None, "Ctrl+0")

        # Project menu
        self.project_menu = self.menu_bar.addMenu("Projet")

        self.view_menu = self.project_menu.addMenu("Vue")
        self.menu_actions['view_journeys'] = self.view_menu.addAction("Parcours", lambda: None)
        self.menu_actions['view_relations'] = self.view_menu.addAction("Relations", lambda: None)
        self.menu_actions['view_chapters'] = self.view_menu.addAction("Chapitres", lambda: None)

        self.components_menu = self.project_menu.addMenu("Composants...")
        self.menu_actions['edit_time_ref'] = self.components_menu.addAction("Réf. temporelle", lambda: None)
        self.menu_actions['edit_space_ref'] = self.components_menu.addAction("Réf. spatiale", lambda: None)
        self.menu_actions['edit_agent'] = self.components_menu.addAction("Agent", lambda: None)
        self.menu_actions['edit_state'] = self.components_menu.addAction("État", lambda: None)
        self.menu_actions['edit_event'] = self.components_menu.addAction("Évènement", lambda: None)

        self.relations_menu = self.project_menu.addMenu("Relations...")
        self.menu_actions['link_agent_agent'] = self.relations_menu.addAction("Agent à agent", lambda: None)
        self.menu_actions['link_agent_state'] = self.relations_menu.addAction("Agent à état", lambda: None)
        self.menu_actions['link_state_event'] = self.relations_menu.addAction("État à évènement", lambda: None)

        # About menu (toujours activé)
        self.about_menu = self.menu_bar.addMenu("À propos")
        self.about_menu.addAction("Journal des changements", self._show_changelog)
        self.about_menu.addAction("À propos de Planoscript", self._show_about)

        # Initialise l'état du menu (aucun projet ouvert)
        self._update_menu_state()


    def _update_menu_state(self):
        """RG006 & RG007: Active/désactive les actions selon l'état du projet"""
        has_project = self.project_opened
        is_modified = self.project_service.is_modified

        # RG007: Désactive si aucun projet ouvert
        rg007_actions = [
            'close', 'save', 'save_as', 'export_map',
            'undo', 'redo', 'history', 'cut', 'copy', 'paste', 'delete',
            'zoom_in', 'zoom_out', 'zoom_reset'
        ]

        self.journey_menu.setEnabled(has_project)
        self.zoom_menu.setEnabled(has_project)
        self.view_menu.setEnabled(has_project)
        self.components_menu.setEnabled(has_project)
        self.relations_menu.setEnabled(has_project)

        for action_key in rg007_actions:
            if action_key in self.menu_actions:
                self.menu_actions[action_key].setEnabled(has_project)

        # RG006: "Enregistrer" désactivé si projet non modifié
        if 'save' in self.menu_actions:
            self.menu_actions['save'].setEnabled(has_project and is_modified)


    def _show_welcome_message(self):
        """Affiche le message d'accueil avec lien cliquable"""
        # Efface le contenu existant
        while self.middle_layout.count():
            item = self.middle_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)

        welcome_label = QLabel("""
            <h2>Construisez le plan de votre nouveau script.</h2>
            <p>Commencez par <a href="new" style="color: #0066cc; text-decoration: underline;">créer un nouveau projet</a> ou ouvrez un projet existant.</p>
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setOpenExternalLinks(False)
        welcome_label.setTextFormat(Qt.RichText)
        welcome_label.setWordWrap(True)
        welcome_label.linkActivated.connect(lambda link: self._create_project())
        welcome_label.setStyleSheet("QLabel { padding: 40px; }")

        welcome_layout.addWidget(welcome_label)
        self.middle_layout.addWidget(welcome_widget, 0, 0, 2, 3)  # Span toutes les cellules


    def _init_workspace(self):
        """Initialise l'espace de travail (appelé à l'ouverture d'un projet)"""
        # Clear existing layout
        self.middle_layout = self.middle_section.layout()
        while self.middle_layout.count():
            item = self.middle_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # TabBar
        self.tab_bar = TabBar()
        self.middle_layout.addWidget(self.tab_bar, 0, 1)
        self.tab_bar.tabChanged.connect(self._on_tab_changed)

        # Toolbars et workspaces
        self.components_toolbar = ComponentsToolbar()
        self.components_toolbar.component_selected.connect(self._on_component_selected)
        self.components_toolbar.relation_selected.connect(self._on_relation_selected)
        # Désactiver le bouton Relation par défaut (pas assez de nœuds)
        self.components_toolbar.set_relation_enabled(False)
        self.middle_layout.addWidget(self.components_toolbar, 1, 0)

        self.stacked_workspaces = QStackedWidget()
        self.workspace_0 = JourneyWorkspace(
          narrative_map=self.project_service.current_project.narrative_map[0]
        )
        self.workspace_1 = JourneyWorkspace()
        self.workspace_2 = JourneyWorkspace()
        self.stacked_workspaces.addWidget(self.workspace_0)
        self.stacked_workspaces.addWidget(self.workspace_1)
        self.stacked_workspaces.addWidget(self.workspace_2)
        self.middle_layout.addWidget(self.stacked_workspaces, 1, 1)

        self.journeys_toolbar = JourneysToolbar()
        self.middle_layout.addWidget(self.journeys_toolbar, 1, 2)

        self.middle_layout.setColumnStretch(1, 1)
        self.middle_layout.setRowStretch(1, 1)


    def _create_project(self):
        """Crée un nouveau projet"""
        self.create_project_usecase.execute()
        self._init_workspace()
        self.project_opened = True
        self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb}")
        self._update_menu_state()
        print(f"{self.project_service.current_project}")


    def _open_project(self):
        """Ouvre un projet depuis le système de fichiers"""
        default_dir = os.path.expanduser("~")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un projet",
            default_dir,
            "Fichiers projet Planoscript (*.json);;Tous les fichiers (*)"
        )

        if not file_path:
            return  # Annulé par l'utilisateur

        if self.load_project_usecase.execute(file_path):
            self._init_workspace()
            self.project_opened = True
            self.setWindowTitle(f"Planoscript : {os.path.basename(file_path)}")
            self._update_menu_state()
        else:
            QMessageBox.critical(
                self,
                "Erreur d'ouverture",
                f"Impossible de charger le fichier : {file_path}"
            )
        print(f"{self.project_service.current_project}")


    def _save_project(self):
        current_project = self.project_service.current_project

        if (current_project and current_project.file_path and
            os.path.exists(os.path.dirname(current_project.file_path))):
            return self._do_save(current_project.file_path)

        return self._save_project_as()


    def _save_project_as(self) -> bool:
        default_dir = os.path.expanduser("~")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer sous...",
            default_dir,
            "Fichiers projet Planoscript (*.json);;Tous les fichiers (*)"
        )

        if not file_path:
            return False

        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        return self._do_save(file_path)


    def _do_save(self, file_path: str) -> bool:
        """Exécute la sauvegarde et gère le résultat."""
        try:
            success = self.save_project_usecase.execute(file_path)
            if success:
                self.setWindowTitle(f"Planoscript : {os.path.basename(file_path)}")
            return success
        except Exception as e:
            QMessageBox.critical(self, "Erreur de sauvegarde", str(e))
            return False


    def _clear_project(self):
        """Nettoie le projet actuel et l'espace de travail"""
        # Nettoyer l'espace de travail
        while self.middle_layout.count():
            item = self.middle_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Réinitialiser les références
        self.tab_bar = None
        self.stacked_workspaces = None
        self.components_toolbar = None
        self.journeys_toolbar = None

        # Nettoyer le projet dans le service
        self.project_service._current_project = None
        self.project_service.set_modified(False)


    def _close_project(self) -> bool:
        """Fermer le projet actuel avec confirmation si non enregistré"""
        if not self.project_opened:
            return True

        # Vérifier si le projet est modifié (comme dans _handle_quit)
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Projet non enregistré",
                "Voulez-vous enregistrer avant de fermer ?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return False
            if reply == QMessageBox.Yes and not self._save_project():
                return False

        # Fermer le projet
        self._clear_project()
        self._show_welcome_message()
        self.project_opened = False
        self.setWindowTitle("Nouveau Projet - Planoscript")
        self._update_menu_state()
        return True


    def _show_changelog(self):
        ChangeLogDialog(self.change_log_service, self).exec()


    def _show_about(self):
        AboutDialog(self.about_service, self).exec()


    def _on_tab_changed(self, tab_index):
        """Gère le changement d'onglet"""
        self.stacked_workspaces.setCurrentIndex(tab_index)
        print(f"Onglet sélectionné: {tab_index}")


    def closeEvent(self, event):
        if self._handle_quit():
            event.accept()
        else:
            event.ignore()


    def _on_quit(self):
        if self._handle_quit():
            self.close()


    def _handle_quit(self) -> bool:
        """Gère l'UI et utilise le use case"""
        if not self.quit_usecase.should_ask_confirmation():
            return True

        reply = QMessageBox.question(
            self,
            "Projet non enregistré",
            "Voulez-vous enregistrer avant de quitter ?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        if reply == QMessageBox.Yes:
            return self._save_project()
        return reply == QMessageBox.No  # True si No, False si Cancel


    def on_narrative_map_selected(self, index: int):
        self.current_narrative_map_index = index
        # Rafraîchir les workspaces pour afficher la bonne carte
        self._refresh_workspaces()

    def _refresh_workspaces(self):
        """Rafraîchit tous les workspaces pour afficher la carte narrative courante."""
        if not hasattr(self, 'stacked_workspaces') or self.stacked_workspaces is None:
            return
        # Pour l'instant, seul workspace_0 est utilisé
        # Quand workspace_1 et workspace_2 seront implémentés, cette méthode sera complétée
        pass

    def _on_component_selected(self, component_type: str):
        """
        Callback appelé lorsqu'un composant est sélectionné dans la toolbar.
        """
        narrative_map = self.project_service.current_project.narrative_map[
            self.current_narrative_map_index
        ]

        if not hasattr(self, 'stacked_workspaces') or self.stacked_workspaces is None:
            print("Aucun workspace initialisé")
            return

        # Obtenir le workspace actif
        current_workspace = self.stacked_workspaces.currentWidget()
        if not isinstance(current_workspace, JourneyWorkspace):
            print("Le widget actif n'est pas un JourneyWorkspace")
            return

        # Position par défaut (centre visible de la vue)
        scene_rect = current_workspace.sceneRect()
        viewport_rect = current_workspace.viewport().rect()
        map_to_scene = current_workspace.mapToScene

        # Calculer le centre visible
        center_x = viewport_rect.width() / 2
        center_y = viewport_rect.height() / 2
        scene_pos = current_workspace.mapToScene(center_x, center_y)

        # Créer le nœud au centre visible
        result = self.create_node_usecase.execute(
            component_type=component_type,
            x=scene_pos.x(),
            y=scene_pos.y(),
            narrative_map = narrative_map
        )
        if result and result.get('success'):
            current_workspace.create_node_from_data(result)
            self._update_menu_state()
            
            # Incrémenter le compteur de nœuds et mettre à jour le bouton Relation
            self.node_count += 1
            self.components_toolbar.set_relation_enabled(self.node_count >= 2)

    def on_narrative_map_selected(self, index: int):
        self.current_narrative_map_index = index
        # Rafraîchir les workspaces pour afficher la bonne carte
        self._refresh_workspaces()

    def _refresh_workspaces(self):
        """Rafraîchit tous les workspaces pour afficher la carte narrative courante."""
        if not hasattr(self, 'stacked_workspaces') or self.stacked_workspaces is None:
            return
        # Pour l'instant, seul workspace_0 est utilisé
        # Quand workspace_1 et workspace_2 seront implémentés, cette méthode sera complétée
        pass

    def _on_relation_selected(self):
        """
        Callback appelé lorsqu'une relation est sélectionnée dans la toolbar.
        Affiche un menu pour choisir le type de relation.
        """
        if self.node_count < 2:
            self.info_bar.show_message("Il faut au moins 2 nœuds pour créer une relation")
            return

        # Créer un menu contextuel pour choisir le type de relation
        from PySide6.QtWidgets import QMenu, QCursor

        menu = QMenu(self)

        # Ajouter les types de relation
        menu.addAction("Agent à agent", lambda: self._start_relation_creation("Agent à agent"))
        menu.addAction("Agent à état", lambda: self._start_relation_creation("Agent à état"))
        menu.addAction("Agent à évènement", lambda: self._start_relation_creation("Agent à évènement"))
        menu.addAction("État à évènement", lambda: self._start_relation_creation("État à évènement"))
        menu.addAction("Évènement à état", lambda: self._start_relation_creation("Évènement à état"))

        menu.exec(QCursor.pos())

    def _start_relation_creation(self, relation_type: str):
        """
        Active le mode création de relation.
        Stocke le type de relation et attend la sélection des nœuds.
        """
        self.relation_type = relation_type
        self.waiting_for_source = True
        self.waiting_for_target = False
        self.source_node = None
        self.info_bar.show_message(f"Cliquez sur le nœud source pour {relation_type}")

    def _on_node_selected_for_relation(self, node):
        """
        Callback appelé lorsqu'un nœud est sélectionné en mode création de relation.
        Gère la sélection source/cible et crée la relation.
        """
        if self.waiting_for_source:
            # Premier nœud sélectionné = source
            self.source_node = node
            self.waiting_for_source = False
            self.waiting_for_target = True
            self.info_bar.show_message(f"Cliquez sur le nœud cible pour {self.relation_type}")
        elif self.waiting_for_target:
            # Deuxième nœud sélectionné = cible
            self.waiting_for_target = False
            self._create_relation(self.source_node, node)
            self.source_node = None
            self.relation_type = None

    def _create_relation(self, source_node, target_node):
        """
        Crée une relation entre deux nœuds via le use case.
        """
        # Extraire les entités métiers des nœuds visuels
        source_entity = source_node.entity
        target_entity = target_node.entity

        # Exécuter le use case
        result = self.create_relation_usecase.execute(
            source_entity=source_entity,
            target_entity=target_entity,
            relation_type=self.relation_type
        )

        if result and result.get('success'):
            # Créer la connexion visuelle dans le workspace
            current_workspace = self.stacked_workspaces.currentWidget()
            if isinstance(current_workspace, JourneyWorkspace):
                current_workspace.create_connection_from_data(result)
            self.info_bar.show_message(f"Relation {self.relation_type} créée")
        else:
            self.info_bar.show_message("Erreur: impossible de créer la relation")
