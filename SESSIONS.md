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
- Commit `3c62f6f` poussé sur `dev`. TSK15 déplacée en « En revue » (revue n°03
  terminée), en attente de validation TSC avant passage en Done et démarrage de TSK13.

## 28-10-2026 — TSK15 revue n°03, correctif disparition grille au scroll

- **Signalement TSC** : la grille de la vue Agents disparaît quand on défile
  au-delà du contenu de la matrice (comportement non attendu, la grille doit
  rester visible comme dans la vue Journey).
- **Cause racine** : `_GridLineItem.shape()` vide (non-interactivité) ⇒
  `boundingRect()` dégénéré (2×2 px) ⇒ l'index BSP de `QGraphicsScene` exclut
  les lignes dès que `sceneRect` (4000×4000) dépasse `itemsBoundingRect` ;
  au scroll, `_draw_grid` recrée les lignes mais le rendu les saute.
  La vue Journey n'est pas touchée (lignes standard, `boundingRect` OK).
- **Correctif** : `boundingRect()` surchargé sur `_GridLineItem` (rect couvrant
  le trait peint ± 1 px) ; `shape()` vide conservé (non-interactivité OK).
- **Vérifications** : py_compile OK ; pytest 95 passed ; 9 scripts offscreen
  PASSED ; test de régression ajouté (rendu scène sur zone visible après scroll
  à (500,300) et (1500,1200) : grille visible, `itemAt` sur ligne = None).
- **Leçon retenue** : en Qt, `shape()` vide ne suffit pas pour la
  non-interactivité si l'item doit rester indexé/rendu hors du contenu :
  `boundingRect()` et `shape()` sont indépendants, il faut les surcharger
  tous les deux explicitement.

## 28-10-2026 — TSK15 revue n°03, ajustement police libellés objets (9 pt)

- **Demande TSC** (hors périmètre grille, en clôture de revue) : diminuer la
  police des libellés des états/événements/agents dans les vues Journey et
  Agents à la taille de l'infobulle.
- **Constat** : `node_label_font_size_px` = 12 était en réalité une taille en
  points (`QFont(family, 12)` = 12 pt, ~27 px de haut) ; l'infobulle
  (`QToolTip`) est en 9 pt (~22 px). Badge agents (Arial 7 pt gras, en dur)
  non concerné (décision TSC : libellés uniquement).
- **Modification** : `config.json` `node_label_font_size_px` 12 → 9 (constante
  partagée `BaseNode.DEFAULT_FONT` vue Journey et `MatrixCardItem` vue Agents,
  aucun changement de code nécessaire) ; charte 98 section typographie mise à
  jour ; commentaire `theme.py` ajusté ; test TSK12 point 04 (assertion
  `pointSize() == 9`).
- **Vérifications** : py_compile OK ; pytest 95 passed ; 9 scripts offscreen
  PASSED ; rendus QImage Journey et Agents validés visuellement (libellés
  ~22 px, centrés, lisibles ; badge agents inchangé).
