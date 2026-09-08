# Test Specification - Planoscript

## Document Version
- **Version**: 1.0
- **Date**: 08-09-2026
- **Status**: Specifications for FN001 to FN029

---

### ID : T-001

### Title : Test FN001

**Preconditions :**
- The application is installed on a Windows PC
- The operating system meets the minimum requirements
- No instance of the application is already running

**Steps :**
1. Launch the application via its executable or desktop shortcut
2. Wait for the application window to appear

**Expected Result :**
- The application displays a welcome screen
- The welcome screen presents options including the creation of a new project

---

### ID : T-002

### Title : Test FN002

**Preconditions :**
- The application is running
- A project is open
- The project has unsaved changes

**Steps :**
1. Select menu "Files > Quit" or use shortcut Ctrl+Q
2. Observe the confirmation dialog
3. Select "Cancel"

**Expected Result :**
- A confirmation dialog appears with options "Save", "Do not save", "Cancel"
- The project remains open
- The application continues running

---

### ID : T-003

### Title : Test FN002 (Save and Quit)

**Preconditions :**
- The application is running
- A project is open
- The project has unsaved changes

**Steps :**
1. Select menu "Files > Quit" or use shortcut Ctrl+Q
2. Select "Save" in the confirmation dialog
3. Confirm the save location if prompted

**Expected Result :**
- The project is saved to the specified location
- The application closes completely

---

### ID : T-004

### Title : Test FN002 (Quit without Saving)

**Preconditions :**
- The application is running
- A project is open
- The project has unsaved changes

**Steps :**
1. Select menu "Files > Quit" or use shortcut Ctrl+Q
2. Select "Do not save" in the confirmation dialog

**Expected Result :**
- The application closes completely
- The unsaved changes are discarded

---

### ID : T-005

### Title : Test FN003

**Preconditions :**
- The application is running

**Steps :**
1. Select menu "About > Change Log"

**Expected Result :**
- A dialog box appears
- The dialog displays a list of application versions
- Each version entry includes the associated changes

---

### ID : T-006

### Title : Test FN004

**Preconditions :**
- The application is running

**Steps :**
1. Select menu "About > About Planoscript"

**Expected Result :**
- A dialog box appears
- The dialog displays general information about the application (version, name, etc.)

---

### ID : T-007

### Title : Test FN005 (Menu)

**Preconditions :**
- The application is running
- The welcome screen is displayed or no project is open

**Steps :**
1. Select menu "Files > New Project..." or use shortcut Ctrl+N

**Expected Result :**
- A new project is created
- The project is named "New project"
- The project contains a narrative map named "Main narrative map"
- The project is unsaved (in memory only)

---

### ID : T-008

### Title : Test FN005 (Welcome Screen)

**Preconditions :**
- The application is running
- The welcome screen is displayed

**Steps :**
1. Click on the "New Project" option on the welcome screen

**Expected Result :**
- A new project is created
- The project is named "New project"
- The project contains a narrative map named "Main narrative map"
- The project is unsaved (in memory only)

---

### ID : T-009

### Title : Test FN005 (Replace Current Project)

**Preconditions :**
- The application is running
- A project is already open and has unsaved changes

**Steps :**
1. Select menu "Files > New Project..." or use shortcut Ctrl+N
2. Observe the save confirmation dialog

**Expected Result :**
- A save confirmation dialog appears
- After confirmation, the current project is replaced by the new one
- The new project is named "New project"

---

### ID : T-010

### Title : Test FN006 (Valid File)

**Preconditions :**
- The application is running
- A valid project file exists on the file system

**Steps :**
1. Select menu "Files > Open..." or use shortcut Ctrl+O
2. Navigate to and select a valid project file
3. Click "Open"

**Expected Result :**
- The selected project opens successfully
- The project content is displayed correctly

---

### ID : T-011

### Title : Test FN006 (Invalid File)

**Preconditions :**
- The application is running
- An invalid project file exists on the file system
- A project is already open

