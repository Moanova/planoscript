# TSK15 — Révision de l'implémentation de la matrice d'association des agents aux états

- **Épic** : EPC04 (révision de la mécanique de gestion des agents et des associations avec les états)
- **Statut** : En revue (implémentation et tests terminés, en attente de validation TSC)
- **Date de création** : 26-10-2026
- **Dépendances** : aucune (TSK08/TSK09/TSK10 Done)
- **Bloque** : TSK13

## Périmètre

Remplacer l'implémentation de la matrice agents × états de la vue Agents
(`QTableWidget`) par une vue graphique (`QGraphicsView` + `QGraphicsScene`),
cohérente avec la logique applicative de la vue Journey. Le comportement
fonctionnel est strictement préservé ; seule la représentation change.

## Exigences validées avec TSC (26-10-2026)

1. **Apparence des composants** : les cartes « State » ont la même
   apparence que les nœuds de la vue Journey (surface `#2D2D2D`, contour
   or doux `#E5C07B`, arrondi ~6 px, libellé centré). Les cartes « Agent »
   ont la même apparence mais avec la teinte des événements (cuivre
   `#D19A66`) — les agents n'ont pas de nœud dans la vue Journey.
2. **Séparation** : 20 px entre composants, horizontal pour les états
   (colonnes), vertical pour les agents (lignes). Paramétré dans
   `config.json` (`agents_view_component_spacing`).
