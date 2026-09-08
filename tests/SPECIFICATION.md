# Test Specification - Planoscript

## Document Version
- **Version**: 1.0
- **Date**: 08-09-2026
- **Status**: Specifications for FN001 to FN011

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
