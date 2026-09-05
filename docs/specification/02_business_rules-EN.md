# Business Rules - Planoscript

## Document Version
- **Version**: 2.1
- **Date**: 2026-08-31
- **Status**: Redesign

---

## 1. Project Management and Lifecycle

## RG001
- **Description**: A project is a local document in JSON format containing project metadata and one or more narrative maps.
- **Classification**: Project Management and Lifecycle.

## RG002
- **Description**: Only one project can be open in the application at any time.
- **Classification**: Project Management and Lifecycle.

## RG003
- **Description**: A newly created project is an unsaved project: it exists in memory but is not associated with any file until the user saves it.
- **Classification**: Project Management and Lifecycle.

## RG004
- **Description**: Each project has a stable identifier (UUID), a name, a creation date, a last modification date, and a format version.
- **Classification**: Project Management and Lifecycle.

## RG005
- **Description**: Projects that are saved and successfully opened are added to the list of recent projects. The list is ordered from most to least recently opened and contains only one occurrence of each file. Its maximum number of entries is defined by the application configuration. Entries corresponding to a non-existent, inaccessible, or invalid file are removed from the list.
- **Classification**: Project Management and Lifecycle.

## RG006
- **Description**: The "Save" command is enabled only when an open project is modified. The "Save as..." command is enabled when a project is open, whether modified or not. When no project is open, both commands are disabled.
- **Classification**: Project Management and Lifecycle.

## RG007
- **Description**: When no project is open, the "File\Close", "File\Save", "File\Save as...", "File\Export map", "Edit\*", "Display\*", and "Project\*" menu entries are disabled (grayed out).
- **Classification**: Project Management and Lifecycle.

## RG008
- **Description**: When a project is opened or a new project is created while no project was previously open, the "File\Close", "File\Save", "File\Export map", "Edit\*", "Display\*", and "Project\*" menu entries are enabled.
- **Classification**: Project Management and Lifecycle.

## RG009
- **Description**: Opening a project replaces the current project only after successful reading and validation of the selected file. If the file is non-existent, inaccessible, invalid, or incompatible, an error is displayed to the user and the current project remains unchanged.
- **Classification**: Project Management and Lifecycle.

## RG010
- **Description**: Each project file has a format version. The application opens a project only if this version is supported or can be reliably migrated to a supported version. A migration must never overwrite the original file without explicit user action.
- **Classification**: Project Management and Lifecycle.

## RG011
- **Description**: A save operation replaces the existing file only after the new version has been completely and successfully written. In case of a save failure, the previously saved file must remain usable and the project must retain its modified state. After a successful save, the project's last modification date is updated.
- **Classification**: Project Management and Lifecycle.

## RG012
- **Description**: The "Save as..." action creates or replaces a file at the location chosen by the user after confirmation if a file already exists. After a successful save, the newly chosen file becomes the file associated with the open project. The previously associated project file is neither renamed nor deleted.
- **Classification**: Project Management and Lifecycle.

## RG013
- **Description**: A new project is named "New project" and contains a narrative map named "Main narrative map".
- **Classification**: Project Management and Lifecycle.

## RG014
- **Description**: A project always contains at least one narrative map.
- **Classification**: Project Management and Lifecycle.

## RG046
- **Description**: The application offers two distinct exports: a technical export in JSON format (re-importable) and a reading export in HTML format (standalone).
- **Classification**: Project Management and Lifecycle.

## RG047
- **Description**: The HTML export generates a folder named after the narrative map, containing an 'index.html' and linked pages.
- **Classification**: Project Management and Lifecycle.

## RG048
- **Description**: The reading order of a map's journeys is determined by the predecessor/successor sequence of the data model, independently of the graphical position.
- **Classification**: Project Management and Lifecycle.

## RG049
- **Description**: The export operation does not mark the narrative map or the project as modified.
- **Classification**: Project Management and Lifecycle.

---

