# Planoscript ::: User Interface Specification

## Document Version
- **Version**: 2.2
- **Date**: 28-10-2026
- **Status**: Retrospective update to reflect the current implementation (latest redesign + EPC01–EPC04: agent management, agent-state associations, agents view; TSK13: mechanical review of agent/association creation and edition)

---

## General Interface Architecture

### Layout
- **Type**: Main vertical layout (QVBoxLayout) with distinct sections.
- **Structure**:
  - **Top**: Integrated menu bar (QMenuBar).
  - **Center**: Main workspace (JourneyWorkspace).
  - **Bottom**: Information bar (75%) + Zoom bar (25%) - *Zoom bar currently disabled*.

> **Note**: The sidebars (components on the left, journeys on the right) are implemented but **not integrated** into the main window.

---

## Interface Components

### 1. Application Window Menu Bar
- **Type**: Native QMenuBar.
- **Position**: At the top of the window.
- **Style**:
  - Background: `#ffffff` (white).
  - Font: Arial, 9pt.
  - Text color: `#000000` (black).
  - Selected items: Background `#404040`, text `#ffffff`.

- **Available Menus**:
  - **File**:
    - New Project... (Ctrl+N)
    - Open... (Ctrl+O)
    - Close (Ctrl+W)
    - Save (Ctrl+S) - Disabled if project not modified
    - Save as... (Ctrl+Shift+S)
    - Export Map - Not implemented
    - Import Map - Not implemented
    - Recent Projects... - Not implemented
    - Quit (Ctrl+Q)
  
  - **Edit**:
    - Undo (Ctrl+Z) - Not implemented
    - Redo (Ctrl+Y) - Not implemented
    - History - Not implemented
    - Cut (Ctrl+X) - Not implemented
    - Copy (Ctrl+C) - Not implemented
    - Paste (Ctrl+V) - Not implemented
    - Delete (Del) - Not implemented

  - **Display**:
    - **Journey**:
      - JourneyList - Not implemented
    - **Zoom**:
      - Zoom in (Ctrl+=) - Not implemented
      - Zoom out (Ctrl+-) - Not implemented
      - Reset (Ctrl+0) - Not implemented

  - **Project**:
    - **View**:
      - Journey - Not implemented (the view is activated via the tab bar, not via this menu)
      - Agents - Not implemented (the view is activated via the tab bar; SU009; the Relations and Chapters entries are leftovers removed from the MVP)
    - **Components...**:
      - **Agent**:
        - New... - Functional, behavior depends on the active view (FN031, TSK13 + TSC review 28-10-2026):
          - "Journey" view: opens the "New Agent" dialog directly, pre-filled with a default label "Agent {id}" (like states/events), editable in the dialog.
          - "Agents" view: creates the agent directly in the matrix row, with the default label (no dialog).
          - Enabled as soon as a project is open, in both views.
        - Edit - Functional, behavior depends on the active view (TSK13 + TSC review 28-10-2026):
          - "Journey" view: opens an agent selection dialog, then the pre-filled "New Agent" dialog; enabled as soon as at least one agent exists (the selection is made in the dialog).
          - "Agents" view: opens the edition dialog directly on the selected agent card; disabled when no agent card is selected.
        - Delete - Functional, behavior depends on the active view (TSK13 + TSC review 28-10-2026):
          - "Journey" view: agent selection dialog, then a confirmation showing the number of cascaded associations (RG064); enabled as soon as at least one agent exists.
          - "Agents" view: deletes the agent whose card is selected directly, with the same RG064 confirmation; disabled when no agent card is selected.
      - Global menu (menu bar): accessible from both the "Journey" and "Agents" views; the agent card context menu ("Agents" view) offers the same "Edit Agent"/"Delete Agent" actions, aligned on the global menu.
      - **State**:
        - New... - Functional
        - Edit - Not implemented (enabled when a State node is selected)
        - Delete - Not implemented (enabled when a State node is selected)
      - **Event**:
        - New... - Functional
        - Edit - Not implemented (enabled when an Event node is selected)
        - Delete - Not implemented (enabled when an Event node is selected)
    - **Relations...**:
      - Connect State and Event - Functional
      - Associate agents with State - Functional (FN030, SU008: association dialog from the menu or the state context menu)
      - Edit - Not implemented (enabled when a relation is selected)
      - Delete - Not implemented (enabled when a relation is selected)

  - **About**:
    - Change Log - Functional
    - About Planoscript - Functional

