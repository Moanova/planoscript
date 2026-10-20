# TSK04 — Dialogue « Associer des agents... » depuis le menu contextuel d'un état

- **Épic** : EPC02 — Associer des agents à un état (FN030, SU008)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK01 (Done), #TSK03 (Done)

## Périmètre

Premier point d'entrée UI des associations agent-état : depuis la vue
parcours, le menu contextuel d'un node d'état propose « Associate
agents... ». Le dialogue liste tous les agents du projet avec leur statut
d'association courant pour cet état (case cochée/décochée), et permet de
créer un nouvel agent puis de l'associer en une seule opération. Toute
modification est immédiatement appliquée aux données (use cases de TSK03)
et marquera le projet comme modifié. Selon le menu spécifié
(`05_menu-EN.yaml`), l'entrée existe aussi sous « Project > Relations... >
Associate agents with State » ; les deux entrées ouvrent le même dialogue
sur l'état sélectionné.

## Règles et critères applicables

- **SU008** : le dialogue liste l'ensemble des agents du projet avec leur
  état d'association courant (coché/décoché) pour cet état ; cocher
  associe, décocher dissocie ; création d'agent intégrée ; empêchement
  des doublons (RG063, garanti par le use case) ; toute
  association/dissociation/création marque le projet comme modifié.
- **FN030** : « Depuis la vue parcours, le menu contextuel d'un état
  ouvre un dialogue listant tous les agents du projet avec leur statut
  d'association courant pour cet état. Cocher associe, décocher
  dissocie. Le dialogue permet de créer un nouvel agent et de l'associer
  en une seule opération. »
- **RG066** : les associations sont indépendantes des parcours — aucun
  filtrage par parcours dans ce dialogue.

## État des lieux (existant mobilisable)

- Use cases prêts (TSK03) : `AssociateAgentStateUseCase` (RG063
  idempotente, retour `already_associated`),
  `DissociateAgentStateUseCase`, et `find_association` pour lire l'état
  courant.
- `CreateAgentUseCase` (TSK01) et `AgentDialog` pour la création
  d'agent intégrée.
