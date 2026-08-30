# ---------------------------------------------------------------------
# Application  : Planoscript
# Script       : main_window.py
# Version      : 1
# Date         : 06-01-2026
# Design       : TSC
# Build        : Mistral Vibe + TSC
# ---------------------------------------------------------------------
# Version      : 2
# Date         : 30-08-2026
# Content      : Rework in progress
# Build        : TSC
# ---------------------------------------------------------------------
import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QLabel, QPushButton, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem, QFrame,
    QMessageBox, QStatusBar, QDialog, QTextEdit, QVBoxLayout, QPushButton,
    QGridLayout, QFileDialog
)
from PySide6.QtCore import Qt, QSize, QSizeF, QPointF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QIcon

from ui.views.journey_workspace import JourneyWorkspace
from ui.widgets.info_bar import InfoBar
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.change_log_dialog import ChangeLogDialog
from core.models.data_model import State, Event
from core.services.project_service import ProjectService
from core.services.about_service import AboutService
from core.services.change_log_service import ChangeLogService
from core.services.state_node_service import StateNodeService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.file_management.load_project_usecase import LoadProjectUseCase
from usecases.file_management.save_project_usecase import SaveProjectUseCase
from usecases.file_management.quit_application_usecase import QuitApplicationUseCase
from usecases.view_management.create_node_usecase import CreateNodeUseCase
from usecases.view_management.create_relation_usecase import CreateRelationUseCase

