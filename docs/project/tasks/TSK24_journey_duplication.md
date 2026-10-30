# TSK24 — Duplication d'un parcours (EPC05)

- **Épic** : EPC05 — Gérer un parcours narratif (SU005)
- **Statut** : En revue
- **Date de création** : 30-10-2026
- **Dépendances** : #TSK22 (Done, validée TSC 29-10-2026)
- **Conception** : `docs/conception/journey_attachment.md`
- **Specs** : FN025 (révisée 30-10-2026 : ce sont les relations/nœuds qui sont copiés, la copie n'est pas activée), RG023 révisée (la duplication ne modifie pas le parcours activé), RG020 (nouvel id), RG021 (libellé non unique), RG055 (`default=False` sur la copie), SU005 critère duplication

## Périmètre

1. **Use case** `DuplicateJourneyUseCase` (`src/usecases/journey_management/duplicate_journey_usecase.py`, pattern de `CreateJourneyUseCase`) : nouvel id via `narrative_map.get_next_id('journey')`, libellé distinctif, note, `default=False`, copie de tous les `Journey_node` du parcours source vers la copie (nouveaux ids via `get_next_id('journey_node')`, mêmes `state_to_event_id` / `event_to_state_id` / `state_agent_rel_id`, même `sequence_order`), arcs et associations eux-mêmes non dupliqués, `active_journey_id` inchangé (RG023 révisée), `set_modified(True)`.
2. **UI** (`main_window.py`) : entrée `Project › Journeys... › Duplicate...` → `JourneySelectionDialog` (sélection de la source, via `_select_journey`) → `JourneyDialog` pré-rempli (libellé proposé + note copiée) → use case → rafraîchissement de `JourneyList` + info_bar. Active dès qu'un projet est ouvert (≥ 1 parcours).
3. **Specs** : `05_menu-EN.yaml` (nouvelle entrée + note TSK24) ; `03_features-FR/EN.md` FN025 état → « Implémenté (TSK24) ».
4. **Tests** : unitaires `tests/test_journeys/test_journey_duplication.py` + script offscreen `tests/test_journeys/offscreen_tsk24_journey_duplicate.py` (à valider en séance GUI).

## Plan d'implémentation

1. **Use case** `duplicate_journey_usecase.py` + export dans `journey_management/__init__.py` :
   - `execute(source_journey, lb=None, note=None, narrative_map=None) -> Optional[Dict]` ; retour `{'success', 'entity', 'entity_id'}` comme `CreateJourneyUseCase` ; `None` si pas de projet.
   - `entity_id = narrative_map.get_next_id('journey')` ; `lb` par défaut `f"{source.lb} (copy)"` si non fournie/vide ; `note` copiée de la source si non fournie ; `default=False` (RG055).
   - Copie des nœuds : pour chaque `Journey_node` de `journey_id == source.id`, créer `Journey_node(id=get_next_id('journey_node'), journey_id=entity_id, sequence_order=n.sequence_order, event_to_state_id=n.event_to_state_id, state_to_event_id=n.state_to_event_id, state_agent_rel_id=n.state_agent_rel_id)`.
   - `active_journey_id` non modifié (RG023 révisée 30-10-2026) ; `set_modified(True)` ; logging.
2. **Tests unitaires** `tests/test_journeys/test_journey_duplication.py` (pattern `test_journey_foundations.py`, RG023/RG020/RG021/RG055/FN025 en docstring) :
   - nouvel id, libellé distinct par défaut, note copiée, `default=False` ;
   - nœuds copiés : nouveaux ids, mêmes références d'arcs (state_to_event / event_to_state) et d'association (`state_agent_rel_id`), `sequence_order` conservé ; arcs/associations non dupliqués (compteurs inchangés) ;
   - `active_journey_id` inchangé ; `set_modified(True)` ;
   - cas limites : parcours source sans nœud, lb fournie explicite, pas de projet → `None`.
3. **UI** `main_window.py` :
   - `self.duplicate_journey_usecase = DuplicateJourneyUseCase(self.project_service)` (à côté des autres, ~ligne 107-110).
   - Menu : `self.menu_actions['journey_duplicate'] = self.journeys_menu.addAction("Duplicate...", lambda: self._duplicate_journey())` entre New... et Edit (ligne ~409-410) ; activé avec `journeys_menu` (`setEnabled(has_project)`, ligne ~454) — ≥ 1 parcours garanti à l'ouverture d'un projet (RG022).
   - Handler `_duplicate_journey()` : `source = self._select_journey()` → si None, retour ; `JourneyDialog(parent=self, default_label=f"{source.lb} (copy)", default_note=source.note)` (ajout d'un paramètre optionnel `default_note` au dialogue, pré-remplissage de la note quand `entity is None`) → si Accepted, `self.duplicate_journey_usecase.execute(source, lb=values['lb'], note=values['note'])` → info_bar « Journey duplicated: {lb} » + `self._update_menu_state()` (rebuild de la JourneyList au prochain aboutToShow).
4. **Specs** : `05_menu-EN.yaml` entrée `Duplicate...` sous `Journeys...` (note « Implemented (TSK24) - Opens a journey selection dialog, then a pre-filled dialog (label '{lb} (copy)', note copied); the copy is not activated (RG023). Enabled as soon as a project is open ») ; `03_features-FR.md` / `-EN.md` FN025 `État`/`Status` → « Implémenté (TSK24) — menu Project › Journeys... › Duplicate... (sélection + dialogue pré-rempli) ; la copie n'est pas activée (RG023) ».
5. **Test offscreen** `tests/test_journeys/offscreen_tsk24_journey_duplicate.py` (pattern `offscreen_tsk23_journey_menu.py`) : ouverture projet → Project › Journeys... › Duplicate... → sélection source → dialogue pré-rempli (label « J1 (copy) », note copiée) → validation → assertions modèle (2 parcours, nœuds copiés, active inchangé, modified) + rebuild JourneyList. Non exécutable dans le sandbox (libGL) — à valider en séance GUI.
6. **Vérifications** (AGENTS.md) : `python -m py_compile` sur chaque fichier modifié ; `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` (complet) ; relecture du diff.

## Décisions actées (30-10-2026)

- **Nom distinctif par défaut** : `f"{source.lb} (copy)"` — traçable et distinct (FN025) ; RG021 autorise les doublons mais FN025 exige un nom distinct ; éditable dans le dialogue avant validation.
- **Note copiée** de la source (la copie est un clone complet hors id/rattachement actif).
- **Copie non activée** : RG023 révisée cette séance (« La duplication d'un parcours (FN025) crée un nouveau parcours sans modifier le parcours activé »).
- **`default=False`** sur la copie (RG055 : un seul parcours par défaut).
- **Copie des nœuds, pas des relations** : les arcs et associations référencés ne sont pas dupliqués (conception `journey_attachment.md` §2.4).

## Hors périmètre

- TSK25 (suppression), FN029 (filtre d'affichage), réordonnancement du `sequence_order`, barre latérale des parcours, activation de la copie.

## Journal

- 30-10-2026 : passage en Doing (kanban v13). Specs préparatoires appliquées la même séance : RG023/RG024/RG025/RG029/RG031/RG034 révisées, RG028/RG030 supprimées, SU005 + FN025/FN027/FN029 alignées sur la conception (rattachement des relations, appartenance dérivée) — 141 tests passed. Plan d'implémentation établi (ci-dessus), en attente de réalisation.
- 30-10-2026 : implémentation réalisée.
  - Use case `duplicate_journey_usecase.py` (`DuplicateJourneyUseCase`) + export `__init__.py` : nouvel id (`get_next_id('journey')`), lb par défaut `f"{source.lb} (copy)"`, note héritée (None) / explicite / vidée ('') , `default=False` (RG055), copie des `Journey_node` du source (nouveaux ids, mêmes refs arcs/association, même `sequence_order`), `active_journey_id` inchangé (RG023 révisée), `set_modified(True)`.
  - Tests `tests/test_journeys/test_journey_duplication.py` : +13 tests (basics RG020/RG021/RG055, copie des nœuds FN025, relations non dupliquées, RG023 révisée, modified, cas limites) — suite complète **154 passed, 3 skipped**.
  - UI : `main_window.py` — entrée `Project › Journeys... › Duplicate...` (entre New... et Edit, activée si ≥ 1 parcours), handler `_duplicate_journey` (sélection → `JourneyDialog` pré-rempli titre « Duplicate Journey » → use case → info_bar + `_update_menu_state`) ; `journey_dialog.py` — paramètre `default_note` (pré-remplissage de la note en mode création/duplication).
  - Specs : `05_menu-EN.yaml` (entrée Duplicate... documentée, YAML valide) ; `03_features-FR/EN.md` FN025 → « Implémenté (TSK24) ».
  - Offscreen `tests/test_journeys/offscreen_tsk24_journey_duplicate.py` : **PASSED** (exécuté dans le sandbox) — menu présent/activé, dialogue pré-rempli, copie (id, lb, default, active inchangé, modified), nœuds copiés, relations non dupliquées, JourneyList à 3 items.
  - `py_compile` OK sur tous les fichiers modifiés. Kanban v14 : TSK24 passée en En revue.