**Steps :**
1. Select menu "Files > Open..." or use shortcut Ctrl+O
2. Navigate to and select an invalid project file
3. Click "Open"

**Expected Result :**
- A clear error message is displayed
- The current project remains unchanged and open

---

### ID : T-012

### Title : Test FN006 (Modified Project)

**Preconditions :**
- The application is running
- A project is open and has unsaved changes
- A valid project file exists on the file system

**Steps :**
1. Select menu "Files > Open..." or use shortcut Ctrl+O
2. Navigate to and select a valid project file
3. Observe the save confirmation dialog

**Expected Result :**
- A save confirmation dialog appears
- After confirmation, the new project opens

---

### ID : T-013

### Title : Test FN007

**Preconditions :**
- The application is running
- Multiple projects have been previously saved or opened
- The "Recent Projects" menu is populated

**Steps :**
1. Select menu "Files > Recent Projects..."
2. Select a project from the list

**Expected Result :**
- The selected project opens successfully
- The project content is displayed correctly

---

### ID : T-014

### Title : Test FN007 (Non-existent File)

**Preconditions :**
- The application is running
- A project that was previously opened no longer exists on the file system

**Steps :**
1. Select menu "Files > Recent Projects..."
2. Attempt to select a project that no longer exists

**Expected Result :**
- The non-existent file is not displayed in the recent projects list
- If selected, an error message is displayed

---

### ID : T-015

### Title : Test FN008 (Existing File)

**Preconditions :**
- The application is running
- A project is open
- The project is already associated with a file
- The project has been modified since the last save

**Steps :**
1. Select menu "Files > Save" or use shortcut Ctrl+S

**Expected Result :**
- The project is saved to the existing file location
- No save dialog appears
- The project is marked as unmodified
- The project is added to the recent projects list

---

### ID : T-016

### Title : Test FN008 (New File)

**Preconditions :**
- The application is running
- A project is open
- The project has never been saved
- The project has been modified

**Steps :**
1. Select menu "Files > Save" or use shortcut Ctrl+S
2. Specify a name and location in the save dialog

**Expected Result :**
- The project is saved to the specified location
- The project is marked as unmodified
- The project is added to the recent projects list

---

### ID : T-017

### Title : Test FN008 (Unmodified Project)

**Preconditions :**
- The application is running
- A project is open
- The project is associated with a file
- The project has no unsaved changes

**Steps :**
1. Observe the "Save" menu option

**Expected Result :**
- The "Save" action is disabled

---

### ID : T-018

### Title : Test FN009

**Preconditions :**
- The application is running
- A project is open
- The project may or may not have been saved before

**Steps :**
1. Select menu "Files > Save As..." or use shortcut Ctrl+Shift+S
2. Specify a new name and/or location in the save dialog

**Expected Result :**
- The project is saved to the new location with the new name
- The saved copy becomes the current project
- The project is added to the recent projects list

---

### ID : T-019

### Title : Test FN010 (Unmodified Project)

**Preconditions :**
- The application is running
- A project is open
- The project has no unsaved changes

**Steps :**
1. Select menu "Files > Close" or use shortcut Ctrl+W

**Expected Result :**
- The project closes
- No project is open (return to welcome screen)

---

### ID : T-020

### Title : Test FN010 (Modified Project)

**Preconditions :**
- The application is running
- A project is open
- The project has unsaved changes

**Steps :**
1. Select menu "Files > Close" or use shortcut Ctrl+W
2. Observe the confirmation dialog
3. Select "Cancel"

**Expected Result :**
- A confirmation dialog appears with options "Save", "Do not save", "Cancel"
- The project remains open

---

### ID : T-021

### Title : Test FN010 (Save and Close)

**Preconditions :**
- The application is running
- A project is open
- The project has unsaved changes

**Steps :**
1. Select menu "Files > Close" or use shortcut Ctrl+W
2. Select "Save" in the confirmation dialog

**Expected Result :**
- The project is saved
- The project closes
- No project is open (return to welcome screen)

---

### ID : T-022

### Title : Test FN011

