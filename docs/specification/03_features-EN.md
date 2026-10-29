# Planoscript ::: Features

## Document Version
- **Version** : 2.2
- **Date** : 28-10-2026
- **Status** : Corrected and enriched version, realigned with user stories v2.0 (29-08-2026) and the general menu v2.0 (27-08-2026); "Agents and agent-state associations" section updated (EPC01–EPC04 implementation, TSK01–TSK15; TSK13: mechanical review of agent/association creation and edition)

---

## Scope decisions (08-09-2026)
- The "Display › Journey" (*Display › Journey*) section of the menu is inconsistent: it is ignored in this specification; the menu description will be corrected at a later date.
- The **narrative map import** feature is removed from the MVP.
- The **project renaming** applies to the project label: it is a business attribute editable in an editing window (not yet defined), and not a menu option.

## MVP scope reminder
- A project contains only one narrative map (SU001, SU002).
- Only the renaming of the default map, the modification of its content, and its export are functional (SU002).
- The "components" and "journeys" toolbars are not implemented: the corresponding actions are exclusively accessible via the menu (SU003, SU005).
- Zoom is not available (SU006).
- The application exclusively targets Windows PCs (SU006).
- The reading export is limited to the "by journey" mode; the "by events" and "by agent relationships" modes are postponed (SU007).
- The application does not analyze journey consistency (SU005).

---

# Application

## FN001 : Launch the application
- **Description** : Launch the application.
- **References** : SU001 (welcome screen).
- **Expected behavior** :
  - On launch, the application displays a welcome screen allowing, among other things, the creation of a new project.
- **Status** : Implemented.

## FN002 : Quit the application
- **Description** : Quit the application.
- **References** : SU001 ; menu "Files › Quit" (Ctrl+Q).
- **Expected behavior** :
  - If the current project is modified, the application offers "Save", "Do not save", "Cancel" before quitting.
  - Canceling keeps the project open and the application running.
- **Status** : Implemented.

## FN003 : Display the change log
- **Description** : Display the change history for each version of the application.
- **References** : menu "About › Change Log".
- **Expected behavior** :
  - A dialog box presents the list of versions and the associated changes.
- **Status** : Implemented.

## FN004 : Display the "about" information
- **Description** : Display the "about" information message of the application.
- **References** : menu "About › About Planoscript".
- **Expected behavior** :
  - A dialog box presents the general information about the application.
- **Status** : Implemented.

---

# Project

## FN005 : Create a new project
- **Description** : Create a new narrative project.
- **References** : SU001 ; menu "Files › New Project..." (Ctrl+N) ; welcome screen.
- **Expected behavior** :
  - The project can be created from the menu, the keyboard shortcut, or the welcome screen.
  - The new project is an unsaved project: it resides in memory and is not associated with any file until the user saves it.
  - It is named "New project" and contains a narrative map named "Main narrative map".
  - Only one project can be open at a time; creating a new project replaces the current project (with a save confirmation if modified).
  - The project has a stable identifier, a name, a creation date, a last modification date, and a format version; the file path is an application state, not business data.
- **Status** : Implemented.

## FN006 : Open a project
- **Description** : Open a project from the file system.
- **References** : SU001 ; menu "Files› Open..." (Ctrl+O).
- **Expected behavior** :
  - The user selects a valid project file on the file system.
  - In case of an invalid, incompatible, or unreadable file, the application displays a clear error message and keeps the current project unchanged.
  - If the current project is modified, a save confirmation is offered before opening.
- **Status** : Implemented.

## FN007 : Open a recent project
- **Description** : Open a project from the list of recent projects.
- **References** : SU001 ; menu "Files › Recents Projects...".
- **Expected behavior** :
  - The "Recent Files" menu presents a dynamic list of previously saved or opened projects.
  - The list respects the configured limit of recent projects.
  - Files that no longer exist are removed from the list.
  - The same handling of invalid files and save confirmations as FN006 applies.
- **Status** : Not implemented (menu entry present, feature missing). Feature required by SU001: to be scheduled.

