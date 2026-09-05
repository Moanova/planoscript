# Planoscript ::: User Stories

## Document Version
- **Version**: 2.0
- **Date**: 2026-08-29
- **Status**: New version realigned with the latest redesign

---

## SU001: Manage a Narrative Project
- **Description**: As an author, I can create, open, save, rename, and close a narrative project in order to gather, retrieve, and continue working on my narrative maps.
- **Additional details**:
    - A project is a local document containing project metadata and one or more narrative maps.
    - Only one project can be open in the application at any time.
    - A newly created project is an unsaved project: it exists in memory but is not associated with any file until the user saves it.
    - Each project has a stable identifier, a name, a creation date, a last modification date, and a format version.
    - The file path is an application state; it does not constitute portable project business data.
    - A new project is named "New project" and contains a narrative map named "Main narrative map".
- **Acceptance criteria**:
    - The user can create a project from the menu, a keyboard shortcut, or the welcome message.
    - The user can open a valid project file from the file system.
    - In case of an invalid, incompatible, or unreadable file, the application displays a clear error and keeps the currently open project unchanged.
    - The user can save an unsaved project by choosing a name and a location.
    - The user can save changes to a project already associated with a file without a new dialog box.
    - The user can save a copy under a different name or in a different location; this copy becomes the currently open project.
    - The user can close a project.
    - If the project is modified during a close, open, create, or exit action, the application offers: "Save", "Don't Save", "Cancel".
    - A saved project is added to the list of recent projects.
    - The list of recent projects respects the configured limit and removes files that no longer exist.
- **MVP scope**:
    - Each project contains only one narrative map.


## SU002: Manage a Narrative Map
- **Description**: As an author, I can create, name, duplicate, delete, and navigate between the narrative maps of a project in order to structure my narrative into alternative threads.
- **Additional details**:
    - A narrative map is a data element stored within the project file. It belongs to one and only one project.
    - Each map has a stable identifier, a name, a creation date, and a last modification date.
    - A project always contains at least one narrative map.
    - The map created by default when a project is created is named "Main narrative map".
    - Deleting a map is irreversible and results in the deletion of all graphical components, relationships, and journeys it contains.
    - A map is considered modified when the user: adds or removes a component or a relationship; modifies the data associated with a component or a relationship; modifies the position of a component in the graphical representation space; creates, modifies, or deletes a journey; modifies the attachment of components or relationships to a journey.
    - Changing the zoom level or the position of the scroll bars of the graphical representation space does not constitute a map modification.
    - The component alignment grid in the visualization space is always visible and active for each map.
    - The user can export a narrative map as a standalone file, and import a narrative map from a standalone file into the current project.
- **Acceptance criteria**:
    - The user can create a new map from the "Project" menu.
    - The user can rename a map by directly editing its label or via a dedicated dialog box.
    - The user can duplicate a map; the copy automatically carries a distinctive name (e.g.: "Name (copy)") and a new stable identifier.
    - The user can delete a map with confirmation if it contains components; deletion is refused with an explicit message if the map is the last one in the project.
    - The user can navigate between the maps of the project from the "Project" menu.
    - The user can export a narrative map to a chosen location.
    - The user can import a narrative map from a valid file into the current project; in case of an invalid, incompatible, or unreadable file, the application displays a clear error and keeps the currently open project unchanged.
    - Any creation, renaming, duplication, or deletion of a map marks the project as modified.
    - Any modification as defined in the additional details updates the last modification date of the map and that of the project.
- **MVP scope**:
    - Each project contains only one narrative map. Consequently, the creation, duplication, deletion, navigation between maps, and reordering of maps are not available.
    - Only the renaming of the default map, the modification of its content, and map export are functional.


## SU003: Manage a Narrative Map Component
- **Description**: As an author, I can create, name, move, modify, or delete a narrative map component in order to define the content of my narrative sequences.
- **Additional details**:
    - Component types are defined by the application data model: agent, state, event.
    - Each component has a unique integer identifier within the narrative map to which it belongs. The same identifier may exist in two distinct maps.
    - A component's label is not constrained to uniqueness within the same narrative map.
    - Each component is visually represented by an icon specific to its type.
    - Each component is movable within the visualization space but not resizable.
    - Each component has two attachment ports, respectively incoming and outgoing (left and right), materialized by active squares, intended for the creation of relationships.
    - A component's position in the visualization space is defined by coordinates (x, y) that are stored in a graphical metadata file associated with the project's data file.
    - Components automatically align to the alignment grid of the visualization space upon creation and movement.
    - Upon the creation of a narrative map, a default journey is automatically created and activated.
    - Any newly created component is automatically attached to the currently activated journey.
    - A component can never exist outside of a journey. The user can modify the attachment of a component to another existing journey, but cannot remove it from its last journey.
    - Deleting a component automatically triggers the cascading deletion of all relationships connecting it to other components.