- **Behavior**:
  - Menus are disabled when no project is open (RG007).
  - The "Save" menu is disabled if the project is not modified.


### 2. Window Title Bar
- **Content**:
  - **Title**: Dynamic format: `"Planoscript : {project_name} ({file_path})"` or `"Planoscript : start your new project"` if no project is open.
  - **Style**: Native operating system window title.


### 3. Components Bar (Left) - *Implemented but not integrated*
- **File**: `./src/ui/widgets/components_toolbar.py`
- **Description**: Sidebar for managing component types.
- **Width**: 40px.
- **Style**:
  - Background: `#f8f8f8`.
  - Right border: `1px solid #ddd`.

- **Elements**: Buttons with SVG icons (24x24px):
  - "Time Reference" (icon: `./src/ui/asset/icon/calendar.svg`)
  - "Spatial Reference" (icon: `./src/ui/asset/icon/map.svg`)
  - "Agent" (icon: `./src/ui/asset/icon/agent.svg`)
  - "State" (icon: `./src/ui/asset/icon/state.svg`)
  - "Event" (icon: `./src/ui/asset/icon/event.svg`)
  - "Relation" (icon: `./src/ui/asset/icon/relation.svg`)

- **Button Style**:
  - Background: `#ffffff`.
  - Border: `1px solid #ddd`.
  - Hover: Background `#AABBCC`, border `#AABBCC`.
  - Pressed: Background `#AABBCC`, border `2px solid #555555`.

- **Behavior**:
  - Emits a `component_selected` signal with the component type.
  - Emits a `relation_selected` signal for the Relation button.


### 4. Journeys Bar (Right) - *Implemented but not integrated*
- **File**: `./src/ui/widgets/journeys_toolbar.py`
- **Description**: Sidebar for managing narrative map journeys.
- **Width**: 40px.
- **Style**:
  - Background: `#f8f8f8`.
  - Left border: `1px solid #ddd`.

- **Elements**:
  - **Action Buttons** (at the top):
    - "Add" (icon: `./src/ui/asset/icon/addJourney.svg`) → Creates a new journey.
    - "Delete" (icon: `./src/ui/asset/icon/delJourney.svg`) → Deletes the selected journey.
      - *Disabled if only one journey remains*.
  - **Separator**: Horizontal line (`#ccc`, 1px).
  - **Journey List**:
    - Each journey is a button with icon `./src/ui/asset/icon/journey.svg`.
    - **Name**: Displayed in the tooltip.
    - **State**: Button checked if the journey is active.
    - **Color**: Background `#AABBCC` when selected.

- **Behavior**:
  - Clicking on a journey **displays** its components/relations in the workspace.
  - **Default**: The first journey is always displayed and cannot be deleted.


### 5. Tab Bar (Center) - *Partially implemented*
- **File**: `./src/ui/widgets/tab_bar.py`
- **Description**: Tab bar for switching between project views.
- **Height**: 40px.
- **Style**:
  - Background: `#f8f8f8`.
  - Font: Arial, 9pt.

- **Elements**:
  - "Journeys" tab - **Active by default**
  - "Agents" tab - **Functional** (second workspace, agents × states matrix - SU009, TSK07–TSK15)
  - The "Relations" and "Chapters" tabs are leftovers from an earlier version: they are not part of the MVP and are removed from the specification.

- **Tab Style**:
  - Background: `#f8f8f8`.
  - Bottom border: `2px solid transparent` (transparent when not selected).
  - Hover: Background `#e0e0e0`.
  - Selected: Background `#ffffff`, text in **bold**, bottom border visible.