- **Leçon retenue** : `QFont(family, size)` prend une taille en *points*, pas
  en pixels — la clé `node_label_font_size_px` était trompeuse (12 pt ≈ 16 px
  à 96 dpi, rendu ~27 px de haut avec l'espacement de ligne).

## 28-10-2026 — Clôture TSK15 et audit d'alignement documentaire

- **Clôture TSK15** : validée TSC (3 revues : QGraphicsView, grille 120×80 +
  espace extensible, libellés 9 pt), déplacée de « En revue » à « Done » dans le
  kanban.
- **Audit** : comparaison des spécifications (`docs/specification/`) avec les
  développements consignés dans SESSIONS.md (EPC01–EPC04, TSK01–TSK15).
- **Écarts trouvés et corrigés** :
  - `04_interface-FR.md` et `04_interface-EN.md` (v2.0, 27-08-2026 → v2.1,
    28-10-2026) : menu Projet>Composants>Agent « Non implémenté » → Fonctionnel
    (FN031) ; entrée « Associer des agents à un état » ajoutée au menu Relations
    (FN030) ; onglet « Agents » → Fonctionnel (TSK07–TSK15) ; section 6.bis
    réécrite (matrice graphique QGraphicsView, cartes 80×40, cases 20×20,
    grille 120×80 centrée, RG068, contrat de focus RG067, rôles) ; checklists
    mises à jour (+5 fonctionnalités agents, − « Vue Agents » des non
    implémentées, note barre d'onglets).
  - `03_features-FR.md` et `03_features-EN.md` (v2.0, 08-09-2026 → v2.1,
    28-10-2026) : FN030, FN031, FN032 « Non implémenté » → Implémenté avec
    références TSK (FN030 : TSK03/04/05/09 ; FN031 : TSK01/02 ; FN032 : TSK10).
  - `05_menu-EN.yaml` (v2.0, 27-08-2026 → v2.1, 28-10-2026) : notes View>Agents,
    Components>Agent et Relations>« Associate agents with State » mises à jour
    (implémenté / actif via la barre d'onglets).
  - `01_user_stories-FR.md` / `-EN.md` (SU009) : deux corrections — l'onglet de
    la vue agents s'appelle « Agents » et non « Relations » (TSK07) ; chaque
    colonne affiche le libellé de l'état, le type étant matérialisé par la
    couleur du contour et précisé dans l'infobulle (TSK12 point 03, le libellé
    de type ayant été supprimé).
- **Documents vérifiés conformes, sans modification** : `02_business_rules`
    (RG063–RG068 présents, FR=EN), `99_mvp_scope` (agents dans le MVP),
    `98_layout_revision` (typographie 9 pt à jour), `07_data_model`
    (Agent/State_agent_rel présents).
- **Écarts mineurs laissés en l'état** (information) : la section 6 de
    `04_interface` (vue Journey) décrit encore les anciennes couleurs du thème
    clair (`#e0e0e0`/`#808080`, fonds blancs) antérieures au thème sombre — la
    charte 98 fait autorité.
- **Vérifications** : cohérence des mentions de statut relue par grep (aucune
  mention « Non implémenté » résiduelle liée aux agents hors l'entrée de menu
  View>Agents, volontairement conservée comme relique) ; `05_menu-EN.yaml`
  parsé (YAML OK).

## 28-10-2026 — TSK13 : révision mécanique création/édition agents et associations (EPC04)

- **Cadrage** : 7 points TSC reçus et clarifiés avant implémentation (1 incohérence
  bloquante détectée et corrigée : point 05 « Edit Event/Delete Event » sur une
  carte d'état → coquille, remplacé par « Edit State/Delete State » ; précisions
  actées sur le sous-menu Agent, la bascule Journey, les menus contextuels et les
  badges d'évènement). Détail dans `docs/project/tasks/TSK13_agent_mechanics_review.md`.
- **Implémentation (7 points)** :
  - 01 : sous-menu « Project > Components... > Agent » → New.../Edit/Delete ;
    `AgentSelectionDialog` (liste + Ok désactivé sans sélection/Cancel) pour
    Edit/Delete ; « New... » actif dès qu'un projet est ouvert, Edit/Delete dès
    qu'un agent existe ; `AgentManagementDialog` supprimé (code mort).
  - 02 : « New Agent » dans le menu contextuel de la grille de la vue Journey
    (AgentDialog direct, pas de bascule).
  - 03 : création d'un Event depuis la vue Agents (menu global ET menu
    contextuel grille) → bascule onglet Journey + sélection du node créé ;
    création State/Agent depuis la vue Agents → pas de bascule.
  - 04 : menu contextuel carte agent (vue Agents) : Edit Agent / Delete Agent
    (confirmation RG064 avec nombre d'associations) / Show in journey view.
  - 05 : menu contextuel carte état (vue Agents) : Edit State / Delete State
    (désactivé pour l'état initial RG031, confirmation SU003, cascade RG065) /
    Show in journey view (extension du contrat de focus TSK10/RG067 :
    signal `focusStateInJourneyViewRequested`, bascule + focus du node).
  - 06 : menu contextuel grille (hors matrice, vue Agents) : New Agent / New State /
    New Event.
  - 07 : deux badges d'évènement par nœud State (pastille + compteur, style
    identique au badge agents, cuivre `event_badge_bg_color` #D19A66) : gauche =
    événements sources (`Event_to_state`), droite = cibles (`State_to_event`),
    même position verticale que le badge agents ; infobulle « Events (in): ... » /
    « Events (out): ... » ; refresh dynamique à la création/suppression de relation
    et au chargement. `EventBadgeService` (miroir d'`AgentBadgeService`).
- **Tests** : +11 tests unitaires `test_event_badge_service.py` ;
  `offscreen_tsk13_agent_mechanics.py` couvre les 7 points (menus, bascule,
  badges logiques + rendu visuel cuivre par différentiel de pixels) ;
  `offscreen_anomaly_regression.py` mis à jour. **106 passed** (pytest) +
  **10 scripts offscreen PASSED**.
- **Leçons Qt** : le test de focus du point 05 assombrit les items non focalisés
  (overlay translucide) — un rendu de vérification visuelle doit appeler
  `clear_focus()` au préalable ; `_find_node_by_entity_id_and_type` attend la
  classe du modèle de données (`State`/`Event`), pas la classe du node.
- **Documentation** : `04_interface-FR/EN.md` v2.2 (sous-menu Agent, menus
  contextuels des deux vues, badges d'évènement, checklists), `03_features-FR/EN.md`
  v2.2 (FN014/FN018/FN031/FN032), `05_menu-EN.yaml` v2.2 (sous-menu Agent,
  note New... Event), `98_layout_revision-FR.md` (ligne badges d'évènement +
  variable `--event-badge-bg`).
- **Kanban** : TSK13 déplacée Doing → En revue (attente validation TSC).
- **Reste à faire (information)** : section 6 de `04_interface` (couleurs thème
  clair, charte 98 autorité) ; menus « Project > View » et « Display > Journey »
  à revoir ultérieurement (décision TSC).

## 28-10-2026 — TSK13 : traitement des 3 retours de test TSC

- **Retour n°1 (badges d'évènement en vue Journey)** : suppression complète —
  `EventBadgeService`, `event_badge_in/out` + tooltip de `StateNode`,
  `refresh_event_badges` de `JourneyWorkspace`, config `event_badge_bg_color`,
  tests unitaires/offscreen, doc (04_interface, charte 98). Seuls les badges
  d'agents (TSK05) restent sur les nœuds State.
- **Retour n°2 (menu Agent selon la vue + sélection vue Agents)** :
  - Sélection des cartes (agents et états) : clic = sélection (une seule carte,
    contour pointillé teinte du type, charte 98), clic vide = désélection,
    clic droit = sélection + menu, drag RG068 maintenu (clic sélectionne,
    déplacement réordonne) ; signal `cardSelectionChanged` → `_update_menu_state`.
  - Sous-menu Agent différencié : vue Parcours = dialogues (New... pré-rempli
    « Agent {id} » éditable via `AgentDialog(default_label=...)`, Edit/Delete via
    `AgentSelectionDialog`) ; vue Agents = création directe avec libellé par
    défaut, édition/suppression directes de la carte sélectionnée (grisé sans
    sélection). Menu contextuel carte agent aligné sur le menu général
    (`_edit_agent`/`_delete_agent` comme handlers communs).
- **Retour n°3 (confirmation suppression en vue Journey, SU003)** : helper
  `_confirm_component_deletion` partagé entre `_delete_selected_component`
  (Journey : State → arcs + associations agents, Event → arcs) et
  `_delete_state_entity` (vue Agents).
- **Tests** : 95 passed (pytest, −11 tests du service supprimé) + 10 offscreen
  PASSED ; `offscreen_tsk13_agent_mechanics.py` couvre les 3 retours
  (sélection/pointillé, grisés, création/édition/suppression directes,
  confirmations SU003 Yes/No, sans confirmation si isolé).
- **Leçons Qt** : `QGraphicsView.scene` est une méthode C++ — dans
  `_MatrixGraphicsView`, passer par `self._workspace.scene` ; `itemChange`
  reçoit la nouvelle valeur de sélection (paramètre `selected` explicite,
  même pattern que `BaseNode._apply_outline`) ; `DashLine` + pattern custom
  rendu comme `CustomDashLine` par Qt ; un `refresh()` de la matrice recrée
  les items → la sélection est perdue (re-sélectionner après édition).
- **Kanban** : TSK13 Doing (retours traités, en attente de validation TSC).

## 28-10-2026 — TSK13 : correction retour n°1 (badges d'évènement déplacés en vue Agents)

- **Incompréhension corrigée** : le retour n°1 ne demandait pas de supprimer les
  badges d'évènement mais de les **retirer de la vue Journey** (connexions
  visibles, surcharge) tout en les **conservant sur les cartes d'état de la vue
  Agents** (gauche = entrants `Event_to_state`, droite = sortants
  `State_to_event`).
- **Implémentation** : `EventBadgeService` + config `event_badge_bg_color`
  restaurés ; badges sur `MatrixCardItem` (cartes état uniquement, coins bas
  gauche/droite, pastille + compteur cuivre #D19A66, infobulle « Events
  (in/out): ... ») ; `AgentsWorkspace.refresh_event_badges` /
  `refresh_all_event_badges` (calcul depuis les arcs, appelé au refresh de la
  matrice) ; `mw._refresh_agents_view_event_badges()` appelé à la
  création/suppression d'arc (`_create_state_event_relation`,
  `_delete_selected_relation`). Vue Journey : nœuds State = badge d'agents
  uniquement (TSK05).
- **Tests** : 106 passed (pytest, +11 `test_event_badge_service.py` restaurés)
  + 10 offscreen PASSED ; nouvelle section du test TSK13 couvrant positions,
  compteurs, tooltip, masquage à 0, absence sur les cartes agent et en vue
  Journey, refresh dynamique (création/suppression d'arc).
- **Leçon** : après un `refresh()` de la matrice, les items Qt sont recréés —
  ne jamais conserver de référence sur un item supprimé (RuntimeError
  libshiboken) ; re-fetch via `_state_cards[...]`.
- **Kanban** : TSK13 En revue (correction retour n°1, attente validation TSC).


## 28-10-2026 — TSK13 : repositionnement des badges d'évènement (vue Agents)

- **Demande TSC** : repositionner les badges d'évènement des cartes d'état de
  la vue Agents aux **mêmes coordonnées que les ports de connexion** des états
  en vue Journey (évalué faisable : ports = cercles 8 px à cheval sur les
  bords G/D, centrés verticalement).
- **Implémentation** : `_position_event_badges` de `MatrixCardItem` — `y =
  h/2 - d/2`, `x_in = -d/2`, `x_out = w - d/2` (centrés verticalement, à
  cheval sur les bords G/D) ; constante `EVENT_BADGE_MARGIN` supprimée ;
  commentaires mis à jour. Test offscreen TSK13 : assertions de position +
  centres vérifiés en coordonnées locales via `mapToScene` (le
  `sceneBoundingRect` de la carte inclut la marge de plume de 2 px).
- **Doc** : `04_interface` FR/EN section 6.bis, `98_layout_revision-FR.md`
  (ligne badges d'évènement), fiche TSK13 (journal + statut).
- **Tests** : 106 passed (pytest) + 10 offscreen PASSED.
- **Points de vigilance actés** : chevauchement possible badge/texte pour les
  libellés longs (à revoir ultérieurement si besoin) ; les menus « Project >
  View » et « Display > Journey » seront à revoir ultérieurement (décision
  TSC).
- **Kanban** : TSK13 Doing → En revue (attente validation TSC).


## 28-10-2026 — TSK17 : badge d'agents centré sur le coin bas-droit (vue Journey)

- **Demande TSC** : décaler le badge d'agents des nœuds d'état (vue Journey)
  pour qu'il soit **centré sur le coin bas-droit du contour**, à cheval sur les
  axes X et Y (débordement 8 px) — même principe que le repositionnement des
  badges d'évènement (TSK13). Nouvelle tâche TSK17 créée au kanban.
- **Implémentation** : `StateNode._position_agent_badge` — `x = w - d/2`,
  `y = h - d/2` ; constante `BADGE_MARGIN` supprimée ; docstrings mises à
  jour. Test offscreen `offscreen_state_badges.py` : assertions de position
  mises à jour.
- **Doc** : `98_layout_revision-FR.md` (ligne badge d'agents), `04_interface`
  FR/EN (section 6), fiche `TSK17_agent_badge_position.md` créée, kanban TSK16
  (la marge du badge n'existe plus dans le périmètre).
- **Tests** : 106 passed (pytest) + 10 offscreen PASSED.
- **Kanban** : TSK17 Doing → En revue (attente validation TSC).


## 28-10-2026 — TSK17 : retour de revue (ratio 2/3 dedans / 1/3 dehors)

- **Retour TSC** : recaler le badge d'agents vers la gauche et vers le haut
  pour que la partie extérieure au contour ne paraisse pas trop importante ;
  ratio proposé 2/3 dedans, 1/3 dehors.
- **Implémentation** : `StateNode._position_agent_badge` — `outside =
  round(diameter / 3)` = 5 px sur un diamètre de 16 ; `x = w - d + outside`,
  `y = h - d + outside` (11 px dedans, 5 px dehors). Test offscreen
  `offscreen_state_badges.py` mis à jour (assertion `outside == 5`).
- **Doc** : `98_layout_revision-FR.md`, `04_interface` FR/EN, fiche TSK17
  (statut, périmètre, journal).
- **Tests** : 106 passed (pytest) + 10 offscreen PASSED.
- **Kanban** : TSK17 reste En revue (attente validation TSC).


## 28-10-2026 — Clôture TSK13 + TSK17 et audit README

- **Kanban** : TSK13 et TSK17 passées en « Terminé » (validées TSC le
  28-10-2026). TSK13 : 3 retours de test + correction retour n°01 +
  repositionnement des badges d'évènement. TSK17 : 2 revues (centrage à
  cheval sur le coin, puis ratio 2/3 dedans / 1/3 dehors).
- **Audit README.md** (inchangé depuis le 29-08-2026) :
  - **Corrigé** : note du créateur du 22-08-2026 — suppression de la
    remarque fausse « there are no tests » ; ajout d'une note du
    28-10-2026 (MVP agents en développement actif, suite de tests :
    106 pytest + 10 offscreen).
  - **Écarts signalés à TSC (en attente de décision)** : section
    Features (pas de mention des agents ni de la double vue,
    « drag-and-drop » inexact) ; workflow (parcours narratifs et export
    décrits mais non implémentés — SU005/SU007) ; installation (aucune
    procédure dev).
  - **Acceptable** : badges PySide6 6.4.0 / Python 3.10+ = contraintes
    minimales du `pyproject.toml`.


## 28-10-2026 — README : correction de la section Features (fin de séance)

- **Décision TSC** : corriger la section Features ; conserver le workflow
  (parcours narratifs et export prévus pour le MVP) et l'installation
  (non prioritaire).
- **Correction** : la section Features mentionne désormais les agents
  (création/édition/suppression, association aux états), la double vue
  synchronisée (Journey + matrice agents × états) avec navigation croisée,
  et les badges informatifs ; le « drag-and-drop » inexact est remplacé par
  le mécanisme réel (menus + connexions en mode rubber band).
- **Fin de séance** : travaux du jour — TSK15 (clôturée), audit doc,
  TSK13 (7 points + 3 retours + correction + repositionnement badges,
  validée), TSK17 (badge d'agents 2/3-1/3, validée), audit et correction
  du README. Aucun problème bloquant. Choix actés : menus « Project >
  View » et « Display > Journey » à revoir ultérieurement ; chevauchement
  badge/texte pour libellés longs à revoir si besoin ; section 6 de
  `04_interface` décrit encore les anciennes couleurs du thème clair
  (charte 98 autorité). Prochaines tâches : TSK14 (barre latérale
  gauche), TSK16 (dimensions vue Journey dans config.json).


## 29-10-2026 — TSK18 : badges d'événement de la vue Agents, 2/3 dedans / 1/3 dehors (axe X)

- **Demande TSC** : sur la matrice agents × états, décaler légèrement les
  badges d'événement vers l'intérieur sur l'axe horizontal — badge de gauche
  vers la droite, badge de droite vers la gauche — ratio 2/3 dedans / 1/3
  dehors (au lieu de 1/2–1/2), avec arrondi entier ; même principe que l'axe
  horizontal du badge d'agents de la vue Journey (TSK17).
- **Implémentation** : `MatrixCardItem._position_event_badges`
  (`src/ui/nodes/matrix_card.py`) — `outside = round(16/3)` = 5 px, badge
  gauche `x = -outside`, badge droit `x = w - d + outside` (11 px dedans) ;
  axe vertical inchangé (centré). Test offscreen TSK13 mis à jour (nouvelles
  assertions de position). Doc : `04_interface` FR/EN (section 6.bis) et
  charte `98_layout_revision-FR.md`. Fiche `tasks/TSK18_event_badge_position.md`.
- **Tests** : py_compile OK ; 106 passed (pytest, hors test_application
  pywinauto non disponible sous Linux) ; 10 offscreen PASSED ; test jetable
  de rendu QImage : géométrie -5 / 69 sur une carte 80 px et mesure pixel
  ~5 px dehors / ~11 px dedans, confirmé visuellement sur le rendu.
- **Kanban** : TSK18 Doing → En revue (attente validation TSC).
- **Fin de séance** : travaux du jour — TSK18 (repositionnement horizontal
  des badges d'événement de la vue Agents). Aucun problème bloquant.
  Choix acté : ratio 1/3–2/3 avec `round(diameter/3)` = 5 px, identique à
  TSK17. Environnement : venv `.venv` créé avec uv (PySide6/pytest) et libs
  Qt système extraites localement sous `/tmp/libs` (pas de root dans le
  sandbox) pour les tests offscreen.


## 29-10-2026 — TSK19 : renommage de la vue « Journey » en vue « Events »

- **Demande TSC** : renommer la vue « Journey » en « Events » pour cohérence
  avec la vue « Agents » (les états sont centraux dans les deux vues) ;
  renommage de la couche UI uniquement — la couche métier `Journey` /
  `Journey_node` (parcours narratif, clés JSON des sauvegardes) est
  conservée telle quelle, ce qui sépare enfin les deux vocabulaires.
- **Implémentation** : `git mv journey_workspace.py → events_workspace.py`,
  `JourneyWorkspace` → `EventsWorkspace` ; `main_window.py` (events_page,
  events_menu, onglet `TabBar(["Events", "Agents"])`, stubs de menu
  `list_events`/`EventsList` et `view_events`/`Events` conservés,
  `_focus_state_in_events_view` / `_focus_agent_in_events_view`, 20
  isinstance) ; signaux `focusAgentInEventsViewRequested` /
  `focusStateInEventsViewRequested` dans `agents_workspace.py` ; commentaires
  des autres fichiers ; 5 scripts offscreen de test mis à jour ; doc
  (AGENTS.md, README, specs 01/02/03/04/98/99 FR+EN, kanban).
- **Tests** : py_compile OK ; 106 passed (pytest) ; 10 offscreen PASSED ;
  grep final : « journey » ne reste que dans la couche métier et les fiches
  historiques. Aucune donnée modifiée (clés JSON `journey` intactes).
- **Kanban** : TSK19 Doing → En revue ; TSK18 reste En revue ; EPC04 passée
  en Terminé (TSK13/TSK15/TSK17 déjà validées).
- **Fin de séance** : TSK18 (badges d'événement 2/3-1/3, non commité
  encore) + TSK19 (renommage vue Events, commité et poussé sur dev).
  Aucun problème bloquant. Choix acté : pluriel « Events » pour la vue,
  singulier `EventsWorkspace` ; libellés de menus stubs renommés en
  « EventsList »/« Events » ; `tests/test_journeys/` conservé (features
  du parcours narratif FN023-FN027, hors périmètre).


## 29-10-2026 — TSK20 : modèle de données, clés `content` (Agent/State/Event) et `note` sur les arcs

- **Demande TSC** (périmètre confirmé après analyse) : `content` ajouté
  après `note` dans Agent/State/Event ; `note` ajouté à Event_to_state et
  State_to_event (State_agent_rel l'avait déjà) ; report des impacts sur
  le code actif.
- **Implémentation** : `data_model.py` (5 champs ajoutés, sérialisation
  générique — pas de migration, projets existants → None) ; use cases
  create/update agent et update component (paramètre `content`, None =
  conserver) ; dialogues ComponentDialog/AgentDialog : zone **Note**
  compacte (60 px max) + zone **Content** large (160 px min), dimensions
  dans config.json (`dialog_note_max_height_px`,
  `dialog_content_min_height_px`) ; câblage main_window +
  agent_association_dialog ; 4 tests unitaires content ajoutés ; stubs
  offscreen corrigés ; doc `07_data_model` FR/EN (ordre des propriétés
  respecté), `03_features` FR/EN (FN015), `04_interface` FR/EN (notes de
  conception).
- **Tests** : py_compile OK ; 110 passed (pytest) ; 10 offscreen PASSED ;
  script jetable : round-trip JSON content/note + chargement rétrocompatible
  + champs des dialogues (hauteurs 60/160, get_values). Tooltips inchangés
  (note seule, content réservé à l'infobulle longue plus tard).
- **Kanban** : TSK20 Doing → En revue ; TSK21 créé en To do (édition des
  annotations des 3 relations, solution clic-droit sur case cochée validée,
  dépendance → #TSK20).
- **Fin de séance** : TSK19 commité/poussé (a1bcdf8) ; TSK20 non commité
  (pas d'instruction). Aucun problème bloquant.


## 29-10-2026 — TSK22 : fondations parcours (EPC05, SU005/FN023-FN026)

- **Conception** (validée TSC en séance, consignée dans
  `docs/conception/journey_attachment.md`) : `Journey_node` est la table de
  liaison vers les parcours ; le rattachement se fait sur les **connexions
  (arcs)** et associations agent-état, jamais sur les composants ; 1 arc dans
  1..n parcours = n noeuds ; appartenance des composants dérivée des noeuds ;
  objets orphelins acceptés (invisibles sous filtre parcours FN029) ;
  RG058 inchangée (pas de paire forward/backward). Vocabulaire acté (TSK26) :
  `arc` = donnée métier directionnelle, `connection` = objet visuel UI,
  `association` = State_agent_rel, `relation` = terme chapeau specs/menus.
- **Implémentation** : `Journey_node.state_agent_rel_id` +
  `NarrativeMap.active_journey_id` (+ `get_active_journey()` avec repli
  parcours par défaut, rétrocompatible) + `Journey_node.for_relation()` ;
  package `usecases/journey_management/` (create/update/activate journey,
  attach/detach relation — nommage arc/association) ; rattachement auto au
  parcours actif dans `ArcService.create_arc` et à la création d'un
  `State_agent_rel` ; cascades RG056/RG064/RG065 étendues aux noeuds
  (suppression arc / dissociation / suppression état / suppression agent) ;
  `CreateProjectUseCase` active le parcours par défaut (RG022).
- **Règles réécrites FR/EN** : RG026 (appartenance dérivée via les noeuds),
  RG027 (liste à choix multiples sur la connexion), RG031 (état initial via
  ses rattachements), RG052 (noeud créé à la création de la connexion, dans
  le parcours actif). `07_data_model` FR/EN : `active_journey_id` ajouté au
  niveau carte narrative.
- **Tests** : py_compile OK ; **127 passed** (pytest, +17 nouveaux dans
  `tests/test_journeys/test_journey_foundations.py` : activation RG022/RG023,
  RG055, rattachement auto arc/association, attach/detach 1..n parcours,
  cascades, round-trip JSON + chargement legacy sans les nouveaux champs).
  Scripts offscreen non exécutables dans le sandbox (libGL.so.1 manquant) —
  inchangé par cette tâche (pas de modification UI).
- **Kanban** : TSK18/TSK20/TSK19 passées en Terminé (commit d3786f0, poussé) ;
  EPC05 créé (TSK22–TSK26) ; TSK22 Doing → En revue ; TSK26 (normalisation
  vocabulaire) complétée avec la distinction actée.
- **Points laissés ouverts** (actés) : `sequence_order` (focus à la tâche
  concernée) ; noeud partagé arc + state_agent_rel_id (à discuter à la tâche).
- **Fin de séance** : non commité (pas d'instruction de commit).


## 29-10-2026 — TSK23 : UI de gestion des parcours (EPC05, FN023/FN024/FN026)

- **Implémentation** : `Display › Events` remplacé par `Display › Journey ›
  JourneyList` (menu dynamique cochable, parcours actif coché, clic →
  activation FN026) ; `Project › Journeys... › New.../Edit` (FN023/FN024,
  Delete stub jusqu'à TSK25) ; nouveaux dialogues `journey_dialog.py` (lb +
  note) et `journey_selection_dialog.py` (pattern AgentSelectionDialog) ;
  handlers dans `main_window.py` + état des menus ; use cases TSK22 câblés.
- **Specs** : `05_menu-EN.yaml` (JourneyList + Journeys..., note de
  remplacement), `03_features` FR/EN FN023/FN024/FN026 → Implémenté (TSK23).
- **Tests** : py_compile OK ; 127 passed (inchangé) ; script offscreen
  `tests/test_journeys/offscreen_tsk23_journey_menu.py` écrit mais non
  exécutable dans le sandbox (libGL.so.1) — à valider en séance GUI.
- **Kanban** : TSK23 Doing → En revue (TSK22 reste En revue).
- **Fin de séance** : non committé (pas d'instruction de commit).


## 29-10-2026 — TSK23 : retours de revue TSC traités

- `Project > Journeys... > Delete` supprimé du menu ; la sélection ouverte par
  Edit gagne **New...** (crée puis revient à la sélection) et **Delete**
  (stub TSK25). `_edit_journey` en boucle, `_new_journey_dialog()` mutualisé.
- Confirmé en revue : édition des connexions/arcs non implémentée
  (`_edit_selected_relation` = message « not yet implemented ») → TSK21
  (SU004/FN021) est la dépendance du rattachement aux parcours sur la
  connexion (RG027 révisée).
- Tests : py_compile OK ; 127 passed ; script offscreen TSK23 mis à jour
  (toujours à valider en GUI, libGL absent du sandbox).


## 29-10-2026 — TSK23 : 2e salve de retours de revue TSC

- Sélection permanente dans la fenêtre de sélection (refresh avec select_id =
  parcours créé) ; session Edit transactionnelle : Cancel annule les parcours
  créés via New... dans la session (rollback modèle + active_journey_id),
  New... du menu reste définitif.
- Tests : py_compile OK ; 127 passed ; offscreen TSK23 mis à jour.