- **Acceptance criteria**:
    - The user can create a component from the general menu, the toolbar, or the context menu.
    - Upon creation, the component is automatically attached to the activated journey and positioned on the grid at the location designated by the user.
    - The user can duplicate a component; the copy automatically carries a distinctive name and a new identifier, and is attached to the activated journey.
    - The user can modify the editable attributes of a component via a properties panel.
    - The user can modify the list of journeys to which a component is attached, from among the existing journeys of the map.
    - The user cannot remove a component from its journey if it has only a single attachment; the application prevents this action or does not offer the option.
    - The user can delete a component with confirmation if data is associated; deletion triggers the cascading deletion of the concerned relationships.
    - The user can position and reposition a component by drag-and-drop using a mouse (on PC), a stylus, or in touch mode (on tablet).
    - During movement, the component automatically aligns to the grid of the visualization space.
    - The component retains its position (x, y coordinates) between sessions via the associated graphical metadata file.
    - The component is represented by the icon corresponding to its type and has two active attachment points (incoming and outgoing).
    - The component is not resizable by the user.
    - The user can choose to display all components and relationships of the map, or only those belonging to the activated journey.
    - Any creation, duplication, data modification, movement, or deletion of a component marks the map as modified, and consequently the project as modified.
- **MVP scope**:
    - The component toolbar is not implemented. The associated actions are therefore only handled by menu.


## SU004: Manage a Relationship Between Narrative Map Components
- **Description**: As an author, I can create, annotate, modify, or delete a relationship between two narrative map components in order to define the sequences of my narrative.
- **Additional details**:
    - A relationship is a data element belonging to a narrative map. It has a unique integer identifier within this map, according to the same mechanism as components.
    - The editable attributes of a relationship depend on its type according to the data model. As a general rule, the mandatory attributes are identical to those of components.
    - A relationship always connects exactly two distinct components of the same narrative map. A component can never be in a relationship with itself.
    - Between two given components, there can only be one relationship.
    - Relationships have no direct link with journeys. They indirectly belong to one or more journeys through the source and target components they connect.
    - Deleting a relationship is independent of that of components, except for the cascading deletion defined in scenario SU003.
    - A relationship's label (textual annotation) is displayed in a tooltip on hover.
    - Relationships are directional: the output of component A is connected to the input of component B, and the output of component B is connected to the input of component C... etc.
    - Two components of the same type can never be connected to each other: a state is necessarily connected to an event, and an event is necessarily connected to a state.
- **Acceptance criteria**:
    - The user can initiate the creation of a relationship from the toolbar, the "Project" menu, or the context menu.
    - During creation, the user selects a source component. If no component was active, it becomes active. A visual link then follows the cursor movements until the user clicks on the attachment point of a target component.
    - The application prevents the creation of a relationship whose source and target components are identical.
    - The application prevents the creation of a relationship whose source and target components are of the same type.
    - The application prevents the creation of a duplicate relationship between two already connected components.
    - The user can annotate a relationship with free text via a properties panel.
    - A relationship cannot be moved as such but follows the movement of the component to which it is attached.
    - If modifying a relationship results in a change of source or target component, the application issues an alert, implicitly deletes the existing relationship, and creates a new one with the new source/target connection.
    - The user can delete a relationship with prior confirmation.
    - A relationship's label is viewable via a tooltip on hover of the representative line.
    - Any creation, annotation modification, movement, or deletion of a relationship marks the map as modified, and consequently the project as modified.
- **MVP scope**:
    - The component toolbar is not implemented. The associated actions are therefore only handled by menu.


## SU005: Manage a Narrative Journey
- **Description**: As an author, I can create, name, describe, duplicate, activate, modify, or delete a narrative journey in order to define the alternative threads of my narrative.
- **Additional details**:
    - A narrative journey is a data element belonging to a narrative map. It has a unique integer identifier within this map, according to the same mechanism as components and relationships.
    - The editable attributes of a journey are its label and its description.
    - Each narrative map always contains at least one journey.
    - Upon the creation of a narrative map, the application automatically creates an initial journey, activates it, and assigns it a default name.
    - A component can be attached simultaneously to multiple journeys. However, every component must remain attached to at least one journey at all times.
    - Relationships between components have no direct attachment to journeys. A relationship is implicit within a journey if and only if both of its connected components are attached to that journey.
    - Upon the creation of a new journey, it automatically becomes the activated journey.
    - Any newly created component is automatically attached to the currently activated journey.
    - Deleting a journey is impossible if it is the last journey of the map; the application displays an explanatory message.
- **Acceptance criteria**:
    - The user can create a new journey from the journey sidebar toolbar or the "Project" menu. The new journey is automatically activated and becomes the current journey.
    - The user can rename a journey and modify its description via a dialog box or a properties panel.
    - The user can duplicate a journey; the copy automatically carries a distinctive name and a new identifier. The components attached to the source journey are also attached to the duplicated journey.
    - The user can activate a journey by selecting it from the list in the journey sidebar toolbar or from the "Project" menu. The activated journey becomes the current journey for editing.
    - The user can delete a journey with prior confirmation, provided it is not the last journey of the map.
    - Upon deletion of a journey, the application identifies the components exclusively attached to it. For each, the user must mandatorily choose a new attachment journey via a dedicated window.
    - A component's membership in one or more journeys is managed via a multiple-choice list in the component's properties. The option is disabled if only one journey exists in the map.
    - Any creation, renaming, duplication, activation, deletion, or modification of a journey's attachments marks the map as modified, and consequently the project as modified.
