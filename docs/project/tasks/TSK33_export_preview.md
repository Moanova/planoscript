# TSK33 — Implémentation de l'aperçu d'export (SU010/FN033)

- **Épic** : SU007/SU010 (export de carte et aperçu d'export)
- **Statut** : En revue (01-11-2026) — tests interactifs GUI à venir (TSC)
- **Date de création** : 01-11-2026
- **Dépendances** : → #TSK32 (RG069, ordre de succession réel — En revue, validation embarquée avec TSK31)
- **Consommée par** : l'implémentation de l'export fichier `Files > Export Map` (FN013, hors périmètre de cette tâche)

## Objectif

Implémenter l'aperçu d'export de la carte narrative (SU010/FN033), conformément
aux décisions actées de la conception (`docs/conception/export.md`, TSK31,
01-11-2026) :

1. **Troisième espace de travail « Export »** en lecture seule : onglet « Export »
   dans la barre d'onglets à côté de « Events » et « Agents » ; contenu jamais
   éditable, liens inertes, la génération de l'aperçu **ne touche jamais** à
   `set_modified`.
2. **Régénération à la bascule sur l'onglet Export** (+ après chaque modification
   du modèle si l'onglet est déjà actif, via le signal métier de modification) ;
   jamais en arrière-plan.
3. **Aperçu dynamique selon le filtre FN029** : filtre actif → parcours actif ;
   « All journeys » → tous les parcours.
4. **Restitution centrée sur les états** depuis l'état initial, dans l'ordre de
   succession réel (RG069) : états listés une seule fois ; pour chaque état (sauf
   l'initial), événements prédécesseurs + agents associés annotés de leur parcours
   (via `Journey_node`) ; libellé en titre, `content` en corps de texte, type
   affiché, `note` en infobulle au survol ; sommaire des parcours (un seul lien si
   filtre actif) ; section agents détaillée ; section composants orphelins ;
   événements pendants ignorés dans le déroulé et listés en fin avec un marqueur.
5. **Généralisation du code « 2 espaces de travail » → 3 onglets** :
   `TabBar(["Events", "Agents"])` + `QStackedWidget` (`main_window.py:149,155`),
   `_on_tab_changed` (branche « Export » = régénération de l'aperçu), et les 6
   tests `currentTab() == "Agents"` (`main_window.py:524, 1015, 1213, 1234, 1267,
   1292`) à rendre explicites (dans l'onglet Export readOnly, les entrées
   Agent New/Edit/Duplicate/Delete sont traitées/désactivées ; la création
   d'événement ne rebascule pas depuis Export).

## Architecture prévue

- Service d'export dédié (ex. `core/services/export_service.py`) :
  `build_reading_text(narrative_map, journey=None)` → texte de lecture rendu
  (HTML 4 subset, `journey=None` = tous les parcours), s'appuyant sur
  `JourneySequenceService` / `Journey_node.sequence_order` (RG069) ;
  `export_map_html(project, narrative_map, dest_dir)` viendra plus tard (FN013,
  hors périmètre de cette tâche).
- UI : `ExportWorkspace` (QWidget + QTextBrowser readOnly) dans `src/ui/views/`,
  troisième page du `QStackedWidget` ; infobulle sur ancres en custom
  (`anchorAt` + `QToolTip.showText`, pattern des nœuds du workspace).
- Régénération déclenchée par `_on_tab_changed("Export")` et par le signal de
  modification du projet si l'onglet est actif.

## Livrables

- `src/ui/views/export_workspace.py` + intégration `main_window.py` (3 onglets) ;
- `src/core/services/export_service.py` (`build_reading_text`) ;
- généralisation 2 → 3 espaces de travail dans `main_window.py` ;
- tests unitaires (restitution, ordre RG069, filtre FN029, readOnly,
  non-modification du flag) + test offscreen si point visuel.

## Journal

- 01-11-2026 : tâche créée en To do (décision TSC). Spécifications rédigées avec la
  clôture de TSK31 : SU010 + FN033 (FR/EN), 04_interface, 05_menu, 99_mvp_scope.
- 01-11-2026 : passée en Doing (feu vert TSC, kanban v31). Décisions retenues :
  détection des modifications par hook `ProjectService.on_modified` (pur Python,
  core reste Qt-free) traduit en signal Qt `map_modified` par MainWindow — régénération
  de l'aperçu en direct uniquement si l'onglet Export est actif ; menus d'édition
  laissés actifs en onglet Export ; menu View aligné avec 3 stubs (Events/Agents/Export) ;
  sous filtre actif, associations agent-état restreintes au parcours actif ; TSK34 créée
  pour la revue de code (dette technique) ; périmètre = aperçu seul (export fichier
  FN013 hors périmètre).
- 01-11-2026 : implémentation (kanban v31 → v32, En revue) —
  - `ProjectService.on_modified` : hook callable pur Python (core reste Qt-free),
    déclenché dans `set_modified(True)` ; MainWindow le traduit en signal Qt
    `map_modified` et ne régénère l'aperçu que si l'onglet Export est actif
    (la régénération à la bascule sur l'onglet reste le filet de sécurité) ;
  - `core/services/export_service.py` : `build_reading_text(narrative_map, journey,
    agents)` (HTML 4 subset échappé : sommaire des parcours, déroulé centré états
    dans l'ordre RG069, états uniques, prédécesseurs + agents annotés du parcours,
    événements pendants en fin avec marqueur, section agents — restreinte au
    parcours filtré si filtre actif — et section orphelins) + `build_note_index`
    (ancres `#note-<kind>-<id>`) ;
  - `ui/views/export_workspace.py` : `ExportWorkspace(QTextBrowser)` readOnly,
    `setOpenLinks(False)` (liens inertes), infobulle note via `anchorAt` +
    `QToolTip.showText` ; ne touche jamais à `set_modified` ;
  - `main_window.py` : `TabBar(["Events", "Agents", "Export"])`, `export_page` dans
    le `QStackedWidget`, branche « Export » dans `_on_tab_changed` (régénération à
    la bascule), `_refresh_export_preview` (filtre FN029 : parcours actif si filtre
    on, tous les parcours sinon), hook filtre dans `_set_journey_filter_active`,
    stubs menu View `view_agents`/`view_export` (édition active en onglet Export).
    Les 6 `currentTab() == "Agents"` (lignes 524, 1015, 1213, 1234, 1267, 1292)
    restent corrects tels quels : comparaison explicite « Agents », le 3e onglet
    hérite du comportement « Events » (édition active) — vérifié un par un ;
  - tests : `tests/test_journeys/test_export_service.py` (+9 : ordre RG069, états
    uniques, sommaire filtré/non filtré, associations restreintes au parcours filtré,
    pendants avec marqueur, orphelins, échappement HTML, index de notes, arc partagé
    annoté multi-parcours).
  - vérifications : py_compile OK ; `pytest tests/ -q --ignore=tests/test_application`
    → 226 passed. **Bloquant sandbox** : libGL absent (pas de sudo) → le script
    offscreen UI (`/tmp/offscreen_tsk33_export_preview.py`, non committé) n'a pas pu
    tourner ici ; à valider en GUI avec les tests interactifs TSC (même situation
    que TSK29).
- 01-11-2026 (retours tests interactifs TSC) : deux correctifs —
  1. **fond blanc** : `APP_STYLESHEET` force le texte blanc sur tout QWidget, et le
     QTextBrowser gardait son fond blanc par défaut → texte invisible. Corrigé :
     stylesheet explicite fond `BG_PRIMARY` + texte `TEXT_PRIMARY` + liens
     `link_color` (nouvelle clé config.json, fallback `#E5C07B`), comme les vues
     Events/Agents ;
  2. **liens du sommaire** : `setOpenLinks(False)` bloquait aussi le scroll interne.
     Corrigé : `anchorClicked` → `scrollToAnchor` pour les ancres internes
     `#journey-*`/`#agent-*` (navigation passive, RG041) ; les liens restent inertes
     pour l'état de l'app (décision TSK31 maintenue — aucun clic ne modifie le
     filtre ni ne régénère) ; les ancres `#note-*` restent des infobulles au survol.
     FN033 FR/EN précisée en ce sens. Vérifications : config.json valide, py_compile
     OK, pytest 226 passed.