## FN008 : Save the project
- **Description** : Save the project.
- **References** : SU001 ; menu "Files › Save" (Ctrl+S).
- **Expected behavior** :
  - If the project is already associated with a file, saving is performed without a new dialog box.
  - If the project has never been saved, the application asks for a name and a location (behavior equivalent to FN009).
  - The action is disabled as long as the project is not modified.
  - Saving adds the project to the list of recent projects.
- **Status** : Implemented.

## FN009 : Save the project as...
- **Description** : Save the project under another name or in another location.
- **References** : SU001 ; menu "Files › Save As..." (Ctrl+Shift+S).
- **Expected behavior** :
  - The user chooses a name and a location.
  - The saved copy becomes the current project.
  - The action adds the project to the list of recent projects.
- **Status** : Implemented.

## FN010 : Close the project
- **Description** : Close the current project.
- **References** : SU001 ; menu "Files › Close" (Ctrl+W).
- **Expected behavior** :
  - If the project is modified, the application offers "Save", "Do not save", "Cancel".
  - After closing, no project is open (return to the welcome screen).
- **Status** : Implemented.

## FN011 : Modify the project label
- **Description** : Modify the label (name) of the current project.
- **References** : SU001 ("name" attribute of the project). **Outside the menu**: no dedicated menu option.
- **Expected behavior** :
  - The project label is a business attribute editable via a project editing window (specification of this window to come).
  - Any modification of the label updates the last modification date and marks the project as modified.
  - The label is not subject to uniqueness.
- **Status** : Not implemented (editing window not defined).

---

# Narrative map

## FN012 : Rename the narrative map
- **Description** : Rename the project's narrative map.
- **References** : SU002 (MVP scope: only the renaming of the default map is available).
- **Expected behavior** :
  - Renaming is performed by direct editing of the label or via a dedicated dialog box.
  - Any renaming marks the map, and therefore the project, as modified, and updates the last modification dates.
- **Status** : Not documented in the menu.

## FN013 : Export the narrative map as a reading document
- **Description** : Export the current narrative map as a standalone reading document, viewable in a standard browser.
- **References** : SU002 (map export), SU007 ; menu "Files › Export Map".
- **Expected behavior** :
  - The export is launched from the "Files" menu (the toolbar does not exist in the MVP).
  - The export generates a folder named after the map name, containing an index file and all pages necessary for hypertext navigation.
  - The document is standalone: no server, no Internet connection, no external dependency; it displays correctly in Chrome, Firefox, and Edge.
  - The home page offers the choice of reading mode; in the MVP, only the "by journey" mode is available.
  - In "journey" mode: an intermediate page lists the journeys of the map; selecting a journey displays the complete linear sequence of its components.
  - Each component is rendered by its label (paragraph heading) and its description (body text); if the description is empty, only the label is displayed.
  - The reading order is determined by the predecessor › successor relationship of the data model, regardless of graphical positions.
  - Each reading page offers a link back to the table of contents.
  - The export does not mark either the map or the project as modified.
- **Status** : Not implemented.
- **Note** : the technical export intended for re-import (standalone map format) is postponed, due to the fact that narrative map import is excluded from the MVP.

---

# Components of the narrative map

## FN014 : Create a component
- **Description** : Create a component of type agent, state, or event in the narrative map.
- **References** : SU003 ; menu "Project › Components... › Agent" (direct creation), "Project › Components... › State › New..." and "Project › Components... › Event › New...".
- **Expected behavior** :
  - In the MVP, creation is performed exclusively from the menu (no toolbar).
  - The component is created with a unique integer identifier within the map, the default label for the type, and the icon corresponding to its type.
  - It is positioned at the location designated by the user, aligned on the alignment grid (always visible and active).
  - It is automatically attached to the active journey; a component can never exist outside a journey.
  - It has two active attachment ports: incoming (left) and outgoing (right).
  - It is not resizable.
  - Any creation marks the map, and therefore the project, as modified.
- **Status** : Partially implemented (creation via menu, positioned at the center of the workspace — to be aligned with the expected behavior "location designated by the user"). TSK13: creating an event from the agents view (global menu or grid context menu) switches to the events view and selects the created node; "New Agent" is offered in the grid context menu of the events view (direct creation, no view switch) and in the grid context menu of the agents view (stays in the agents view).

