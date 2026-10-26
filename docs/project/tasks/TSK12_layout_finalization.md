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

## Implémentation (séance du 25-10-2026)

| # | Fichier(s) | Changement |
|---|---|---|
| 01 | `journey_workspace.py` | `setFrameShape(QFrame.NoFrame)` dans `__init__` |
| 02 | `config.json` | `grid_major_color` → `#4A4A4A` |
| 03 | `base_node.py` | Suppression de `type_label` et `_init_type_label` (TypedNode) ; le nom redevient le seul texte du nœud |
| 04 | `config.json`, `theme.py`, `base_node.py` | Nouvelle clé `node_label_font_size_px: 12` ; le label utilise `DEFAULT_FONT` (12px non gras) et est centré dans le nœud (`_position_label`, repositionné au resize) |
| 05 | `connection.py`, `journey_workspace.py` | `DEFAULT_PEN` uni ; `DASH_PATTERN = [2,3]` partagé sélection/création (stylo sélection + connexion temporaire) ; survol = trait uni en teinte de type du premier nœud défini (`_hover_pen`/`_type_tint_color`) ; suppression de `DEFAULT_SELECTED_PEN` (code mort) |
| 06 | `theme.py` | Règles `:pressed`/`:active` du handle (or doux `state_color`) dans `SCROLLBAR_STYLESHEET` et `DIALOG_STYLESHEET` |
| 07 | `agents_workspace.py` | `verticalHeader().setFixedWidth(80)` appliqué à chaque `refresh()` (aussi à 0 agent) ; pas de placeholder |
| 08 | `agents_workspace.py` | Délégué `_MatrixCardDelegate` : carte arrondie (rayon 6, bord `border_color`) dessinée avec une marge de 4px dans chaque cellule, `setShowGrid(False)` ; le fond `bg_primary` apparaît dans les interstices verticaux (agents) et horizontaux (états) |
| 09 | `agents_workspace.py` | Case à cocher centrée dans la carte (rect d'indicateur recalculé par le délégué) |
| 10 | `agents_workspace.py` | `defaultSectionSize` : lignes 40px haut, colonnes 80px large (clés `agents_view_row_header_width`/`agents_view_column_header_height`) |
| 11 | `agents_workspace.py` | En-tête de ligne = `agent.lb` (suffixe ` (typ)` supprimé) |
| 12 | `agents_workspace.py` | En-tête de colonne = libellé tronqué (suffixe ` [typ]` supprimé) |

Note d'implémentation : une première piste « lignes/colonnes intercalaires » pour le
point 08 a été écartée — elle décalait les indices du modèle (row/column) et
cassait la persistance RG068 et les tests ; l'esthétique de cartes flottantes a
été obtenue par le délégué de peinture, sans toucher à la structure du modèle.

## Journal (suite)

- 25-10-2026 (2) : implémentation des 12 points ; test offscreen dédié
  `tests/test_agents/offscreen_tsk12_layout_finalization.py` (points 01 à 12
  vérifiés un à un) ; `pytest` 95 passed hors `test_application` (pywinauto,
  skippé sans session GUI) ; 7 tests offscreen existants PASSED ; rendu
  d'intégration offscreen de la MainWindow (projet + agent + bascule onglet
  Agents + grab) OK. TSK12 passée en revue (kanban).

## Deuxième passe de revue TSC (25-10-2026, séance 2) — 2 anomalies

| Cas | Diagnostic (vérifié offscreen) | Correctif |
|---|---|---|
| 1 — carré clair bas-gauche toujours visible | Le « carré » n'était pas le cadre du workspace (diagnostic initial erroné) : bande claire de 10px = marge gauche du layout de l'InfoBar où le fond stylesheet n'était pas peint (un QWidget custom ne peint son fond stylesheet que si `WA_StyledBackground` est actif) ; résidu de 3–8px = coins arrondis des ascenseurs et coin inter-ascenseurs du QGraphicsView, où transparaissait le fond clair par défaut de la fenêtre | `InfoBar` : `setAttribute(Qt.WA_StyledBackground, True)` ; nouveau `theme.WORKSPACE_STYLESHEET` (scrollbars + fond `bg_primary` du QGraphicsView + `border: none`) appliqué au workspace avec `WA_StyledBackground` |
| 2 — matrice : coches invisibles + logs erronés au clic | (a) le délégué appelait `drawControl(CE_CheckBox, QStyleOptionViewItem, ...)` qui ne rend rien ; (b) le délégué ne surchargeait pas `editorEvent` : le toggle Qt n'opérait que dans le rect d'indicateur par défaut (gauche), pas sur la case centrée ; `_toggle_cell` lisait alors l'état inchangé et tentait l'opération inverse (log RG063 ou « No association ») | `paint` : `CE_ItemViewItem` avec le rect centré ; nouvel `editorEvent` : toggle du `CheckStateRole` si le press est dans le rect d'indicateur centré (`_indicator_rect`, source unique partagée avec `paint`) ; `_toggle_cell` ignore les clics hors case (garde `_last_press_on_indicator`) ; comparaison d'état tolérante enum/int (`in (Checked, Checked.value)`) |

Vérifications (séance 2) : pytest 95 passed ; 8 tests offscreen PASSED (TSK12 étendu aux cas 1 et 2 :
rendu pixel de la coche, clic centre → dissociation puis ré-association sans log RG063/« No association »,
clic hors case = no-op, bande au-dessus de la barre d'info sans pixel clair) ; intégration complète
MainWindow (clics réels, barre d'info « Agent 'Hero' associated/dissociated ») OK. Les tests
`offscreen_matrix_cell_edition` et `offscreen_anomaly_regression` cliquaient l'ancienne position
gauche de la case : mis à jour vers la case centrée (point 09).
