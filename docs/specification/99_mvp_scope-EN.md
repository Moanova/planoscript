# Planoscript ::: MVP Scope
- **Version**: 0.1.0-alpha
- **Status**: To be validated
- **Date**: 2026-08-26

## 1. MVP Objective
Enable an author to create and save locally a project consisting of a narrative map composed of simple components and relationships, and to export it in a readable format.
The MVP must verify that the graphical representation provides real value for structuring a narrative and that the export is understandable.

## 2. Target Audience
- Independent screenwriter.
- Non-technical user.
- Individual use, on a local workstation.

## 3. Included in the MVP
| Domain          | Included Features                                                      | References |
|---|---|---|
| Project         | Create, open, save, save as, close a project                           | SU001 |
| Narrative map   | One unique narrative map per project                                   | SU002 |
| Components      | Create, move, select and display the five types of components          | SU003 |
| Relationships   | Create and display the initially supported relationships               | SU004 |
| Visualization   | Journey view, grid, panning, scrolling                                 | SU006 |
| Persistence     | Local saving of data and layout                                        | RG003 |
| Export          | Local export for reading in a browser                                  | SU007 |

## 4. Excluded from the MVP
| Domain            | Excluded Features                                     | Rationale / Condition for Reintegration                             |
|---|---|---|
| Maps              | Import, export, duplicate or delete a map             | To be prioritized after validation of the main map                  |
| Narrative quality | Detection of dead ends, inconsistencies or contradictions | Depends on more detailed business rules                         |
| History           | Undo/redo and modification history                    | To be added after stabilization of editing operations               |

## 5. Scope Decisions
- Only one project can be open at a time.
- A project contains one and only one narrative map.
- Tool sidebars will not be implemented.
- Map visualization zoom is not available.
- Narrative data and layout information must be restorable after closing and reopening the project.
- The alternative view of relationships between agents is not available; it will be implemented in a later version.
- Technical export for re-import into another project is not available.
- Event-based reading of the export is not available; it will be implemented in a later version.
- Journey consistency is not analyzed: broken sequences will therefore not be detected.

## 6. MVP Exit Criteria
The MVP is considered ready for testing when the user can:
1. create a project;
2. create a complete journey;
3. create alternative journeys;
4. save and then reopen the project;
5. find the project in the state in which it was saved with regard to the graphical representation of the narrative map;
6. close the application without involuntarily losing modified work;
7. export the narrative map of the project.

## 8. Planned Evolutions After the MVP
- Management of multiple narrative maps within a single project.
- Narrative consistency validation.
- Event-based reading of the export.
- Technical export of narrative maps for re-import into other projects.
- Undo/redo.