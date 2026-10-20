# TSK08 — Affichage de la matrice agents × états en lecture seule

- **Épic** : EPC03 — Implémenter la vue agents (SU009, FN030)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK06 (Done), #TSK07 (Done)

## Périmètre

Contenu de l'onglet « Agents » : la matrice agents × états — une ligne
par agent du projet, une colonne par état de la carte narrative
courante, une cellule cochée matérialisant chaque association agent-état
existante. **Lecture seule dans cette tâche** (l'édition
cocher/décocher est TSK09) : la matrice reflète les données, l'ordre
des colonnes suit RG068 (défaut : ordre de création ; réordonnancement
manuel rémanent dans les métadonnées graphiques). Rafraîchissement :
toute modification des associations ou des agents depuis la vue
parcours (dialogue TSK04, suppression/édition d'agent TSK01/TSK02,
suppression/création d'état) doit se répercuter dans la matrice
(SU008 : « immédiatement répercutée dans l'autre vue »).

## Règles et critères applicables

- **SU009** : matrice agents × états ; colonnes = états de la carte
  courante, lignes = agents du projet ; cellule cochée = association ;
  ordre des colonnes RG068 ; libellé d'état tronqué selon les règles
  d'affichage courantes + type affiché.
- **RG068** : ordre par défaut = création (id croissant) ;
  réordonnancement manuel autorisé et rémanent (métadonnées graphiques,
  fichier de layout) ; état initial toujours en première colonne et non
  déplaçable ; nouvel état en fin d'ordre ; repli sur l'ordre de
  création si anomalie ; lignes (agents) : même règle ; l'ordre n'est
  pas une donnée narrative (ne marque pas la carte modifiée).
- **RG063** : unicité — une cellule = 0 ou 1 association, jamais de
  doublon affichable.
- **SU008** : les agents sont portés par le projet — la matrice liste
  tous les agents du projet, indépendamment de leurs associations.

## État des lieux (existant mobilisable)

- `AgentsWorkspace` (TSK07) : placeholder vide, à remplir — la bascule
  d'onglets ne change pas.
- `WorkspaceLayout` (view_model) : déjà persisté dans le fichier de
  layout (zoom, scroll, nodes) — lieu naturel pour l'ordre des
  colonnes RG068 (décision TSK06 : métadonnées graphiques).
- `AssociateAgentStateUseCase.find_association` : lecture de l'état
  d'association.
- `Label.format_label_for_display` / troncature à 8 caractères
  (`LABEL_MAX_DISPLAY_LENGTH`) : règles d'affichage courantes pour les
  libellés de colonnes.

## Plan d'implémentation

1. **Modèle d'ordre (RG068)** — `core/models/view_model.py` :
   - `WorkspaceLayout` : ajout de `agents_view_column_order:
     List[int]` (IDs d'états, ordre personnalisé des colonnes) et
     `agents_view_row_order: List[int]` (IDs d'agents) — sérialisés
     dans `to_dict`/`from_dict` avec valeurs par défaut vides (ordre de
     création). Rétrocompatibilité : les fichiers de layout existants
     (sans ces clés) se chargent sans erreur.
   - **Logique d'ordre pure** : fonction utilitaire (par ex. dans
     `LayoutService` ou un module dédié sans Qt)
     `resolve_matrix_order(entities, saved_order, pinned_first_id)` :
     épinglage de l'état initial en tête, entités de l'ordre sauvegardé
     dans l'ordre, entités manquantes rattrapées en fin par id
     croissant, IDs inconnus ignorés (repli RG068). Testable en tests
     unitaires.
2. **`AgentsWorkspace`** (`ui/views/agents_workspace.py`) — remplacement
   du placeholder :
   - **`QTableWidget`** : lignes = agents, colonnes = états ; en-têtes
     de colonnes = libellé tronqué + type (« Init State [Initial] ») ;
     en-têtes de lignes = libellé d'agent (+ type).
   - Cellules : `QTableWidgetItem` avec `CheckState` (coché si
     association existe) ; **lecture seule** dans TSK08 — pas de
     signal d'édition branché (les items seront éditables en
     TSK09 ; ici les CheckStates sont posés programmatiquement et
     `itemChanged` n'est pas connecté).
   - Alimentation : `refresh()` reconstruit la matrice depuis les
     données courantes (agents du projet, états de la carte,
     associations via `find_association`) en appliquant l'ordre RG068.
   - Peuplement initial : à l'ouverture d'un projet (après
     `_populate_workspace`, la matrice doit exister même si l'utilisateur
     n'a pas encore visité l'onglet Agents) et rafraîchissement à chaque
     activation de l'onglet (sécurité de cohérence).
3. **Réordonnancement des colonnes (RG064/RG068)** :
   - `QTableWidget` avec `verticalHeader().sectionsMovable` — le
     glisser-déposer d'en-têtes de colonnes est natif ; interception du
     signal `sectionMoved` pour mettre à jour `agents_view_column_order`
     dans le layout courant.
   - État initial (première colonne) : `sectionsMovable` laissé actif
     mais le déplacement de la section 0 est annulé (retour à sa
     position) — l'état initial ne peut pas être déplacé (RG068).
   - Lignes (agents) : même mécanisme sur l'en-tête horizontal.
   - Persistance : l'ordre personnalisé est collecté à la sauvegarde
     du projet (branchement dans le flux `_do_save` existant, qui
     collecte déjà le `WorkspaceLayout` du JourneyWorkspace) — l'ordre
     est une donnée du `WorkspaceLayout` (par carte narrative pour les
     colonnes ; les lignes sont au niveau projet).
4. **Rafraîchissement croisé (SU008)** :
   - MainWindow appelle `agents_workspace.refresh()` après : dialogue
     d'association (TSK04), gestion des agents (TSK01/TSK02 :
     création/édition/suppression), suppression/création d'état.
   - Un point d'entrée unique `_refresh_agents_view()` dans
     MainWindow (même pattern que `_refresh_all_state_badges`).
5. **Tests** :
   - `tests/test_agents/test_matrix_order.py` : logique pure
     `resolve_matrix_order` (ordre par défaut, ordre sauvegardé
     respecté, état initial épinglé, états manquants rattrapés, IDs
     inconnus ignorés, nouvel état en fin).
   - Persistance : aller-retour `WorkspaceLayout.to_dict/from_dict`
     avec ordres personnalisés.
   - Rendu et interactions Qt : test offscreen local (rédigé, libGL) —
     cellules cochées conformes aux associations, en-têtes corrects,
     déplacement de colonne annulé pour l'état initial.

## Décisions à valider

- **QTableWidget** comme base de la matrice (recommandé : glisser-déposer
    d'en-têtes natif, items à CheckState prêts pour TSK09, coût minimal)
    vs QTableView+modèle (plus extensible mais nettement plus lourd pour
    une matrice simple).
- **Ordre stocké dans `WorkspaceLayout`** (décision TSK06 confirmée) ;
    les lignes (agents) également dans le `WorkspaceLayout` — l'ordre
    des lignes est une préférence d'affichage, pas une donnée projet.
- **Rafraîchissement complet** (`refresh()` reconstruit) plutôt que
    mise à jour fine des cellules (recommandé : simple, sûr, la
    matrice est petite en MVP ; l'ordre fini n'est pas perturbé car
    sauvegardé).

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen de la matrice : local (libGL) — cocher/décocher non
   branché (lecture seule), cellules conformes aux associations,
   déplacement de colonnes, état initial immobile.
4. Test manuel utilisateur : à la fin d'EPC03 (décision de cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : décisions validées : ordre des lignes dans le
  WorkspaceLayout ; rafraîchissement complet. Point QTableWidget vs
  QTableView délégué à l'implémentation : **QTableWidget** retenu
  (glisser-déposer d'en-têtes natif, CheckState prêts pour TSK09, coût
  minimal pour une matrice simple).
- 15-10-2026 : implémentation terminée :
  - `view_model.py` : `WorkspaceLayout.agents_view_column_order` /
    `agents_view_row_order` (List[int], sérialisés, rétrocompatibles —
    absence de clés = ordre de création).
  - `layout_service.py` : `resolve_matrix_order(entities, saved_order,
    pinned_first_id)` — logique pure RG068 (épinglage tête, ordre
    sauvegardé, manquants en fin par id croissant, IDs inconnus
    ignorés).
  - `agents_workspace.py` (v2) : placeholder remplacé par un
    QTableWidget — lignes agents, colonnes états, en-têtes avec IDs en
    UserRole (robuste aux libellés tronqués non uniques), CheckStates
    posés via `find_association`, lecture seule (NoEditTriggers, pas
    de itemChanged — TSK09) ; déplacement d'en-têtes natif
    (sectionsMovable) avec épinglage de la colonne 0 (état initial,
    RG068/RG031 : déplacement annulé) ; ordre persisté dans le
    WorkspaceLayout via `_save_visual_order`.
  - `main_window.py` : `_current_workspace_layout` tenu au niveau
    fenêtre (le JourneyWorkspace ne référence pas le layout chargé) ;
    `agents_page.set_project()` + premier refresh dans
    `_populate_workspace` ; `_refresh_agents_view()` (point d'entrée
    unique) branché sur : activation de l'onglet Agents, dialogue
    d'association, création/édition/suppression d'agent,
    création/suppression d'état ; à la sauvegarde, l'ordre RG068 est
    fusionné dans le layout collecté avant écriture.
  - Tests : `test_matrix_order.py` (10 tests : ordres, épinglage,
    manquants, inconnus, aller-retour layout, rétrocompatibilité) ;
    test offscreen rédigé dans
    `tests/test_agents/offscreen_agents_matrix.py` (local, libGL).
    Suite complète : 95 passed.
