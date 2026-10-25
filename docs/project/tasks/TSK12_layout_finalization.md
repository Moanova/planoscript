# TSK12 — Finalisation de la révision du layout

- **Épic** : aucune (suivi de TSK11)
- **Statut** : Doing
- **Date de création** : 24-10-2026
- **Dépendances** : #TSK11 (Done)

## Périmètre

12 points soulevés par TSC lors de la revue visuelle de TSK11 (thème
sombre), reçus le 25-10-2026, non couverts par les documents de révision du
layout (`docs/specification/98_layout_revision-FR.md`,
`docs/specification/97_layout_revision-EN.svg`).

## Contexte

TSK11 a livré le thème sombre complet (palette centralisée dans
`config.json` + `src/ui/utils/theme.py`, nœuds, connexions, vues, onglets,
barre d'info, matrice agents, fenêtre principale, dialogues, menus
contextuels, `QMessageBox`). Revue visuelle validée le 24-10-2026. Les
ajustements fins constatés lors de cette revue (hors périmètre initial de
la charte 98) sont regroupés ici.

## Analyse et décisions par point (validées TSC le 25-10-2026)

| # | Point TSC | Analyse | Décision retenue |
|---|---|---|---|
| 01 | Espace gris clair coin bas-gauche avant la barre d'info | Cadre `QFrame` StyledPanel du `JourneyWorkspace` (frameWidth=1), dessiné par le style en gris clair `#b8b8b8` sur les bords haut/gauche/droit + bas (juste au-dessus de la barre d'info ; les scrollbars couvrent le reste) | **Suppression du cadre** : `setFrameShape(QFrame.NoFrame)` sur le workspace |
| 02 | Grille : carrés 4×4 (lignes majeures 80px) peu visibles | `grid_major_color` = `#333333` = `grid_minor_color` → lignes majeures indiscernables | **Éclaircir** : `grid_major_color` → `#4A4A4A` (1px conservé) |
| 03 | Nœuds désignés par leur type (« State »/« Event ») | `TypedNode._init_type_label` affiche `ENTITY_TYPE_LABEL` au-dessus du nom | **Supprimer le libellé de type** sur les nœuds (maquette non reprise) |
| 04 | Police du nom des nœuds trop grande | `label` en `TITLE_FONT` = 14px gras (même taille que le libellé de type) ; matrice Agents en ~12px | **12px non gras** (aligné sur la police du tableau Agents) ; le libellé de type étant supprimé (point 03), le nom redevient le texte principal du nœud |
| 05 | Connexions : pointillés courts = création + sélection ; passif = uni ; survol = uni « inversé » | Actuel : passif = pointillés longs 6/4 `#CCCCCC` ; sélection = pointillés mêmes couleur ; survol = uni `#F0F0F0` ; création (temp) = `Qt.DashLine` (pointillés courts) | **Passif = trait uni `#CCCCCC`** ; **sélection = pointillés courts** (création et sélection partagent l'apparence) ; **survol = trait uni en teinte de type** (or/cuivre selon le type des nœuds connectés) |
| 06 | Ascenseur sélectionné quasi invisible (gris clair) | `SCROLLBAR_STYLESHEET` : handle `#383838`, `:hover` `#CCCCCC`, **aucune règle `:pressed`/`:active`** → le style QStyleSheetStyle retombe sur le rendu Fusion par défaut en état pressé (gris clair) | **Ajouter une règle `:pressed` (et `:active`) sur le handle** en or doux `#E5C07B` (accent charte) |
| 07 | Colonne de gauche (agents) n'apparaît que s'il y a ≥1 agent | `QTableWidget` : `verticalHeader` width 0 quand `rowCount == 0` (comportement Qt par défaut) | **Toujours afficher le header vertical** : réserver une largeur fixe (ex. 80px) même à 0 ligne, ou masquer proprement avec un placeholder — à préciser en implémentation (piste : `setVerticalHeaderMinimumSectionSize` + header visible) |
| 08 | Agents contigus (pas d'espacement vertical) ; états contigus (pas d'espacement horizontal) | `QTableWidget` : `defaultSectionSize` v=30 h=100, cellules contiguës, `gridline-color` = bordure | **Espacement** : espacer les lignes (agents) et les colonnes (états) — via `setVertical/HorizontalHeaderDefaultSectionSize` + marges visuelles (piste : espacement via `QTableWidget` spacing ou délégation) |
| 09 | Case à cocher : espace à droite à supprimer, case centrée | `QStyle.subElementRect(SE_ItemViewItemCheckIndicator)` place la case à gauche (x=3) dans la cellule (100×30) | **Centrer la case à cocher** dans la cellule (délégation ou `setTextAlignment(Qt.AlignCenter)` + indicateur centré) |
| 10 | Cellules de la matrice : dimensions comparables aux nœuds Journey (80×40) | Cellules actuelles : 100×30 (h=100, v=30) | **En-têtes 80×40** : en-têtes de lignes (agents) 80px de large, en-têtes de colonnes (états) 40px de haut — décision TSC |
| 11 | Pas besoin de préciser le type de l'agent dans sa dénomination (matrice) | `agents_workspace.refresh` : header = `f"{agent.lb} ({agent.typ})"` | **Supprimer le suffixe ` (typ)`** des en-têtes de lignes |
| 12 | Pas besoin de préciser le type de l'état dans sa dénomination (matrice) | `agents_workspace.refresh` : header = `f"{label} [{state.typ}]"` | **Supprimer le suffixe ` [typ]`** des en-têtes de colonnes |

## Journal

- 24-10-2026 : tâche créée à la demande de TSC, en attente de la liste des
  points à traiter (prochaine séance).
- 25-10-2026 : liste des 12 points reçue ; TSK12 passée en Doing (kanban) ;
  analyse point par point réalisée (investigation offscreen : rendu pixel
  par pixel de la fenêtre, du workspace, de la matrice, des scrollbars) ;
  questions de cadrage posées à TSC et décisions enregistrées ci-dessus.