- **MVP scope**:
    - The journey toolbar is not implemented. The associated actions are therefore only handled by menu.
    - Journey consistency is not analyzed: the application does not detect if a journey has broken sequences (an event whose connected state belongs to another journey, or vice versa); this will be the subject of a later feature.


## SU006: Visualize a Narrative Map
- **Description**: As an author, I can view and navigate within the graphical representation space of a narrative map in order to consult, structure, and validate my narrative.
- **Additional details**:
    - The visualization space is virtually unlimited in its dimensions (limited by the operating system's capabilities).
    - Navigation is performed using horizontal and vertical scroll bars.
    - The component alignment grid is always visible and active.
    - A journey filter allows displaying either all existing journeys, or the selected journey. Switching from one journey to another updates the display to represent only the components attached to that journey and the relationships between its components.
    - The position of the scroll bars and the zoom level do not constitute business data; they are not retained between sessions.
- **Acceptance criteria**:
    - The application adapts to the window size without loss of functionality; the toolbars (components and journeys) remain accessible.
    - The user can navigate within the visualization space using the horizontal and vertical scroll bars.
    - The visualization space supports extended deployment without stability degradation.
    - If the journey filter is activated, the user can switch from one journey to another via the journey toolbar or the "Project" menu; the display updates instantly.
    - The components and relationships of the displayed journey are rendered according to their coordinates and graphical representation defined in the project metadata.
    - Components align to the alignment grid upon creation and movement.
    - Changes in scroll bar position do not mark the map as modified.
    - The interface remains fully functional for a minimum window size of 1280×720.
    - The response time between a user action (creation, movement, deletion of a component) and the display update is immediate (without perceptible latency) for a map containing up to 100 components.
    - The application remains stable when navigating within a visualization space of 10,000×10,000 pixels.
- **MVP scope**:
    - The component and journey toolbars are not available.
    - Zoom is not available.
    - The application exclusively targets PCs running Windows.
    - The alternative view of relationships between agents is not available; it will be implemented in a later version.


## SU007: Export a Narrative Map
- **Description**: As an author, I can export a narrative map as a standalone document readable in a standard browser in order to validate my narrative and share it with my team.
- **Additional details**:
    - The application offers two distinct exports for a narrative map: a technical export intended for re-importation into another project, and a reading export intended for consultation outside the application.
    - The reading export document is standalone: it requires no server, no Internet connection, and no external dependencies.
    - The export generates a folder named after the physical name of the narrative map. This folder contains an index file and all the pages necessary for hypertext navigation.
    - The content rendered for each component consists of its label (displayed as a paragraph title) and its description (body text). If the description is empty, only the label is displayed.
    - The reading order is determined by the predecessor-to-successor sequence defined in the application data model, independently of the components' positions in the graphical visualization space.
    - The export offers two reading modes:
        1. **Journey view**: the reader selects a journey in the table of contents and accesses a page displaying the entire sequence of its components in a linear fashion.
        2. **Event view**: the reader accesses a page presenting the first event of the map, then linearly scrolls through the sequence of events until the first branching point (that is, an event having successors in several distinct journeys). At this branching point, hypertext links allow choosing the desired journey; each link indicates the name of the corresponding journey in parentheses. Choosing a link opens a new page continuing the linear reading until the next branching point, and so on.
    - Each reading page offers a link back to the table of contents. In the event view, each page also offers a link to the previous page (the one that led to the branching point).
- **Acceptance criteria**:
    - The user can launch the export of the current narrative map from the "File" menu or the toolbar.
    - The application generates an export folder named after the map's name, containing an index file and all necessary pages.
    - The document displays correctly in standard browsers (Chrome, Firefox, Edge) without an Internet connection.
    - The home page offers a choice between reading by journey and reading by events.
    - In **journey** mode, an intermediate page lists all the journeys of the map; clicking on a journey displays a page with the complete linear sequence of its components.
    - In **event** mode, the first page displays the first event determined by the application from the data model, then linearly scrolls through the events until the first branching point; at each branching point, the page displays hypertext links to each possible journey, with the name of the corresponding journey in parentheses; choosing a hypertext link opens a new page continuing the linear reading until the next branching point.
    - Each reading page has a link back to the table of contents. Each page of the event view has a link to the previous page.
    - The export operation does not mark the narrative map or the project as modified.
- **MVP scope**:
    - The technical export for re-import into another project is not available.
    - Reading by events is not available; it will be implemented in a later version.
    - Reading by relationships between agents is not available; it will be implemented in a later version.