### 6. Workspace (Center)
- **File**: `./src/ui/views/journey_workspace.py`
- **Description**: Main workspace for viewing and editing the narrative map.
- **Class**: `JourneyWorkspace` (inheriting from `QGraphicsView`).

- **Style**:
  - Background: `#ffffff`.
  - Border: None (integrated in QGraphicsView).

- **Implemented Features**:
  
  - **Alignment Grid**:
    - **Main grid**: 20x20 pixel step, color `#e0e0e0`.
    - **Sub-grid**: 4x4 step squares (80x80 pixels), color `#808080`.
    - **Visibility**: Always visible.
    - **Snap**: *Not yet implemented* - nodes do not automatically snap.
    - **Optimization**: The grid is dynamically redrawn only for the visible area.

  - **Scrolling**:
    - **Type**: Infinite scrolling (theoretically).
    - **Scroll bars**: Always visible.
    - **Scroll bar style**:
      - Background: `#f0f0f0`.
      - Handle: `#c0c0c0`.
      - Buttons: `#e0e0e0`.
    - **Auto-scroll**: When the mouse is near the edges (50px margin), the view scrolls automatically.
    - **Scene limit**: 4000x4000 pixels by default, extends dynamically when nodes exceed it.

  - **Zoom**:
    - **Range**: 10% to 300% (via `ZoomBar`).
    - **Behavior**: *Not connected* - zoom controls exist but are not connected to the view.
    - **Shortcuts**: *Not implemented* (Ctrl+, Ctrl-, Ctrl+0).

  - **Drag and Drop**:
    - **Enabled** for nodes and relations.
    - **Behavior**:
      - Nodes can be moved freely.
      - *Nodes do not snap to the grid* during movement.
      - The scene extends automatically when a node is dragged toward the edges.

  - **Context Menu** (right click; unavailable while a relation creation is in progress):
    - On the grid (outside nodes and relations): "New State", "New Event", "New Agent" (TSK13: opens the "New Agent" dialog directly, without switching views), "Connect State and Event".
    - On a State node: "Edit State", "Associate agents..." (FN030), "Show in agents view" (TSK10/RG067, disabled when the state has no agent association), "Delete State" (disabled for the initial state, RG031; **SU003 confirmation when the state is connected to at least one event and/or associated with at least one agent** — TSC review 28-10-2026, arcs + RG065 cascade).
    - On an Event node: "Edit Event", "Delete Event" (**SU003 confirmation when the event is connected to at least one state** — TSC review 28-10-2026, arcs cascade).
    - On a relation: "Edit Relation", "Delete Relation".
    - The click selects the item under the cursor before the menu opens, so the actions apply to the clicked item.

- **Visual Elements**:

  - **Nodes (Components)**:
    - **Files**: 
      - `./src/ui/nodes/base_node.py` (BaseNode)
      - `./src/ui/nodes/agent_node.py` (AgentNode)
      - `./src/ui/nodes/state_node.py` (StateNode)
      - `./src/ui/nodes/event_node.py` (EventNode)
    - **Implemented types**: Agent, State, Event.
    - **Not implemented types**: Time Reference, Spatial Reference.
    - **Shape**: Rectangle (80x40px by default).
    - **Style**:
      - Background: `#f0f0f0` (light gray).
      - Border: `1px solid #808080` (medium gray).
      - Shadow: None (to be implemented).
      - Selection: Background `#dce6ff` (very light blue), border `#0078d7` (blue).
    - **Content**:
      - **Name**: Text at the top, Arial 10pt **bold**.
      - **Description**: *Not displayed* - to be implemented.
    - **Badge on State nodes** (TSK05):
      - **Agent badge** (centered on the bottom-right corner of the card, straddling the X and Y edges of the outline — TSK17, TSC 28-10-2026): pill with a counter of the agents associated with the state (FN030); fill `#E5C07B`, border `#F0F0F0`, text `#1E1E1E`; tooltip "Agents: ...".
      - *No event badge in the journey view* (TSC review 28-10-2026, feedback n°1: the connections are visible there, the badges would overload the nodes) — the event badges are displayed on the state cards of the **agents view** (see section 6.bis).
    - **Anchor Points**:
      - 4 points (top, bottom, left, right) - *Not yet visually implemented*.
      - Should be visible on hover (8px squares, color `#4CAF50`).

  - **Relations (Connections)**:
    - **File**: `./src/ui/nodes/connection.py`
    - **Class**: `Connection` (inheriting from `QGraphicsPathItem`).
    - **Style**:
      - **Directional**: Line with arrow, color to be defined.
      - **Non-directional**: Simple line, color `#999`.
      - **Thickness**: 2px.
    - **Annotation**:
      - *Not implemented* - text in the middle of the relation.
      - Should have a semi-transparent white background for readability.


