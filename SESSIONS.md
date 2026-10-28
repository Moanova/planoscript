# SESSIONS.md — Planoscript

Journal de session : informations importantes échangées avec le client
(TSC), décisions prises et anomalies traitées. Complément de `AGENTS.md`
(règles de travail) et de `docs/project/kanban.md` (suivi des tâches).

Les entrées sont ajoutées en fin de fichier, ordre chronologique.

---

## 2026-10-15 — Epic EPC01-EPC03 (agents) : bilan de fin de session

- Livraison de la gestion des agents (TSK01-TSK10) : entité `Agent`
  portée par le projet, CRUD (FN031), associations agent-état (FN030,
  RG063/RG064/RG065), vue Agents (matrice éditable, RG068), badges sur
  les nœuds d'état, navigation croisée (RG067).
- 95 tests unitaires passent ; scripts offscreen de vérification disponibles
  dans `tests/test_agents/offscreen_*.py`.

## 2026-10-23 — Session 1 : 5 anomalies remontées en test utilisateur

Anomalies corrigées (commit `3b23c2f`) :

1. **Save désactivé après création d'un agent** — la branche « new » de
   `_manage_agents` ne rafraîchissait pas l'état des menus.
2. **Décochage impossible dans la vue Agents** — `_toggle_cell` lisait le
   check state APRÈS la bascule Qt (`cellClicked` est émis après le
   toggle) : la logique était inversée.
3. **Cochage sans effet dans la vue Agents** — idem (symptôme inverse).
4. **Nouvel agent invisible dans la vue Agents** — pas de
   `_refresh_agents_view()` après création.
5. **Exception à la suppression d'un état** — appel
   `RemoveStateAssociationsUseCase.execute(entity=...)` vs signature
   `execute(state=...)` → `TypeError`.

Correctif complémentaire : import `QCloseEvent` manquant dans
`main_window.py` (`NameError` au chargement du module, latent depuis le
08-09-2026, masqué car les tests unitaires n'importent pas `MainWindow`).

Leçons retenues :
- **Qt bascule le check state d'un item user-checkable AVANT d'émettre
  `cellClicked`** : dans ce slot, le check state lu est l'état APRÈS le
  clic. L'intention utilisateur est l'inverse de l'état lu.
- **Ne jamais appeler un use case UI sans test au niveau du site
  d'appel** : le test unitaire de `RemoveStateAssociationsUseCase`
  utilisait le bon keyword (`state=`), l'appel UI utilisait `entity=`.
- **Vérifier les imports au niveau module** : une annotation de type
  évaluée à la définition de classe (`def closeEvent(self, event:
  QCloseEvent)`) plante à l'import, pas à l'exécution.

## 2026-10-23 — Session 2 : anomalie « association à l'état initial » + audit

### Anomalie : `AttributeError: 'EventNode' object has no attribute 'refresh_agent_badge'`

Symptôme : associer un agent à l'état initial depuis la vue Agents plante
**uniquement si au moins un évènement existe** dans la carte (même non
relié). L'association depuis la vue Journey fonctionne.

Cause racine (confirmée par le client) : **les IDs des composants sont
uniques PAR TYPE, pas globalement**. `NarrativeMap.get_next_id()` génère
`max+1` séparément pour `state` et `event` : l'état initial a `id=1`,
et le premier évènement créé a aussi `id=1`. Dans
`_on_matrix_association_changed` (`main_window.py`), la boucle de
recherche du nœud à rafraîchir comparait `entity.id == state_id` **sans
filtrer par type** : elle pouvait tomber sur l'`EventNode`.

**Décision client (2026-10-23) : les IDs restent uniques par type, pas
au global.** C'est un choix de conception à documenter, pas un bug de
génération. Les consommateurs d'IDs doivent donc toujours filtrer par
type.

### Audit post-anomalie (résultat)

Sites vulnérables (recherche par ID sans filtre de type), tous corrigés :

| # | Site | Impact |
|---|------|--------|
| 1 | `_on_matrix_association_changed` (`main_window.py`) | Crash (`AttributeError`) |
| 2 | `JourneyWorkspace.set_focus` (`journey_workspace.py`) | Visuel : un évènement partageant l'ID d'un état focalisé n'est pas estompé (RG067) |
| 3 | `_find_node_by_entity_id` + fallback « legacy » de `create_connection_from_data` | Latent : code mort (aucun appelant) |

Sites audités et **non vulnérables** : `WorkspaceLayout` (dicts séparés
`state_nodes`/`event_nodes` routés par `NodeType`), persistance
save/reload (testé avec collision), `ArcService` (compare des paires
typées), use cases d'association/suppression (listes de relations
typées), vue Agents (recherche dans les listes respectives), sélection
et menus (identité d'objet, pas comparaison d'ID).

