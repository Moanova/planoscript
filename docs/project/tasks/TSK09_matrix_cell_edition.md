# TSK09 — Édition des cellules de la matrice (cocher/décocher)

- **Épic** : EPC03 — Implémenter la vue agents (SU008/SU009, FN030)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK08 (Done), #TSK03 (Done)

## Périmètre

Second point d'entrée des associations (SU008) : l'édition des cellules
de la matrice agents × états — cocher une cellule associe l'agent de la
ligne à l'état de la colonne, la décocher les dissocie. Complète la
symétrie : toute modification faite depuis la vue parcours (dialogue
TSK04) est visible dans la matrice (TSK08) et réciproquement, toute
modification faite depuis la matrice doit être répercutée dans la vue
parcours (badges TSK05, infobulles).

## Règles et critères applicables

- **SU008** : « Depuis la vue agents, l'édition s'effectue en
  cochant/décochant la cellule » ; « Les deux points d'entrée modifient
  la même donnée métier. Toute association ou dissociation est
  immédiatement répercutée dans l'autre vue. »
- **FN030** : cocher/décocher la cellule appelle le use case
  d'association ; RG063 (unicité) garantie côté données.
- **RG067** (par extension) : le rafraîchissement des badges est un état
  visuel — ne marque pas le projet au-delà de ce que les use cases font
  déjà (`set_modified(True)` vient des use cases, pas de l'UI).
- L'ordre des colonnes/lignes n'est pas impacté par l'édition (RG068 :
  seuls les déplacements d'en-têtes le modifient).

## État des lieux (existant mobilisable)

- Matrice TSK08 : `AgentsWorkspace.refresh()` reconstruit, CheckStates
  programmatiques, `NoEditTriggers`, pas de `itemChanged` branché.
- Use cases TSK03 : `AssociateAgentStateUseCase` (RG063 idempotente),
  `DissociateAgentStateUseCase`.
- En-têtes de la matrice : IDs (agent/state) stockés en `UserRole` des
  items d'en-tête — récupérables sans ambiguïté au moment du clic.
- `JourneyWorkspace.refresh_state_badge(node)` / MainWindow
  `_refresh_all_state_badges()` : rafraîchissement inverse déjà en place.
- `InfoBar` : messages de statut.

## Plan d'implémentation

1. **Activation de l'édition dans la matrice** (`agents_workspace.py`) :
   - Les items de cellule deviennent activables au clic pour basculer
     leur CheckState (les CheckState des `QTableWidgetItem` ne
     basculent pas au clic sans flags d'activation — un simple
     `cellClicked`/`itemClicked` ne suffit pas : brancher
     `cellClicked` sur un handler qui bascule l'état, **ou** laisser
     l'interaction de case à cocher native). Recommandé : handler
     unique `cellClicked(row, column)` qui lit l'état courant et
     exécute l'action inverse — un seul point d'édition, pas de double
     signal (convention AGENTS.md).
   - Le handler résout les entités via les IDs des en-têtes
     (`UserRole`), appelle le use case correspondant (associer si
     décochée, dissocier si cochée).
   - En cas d'échec du use case : retour arrière de la case (état
     visuel replacé sur la valeur réelle des données) — même pattern
     que le dialogue TSK04.
   - Suppression du libellé « read only » et de l'info label de TSK08.
2. **Injection des use cases** : `AgentsWorkspace` reçoit les use cases
   d'association/dissociation (constructeur ou `set_project`,
   cohérent avec l'injection existante du `project_service`).
3. **Répercuter dans la vue parcours** (SU008, sens matrice → parcours) :
   - Après chaque édition réussie : rafraîchir le badge du node de
     l'état concerné. `AgentsWorkspace` ne connaît pas le workspace
     parcours (découplage) → signal Qt `associationChanged(state_id)`
     émis par `AgentsWorkspace`, connecté dans MainWindow à un handler
     qui appelle `refresh_state_badge` sur le node de l'état (pattern
     signaux établi : le workspace communique avec MainWindow par
     signaux, jamais par appels de méthodes privées — AGENTS.md).
   - Pas de reconstruction de la matrice après édition (la case est
     déjà à jour ; le refresh complet n'est déclenché que par les
     autres points d'entrée).
4. **Barre d'infos** : message de statut après chaque édition
   (« Agent 'X' associated with state 'Y' » / dissociated) — même
   granularité que le dialogue TSK04, via le même signal (charge
   utile étendue) ou un second signal dédié. Recommandé : le signal
   `associationChanged` transporte (state_id, agent_lb, associated:
   bool) et MainWindow affiche le message et rafraîchit le badge.
5. **Tests** :
   - Logique d'édition testable hors rendu : le handler
     `_toggle_cell(row, column)` appelle des use cases injectés —
     testable en offscreen local (cellule cochée → `state_agent_rel`
     créé ; décochée → supprimé ; échec de use case simulé → case
     restaurée).
   - Suite unitaire : inchangée (les use cases sont déjà couverts par
     les 13 tests de TSK03).
   - Test offscreen local (rédigé, libGL) : édition depuis la matrice
     puis vérification du badge du node dans la vue parcours (sens
     inverse), et édition depuis le dialogue TSK04 visible dans la
     matrice (déjà couvert par le refresh TSK08).

## Décisions à valider

- **Handler `cellClicked` unique** qui bascule l'état (recommandé :
    un seul point d'édition, pas de double signal) vs activation des
    cases natives (`ItemIsUserCheckable` + interaction de clic de Qt).
- **Signal `associationChanged`** vers MainWindow (pattern signaux du
    projet, découplage) vs accès direct au workspace parcours
    (interdit par AGENTS.md — écarté d'office, mentionné pour mémoire).
- Message de statut dans la barre d'infos pour chaque édition
    (recommandé, symétrique du dialogue TSK04).

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen local (libGL) : édition cellule → données + badge ;
   échec simulé → case restaurée.
4. Test manuel utilisateur : à la fin d'EPC03 (décision de cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : décisions techniques déléguées par l'utilisateur aux
  recommandations : handler `cellClicked` unique ; signal
  `associationChanged` vers MainWindow (pattern signaux AGENTS.md) ;
  message de statut dans la barre d'infos.
- 15-10-2026 : implémentation terminée :
  - `agents_workspace.py` (v3) : handler unique `_toggle_cell(row,
    column)` branché sur `cellClicked` — résolution des entités via
    les IDs `UserRole` des en-têtes (`_entities_at`), bascule
    associer/dissocier via les use cases, retour arrière de la case en
    cas d'échec, libellé « read only » retiré ; signal
    `associationChanged(state_id, agent_lb, associated)` émis après
    chaque édition réussie ; use cases injectés via `set_project`.
  - `main_window.py` : injection des use cases à l'initialisation de
    la vue agents ; connexion unique du signal à
    `_on_matrix_association_changed` (rafraîchit le badge du node
    d'état dans la vue parcours + message dans la barre d'infos).
  - Symétrie SU008 complète : parcours → matrice (refresh TSK08) et
    matrice → parcours (signal + badge TSK05).
  - Vérifications : `py_compile` OK ; suite complète 95 passed ; test
    offscreen rédigé dans
    `tests/test_agents/offscreen_matrix_cell_edition.py` (local,
    libGL) : édition → données + signal, double bascule, échec simulé
    → case restaurée sans émission.
