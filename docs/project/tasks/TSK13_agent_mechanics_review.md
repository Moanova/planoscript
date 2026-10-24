# TSK13 — Révision de la mécanique de création et d'édition des agents, et de l'association états-agents

- **Épic** : EPC01/EPC02 (gestion des agents, associations)
- **Statut** : To do
- **Date de création** : 24-10-2026
- **Dépendances** : aucune (TSK01–TSK05 Done)

## Périmètre

Revue de la mécanique fonctionnelle (hors esthétique) de :

1. **Création et édition des agents** — dialogue `AgentDialog`
   (TSK01, FN031), gestion des agents `AgentManagementDialog`
   (`Project > Manage agents`), création d'agent intégrée au dialogue
   d'association (TSK04).
2. **Association états-agents** — dialogue « Associer des agents... »
   (TSK04), édition des cellules de la matrice agents × états (TSK09),
   badges sur les nœuds d'état (TSK05).

Le périmètre précis (points à corriger/améliorer, parcours utilisateur
cible) sera précisé par TSC. Cette tâche est volontairement ouverte en
l'attente de ce cadrage.

## Contexte (existant mobilisable)

- Entité `Agent` portée par le projet, CRUD via use cases
  (`CreateAgentUseCase`, `UpdateAgentUseCase`, `DeleteAgentUseCase`),
  cascade RG064 à la suppression (TSK02).
- Association agent-état idempotente (RG063), dissociation, cascades
  RG064/RG065 (TSK03) ; dialogue d'association à cocher à application
  immédiate (TSK04) ; matrice éditable avec ordre RG068 persisté (TSK08,
  TSK09) ; badges compteur sur les nœuds d'état (TSK05) ; navigation
  croisée avec focus RG067 (TSK10).

## Journal

- 24-10-2026 : tâche créée à la demande de TSC, en attente de cadrage
  (prochaine séance).