**Preconditions :**
- The application is running
- A project is open
- The project editing window is available

**Steps :**
1. Open the project editing window
2. Modify the project label (name)
3. Save the changes

**Expected Result :**
- The project label is updated
- The last modification date is updated
- The project is marked as modified

---

### ID : T-023

### Title : Test FN012 (Direct Editing)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed
- The map label is editable

**Steps :**
1. Directly edit the narrative map label in the visualization space
2. Change the label text
3. Confirm the change

**Expected Result :**
- The narrative map label is updated
- The map is marked as modified
- The project is marked as modified
- The last modification date is updated

---

### ID : T-024

### Title : Test FN012 (Dialog Box)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed

**Steps :**
1. Open the map renaming dialog box
2. Enter a new label
3. Confirm the change

**Expected Result :**
- The narrative map label is updated
- The map is marked as modified
- The project is marked as modified
- The last modification date is updated

---

### ID : T-025

### Title : Test FN013

**Preconditions :**
- The application is running
- A project is open
- A narrative map with journeys and components exists

**Steps :**
1. Select menu "Files > Export Map"
2. Specify export location if prompted

**Expected Result :**
- A folder named after the map name is created at the specified location
- The folder contains an index file and all necessary pages for hypertext navigation
- The document is standalone and displays correctly in Chrome, Firefox, and Edge
- The home page offers the choice of reading mode (only "by journey" available in MVP)
- The map is not marked as modified
- The project is not marked as modified

---

### ID : T-026

### Title : Test FN013 (Journey Mode Navigation)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys exists
- The map has been exported

**Steps :**
1. Open the exported index file in a browser
2. Select "by journey" reading mode
3. Select a journey from the list

**Expected Result :**
- An intermediate page lists all journeys of the map
- Selecting a journey displays the complete linear sequence of its components
- Each component is rendered with its label as paragraph heading and description as body text
- Components with empty descriptions display only the label
- The reading order follows the predecessor-successor relationship from the data model
- Each reading page offers a link back to the table of contents

---

### ID : T-027

### Title : Test FN014 (Agent)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed
- The active journey is set

**Steps :**
1. Select menu "Project > Components... > Agent"
2. Click on a position in the visualization space

**Expected Result :**
- A new agent component is created at the clicked position
- The component has a unique integer identifier
- The component has the default label for agent type
- The component displays the agent icon
- The component is aligned to the grid
- The component is attached to the active journey
- The component has incoming (left) and outgoing (right) attachment ports
- The component is not resizable
- The map is marked as modified
- The project is marked as modified

---

### ID : T-028

### Title : Test FN014 (State)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed
- The active journey is set

**Steps :**
1. Select menu "Project > Components... > State"
2. Click on a position in the visualization space

**Expected Result :**
- A new state component is created at the clicked position
- The component has a unique integer identifier
- The component has the default label for state type
- The component displays the state icon
- The component is aligned to the grid
- The component is attached to the active journey
- The component has incoming (left) and outgoing (right) attachment ports
- The component is not resizable
- The map is marked as modified
- The project is marked as modified

---

### ID : T-029

### Title : Test FN014 (Event)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed
- The active journey is set

**Steps :**
1. Select menu "Project > Components... > Event"
2. Click on a position in the visualization space

**Expected Result :**
- A new event component is created at the clicked position
- The component has a unique integer identifier
- The component has the default label for event type
- The component displays the event icon
- The component is aligned to the grid
- The component is attached to the active journey
- The component has incoming (left) and outgoing (right) attachment ports
- The component is not resizable
- The map is marked as modified
- The project is marked as modified

---

### ID : T-030

### Title : Test FN014 (Grid Alignment)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed
- The alignment grid is visible and active
- The active journey is set

**Steps :**
1. Select menu "Project > Components... > Agent"
2. Click on a non-grid-aligned position in the visualization space

**Expected Result :**
- The new component is created
- The component is automatically aligned to the nearest grid position

---

### ID : T-031

