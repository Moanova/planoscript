# Planoscript ::: Suivi de projet (Kanban)

- **Version** : 3
- **Date** : 15-10-2026
- **Description** : Suivi de l'avancement des tâches du projet. Les chantiers majeurs sont des **épics** (EPCnn) découpés en **tâches** (TSKnn). Le détail de chaque tâche (analyse, décisions, journal des travaux) est consigné dans un fichier markdown dédié du sous-dossier `tasks/`, nommé d'après le code de la tâche. Le fichier de détail est créé au passage de la tâche en Doing.

---

## Convention de dépendances

- Une dépendance est notée `→ #TSKnn` (ou `→ #SUxxx` pour les scénarios) **uniquement sur la tâche dépendante** (source unique de vérité ; pas de lien inverse sur la tâche bloquante).
- Une tâche ne passe en Doing que si toutes ses dépendances sont en Done ; une tâche bloquée reste en To do.
- Les dépendances se déclarent entre tâches ; les mentions au niveau epic restent indicatives.

## Chaîne critique (déroulé de référence)

```
TSK01 → TSK02 → TSK03 → TSK04 → TSK05
                    TSK06 → TSK07 → TSK08 → TSK09 → TSK10
```

---

## To do

- [ ] **EPC01 — Gérer les agents du projet** (FN031, SU008/SU009)
  - [ ] TSK01 — Créer et modifier un agent : entité Agent portée par le projet, identifiant unique projet, type (sujet/objet), réactivation de l'entrée de menu, dialogue d'édition
  - [ ] TSK02 — Supprimer un agent avec confirmation et suppression en cascade des associations agent-état (RG064) → #TSK01
- [ ] **EPC02 — Associer des agents à un état** (FN030, SU008)
  - [ ] TSK03 — Use case d'association agent-état : associer/dissocier, unicité (RG063), cascades (RG064/RG065) — sans UI → #TSK01
  - [ ] TSK04 — Dialogue « Associer des agents... » depuis le menu contextuel d'un état (liste à cocher, création d'agent intégrée) → #TSK01, #TSK03
  - [ ] TSK05 — Badges d'agents sur les nodes d'état dans la vue parcours (affichage + rafraîchissement) → #TSK03
- [ ] **EPC03 — Implémenter la vue agents** (SU009, second espace de travail, onglet « Agents »)
  - [ ] TSK06 — Déterminer la règle de gestion de l'ordre des colonnes de la matrice (conception ; à ajouter aux règles de gestion avant implémentation)
  - [ ] TSK07 — Bascule d'espace de travail : barre d'onglets Parcours ↔ Agents
  - [ ] TSK08 — Affichage de la matrice agents × états en lecture seule → #TSK06, #TSK07
  - [ ] TSK09 — Édition des cellules de la matrice (cocher/décocher → use case d'association) → #TSK08, #TSK03
  - [ ] TSK10 — (P2) Navigation croisée entre vues avec focus (RG067) → #TSK08
- [ ] SU003 — Duplication d'un composant (FN016)
- [ ] SU003 — Rattachement des composants aux parcours (FN019) → #SU005
- [ ] SU004 — Éditer une relation : annotation via panneau de propriétés (FN021)
- [ ] SU005 — Gérer un parcours narratif (FN023 à FN027 — à découper avant passage en Doing)
- [ ] SU006 — Zoom de l'espace de visualisation
- [ ] SU007 — Export de lecture « par événements »
- [ ] SU007 — Export technique pour réimport → #import de carte (hors périmètre)


## Doing

- (aucune tâche en cours)

## Done

- [x] Conception — Évaluer et ajuster le contenu de AGENTS.md (vue d'ensemble alignée sur le MVP agents, rechargement des specs et du kanban en début de séance, suivi kanban, stubs de menus)

- [x] SU003 — Création des composants State et Event (menu + menu contextuel, position centre de l'espace de travail)
- [x] SU003 — Suppression d'un composant avec suppression en cascade des relations (RG031 : état initial non supprimable)
- [x] SU003 — Édition des données d'un composant State/Event : UpdateComponentUseCase + ComponentDialog (RG061/RG062)
- [x] SU004 — Création d'une relation State-Event (mode rubber band, RG054/RG058)
- [x] SU004 — Suppression d'une relation avec confirmation
- [x] Nettoyage des layouts obsolètes lors d'une sauvegarde par écrasement (delete_stale_layouts)
- [x] Conception — SU008/SU009 : associations agent-état et vue agents (user stories, règles RG063-RG067, features FN030-FN032, interface, menu — FR/EN)
- [x] Conception — Mise en cohérence des spécifications (périmètre MVP agents, trois composants, onglets Parcours/Agents, reliquats retirés)
- [x] Journalisation des actions sur les données du projet (config log_level dans config.json)
