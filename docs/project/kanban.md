# Planoscript ::: Suivi de projet (Kanban)

- **Version** : 1
- **Date** : 15-10-2026
- **Description** : Suivi de l'avancement des tâches du projet. Le détail de chaque tâche (analyse, décisions, journal des travaux) est consigné dans un fichier markdown dédié du sous-dossier `tasks/`, nommé d'après la tâche.

---

## To do

- [ ] SU003 — Duplication d'un composant (FN016)
- [ ] SU003 — Rattachement des composants aux parcours (FN019, dépend de SU005)
- [ ] SU005 — Gérer un parcours narratif (FN023 à FN027)
- [ ] SU004 — Éditer une relation (annoter une relation via panneau de propriétés, FN021)
- [ ] SU008 — Associer des agents à un état : dialogue « Associer des agents... » depuis le menu contextuel d'un état (FN030)
- [ ] SU008 — Gérer les agents du projet : création, renommage, modification, suppression (FN031)
- [ ] SU009 — Implémenter la vue agents (matrice agents × états, second espace de travail, onglet « Agents »)
- [ ] SU009 — Déterminer la règle de gestion de l'ordre des colonnes de la matrice (à ajouter aux règles de gestion avant implémentation)
- [ ] SU006 — Zoom de l'espace de visualisation
- [ ] SU007 — Export de lecture « par événements »
- [ ] SU007 — Export technique pour réimport (dépend de la réintroduction de l'import de carte)
- [ ] Conception — Évaluer et ajuster le contenu de AGENTS.md

## Doing

- (aucune tâche en cours)

## Done

- [x] SU003 — Création des composants State et Event (menu + menu contextuel, position centre de l'espace de travail)
- [x] SU003 — Suppression d'un composant avec suppression en cascade des relations (RG031 : état initial non supprimable)
- [x] SU003 — Édition des données d'un composant State/Event : UpdateComponentUseCase + ComponentDialog (RG061/RG062)
- [x] SU004 — Création d'une relation State-Event (mode rubber band, RG054/RG058)
- [x] SU004 — Suppression d'une relation avec confirmation
- [x] Nettoyage des layouts obsolètes lors d'une sauvegarde par écrasement (delete_stale_layouts)
- [x] Conception — SU008/SU009 : associations agent-état et vue agents (user stories, règles RG063-RG067, features FN030-FN032, interface, menu — FR/EN)
- [x] Conception — Mise en cohérence des spécifications (périmètre MVP agents, trois composants, onglets Parcours/Agents, reliquats retirés)
- [x] Journalisation des actions sur les données du projet (config log_level dans config.json)
