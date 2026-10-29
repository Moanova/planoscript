# TSK22 — Fondations parcours (EPC05)

- **Épic** : EPC05 — Gérer un parcours narratif (SU005, FN023–FN027)
- **Statut** : To do
- **Date de création** : 29-10-2026
- **Dépendances** : aucune (première tâche de l'epic)

## Rappel de conception

La conception du rattachement aux parcours est consignée et **validée TSC
le 29-10-2026** dans [`docs/conception/journey_attachment.md`](../../conception/journey_attachment.md).
Points clés :

- `Journey_node` est la **table de liaison** vers les parcours ; le
  rattachement se fait **sur les connexions (arcs)** et associations
  agent-état, jamais directement sur un composant State/Event (aucun champ
  `journey_ids` sur les composants ; l'appartenance est dérivée des nœuds).
- Un arc appartient à **1..n parcours** (n nœuds référençant le même arc).
- Objets orphelins acceptés : invisibles sous filtre parcours (FN029),
  visibles sinon.
- À la création d'une connexion / association, un nœud est créé dans le
  parcours actif.
- Suppression d'un parcours : nœuds orphelins basculés vers le parcours par
  défaut (RG029, RG066 révisée).

## Périmètre de la tâche

1. **Modèle code** :
   - `Journey_node.state_agent_rel_id: Optional[int] = None` (déjà dans les
     specs `07_data_model-FR/EN.json`) ;
   - `NarrativeMap.active_journey_id: Optional[int] = None`, persisté en JSON
     (rétrocompatible : `None` → parcours par défaut).
2. **Use cases** : créer / renommer / activer un parcours
   (FN023/FN024/FN026, RG022/RG023/RG055) ; rattacher / détacher un arc ou
   une association agent-état à un parcours (création/suppression de
   `Journey_node`) ; création automatique du nœud au parcours actif dans
   `ArcService.create_arc` et à la création d'un `State_agent_rel`.
3. **Cascade RG056** étendue aux `Journey_node` référençant l'arc supprimé.
4. **Réécriture des règles FR/EN** (`02_business_rules-FR/EN.md`) selon la
   conception : RG026, RG027, RG031, RG052 (les textes proposés sont dans
   la note de conception, section 4).
5. **Tests unitaires** couvrant chaque règle réécrite (AGENTS.md : toute
   modification de règle implique la mise à jour du test correspondant).

## Points à affiner au fil de la réalisation (actés TSC 29-10-2026)

- `sequence_order` : sémantique exacte au moment du traitement de la tâche
  concernée.
- Nœud partagé (arc + `state_agent_rel_id` sur un même nœud) : à discuter
  au moment de traiter la tâche.

## Hors périmètre

- UI de gestion des parcours (TSK23), duplication (TSK24), suppression
  (TSK25), filtre d'affichage FN029.

## Journal (29-10-2026)

- Modèle : `Journey_node.state_agent_rel_id`, `NarrativeMap.active_journey_id`
  (+ `get_active_journey()`, repli parcours par défaut), `Journey_node.for_relation()`.
- Use cases `src/usecases/journey_management/` : Create/Update/ActivateJourney,
  Attach/DetachRelationToJourney (1..n parcours par relation, idempotent).
- Rattachement auto au parcours actif : `ArcService.create_arc` (arcs) et
  `AssociateAgentStateUseCase` (associations) via `ArcService.attach_to_active_journey`.
- Cascades : `ArcService.delete_related_arcs` (RG056 étendue),
  dissociation, `RemoveStateAssociationsUseCase` (RG065), `DeleteAgentUseCase` (RG064).
- `CreateProjectUseCase` active le parcours par défaut (RG022).
- Règles RG026/RG027/RG031/RG052 réécrites FR/EN ; `active_journey_id` ajouté
  à `07_data_model` FR/EN (niveau carte narrative, type integer/null).
- Tests : +17 dans `tests/test_journeys/test_journey_foundations.py` ;
  suite complète 127 passed ; py_compile OK. Scripts offscreen non exécutables
  dans le sandbox (libGL.so.1) — aucun changement UI dans cette tâche.
- Ouvert (acté) : `sequence_order` ; noeud partagé arc + `state_agent_rel_id`.
