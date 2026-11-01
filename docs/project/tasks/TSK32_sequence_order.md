# TSK32 — Ordre de succession réel des parcours (révision de `Journey_node.sequence_order`)

- **Épic** : EPC05 (gestion des parcours) — prerequisite de l'aperçu d'export (TSK31 suite)
- **Statut** : To do (créée 01-11-2026, décision TSC)
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

- RG (FR/EN) + `07_data_model` FR/EN mis à jour ; recalcul dans
  `ArcService` + use cases attach/detach + load ; tests unitaires.

## Journal

- 01-11-2026 : tâche créée en To do (décision TSC 01-11-2026) — à traiter
  avant l'implémentation de l'aperçu d'export (TSK31 suite).
