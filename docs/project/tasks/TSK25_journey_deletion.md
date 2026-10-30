# TSK25 — Suppression d'un parcours (EPC05)

- **Épic** : EPC05 — Gérer un parcours narratif (SU005)
- **Statut** : En revue
- **Date de création** : 30-10-2026
- **Dépendances** : #TSK22 (Done), #TSK24 (Done, validée TSC 30-10-2026)
- **Conception** : `docs/conception/journey_attachment.md`
- **Specs** : FN027 (révisée 30-10-2026), RG018 (dernier parcours non supprimable), RG015, RG029 (parcours par défaut existe toujours), RG036 (les nœuds du parcours supprimé sont traités : supprimés si la relation reste rattachée ailleurs, basculés vers le défaut sinon), RG055 (default unique ; si supprimé → plus ancien restant), RG026 (relation = 1..n parcours), RG066 (association jamais orpheline → bascule vers le défaut), SU005

## Périmètre

1. **Use case** `DeleteJourneyUseCase` (`src/usecases/journey_management/delete_journey_usecase.py`, pattern de `DuplicateJourneyUseCase`) : refus si dernier parcours (RG018), traitement des `Journey_node` du parcours supprimé (RG036 + RG066 + RG026), réattribution du default (RG055) et de l'actif (FN027), `set_modified(True)`.
2. **UI** (`main_window.py`) : remplacer le stub Delete du bouton de la fenêtre de sélection ouverte par `Project › Journeys... › Edit` par une confirmation `QMessageBox.question` (pattern `_delete_agent_with_confirmation`) + message explicatif si dernier parcours, puis exécution du use case et retour à la sélection (boucle existante de `_edit_journey`).
3. **Specs** : `05_menu-EN.yaml` (note Edit : Delete implémenté TSK25) ; `03_features-FR/EN.md` FN027 état → « Implémenté (TSK25) ».
4. **Tests** : unitaires `tests/test_journeys/test_journey_deletion.py` + script offscreen `tests/test_journeys/offscreen_tsk25_journey_delete.py` (dialogues/confirmation mockés).

## Plan d'implémentation

1. **Use case** `delete_journey_usecase.py` + export dans `journey_management/__init__.py` :
   - `execute(journey, narrative_map=None) -> Optional[Dict]` ; `None` si pas de projet ou source invalide ; `{'success': False, 'reason': 'last_journey'}` si `len(narrative_map.journey) <= 1` (RG018/RG015) — rien n'est modifié dans ce cas.
   - Default courant : le parcours avec `default=True` (unique, RG055) ; s'il est supprimé, le plus ancien restant (`min(id)`) devient `default=True` (RG055).
   - Traitement des nœuds (RG036/RG066/RG026) : pour chaque `Journey_node` de `journey_id == supprimé.id`, regarder si la relation référencée (`state_to_event_id` / `event_to_state_id` / `state_agent_rel_id`) possède encore un nœud dans un autre parcours restant :
     - oui → supprimer le nœud (RG036) ;
     - non → basculer le nœud vers le default : `node.journey_id = default.id` (sa relation reste à 1..n parcours, RG026 ; obligatoire pour les associations, RG066). Le `sequence_order` est conservé tel quel (sémantique à affiner plus tard, conception §5).
   - Retirer le parcours de `narrative_map.journey`.
   - Si `active_journey_id == supprimé.id` → `active_journey_id = default.id` (FN027 révisée 30-10-2026).
   - `set_modified(True)` ; retour `{'success': True, 'entity_id', 'removed_nodes': [...], 'switched_nodes': [...], 'new_default': ...}` ; logging.
2. **Tests unitaires** `tests/test_journeys/test_journey_deletion.py` (pattern `test_journey_duplication.py`) :
   - dernier parcours → `success False / reason 'last_journey'`, modèle inchangé (RG018) ;
   - relation partagée entre 2 parcours → nœud du supprimé retiré, nœud de l'autre parcours conservé, relation intacte (RG036) ;
   - arc orphelin après suppression → nœud basculé vers le default (`journey_id` changé, relation toujours rattachée, RG026) ;
   - association orpheline → basculée vers le default via `state_agent_rel_id` (RG066) ;
   - default supprimé → plus ancien restant (`min id`) devient `default=True`, unicité conservée (RG055) ;
   - actif supprimé → `active_journey_id` = nouveau default (FN027) ;
   - composants et relations jamais supprimés par la suppression d'un parcours ;
   - `set_modified(True)` ; cas limites : pas de projet → `None`, journey étrangère → `None`.
3. **UI** `main_window.py` :
   - `self.delete_journey_usecase = DeleteJourneyUseCase(self.project_service)` (à côté des autres use cases journeys).
   - Dans `_edit_journey`, remplacer le stub `elif action == "delete":` : récupérer `dialog.get_selected_journey()` ; si dernier parcours (`len(nm.journey) <= 1`) → `info_bar.show_message(...)` explicatif (RG018) ; sinon `QMessageBox.question(self, "Delete Journey", f"Delete journey '{journey.lb}'? ...", Yes|No)` (pattern `_delete_agent_with_confirmation`) → si Yes, `self.delete_journey_usecase.execute(journey)` → info_bar « Journey deleted: {lb} » ; la boucle existante recrée une instance fraîche de `JourneySelectionDialog` (liste à jour) et revient à la sélection (décision TSK23).
   - `_update_menu_state()` en sortie (déjà appelé).