### Code mort supprimé

- `WorkspaceLayout.remove_node`, `get_node_layout`,
  `get_connection_layout`, `remove_connection`, `clear` : aucun appelant
  dans `src/` ni `tests/`. Le layout est reconstruit à chaque sauvegarde
  via `collect_workspace_layout()` ; la suppression passe par
  `JourneyWorkspace.remove_node(item)` (scène).
- Fallback « legacy » de `create_connection_from_data` (clés
  `connection_layout`/`source_entity`/`target_entity`) et
  `_find_node_by_entity_id` : le seul producteur de ce format,
  `CreateRelationUseCase`, n'est jamais exécuté (création d'arc via
  `ArcService` + format « new » `source`/`target`/`relation`).

### Règle de conception à retenir

> **Les identifiants des entités métier (State, Event, Agent, arcs,
> relations) sont uniques par type au sein d'une narrative map, pas
> globalement.** Toute recherche d'un nœud/entité à partir d'un ID doit
> filtrer par type (`isinstance` / `_find_node_by_entity_id_and_type`).
> Le pattern « recherche par ID seul » est un piège : `State.id=1` et
> `Event.id=1` coexistent légitimement.

## 2026-10-24 — TSK11 : révision esthétique du layout (thème sombre)

Implémentation de la charte `docs/specification/98_layout_revision-FR.md`
(maquette `97_layout_revision-EN.svg`) : passage du thème clair au thème
sombre (fond `#1E1E1E`, surfaces `#2D2D2D`, bordures `#383838`, grille
`#333333`, texte `#FFFFFF`/`#CCCCCC`, State or doux `#E5C07B`, Event cuivre
`#D19A66`, ancres/survol blanc doux `#F0F0F0`, sélection = contour pointillé
6/4 de la teinte du type avec priorité sélection > survol > type, connexions
pointillées `#CCCCCC`, badges d'agents `#E5C07B`/`#F0F0F0`/`#1E1E1E`, onglets
identiques et neutres, dialogues en thème sombre, typographie Segoe UI).

### Travaux réalisés

- Palette 100 % centralisée dans `config.json` + nouveau module
  `src/ui/utils/theme.py` (constantes + stylesheets construits, fallback =
  charte 98) — fin des couleurs codées en dur dans l'UI.
- Nœuds : arrondi 6 px (`QPainterPath.addRoundedRect` via `paint`/`shape`),
  libellé de type « State »/« Event » ajouté en couleur du type (14 px gras),
  `_apply_outline` avec priorité sélection > survol.
- Fenêtre principale, onglets, barre d'info, scrollbars, matrice agents,
  6 dialogues, menus contextuels, `QMessageBox` (stylesheet applicatif dans
  `main.py`).

### Décisions actées (charte 98 mise à jour)

- Badges d'agents : remplissage `#E5C07B`, contour `#F0F0F0`, texte
  `#1E1E1E`.
- Dialogues : thème sombre appliqué.
- Barres latérales (gauche future, droite « Journey Filter ») : **hors
  périmètre** de TSK11 — chantier ultérieur pour le Journey Filter,
  y compris la décision Journey/Agents.
- Couleurs de layout persistées (`NodeLayout.color`/`ConnectionLayout.color`)
  : **aucune migration** — le champ n'est jamais renseigné (aucune
  fonctionnalité utilisateur ; `Connection.set_color` sans appelant).

### Choix par défaut en attente de revue visuelle

- Focus matrice agents : `#383838` ; erreurs dialogues : `#D19A66` ;
  rubber band : `#CCCCCC` pointillé.

### Vérifications

- `pytest tests/ -q` : 95 passed (hors `tests/test_application`, skippé
  sans session GUI).
- Test offscreen jetable TSK11 : 27/27 PASS (couleurs, sélection pointillée,
  priorité survol, rendu QImage pixel par pixel).
- Smoke tests offscreen : fenêtre principale + 5 dialogues OK ; tests
  offscreen existants toujours OK.

