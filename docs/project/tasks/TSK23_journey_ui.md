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

## Retours de revue TSC (29-10-2026) — traités

- Entrée `Project > Journeys... > Delete` **supprimée** du menu (un parcours
  n'est pas un objet sélectionnable dans l'espace de travail).
- La fenêtre de sélection ouverte par `Edit` gagne les boutons **New...**
  (crée un parcours puis revient sur la sélection au lieu de revenir à
  l'espace de travail) et **Delete** (stub jusqu'à TSK25, message
  info_bar).
- `_edit_journey` réécrit en boucle sur la sélection (actions ok/new/delete) ;
  `_new_journey_dialog()` mutualisé entre le menu New... et le bouton New...
  de la sélection. Specs `05_menu-EN.yaml` et script offscreen mis à jour.
- Tests : py_compile OK ; 127 passed.

## Retours de revue TSC (29-10-2026, 2e salve) — traités

- **Sélection permanente** : la fenêtre de sélection sélectionne toujours un
  parcours (ligne 0 à l'ouverture ; `refresh(..., select_id=...)` sélectionne
  le parcours nouvellement créé après un New...). Ok/Delete ne sont donc
  plus jamais grisés.
- **Logique transactionnelle** : la session Edit est un snapshot
  (journeys + active_journey_id) ; si elle se termine par **Cancel**, les
  parcours créés via New... pendant la session sont retirés du modèle et le
  parcours actif précédent est restauré (la création via le menu New... reste,
  elle, définitive et revient à l'espace de travail).
- Tests : py_compile OK ; 127 passed ; script offscreen mis à jour.

## Retour de test TSC (29-10-2026, 3e salve) — corrigé

- Bug : boucle infinie de fenêtres de création depuis Edit (les `continue`
  de la boucle sautaient le ré-`exec()` de la sélection). Corrigé : plus aucun
  `continue` dans la boucle, chaque action retombe sur `result = dialog.exec()` ;
  seul Ok termine la session (break).
- Tests : py_compile OK ; 127 passed.

## Retour de test TSC (29-10-2026, 4e salve) — corrigé

- Bug : après New... depuis Edit puis Ok sur la sélection, une fenêtre de
  création se rouvrait (double création). Cause : la même instance de
  `JourneySelectionDialog` était ré-ouverte en boucle et conservait un
  `_action` périmé entre deux `exec()`. Corrigé : **nouvelle instance du
  dialogue à chaque itération**, `select_id` passé au constructeur (plus de
  `refresh()` ni d'état réutilisé) ; `_action` repart donc vide à chaque fois.
- Tests : py_compile OK ; 127 passed ; offscreen mis à jour (select_id au
  constructeur, action vide sur instance fraîche).

## Retour de test TSC (29-10-2026, 5e salve) — traité

- Bouton **New... supprimé** de la fenêtre de sélection (Edit) : la création se
  fait uniquement par `Project > Journeys... > New...`. Conséquence : plus de
  création possible dans la session Edit, donc le rollback transactionnel
  (snapshot/annulation) est retiré de `_edit_journey`, simplifié en boucle
  Ok/Delete. `select_id`/`refresh()` retirés du dialogue.
- Note pour TSK25 : le bouton Delete de la sélection ouvrira une confirmation
  puis reviendra à la sélection (jamais la fenêtre d'édition, réservée à Ok).
- Tests : py_compile OK ; 127 passed ; offscreen + spec menu mis à jour.