### 6.bis. Agents View (Secondary Workspace) - *Implemented (TSK07–TSK15)*

- **File** : `./src/ui/views/agents_workspace.py`
- **Description** : Second dedicated workspace for the associations between the project agents and the states of the current narrative map. Accessible via the "Agents" tab of the tab bar. `QGraphicsView` (like the journey view, TSK15). Agent and state creation/edition are possible from this view via the global menu and the context menus (TSK13).
- **Representation** : Agents × states matrix in graphical view.
  - One card per project agent (left column, rows); one card per state of the current narrative map (top row, columns); one 20×20 checkbox at each intersection.
  - 80×40 cards rendered like the journey view nodes (surface `#2D2D2D`, outline tinted by type: gold `#E5C07B` for states, copper `#D19A66` for agents); label truncated to 8 characters, immediate tooltip on hover.
  - Background grid 120×80 (config `agents_view_cell_width`/`_height`): each card and each checkbox is centered in its cell (20 px margins for cards, 50/30 px for checkboxes). The grid is redrawn over the visible area (journey view pattern) and the scene extends right/down only: the matrix stays anchored at the top-left corner.
  - The column order follows business rule RG068 (creation order by default, manual reordering persisted by drag and drop, initial state pinned to the first column with a rejection message in the info bar).
  - A checked cell materializes an agent-state association (SU008). Editing is done by clicking the checkbox (TSK09).
- **Card selection (TSC review 28-10-2026)**: like in the journey view, a click on a card selects it (a single card selected at a time, across agents and states); the selection is shown by a **dashed outline in the type color** (charter 98: selection > hover > type). A click on empty space clears the selection. Drag-and-drop reordering (RG068) is preserved: the click selects, the drag reorders. A right-click on a card selects it before opening the context menu. The selection drives the activation of the "Edit"/"Delete" entries of the Agent submenu in the "Agents" view.
- **Event badges on state cards (TSK13, agents view only)**: two pills with counters, same style as the journey agent badge but in copper `#D19A66` (Event type tint), **vertically centered and straddling the left and right edges** of the card — same coordinates as the connection ports (incoming/outgoing) of states in the journey view (TSC repositioning 28-10-2026): **left** badge = number of **source** events (arcs `Event_to_state` pointing to this state), **right** badge = number of **target** events (arcs `State_to_event` leaving this state). Tooltip "Events (in): ..." / "Events (out): ...". Hidden at 0; refreshed dynamically on relation creation/deletion and on matrix refresh. Agent cards carry no event badge. In the journey view, state nodes carry only the agent badge (TSC review 28-10-2026, feedback n°1).
- **Focus contract (cross-view navigation, TSK10/RG067, extended by TSK13)** :
  - Method common to both views: "focus on an entity" (target state → highlight + scroll of the column, translucent band on the cell; target agent → highlight of the associated state nodes in the journey view with the rest of the graph dimmed; target state from the agents view → switch to the journey view and focus on the state node, TSK13).
  - The focus is a temporary visual state (RG067): no modified marking, no persistence. A click on empty space or the Escape key releases it.