### Title : Test FN015 (Agent Attributes)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with an agent component exists

**Steps :**
1. Select the agent component
2. Open the properties panel
3. Modify one or more editable attributes

**Expected Result :**
- The properties panel displays agent-specific editable attributes
- The modified attributes are updated
- The map is marked as modified
- The project is marked as modified

---

### ID : T-032

### Title : Test FN015 (State Attributes)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a state component exists

**Steps :**
1. Select the state component
2. Open the properties panel
3. Modify one or more editable attributes

**Expected Result :**
- The properties panel displays state-specific editable attributes
- The modified attributes are updated
- The map is marked as modified
- The project is marked as modified

---

### ID : T-033

### Title : Test FN015 (Event Attributes)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with an event component exists

**Steps :**
1. Select the event component
2. Open the properties panel
3. Modify one or more editable attributes

**Expected Result :**
- The properties panel displays event-specific editable attributes
- The modified attributes are updated
- The map is marked as modified
- The project is marked as modified

---

### ID : T-034

### Title : Test FN015 (Label Uniqueness)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple components exists

**Steps :**
1. Select a component
2. Open the properties panel
3. Change the label to match another component's label

**Expected Result :**
- The label change is accepted
- The application allows non-unique labels within the map

---

### ID : T-035

### Title : Test FN016

**Preconditions :**
- The application is running
- A project is open
- A narrative map with an existing component exists
- The active journey is set

**Steps :**
1. Select the existing component
2. Duplicate the component

**Expected Result :**
- A new component is created
- The copy has a distinct name from the original
- The copy has a new unique identifier
- The copy is attached to the active journey
- The copy is positioned near the original component
- The map is marked as modified
- The project is marked as modified

---

### ID : T-036

### Title : Test FN017 (Mouse Drag-and-Drop)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a component exists
- The alignment grid is visible and active

**Steps :**
1. Select the component with the mouse
2. Drag the component to a new position
3. Drop the component

**Expected Result :**
- The component moves to the new position
- The component automatically aligns to the grid during movement
- The component remains at the grid-aligned position after drop
- The map is marked as modified
- The project is marked as modified

---

### ID : T-037

### Title : Test FN017 (Position Persistence)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with components at specific positions exists

**Steps :**
1. Move one or more components to new positions
2. Save the project
3. Close the project
4. Reopen the project

**Expected Result :**
- The components are displayed at their last saved positions
- The positions (x, y) are preserved between sessions

---

### ID : T-038

### Title : Test FN018 (Without Data)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a component without associated data exists

**Steps :**
1. Select the component
2. Delete the component

**Expected Result :**
- The component is deleted
- All relations connected to the component are cascade-deleted
- The map is marked as modified
- The project is marked as modified

---

### ID : T-039

### Title : Test FN018 (With Data)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a component with associated data exists

**Steps :**
1. Select the component
2. Attempt to delete the component
3. Observe the confirmation dialog

**Expected Result :**
- A confirmation dialog appears
- After confirmation, the component is deleted
- All relations connected to the component are cascade-deleted
- The map is marked as modified
- The project is marked as modified

---

### ID : T-040

### Title : Test FN018 (Cascade Deletion)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple components connected by relations exists

**Steps :**
1. Select a component that has relations to other components
2. Delete the component

**Expected Result :**
- The component is deleted
- All relations connecting the component to other components are deleted
- The remaining components are not affected

---

### ID : T-041

### Title : Test FN019 (Multiple Journeys)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys exists
- A component attached to multiple journeys exists

**Steps :**
1. Select the component
2. Open the component properties
3. Modify the list of journeys the component is attached to

**Expected Result :**
- The properties panel displays a multiple-choice list of existing journeys
- The component can be attached/detached from journeys
- The component remains attached to at least one journey
- The map is marked as modified
- The project is marked as modified

---

### ID : T-042

### Title : Test FN019 (Single Journey)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with only one journey exists
- A component attached to that journey exists

**Steps :**
1. Select the component
2. Open the component properties
3. Attempt to modify the journey membership

