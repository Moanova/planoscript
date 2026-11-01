# TSK29 — Implémentation du filtre d'affichage par parcours (FN029, RG042, SU006)

- **Épic** : EPC05 (SU005/SU006, gestion des parcours) — tâche d'implémentation
- **Statut** : En revue (01-11-2026)
- **Date de création** : 01-11-2026
- **Dépendances** : → #TSK27 (Done, conception validée TSC 31-10-2026)
- **Conception** : `docs/conception/journey_filter.md` (validée TSC 31-10-2026, amendée 01-11-2026 : filtre **désactivé par défaut** à l'ouverture d'un projet)

## Objectif

Implémenter le filtre d'affichage par parcours (FN029/RG042) selon la conception TSK27 :

1. **Sémantique de visibilité** (RG026, dérivée du modèle, jamais stockée) :
   - filtre actif (parcours J actif) : visibles = relations (arcs + associations) ayant un `Journey_node` dans J, et composants auxquels elles donnent appartenance ; masqués = relations des autres parcours, composants n'appartenant qu'à d'autres parcours, composants orphelins ;
   - filtre désactivé (« All journeys ») : tout est visible, y compris les orphelins.
2. **État du filtre** : `journey_filter_active: bool`, **désactivé par défaut** à l'ouverture d'un projet (décision TSC 01-11-2026 : en début de construction, l'appartenance des composants aux parcours n'est pas encore claire — il faut pouvoir tout voir) ; **non persisté** (RG041, état de visualisation en mémoire uniquement : ni `WorkspaceLayout`, ni `user_state.json`, ni sauvegarde projet).
3. **Point d'entrée UI** : entrée cochable « All journeys » en tête de `Display > Journey > JourneyList` (cochée = filtre désactivé) ; cocher un parcours = activer ce parcours **et** le filtre.
4. **Vue Events** : `EventsWorkspace.apply_journey_filter()` — `setVisible()` sur les `BaseNode`/`Connection`, recalculé après activation de parcours, bascule du filtre, création/suppression de relation, attach/detach (RG027), suppression de composant, chargement de projet.
5. **Vue Agents** (décision TSC 31-10-2026) : filtrée comme la vue Events — colonnes des états du parcours actif et cases rattachées à ce parcours ; les lignes (agents, niveau projet) restent toutes visibles.
6. **Édition sous filtre** : création d'un composant orphelin → message dans la barre d'info (pas de bascule auto) ; création d'une relation → visible instantanément (rattachement auto parcours actif, RG052) ; suppression → recalcul ; navigation croisée RG067 → bascule « All journeys » d'abord si la cible est masquée.

## Livrables

- `src/core/services/journey_filter_service.py` : visibilité dérivée (RG026/FN029).
- `EventsWorkspace` : `journey_filter_active` + `apply_journey_filter()` + appels aux points de rafraîchissement.
- `AgentsWorkspace` : `apply_journey_filter()` (colonnes états / cases associations).
- `MainWindow` : entrée « All journeys » dans JourneyList, `_set_journey_filter_active()`, recalcul à l'activation d'un parcours, comportements d'édition sous filtre, RG067.
- `config.json` : libellé de l'entrée « All journeys » (`journey_list_all_label`).
- Specs : FN029 « Implémenté » (FR/EN), `05_menu-EN.yaml`, `04_interface` FR/EN.
- Tests : `tests/test_visualization/test_journey_filter.py` (visibilité dérivée, orphelins, bascule, non-persistance) + script offscreen jetable.

## Hors périmètre (acté)

- Filtrage multi-parcours, cohérence narrative (SU005), barre latérale de filtre (note §5bis de la conception — tâche ultérieure).

## Journal

- 01-11-2026 : tâche créée et passée en Doing (dépendance TSK27 Done). Décision TSC 01-11-2026 : filtre désactivé par défaut à l'ouverture (construction facilitée), état toujours non rémanent.
- 01-11-2026 : implémentation complète — `JourneyFilterService` (visibilité dérivée), `EventsWorkspace.journey_filter_active` + `apply_journey_filter()` (création nœud/connexion, suppression nœud/connexion, populate), `AgentsWorkspace.apply_journey_filter()` (colonnes états + cases), `MainWindow` (entrée « All journeys », `_set_journey_filter_active`, `_refresh_journey_filter` aux points de rafraîchissement, reset filtre off à l'ouverture, RG067 bascule « All journeys » avant focus, message barre d'info composant orphelin sous filtre), config `journey_list_all_label`. Specs FN029 « Implémenté » FR/EN, 05_menu, 04_interface FR/EN.
- Vérifications : py_compile OK (6 fichiers) ; `pytest tests/ -q --ignore=tests/test_application` : **199 passed** (+9 nouveaux) ; script offscreen `tests/test_visualization/offscreen_tsk29_journey_filter.py` écrit, non exécutable dans le sandbox (libGL.so.1 absent, comme les séances précédentes) — à valider en séance GUI. Tâche passée en En revue (kanban v24).
- 01-11-2026 (retours TSC après test GUI) :
  - **Correctif script offscreen** (le bug était dans le test, pas l'app) : `actions[3]` indexait une liste d'actions périmée après le rebuild du menu → recherche des entrées par libellé via un helper `menu_action(label)` qui re-read le menu à chaque appel.
  - **Révision visualisation** : les éléments hors filtre ne sont plus masqués (`setVisible(False)`) mais **estompés** (opacité 0.25 + `setEnabled(False)`), comme le focus RG067 « Show in events view » — vue Events (nœuds/connexions) et vue Agents (cartes d'état/cases). Les nœuds d'état focalisés (RG067) gardent la pleine opacité même sous filtre actif (priorité focus > filtre dans `_apply_item_opacity`) ; la bascule auto « All journeys » avant focus est retirée (inutile avec l'estompage). Éléments estompés non cliquables (ports, menus contextuels, cartes/cases matrice). Conception §2/§5/§6 et specs FN029/04_interface mises à jour. py_compile OK ; pytest 199 passed ; script offscreen mis à jour (vérifie opacité/enabled au lieu de visibilité).
