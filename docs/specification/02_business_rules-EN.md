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

## RG060
- **Description**: Before replacing the current project (e.g., opening a new project, creating a new project, closing the application), the application must check if the current project is modified and unsaved. If so, an alert is displayed to offer the user the choice to save, discard changes, or cancel the operation.
- **Classification**: Project Management and Lifecycle.

---

## 2. Narrative Map Structure