## 2. Narrative Map Structure

## RG015
- **Description**: A narrative map always contains at least one journey.
- **Classification**: Narrative Map Structure.

## RG016
- **Description**: Deleting a narrative map is irreversible and results in the deletion of all components (states and events), relationships, and journeys it contains.
- **Classification**: Narrative Map Structure.

## RG017
- **Description**: Deleting a component (state or event) triggers the automatic deletion of all relationships connecting it to other components. The state nodes that reference it via a foreign key (predecessor event, state, or successor event) are updated or deleted according to the narrative map graph consistency rules.
- **Classification**: Narrative Map Structure.

## RG018
- **Description**: Deleting a journey is impossible if it is the last journey of the map.
- **Classification**: Narrative Map Structure.

## RG019
- **Description**: Each entity (project, narrative map) has a stable identifier (UUID).
- **Classification**: Narrative Map Structure.

## RG020
- **Description**: Each component, relationship, and journey has a unique integer identifier within its narrative map. The same identifier may exist in two distinct maps.
- **Classification**: Narrative Map Structure.

## RG021
- **Description**: The label of a component or a journey is not constrained to uniqueness within the same narrative map.
- **Classification**: Narrative Map Structure.

## RG031
- **Description**: Each narrative map has one and only one initial state. This initial state is necessarily found in all journeys. All journeys begin at this initial state. This state is automatically created by the application and can never be deleted.
- **Classification**: Narrative Map Structure.

## RG032
- **Description**: Each valid and complete journey ends with a final state. This final state may be specific to each journey, unlike the initial state which is common to all journeys. During editing, a journey may temporarily not have a final state.
- **Classification**: Narrative Map Structure.

## RG033
- **Description**: The constituent sequence of a journey is defined by the succession of state to event to state, and is materialized by a state node that specifies the identifier of the previous event, the identifier of the state, and the identifier of the next event.
- **Classification**: Narrative Map Structure.

## RG034
- **Description**: The same component (state or event) can belong to multiple journeys without duplication thanks to the management of state nodes.
- **Classification**: Narrative Map Structure.

## RG035
- **Description**: The constituent sequence of a journey allows that the same state has multiple predecessor and successor events, and that the same event has multiple predecessor and successor states.
- **Classification**: Narrative Map Structure.

## RG036
- **Description**: Deleting a journey necessarily deletes all entries of the journey nodes that carry its identifier.
- **Classification**: Narrative Map Structure.

## RG037
- **Description**: Deleting a state or an event triggers the cascading deletion of the associated references in all data tables where its identifier is used as a foreign key. An informational message is displayed if the component is referenced by at least one other element.
- **Classification**: Narrative Map Structure.

## RG038
- **Description**: A state of type final can only appear in state nodes whose successor event identifier is set to 0.
- **Classification**: Narrative Map Structure.

---

## 3. Journey Logic and Membership

## RG022
- **Description**: Upon the creation of a narrative map, a default journey is automatically created and activated.
- **Classification**: Journey Logic and Membership.

## RG023
- **Description**: Upon the creation of a new journey, it automatically becomes the activated journey.
- **Classification**: Journey Logic and Membership.

## RG024
- **Description**: Any newly created component (state or event) is automatically attached to the currently activated journey.
- **Classification**: Journey Logic and Membership.

## RG025
- **Description**: A component (state or event) can be attached simultaneously to multiple journeys. However, every component must remain attached to at least one journey at all times.
- **Classification**: Journey Logic and Membership.

## RG026
- **Description**: Relationships between components (state or event) have no direct attachment to journeys. A relationship is implicit within a journey if and only if both of its endpoint components are attached to that journey.
- **Classification**: Journey Logic and Membership.

## RG027
- **Description**: A component's (state or event) membership in one or more journeys is managed via a multiple-choice list in the component's properties. The option is disabled if only one journey exists in the map.
- **Classification**: Journey Logic and Membership.