### Problème rencontré et résolu

- **Sélection pointillée non appliquée au premier `setSelected(True)`** :
  dans `itemChange(ItemSelectedChange)`, `isSelected()` retourne encore
  l'ancienne valeur → `_apply_outline()` appliquait le contour de repos.
  Corrigé en passant explicitement l'état cible
  (`_apply_outline(selected)` / `set_selected_appearance(selected)`).
- **Qt et `setDashPattern`** : un pattern personnalisé 6/4 produit
  `CustomDashLine` (et non `DashLine`) ; le test offscreen accepte les deux.
- Environnement sandbox : PySide6 installé via pip + bibliothèques système
  Qt extraites de .deb Debian dans `/tmp/qtroot` (hors dépôt).

### Leçon retenue

> **Dans `itemChange(ItemSelectedChange)`, l'état de sélection n'est pas
> encore à jour** : toujours utiliser la valeur portée par l'événement,
> jamais `isSelected()`.

## 2026-10-24 — Fin de TSK11 (validée) + création TSK12/TSK13/TSK14

- **TSK11 validée** par TSC après revue visuelle (« c'est vraiment mieux
  comme ça »). Tâche passée en Done ; commit `d87b8e6` poussé sur `dev`.
- **TSK12 — Finalisation de la révision du layout** (To do) : points
  soulevés en revue visuelle, non couverts par les documents de révision ;
  la liste sera fournie par TSC en prochaine séance.
- **TSK13 — Révision de la mécanique de création et d'édition des agents,
  et de l'association états-agents** (To do) : revue fonctionnelle des
  dialogues agent (TSK01/TSK04) et de la matrice d'association (TSK09) ;
  en attente de cadrage.
- **TSK14 — Barre latérale gauche de contrôle** (To do) : création
  des agents, états, événements et relations depuis un panneau latéral
  gauche ; dépend de TSK11 (Done). Cadrage à préciser (largeur, forme des
  contrôles, comportement relation, présence selon les vues).

## 2026-10-25 — Correctif régression « clôture d'un projet » (remontée TSC avant TSK12)

- **Anomalie** : ouvrir un projet modifié puis le fermer ne revenait pas à la
  page d'accueil, et la création/ouverture suivante levait
  `RuntimeError: libshiboken: Internal C++ object (PySide6.QtWidgets.QWidget)
  already deleted` dans `_init_workspace`
  (`while self.journey_page.layout().count():`).
- **Cause racine** : depuis TSK07, la zone centrale (`middle_layout`) est une
  structure permanente (TabBar + `QStackedWidget` welcome/journey/agents,
  créée une fois dans `__init__`). Or `_clear_project` vidait encore tout le
  `middle_layout` (héritage d'avant TSK07, où le vidage de
  `_init_workspace` avait été déplacé vers `journey_page` mais pas celui de
  `_clear_project`) : `tab_bar`, `pages`, `welcome_page`, `journey_page` et
  `agents_page` étaient détachés puis supprimés par `deleteLater`. Au retour
  à l'accueil, la page « welcome » affichée était un `QWidget` orphelin ; à la
  réouverture d'un projet, `journey_page.layout()` levait le RuntimeError.
- **Correctif** (`src/ui/main_window.py`, `_clear_project`) : ne plus vider le
  `middle_layout` ; détacher et supprimer (`setParent(None)` +
  `deleteLater()`) uniquement le `JourneyWorkspace` courant. La structure
  centrale (onglets + pages empilées) est permanente et réutilisée par le
  prochain projet.
