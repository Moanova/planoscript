# TSK35 — Corrections pré-clôture (filtre parcours + cascade suppression relation)

- **Créée** : 06-11-2026 (décision TSC), passée en Doing 06-11-2026
- **Contexte** : test utilisateur des deux cas de test (`testCase01.json` —
  persona Jen Yen, `testCase02.json` — persona Tom Son). Deux bugs constatés :
  1. sous le filtre « Premier parcours » de testCase01, les états des branches
     P2/P3 restent affichés (idem « Troisième parcours » avec des états P1/P2) ;
  2. `journey_node#22` de testCase01 référence un arc supprimé (nœud fantôme).

## Analyse

1. **Filtre parcours** : `JourneyFilterService.visible_component_ids` fait
   dériver l'appartenance d'un composant des associations agent-état aussi
   (boucle sur `state_agent_rel`), alors que `docs/conception/journey_attachment.md`
   §2.3 prévoit une dérivation **par les arcs seuls**. Les associations créées
   sous un autre parcours actif (RG052) « tirent » donc leur état dans le
   parcours filtré. Le nœud fantôme n'y est pour rien (l'arc supprimé n'existe
   plus, il ne donne aucune visibilité).
2. **Suppression de relation** : `Connection.delete_arc_or_association`
   (`src/ui/nodes/connection.py:811-850`) écrit directement dans le modèle,
   supprime la relation **sans** supprimer les `Journey_node` qui la
   référencent ni recalculer RG069, et contient le code mort
   `narrative_map.set_modified` (dette TSK34).

## Décisions

- RG026 révisée (FR/EN) : appartenance d'un composant dérivée des arcs seuls ;
  une association n'est visible sous le filtre que si son état y est visible.
  RG066 précisée en ce sens.
- `JourneyFilterService` : `visible_component_ids` = arcs seuls ;
  `visible_relation_keys` filtre les clés d'association dont l'état n'est pas
  visible.
- `ArcService.delete_relation(narrative_map, relation_type, relation_id)` :
  supprime la relation + les `Journey_node` référençant (RG056 extended) +
  recompute RG069 ; `connection.py` appelle ce service (plus d'écriture
  directe, `set_modified` mort retiré).
- `ArcService.prune_orphan_journey_nodes` appelé au chargement
  (`ProjectService.load_project`) pour réparer les fichiers existants.
- Tests : `tests/test_visualization/test_journey_filter.py` mis à jour (RG026
  révisée) + régression bug #1 ; nouveaux tests pour `delete_relation` et la
  purge au chargement.

## Journal

- 06-11-2026 : implémentation en cours.
- 06-11-2026 : livrée. (1) `JourneyFilterService` : `_arc_component_ids` +
  filtrage des clés d'association par visibilité de l'état ; RG026 révisée
  FR/EN (« arcs seuls »), RG066 précisée, FN029 FR/EN, `journey_filter.md`
  amendé ; tests `test_journey_filter.py` mis à jour + régression
  (association d'un état étranger rattachée à un autre parcours). (2)
  `ArcService.delete_relation` (relation + `Journey_node` + recompute RG069)
  appelé par `Connection.delete_arc_or_association` (écriture directe et
  `set_modified` mort retirés) ; `ArcService.prune_orphan_journey_nodes`
  appelé au chargement dans `ProjectService.load_project` ; tests
  `tests/test_relations/test_relation_deletion_cascade.py` (+5).
- Vérifications : py_compile OK ; `pytest tests/ -q --ignore=tests/test_application`
  → **232 passed** (226 + 6) ; rejeu sur `testCase01.json` : filtre J1 →
  Ett 00/01P1/02P1/99, J3 → Ett 00/01P3/03P2/04P2/05P2/99, J2 inchangé ;
  nœud orphelin node#22 purgé au chargement. En revue, en attente de
  validation TSC (test GUI du filtre sur testCase01).
