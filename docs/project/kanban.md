# Planoscript ::: Suivi de projet (Kanban)

- **Version** : 18
- **Date** : 31-10-2026
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
EPC05 : TSK22 → TSK23 / TSK24 → TSK25
```

---

## To do

- [ ] TSK14 — Barre latérale gauche de contrôle (création des agents, des états, des événements et des relations) → #TSK11

- [ ] SU006 — Zoom de l'espace de visualisation
- [ ] SU007 — Export de lecture « par événements »
- [ ] SU007 — Export technique pour réimport → #import de carte (hors périmètre)


## Doing

- (aucune tâche en cours)

## En revue

- [x] TSK16 — Dimensions de la vue Events dans config.json (`events_view_port_size_px`, `events_view_port_margin_px`, `events_view_badge_diameter_px`, `events_view_hit_area_width_px`) — `base_node.py`/`state_node.py`/`connection.py` lisent config avec défauts identiques — py_compile OK — fiche `tasks/TSK16_config_dimensions.md`
- [x] TSK28 — Duplication d'un composant (SU003/FN016) : `DuplicateComponentUseCase` (nouvel id RG020, libellé « {lb} (copy) », attributs hérités, copie isolée sans Journey_node RG024/RG052, refus de l'état initial RG062, position +1 cran de grille à droite) + entrées « Duplicate » dans Project›Components...›State/Event et menus contextuels (désactivées pour l'état initial) — tests +15 (exécutés manuellement 15/15 PASS ; pytest non installable dans le sandbox) — fiche `tasks/TSK28_component_duplication.md`
- [x] TSK26 — Normalisation du vocabulaire (étape 1) : ordre des clés `Journey_node` inversé (`state_to_event_id` avant `event_to_state_id`, vérifié en round-trip JSON) + `07_data_model-FR/EN.json` mis à jour ; audit partiel : paramètre `relation`→`arc` dans `UpdateRelationUseCase.execute`, `arc_or_association` dans `ArcService.attach_to_active_journey` — py_compile OK — fiche `tasks/TSK26_vocabulary_normalization.md` (audit complet à poursuivre)
- [x] TSK27 — Conception du filtre d'affichage par parcours (FN029/RG042) : note `docs/conception/journey_filter.md` (visibilité dérivée RG026, état non persisté RG041, entrée « All journeys » dans Display›Journey›JourneyList, vue Agents non filtrée, comportements d'édition sous filtre) — FN029 « Conçu » FR/EN, 05_menu mis à jour — fiche `tasks/TSK27_journey_filter_conception.md`

## Done

- [x] **EPC05 — Gérer un parcours narratif** (SU005, FN023 à FN027) — TSK21–TSK25 terminées — conception retenue et validée TSC 29-10-2026 : `Journey_node` est la table de liaison, le rattachement se fait sur les connexions (arcs) et non sur les composants, l'appartenance est dérivée des noeuds, aucun champ `journey_ids` sur State/Event, objets orphelins acceptés (invisibles sous filtre parcours) — note de conception : `docs/conception/journey_attachment.md` — validée TSC le 30-10-2026 (TSK26, normalisation du vocabulaire, déplacée en tâche autonome hors épic ; FN019 répositionnée sur la connexion, ligne SU003 retirée du To do)

- [x] TSK25 — Suppression d'un parcours (FN027 : dernier parcours non supprimable (RG018), nœuds orphelins basculés vers le parcours par défaut incl. `state_agent_rel_id` (RG036/RG066), default/actif réattribués (RG055)) → #TSK22, #TSK24 — use case `DeleteJourneyUseCase` + entrée dédiée `Project › Journeys... › Delete...` (sélection Ok/Cancel + confirmation, refus du dernier parcours — UX review 30-10-2026 : plus de bouton Delete dans la sélection Edit) — tests +11 (165 passed, 3 skipped) + offscreen PASSED — détail dans `tasks/TSK25_journey_deletion.md` — validée TSC le 30-10-2026

- [x] TSK21 — Scénario SU004 (FN021) : édition des relations (note + rattachement aux parcours via la liste des parcours sur la connexion/association) — arcs via menu contextuel « Edit Relation » de la connexion (vue Events) et menu Project › Relations... › Edit, State_agent_rel via clic droit « Annotate association... » sur case cochée (vue Agents), infobulle note au survol de la connexion — détail dans `tasks/TSK21_relation_annotation_edition.md` — tests 165 passed (+14 au passage de la tâche) — validée TSC le 30-10-2026

- [x] TSK24 — Duplication d'un parcours (FN025 : nouvel id, nom distinctif « {lb} (copy) », nœuds de parcours du source copiés vers la copie, copie ni activée (RG023 révisée) ni par défaut (RG055)) → #TSK22 — use case `DuplicateJourneyUseCase` + menu `Project › Journeys... › Duplicate...` + `JourneyDialog.default_note` — tests +13 (154 passed, 3 skipped) + offscreen PASSED — détail dans `tasks/TSK24_journey_duplication.md` — validée TSC le 30-10-2026

- [x] TSK22 — Fondations parcours (EPC05) : `active_journey_id` + `Journey_node.state_agent_rel_id` dans le modèle, use cases `journey_management` (create/update/activate, attach/detach), rattachement auto au parcours actif, cascades étendues, règles RG026/RG027/RG031/RG052 réécrites FR/EN — détail dans `tasks/TSK22_journey_foundations.md` — conception : `docs/conception/journey_attachment.md` — tests 127 passed (+17) — validée TSC le 29-10-2026

- [x] TSK23 — UI de gestion des parcours : `Display › Journey › JourneyList` remplace `Display › Events` (liste cochable dynamique, parcours actif) + entrées `Project › Journeys...` New.../Edit (FN023/FN024, Delete stub → TSK25) → #TSK22 — détail dans `tasks/TSK23_journey_ui.md` — validée TSC le 29-10-2026 (5 revues traitées)
- [x] TSK18 — Ajustement esthétique : badges d'événement des cartes d'état (vue Agents) 2/3 dedans / 1/3 dehors sur l'axe horizontal (5 px dehors sur 16, même règle que l'axe X du badge d'agents de la vue Events, TSK17) — détail dans `tasks/TSK18_event_badge_position.md` — tests 106 passed + 10 offscreen PASSED + rendu QImage vérifié — validée TSC le 29-10-2026
- [x] TSK20 — Modèle de données : clé `content` après `note` dans Agent/State/Event, clé `note` ajoutée à Event_to_state/State_to_event (State_agent_rel inchangé) + impacts code (dialogues Note/Content, use cases, tests) + doc — détail dans `tasks/TSK20_data_model_content_note.md` — tests 110 passed + 10 offscreen PASSED + round-trip JSON vérifié — validée TSC le 29-10-2026
- [x] TSK19 — Renommage de la vue « Journey » en vue « Events » (cohérence avec la vue « Agents » : les états sont centraux dans les deux vues) — renommage couche UI uniquement (`EventsWorkspace`, onglet « Events », menus, signaux, tests) ; la couche métier `Journey`/`Journey_node` (parcours narratif, clés JSON) est conservée — détail dans `tasks/TSK19_rename_journey_view.md` — tests 106 passed + 10 offscreen PASSED — validée TSC le 29-10-2026
- [x] TSK17 — Ajustement esthétique : badge d'agents des nœuds d'état (vue Journey) centré sur le coin bas-droit, à cheval sur les bords X et Y du contour (comme les badges d'évènement de la vue Agents, TSK13) — détail dans `tasks/TSK17_agent_badge_position.md` — validée TSC le 28-10-2026 (2 revues : centrage à cheval sur le coin, puis ratio 2/3 dedans / 1/3 dehors)
- [x] TSK13 — Révision de la mécanique de création et d'édition des agents, et de l'association états-agents (EPC04 → #TSK15, TSK15 Done) — 7 points TSC implémentés ; retours de test TSC du 28-10-2026 traités ; **repositionnement des badges d'évènement traité** (centrés verticalement, à cheval sur les bords G/D des cartes d'état — mêmes coordonnées que les ports de connexion de la vue Journey, validé TSC) — détail dans `tasks/TSK13_agent_mechanics_review.md` — validée TSC le 28-10-2026 (3 retours de test + correction retour n°01 + repositionnement des badges d'évènement)

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
- [x] **EPC04 — Révision de la mécanique de gestion des agents et des associations avec les états** (TSK15 → TSK13, toutes deux validées TSC le 28-10-2026)
  - [x] TSK15 — Révision de l'implémentation de la matrice d'association des agents aux états (QGraphicsView, cartes 80×40, cases 20×20, grille 120×80) → validée TSC le 28-10-2026
  - [x] TSK13 — Révision de la mécanique de création/édition des agents et de l'association états-agents (7 points + retours de test + repositionnement des badges d'évènement) → validée TSC le 28-10-2026