**Expected Result :**
- The journey membership modification option is disabled
- The component cannot be detached from the only journey

---

### ID : T-043

### Title : Test FN019 (Last Attachment)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys exists
- A component attached to exactly one journey exists

**Steps :**
1. Select the component
2. Open the component properties
3. Attempt to remove the last journey attachment

**Expected Result :**
- The option to remove the last attachment is not offered
- The action is blocked
- The component remains attached to the journey

---

### ID : T-044

### Title : Test FN020 (Valid Connection)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with at least one state and one event component exists

**Steps :**
1. Select menu "Project > Relations... > Connect State and Event"
2. Select a state component as source
3. Move the cursor to an event component
4. Click on the incoming (left) port of the event component

**Expected Result :**
- A directed relation is created from the state to the event
- The relation is represented by a line connecting the output of the source to the input of the target
- The map is marked as modified
- The project is marked as modified

---

### ID : T-045

### Title : Test FN020 (Invalid - Same Component)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a component exists

**Steps :**
1. Select menu "Project > Relations... > Connect State and Event"
2. Select a component as source
3. Attempt to create a relation to the same component as target

**Expected Result :**
- The application refuses to create the relation
- No relation is created
- An error message or visual feedback indicates the invalid operation

---

### ID : T-046

### Title : Test FN020 (Invalid - Same Type)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with two state components exists

**Steps :**
1. Select menu "Project > Relations... > Connect State and Event"
2. Select a state component as source
3. Attempt to create a relation to another state component as target

**Expected Result :**
- The application refuses to create the relation
- No relation is created
- An error message or visual feedback indicates the invalid operation

---

### ID : T-047

### Title : Test FN020 (Invalid - Existing Relation)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a state and event component already connected exists

**Steps :**
1. Select menu "Project > Relations... > Connect State and Event"
2. Select the state component as source
3. Attempt to create another relation to the same event component

**Expected Result :**
- The application refuses to create the duplicate relation
- No additional relation is created
- An error message or visual feedback indicates the invalid operation

---

### ID : T-048

### Title : Test FN020 (Relation Follows Movement)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with components connected by a relation exists

**Steps :**
1. Select and move one of the connected components
2. Observe the relation line

**Expected Result :**
- The relation line follows the movement of the components
- The relation remains connected to the attachment ports
- The relation line updates dynamically during movement

---

### ID : T-049

### Title : Test FN021 (Annotation)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a relation exists

**Steps :**
1. Select the relation
2. Open the relation properties panel
3. Add free text annotation to the relation

**Expected Result :**
- The annotation is saved
- The relation label is displayed in a tooltip when hovering over the relation line
- The map is marked as modified
- The project is marked as modified

---

### ID : T-050

### Title : Test FN021 (Modify Endpoints)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a relation exists

**Steps :**
1. Select the relation
2. Open the relation properties panel
3. Change the source or target component

**Expected Result :**
- A warning is issued
- The existing relation is implicitly deleted
- A new relation is created with the new endpoints
- The map is marked as modified
- The project is marked as modified

---

### ID : T-051

### Title : Test FN022

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a relation exists

**Steps :**
1. Select the relation
2. Attempt to delete the relation
3. Confirm the deletion

**Expected Result :**
- A confirmation dialog appears before deletion
- After confirmation, the relation is deleted
- The components remain unaffected
- The map is marked as modified
- The project is marked as modified

---

### ID : T-052

### Title : Test FN023

**Preconditions :**
- The application is running
- A project is open
- A narrative map exists

**Steps :**
1. Create a new journey

**Expected Result :**
- A new journey is created
- The journey has a unique identifier
- The journey has a default name
- The journey has an empty description
- The new journey is automatically activated and becomes the current journey
- The map is marked as modified
- The project is marked as modified

---

### ID : T-053

### Title : Test FN024

**Preconditions :**
- The application is running
- A project is open
- A narrative map with a journey exists

