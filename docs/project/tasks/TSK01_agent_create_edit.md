# TSK01 — Créer et modifier un agent

- **Épic** : EPC01 — Gérer les agents du projet (FN031, SU008/SU009)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : aucune

## Périmètre

Création et modification d'un agent du projet : entité `Agent` portée par le
projet (et non par la carte narrative), identifiant entier unique au niveau du
projet, type (sujet/objet), réactivation de l'entrée de menu
« Project > Components > Agent », dialogue d'édition. La suppression
d'agent est hors périmètre (TSK02), les associations agent-état sont hors
périmètre (TSK03/TSK04).

## État des lieux (existant mobilisable)

- `core.models.data_model.Agent` existe déjà : `id`, `lb`, `typ`
  (`"Subject"`/`"Object"`, validé dans `__post_init__`), `note`,
  horodatages, `to_dict`/`from_dict`.
- `Project.agent: List[Agent]` existe, sérialisé dans `Project.to_dict` et
  restauré dans `Project.from_dict` : la persistance est déjà en place.
- `Project.get_next_id('agent')` existe (identifiant unique projet).
- Entrée de menu « Agent » stubbée dans `main_window.py`
  (`self.components_menu.addAction("Agent", lambda: None)`).
- `CreateNodeUseCase` contient une branche « Agent » qui crée un **node
  graphique** : c'est un reliquat contraire à la spécification (SU008/SU009 :
  l'agent n'est jamais un node de la vue parcours) ; le node `AgentNode`
  est dans le même cas.
- Journalisation des actions sur les données du projet en place
  (`change_log_service` / logger, `log_level` dans `config.json`).

## Plan d'implémentation

1. **Use cases** (`src/usecases/project_management/`) — créer
   `create_agent_usecase.py` et `update_agent_usecase.py`, sur le modèle des
   use cases existants (injection de `ProjectService`, `execute()` retournant
   un dictionnaire de résultat) :
   - Création : `id = project.get_next_id('agent')`, libellé par défaut
     `Agent {id}`, `typ="Subject"` par défaut, note optionnelle ; ajout à
     `project.agent` ; `set_modified(True)` ; journalisation de l'action.
   - Modification : mise à jour de `lb`, `typ`, `note` ;
     `modification_date_time` actualisé ; `set_modified(True)` ;
     journalisation. Refus si `typ` invalide (le modèle lève déjà
     `ValueError`).
2. **Dialogue d'édition** (`src/ui/dialogs/agent_dialog.py`) — nouveau
   `AgentDialog` sur le pattern de `ComponentDialog` (validation `lb` non
   vide, `get_values()`, boutons OK/Cancel) :
   - Formulaire : libellé (obligatoire), type (combo `Subject`/`Object`),
     note (champ texte multi-ligne, optionnel).
   - Le dialogue est réutilisable en mode création (formulaire vide) et en
     mode édition (formulaire prérempli depuis une entité `Agent`).
3. **Sélection de l'agent à éditer** : l'entrée de menu « Agent » ouvre un
   dialogue de gestion listant les agents existants (libellé + type), avec
   boutons « New... » et « Edit ». L'édition n'est active que si un agent est
   sélectionné dans la liste. Ce dialogue est la seule surface de sélection
   tant que la vue agents n'existe pas (EPC03) ; la liste sera réutilisée
   par le dialogue d'association de TSK04.
4. **Câblage UI** (`main_window.py`) : remplacer le stub `addAction("Agent",
   lambda: None)` par l'ouverture du dialogue de gestion ; l'action est
   active uniquement si un projet est ouvert (le menu `components_menu` est
   déjà gated par `has_project`, RG007/RG008).
5. **Nettoyage du reliquat « agent node »** : retirer la branche `Agent` de
   `CreateNodeUseCase` (COMPONENT_MAPPING, `_create_entity`,
   `_add_entity_to_narrative_map`) et `src/ui/nodes/agent_node.py`, conforme
   à la convention « retirer complètement le code mort » et à la
   spécification (l'agent n'est jamais un node de la vue parcours).
6. **Tests** (`tests/test_agents/`, sur le modèle de
   `tests/test_components/`) :
   - `test_create_agent_usecase.py` : identifiants uniques successifs,
     valeurs par défaut, ajout à `project.agent`, projet marqué modifié,
     rejet de `typ` invalide.
   - `test_update_agent_usecase.py` : modification des attributs,
     horodatage, projet marqué modifié.
   - Test de persistance : aller-retour sauvegarde/rechargement d'un projet
     contenant des agents (créé, modifié, fermé, rouvert).
   - Le dialogue et le câblage menu seront vérifiés par le test offscreen
     ciblé (jetable, non commité) + test manuel reporté en fin d'EPC03
     (décision de cadrage utilisateur).

## Décisions à valider

- **Point 5 (nettoyage du reliquat)** : retirer dès TSK01 la branche Agent
  de `CreateNodeUseCase` et `AgentNode`, ou différer à TSK05 (badges) pour
  limiter le périmètre du diff. Recommandation : retirer dès TSK01
  (convention AGENTS.md sur le code mort).
- Libellés par défaut : `Agent {id}` sur le modèle de
  `State {id}` / `Event {id}` dans `CreateNodeUseCase`.

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen ciblé du dialogue (si l'environnement le permet).
4. Test manuel utilisateur : reporté en fin d'EPC03 (décision de cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : implémentation terminée :
  - `create_agent_usecase.py` / `update_agent_usecase.py` (identifiant unique
    projet via `get_next_id('agent')`, libellé par défaut `Agent {id}`,
    validation typ Subject/Object, horodatage, `set_modified(True)`,
    journalisation `logger.info`).
  - `AgentDialog` (création/édition, pattern ComponentDialog) et
    `AgentManagementDialog` (liste des agents, New/Edit, bouton Edit
    désactivé si la liste est vide, double-clic = édition).
  - Câblage `main_window.py` : entrée « Project > Components > Agent »
    branchée sur `_manage_agents()` (gated par `components_menu` déjà
    contrôlé par RG007/RG008).
  - Nettoyage du reliquat : `agent_node.py` supprimé, branche Agent retirée
    de `CreateNodeUseCase`, `NodeType.AGENT` et `agent_nodes` retirés du
    `WorkspaceLayout` (l'agent n'a pas de layout visuel), imports et
    docstrings mis en cohérence.
  - Tests : `tests/test_agents/test_agent_usecases.py` (14 tests : use
    cases création/édition, rejets, persistance aller-retour). Suite
    complète : 56 passed. Test offscreen des dialogues rédigé mais non
    exécutable dans la sandbox (libGL absent) — à exécuter localement.
- Décision validée par l'utilisateur : nettoyage du reliquat effectué dès
  TSK01 (pas de report à TSK05).
