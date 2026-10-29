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
- **Description**: Deleting a component (state or event) triggers the automatic deletion of all relationships connecting it to other components. The state-event edges that reference it are deleted according to the narrative map graph consistency rules.
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
- **Description**: The constituent sequence of a journey is defined by the succession of state to event to state. Each directed relation between a state and an event is materialized by a state-event edge that specifies the identifier of the state, the identifier of the event, and the direction of the relation (predecessor or successor). The succession of state to event to state is reconstituted by chaining edges through the states and events they connect.
- **Classification**: Narrative Map Structure.

## RG034
- **Description**: The same component (state or event) can belong to multiple journeys without duplication thanks to the management of state-event edges and journey nodes. A state is attached to a journey via a journey node. An event is not directly attached to any journey; it belongs to a journey if and only if at least one state-event edge connects it to a state that is itself attached to that journey. An isolated event therefore belongs to no journey.
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
- **Description**: A state of type final has no outgoing state-event edge, that is, no edge linking it to an event as a successor.
- **Classification**: Narrative Map Structure.

## RG060
- **Description**: The type of the initial state of a narrative map can never be modified. The initial state permanently keeps the type "Initial".
- **Classification**: Narrative Map Structure.

## RG061
- **Description**: The type "Initial" can never be selected for a state other than the initial state of the narrative map. When creating or editing a state, the type "Initial" is not offered among the selectable values.
- **Classification**: Narrative Map Structure.

## RG058
- **Description**: A direct bidirectional connection between a State and an Event is forbidden. If a relationship from a State S to an Event E already exists (output port of S connected to the input port of E), creating the reverse relationship from Event E to State S (output port of E connected to the input port of S) is prohibited, and vice versa. This rule prevents direct cycles of length 2 (State → Event → State) in the narrative map graph.
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
- **Description**: A newly created state is automatically attached to the currently activated journey. A newly created event is not attached to any journey as long as it is isolated, that is, not linked by any incoming or outgoing relation to a state. An event becomes attached to a journey as soon as a relation connects it to a state that is itself attached to that journey. Conversely, if the last relation connecting an event to the states of a journey is deleted, the event becomes detached from that journey and returns to an orphan status with no journey.
- **Classification**: Journey Logic and Membership.

## RG025
- **Description**: A component (state or event) can be attached simultaneously to multiple journeys. A state must remain attached to at least one journey at all times. An event, on the other hand, may be orphan of all journeys as long as it is not engaged in at least one relation with a state; this situation cannot arise for a state.
- **Classification**: Journey Logic and Membership.

## RG026
- **Description**: Relationships between components (state or event) have no direct attachment to journeys. A relationship is implicit within a journey if and only if both of its endpoint components are attached to that journey.
- **Classification**: Journey Logic and Membership.

## RG027
- **Description**: A component's (state or event) membership in one or more journeys is managed via a multiple-choice list in the component's properties. The option is disabled if only one journey exists in the map.
- **Classification**: Journey Logic and Membership.

## RG028
- **Description**: The user cannot remove a state from its last journey. An event can be removed from all its journeys, in which case it becomes orphan of all journeys until it is engaged in a relation with a state.
- **Classification**: Journey Logic and Membership.

## RG029
- **Description**: There is always a default journey. Orphan nodes after the deletion of a journey are automatically switched to the default journey.
- **Classification**: Journey Logic and Membership.

## RG030
- **Description**: When the user removes a component (state or event) from a journey, the application checks whether this component is connected to another component still attached to that journey. If so, the application raises an alert: the user can cancel the removal, or confirm the deletion of the inconsistent relationship.
- **Classification**: Journey Logic and Membership.

## RG052
- **Description**: The journey concept is not activated until a relation has been established in the narrative map. Upon creation of an isolated state, no journey node is created. The attachment of a state to a journey occurs when a relation connecting it to an event is established: a journey node is then created, referencing the corresponding edge and attaching the state to the currently activated journey.
- **Classification**: Journey Logic and Membership.