4. **Specs** : `05_menu-EN.yaml` — note de `Edit` : « Delete implemented (TSK25) - confirmation, last journey refused (RG018) » ; `03_features-FR.md` / `-EN.md` FN027 `État`/`Status` → « Implémenté (TSK25) — bouton Delete de la fenêtre de sélection `Project › Journeys... › Edit` (confirmation ; dernier parcours refusé avec message, RG018) ».
5. **Test offscreen** `tests/test_journeys/offscreen_tsk25_journey_delete.py` (pattern `offscreen_tsk24_journey_duplicate.py`) : projet + 2 parcours + arcs répartis ; mocker `JourneySelectionDialog.exec` (1re itération Accepted avec action « delete », puis Rejected pour sortir de la boucle) et `QMessageBox.question` → `QMessageBox.Yes` ; appeler `mw._edit_journey()` ; assertions modèle (parcours supprimé, nœuds basculés/supprimés, default/actif, modified) + rebuild JourneyList. Exécutable dans le sandbox (offscreen TSK24 a passé).
6. **Vérifications** (AGENTS.md) : `py_compile` des fichiers modifiés ; `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` complet ; offscreen ; relecture du diff ; kanban + journal.

## Décisions actées (30-10-2026)

- **Point d'entrée de la suppression** : entrée dédiée `Project › Journeys... › Delete...` + fenêtre de sélection Ok/Cancel + confirmation (décision **révisée le 30-10-2026 en revue UX** : la version initiale prévoyait le bouton Delete de la fenêtre de sélection Edit — abandonnée car peu satisfaisante ; le bouton Delete a donc été retiré de `JourneySelectionDialog`, et `_edit_journey` est redevenu un flux linéaire Ok → édition).
- **Nœuds orphelins basculés vers le parcours par défaut** (pas de fenêtre de réattribution manuelle) : RG036 pour les nœuds dont la relation reste ailleurs, RG066/RG026 pour les orphelins — `sequence_order` conservé tel quel en attendant l'affinage de la sémantique (conception §5).
- **Default supprimé** → plus ancien restant (`min(id)` = ordre de création, RG055) ; **actif supprimé** → le (nouveau) default devient actif (FN027 révisée).
- **Confirmation** par `QMessageBox.question` Yes/No (pattern suppression agent) ; **dernier parcours** → refus avec message explicatif (RG018), aucune confirmation demandée.

## Hors périmètre

- FN029 (filtre d'affichage), renumérotation du `sequence_order` après bascule, TSK26 (vocabulaire), barre latérale des parcours.

## Journal

- 30-10-2026 : passage en Doing (kanban v15) après validation TSC de TSK24. Plan d'implémentation établi (ci-dessus), en attente de réalisation.
- 30-10-2026 : implémentation réalisée (6 étapes du plan).
  - Use case `delete_journey_usecase.py` (`DeleteJourneyUseCase`) + export `__init__.py` : refus `{'success': False, 'reason': 'last_journey'}` si dernier parcours (RG018), nœuds du parcours supprimé retirés si la relation reste rattachée ailleurs (RG036) ou basculés vers le parcours par défaut sinon (RG066/RG026, incl. `state_agent_rel_id`), default supprimé → plus ancien restant (RG055), actif supprimé → default activé (FN027 révisée), `set_modified(True)` ; composants/relations jamais supprimés.
  - Tests `tests/test_journeys/test_journey_deletion.py` : +11 tests — suite complète **165 passed, 3 skipped**.
  - UI `main_window.py` : import + instanciation `delete_journey_usecase`, stub Delete de `_edit_journey` remplacé par `_delete_journey_with_confirmation` (dernier parcours → message explicatif RG018 sans confirmation ; sinon `QMessageBox.question` Yes/No pattern agent → use case → info_bar → retour à la sélection via la boucle existante).
  - Specs : `05_menu-EN.yaml` (note Edit : Delete implémenté TSK25, YAML valide) ; `03_features-FR/EN.md` FN027 → « Implémenté (TSK25) ».
  - Offscreen `tests/test_journeys/offscreen_tsk25_journey_delete.py` : **PASSED** (exécuté dans le sandbox) — flux Edit→Delete→confirmation mockée, nœud orphelin basculé, actif réactivé sur le default, refus du dernier parcours sans confirmation, JourneyList à 1 item.
  - `py_compile` OK sur tous les fichiers modifiés. Kanban v16 : TSK25 passée en En revue.
- 30-10-2026 (revue UX) : évolution du point d'entrée de la suppression — entrée dédiée `Project › Journeys... › Delete...` (sélection Ok/Cancel + confirmation), bouton Delete retiré de la fenêtre de sélection Edit (`JourneySelectionDialog` allégé, `_edit_journey` simplifié en flux linéaire, `_delete_journey` = sélection + confirmation + use case). Specs mises à jour (`05_menu-EN.yaml` entrée Delete..., note Edit corrigée ; FN027 FR/EN). Offscreen TSK23 corrigé (plus de `delete_button`/`get_action`), offscreen TSK25 réécrit pour le nouveau flux — **TSK23/TSK24/TSK25 offscreen PASSED**, pytest **165 passed, 3 skipped**, `py_compile` OK, YAML valide.