## FN015 : Modify the attributes of a component
- **Description** : Modify the editable attributes of a component via its properties panel.
- **References** : SU003 ; menu "Project › Components... › State › Edit" and "Project › Components... › Event › Edit".
- **Expected behavior** :
  - The properties panel presents the editable attributes according to the component type (agent, state, event): label, type, **note** (a few summary notes describing the object — compact input area) and **content** (the narrative content itself — larger input area, TSK20, 29-10-2026).
  - The label is not subject to uniqueness within the map.
  - Any attribute modification marks the map, and therefore the project, as modified.
- **Status** : Not implemented (properties panel not defined). The menu option is specified but not implemented; it is enabled only when a node of the relevant type is selected in the workspace.

## FN016 : Duplicate a component
- **Description** : Duplicate an existing component.
- **References** : SU003.
- **Expected behavior** :
  - The copy bears a distinct name and a new identifier.
  - The copy is attached to the active journey.
  - Any duplication marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

## FN017 : Move a component
- **Description** : Position or reposition a component in the visualization space.
- **References** : SU003, SU006.
- **Expected behavior** :
  - Moving is performed by drag-and-drop with the mouse (PC), with a stylus, or in touch mode (tablet).
  - During movement, the component automatically aligns to the grid.
  - The position (x, y) is preserved between sessions via the graphical metadata file associated with the project.
  - The component is not resizable.
  - Any movement marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

## FN018 : Delete a component
- **Description** : Delete a component from the narrative map.
- **References** : SU003 ; menu "Project › Components... › State › Delete" and "Project › Components... › Event › Delete".
- **Expected behavior** :
  - If data is associated with the component, a confirmation is requested.
  - Deletion triggers the cascade deletion of all relations connecting the component to other components.
  - Any deletion marks the map, and therefore the project, as modified.
- **Status** : Partially implemented. Agent deletion via the "Project › Components... › Agent › Delete" submenu (selection dialog + RG064 confirmation; in the agents view: direct deletion of the selected card — TSC review 28-10-2026) and via the agent card context menu in the agents view (TSK13); state deletion via the state card context menu in the agents view (TSK13: confirmation when arcs/associations exist, entry disabled for the initial state RG031, RG065 cascades) and via the state node context menu in the events view (disabled for the initial state, **SU003 confirmation when the state is connected to at least one event and/or associated with at least one agent** — TSC review 28-10-2026); event deletion via the event node context menu in the events view (**SU003 confirmation when the event is connected to at least one state** — TSC review 28-10-2026). The "State › Delete" / "Event › Delete" menu options remain specified but not implemented; they are enabled only when a node of the relevant type is selected in the workspace.

## FN019 : Manage the membership of a component to journeys
- **Description** : Modify the list of journeys to which a component is attached.
- **References** : SU003, SU005.
- **Expected behavior** :
  - Membership is managed via a multiple-choice list in the component properties, among the existing journeys of the map.
  - A component must remain attached to at least one journey: removing the last attachment is impossible (option not offered or action blocked).
  - The option is disabled if the map contains only one journey.
  - Any attachment modification marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

---

# Relations between components

## FN020 : Create a relation
- **Description** : Create a directed relation between two components of the narrative map.
- **References** : SU004 ; menu "Project › Relations... › Connect State and Event".
- **Expected behavior** :
  - In the MVP, creation is initiated from the menu (no toolbar).
  - The user selects a source component; if no component is active, it becomes active. A visual link then follows the cursor until clicking on the attachment port of the target component.
  - The relation is directed: the output of the source component is connected to the input of the target component.
  - The application refuses creation if: source and target are identical; source and target are of the same type (a state necessarily connects to an event, and vice versa); a relation already exists between the two components, in the same direction or in the opposite direction.
  - The relation is represented by a line; it follows the movements of the components it connects and is not movable as such.
  - Any creation marks the map, and therefore the project, as modified.
- **Status** : Implemented (creation mode via menu).