## RG054
- **Description**: When a user establishes a relationship between a state and an event, the application creates a new state-event edge specifying the state, the event, and the direction of the relation (predecessor or successor). No two identical edges may exist for the same state, event, and direction.
- **Classification**: Journey Logic and Membership.

## RG055
- **Description**: Only one journey can be defined as the default journey of its narrative map. If the default journey is deleted, the application automatically designates the oldest remaining journey as the new default journey.
- **Classification**: Journey Logic and Membership.

## RG056
- **Description**: Deleting a state or an event triggers the cascading deletion of all state-event edges that reference it, then of all journey nodes that reference the deleted edges.
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

## RG059
- **Description**: The visual representation of a connection (relation) between two components must never overlap a component that is neither its source nor its target. Upon creation of a connection, the application detects whether the connection path is likely to cross a third-party component and, if so, automatically adjusts the connection routing to circumvent that component. This detection and readjustment are also performed when a component is moved by the user and its new position causes an existing connection, of which it is not an endpoint, to be overlapped. The routing adjustment modifies neither component coordinates nor project data; it affects only the graphical representation of the connection.
- **Classification**: Visualization and Interaction.

---

## 5. Technical Architecture and Data Model

## RG050
- **Description**: The absence of a predecessor or successor for a state is materialized by the absence of a state-event edge in the corresponding direction. A state with no incoming edge is the first element of a sequence; a state with no outgoing edge is the last element.
- **Classification**: Technical Architecture and Data Model.

## RG051
- **Description**: Graphical representation metadata is stored in a dedicated file associated with the project's data file.
- **Classification**: Technical Architecture and Data Model.
## 2. Narrative Map Structure

## RG061
- **Description**: The type of the initial state of a narrative map can never be modified. The initial state permanently keeps the type "Initial".
- **Classification**: Narrative Map Structure.

## RG062
- **Description**: The type "Initial" can never be selected for a state other than the initial state of the narrative map. When creating or editing a state, the type "Initial" is not offered among the selectable values.
- **Classification**: Narrative Map Structure.

## RG063
- **Description**: Between a given agent and a given state of the same narrative map, only one association can exist. Any attempt to create a duplicate association is ignored or refused by the application.
- **Classification**: Narrative Map Structure.

## RG064
- **Description**: Deleting an agent cascades the deletion of all agent-state associations referencing its identifier. An informational message is displayed if the agent is associated with at least one state.
- **Classification**: Narrative Map Structure.

## RG065
- **Description**: Deleting a state cascades the deletion of all agent-state associations referencing its identifier. An informational message is displayed if the state is associated with at least one agent.
- **Classification**: Narrative Map Structure.

## RG066
- **Description**: Every agent-state association belongs to at least one journey at all times. When created, it is attached to the currently active journey (or to the default journey if no journey is active), via a journey node referencing the association (Journey_node.state_agent_rel_id). If deleting a journey leaves it orphaned from every journey, it is automatically moved to the default journey. The same pair of agents meeting in several journeys is modeled by distinct states, each attached to the relevant journey. Filtering the display by journey applies to agent-state associations as to other relationships.
- **Classification**: Narrative Map Structure.

## RG068
- **Description**: The columns of the agents × states matrix of the agents view are ordered by default by state creation order (ascending ID). The user can reorder the columns; this custom order is persistent: it is kept in the graphical metadata (layout file) associated with the project, across sessions. The initial state always occupies the first column and cannot be moved (RG031: all journeys begin at this state). Any newly created state appears at the end of the order. In case of an anomaly in the saved order (missing or unknown state), the application falls back to creation order. The column order is not narrative data: modifying it does not mark the map as modified. The rows (agents) follow the same rule: default creation order, persistent manual reordering allowed.
- **Classification**: Visualization and Interaction.

## RG067
- **Description**: The cross-view navigation focus (events view, agents view) is a temporary visual state: it does not mark the map or the project as modified, and is not persisted in the graphical metadata or between sessions.
- **Classification**: Visualization and Interaction.