- **Vérifications** :
  - Reproduction offscreen jetable du scénario exact (créer → modifier →
    fermer → recréer, boucle d'événements réelle via `QTimer`/`app.exec`) :
    `RuntimeError` reproduit avant correctif, disparu après ; page d'accueil
    restaurée, `middle_layout` intact (2 items), cycles
    fermer/créer/fermer/créer stables.
  - `pytest tests/ -q` (hors `tests/test_application`, skippé sans session
    GUI/pywinauto) : 95 passed.
  - Tests offscreen existants : `offscreen_workspace_tabs`,
    `offscreen_cross_view_navigation`, `offscreen_anomaly_regression`,
    `offscreen_agents_matrix`, `offscreen_matrix_cell_edition`,
    `offscreen_state_badges`, `offscreen_agent_association_dialog` : tous
    PASSED.
  - `py_compile src/ui/main_window.py` OK.
- **Choix acté** : pas de recréation de la structure centrale à la fermeture
  (coûteux, source de fuites de connexions) ; la structure TSK07 est conçue
  permanente, le correctif aligne `_clear_project` sur cette conception.
- **Leçon retenue** : un `deleteLater()` sur un widget parent détruit en
  cascade tous ses enfants C++ ; après un tel vidage, toute référence Python
  vers un descendant (ici `journey_page`, `pages`, `tab_bar`) est invalide
  même si le widget semblait « encore là » visuellement.

## 2026-10-25 — Évolution : réinitialisation de la barre d'information à la fermeture d'un projet

- **Demande TSC** (validation du correctif clôture OK) : lorsque le projet
  actif est fermé et que la page d'accueil réapparaît, la barre
  d'information conservait le message de la dernière action du projet fermé.
- **Analyse** : `InfoBar` (`src/ui/widgets/info_bar.py`) n'exposait que
  `show_message` ; aucun point de réinitialisation n'existait, et
  `_close_project` ne touchait pas la barre.
- **Évolution** :
  - `InfoBar.clear()` (nouvelle méthode) : réaffiche le message par défaut,
    lu dans `config.json` via `config_loader.get("info_bar_default_message", "")`
    (nouvelle clé, chaîne vide — conforme à la règle « aucune valeur codée en
    dur pour l'UI »). Appelée aussi dans `InfoBar.__init__` pour un démarrage
    propre.
  - `_close_project` (`main_window.py`) appelle `self.info_bar.clear()` au
    retour à la page d'accueil.
- **Vérifications** : test offscreen jetable du scénario (créer → message →
  fermer → barre vide sur l'accueil → recréer → barre réutilisable) : OK ;
  `pytest` 95 passed ; 7 tests offscreen existants PASSED ; `py_compile` OK.

## 2026-10-25 — TSK12 : finalisation de la révision du layout (12 points de revue TSC)

- **Reprise après incident** : la séance précédente avait produit l'analyse et
  les décisions (consignées dans `docs/project/tasks/TSK12_layout_finalization.md`)
  mais aucune implémentation ; le working tree était propre sur dev.
- **Travaux** : implémentation des 12 points de la revue visuelle TSK11.
  - Journey : cadre QFrame supprimé (point 01), grille majeure éclaircie à
    `#4A4A4A` (02), libellé de type « State »/« Event » supprimé des nœuds (03),
    nom en 12px non gras centré — clé `node_label_font_size_px` (04),
    connexions : passif uni, sélection/création pointillés courts `[2,3]`,
    survol uni en teinte de type or/cuivre (05), handle d'ascenseur
    `:pressed`/`:active` en or doux (06).
  - Agents : colonne des agents toujours visible (largeur fixe 80px, pas de
    placeholder — point 07), esthétique cartes flottantes par délégué de
    peinture (08), case à cocher centrée (09), en-têtes 80×40 (10), suffixes
    de type supprimés des en-têtes (11, 12).
- **Problème rencontré / choix acté** : la piste initiale du point 08 (lignes et
  colonnes intercalaires dans le QTableWidget) décalait les indices du modèle
  et cassait la persistance RG068 ; remplacée par un délégué de peinture
  (`_MatrixCardDelegate`) qui dessine des cartes arrondies espacées sans
  toucher à la structure. Le code mort `DEFAULT_SELECTED_PEN` (connection.py)
  a été retiré conformément à la règle « diff minimal, pas de code mort ».
- **Vérifications** :
  - `pytest tests/ -q` (hors `test_application`, skippé sans session GUI) :
    95 passed.
  - Test offscreen dédié `tests/test_agents/offscreen_tsk12_layout_finalization.py`
    (12 points vérifiés un à un) : PASSED.
  - 7 tests offscreen existants (matrice, édition de cellule, onglets,
    navigation croisée, badges, dialogue d'association, régression anomalie) :
    PASSED.
  - Rendu d'intégration offscreen de la MainWindow (création projet + agent +
    bascule onglet Agents + rendu) : OK.
  - Note environnement : `test_application` (pywinauto) ne peut pas être
    collecté dans un sandbox Linux (ImportError `Desktop`), indépendant du
    changement ; les libs Qt offscreen ont été installées dans /tmp pour la
    séance uniquement.
- **État** : TSK12 en revue (kanban), en attente de validation visuelle TSC.

## 2026-10-26 — TSK12 (2) : correctifs des 2 anomalies de la revue TSC

- **Anomalie 1 (carré clair bas-gauche)** : le diagnostic initial (cadre QFrame du workspace) était
  erroné — le carré restant était double : (a) la marge gauche de l'InfoBar, dont le fond stylesheet
  n'était pas peint (`WA_StyledBackground` absent, comportement Qt des QWidget custom) ; (b) les
  coins arrondis des ascenseurs et le coin inter-ascenseurs du QGraphicsView, où transparaissait le
  fond clair par défaut de la fenêtre. Correctifs : `WA_StyledBackground` sur `InfoBar`, nouveau
  `theme.WORKSPACE_STYLESHEET` (scrollbars + fond de vue `bg_primary`, `border: none`) appliqué au
  workspace avec `WA_StyledBackground`. Vérifié par scan pixel : 0 pixel clair dans la bande.
- **Anomalie 2 (matrice agents × états)** : cause racine = le délégué `_MatrixCardDelegate`
  (points 08/09) — `drawControl(CE_CheckBox, QStyleOptionViewItem)` ne rend rien (coches
  invisibles) et `editorEvent` non surchargé basculait l'état selon le rect d'indicateur par défaut
  (gauche) au lieu de la case centrée, d'où les logs trompeurs RG063/« No association » (les use
  cases idempotents ont protégé les données). Correctifs : `CE_ItemViewItem` dans `paint`,
  `editorEvent` dédié avec rect d'indicateur centré partagé (`_indicator_rect`), garde dans
  `_toggle_cell` (clic hors case = no-op), comparaison enum/int tolérante.
- **Tests mis à jour** : `offscreen_anomaly_regression` et `offscreen_matrix_cell_edition`
  cliquaient l'ancienne position gauche de la case — position mise à jour (centre) ; test TSK12
  étendu aux deux anomalies (rendu pixel, cycle clic/re-clic, no-op hors case, bande InfoBar).
- **Vérifications** : pytest 95 passed ; 8 tests offscreen PASSED ; intégration MainWindow
  complète (clics réels via QTest, messages de barre d'info corrects, aucun log erroné) OK.
- **Leçon retenue** : deux pièges Qt confirmés expérimentalement — (1) un QWidget custom ne peint
  son fond stylesheet sans `WA_StyledBackground` ; (2) dans un délégué custom, le rendu ET le
  hit-testing de l'indicateur doivent partager le même rect, sinon l'état visuel et l'état du
  modèle divergent silencieusement.

## 2026-10-26 — TSK12 (3) : en-têtes de matrice non redimensionnables

- **Demande TSC** : empêcher le redimensionnement à la souris des en-têtes de la matrice agents × états.
- **Correctif** : `setSectionResizeMode(QHeaderView.ResizeMode.Fixed)` sur les en-têtes vertical
  (agents) et horizontal (états) de la matrice — dimensions fixes pilotées par la config (80×40),
  réordonnancement RG068 conservé.
- **Vérifications** : offscreen (modes Fixed, dimensions inchangées) ; assertion dans le test TSK12 ;
  pytest 95 passed ; 8 tests offscreen PASSED.

## 2026-10-26 — TSK12 : validation TSC et clôture

- TSC confirme le fonctionnement des en-têtes non redimensionnables et valide la tâche.
- TSK12 passée de « En revue » à « Terminé » (Done) dans le kanban.

## 2026-10-26 — TSK15 : matrice agents × états en vue graphique (EPC04)

- **Demande TSC** : revoir l'implémentation de la matrice d'association agents × états
  (vue Agents) du point de vue UX/esthétique — option B retenue : remplacer le
  QTableWidget par une QGraphicsView, cohérente avec la vue Journey.
- **Travaux** :
  - Étude d'options (A : délégués QTableWidget custom / B : QGraphicsView / C : widgets
    purs) — B retenue par TSC.
  - Kanban : EPC04 créé (TSK15 → TSK13), TSK16 créée (paramétrage config.json des
    dimensions de la vue Journey actuellement en constantes de classe).
  - Implémentation : `matrix_card.py` (MatrixCardItem + MatrixCheckItem),
    `agents_workspace.py` réécrit, contrat public inchangé (main_window.py non modifié
    hors correction de persistance).
  - Bug corrigé en passant : `_do_save` lisait `_current_workspace_layout` (jamais
    initialisé) → l'ordre personnalisé RG068 n'était jamais sauvegardé ; lit désormais
    `agents_page.layout_data`.
- **Choix actés** : agents en cuivre #D19A66 (teinte Event, les agents n'ont pas de nœud
  dans la vue Journey) ; cases 20×20 toujours visibles, fond #383838, coche #F0F0F0,
  clic actif uniquement dans la case ; espacement 20 px et dimensions des cases dans
  config.json ; fond #1E1E1E sans grille ; épinglage de l'état initial par contrainte
  applicative au lâcher du drag.
- **Problèmes rencontrés** : environnement bac à sable dépourvu de PySide6 et des libs
  GL/X11 — installation pip (PySide6, pytest, Pillow) + extraction de paquets .deb dans
  /tmp/gllibs (LD_LIBRARY_PATH) pour exécuter les tests offscreen.
- **Vérifications** : py_compile OK ; pytest 95 passed (--ignore=test_application,
  pywinauto indisponible) ; 9 scripts offscreen PASSED (matrice, édition, reorder,
  régression anomalies, navigation croisée, onglets, dialogue association, badges,
  finalisation TSK12) ; rendu QImage validé (cases peintes, contours or/cuivre, fond
  sombre, écart 20 px).
- **État** : TSK15 en « En revue », commit 0314ee0 poussé sur dev. En attente de
  validation TSC avant passage en Done et démarrage de TSK13.

## 26-10-2026 — TSK15 revue n°2 (grille + message de rejet)
- Grille majeure de fond de la matrice agents×états : lignes espacées de 80 px, décalées de 10 px (moitié de l'espacement composants), couleur `#4A4A4A`, zValue -2. Lignes non interactives via sous-classe `_GridLineItem` (`shape()` vide) — le monkey-patching d'instance ne fonctionne pas en PySide6.
- Message info bar quand le déplacement de l'état initial est rejeté : signal `reorderRejected(str)` sur `AgentsWorkspace`, connecté à `info_bar.show_message` dans `MainWindow` (connexion déplacée après la création de l'info bar — bug attrapé par les tests offscreen).
- Corrections de tests : bloc "pixels de grille" déplacé après la définition de `render`/`offset` dans `offscreen_agents_matrix.py`.
- Vérifications : py_compile OK, pytest 95 passed, 9 scripts offscreen PASSED.
- Commit `11fa4d4`, poussé sur `dev`. TSK15 reste "En revue" en attente de validation TSC.

## 28-10-2026 — TSK15 revue n°03 (grille 120×80 centrée + espace extensible)

- **Demande TSC corrigée** : objets State/Agent/cases centrés dans une grille
  120×80 (cartes : marge 20 px sur les 4 côtés ; cases : 50 px horizontal, 30 px
  vertical), la grille remplace l'ancienne 80×80, la logique de la matrice est
  prioritaire. Incohérence initiale détectée et levée avec TSC : le pas de la
  matrice passe de 100×60 à 120×80 (espacement 40 px entre objets).
- **Implémentation** (`agents_workspace.py` v5) : constantes `_CELL_WIDTH`/
  `_CELL_HEIGHT` (config `agents_view_cell_width`/`_height`, anciennes clés
  `agents_view_component_spacing` retirée), offsets dérivés 20/20 (cartes) et
  50/30 (cases) ; grille dessinée sur le viewport uniquement (pattern Journey,
  redraw sur scroll/resize), origine (0,0), lignes non interactives ; scène
  minimale 4000×4000 extensible uniquement vers la droite/le bas
  (`_expand_scene_right_down`) ; reorder et focus recalés sur la grille
  cellulaire.
- **Vérifications** : py_compile OK ; pytest 95 passed ; 9 scripts offscreen
  PASSED ; rendu QImage MainWindow validé visuellement (grille alignée sur les
  cellules, cartes/cases centrées, grille sur tout le viewport, ancrée
  haut-gauche).
- **Leçon retenue** : avec l'antialiasing, un trait 1 px sur coordonnée entière
  rend des pixels ~52-63 (pas la couleur pleine #4A4A4A=74) — le test de rendu
  vérifie une plage entre le fond (#1E1E1E) et la couleur de grille, et doit
  scanner à la position visible (après retour du scroll à l'origine).
- **État** : TSK15 en « Doing » (revue n°03), en attente de validation TSC.
