# TSK32 — Ordre de succession réel des parcours (révision de `Journey_node.sequence_order`)

- **Épic** : EPC05 (gestion des parcours) — prerequisite de l'aperçu d'export (TSK31 suite)
- **Statut** : En revue (01-11-2026)
- **Date de création** : 01-11-2026
- **Dépendances** : TSK22–TSK29 Done (fondations parcours + filtre en place)
- **Consommée par** : la future tâche d'implémentation de l'aperçu d'export (TSK31 suite)

## Problème

`Journey_node.sequence_order` est aujourd'hui un simple `max+1` à la
création (`Journey_node.for_relation`) — il ne matérialise **pas** l'ordre
réel des séquences (point laissé ouvert par la conception TSK22 §5). Or
l'aperçu/export de la carte narrative (SU007) a besoin de l'ordre réel,
par parcours.

## Objectif

1. **Nouvelle règle de gestion** (FR/EN) : `sequence_order` = position
   réelle du nœud dans la séquence du parcours, calculée par parcours en
   profondeur depuis l'état initial (RG031), en ne suivant que les arcs
   rattachés à ce parcours (ordre topologique). À un embranchement, les
   branches sont ordonnées de façon déterministe (ex. par id d'arc).
2. **Recalcul aux points de modification du graphe** : `ArcService.create_arc`,
   `ArcService.delete_related_arcs`, `Attach/DetachRelationToJourneyUseCase`
   (RG027), cascades de suppression (état/agent/parcours), chargement de
   projet (recalcul au load pour corriger les anciennes valeurs).
3. **Cycles longs** : RG058 n'interdit que les cycles de longueur 2 ; le
   recalcul doit mémoriser les nœuds déjà visités pour ne pas reboucler.
4. **Pas de second champ** : la clé JSON `sequence_order` est conservée,
   seule sa sémantique change (rétrocompatible : recalcul au chargement).
5. **Tests** : ordre recalculé après création/suppression d'arc,
   attach/detach, embranchements, cycle long, round-trip JSON + chargement
   legacy.

## Livrable

- RG069 (FR/EN) + `07_data_model` FR/EN mis à jour ; `JourneySequenceService`
  + recalcul dans `ArcService` + use cases attach/detach/cascades/duplication/suppression
  + load ; tests unitaires.

## Journal

- 01-11-2026 : tâche passée en Doing (décision TSC). Plan d'implémentation validé :
  RG069 (DFS depuis l'état initial sur les arcs du parcours, branches par id d'arc
  croissant, mémoïsation des états visités pour les cycles longs) ; nœud
  d'association = rang de l'état rattaché (1 pour l'état initial) ; repli
  déterministe (id croissant, à partir de max+1) pour les nœuds non atteignables
  depuis l'état initial ; recalcul global (tous les parcours) à chaque point de
  modification du graphe.
- 01-11-2026 : implémentation — RG069 FR/EN + `07_data_model` FR/EN (description
  `sequence_order`) ; nouveau `core/services/journey_sequence_service.py`
  (`recompute_all` / `recompute_journey`, DFS depuis l'état initial, mémoïsation
  des composants visités par (type, id), repli par (type de relation, id)) ;
  `Journey_node.for_relation` passe à `sequence_order=0` (placeholder) ;
  recalcul branché aux 10 points : `ArcService.attach_to_active_journey`,
  `ArcService.delete_journey_nodes_for_arcs`, attach/detach use cases,
  `DissociateAgentStateUseCase`, `RemoveStateAssociationsUseCase`,
  `DeleteAgentUseCase`, `DeleteJourneyUseCase` (nœuds basculés), `DuplicateJourneyUseCase`,
  `ProjectService.load_project` (valeurs legacy recalculées au chargement, sans
  toucher à `_is_modified`). Tests `tests/test_journeys/test_sequence_order.py`
  (+18 : chaîne linéaire, embranchement déterministe, arc partagé multi-parcours,
  cycle long, rang des associations, repli nœuds non atteignables, recalcul à chaque
  point de modification, idempotence, round-trip JSON + chargement legacy).
  Vérifications : py_compile OK, `pytest tests/ -q --ignore=tests/test_application`
  → 217 passed (199 existants + 18 nouveaux ; `test_application` exclu, pywinauto
  Windows-only non installable ici).
- 01-11-2026 : correctif constaté par les tests — les ids d'arcs étant uniques par
  type seulement, `ArcService.delete_journey_nodes_for_arcs` mélangeait les ids des
  deux listes d'arcs (suppression d'un arc `Event_to_state` id n supprimait aussi le
  nœud de l'arc `State_to_event` id n) : signature passée à deux sets
  (`deleted_stes_ids`, `deleted_e2s_ids`) ; même séparation par type dans
  `JourneySequenceService` (`stes_ids` / `e2s_ids`) et mémoïsation `visited` par
  (type, id). Kanban v29 : tâche passée en En revue.

## Journal

- 01-11-2026 : tâche créée en To do (décision TSC 01-11-2026) — à traiter
  avant l'implémentation de l'aperçu d'export (TSK31 suite).