## FN021 : Annotate and modify a relation
- **Description** : Annotate a relation with free text and modify its editable attributes.
- **References** : SU004 ; menu "Project › Relations... › Edit".
- **Expected behavior** :
  - Annotation is performed via the relation properties panel.
  - The relation label is displayed in a tooltip on hover over the representing line.
  - If a modification results in a change of the source or target component, the application issues a warning, implicitly deletes the existing relation, and creates a new relation with the new endpoints.
  - Any modification marks the map, and therefore the project, as modified.
- **Status** : Not implemented. The menu option is specified but not implemented; it is enabled only when a relation is selected in the workspace.

## FN022 : Delete a relation
- **Description** : Delete a relation between two components.
- **References** : SU004 ; menu "Project › Relations... › Delete".
- **Expected behavior** :
  - A confirmation is requested before deletion.
  - Deletion of a relation is independent of that of the components (outside the cascade of FN018).
  - Any deletion marks the map, and therefore the project, as modified.
- **Status** : Not implemented. The menu option is specified but not implemented; it is enabled only when a relation is selected in the workspace.

---

# Narrative journeys

## FN023 : Create a journey
- **Description** : Create a narrative journey in the map.
- **References** : SU005 ; menu "Project" (the journey sidebar does not exist in the MVP).
- **Expected behavior** :
  - The new journey receives a unique identifier, a default name, and an empty description.
  - The new journey is automatically activated and becomes the current journey.
  - Any component created thereafter is attached to this journey.
  - Any creation marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

## FN024 : Rename and describe a journey
- **Description** : Modify the label and description of a journey.
- **References** : SU005.
- **Expected behavior** :
  - The modification is performed via a dialog box or a properties panel.
  - Any modification marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

## FN025 : Duplicate a journey
- **Description** : Duplicate an existing journey.
- **References** : SU005.
- **Expected behavior** :
  - The copy bears a distinct name and a new identifier.
  - Components attached to the source journey are also attached to the copy.
  - Any duplication marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

## FN026 : Activate a journey
- **Description** : Activate a journey as the current journey for editing.
- **References** : SU005 ; menu "Project" (the journey sidebar does not exist in the MVP).
- **Expected behavior** :
  - Activation is performed from the journey list.
  - The activated journey becomes the current journey: new components are attached to it and the display filtering applies to it (cf. FN029).
  - Activation marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

## FN027 : Delete a journey
- **Description** : Delete a journey from the narrative map.
- **References** : SU005.
- **Expected behavior** :
  - Deleting the last journey of the map is impossible: the application displays an explanatory message.
  - In other cases, a confirmation is requested.
  - The application identifies the components attached exclusively to the deleted journey; for each one, the user must choose a new attachment journey via a dedicated window.
  - Any deletion marks the map, and therefore the project, as modified.
- **Status** : Not documented in the menu.

---

# Visualization

## FN028 : Navigate in the visualization space
- **Description** : Navigate in the graphical representation space of the narrative map.
- **References** : SU006.
- **Expected behavior** :
  - Navigation is performed via the horizontal and vertical scrollbars.
  - The visualization space is virtually unlimited (within the limits of the operating system).
  - The component alignment grid is always visible and active.
  - Scrollbar positions and zoom level do not constitute business data: they are not preserved between sessions and do not mark the map as modified.
  - The interface remains fully functional for a window of at least 1280×720.
- **Status** : Not documented in the menu (zoom not available in the MVP).

## FN029 : Filter the display by journey
- **Description** : Display either all components and relations of the map, or only those of the active journey.
- **References** : SU006.
- **Expected behavior** :
  - The filter allows switching between "show all" and "active journey".
  - Where applicable, switching from one journey to another instantly updates the display: only the components attached to the selected journey and the relations between these components are represented.
  - Filtering does not mark the map as modified.
- **Status** : Not documented in the menu ("Display › Journey" section of the menu ignored pending its correction).

---

# Agents and agent-state associations

## FN030 : Associate agents with a state

