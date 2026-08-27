# Planoscript ::: User Interface Specification

## Document Version
- **Version**: 2.0
- **Date**: 27-08-2026
- **Status**: Retrospective update to reflect the current implementation

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
      - Journey - Not implemented
      - Relations - Not implemented
      - Chapters - Not implemented
    - **Components...**:
      - Agent - Functional
      - State - Functional
      - Event - Functional
    - **Relations...**:
      - Link State and Event - Functional

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
  - "Relations" tab - *Not implemented*
  - "Chapters" tab - *Not implemented*

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

- **Visual Elements**:

  - **Nodes (Components)**:
    - **Files**: 
      - `./src/ui/nodes/base_node.py` (BaseNode)
      - `./src/ui/nodes/agent_node.py` (AgentNode)
      - `./src/ui/nodes/state_node.py` (StateNode)
      - `./src/ui/nodes/event_node.py` (EventNode)
    - **Implemented types**: Agent, State, Event.
    - **Not implemented types**: Time Reference, Spatial Reference.
    - **Shape**: Rectangle (120x80px by default).
    - **Style**:
      - Background: `#f0f0f0` (light gray).
      - Border: `1px solid #808080` (medium gray).
      - Shadow: None (to be implemented).
      - Selection: Background `#dce6ff` (very light blue), border `#0078d7` (blue).
    - **Content**:
      - **Name**: Text at the top, Arial 10pt **bold**.
      - **Description**: *Not displayed* - to be implemented.
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

### Partially Implemented
- [ ] Components bar (exists but not integrated)
- [ ] Journeys bar (exists but not integrated)
- [ ] Tab bar (exists but only "Journeys" is active)
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
- [ ] "Relations" view
- [ ] "Chapters" view
- [ ] Deletion of nodes/relations


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