**Steps :**
1. Open the journey renaming/description dialog or properties panel
2. Modify the journey label
3. Modify the journey description
4. Save the changes

**Expected Result :**
- The journey label is updated
- The journey description is updated
- The map is marked as modified
- The project is marked as modified

---

### ID : T-054

### Title : Test FN025

**Preconditions :**
- The application is running
- A project is open
- A narrative map with an existing journey exists

**Steps :**
1. Duplicate the journey

**Expected Result :**
- A new journey is created
- The copy has a distinct name from the original
- The copy has a new unique identifier
- Components attached to the source journey are also attached to the copy
- The map is marked as modified
- The project is marked as modified

---

### ID : T-055

### Title : Test FN026

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys exists

**Steps :**
1. Open the journey list
2. Select a journey that is not the current journey

**Expected Result :**
- The selected journey becomes the current journey
- New components created thereafter are attached to this journey
- The display filtering applies to this journey
- The map is marked as modified
- The project is marked as modified

---

### ID : T-056

### Title : Test FN027 (Not Last Journey)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys exists
- A journey with components exclusively attached to it exists

**Steps :**
1. Select the journey to delete
2. Confirm the deletion
3. For each exclusively attached component, select a new journey

**Expected Result :**
- A confirmation dialog appears
- For each component exclusively attached to the journey, a dedicated window prompts for new journey selection
- After all reassignments, the journey is deleted
- The map is marked as modified
- The project is marked as modified

---

### ID : T-057

### Title : Test FN027 (Last Journey)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with only one journey exists

**Steps :**
1. Attempt to delete the last journey

**Expected Result :**
- The application displays an explanatory message
- The deletion is impossible
- The journey remains in the map

---

### ID : T-058

### Title : Test FN028 (Scrollbars)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with components exists
- The visualization space extends beyond the visible window

**Steps :**
1. Use the horizontal scrollbar to navigate
2. Use the vertical scrollbar to navigate

**Expected Result :**
- The visualization space can be navigated horizontally via the horizontal scrollbar
- The visualization space can be navigated vertically via the vertical scrollbar
- The visualization space appears virtually unlimited
- The component alignment grid remains visible and active

---

### ID : T-059

### Title : Test FN028 (Window Resizing)

**Preconditions :**
- The application is running
- A project is open
- A narrative map is displayed

**Steps :**
1. Resize the application window to at least 1280x720
2. Interact with the visualization space

**Expected Result :**
- The interface remains fully functional
- All components and relations are visible and accessible
- The visualization space adapts to the window size

---

### ID : T-060

### Title : Test FN028 (Scrollbar Positions Not Preserved)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with components exists

**Steps :**
1. Scroll the visualization space to a specific position
2. Save the project
3. Close the project
4. Reopen the project

**Expected Result :**
- The scrollbar positions are not preserved
- The visualization space returns to a default position
- The map is not marked as modified by scrollbar position changes

---

### ID : T-061

### Title : Test FN029 (Show All)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys and components exists
- Some components are attached to different journeys

**Steps :**
1. Switch the display filter to "show all"

**Expected Result :**
- All components and relations of the map are displayed
- Components from all journeys are visible
- All relations between components are visible

---

### ID : T-062

### Title : Test FN029 (Active Journey Only)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys and components exists
- Components are attached to different journeys

**Steps :**
1. Activate a specific journey
2. Switch the display filter to "active journey"

**Expected Result :**
- Only components attached to the active journey are displayed
- Only relations between components of the active journey are displayed
- Components from other journeys are hidden
- Relations involving components from other journeys are hidden

---

### ID : T-063

### Title : Test FN029 (Switch Journey)

**Preconditions :**
- The application is running
- A project is open
- A narrative map with multiple journeys exists
- The display filter is set to "active journey"

**Steps :**
1. Activate journey A
2. Observe the displayed components
3. Activate journey B

**Expected Result :**
- The display instantly updates when switching from journey A to journey B
- Only components attached to journey B are displayed
- Only relations between components of journey B are displayed
- Filtering does not mark the map as modified