- Menu contextuel des State nodes : `show_context_menu` dans
  `journey_workspace.py` (pattern `menu.exec()` + dispatch sur l'action
  retournée, sélection de l'item sous le curseur avant ouverture).
- L'entrée de menu « Associate agents with State » sous
  « Project > Relations... » n'existe pas encore dans `main_window.py`
  (le sous-menu Relations contient uniquement Connect/Edit/Delete) ;
  `05_menu-EN.yaml` la spécifie avec la note « Enabled only when a State
  node is selected » (à faire valider : entrée de menu vs menu
  contextuel uniquement).

## Plan d'implémentation

1. **`AgentAssociationDialog`** (`src/ui/dialogs/agent_association_dialog.py`)
   — sur le pattern des dialogues existants (modal, boutons en bas) :
   - Constructeur : `project_service`, l'état `State` ciblé, et les use
     cases (association/dissociation/création) injectés par MainWindow.
   - Liste à cocher (une ligne par agent du projet, triée par identifiant
     ou libellé — l'ordre des agents n'est pas spécifié, ordre de création
     par défaut) : `QListWidget` avec `QCheckBox` par agent, précochée si
     une association existe (`find_association`).
   - Interaction immédiate (pas de bouton OK) : le cochage/décochement
     applique immédiatement le use case correspondant ; un message de
     statut dans le dialogue (ou la barre d'infos) confirme l'action.
     Le dialogue se ferme avec « Close ». À trancher : application
     immédiate vs validation au bouton OK (SU008 penche pour
     l'immédiat : « cocher associe, décocher dissocie »).
   - Bouton « New agent... » : ouvre `AgentDialog` en mode création ;
     si validé, crée l'agent (`CreateAgentUseCase`) **et l'associe
     immédiatement** à l'état courant, puis rafraîchit la liste (le
     nouveau agent apparaît coché). Conforme FN030 : « créer un nouvel
     agent et de l'associer en une seule opération ».
2. **Menu contextuel** (`journey_workspace.py`, `show_context_menu`) :
   - Ajout de l'entrée « Associate agents... » dans la section StateNode,
     entre « Edit State » et « Delete State » (l'état initial peut être
     associé — rien dans les règles ne l'interdit, contrairement à la
     suppression RG031).
   - Handler : appel d'une méthode de MainWindow
     (`_associate_agents_to_state(entity)`) qui ouvre le dialogue sur
     l'entité de l'item sélectionné (pattern dispatch existant).
3. **Entrée de menu « Project > Relations... > Associate agents with
   State »** (`main_window.py`) :
   - Ajout de l'action dans le sous-menu Relations, active uniquement si
     un State node est sélectionné (pattern `_update_menu_state`, clé
     `menu_actions['associate_agents']` — même logique que
     `state_edit`).
   - Même handler que le menu contextuel, sur l'entité sélectionnée.
   - À valider : la spécification de menu (`05_menu-EN.yaml`) place
     l'entrée dans le sous-menu Relations avec la contrainte d'activation
     sur sélection d'état. Alternative : menu contextuel uniquement
     (SU008 ne mentionne que le contextuel, FN030 aussi). Recommandation
     : implémenter les deux (cohérent avec le pattern existant :
     Edit/Delete existent en double également), en gardant la même
     action.
4. **Câblage MainWindow** :
   - `_associate_agents_to_state(entity)` : vérifications minimales
     (projet ouvert, entité est un State), instanciation du dialogue
     avec les use cases, `exec()`, retour d'informations dans la barre
     d'infos si pertinent (ex. : nombre d'agents associés à l'état).
   - Après fermeture du dialogue : rafraîchissement des nodes d'état
     (les badges de TSK05 s'appuieront sur ce rafraîchissement ;
     en attendant, `update_entity_data()` sur le node si nécessaire —
     mais sans badges, rien à rafraîchir visuellement pour l'instant).
5. **Tests** (`tests/test_agents/test_agent_association_dialog.py`) :
   - Tests unitaires sur les use cases déjà couverts (TSK03) ; le dialogue
     étant de l'UI Qt, sa vérification relève du test offscreen (non
     exécutable dans la sandbox, libGL) et du test manuel de fin
     d'EPC03.
   - Un test de logique non-Qt peut couvrir la préparation de la liste
     (agents du projet + statut d'association courant) si elle est
     isolée dans une méthode testable sans QApplication (à évaluer ;
     sinon couvert par le offscreen local).

## Décisions à valider

- **Application immédiate vs bouton OK** dans le dialogue :
    recommandation = application immédiate au cochage/décochement
    (littérature SU008/FN030), fermeture par « Close ».
- **Double point d'entrée** (menu contextuel + sous-menu Relations) :
    recommandation = implémenter les deux, comme le spécifie
    `05_menu-EN.yaml` (cohérent avec le pattern Edit/Delete existant).
- L'état initial peut être associé à des agents (aucune règle ne
    l'interdit — seule sa suppression et la modification de son type sont
    régies, RG031/RG061).

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen du dialogue : rédigé mais non exécutable dans la
   sandbox (libGL) — à exécuter localement ; couvrira l'état initial des
   cases, le cochage/décochement (succès des use cases), la création
   d'agent intégrée (case cochée après création).
4. Test manuel utilisateur : reporté en fin d'EPC03 (décision de
   cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : trois décisions validées par l'utilisateur : application
  immédiate (pas de bouton OK, fermeture par « Close ») ; double point
  d'entrée (menu contextuel + Project > Relations... > Associate agents
  with State) ; état initial associable.
- 15-10-2026 : implémentation terminée :
  - `agent_association_dialog.py` : liste à cocher préremplie via
    `find_association` (déconnexion de `itemChanged` pendant le
    rebuild pour éviter les appels parasites), application immédiate au
    cochage/décochement avec statut dans le dialogue (et retour arrière
    de la case si le use case échoue), bouton « New agent... » qui crée
    et associe en une seule opération puis rafraîchit la liste.
  - `journey_workspace.py` : entrée « Associate agents... » dans le menu
    contextuel des State nodes (entre Edit et Delete).
  - `main_window.py` : action « Associate agents with State » dans le
    sous-menu Relations (active uniquement si un State node est
    sélectionné, via `_update_menu_state`) ; handler commun
    `_associate_agents_to_state(entity)` + variante
    `_associate_agents_to_selected_state()`.
  - Vérifications : `py_compile` OK ; suite complète 76 passed ; test
    offscreen du dialogue rédigé dans
    `tests/test_agents/offscreen_agent_association_dialog.py` (à exécuter
    localement, libGL absent de la sandbox).
