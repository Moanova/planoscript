# TSK02 — Supprimer un agent avec confirmation et suppression en cascade

- **Épic** : EPC01 — Gérer les agents du projet (FN031, SU008/SU009)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK01 (Done)

## Périmètre

Suppression d'un agent du projet : confirmation préalable systématique
(critère SU008 : « avec confirmation préalable », sans condition sur les
données associées), suppression en cascade de toutes les associations
agent-état qui référencent son identifiant (RG064), message d'information si
l'agent est associé à au moins un état (RG064). Le point d'entrée est le
dialogue de gestion des agents issu de TSK01.

## Règles et critères applicables

- **RG064** : la suppression d'un agent supprime en cascade toutes les
  associations agent-état qui référencent son identifiant. Un message
  d'information est affiché si l'agent est associé à au moins un état.
- **SU008** (critère d'acceptation) : « La suppression d'un agent supprime en
  cascade toutes ses associations avec les états, avec confirmation
  préalable. »
- **FN031** : « La suppression d'un agent supprime en cascade toutes ses
  associations aux états (RG064), avec confirmation préalable. Toute
  suppression d'agent marque le projet comme modifié. »
- RG065 (cascade côté état) ne concerne pas cette tâche (suppression d'un
  état — seront traitées via les cascades de composants existantes).

## État des lieux (existant mobilisable)

- `State_agent_rel` existe dans le data model (`id`, `state_id`, `agent_id`,
  `note`), stocké dans `narrative_map.state_agent_rel`, sérialisé et
  restauré (persistance en place).
- `AgentManagementDialog` (TSK01) liste les agents avec New/Edit ; il
  n'offre pas encore de suppression.
- Pattern de confirmation existant : `QMessageBox.question` dans
  `main_window.py` (Yes/No/Cancel).
- Pattern de cascade existant : `ArcService.delete_related_arcs` pour les
  arcs état-événement ; la suppression d'un agent suivra le même principe
  (méthode de service ou logique dans le use case).

## Plan d'implémentation

1. **`DeleteAgentUseCase`** (`src/usecases/project_management/delete_agent_usecase.py`),
   sur le modèle des use cases existants :
   - Vérifications : projet ouvert, entité est un `Agent`.
   - Suppression en cascade RG064 : retrait de toutes les
     `State_agent_rel` de `narrative_map.state_agent_rel` dont
     `agent_id == agent.id` (toutes les cartes narratives, par cohérence
     avec le MVP une seule carte mais la boucle couvre la liste).
   - Retrait de l'agent de `project.agent`.
   - `set_modified(True)` ; journalisation (`logger.info`) avec le nombre
     d'associations supprimées en cascade.
   - Retour : dictionnaire `{'success', 'entity_id', 'deleted_associations'}`
     (le compte alimente le message d'information RG064 côté UI).
   - La confirmation est une responsabilité UI : le use case ne confirme
     pas, il exécute (même séparation que `_delete_selected_component`).
2. **`AgentManagementDialog`** : ajout d'un bouton « Delete » :
   - activé uniquement si un agent est sélectionné dans la liste ;
   - désactivé si la liste est vide (cohérent avec « Edit »).
3. **Câblage `main_window.py`** (`_manage_agents`) :
   - le dialogue retourne l'action `"delete"` avec l'agent sélectionné ;
   - `QMessageBox.question` de confirmation mentionnant, le cas échéant,
     le nombre d'états associés (message d'information RG064, ex. :
     « This agent is associated with 3 state(s). Delete the agent and all
     its associations? ») ;
   - en cas de confirmation : exécution du use case, message dans la barre
     d'infos (« Agent deleted » ou « Agent deleted (3 association(s)
     removed) »), rafraîchissement de la liste du dialogue de gestion
     (recréation du dialogue ou re-listing après suppression — à définir à
     l'implémentation, probablement une boucle sur le dialogue pour
     permettre plusieurs suppressions en série).
4. **Tests** (`tests/test_agents/test_delete_agent_usecase.py`) :
   - Suppression simple : agent retiré de `project.agent`, projet marqué
     modifié.
   - Cascade RG064 : création d'associations `State_agent_rel` (via
     construction directe du modèle) référençant l'agent + d'autres agents ;
     après suppression, seules les associations de l'agent supprimé ont
     disparu, les autres sont intactes.
   - Compte `deleted_associations` correct (0, 1, n).
   - Rejets : agent non-Agent, pas de projet.
   - Persistance : après suppression + save/load, l'agent et ses
     associations sont bien absents du fichier rechargé.
   - Note : la confirmation UI (QMessageBox) relève du test offscreen
     local et du test manuel de fin d'EPC03.

## Décisions à valider

- Aucune bloquante. Point d'implémentation mineur : après une suppression,
    le dialogue de gestion se rouvre avec la liste rafraîchie (permet
    suppressions en série), plutôt qu'un message seul dans la barre d'infos.

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen du dialogue : non exécutable dans la sandbox (libGL),
   à exécuter localement si souhaité.
4. Test manuel utilisateur : reporté en fin d'EPC03 (décision de cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : implémentation terminée :
  - `delete_agent_usecase.py` : cascade RG064 sur toutes les cartes
    narratives, retrait de l'agent, `set_modified(True)`, journalisation
    avec le compte d'associations supprimées ; la confirmation reste une
    responsabilité UI.
  - `AgentManagementDialog` : bouton « Delete », activé uniquement sur
    sélection (Edit/Delete pilotés par `currentItemChanged`).
  - `main_window.py` : `_manage_agents` réécrit en boucle (dialogue rouvert
    après chaque opération) ; confirmation `QMessageBox.question` avec
    message d'information RG064 (nombre d'états associés) ; barre d'infos
    « Agent deleted (n association(s) removed) ».
  - Tests : `tests/test_agents/test_delete_agent_usecase.py` (7 tests :
    suppression simple, cascades 1/n, associations des autres agents
    intactes, rejets, persistance). Fixtures agents alignées sur
    `CreateProjectUseCase` (RG031 : l'état initial existe). Suite
    complète : 63 passed.
