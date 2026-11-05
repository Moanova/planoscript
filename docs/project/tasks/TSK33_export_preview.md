# TSK33 — Implémentation de l'aperçu d'export (SU010/FN033)

- **Épic** : SU007/SU010 (export de carte et aperçu d'export)
- **Statut** : To do (créée 01-11-2026, décision TSC)
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
