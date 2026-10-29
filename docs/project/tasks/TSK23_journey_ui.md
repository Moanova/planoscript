# TSK23 — UI de gestion des parcours (EPC05)

- **Épic** : EPC05 — Gérer un parcours narratif (SU005)
- **Statut** : Doing
- **Date de création** : 29-10-2026
- **Dépendances** : #TSK22 (fondations : use cases + `active_journey_id`)
- **Conception** : `docs/conception/journey_attachment.md`

## Périmètre

1. **Dialogues** (`src/ui/dialogs/`, thème charte 98, pattern AgentDialog/AgentSelectionDialog) :
   - `journey_dialog.py` — création/édition d'un parcours : `lb` + `note` (FN024), libellé par défaut « Journey {id} » éditable en création.
   - `journey_selection_dialog.py` — sélection d'un parcours (Edit), Ok désactivé sans sélection.
2. **Menus** (`main_window.py`) :
   - `Display › Events › EventsList` **remplacé** par `Display › Journey › JourneyList` : liste **dynamique cochable**, un item par parcours, coché = parcours actif ; clic → `ActivateJourneyUseCase` (FN026) ; reconstruite sur `aboutToShow`.
   - `Project › Journeys... › New... / Edit / Delete` : New... → dialogue + `CreateJourneyUseCase` (FN023, RG023) ; Edit → sélection + dialogue + `UpdateJourneyUseCase` (FN024) ; **Delete = stub** (`lambda: None`, note TSK25).
3. **État des menus** : `Journeys...` et `Display › Journey` actifs dès qu'un projet est ouvert ; Edit (et le stub Delete) actifs si ≥ 1 parcours.
4. **Specs** : `05_menu-EN.yaml` (remplacement Events→Journey, notes TSK23), `03_features` FR/EN (FN023/FN024/FN026 → « Implémenté (TSK23) »).
5. **Tests** : script offscreen `tests/test_journeys/offscreen_tsk23_journey_menu.py` (création, liste cochable, activation) ; py_compile + pytest (use cases déjà couverts, 127 tests).

## Hors périmètre

Suppression d'un parcours (TSK25), duplication (TSK24), filtre d'affichage FN029, barre latérale `journeys_toolbar.py` (non intégrée, inchangé).

## Journal (29-10-2026)

- Dialogues `journey_dialog.py` (lb + note, Note compacte 60 px par config, validation libellé non vide) et `journey_selection_dialog.py` (pattern AgentSelectionDialog).
- `main_window.py` : `Display › Events` remplacé par `Display › Journey › JourneyList` (dynamique, cochable, reconstruit sur `aboutToShow`, clic → activation FN026) ; `Project › Journeys... › New.../Edit/Delete` (Delete = stub TSK25) ; use cases câblés ; `_update_menu_state` gère l'activation ; handlers `_new_journey` / `_edit_journey` / `_select_journey` / `_rebuild_journey_list_menu` / `_activate_journey`.
- Specs : `05_menu-EN.yaml` (JourneyList + Journeys..., note remplacement Events) ; `03_features` FR/EN FN023/FN024/FN026 → Implémenté (TSK23).
- Tests : py_compile OK ; 127 passed (inchangé, use cases déjà couverts TSK22) ; script offscreen `tests/test_journeys/offscreen_tsk23_journey_menu.py` écrit mais non exécutable dans le sandbox (libGL.so.1) — à valider en séance GUI.
- Hors périmètre respecté : Delete stub, pas de filtre FN029, pas de barre latérale.
