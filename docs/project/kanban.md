# Planoscript ::: Suivi de projet (Kanban)

- **Version** : 7
- **Date** : 26-10-2026
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
EPC03 layout : TSK11 → TSK12
EPC04 : TSK15 → TSK13
```

---

## To do

- [ ] **EPC04 — Révision de la mécanique de gestion des agents et des associations avec les états**
- [ ] TSK14 — Barre latérale gauche de contrôle (création des agents, des états, des événements et des relations) → #TSK11
- [ ] TSK16 — Paramétrer dans config.json les dimensions de la vue Journey actuellement en constantes de classe (taille/marge des ports `base_node.py`, diamètre/marge du badge `state_node.py`, largeur de zone cliquable `connection.py`)

- [ ] SU003 — Duplication d'un composant (FN016)
- [ ] SU003 — Rattachement des composants aux parcours (FN019) → #SU005
- [ ] SU004 — Éditer une relation : annotation via panneau de propriétés (FN021)
- [ ] SU005 — Gérer un parcours narratif (FN023 à FN027 — à découper avant passage en Doing)
- [ ] SU006 — Zoom de l'espace de visualisation
- [ ] SU007 — Export de lecture « par événements »
- [ ] SU007 — Export technique pour réimport → #import de carte (hors périmètre)


## Doing

- (aucune tâche en cours)

## En revue

- [ ] TSK13 — Révision de la mécanique de création et d'édition des agents, et de l'association états-agents (EPC04 → #TSK15, TSK15 Done) — 7 points TSC implémentés ; **retours de test TSC du 28-10-2026 traités** : (1) badges d'évènement déplacés de la vue Journey vers les cartes d'état de la vue Agents, (2) menu Agent différencié selon la vue + sélection des cartes avec contour pointillé, (3) confirmation SU003 suppression State/Event en vue Journey — tests 106 passed + 10 offscreen PASSED (détail dans `tasks/TSK13_agent_mechanics_review.md`)

## Done

- [x] TSK15 — Révision de l'implémentation de la matrice d'association des agents aux états (EPC04, vue Agents : QGraphicsView, cartes style Journey 80×40, cases 20×20, grille 120×80 centrée, RG068 conservé — détail dans `tasks/TSK15_agents_matrix_revision.md`) — validée TSC le 28-10-2026 (3 revues : QGraphicsView, grille 120×80 + espace extensible, libellés 9 pt)

- [x] TSK12 — Finalisation de la révision du layout — 12 points de la revue visuelle TSK11 + 2 correctifs de revue (carré bas-gauche, cases de la matrice) + en-têtes non redimensionnables — validée TSC le 26-10-2026 (détail dans `tasks/TSK12_layout_finalization.md`)
- [x] TSK11 — Révision esthétique du layout (charte `docs/specification/98_layout_revision-FR.md`, maquette `97_layout_revision-EN.svg` — détail dans `tasks/TSK11_layout_revision.md`) — thème sombre implémenté et validé en revue visuelle par TSC ; finalisation des points restants transférée à TSK12
- [x] TSK10 — Navigation croisée entre vues avec focus RG067 (EPC03, SU009/FN032) — deux sens, Échap/clic relâchent, aucune persistance ni marquage modifié (détail dans `tasks/TSK10_cross_view_navigation.md`)
- [x] TSK09 — Édition des cellules de la matrice (EPC03, SU008/FN030) — cellClicked → use cases, signal associationChanged, symétrie parcours/matrice (détail dans `tasks/TSK09_matrix_cell_edition.md`)
- [x] TSK08 — Affichage de la matrice agents × états en lecture seule (EPC03, SU009) — QTableWidget, ordre RG068 persisté, rafraîchissement croisé (détail dans `tasks/TSK08_agents_matrix.md`)
- [x] TSK07 — Bascule d'espace de travail (EPC03, SU009) — TabBar Journey/Agents, QStackedWidget, placeholder vue agents (détail dans `tasks/TSK07_workspace_tabs.md`)
- [x] TSK06 — Règle de gestion de l'ordre des colonnes de la matrice (EPC03, conception) — RG068 rédigée (FR/EN), SU009 mise à jour (détail dans `tasks/TSK06_matrix_column_order.md`)
- [x] TSK05 — Badges d'agents sur les nodes d'état (EPC02, FN030) — pastille unique compteur bas-droit non interactive, infobulle, rafraîchissement (détail dans `tasks/TSK05_agent_badges.md`)
- [x] TSK04 — Dialogue « Associer des agents... » (EPC02, FN030) — liste à cocher à application immédiate, création d'agent intégrée, double point d'entrée (détail dans `tasks/TSK04_agent_association_dialog.md`)
- [x] TSK03 — Use case d'association agent-état sans UI (EPC02, FN030) — RG063 idempotente, dissociation, cascade RG065 (détail dans `tasks/TSK03_agent_state_association.md`)
- [x] TSK02 — Supprimer un agent avec confirmation et cascade RG064 (EPC01, FN031) — confirmation UI, message d'information, tests unitaires (détail dans `tasks/TSK02_agent_delete.md`)
- [x] TSK01 — Créer et modifier un agent (EPC01, FN031) — création/édition via dialogues, tests unitaires et persistance (détail dans `tasks/TSK01_agent_create_edit.md`)
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

- [x] **EPC01 — Gérer les agents du projet** (FN031, SU008/SU009)
  - [x] TSK01 — Créer et modifier un agent : entité Agent portée par le projet, identifiant unique projet, type (sujet/objet), réactivation de l'entrée de menu, dialogue d'édition
  - [x] TSK02 — Supprimer un agent avec confirmation et suppression en cascade des associations agent-état (RG064) → #TSK01
- [x] **EPC02 — Associer des agents à un état** (FN030, SU008)
  - [x] TSK03 — Use case d'association agent-état : associer/dissocier, unicité (RG063), cascades (RG064/RG065) — sans UI → #TSK01
  - [x] TSK04 — Dialogue « Associer des agents... » depuis le menu contextuel d'un état (liste à cocher, création d'agent intégrée) → #TSK01, #TSK03
  - [x] TSK05 — Badges d'agents sur les nodes d'état dans la vue parcours (affichage + rafraîchissement) → #TSK03
- [x] **EPC03 — Implémenter la vue agents** (SU009, second espace de travail, onglet « Agents »)
  - [x] TSK06 — Déterminer la règle de gestion de l'ordre des colonnes de la matrice (conception ; à ajouter aux règles de gestion avant implémentation)
  - [x] TSK07 — Bascule d'espace de travail : barre d'onglets Parcours ↔ Agents
  - [x] TSK08 — Affichage de la matrice agents × états en lecture seule → #TSK06, #TSK07
  - [x] TSK09 — Édition des cellules de la matrice (cocher/décocher → use case d'association) → #TSK08, #TSK03
  - [x] TSK10 — (P2) Navigation croisée entre vues avec focus (RG067) → #TSK08