class MainWindow(QMainWindow):
    """Main Application Window"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ---------------------------------------------------------------------
    # Environment setup
    # ---------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        # MVP : one narrative map only per project
        self.current_narrative_map_index = 0

        # Boolean to define whether a project is opened or not
        self.project_opened = False

        # Node counter to enable or disable the "Relation" button (MVP : no control buttons, menu operations only)
        self.node_count = 0

        # Variables for relation creation
        self.relation_type = None
        self.waiting_for_source = False
        self.waiting_for_target = False
        self.source_node = None

        # Dependencies initialization
        self.project_service = ProjectService()
        self.create_project_usecase = CreateProjectUseCase(self.project_service)
        self.load_project_usecase = LoadProjectUseCase(self.project_service)
        self.save_project_usecase = SaveProjectUseCase(self.project_service)
        self.quit_usecase = QuitApplicationUseCase(self.project_service)
        self.create_node_usecase = CreateNodeUseCase(self.project_service)
        self.create_relation_usecase = CreateRelationUseCase(self.project_service)
        self.about_service = AboutService()
        self.change_log_service = ChangeLogService()

        # Dimensions of the application window
        self.setGeometry(100, 100, 1280, 720)

        # Central widget and layout creation
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Menu bar
        self._create_menu_bar()

        # Central space
        self.middle_section = QWidget()
        self.middle_layout = QGridLayout(self.middle_section)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.setSpacing(0)
        main_layout.addWidget(self.middle_section, 1)

        # Deferred initialization of workspace
        self.workspace = None
        self._show_welcome_message()

        # Bottom section
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        # Information bar (75%) --> MPV 100%, no zoom bar
        self.info_bar = InfoBar()
        ##bottom_layout.addWidget(self.info_bar, 4)  # 75%
        bottom_layout.addWidget(self.info_bar)
        
        # Zoom bar (25%)
        #self.zoom_bar = ZoomBar()
        #bottom_layout.addWidget(self.zoom_bar, 1)  # 25%
        
        main_layout.addLayout(bottom_layout)
        
        self.setWindowTitle("Planoscript : start your new project")


    def _create_menu_bar(self):
        """Creates the menu bar"""
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
        
        # Files menu
        self.file_menu = self.menu_bar.addMenu("Fichiers")

        # Actions to disable without project
        self.menu_actions['new'] = self.file_menu.addAction("New Project...", self._create_project, "Ctrl+N")
        self.menu_actions['open'] = self.file_menu.addAction("Open...", self._open_project, "Ctrl+O")
        self.menu_actions['close'] = self.file_menu.addAction("Close", self._close_project, "Ctrl+W")
        self.menu_actions['save'] = self.file_menu.addAction("Save", self._save_project, "Ctrl+S")  # RG006
        self.menu_actions['save_as'] = self.file_menu.addAction("Save as...", self._save_project_as, "Ctrl+Shift+S")
        self.menu_actions['export_map'] = self.file_menu.addAction("Export Map", lambda: None)
        self.file_menu.addSeparator()
        self.menu_actions['import_map'] = self.file_menu.addAction("Import Map", lambda: None)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Recent Projects...", lambda: None)
        self.file_menu.addSeparator()
        quit_action = self.file_menu.addAction("Quit", self._on_quit, "Ctrl+Q")

        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.menu_actions['undo'] = self.edit_menu.addAction("Undo", lambda: None, "Ctrl+Z")
        self.menu_actions['redo'] = self.edit_menu.addAction("Redo", lambda: None, "Ctrl+Y")
        self.menu_actions['history'] = self.edit_menu.addAction("History", lambda: None)
        self.edit_menu.addSeparator()
        self.menu_actions['cut'] = self.edit_menu.addAction("Cut", lambda: None, "Ctrl+X")
        self.menu_actions['copy'] = self.edit_menu.addAction("Copy", lambda: None, "Ctrl+C")
        self.menu_actions['paste'] = self.edit_menu.addAction("Paste", lambda: None, "Ctrl+V")
        self.menu_actions['delete'] = self.edit_menu.addAction("Delete", lambda: None, "Del")

        # Display menu
        self.view_menu = self.menu_bar.addMenu("Display")
        self.journey_menu = self.view_menu.addMenu("Journey")
        self.menu_actions['list_journeys'] = self.journey_menu.addAction("JourneyList", lambda: None)
        self.zoom_menu = self.view_menu.addMenu("Zoom")
        self.menu_actions['zoom_in'] = self.zoom_menu.addAction("Zoom in", lambda: None, "Ctrl+=")
        self.menu_actions['zoom_out'] = self.zoom_menu.addAction("Zoom out", lambda: None, "Ctrl+-")
        self.menu_actions['zoom_reset'] = self.zoom_menu.addAction("Reset", lambda: None, "Ctrl+0")

        # Project menu
        self.project_menu = self.menu_bar.addMenu("Project")

        # MVP : journey view only + the relation view will be reworked at a leter stage of development
        self.view_menu = self.project_menu.addMenu("View")
        self.menu_actions['view_journeys'] = self.view_menu.addAction("Journey", lambda: None)
        #self.menu_actions['view_relations'] = self.view_menu.addAction("Relations", lambda: None)
        #self.menu_actions['view_chapters'] = self.view_menu.addAction("Chapters", lambda: None)

        self.components_menu = self.project_menu.addMenu("Components...")
        self.components_menu.addAction("Agent", lambda: self._create_new_node("Agent"))
        self.components_menu.addAction("State", lambda: self._create_new_node("State"))
        self.components_menu.addAction("Event", lambda: self._create_new_node("Event"))

        self.relations_menu = self.project_menu.addMenu("Relations...")
        self.relations_menu.addAction("Link State and Event", lambda: self._start_state_event_relation_creation())

        # About menu (always enabled)
        self.about_menu = self.menu_bar.addMenu("About")
        self.about_menu.addAction("Change Log", self._show_changelog)
        self.about_menu.addAction("About Planoscript", self._show_about)

        # Initialize menu state (no project opened)
        self._update_menu_state()


    def _update_menu_state(self):
        """Enable or disable actions based on project state"""
        has_project = self.project_opened
        is_modified = self.project_service.is_modified

        # Disable if no project is opened
        actions = [
            'close', 'save', 'save_as', 'export_map',
            'undo', 'redo', 'history', 'cut', 'copy', 'paste', 'delete',
            'zoom_in', 'zoom_out', 'zoom_reset'
        ]

        self.journey_menu.setEnabled(has_project)
        self.zoom_menu.setEnabled(has_project)
        self.view_menu.setEnabled(has_project)
        self.components_menu.setEnabled(has_project)
        self.relations_menu.setEnabled(has_project)

        for action_key in actions:
            if action_key in self.menu_actions:
                self.menu_actions[action_key].setEnabled(has_project)

        # "Save" disabled if project not modified
        if 'save' in self.menu_actions:
            self.menu_actions['save'].setEnabled(has_project and is_modified)


    def _show_welcome_message(self):
        """Display welcome message with clickable link"""
        # Clear existing content
        while self.middle_layout.count():
            item = self.middle_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)

        welcome_label = QLabel("""
            <h2>Build the plan of your new script.</h2>
            <p>Start by <a href="new" style="color: #0066cc; text-decoration: underline;">creating a new project</a> or open an existing project.</p>
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setOpenExternalLinks(False)
        welcome_label.setTextFormat(Qt.RichText)
        welcome_label.setWordWrap(True)
        welcome_label.linkActivated.connect(lambda link: self._create_project())
        welcome_label.setStyleSheet("QLabel { padding: 40px; }")

        welcome_layout.addWidget(welcome_label)
        self.middle_layout.addWidget(welcome_widget, 0, 0, 2, 3)  # Span toutes les cellules


    # ---------------------------------------------------------------------
    # Project and application state management
    # ---------------------------------------------------------------------
    def _create_project(self):
        """Create a new project"""
        # Close current project with confirmation if needed
        if not self._close_project():
            return

        self.create_project_usecase.execute()
        self._init_workspace()
        self.project_opened = True
        self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb}")
        self._update_menu_state()

        # For debugging
        print(f"{self.project_service.current_project}")


    def _open_project(self):
        """Open a project from the file system"""
        default_dir = os.path.expanduser("~")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open a Project",
            default_dir,
            "Planoscript Project Files (*.json);;All Files (*)"
        )

        if not file_path:
            return  # Cancelled by user

        if self.load_project_usecase.execute(file_path):
            self._init_workspace()
            self.project_opened = True
            self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb} ({file_path})")
            self._update_menu_state()
        else:
            QMessageBox.critical(
                self,
                "Error opening the File",
                f"The File cannot be opened : {file_path}"
            )

        # For debugging
        print(f"{self.project_service.current_project}")


    def _init_workspace(self):
        """Initialize workspace with a single JourneyWorkspace."""
        # Clear existing layout
        self.middle_layout = self.middle_section.layout()
        while self.middle_layout.count():
            item = self.middle_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Single workspace (MVP : journey view only)
        self.workspace = JourneyWorkspace(
            narrative_map=self.project_service.current_project.narrative_map[0]
        )
        self.middle_layout.addWidget(self.workspace)


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
            "Save as...",
            default_dir,
            "Planoscript Project Files (*.json);;All Files (*)"
        )

        if not file_path:
            return False

        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        return self._do_save(file_path)


    def _do_save(self, file_path: str) -> bool:
        """Execute save and handle result."""
        try:
            success = self.save_project_usecase.execute(file_path)
            if success:
                self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb} ({file_path})")
            return success
        except Exception as e:
            QMessageBox.critical(self, "Error Saving the Project", str(e))
            return False


    def _close_project(self) -> bool:
        """Close current project with confirmation if not saved"""
        if not self.project_opened:
            return True

        # Check if project is modified (same as in _handle_quit)
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The project has been modified. Do you want to save it before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return False
            if reply == QMessageBox.Yes and not self._save_project():
                return False

        # Close the project and reinitialize the state of the application
        self._clear_project()
        self._show_welcome_message()
        self.project_opened = False
        self.setWindowTitle("Planoscript : start your new project")
        self._update_menu_state()

        return True


    def _clear_project(self):
        """Clear project from memory and reset workspace"""
        # Clean up workspace
        while self.middle_layout.count():
            item = self.middle_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Reset references
        self.workspace = None

        # Clean up project in service
        self.project_service._current_project = None
        self.project_service.set_modified(False)


    def closeEvent(self, event: QCloseEvent):
        """Override QWidget's closeEvent method."""
        if self._handle_quit():
            event.accept()
        else:
            event.ignore()


    def _handle_quit(self) -> bool:
        """Handle UI and use the use case"""
        if not self.quit_usecase.should_ask_confirmation():
            return True

        reply = QMessageBox.question(
            self,
            "Confirmation",
            "The project has been modified. Do you want to save it before closing?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        if reply == QMessageBox.Yes:
            return self._save_project()

        return reply == QMessageBox.No  # True if No, False if Cancel


    def _on_quit(self):
        # Method inherited from QWidget, emits closeEvent signal captured by closeEvent method
        self.close()


    # ---------------------------------------------------------------------
    # Interaction handling
    # ---------------------------------------------------------------------
    def _create_new_node(self, component_type: str):
        """
        Create a node from menu selection.
        Places the node at the center of the workspace.
        """
        # Check project and workspace
        if not self.project_opened or not hasattr(self, 'workspace') or self.workspace is None:
            return

        # MVP : one narrative map only per project
        narrative_map = self.project_service.current_project.narrative_map[0]

        # Calculate center position of the workspace
        viewport_rect = self.workspace.viewport().rect()
        scene_pos = self.workspace.mapToScene(
            viewport_rect.width() / 2,
            viewport_rect.height() / 2
        )

        # Execute use case
        result = self.create_node_usecase.execute(
            component_type=component_type,
            x=scene_pos.x(),
            y=scene_pos.y(),
            narrative_map=narrative_map
        )

        if result and result.get('success'):
            self.workspace.create_node_from_data(result)
            self._update_menu_state()
            self.node_count += 1


    def _start_state_event_relation_creation(self):
        """
        Activate State-Event relation creation mode.
        Wait for user to select source and target nodes.
        """
        # Check minimum node count
        if self.node_count < 2:
            self.info_bar.show_message("A relation needs at least two nodes in the map")
            return

        # Set up relation creation mode
        self.waiting_for_source = True
        self.waiting_for_target = False
        self.source_node = None
        self.info_bar.show_message("Click on the first node (State or Event)")


    def _on_node_selected_for_relation(self, node):
        """
        Callback called when a node is selected in relation creation mode.
        Handle source/target selection and create the State-Event relation.
        """
        if self.waiting_for_source:
            # First selected node = source
            self.source_node = node
            self.waiting_for_source = False
            self.waiting_for_target = True
            self.info_bar.show_message("Click on the second node (Event or State)")
        elif self.waiting_for_target:
            # Second selected node = target
            self.waiting_for_target = False
            self._create_state_event_relation(self.source_node, node)
            self.source_node = None


    def _create_state_event_relation(self, source_node, target_node):
        """
        Create a State-Event relation between two nodes using StateNodeService.
        """
        # Extract business entities from visual nodes
        source_entity = source_node.entity
        target_entity = target_node.entity
        
        # Check if the connection is valid (State <-> Event only)
        source_type = "State" if isinstance(source_entity, State) else "Event" if isinstance(source_entity, Event) else None
        target_type = "State" if isinstance(target_entity, State) else "Event" if isinstance(target_entity, Event) else None
        
        if not source_type or not target_type:
            self.info_bar.show_message("Error: Only State and Event can be connected")
            return
        
        if not StateNodeService.can_connect(source_type, target_type):
            self.info_bar.show_message("Error: Invalid connection (only State <-> Event allowed)")
            return
        
        # Get the current narrative map (MVP : one narrative map only per project)
        narrative_map = self.project_service.current_project.narrative_map[0]
        
        # Create the State_node using the service
        state_node = StateNodeService.create_state_node(
            narrative_map=narrative_map,
            source_entity=source_entity,
            target_entity=target_entity
        )
        
        if state_node:
            # Create visual connection in workspace
            if isinstance(self.workspace, JourneyWorkspace):
                self.workspace.create_connection_from_data({
                    'source': source_node,
                    'target': target_node,
                    'relation': state_node
                })
            self.info_bar.show_message("State-Event relation created")
            self.project_service.set_modified(True)
        else:
            self.info_bar.show_message("Error: Cannot create State-Event relation")


    def _show_changelog(self):
        ChangeLogDialog(self.change_log_service, self).exec()


    def _show_about(self):
        AboutDialog(self.about_service, self).exec()