## RG028
- **Description**: The user cannot remove a component (state or event) from its last journey.
- **Classification**: Journey Logic and Membership.

## RG029
- **Description**: There is always a default journey. Orphan nodes after the deletion of a journey are automatically switched to the default journey.
- **Classification**: Journey Logic and Membership.

## RG030
- **Description**: When the user removes a component (state or event) from a journey, the application checks whether this component is connected to another component still attached to that journey. If so, the application raises an alert: the user can cancel the removal, or confirm the deletion of the inconsistent relationship.
- **Classification**: Journey Logic and Membership.

## RG052
- **Description**: Upon each creation of an isolated state, the application implicitly creates a state node with the predecessor event identifier set to the value 0, the state identifier set to the value of the new state, and the successor event identifier set to the value 0.
- **Classification**: Journey Logic and Membership.

## RG053
- **Description**: Upon each creation of an isolated event, the application implicitly creates a state node with the predecessor event identifier set to the value of the new event, the state identifier set to the value 0, and the successor event identifier set to the value 0.
- **Classification**: Journey Logic and Membership.

## RG054
- **Description**: When a user establishes a relationship between a state and an event, a new state node is created if one does not already exist implicitly; otherwise, the pre-existing state node is updated, in accordance with the non-duplication of triplet rule.
- **Classification**: Journey Logic and Membership.

## RG055
- **Description**: Only one journey can be defined as the default journey of its narrative map. If the default journey is deleted, the application automatically designates the oldest remaining journey as the new default journey.
- **Classification**: Journey Logic and Membership.

## RG056
- **Description**: Deleting a state or an event triggers the cascading deletion of all state nodes that reference it, then of all journey nodes.
- **Classification**: Journey Logic and Membership.

## RG057
- **Description**: An implicit state node (whose successor event identifier or state identifier is set to the value 0) is automatically deleted as soon as it is updated with a complete relationship, unless it is the starting point of several branchings.
- **Classification**: Journey Logic and Membership.

---

## 4. Visualization and Interaction

## RG039
- **Description**: A component's (state or event) position is defined by coordinates (x, y) stored in a graphical metadata file associated with the project's data file.
- **Classification**: Visualization and Interaction.

## RG040
- **Description**: Components (state or event) automatically align to the alignment grid upon creation and movement.
- **Classification**: Visualization and Interaction.

## RG041
- **Description**: Changing the zoom level or the position of the scroll bars does not constitute a modification of the map or the project.
- **Classification**: Visualization and Interaction.

## RG042
- **Description**: At any time, either all journeys or a single journey are/is displayed in the representation space, depending on whether the journey filter is activated or not.
- **Classification**: Visualization and Interaction.

## RG043
- **Description**: At any time, only one component is selected in the workspace. Creating or clicking on a component selects it and deselects the previous one. Clicking on the workspace outside of any component deselects the current component.
- **Classification**: Visualization and Interaction.

## RG044
- **Description**: A component cannot be created at coordinates that overlap those of an existing component. The application checks the position before creation and adjusts the new component's coordinates to avoid any overlap, applying a lateral or vertical translation according to the characteristics of the graphical representation space.
- **Classification**: Visualization and Interaction.

## RG045
- **Description**: When a component is moved by the user and its coordinates exceed the visible part of the workspace, the application moves the corresponding scroll bar (lateral or vertical) to keep the component visible according to its current coordinates.
- **Classification**: Visualization and Interaction.

---

## 5. Technical Architecture and Data Model

## RG050
- **Description**: The value 0 (zero) in a predecessor or successor reference field ('from_event_id', 'to_event_id') means the absence of a predecessor or successor. This corresponds to the first or last element of a narrative map sequence.
- **Classification**: Technical Architecture and Data Model.

## RG051
- **Description**: Graphical representation metadata is stored in a dedicated file associated with the project's data file.
- **Classification**: Technical Architecture and Data Model.