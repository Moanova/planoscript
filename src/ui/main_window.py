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
import logging
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QLabel,
    QMessageBox, QGridLayout, QFileDialog, QStackedWidget
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCloseEvent

from ui.views.events_workspace import EventsWorkspace
from ui.views.agents_workspace import AgentsWorkspace
from ui.widgets.tab_bar import TabBar
from ui.nodes.connection import Connection
from ui.nodes.state_node import StateNode
from ui.widgets.info_bar import InfoBar
from ui.utils import theme
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.change_log_dialog import ChangeLogDialog
from core.models.data_model import State, Event
from core.models.view_model import NodeType, RelationType
from core.services.project_service import ProjectService
from core.services.about_service import AboutService
from core.services.change_log_service import ChangeLogService
from core.services.arc_service import ArcService
from core.services.layout_service import LayoutService
from usecases.project_management.create_project_usecase import CreateProjectUseCase
from usecases.project_management.create_agent_usecase import CreateAgentUseCase
from usecases.project_management.update_agent_usecase import UpdateAgentUseCase
from usecases.project_management.delete_agent_usecase import DeleteAgentUseCase
from usecases.file_management.load_project_usecase import LoadProjectUseCase
from usecases.file_management.save_project_usecase import SaveProjectUseCase
from usecases.file_management.quit_application_usecase import QuitApplicationUseCase
from usecases.agent_association.associate_agent_state_usecase import AssociateAgentStateUseCase
from usecases.agent_association.dissociate_agent_state_usecase import DissociateAgentStateUseCase
from usecases.agent_association.remove_state_associations_usecase import RemoveStateAssociationsUseCase
from usecases.view_management.create_node_usecase import CreateNodeUseCase
from usecases.view_management.create_relation_usecase import CreateRelationUseCase
from usecases.view_management.update_component_usecase import UpdateComponentUseCase
from usecases.journey_management import (
    CreateJourneyUseCase, UpdateJourneyUseCase, ActivateJourneyUseCase
)
from ui.dialogs.component_dialog import ComponentDialog
from ui.dialogs.agent_dialog import AgentDialog
from ui.dialogs.agent_selection_dialog import AgentSelectionDialog
from ui.dialogs.agent_association_dialog import AgentAssociationDialog
from ui.dialogs.journey_dialog import JourneyDialog
from ui.dialogs.journey_selection_dialog import JourneySelectionDialog
from config.config_loader import get as _get_config
from config.user_state_loader import get as _get_user_state, set as _set_user_state

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main Application Window"""

    # ---------------------------------------------------------------------
    # Environment setup
    # ---------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        # Boolean to define whether a project is opened or not
        self.project_opened = False

        # Node counter to enable or disable the "Relation" button (MVP : no control buttons, menu operations only)
        self.node_count = 0

        # Dependencies initialization
        self.project_service = ProjectService()
        self.create_project_usecase = CreateProjectUseCase(self.project_service)
        self.load_project_usecase = LoadProjectUseCase(self.project_service)
        self.save_project_usecase = SaveProjectUseCase(self.project_service)
        self.quit_usecase = QuitApplicationUseCase(self.project_service)
        self.create_node_usecase = CreateNodeUseCase(self.project_service)
        self.create_agent_usecase = CreateAgentUseCase(self.project_service)
        self.update_agent_usecase = UpdateAgentUseCase(self.project_service)
        self.delete_agent_usecase = DeleteAgentUseCase(self.project_service)
        self.associate_agent_state_usecase = AssociateAgentStateUseCase(self.project_service)
        self.dissociate_agent_state_usecase = DissociateAgentStateUseCase(self.project_service)
        self.remove_state_associations_usecase = RemoveStateAssociationsUseCase(self.project_service)
        self.update_component_usecase = UpdateComponentUseCase(self.project_service)
        self.create_relation_usecase = CreateRelationUseCase(self.project_service)
        # TSK23: journey management (EPC05)
        self.create_journey_usecase = CreateJourneyUseCase(self.project_service)
        self.update_journey_usecase = UpdateJourneyUseCase(self.project_service)
        self.activate_journey_usecase = ActivateJourneyUseCase(self.project_service)
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

        # Central space: single tab bar above a stack of workspace pages.
        # The tab bar is a single instance (single source of truth for the
        # active workspace, TSK07); it is hidden until a project is opened.
        self.middle_section = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_section)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.setSpacing(0)
        main_layout.addWidget(self.middle_section, 1)

        self.tab_bar = TabBar(["Events", "Agents"])
        self.tab_bar.hide()
        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        self.middle_layout.addWidget(self.tab_bar)

        # Stacked pages: welcome / events workspace / agents workspace
        self.pages = QStackedWidget()
        self.middle_layout.addWidget(self.pages, 1)

        # Welcome page (no project opened)
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_page)
        self.pages.addWidget(self.welcome_page)

        # Events workspace page: created empty, populated per project
        self.events_page = QWidget()
        events_layout = QVBoxLayout(self.events_page)
        events_layout.setContentsMargins(0, 0, 0, 0)
        self.pages.addWidget(self.events_page)

        # Agents workspace page: placeholder until TSK08
        self.agents_page = AgentsWorkspace()
        # TSK13: the agents view context menus act on entities through
        # the main window (the workspace only emits requests)
        self.agents_page.main_window = self
        # TSK09: matrix cell editions refresh the events view (SU008)
        self.agents_page.associationChanged.connect(self._on_matrix_association_changed)
        # TSK10: cross-view navigation request
        self.agents_page.focusAgentInEventsViewRequested.connect(
            self._focus_agent_in_events_view)
        # TSK13: cross-view navigation request (state -> events view)
        self.agents_page.focusStateInEventsViewRequested.connect(
            self._focus_state_in_events_view)
        # TSK13 review: card selection changes re-evaluate the Agent
        # menu activation in the agents view
        self.agents_page.cardSelectionChanged.connect(self._update_menu_state)
        self.pages.addWidget(self.agents_page)

        self.pages.setCurrentWidget(self.welcome_page)

        # TSK10/RG067: Escape releases the cross-view navigation focus
        from PySide6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._release_focus)

        # Deferred initialization of workspace
        self.workspace = None

        # Bottom section
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        # Information bar (75%) --> MPV 100%, no zoom bar
        self.info_bar = InfoBar()
        ##bottom_layout.addWidget(self.info_bar, 4)  # 75%
        bottom_layout.addWidget(self.info_bar)
        # TSK15: a rejected reorder (initial state pinned, RG068/RG031)
        # is reported in the info bar
        self.agents_page.reorderRejected.connect(self.info_bar.show_message)
        
        # Zoom bar (25%)
        #self.zoom_bar = ZoomBar()
        #bottom_layout.addWidget(self.zoom_bar, 1)  # 25%
        
        main_layout.addLayout(bottom_layout)
        
        self.setWindowTitle("Planoscript : start your new project")

        self._show_welcome_message()

    def _on_tab_changed(self, tab_name: str):
        """Switch the stacked page to the selected workspace (TSK07).

        Refreshing the agents view on tab activation guarantees the
        matrix is in sync with the data (SU008) even if a refresh hook
        was missed.
        """
        if tab_name == "Events":
            self.pages.setCurrentWidget(self.events_page)
        elif tab_name == "Agents":
            self.pages.setCurrentWidget(self.agents_page)
            self._refresh_agents_view()

    def _on_matrix_association_changed(self, state_id, agent_lb, associated):
        """Handle a matrix cell edition (TSK09, SU008).

        Refreshes the agent badge of the events view state node and
        reports the action in the info bar.
        """
        if isinstance(self.workspace, EventsWorkspace):
            # Entity IDs are unique per type, not globally (State.id=1 and
            # Event.id=1 can coexist): only a state node may carry the
            # badge, so the lookup must filter on the State entity type
            for item in self.workspace.scene.items():
                if (isinstance(item, StateNode)
                        and item.entity.id == state_id):
                    self.workspace.refresh_state_badge(item)
                    break
        if associated:
            self.info_bar.show_message(f"Agent '{agent_lb}' associated")
        else:
            self.info_bar.show_message(f"Agent '{agent_lb}' dissociated")

    def _focus_state_in_agents_view(self, state_id):
        """Show a state in the agents view, focused (TSK10, RG067).

        Switches to the Agents tab and highlights the state column.
        The focus is temporary: no modification flag, no persistence
        (RG067).
        """
        self.tab_bar.setCurrentTab("Agents")
        # _on_tab_changed has refreshed the matrix: apply the focus on
        # the rebuilt columns
        self.agents_page.set_focus(state_id)

    def _focus_state_in_events_view(self, state_id):
        """Show a state in the events view, focused (TSK13, RG067).

        Switches to the Events tab and highlights the node of the
        state. The focus is temporary: no modification flag, no
        persistence (RG067).
        """
        project = self.project_service.current_project
        state = next(
            (s for s in project.narrative_map[0].state if s.id == state_id),
            None)
        if state is None:
            return
        self.tab_bar.setCurrentTab("Events")
        if isinstance(self.workspace, EventsWorkspace):
            self.workspace.set_focus([state_id])
        self.info_bar.show_message(f"State '{state.lb}' highlighted")

    def _focus_agent_in_events_view(self, agent_id):
        """Show the states of an agent in the events view, focused
        (TSK10, RG067).

        Switches to the Events tab and highlights the nodes of the
        states associated with the agent, dimming the rest. If the agent
        has no associated state, reports it without switching.
        """
        project = self.project_service.current_project
        agent = next((a for a in project.agent if a.id == agent_id), None)
        if agent is None:
            return
        narrative_map = project.narrative_map[0]
        state_ids = [
            rel.state_id for rel in narrative_map.state_agent_rel
            if rel.agent_id == agent_id]
        if not state_ids:
            self.info_bar.show_message(
                f"Agent '{agent.lb}' has no associated state")
            return
        self.tab_bar.setCurrentTab("Events")
        if isinstance(self.workspace, EventsWorkspace):
            self.workspace.set_focus(state_ids)
        self.info_bar.show_message(
            f"Agent '{agent.lb}': {len(state_ids)} state(s) highlighted")

    def _release_focus(self):
        """Release the cross-view navigation focus (TSK10, RG067).

        Escape releases the focus of the currently displayed view.
        """
        if not hasattr(self, 'pages'):
            return
        current = self.pages.currentWidget()
        if current is self.events_page and isinstance(self.workspace, EventsWorkspace):
            self.workspace.clear_focus()
        elif current is self.agents_page:
            self.agents_page.clear_focus()

    def _refresh_agents_view(self):
        """Refresh the agents view matrix (TSK08, SU008).

        Single refresh entry point, called after any modification of
        the agents, the states or the associations.
        """
        if hasattr(self, 'agents_page') and self.agents_page is not None:
            self.agents_page.refresh()


    def _create_menu_bar(self):
        """Creates the menu bar"""
        self.menu_actions = {}
        self.menu_bar = self.menuBar()
        # Dark theme menu bar (charter 98, via ui.utils.theme)
        self.menu_bar.setStyleSheet(theme.MENU_BAR_STYLESHEET)
        
        # Files menu
        self.file_menu = self.menu_bar.addMenu("Files")

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
        self.display_menu = self.menu_bar.addMenu("Display")
        # TSK23: dynamic checkable list of journeys (active journey is checked)
        self.journey_menu = self.display_menu.addMenu("Journey")
        self.journey_list_menu = self.journey_menu.addMenu("JourneyList")
        self.journey_list_menu.aboutToShow.connect(self._rebuild_journey_list_menu)
        self.zoom_menu = self.display_menu.addMenu("Zoom")
        self.menu_actions['zoom_in'] = self.zoom_menu.addAction("Zoom in", lambda: None, "Ctrl+=")
        self.menu_actions['zoom_out'] = self.zoom_menu.addAction("Zoom out", lambda: None, "Ctrl+-")
        self.menu_actions['zoom_reset'] = self.zoom_menu.addAction("Reset", lambda: None, "Ctrl+0")

        # Project menu
        self.project_menu = self.menu_bar.addMenu("Project")

        # MVP : events view only + the relation view will be reworked at a leter stage of development
        self.view_menu = self.project_menu.addMenu("View")
        self.menu_actions['view_events'] = self.view_menu.addAction("Events", lambda: None)
        #self.menu_actions['view_relations'] = self.view_menu.addAction("Relations", lambda: None)

        self.components_menu = self.project_menu.addMenu("Components...")

        # Agent submenu (Type → Action, TSK13): New... opens the
        # creation dialog directly; Edit/Delete open a selection dialog
        # and apply the action to the selected agent
        self.agent_menu = self.components_menu.addMenu("Agent")
        self.menu_actions['agent_new'] = self.agent_menu.addAction("New...", lambda: self._new_agent())
        self.menu_actions['agent_edit'] = self.agent_menu.addAction("Edit", lambda: self._edit_agent())
        self.menu_actions['agent_delete'] = self.agent_menu.addAction("Delete", lambda: self._delete_agent())

        # State submenu (Type → Action)
        self.state_menu = self.components_menu.addMenu("State")
        self.menu_actions['state_new'] = self.state_menu.addAction("New...", lambda: self._create_new_node("State"))
        self.menu_actions['state_edit'] = self.state_menu.addAction("Edit", lambda: self._edit_selected_component("State"))
        self.menu_actions['state_delete'] = self.state_menu.addAction("Delete", lambda: self._delete_selected_component("State"))

        # Event submenu (Type → Action)
        self.event_menu = self.components_menu.addMenu("Event")
        self.menu_actions['event_new'] = self.event_menu.addAction("New...", lambda: self._create_new_node("Event"))
        self.menu_actions['event_edit'] = self.event_menu.addAction("Edit", lambda: self._edit_selected_component("Event"))
        self.menu_actions['event_delete'] = self.event_menu.addAction("Delete", lambda: self._delete_selected_component("Event"))

        self.relations_menu = self.project_menu.addMenu("Relations...")
        self.relations_menu.addAction("Connect State and Event", lambda: self._start_state_event_relation_creation())
        self.menu_actions['associate_agents'] = self.relations_menu.addAction("Associate agents with State", lambda: self._associate_agents_to_selected_state())
        self.menu_actions['relation_edit'] = self.relations_menu.addAction("Edit", lambda: self._edit_selected_relation())
        self.menu_actions['relation_delete'] = self.relations_menu.addAction("Delete", lambda: self._delete_selected_relation())

        # Journeys submenu (TSK23, FN023/FN024; TSK23 review: no Delete
        # entry here - deletion is handled from the selection dialog
        # opened by Edit, stubbed until TSK25)
        self.journeys_menu = self.project_menu.addMenu("Journeys...")
        self.menu_actions['journey_new'] = self.journeys_menu.addAction("New...", lambda: self._new_journey())
        self.menu_actions['journey_edit'] = self.journeys_menu.addAction("Edit", lambda: self._edit_journey())

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
        #actions = [
        #    'close', 'save', 'save_as', 'export_map', 'import_map',
        #    'undo', 'redo', 'history', 'cut', 'copy', 'paste', 'delete',
        #    'zoom_in', 'zoom_out', 'zoom_reset'
        #]
        actions = [
            'close', 'save', 'save_as'
        ]

        self.menu_actions['export_map'].setEnabled(False)
        self.menu_actions['import_map'].setEnabled(False)
        self.menu_actions['undo'].setEnabled(False)
        self.menu_actions['redo'].setEnabled(False)
        self.menu_actions['history'].setEnabled(False)
        self.menu_actions['cut'].setEnabled(False)
        self.menu_actions['copy'].setEnabled(False)
        self.menu_actions['paste'].setEnabled(False)
        self.menu_actions['delete'].setEnabled(False)

        self.journey_menu.setEnabled(False)
        self.zoom_menu.setEnabled(False)

        self.view_menu.setEnabled(False)
        self.components_menu.setEnabled(has_project)
        self.relations_menu.setEnabled(has_project)
        # TSK23: journeys menus need an open project; Edit/Delete also
        # need at least one journey (always true: RG022 default journey)
        self.journeys_menu.setEnabled(has_project)
        self.journey_menu.setEnabled(has_project)
        has_journey = bool(
            has_project and self.project_service.current_project
            and self.project_service.current_project.narrative_map
            and self.project_service.current_project.narrative_map[0].journey)
        self.menu_actions['journey_new'].setEnabled(has_project)
        self.menu_actions['journey_edit'].setEnabled(has_journey)

        for action_key in actions:
            if action_key in self.menu_actions:
                self.menu_actions[action_key].setEnabled(has_project)

        # "Save" disabled if project not modified
        if 'save' in self.menu_actions:
            self.menu_actions['save'].setEnabled(has_project and is_modified)

        # Edit/Delete actions: enabled only if a matching item is selected
        selected = self._get_selected_item()
        has_state = (selected is not None and hasattr(selected, 'entity')
                     and isinstance(selected.entity, State))
        has_event = (selected is not None and hasattr(selected, 'entity')
                      and isinstance(selected.entity, Event))
        has_relation = isinstance(selected, Connection)
        # RG031: the initial state can never be deleted, so the Delete State
        # action stays disabled when the initial state is selected
        has_deletable_state = (has_state and selected.entity.typ != "Initial")

        self.menu_actions['state_edit'].setEnabled(has_project and has_state)
        self.menu_actions['state_delete'].setEnabled(has_project and has_deletable_state)
        self.menu_actions['event_edit'].setEnabled(has_project and has_event)
        self.menu_actions['event_delete'].setEnabled(has_project and has_event)
        self.menu_actions['relation_edit'].setEnabled(has_project and has_relation)
        self.menu_actions['relation_delete'].setEnabled(has_project and has_relation)
        self.menu_actions['associate_agents'].setEnabled(has_project and has_state)

        # TSK13 + TSK13 review: the agent submenu depends on the active
        # view. Events view: "New..." needs an open project, "Edit"/
        # "Delete" need at least one agent (picked in a selection
        # dialog). Agents view: "Edit"/"Delete" act directly on the
        # selected agent card and need a selected agent card.
        # (tab_bar/agents_page do not exist yet on the first call from
        # _create_menu_bar)
        tab_bar = getattr(self, 'tab_bar', None)
        agents_page = getattr(self, 'agents_page', None)
        in_agents_view = bool(
            tab_bar is not None and tab_bar.currentTab() == "Agents")
        has_agent = bool(
            has_project and self.project_service.current_project
            and self.project_service.current_project.agent)
        agent_card_selected = bool(
            has_project and in_agents_view and agents_page is not None
            and agents_page.selected_agent() is not None)
        self.menu_actions['agent_new'].setEnabled(has_project)
        if in_agents_view:
            self.menu_actions['agent_edit'].setEnabled(agent_card_selected)
            self.menu_actions['agent_delete'].setEnabled(agent_card_selected)
        else:
            self.menu_actions['agent_edit'].setEnabled(has_agent)
            self.menu_actions['agent_delete'].setEnabled(has_agent)


    def _show_welcome_message(self):
        """Display welcome message with clickable link"""
        # Reset the welcome page content
        while self.welcome_page.layout().count():
            item = self.welcome_page.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)

        welcome_label = QLabel(f"""
            <h2 style="color: {theme.TEXT_PRIMARY};">Build the plan of your new script.</h2>
            <p style="color: {theme.TEXT_SECONDARY};">Start by <a href=\"new\" style=\"color: {theme.STATE_COLOR}; text-decoration: underline;\">creating a new project</a> or open an existing project.</p>
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setOpenExternalLinks(False)
        welcome_label.setTextFormat(Qt.RichText)
        welcome_label.setWordWrap(True)
        welcome_label.linkActivated.connect(lambda link: self._create_project())
        welcome_label.setStyleSheet(f"QLabel {{ padding: 40px; background-color: {theme.BG_PRIMARY}; }}")
        self.welcome_page.setStyleSheet(f"background-color: {theme.BG_PRIMARY};")

        welcome_layout.addWidget(welcome_label)
        self.welcome_page.layout().addWidget(welcome_widget)
        self.pages.setCurrentWidget(self.welcome_page)
        # No project opened: hide the workspace tab bar (TSK07)
        self.tab_bar.hide()


    # ---------------------------------------------------------------------
    # Project and application state management
    # ---------------------------------------------------------------------
    def _create_project(self):
        """Create a new project"""
        # RG060: Check if the current project is modified before creating a new one
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The current project has been modified. Do you want to save it before creating a new one?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return  # Cancel creation
            if reply == QMessageBox.Yes and not self._save_project():
                return  # Save failed or was cancelled

        self.create_project_usecase.execute()
        self._init_workspace()
        self._create_initial_state_visual()
        # Initialize the agents view for the new project (TSK08): no
        # saved layout yet, the matrix order falls back to creation
        # order (RG068)
        self.agents_page.set_project(
            self.project_service, None,
            associate_usecase=self.associate_agent_state_usecase,
            dissociate_usecase=self.dissociate_agent_state_usecase)
        self._refresh_agents_view()
        self.project_opened = True
        self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb}")
        self._update_menu_state()

        logger.debug("Project created: %s", self.project_service.current_project)


    def _open_project(self):
        """Open a project from the file system"""
        # RG060: Check if the current project is modified before opening a new one
        if self.project_service.is_modified:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "The current project has been modified. Do you want to save it before opening a new one?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return  # Cancel opening
            if reply == QMessageBox.Yes and not self._save_project():
                return  # Save failed or was cancelled

        default_dir = self._get_default_project_dir()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open a Project",
            default_dir,
            "Planoscript Project Files (*.json);;All Files (*)"
        )

        if not file_path:
            return  # Cancelled by user

        # Remember the chosen directory for next time
        _set_user_state("last_project_dir", os.path.dirname(file_path))

        if self.load_project_usecase.execute(file_path):
            self._init_workspace()
            self._populate_workspace(file_path)
            self.project_opened = True
            self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb} ({file_path})")
            self._update_menu_state()
        else:
            QMessageBox.critical(
                self,
                "Error opening the File",
                f"The File cannot be opened : {file_path}"
            )

        logger.debug("Project loaded: %s", self.project_service.current_project)


    def _init_workspace(self):
        """Initialize workspace with a single EventsWorkspace."""
        # Disconnect signals from old workspace if it exists
        if hasattr(self, 'workspace') and self.workspace is not None:
            try:
                self.workspace.relation_created.disconnect()
            except (TypeError, AttributeError):
                # No connection to disconnect or workspace doesn't have the signal
                pass
            try:
                self.workspace.workspace_modified.disconnect()
            except (TypeError, AttributeError):
                pass
            try:
                self.workspace.scene.selectionChanged.disconnect()
            except (TypeError, AttributeError):
                pass

        # Clear the events page before rebuilding the workspace
        while self.events_page.layout().count():
            item = self.events_page.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Single workspace per project: events view (agents view is the
        # second workspace, TSK07; it does not depend on the map instance)
        self.workspace = EventsWorkspace(
            narrative_map=self.project_service.current_project.narrative_map[0],
            info_bar=self.info_bar,
            main_window=self
        )
        self.events_page.layout().addWidget(self.workspace)

        # Show the workspace pages: tab bar visible, Events active by
        # default on project opening (TSK07: display state, not persisted)
        self.tab_bar.show()
        self.tab_bar.forceCurrentTab("Events")
        self.pages.setCurrentWidget(self.events_page)
        
        # Connect workspace signal for relation creation
        if isinstance(self.workspace, EventsWorkspace):
            self.workspace.relation_created.connect(self._on_relation_created)
            # TSK10: cross-view navigation requests
            self.workspace.focusStateInAgentsViewRequested.connect(
                self._focus_state_in_agents_view)
            self.workspace.workspace_modified.connect(self._on_workspace_modified)
            # Update menu state when selection changes (enables/disables Edit/Delete)
            self.workspace.scene.selectionChanged.connect(self._update_menu_state)


    def _create_initial_state_visual(self):
        """Create the visual node for the initial state (RG031) in the workspace."""
        narrative_map = self.project_service.current_project.narrative_map[0]
        initial_state = next(
            (s for s in narrative_map.state if s.typ == "Initial"), None
        )
        if not initial_state:
            return

        # Position at the center of the workspace viewport
        viewport_rect = self.workspace.viewport().rect()
        scene_pos = self.workspace.mapToScene(
            viewport_rect.width() / 2,
            viewport_rect.height() / 2
        )
        layout = LayoutService.create_node_layout(
            node_id=initial_state.id,
            node_type=NodeType.STATE.value,
            x=scene_pos.x(),
            y=scene_pos.y()
        )
        self.workspace.create_node_from_data({
            'success': True,
            'entity': initial_state,
            'entity_id': initial_state.id,
            'layout': layout,
            'node_type': NodeType.STATE,
            'narrative_map_id': narrative_map.id,
            'component_type': 'State'
        })
        self.node_count += 1


    def _get_default_project_dir(self) -> str:
        """
        Resolve the default directory for file dialogs.

        Priority: last used directory (user state) > configured default
        (config.json) > user home.  The resolved directory is created
        if it does not exist.

        The configured path supports a leading ``~/`` that is resolved
        against the user home.  If ``~/Documents`` exists, a relative
        ``PlanoscriptProjects`` is placed inside it; otherwise it is
        placed directly under the user home.
        """
        last_dir = _get_user_state("last_project_dir")
        if last_dir and os.path.isdir(last_dir):
            return last_dir

        home = os.path.expanduser("~")
        configured = _get_config("projects_default_dir", "~/PlanoscriptProjects")
        configured = os.path.expanduser(configured)

        # If the configured path is directly under the user home and
        # ~/Documents exists, nest it inside ~/Documents instead.
        parent = os.path.dirname(configured)
        if os.path.normcase(parent) == os.path.normcase(home):
            documents_dir = os.path.join(home, "Documents")
            if os.path.isdir(documents_dir):
                configured = os.path.join(documents_dir, os.path.basename(configured))

        try:
            os.makedirs(configured, exist_ok=True)
        except OSError:
            pass
        return configured


    def _populate_workspace(self, file_path: str):
        """
        Load visual layout and rebuild workspace nodes and connections.

        Tries to load a saved WorkspaceLayout from the layout file. If found,
        restores node positions, connections, zoom, and scroll. If no layout
        file exists, creates nodes with default positions.
        """
        narrative_map = self.project_service.current_project.narrative_map[0]

        workspace_layout = LayoutService.load_workspace_layout(
            file_path, narrative_map.id
        )

        if workspace_layout and isinstance(self.workspace, EventsWorkspace):
            self.node_count = self.workspace.populate_from_layout(
                workspace_layout, narrative_map
            )
        elif isinstance(self.workspace, EventsWorkspace):
            self.node_count = self.workspace.populate_default(narrative_map)

        # Initialize the agents view (TSK08) with its edition use
        # cases (TSK09)
        self.agents_page.set_project(
            self.project_service, workspace_layout,
            associate_usecase=self.associate_agent_state_usecase,
            dissociate_usecase=self.dissociate_agent_state_usecase)
        self._refresh_agents_view()

    def _save_project(self):
        current_project = self.project_service.current_project

        if (current_project and current_project.file_path and
            os.path.exists(os.path.dirname(current_project.file_path))):
            return self._do_save(current_project.file_path)

        return self._save_project_as()


    def _save_project_as(self) -> bool:
        default_dir = self._get_default_project_dir()
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

        # Remember the chosen directory for next time
        _set_user_state("last_project_dir", os.path.dirname(file_path))

        return self._do_save(file_path)


    def _do_save(self, file_path: str) -> bool:
        """Execute save and handle result."""
        try:
            success = self.save_project_usecase.execute(file_path)
            if success:
                # Save visual layout alongside the business data
                if isinstance(self.workspace, EventsWorkspace):
                    workspace_layout = self.workspace.collect_workspace_layout()
                    # RG068: persist the agents view matrix order
                    # (column and row order is layout data). The agents
                    # view keeps its layout data up to date on every
                    # reorder; _current_workspace_layout was never
                    # assigned, so the order was silently lost on save
                    if self.agents_page.layout_data is not None:
                        workspace_layout.agents_view_column_order = (
                            self.agents_page.layout_data.agents_view_column_order)
                        workspace_layout.agents_view_row_order = (
                            self.agents_page.layout_data.agents_view_row_order)
                    LayoutService.save_workspace_layout(
                        file_path,
                        workspace_layout.narrative_map_id,
                        workspace_layout
                    )
                    # Remove layouts left over from a project previously saved
                    # under the same file (MVP: one narrative map per project)
                    stale = LayoutService.delete_stale_layouts(
                        file_path,
                        [workspace_layout.narrative_map_id]
                    )
                    if stale:
                        logger.debug("Deleted %d stale layout file(s) for %s", stale, file_path)
                self.setWindowTitle(f"Planoscript : {self.project_service.current_project.lb} ({file_path})")
                # Refresh menu state: is_modified is now False, so Save
                # should be disabled until the next modification.
                self._update_menu_state()
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
        # Reset the information bar: the last message belonged to the
        # project being closed
        self.info_bar.clear()
        self.project_opened = False
        self.setWindowTitle("Planoscript : start your new project")
        self._update_menu_state()

        return True


    def _clear_project(self):
        """Clear project from memory and reset workspace"""
        # Detach and delete only the events workspace: the middle section
        # structure (tab bar, stacked pages) is permanent since TSK07 and
        # must survive project closing (the welcome/events/agents pages
        # are reused by the next project)
        if self.workspace is not None:
            self.workspace.setParent(None)
            self.workspace.deleteLater()

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
            # TSK08: a state column may have appeared -> refresh the
            # agents view matrix
            self._refresh_agents_view()
            entity = result.get('entity')
            logger.debug("Node created (%s): %s",
                         result.get('component_type'),
                         entity.to_dict() if entity and hasattr(entity, 'to_dict') else entity)
            # TSK13: creating an event from the agents view (menu or
            # context menu) switches back to the events view, where the
            # event node lives, and selects it. Creating a state stays in
            # the agents view (the new column appears in the matrix).
            if (component_type == "Event"
                    and self.tab_bar.currentTab() == "Agents"):
                self.tab_bar.setCurrentTab("Events")
                node = self.workspace._find_node_by_entity_id_and_type(
                    entity.id, Event)
                if node is not None:
                    self.workspace._select_item_only(node)


    def _start_state_event_relation_creation(self):
        """
        Activate State-Event relation creation mode with rubber band effect.
        """
        # Check minimum node count
        if self.node_count < 2:
            self.info_bar.show_message("two nodes are needed in the narrative map for a relation")
            return

        # Check if workspace is ready
        if not isinstance(self.workspace, EventsWorkspace):
            self.info_bar.show_message("Error: Workspace not ready for relation creation")
            return

        # Enter relation creation mode in workspace
        self.workspace.enter_relation_creation_mode()
        self.info_bar.show_message("Click on source node output port")

    
    def _on_relation_created(self, source_node, target_node):
        """
        Callback called when a relation is created via rubber band connection.
        Creates the business arc relation and visual connection.
        """
        logger.debug("_on_relation_created called with source=%s, target=%s",
                     source_node.entity.lb if hasattr(source_node, 'entity') else 'None',
                     target_node.entity.lb if hasattr(target_node, 'entity') else 'None')
        self._create_state_event_relation(source_node, target_node)


    def _on_workspace_modified(self):
        """Mark project as modified when the workspace is visually changed."""
        if self.project_opened:
            self.project_service.set_modified(True)
            self._update_menu_state()


    def _create_state_event_relation(self, source_node, target_node):
        """
        Create a State-Event relation between two nodes using ArcService.
        """
        # Extract business entities from visual nodes
        if not hasattr(source_node, 'entity') or not hasattr(target_node, 'entity'):
            self.info_bar.show_message("Error: Invalid node type for relation")
            return
        
        source_entity = source_node.entity
        target_entity = target_node.entity
        
        # Check if the connection is valid (State <-> Event only)
        source_type = "State" if isinstance(source_entity, State) else "Event" if isinstance(source_entity, Event) else None
        target_type = "State" if isinstance(target_entity, State) else "Event" if isinstance(target_entity, Event) else None
        
        if not source_type or not target_type:
            self.info_bar.show_message("Error: Only State and Event can be connected")
            return
        
        if not ArcService.can_connect(source_type, target_type):
            self.info_bar.show_message("Error: Invalid connection (only State <-> Event allowed)")
            return
        
        # Get the current narrative map (MVP : one narrative map only per project)
        narrative_map = self.project_service.current_project.narrative_map[0]

        # RG058: check for direct cycle before attempting creation
        if ArcService.would_create_cycle(narrative_map, source_entity, target_entity):
            self.info_bar.show_message(
                "Cannot connect: this relation would create a direct cycle "
                "with the existing reverse relation"
            )
            return

        # RG054: refuse duplicate visual connection
        if isinstance(self.workspace, EventsWorkspace):
            if self.workspace.has_connection_between(source_node, target_node):
                self.info_bar.show_message(
                    "Cannot connect: a relation already exists between these components"
                )
                return

        # Create the arc using the service
        arc = ArcService.create_arc(
            narrative_map=narrative_map,
            source_entity=source_entity,
            target_entity=target_entity
        )

        if arc:
            logger.debug("Arc created: %s", arc.to_dict())
            # Mark project as modified BEFORE creating the visual connection,
            # because create_connection_from_data triggers a selection change
            # which refreshes the menu state via scene.selectionChanged.
            self.project_service.set_modified(True)
            # Determine relation type based on direction
            if source_type == "State":
                relation_type = RelationType.STATE_TO_EVENT
            else:
                relation_type = RelationType.EVENT_TO_STATE

            # Create visual connection in workspace
            if isinstance(self.workspace, EventsWorkspace):
                self.workspace.create_connection_from_data({
                    'source': source_node,
                    'target': target_node,
                    'relation': arc,
                    'relation_type': relation_type
                })
            self.info_bar.show_message("State-Event relation created")
            # TSK13: the agent badge of the events state node and the
            # event badges of the agents-view state card may have changed
            self._refresh_all_state_badges()
            self._refresh_agents_view_event_badges()
            self._update_menu_state()
        else:
            self.info_bar.show_message("Error: Cannot create State-Event relation")


    # ---------------------------------------------------------------------
    # Component and relation editing / deletion (not yet implemented)
    # ---------------------------------------------------------------------
    def _get_selected_item(self):
        """Return the single selected item in the workspace, or None."""
        workspace = getattr(self, 'workspace', None)
        if not workspace or not hasattr(workspace, 'scene'):
            return None
        selected = workspace.scene.selectedItems()
        if len(selected) == 1:
            return selected[0]
        return None


    def _associate_agents_to_selected_state(self):
        """Associate agents with the currently selected state (FN030)."""
        item = self._get_selected_item()
        if item is None or isinstance(item, Connection) or not hasattr(item, 'entity'):
            self.info_bar.show_message("Select a state to associate agents with")
            return
        self._associate_agents_to_state(item.entity)

    def _associate_agents_to_state(self, entity):
        """Open the agent association dialog for a state (FN030, SU008)."""
        from core.models.data_model import State
        if not self.project_service or not self.project_service.current_project:
            self.info_bar.show_message("No project open")
            return
        if not isinstance(entity, State):
            self.info_bar.show_message("Selected component is not a state")
            return
        dialog = AgentAssociationDialog(
            self.project_service, entity,
            self.associate_agent_state_usecase,
            self.dissociate_agent_state_usecase,
            self.create_agent_usecase, parent=self)
        dialog.exec()
        # TSK05: refresh the agent badge of the state node
        if isinstance(self.workspace, EventsWorkspace):
            for item in self.workspace.scene.items():
                if getattr(item, 'entity', None) is entity:
                    self.workspace.refresh_state_badge(item)
                    break
        # TSK08: keep the agents view matrix in sync (SU008)
        self._refresh_agents_view()
        self._update_menu_state()

    def _create_agent_from_values(self, lb, typ, note, content=None):
        """Shared agent creation (use case + refreshes). Returns True on
        success."""
        result = self.create_agent_usecase.execute(lb=lb, typ=typ, note=note, content=content)
        if result and result.get('success'):
            self.info_bar.show_message("Agent created")
            # TSK08: a new agent row may have appeared -> refresh
            # the agents view matrix; a new agent marks the
            # project as modified -> re-enable "Save"
            self._refresh_agents_view()
            self._update_menu_state()
            return True
        self.info_bar.show_message("Cannot create agent: invalid data")
        return False

    def _new_agent(self):
        """Create an agent from the "Project > Components... > Agent >
        New..." menu entry (TSK13, FN031). TSK13 review: the behavior
        depends on the active view — events view: the "New Agent"
        dialog opens, prefilled with a default label (editable);
        agents view: the agent is created directly in the matrix row,
        with the default label."""
        if self.tab_bar.currentTab() == "Agents":
            project = self.project_service.current_project
            default_lb = f"Agent {project.get_next_id('agent')}" if project else None
            self._create_agent_from_values(lb=default_lb, typ="Subject", note=None, content=None)
            return
        project = self.project_service.current_project
        default_lb = f"Agent {project.get_next_id('agent')}" if project else None
        dialog = AgentDialog(parent=self, default_label=default_lb)
        if dialog.exec() != AgentDialog.Accepted:
            return
        values = dialog.get_values()
        self._create_agent_from_values(
            lb=values['lb'], typ=values['typ'], note=values['note'],
            content=values['content'])

    def _edit_agent(self):
        """Edit an agent from the "Project > Components... > Agent >
        Edit" menu entry (TSK13, FN031). TSK13 review: events view ->
        selection dialog, then the edition dialog; agents view -> the
        edition dialog opens directly on the selected agent card (the
        entry is disabled when no agent card is selected)."""
        if self.tab_bar.currentTab() == "Agents":
            agent = self.agents_page.selected_agent()
            if agent is None:
                self.info_bar.show_message("No agent selected")
                return
            self._edit_agent_entity(agent)
            return
        agent = self._select_agent()
        if agent is None:
            return
        dialog = AgentDialog(entity=agent, parent=self)
        if dialog.exec() != AgentDialog.Accepted:
            return
        values = dialog.get_values()
        result = self.update_agent_usecase.execute(
            entity=agent, lb=values['lb'],
            typ=values['typ'], note=values['note'], content=values['content'])
        if result and result.get('success'):
            self.info_bar.show_message("Agent updated")
            # TSK05: agent label may have changed, refresh tooltips
            self._refresh_all_state_badges()
            self._refresh_agents_view()
            self._update_menu_state()
        else:
            self.info_bar.show_message("Cannot update agent: invalid data")

    def _delete_agent(self):
        """Delete an agent from the "Project > Components... > Agent >
        Delete" menu entry (TSK13, FN031). TSK13 review: events view ->
        selection dialog, then confirmation (RG064); agents view -> the
        selected agent card is deleted directly, with the same
        confirmation (the entry is disabled when no agent card is
        selected)."""
        if self.tab_bar.currentTab() == "Agents":
            agent = self.agents_page.selected_agent()
            if agent is None:
                self.info_bar.show_message("No agent selected")
                return
            self._delete_agent_with_confirmation(agent)
            return
        agent = self._select_agent()
        if agent is None:
            return
        self._delete_agent_with_confirmation(agent)

    def _select_agent(self):
        """Open the agent selection dialog (TSK13) and return the
        selected agent, or None if the dialog was cancelled or no agent
        exists."""
        project = self.project_service.current_project
        if not project or not project.agent:
            self.info_bar.show_message("No agent in the project")
            return None
        dialog = AgentSelectionDialog(project.agent, parent=self)
        if dialog.exec() != AgentSelectionDialog.Accepted:
            return None
        return dialog.get_selected_agent()

    # ---------------------------------------------------------------------
    # Journeys (TSK23, EPC05, FN023/FN024/FN026)
    # ---------------------------------------------------------------------

    def _current_narrative_map(self):
        """Return the current narrative map, or None if no project."""
        project = self.project_service.current_project
        if not project or not project.narrative_map:
            return None
        return project.narrative_map[0]

    def _new_journey(self):
        """Create a journey from "Project > Journeys... > New..." (TSK23,
        FN023). The new journey is automatically activated (RG023)."""
        self._new_journey_dialog()
        self._update_menu_state()

    def _edit_journey(self):
        """Journey management from "Project > Journeys... > Edit" (TSK23
        review, FN024): a selection dialog with Ok (edit the selected
        journey), New... (create a journey, then back to the selection)
        and Delete (stub until TSK25)."""
        narrative_map = self._current_narrative_map()
        if narrative_map is None or not narrative_map.journey:
            self.info_bar.show_message("No journey in the map")
            return
        dialog = JourneySelectionDialog(narrative_map.journey, parent=self)
        while dialog.exec() == JourneySelectionDialog.Accepted:
            action = dialog.get_action()
            if action == "ok":
                journey = dialog.get_selected_journey()
                if journey is None:
                    continue
                edit_dialog = JourneyDialog(entity=journey, parent=self)
                if edit_dialog.exec() != JourneyDialog.Accepted:
                    continue
                values = edit_dialog.get_values()
                result = self.update_journey_usecase.execute(
                    journey, lb=values['lb'], note=values['note'])
                if result and result.get('success'):
                    self.info_bar.show_message("Journey updated")
                else:
                    self.info_bar.show_message("Cannot update journey: invalid data")
                break
            elif action == "new":
                # TSK23 review: creation from the selection dialog, then
                # back to the selection instead of the workspace
                self._new_journey_dialog()
                dialog.refresh(narrative_map.journey)
                continue
            elif action == "delete":
                # TSK25: journey deletion not implemented yet
                self.info_bar.show_message("Journey deletion is not yet implemented")
                continue
            break
        self._update_menu_state()

    def _new_journey_dialog(self):
        """Open the journey creation dialog and create the journey
        (shared by the menu entry and the selection dialog, TSK23)."""
        narrative_map = self._current_narrative_map()
        if narrative_map is None:
            return
        default_lb = f"Journey {narrative_map.get_next_id('journey')}"
        dialog = JourneyDialog(parent=self, default_label=default_lb)
        if dialog.exec() != JourneyDialog.Accepted:
            return
        values = dialog.get_values()
        result = self.create_journey_usecase.execute(lb=values['lb'], note=values['note'])
        if result and result.get('success'):
            self.info_bar.show_message(f"Journey created: {result['entity'].lb}")
        else:
            self.info_bar.show_message("Cannot create journey")

    def _select_journey(self):
        """Open the journey selection dialog (TSK23) and return the
        selected journey, or None if the dialog was cancelled or no
        journey exists."""
        narrative_map = self._current_narrative_map()
        if narrative_map is None or not narrative_map.journey:
            self.info_bar.show_message("No journey in the map")
            return None
        dialog = JourneySelectionDialog(narrative_map.journey, parent=self)
        if dialog.exec() != JourneySelectionDialog.Accepted:
            return None
        return dialog.get_selected_journey()

    def _rebuild_journey_list_menu(self):
        """Rebuild the "Display > Journey > JourneyList" dynamic menu (TSK23):
        one checkable action per journey, checked for the active journey."""
        self.journey_list_menu.clear()
        narrative_map = self._current_narrative_map()
        if narrative_map is None:
            return
        active = narrative_map.get_active_journey()
        for journey in narrative_map.journey:
            action = self.journey_list_menu.addAction(journey.lb)
            action.setCheckable(True)
            action.setChecked(active is not None and journey.id == active.id)
            action.triggered.connect(
                lambda checked=False, j=journey: self._activate_journey(j))

    def _activate_journey(self, journey):
        """Activate a journey from the JourneyList menu (TSK23, FN026)."""
        result = self.activate_journey_usecase.execute(journey)
        if result and result.get('success'):
            self.info_bar.show_message(f"Active journey: {journey.lb}")
        self._update_menu_state()

    def _delete_agent_with_confirmation(self, agent):
        """Delete an agent with confirmation (RG064: the confirmation
        message reports the number of cascaded associations)."""
        # RG064: cascade information in the confirmation message
        association_count = self._count_agent_associations(agent)
        if association_count:
            message = (f"This agent is associated with {association_count} "
                       f"state(s). Delete the agent and all its associations?")
        else:
            message = f"Delete the agent '{agent.lb}'?"
        reply = QMessageBox.question(self, "Confirmation", message,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        result = self.delete_agent_usecase.execute(entity=agent)
        if result and result.get('success'):
            removed = result.get('deleted_associations', 0)
            if removed:
                self.info_bar.show_message(
                    f"Agent deleted ({removed} association(s) removed)")
            else:
                self.info_bar.show_message("Agent deleted")
            # TSK05: cascaded associations may have changed badges
            self._refresh_all_state_badges()
            # TSK08: the agent row disappeared -> refresh the matrix
            self._refresh_agents_view()
            self._update_menu_state()
        else:
            self.info_bar.show_message("Cannot delete agent")

    def _refresh_all_state_badges(self):
        """Refresh the agent badges of all state nodes (TSK05)."""
        if isinstance(self.workspace, EventsWorkspace):
            self.workspace.refresh_all_state_badges()

    def _refresh_agents_view_event_badges(self):
        """Refresh the event badges of all state cards of the agents
        view matrix (TSK13, agents view)."""
        if hasattr(self, 'agents_page') and self.agents_page is not None:
            self.agents_page.refresh_all_event_badges()

    def _count_agent_associations(self, agent) -> int:
        """Count the agent-state associations referencing an agent (RG064)."""
        project = self.project_service.current_project
        if not project:
            return 0
        return sum(
            1 for narrative_map in project.narrative_map
            for rel in narrative_map.state_agent_rel
            if rel.agent_id == agent.id
        )

    def _edit_selected_component(self, component_type: str):
        """Edit the data of the currently selected component (State or Event)."""
        item = self._get_selected_item()
        if item is None:
            self.info_bar.show_message("No component selected")
            return
        if isinstance(item, Connection) or not hasattr(item, 'entity'):
            self.info_bar.show_message("Selected item is not a component")
            return
        entity = item.entity
        # Check consistency between the menu entry and the selected entity
        actual_type = "State" if isinstance(entity, State) else "Event" if isinstance(entity, Event) else None
        if actual_type != component_type:
            self.info_bar.show_message(f"Selected component is not a {component_type}")
            return
        # Open the edition dialog centered on the workspace
        dialog = ComponentDialog(entity, self)
        if hasattr(self, 'workspace') and self.workspace is not None:
            workspace_center = self.workspace.viewport().rect().center()
            dialog.move(self.workspace.mapToGlobal(workspace_center) - QPoint(dialog.width() // 2, dialog.height() // 2))
        if dialog.exec() != ComponentDialog.Accepted:
            return
        values = dialog.get_values()
        result = self.update_component_usecase.execute(
            entity=entity,
            lb=values['lb'],
            note=values['note'],
            content=values['content'],
            typ=values.get('typ')
        )
        if result and result.get('success'):
            item.update_entity_data()
            self.info_bar.show_message(f"{component_type} updated")
            self._update_menu_state()
        else:
            self.info_bar.show_message(f"Cannot update {component_type}: invalid data")

    def _edit_agent_entity(self, agent):
        """Edit a specific agent entity (TSK13, from the agents view
        context menu): opens the edition dialog prefilled with the
        agent."""
        dialog = AgentDialog(entity=agent, parent=self)
        if dialog.exec() != AgentDialog.Accepted:
            return
        values = dialog.get_values()
        result = self.update_agent_usecase.execute(
            entity=agent, lb=values['lb'],
            typ=values['typ'], note=values['note'], content=values['content'])
        if result and result.get('success'):
            self.info_bar.show_message("Agent updated")
            # TSK05: agent label may have changed, refresh tooltips
            self._refresh_all_state_badges()
            self._refresh_agents_view()
            self._update_menu_state()
        else:
            self.info_bar.show_message("Cannot update agent: invalid data")

    def _edit_state_entity(self, state):
        """Edit a specific state entity (TSK13, from the agents view
        context menu): opens the edition dialog prefilled with the
        state, then refreshes the matrix column."""
        dialog = ComponentDialog(state, self)
        if dialog.exec() != ComponentDialog.Accepted:
            return
        values = dialog.get_values()
        result = self.update_component_usecase.execute(
            entity=state,
            lb=values['lb'],
            note=values['note'],
            content=values['content'],
            typ=values.get('typ')
        )
        if result and result.get('success'):
            self.info_bar.show_message("State updated")
            # The label may have changed: refresh the matrix column
            self._refresh_agents_view()
            if isinstance(self.workspace, EventsWorkspace):
                node = self.workspace._find_node_by_entity_id_and_type(
                    state.id, State)
                if node is not None:
                    node.update_entity_data()
            self._update_menu_state()
        else:
            self.info_bar.show_message("Cannot update State: invalid data")


    def _delete_selected_component(self, component_type: str):
        """Delete the currently selected component (State or Event)."""
        item = self._get_selected_item()
        if item is None:
            self.info_bar.show_message("No component selected")
            return

        # Must be a node (has 'entity'), not a Connection
        if isinstance(item, Connection) or not hasattr(item, 'entity'):
            self.info_bar.show_message("Selected item is not a component")
            return

        entity = item.entity

        # Get the narrative map
        if not self.project_service or not self.project_service.current_project:
            self.info_bar.show_message("No project open")
            return
        narrative_map = self.project_service.current_project.narrative_map[0]

        # RG031: the initial state can never be deleted
        if isinstance(entity, State) and entity.typ == "Initial":
            self.info_bar.show_message("The initial state cannot be deleted (RG031)")
            return

        # Determine entity type for arc cleanup
        if isinstance(entity, State):
            entity_type = "State"
            entity_list = narrative_map.state
        elif isinstance(entity, Event):
            entity_type = "Event"
            entity_list = narrative_map.event
        else:
            self.info_bar.show_message("Selected component type is not deletable")
            return

        # SU003 (TSK13 review): confirmation when associated data
        # exists — arcs for both types, plus agent-state associations
        # for states (same rule as the agents view context menu)
        if not self._confirm_component_deletion(entity, entity_type,
                                                narrative_map):
            return

        # Delete all arcs referencing this entity (State_to_event + Event_to_state)
        ArcService.delete_related_arcs(narrative_map, entity.id, entity_type)
        # RG065: cascade the deletion to the agent-state associations
        # referencing the state, and report the count in the info message
        removed_associations = 0
        if isinstance(entity, State):
            cascade = self.remove_state_associations_usecase.execute(state=entity)
            removed_associations = (cascade.get('deleted_associations', 0)
                                    if cascade else 0)

        # Remove the entity from the narrative map's entity list
        entity_list[:] = [e for e in entity_list if e.id != entity.id]

        # Remove the visual node and its attached connections from the workspace
        if isinstance(self.workspace, EventsWorkspace):
            self.workspace.remove_node(item)

        self.node_count -= 1

        # Mark project as modified and update menu state
        self.project_service.set_modified(True)
        self.info_bar.show_message(f"{entity_type} deleted")
        if removed_associations:
            # RG065: information message when the state was associated
            # with at least one agent
            self.info_bar.show_message(
                f"{entity_type} deleted ({removed_associations} agent association(s) removed)")
        # TSK08: a state column may have disappeared or associations may
        # have been cascaded (RG065) -> refresh the agents view matrix
        self._refresh_agents_view()
        self._update_menu_state()

    def _confirm_component_deletion(self, entity, entity_type,
                                    narrative_map) -> bool:
        """SU003: ask for confirmation before deleting a component with
        associated data (TSK13 review: same rule in the events and
        agents views). Arcs count for both types; agent-state
        associations count for states. Returns True when the deletion
        may proceed (no associated data, or the user confirmed)."""
        arc_count = len(ArcService.get_connected_entities(
            narrative_map, entity.id, entity_type))
        association_count = 0
        if isinstance(entity, State):
            association_count = sum(
                1 for rel in narrative_map.state_agent_rel
                if rel.state_id == entity.id)
        if not arc_count and not association_count:
            return True
        message = f"{entity_type} '{entity.lb}' is connected to "
        if arc_count:
            message += f"{arc_count} event(s)"
        if arc_count and association_count:
            message += " and "
        if association_count:
            message += f"{association_count} agent(s)"
        noun = "state" if entity_type == "State" else "event"
        message += f". Delete the {noun} and all its relations?"
        reply = QMessageBox.question(self, "Confirmation", message,
                                     QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes

    def _delete_state_entity(self, state):
        """Delete a specific state entity (TSK13, from the agents view
        context menu). SU003: confirmation when associated data exists;
        cascades arcs and agent-state associations (RG065); RG031
        protects the initial state (the menu entry is disabled for it,
        this guard is a safety net)."""
        if not self.project_service or not self.project_service.current_project:
            self.info_bar.show_message("No project open")
            return
        narrative_map = self.project_service.current_project.narrative_map[0]

        # RG031: the initial state can never be deleted
        if state.typ == "Initial":
            self.info_bar.show_message("The initial state cannot be deleted (RG031)")
            return

        # SU003: confirmation when the state has associated data (arcs
        # or agent-state associations)
        if not self._confirm_component_deletion(state, "State",
                                                narrative_map):
            return

        # Delete all arcs referencing this state (State_to_event + Event_to_state)
        ArcService.delete_related_arcs(narrative_map, state.id, "State")
        # RG065: cascade the deletion to the agent-state associations
        cascade = self.remove_state_associations_usecase.execute(state=state)
        removed_associations = (cascade.get('deleted_associations', 0)
                                if cascade else 0)

        # Remove the entity from the narrative map's entity list
        narrative_map.state[:] = [
            s for s in narrative_map.state if s.id != state.id]

        # Remove the visual node and its attached connections
        if isinstance(self.workspace, EventsWorkspace):
            item = self.workspace._find_node_by_entity_id_and_type(
                state.id, State)
            if item is not None:
                self.workspace.remove_node(item)

        self.node_count -= 1

        # Mark project as modified and update menu state
        self.project_service.set_modified(True)
        self.info_bar.show_message("State deleted")
        if removed_associations:
            # RG065: information message when the state was associated
            # with at least one agent
            self.info_bar.show_message(
                f"State deleted ({removed_associations} agent association(s) removed)")
        # The state column disappeared and associations may have been
        # cascaded (RG065) -> refresh the agents view matrix
        self._refresh_agents_view()
        self._update_menu_state()


    def _edit_selected_relation(self):
        """Edit the currently selected relation (not yet implemented)."""
        self.info_bar.show_message("Editing relation is not yet implemented")


    def _delete_selected_relation(self):
        """Delete the currently selected relation (connection)."""
        item = self._get_selected_item()
        if item is None:
            self.info_bar.show_message("No relation selected")
            return

        if not isinstance(item, Connection):
            self.info_bar.show_message("Selected item is not a relation")
            return

        # Get the narrative map
        if not self.project_service or not self.project_service.current_project:
            self.info_bar.show_message("No project open")
            return
        narrative_map = self.project_service.current_project.narrative_map[0]

        # Delete the business relation entity (arc) from the data model
        if not item.delete_relation_entity(narrative_map):
            self.info_bar.show_message("Cannot delete relation: no business entity associated")
            return

        # Remove the visual connection from the workspace
        if isinstance(self.workspace, EventsWorkspace):
            self.workspace.remove_connection(item)

        # Mark project as modified and update menu state
        self.project_service.set_modified(True)
        self.info_bar.show_message("Relation deleted")
        # TSK13: the agent badge of the events state node and the
        # event badges of the agents-view state card may have changed
        self._refresh_all_state_badges()
        self._refresh_agents_view_event_badges()
        self._update_menu_state()


    def _show_changelog(self):
        ChangeLogDialog(self.change_log_service, self).exec()


    def _show_about(self):
        AboutDialog(self.about_service, self).exec()