- **Context Menus (TSK13, aligned on the global menu by the TSC review 28-10-2026)** :
  - Agent card: "Edit Agent" and "Delete Agent" behave like the global menu in the "Agents" view (direct edition/deletion of the selected card — the right-click selects the clicked card; "Delete Agent" with the RG064 confirmation), "Show in journey view" (TSK10).
  - State card: "Edit State" (pre-filled dialog), "Delete State" (disabled for the initial state, RG031; confirmation when arcs or associations exist, RG065 cascades), "Show in journey view" (switches to the journey view + focuses the node, extension of the TSK10/RG067 contract).
  - Grid (outside the matrix): "New Agent" (direct creation in the matrix row, stays in the agents view), "New State" (stays in the agents view; the new column appears in the matrix), "New Event" (creates the node in the journey view, switches to the journey view and selects the node — same behavior as point 03).
- **Event creation from the agents view (TSK13)**: whether the creation starts from the global menu "Project > Components... > Event > New..." or from the grid context menu, the view switches to "Journey" once the event is created, and the created node is selected. Creating an agent or a state from the agents view does not switch the view.
- **Roles** :
  - Display the agent-state associations of the current map.
  - Edit associations (check/uncheck).
  - Manage project agents via the global menu ("Project > Components... > Agent" submenu: New.../Edit/Delete — FN031, TSK13) and via the context menus (create/edit/delete an agent, edit/delete a state).
### 7. Information Bar (Bottom Left)
- **File**: `./src/ui/widgets/info_bar.py`
- **Description**: Displays contextual information about the selected object.
- **Width**: 80% of the bottom area (4/5 of the layout).
- **Height**: 30px.
- **Style**:
  - Background: `#f0f0f0`.
  - Top border: `1px solid #ddd`.

- **Elements**:
  - **Text**: Label with style `font-size: 10pt; color: #666;`.
  - **Content**:
    - If a **component** is selected: Displays a custom message.
    - If a **relation** is selected: Displays a custom message.
    - If **nothing is selected**: Empty.


### 8. Zoom Bar (Bottom Right) - *Disabled*
- **File**: `./src/ui/widgets/zoom_bar.py`
- **Description**: Zoom level control.
- **Width**: 20% of the bottom area (1/5 of the layout).
- **Height**: 30px.
- **Style**:
  - Background: `#f0f0f0`.
  - Top border: `1px solid #ddd`.
  - Left border: `1px solid #ddd`.

- **Elements** (from left to right):
  - **"Zoom Out" Button**:
    - Text: "-"
    - Action: Decreases zoom by 10% - *Not connected*.
    - Shortcut: Ctrl - - *Not implemented*.
  - **Zoom Slider**:
    - Type: Horizontal `QSlider`.
    - Range: 10% to 190% (internal value, corresponds to 10%-300% after mapping).
    - Default value: 100%.
    - Increment: 10%.
    - Tooltip: Displays the current percentage.
  - **"Zoom In" Button**:
    - Text: "+"
    - Action: Increases zoom by 10% - *Not connected*.
    - Shortcut: Ctrl + - *Not implemented*.
  - **"Reset" Button**:
    - *Not implemented* in the interface.
    - Shortcut: Ctrl 0 - *Not implemented*.
  - **Percentage Display**:
    - *Not implemented* - replaced by the slider tooltip.


### 9. Welcome Message
- **Description**: Displayed when no project is open.
- **Content**:
  ```html
  <h2>Build the plan of your new script.</h2>
  <p>Start by <a>creating a new project</a> or open an existing project.</p>
  ```
- **Style**: Centered text with 40px padding.
- **Behavior**: The "creating a new project" link triggers `_create_project()`.


---

## Implemented Features