3. **Cases à cocher** : toujours visibles, 20×20 px, fond gris moyen
   `#383838` (teinte de contour des lignes/colonnes de l'ancienne matrice),
   symbole de coche en blanc doux `#F0F0F0` quand cochée. Le clic ne
   toggle l'association que dans cette zone ; un clic ailleurs est un
   no-op. Taille et couleur paramétrées dans `config.json`
   (`agents_view_checkbox_size`, `agents_view_checkbox_color`).
4. **Fond de la vue** : uni `#1E1E1E`, sans grille (inchangé).
5. **Réordonnancement par glisser-déposer** (RG068) : conservé. Drag des
   cartes d'états (horizontal) et d'agents (vertical). L'état initial reste
   épinglé en première colonne (contrainte applicative au lâcher, comme
   le `moveSection` de l'ancienne implémentation). Les cases suivent les
   cartes (repositionnement global depuis les listes ordonnées).
6. **Persistance** : ordre des colonnes/lignes conservé dans
   `WorkspaceLayout.agents_view_column_order` / `agents_view_row_order`
   (RG068), entre les sessions.

## Comportement préservé (contrat inchangé)

- Clic case → use cases `AssociateAgentStateUseCase` /
  `DissociateAgentStateUseCase` ; en cas d'échec, restauration de l'état
  visuel à l'état des données.
- Signal `associationChanged(state_id, agent_lb, associated)` émis après
  succès (badge + info bar, `main_window.py` inchangé).
- Signal `focusAgentInJourneyViewRequested(agent_id)` (menu contextuel
  « Show in journey view » sur une carte agent, TSK10).
- Focus colonne état (TSK10, RG067) : `set_focus(state_id)` surligne la
  colonne (cartes + cases de l'état), défile jusqu'à elle ;
  `clear_focus()` / `has_focus()` ; Échap et clic dans le vide relâchent
  (géré par `MainWindow`).
- Interface publique de `AgentsWorkspace` inchangée : constructeur,
  `set_project(project_service, layout_data, associate_usecase,
  dissociate_usecase)`, `refresh()`, `set_focus()`, `clear_focus()`,
  `has_focus()`. Aucun changement dans `main_window.py` (sauf point
  « Bug corrigé » ci-dessous).
- Infobulles immédiates au survol des cartes (pattern AGENTS.md :
  `hoverEnterEvent` + `QToolTip.showText`, `viewportEvent` avale
  l'événement `ToolTip` automatique).

## Bug corrigé en passant (RG068)

`_do_save` (`main_window.py`) copiait l'ordre de la matrice depuis
`self._current_workspace_layout`, attribut jamais initialisé (`getattr`
défensif → `None`) : l'ordre personnalisé de la matrice n'était en
réalité jamais reporté dans le layout sauvegardé. La copie lit
désormais `self.agents_page.layout_data` (l'objet `WorkspaceLayout`
chargé au populate et tenu à jour par la vue).

## Plan d'implémentation

1. `config.json` : `agents_view_component_spacing` (20),
   `agents_view_checkbox_size` (20), `agents_view_checkbox_color`
   (`#383838`), `agents_view_checkbox_check_color` (`#F0F0F0`).
2. `src/ui/nodes/matrix_card.py` (nouveau) : `MatrixCardItem`, item
   graphique réutilisable renders comme un nœud Journey (rounded rect
   80×40, radius `node_corner_radius_px`, contour teinte du type, libellé
   centré, hover blanc doux, infobulle immédiate). Ne porte pas de ports
   (pas de connexions dans cette vue).
3. `src/ui/views/agents_workspace.py` (réécrit) : `QGraphicsView` +
   `QGraphicsScene`. Cartes états en ligne horizontale (haut), cartes
   agents en colonne verticale (gauche), cases 20×20 aux intersections.
   Drag des cartes avec contrainte d'épinglage ; écriture de l'ordre dans
   `layout_data` à chaque reorder. Focus colonne par rectangle de
   surbrillance + `scrollTo`.
4. `src/ui/main_window.py` : correction de la persistance de l'ordre
   (point « Bug corrigé »). Aucune autre modification.
5. Tests : réécriture de `tests/test_agents/offscreen_agents_matrix.py`
   et `offscreen_matrix_cell_edition.py` contre la nouvelle API (mêmes
   scénarios + vérification du repositionnement des cases après reorder
   + rendu `QImage` pour l'aspect visuel). `test_matrix_order.py`
   (logique pure RG068) inchangé.
6. Vérifications : `py_compile`, suite pytest complète, tests offscreen.

## Journal

- 26-10-2026 : tâche créée à la demande de TSC (étude d'options A/B/C
  réalisée en amont ; option B retenue : vue graphique). Passage en
  Doing, feu vert TSC pour l'implémentation.
- 26-10-2026 : implémentation terminée.
  - `src/ui/nodes/matrix_card.py` (nouveau) : `MatrixCardItem` (carte
    80×40, rendu nœud Journey, contour teinte du type, infobulle
    immédiate) et `MatrixCheckItem` (case 20×20 toujours visible, fond
    `#383838`, coche `#F0F0F0`, clic actif uniquement dans la case).
  - `src/ui/views/agents_workspace.py` (réécrit) : `QGraphicsView` +
    `QGraphicsScene`, fond `#1E1E1E` sans grille. Cartes états en
    colonnes (or `#E5C07B`), cartes agents en lignes (cuivre `#D19A66`,
    décision TSC). Espacement 20 px. Drag des cartes avec épinglage de
    l'état initial ; cases repositionnées avec les cartes ; ordre
    persisté dans `WorkspaceLayout` (RG068). Focus colonne TSK10
    (bande translucide + surface relevée + surbrillance des cases),
    menu contextuel « Show in journey view » sur les cartes agents.
    Contrat public inchangé (`set_project`, `refresh`, `set_focus`,
    `clear_focus`, `has_focus`, signaux).
  - `src/ui/main_window.py` : correction de la persistance RG068
    (`_do_save` lisait un attribut `_current_workspace_layout` jamais
    initialisé → l'ordre personnalisé n'était jamais sauvegardé ;
    lit désormais `agents_page.layout_data`).
  - `config.json` : `agents_view_component_spacing` (20),
    `agents_view_checkbox_size` (20), `agents_view_checkbox_color`
    (`#383838`), `agents_view_checkbox_check_color` (`#F0F0F0`).
  - Tests : `offscreen_agents_matrix.py` et
    `offscreen_matrix_cell_edition.py` réécrits (mêmes scénarios +
    rendu `QImage` : cases peintes, contours or/cuivre, fond sombre) ;
    `offscreen_matrix_reorder.py` nouveau (drag agents/états, épinglage,
    cases suivies, persistance + rechargement) ;
    `offscreen_anomaly_regression.py` et
    `offscreen_tsk12_layout_finalization.py` adaptés à la nouvelle API.
  - Vérifications : `py_compile` OK ; pytest 95 passed
    (`--ignore=tests/test_application`, pywinauto indisponible dans le
    bac à sable — ces tests sont skippés automatiquement sans session
    GUI) ; 9 scripts offscreen agents tous PASSED (matrice, édition,
    reorder, régression anomalies, navigation croisée, onglets, dialogue
    association, badges, finalisation TSK12).
  - Note environnement : PySide6 + libs GL/X11 installés dans le bac à
    sable pour exécuter les tests offscreen (absents à l'origine).
- 26-10-2026 (revue TSC) : 4 KO corrigés.
  - **En-têtes disparus + superposition agents/cases** : cause racine
    unique — la zone des cases démarrait au même x/y que les cartes
    en-têtes (agents x=20, états y=20), donc les cases de la première
    colonne étaient centrées dans les cartes agents (chevauchement
    confirmé par `sceneBoundingRect().intersects`). Correctif : la zone
    des cases démarre après la colonne agents et la ligne états
    (`_CELLS_LEFT = margin + card width + spacing`,
    `_CELLS_TOP = margin + card height + spacing`) ; les en-têtes
    (cartes agents/états) restent visibles et les cases sont disjointes
    des cartes agents (vérifié par test d'intersection).
  - **Matrice centrée** : `QGraphicsView` aligne la scène au centre
    par défaut (`alignment = AlignCenter`). Correctif :
    `setAlignment(AlignLeft | AlignTop)` — la matrice est ancrée dans
    le coin haut-gauche du viewport.
  - Géométrie résultante : première carte état à
    x = 20 + 80 + 20 = 120, y = 20 ; première carte agent à x = 20,
    y = 20 + 40 + 20 = 80 ; première case centrée dans la cellule
    (120, 80). Le décalage demandé (80 + 20) est l'offset relatif entre
    la colonne agents et la première colonne d'états (resp. ligne
    états et première ligne d'agents).
  - Tous les recalculs de position (refresh, relayout, drag, focus)
    utilisent les nouvelles constantes `_CELLS_LEFT`/`_CELLS_TOP`/
    `_AGENTS_LEFT`/`_STATES_TOP`.
  - Tests offscreen mis à jour (géométrie attendue, assertion de
    non-chevauchement, assertion d'ancrage haut-gauche) ; py_compile
    OK, pytest 95 passed, 9 offscreen PASSED.
- 26-10-2026 (revue TSC n°2) : grille majeure de fond + message de rejet.
  - **Grille** : lignes majeures uniquement (pas de grille 20×20), décalées
    de 10 px (moitié de l'espacement composants) en horizontal et vertical,
    couleur `#4A4A4A` paramétrée (`grid_major_size`, `grid_major_color` dans
    config.json), zValue -2 (sous les cartes et cases). Les lignes sont des
    `_GridLineItem` (sous-classe `QGraphicsLineItem` avec `shape()` vide) :
    non interactives — le monkey-patching d'instance de `shape()` ne
    fonctionne pas en PySide6, la sous-classe oui. Vérifié : `itemAt` sur une
    ligne retourne None, les cartes restent cliquables, pixels de grille
    rendus (couleur antialiasée ~`#343434`).
  - **Message de rejet** : nouveau signal `reorderRejected(str)` sur
    `AgentsWorkspace`, émis uniquement quand l'état initial lui-même est
    déplacé (pas quand un autre état cible la colonne 0, ni sur un
    réordonnancement valide). Connecté dans `MainWindow` à
    `info_bar.show_message` (connexion placée après la création de
    l'info bar). Message : `"State '<lb>' is the initial state and cannot
    be moved"`.
  - Tests : assertions grille dans `offscreen_agents_matrix.py` (offset 10,
    espacement 80, non-interactivité, rendu pixels) ; assertions message de
    rejet dans `offscreen_matrix_reorder.py` (3 scénarios).
  - Vérifications : py_compile OK, pytest 95 passed, 9 scripts offscreen
    PASSED.
