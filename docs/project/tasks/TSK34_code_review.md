# TSK34 — Revue de code (dette technique) : normalisation des modifications du modèle

- **Épic** : hygiène du code (hors epic métier)
- **Statut** : To do (créée 01-11-2026, décision TSC) — à traiter ultérieurement
- **Date de création** : 01-11-2026
- **Dépendances** : aucune bloquante (TSK33 en cours apporte le hook `ProjectService.on_modified`)
- **Contexte** : créée à la demande TSC lors du lancement de TSK33.

## Problème constaté (audit 01-11-2026)

Architecture visée : UI → use cases → services → models (« l'UI ne modifie jamais
directement le modèle métier »). En pratique :

- le **flag** passe toujours par `project_service.set_modified(...)` (19 use cases +
  handlers `main_window`) — conforme ;
- mais la **modification du modèle** se fait parfois en direct depuis l'UI :
  - `main_window.py` appelle `ArcService.delete_related_arcs(...)` directement
    (suppression composant, lignes ~1725/1811) au lieu d'un use case dédié ;
  - `src/ui/nodes/connection.py` écrit directement dans les listes du modèle
    (`narrative_map.state_to_event = [...]`, lignes ~833-847) ;
  - `connection.py:849-850` : **code mort** — `hasattr(narrative_map, 'set_modified')`
    est toujours False (`NarrativeMap` n'a pas de méthode `set_modified`).

## Objectif

1. Audit complet des modifications du modèle hors use cases ; décider pour chaque cas
   du use case à créer (ex. `DeleteComponentUseCase`, `DeleteRelationUseCase`) ou de
   la justification à conserver.
2. Supprimer le code mort `narrative_map.set_modified` de `connection.py`.
3. Faire reposer la notification de modification sur le hook `ProjectService.on_modified`
   (mis en place par TSK33) : un seul point de passage, core reste Qt-free.
4. Tests de non-régression après refactor.

## Livrables

- Use cases manquants + appels UI remplacés ; code mort supprimé ; tests à jour.

## Journal

- 01-11-2026 : tâche créée en To do (décision TSC, kanban v31).
