# TSK19 — Renommage de la vue « Journey » en vue « Events »

- **Épic** : Cohérence de conception (nommage) — hors epic existante
- **Statut** : En revue (implémentation + tests faits — attente validation TSC)
- **Date de début** : 29-10-2026
- **Dépendances** : aucune

## Motivation (décision TSC 29-10-2026)

La vue « Journey » affiche le graphe états + événements reliés par des
arcs ; les états sont les objets centraux des cartes narratives, communs
aux deux vues. Nommer la vue « Events » est plus fidèle à son contenu et
cohérent avec la vue « Agents » (nommée d'après les agents). Cela sépare
aussi deux vocabulaires aujourd'hui confondus : la **vue** (UI) et le
**parcours narratif** (métier, entité `Journey`).

## Périmètre

**Renommer (couche UI uniquement)** : tout objet nommé d'après la vue.

**Conserver tel quel (couche métier)** : `class Journey`,
`class Journey_node`, les champs `narrative_map.journey` /
`journey_node` et leurs **clés JSON** `'journey'` / `'journey_node'`
(persistées dans les sauvegardes — aucun impact sur les fichiers
projet existants), RG022 et `create_project_usecase.py`
(`Journey(lb="Journey 1", default=True)`), l'enum commentée
`view_model.py:42`.

## Plan d'implémentation

### 1. Code source (`src/`)

1. `git mv src/ui/views/journey_workspace.py src/ui/views/events_workspace.py`
   ; `class JourneyWorkspace` → `class EventsWorkspace` (ligne 42) ;
   docstring du module.
2. `src/ui/views/__init__.py` : import / `__all__`.
3. `src/ui/main_window.py` (~37 occurrences de « journey") :
   - import : `from ui.views.events_workspace import EventsWorkspace`
   - `self.journey_page` → `self.events_page` (9 réf.), variable locale
     `journey_layout` → `events_layout`
   - onglet : `TabBar(["Events", "Agents"])` et tous les littéraux
     `"Journey"` → `"Events"` (`setCurrentTab` ×4, `forceCurrentTab`,
     `tab_name == "Journey"`, `currentTab() == "Journey"`)
   - menus : `self.journey_menu` → `self.events_menu`,
     `display_menu.addMenu("Events")`, stubs conservés mais renommés :
     `menu_actions['list_events'] = ... addAction("EventsList", lambda: None)`,
     `menu_actions['view_events'] = view_menu.addAction("Events", lambda: None)`
     (AGENTS.md : conserver les entrées stubbées)
   - méthodes : `_focus_state_in_journey_view` → `_focus_state_in_events_view`,
     `_focus_agent_in_journey_view` → `_focus_agent_in_events_view`
   - 20 × `isinstance(self.workspace, JourneyWorkspace)` → `EventsWorkspace`
4. `src/ui/views/agents_workspace.py` : signaux
   `focusAgentInJourneyViewRequested` → `focusAgentInEventsViewRequested`,
   `focusStateInJourneyViewRequested` → `focusStateInEventsViewRequested`
   (déclarations lignes 131/135, émissions 640/671, connexions
   `main_window.py:147/150`) ; commentaires « journey workspace/view ».
5. Commentaires/docstrings « journey view/workspace » dans
   `matrix_card.py`, `base_node.py`, `create_node_usecase.py`,
   `create_relation_usecase.py`, `event_badge_service.py` → « events view ».

### 2. Tests (`tests/test_agents/`)

- `offscreen_workspace_tabs.py` (5 réf.) : import, `currentTab() == "Events"`,
  `mw.events_page`
- `offscreen_tsk13_agent_mechanics.py` (8 réf.) : import, `jw_module`,
  `"Events"`, `_focus_*_in_events_view`
- `offscreen_tsk12_layout_finalization.py` (3 réf.) : import `EventsWorkspace`
- `offscreen_cross_view_navigation.py` : `mw.events_page`,
  `mw._focus_agent_in_events_view(...)`
- Lancer les 10 scripts offscreen + `pytest tests/ -q` (106 tests).

### 3. Documentation

- `AGENTS.md` : « vue Parcours (Journey) » → « vue Events » ;
  `JourneyWorkspace.viewportEvent` / `JourneyWorkspace.show_context_menu`
  → `EventsWorkspace...`
- `docs/specification/04_interface-FR.md` (12 « vue parcours ») et
  `04_interface-EN.md` : renommer la vue (garder « parcours » quand il
  s'agit de l'entité Journey / SU005)
- `98_layout_revision-FR.md` (2 réf.), `01_user_stories` FR/EN,
  `03_features` FR/EN, `99_mvp_scope` FR/EN, `02_business_rules` FR/EN
  : « vue Journey/parcours » → « vue Events » selon le sens
- `README.md` : « Journey view » → « Events view » (lignes 15-16, 57)
- Kanban (cette tâche), `SESSIONS.md`.

### 4. Hors périmètre (à noter, pas à changer)

- Icônes `src/ui/asset/icon/journey.svg`, `addJourney.svg`,
  `delJourney.svg` : non référencées dans le code Python (vérifié) —
  renommage facultatif, hors périmètre code.
- Toute la couche métier `Journey` (voir Périmètre).

## Vérifications

1. `python -m py_compile` sur chaque fichier modifié.
2. `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` (106 passed,
   hors `test_application` pywinauto).
3. Les 10 scripts `tests/test_agents/offscreen_*.py` PASSED.
4. `grep -ri "journey" src/ tests/` : ne doit rester que la couche métier
   (`data_model.py`, `create_project_usecase.py`, `view_model.py` commenté)
   et éventuellement les icônes.

## Journal

- 29-10-2026 : création de la tâche (demande TSC 29-10-2026) — plan
  d'implémentation établi après analyse d'impact (TSK19 = renommage
  couche UI ; couche métier `Journey` conservée).
- 29-10-2026 : implémentation — `git mv journey_workspace.py →
  events_workspace.py`, `JourneyWorkspace` → `EventsWorkspace`,
  `main_window.py` (events_page, events_menu, onglet « Events », stubs
  `list_events`/`EventsList` et `view_events`/`Events`, méthodes
  `_focus_*_in_events_view`, 20 isinstance), signaux
  `focus*InEventsViewRequested` dans `agents_workspace.py`, commentaires
  des 7 fichiers restants, 5 scripts offscreen de test mis à jour, doc
  (AGENTS.md, README, 04_interface FR/EN, 01/02/03/98/99 specs FR/EN,
  kanban TSK16/TSK18). Couche métier `Journey`/`Journey_node` + clés
  JSON inchangées (grep final : « journey » restant = data_model,
  create_project_usecase, view_model commenté, test_journeys, fiches
  historiques). Vérifications : py_compile OK, pytest 106 passed,
  10 offscreen PASSED. Kanban : Doing → En revue.