### Functional
- [x] Creating a new project
- [x] Opening an existing project
- [x] Closing a project with confirmation
- [x] Saving a project (Ctrl+S)
- [x] Save as... (Ctrl+Shift+S)
- [x] Displaying the welcome message
- [x] Creating nodes (Agent, State, Event) via menu
- [x] Creating State-Event relations
- [x] Simple selection of nodes and relations
- [x] Moving nodes in the workspace
- [x] Auto-scrolling when moving toward edges
- [x] Dynamic scene extension
- [x] Grid display (20px + 80px)
- [x] Contextual information bar
- [x] Management of project modified state
- [x] "About" and "Change Log" dialogs
- [x] Project agent management (create, edit, delete with RG064 cascade — FN031, TSK01/TSK02; "Agent" submenu New.../Edit/Delete with selection dialog — TSK13)
- [x] Agent-state associations from the journey view ("Associate agents..." dialog — FN030, TSK04)
- [x] Agent badges on state nodes in the journey view (TSK05)
- [x] Event badges (source/target) on state cards in the agents view (TSK13; absent from the journey view — TSC review 28-10-2026)
- [x] "Agents" view: agents × states matrix in graphical view, cell editing, RG068 order, 120×80 grid (TSK07–TSK15, SU008/SU009)
- [x] Cross-view navigation with focus (RG067 — TSK10, extended state→journey by TSK13)
- [x] Context menus of the journey and agents views (agent create/edit/delete, state edit/delete, switch to journey after event creation — TSK13)

### Partially Implemented
- [ ] Components bar (exists but not integrated)
- [ ] Journeys bar (exists but not integrated)
- [ ] Tab bar (both "Journeys" and "Agents" tabs are active)
- [ ] Zoom bar (exists but not connected)
- [ ] Time Reference nodes (class not implemented)
- [ ] Spatial Reference nodes (class not implemented)

### Not Implemented
- [ ] Grid snap
- [ ] Visible anchor points on nodes
- [ ] Annotation on relations
- [ ] Functional zoom (shortcuts and controls)
- [ ] Complete infinite scrolling (limited to 4000x4000)
- [ ] Multiple selection
- [ ] Copy/Paste/Cut
- [ ] Undo/Redo
- [ ] Modification history
- [ ] Map Export/Import
- [ ] Recent projects
- [ ] Deletion of relations (State/Event node deletion is functional via the context menus with the SU003 confirmation — TSK13 + TSC review 28-10-2026)


---

## File Structure

```
./src/ui/
├── main_window.py          # Main window
├── views/
│   └── journey_workspace.py # Workspace
├── widgets/
│   ├── components_toolbar.py # Components bar (not integrated)
│   ├── journeys_toolbar.py   # Journeys bar (not integrated)
│   ├── tab_bar.py           # Tab bar (partially integrated)
│   ├── info_bar.py          # Information bar (integrated)
│   └── zoom_bar.py          # Zoom bar (not integrated)
├── nodes/
│   ├── base_node.py         # Base class for nodes
│   ├── agent_node.py        # Agent node
│   ├── state_node.py        # State node
│   ├── event_node.py        # Event node
│   └── connection.py         # Connections between nodes
└── dialogs/
    ├── about_dialog.py       # About dialog
    └── change_log_dialog.py  # Change Log dialog
```


---

## Design Notes

1. **Architecture**: The application follows a layered architecture with separation between:
   - **UI** (`./src/ui/`): Visual components
   - **Core** (`./src/core/`): Models and services
   - **Use Cases** (`./src/usecases/`): Application logic
2. **MVC Pattern**: UI classes use services and use cases to manipulate data.
3. **Scalability**: The sidebars and zoom bar are implemented as separate widgets, ready to be integrated.
4. **Style**: The application uses Qt Style Sheets (QSS) for consistent rendering.
5. **Internationalization**: Texts are currently in English only. A refactoring for i18n is recommended.


---

## Recommended Next Steps

1. **Integrate the sidebars** into `main_window.py`
2. **Connect the zoom** between `ZoomBar` and `JourneyWorkspace`
3. **Implement grid snap**
4. **Add anchor points** on nodes
5. **Connect the tab bar** to switch views
6. **Add the missing features** (multiple selection, copy/paste, etc.)
