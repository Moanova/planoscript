# TSK03 — Use case d'association agent-état (sans UI)

- **Épic** : EPC02 — Associer des agents à un état (FN030, SU008)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK01 (Done)

## Périmètre

Use case d'association/dissociation agent-état, **sans UI** : associer un
agent à un état, dissocier un agent d'un état, unicité de l'association
(RG063). Les cascades RG064 (suppression d'agent) et RG065 (suppression
d'état) sont déjà implémentées respectivement dans
`DeleteAgentUseCase` (TSK02) et restent à compléter côté suppression
d'état dans le cadre de cette tâche (RG065).

## Règles et critères applicables

- **RG063** : entre un agent et un état donnés d'une même carte narrative,
  il ne peut exister qu'une seule association. Toute tentative de création
  d'une association en double est ignorée ou refusée.
- **RG064** : cascade à la suppression d'un agent — déjà en place (TSK02).
- **RG065** : la suppression d'un état supprime en cascade toutes les
  associations agent-état qui référencent son identifiant. Un message
  d'information est affiché si l'état est associé à au moins un agent.
- **SU008** : l'association est non orientée, porte une note optionnelle
  (non éditable en MVP) ; cocher associe, décocher dissocie.
- Toute association ou dissociation marque la carte, et donc le projet,
  comme modifiés.

## État des lieux (existant mobilisable)

- `State_agent_rel` (`id`, `state_id`, `agent_id`, `note`) dans le data
  model, sérialisé/restauré dans `NarrativeMap`.
- `NarrativeMap.get_next_id('state_agent_rel')` pour l'identifiant.
- Pattern `CreateRelationUseCase` (use case existant de création de
  relation) et `DeleteAgentUseCase` (cascade) comme modèles.
- `Connection` (nodes) et `CreateRelationUseCase` contiennent une branche
  `STATE_AGENT_REL` : reliquat d'un mécanisme de connexion graphique
  agent-état qui n'existe plus dans le MVP (l'association se fait par
  dialogue/matrice, jamais par arc graphique) — à évaluer au nettoyage
  lors de cette tâche ou de TSK05.

## Plan d'implémentation

1. **`AssociateAgentStateUseCase`**
   (`src/usecases/agent_association/` — nouveau sous-dossier, ou
   `usecases/project_management/` ; à trancher à l'implémentation) :
   - `execute(agent, state)` → vérifications (projet ouvert, agent est un
     `Agent` du projet, état est un `State` de la carte narrative courante)
     puis création de `State_agent_rel` avec
     `get_next_id('state_agent_rel')`.
   - **RG063** : si une association `(agent.id, state.id)` existe déjà,
     la création est ignorée (retour succès avec
     `'already_associated': True`, pas d'erreur bloquante — le dialogue
     et la matrice cocheront déjà les cases existantes).
   - `set_modified(True)`, journalisation.
2. **`DissociateAgentStateUseCase`** :
   - `execute(agent, state)` → retrait de la `State_agent_rel`
     correspondante ; refus si elle n'existe pas.
   - `set_modified(True)`, journalisation.
   - Retour du résultat pour la barre d'infos (UI).
3. **RG065 — complément à la suppression d'état** : le flux
   `_delete_selected_component` de `main_window.py` ne traite pas encore
   les `State_agent_rel` (seuls les arcs état-événement le sont via
   `ArcService`). Ajouter la cascade : à la suppression d'un `State`,
   retirer toutes les `State_agent_rel` dont `state_id` correspond, via
   une méthode dédiée dans le use case de suppression ou un service, et
   afficher le message d'information RG065 (état associé à au moins un
   agent) dans la confirmation UI existante.
4. **Tests** (`tests/test_agents/test_agent_state_association.py`) :
   - Association : création correcte (`state_id`/`agent_id`), projet
     modifié, note par défaut absente.
   - RG063 : double association ignorée/refusée, pas de doublon dans
     `state_agent_rel`.
   - Dissociation : retrait, refus si absente, projet modifié.
   - RG065 : suppression d'un état — associations de cet état retirées,
     associations d'autres états intactes ; compte transmis pour le
     message.
   - Persistance : associations préservées/retirées après save/load.
   - Rejets : projet absent, entités invalides, état d'une autre carte
     (hors MVP : une seule carte, mais garde-fou sur l'appartenance).

## Décisions à valider

- **Emplacement du use case** : nouveau sous-dossier
    `src/usecases/agent_association/` (regroupe association/dissociation,
    puis TSK04 et TSK09 s'y raccrocheront) plutôt que
    `project_management/`. Recommandation : `agent_association/`.
- **RG063 en double association** : ignorer silencieusement côté données
    (retour `already_associated`) — le point d'entrée UI (checkbox déjà
    cochée) ne devrait jamais le déclencher en usage normal.
- **RG065** : traiter la cascade dans cette tâche (au lieu d'attendre un
    hypothétique flux dédié) car le kanban lie explicitement TSK03 aux
    cascades RG064/RG065.

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen : non applicable (use case sans UI), tests manuels
   reportés à la fin d'EPC03.

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : décisions validées par l'utilisateur : sous-dossier
  `usecases/agent_association/` (l'agent est porté par le projet, la
  relation est transverse projet/carte) ; RG063 « ignorée » idempotente
  (checkbox déjà cochée en usage normal, journalisée, retour
  `already_associated`) ; RG065 traitée dans cette tâche.
- 15-10-2026 : implémentation terminée :
  - `associate_agent_state_usecase.py` : création de `State_agent_rel`
    (ID via `get_next_id('state_agent_rel')`), RG063 idempotente
    (`already_associated`), validations (projet, agent du projet, état de
    la carte courante), `set_modified(True)`, journalisation ;
    `find_association` réutilisé par la dissociation.
  - `dissociate_agent_state_usecase.py` : retrait de l'association,
    refus si absente, `set_modified(True)`, journalisation.
  - `remove_state_associations_usecase.py` : cascade RG065 sur toutes
    les cartes narratives, compte `deleted_associations`.
  - `main_window.py` : `_delete_selected_component` complète la cascade
    RG065 à la suppression d'un State et affiche le message
    d'information (« State deleted (n agent association(s) removed) »).
  - Tests : `tests/test_agents/test_agent_state_association.py`
    (13 tests : association, RG063 idempotente, dissociation, RG065,
    persistance, rejets). Suite complète : 76 passed.