- **Description** : Associate or dissociate one or several agents with a state of the narrative map, from the events view or from the agents view.
- **References** : SU008; state context menu "Associate agents..." (events view); agents × states matrix (agents view); RG063.
- **Expected behavior** :
    - From the events view, the state context menu opens a dialog listing all the project agents with their current association status for this state (checked/unchecked). Checking associates, unchecking dissociates.
    - The dialog allows creating a new agent and associating it in a single operation; creation follows the rules of FN031 (identifier, label, type, note), the dialog being only an additional entry point.
    - From the agents view, editing is done by checking/unchecking the matrix cell.
    - The application prevents creating a duplicate association (RG063).
    - Agents associated with a state are represented by badges on the state node in the events view.
    - Any association or dissociation marks the map, and therefore the project, as modified.
- **Status** : Implemented (TSK03/TSK04/TSK05/TSK09: association use case, "Associate agents..." dialog, badges, matrix cell editing).

## FN031 : Manage project agents

- **Description** : Create, rename, modify or delete a project agent.
- **References** : SU008, SU009; submenu "Project › Components... › Agent" (New.../Edit/Delete); agents view (context menus); TSK13.
- **Expected behavior** :
    - An agent belongs to the project; it is characterized by an integer identifier unique within the project, a label, a type (subject or object) and an optional note.
    - "New..." opens the "New Agent" dialog directly; enabled as soon as a project is open.
    - "Edit" and "Delete" open an agent selection dialog (list + "Ok"/"Cancel", "Ok" disabled without selection); enabled as soon as at least one agent exists — the selection is made in the dialog, with no dependency on the workspace selection. In all three cases, validation returns to the workspace.
    - Deleting an agent cascades the deletion of all its associations with states (RG064), with prior confirmation showing the number of deleted associations.
    - Any agent creation, modification or deletion marks the project as modified.
    - The submenu is global (menu bar): accessible from both the "Journey" and "Agents" views.
- **Status** : Implemented (TSK01/TSK02: create/edit/delete with RG064 cascade; TSK13: New.../Edit/Delete submenu, context menus of both views, "New Agent" in the journey grid context menu; **TSC review 28-10-2026: submenu behavior depends on the active view** — "Journey" view: dialogs (creation with an editable default label "Agent {id}", selection then edit/delete with the RG064 confirmation); "Agents" view: direct creation in the matrix with the default label, direct edit/delete of the selected agent card (disabled without selection), based on the card selection aligned on the events view).

## FN032 : Switch between the events view and the agents view (cross-navigation)

- **Description** : Switch from one view to the other while targeting an entity (state or agent) in order to examine its relations in the other representation.
- **References** : SU009; RG067; state context menu "Show in agents view" (events view); agent context menu "Show in events view" (agents view); state context menu "Show in events view" (agents view, TSK13).
- **Expected behavior** :
    - From the events view, "Show in agents view" switches to the agents view and highlights the column of the target state (highlight + scroll).
    - From the agents view, "Show in events view" switches to the events view and highlights all the states associated with the target agent; the rest of the graph is dimmed.
    - From the agents view, "Show in events view" on a state switches to the events view and focuses on the node of the target state (extension of the TSK10/RG067 contract by TSK13).
    - The focus is a temporary visual state (RG067): a click on empty space or the Escape key releases it.
    - The navigation does not mark the map or the project as modified.
- **Status** : Implemented (TSK10: switching and focus in both directions; TSK13: state→events view navigation from the agents view).

---

# Outside MVP scope (postponed)
- Multi-map operations: creation, duplication, deletion, and navigation between multiple narrative maps of the same project (SU001, SU002 — MVP: one single map per project).
- Import of a narrative map from a standalone file (SU002 — removed from the MVP by decision of 08-09-2026).
- Technical map export intended for re-import (SU007 — postponed, due to the exclusion of import).
- Reading export "by events" and "by agent relationships" (SU007 — agent-to-agent relations).
- Zoom of the visualization space (SU006).
- "Components" and "journeys" toolbars (SU003, SU005 — menu actions only).
- Journey consistency analysis (SU005).
- "Edit" menu (undo, redo, history, cut, copy, paste, delete): absent from user stories and not implemented; to be decided (menu removal or later specification).
- View of relations between agents (agent-to-agent relations) (SU006) — distinct workspace, outside MVP.
