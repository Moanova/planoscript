# TSK13 — Révision de la mécanique de création et d'édition des agents, et de l'association états-agents

- **Épic** : EPC01/EPC02 (gestion des agents, associations)
- **Statut** : En revue (implémentation + 3 retours de test TSC traités le 28-10-2026, attente validation TSC)
- **Date de création** : 24-10-2026
- **Dépendances** : TSK15 (Done)

## Périmètre

Revue de la mécanique fonctionnelle (hors esthétique) de :

1. **Création et édition des agents** — dialogue `AgentDialog`
   (TSK01, FN031), gestion des agents `AgentManagementDialog`
   (`Project > Manage agents`), création d'agent intégrée au dialogue
   d'association (TSK04).
2. **Association états-agents** — dialogue « Associer des agents... »
   (TSK04), édition des cellules de la matrice agents × états (TSK09),
   badges sur les nœuds d'état (TSK05).

Cadrage TSC reçu le 28-10-2026 (7 points, validés et complétés en revue) :

1. **Sous-menu « Project > Components... > Agent »** (New... / Edit / Delete),
   comparable aux sous-menus State et Event :
   - « New... » ouvre directement le dialogue « New Agent » (`AgentDialog`,
     création) ; retour à l'espace de travail à la validation.
   - « Edit » ouvre un nouveau dialogue de sélection `AgentSelectionDialog`
     (liste des agents, boutons Ok/Cancel, Ok désactivé sans sélection) ;
     Ok ouvre `AgentDialog` pré-rempli sur l'agent sélectionné.
   - « Delete » ouvre le même `AgentSelectionDialog` ; Ok supprime l'agent
     avec confirmation (message RG064 avec nombre d'associations).
   - Activation : « New... » actif dès qu'un projet est ouvert ; « Edit » et
     « Delete » actifs dès qu'au moins un agent existe (la sélection se fait
     dans le dialogue, pas dans l'espace de travail). Menu global : accessible
     des vues Journey et Agents.
2. **Menu contextuel vue Journey** (clic sur la grille) : ajout de l'entrée
   « New Agent » → `AgentDialog` (création), reste dans la vue Journey.
3. **Bascule vers la vue Journey après création d'un évènement** : lorsque
   « New Event » est déclenché (menu global « Project > Components... >
   Event > New... » ou menu contextuel de la grille Agents, point 6) alors
   que la vue Agents est active, la vue bascule sur Journey et l'évènement
   créé est sélectionné. La création d'un état ne bascule pas (la colonne
   apparaît dans la matrice au rafraîchissement).
4. **Menu contextuel carte agent (vue Agents)** : « Edit Agent » (ouvre
   `AgentDialog` pré-rempli), « Delete Agent » (confirmation RG064), « Show
   in journey view » (TSK10, conservé).
5. **Menu contextuel carte état (vue Agents)** : « Edit State » (ouvre
   `ComponentDialog` pré-rempli), « Delete State » (désactivé pour l'état
   initial, RG031 ; confirmation et cascades arcs + RG065), « Show in
   journey view » (nouveau : bascule vers Journey et met le focus sur le
   node de l'état — extension du contrat de focus TSK10/RG067).
6. **Menu contextuel grille Agents** (clic droit hors matrice) : « New
   Agent » (création, reste dans la vue Agents), « New State » (création,
   reste dans la vue Agents), « New Event » (création puis bascule Journey,
   point 3).
7. **Badges d'événements sur les nœuds State (vue Journey)** — **point
   abandonné en revue TSC (28-10-2026, retour n°1)** : les badges
   d'évènement sont retirés de la vue Journey (les connexions y sont
   visibles, les badges surchargeaient les objets). Implémentation
   initiale complète (deux badges pastille + compteur, cuivre
   `event_badge_bg_color` #D19A66, `EventBadgeService`, refresh
   dynamique), puis **suppression complète** du code, des tests et de
   la configuration (`event_badge_bg_color` retiré de config.json) ;
   seuls les badges d'agents (TSK05) restent sur les nœuds State.

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
- 28-10-2026 : cadrage TSC reçu (7 points, complété en revue : coquille point 05
  corrigée en Edit State/Delete State ; activation du sous-menu Agent, bascule
  Journey, badges cuivre actés). Implémentation des 7 points : sous-menu
  Agent New.../Edit/Delete + `AgentSelectionDialog` (`AgentManagementDialog`
  supprimé), « New Agent » menu contextuel grille Journey, bascule Journey +
  sélection après création Event depuis la vue Agents (menu global et
  contextuel), menus contextuels cartes agent/état et grille en vue Agents
  (Edit/Delete/Show in journey view ; Delete State désactivé pour l'état
  initial RG031, cascade RG065 ; focus état→parcours via
  `focusStateInJourneyViewRequested`), badges d'évènement source/cible sur les
  nœuds State (`EventBadgeService`, cuivre `event_badge_bg_color` #D19A66,
  refresh dynamique). Tests : 106 passed (pytest) + 10 offscreen PASSED
  (`offscreen_tsk13_agent_mechanics.py` couvre les 7 points). Documentation :
  `04_interface` FR/EN v2.2, `03_features` FR/EN v2.2, `05_menu-EN.yaml` v2.2,
  `98_layout_revision-FR.md` (badges d'évènement). Kanban : Doing → En revue.
- 28-10-2026 (revue TSC, 3 retours) : **retour n°1** — badges d'évènement
  retirés de la vue Journey (suppression complète : `EventBadgeService`,
  `event_badge_in/out` de `StateNode`, `refresh_event_badges` de
  `JourneyWorkspace`, config `event_badge_bg_color`, tests, doc) ; **retour
  n°2** — sous-menu Agent différencié selon la vue (vue Parcours : dialogues
  avec libellé par défaut « Agent {id} » éditable ; vue Agents : création
  directe, édition/suppression directes de la carte sélectionnée, grisé sans
  sélection) + sélection des cartes en vue Agents (clic = sélection avec
  contour pointillé teinte du type, drag RG068 maintenu, clic droit =
  sélection + menu, signal `cardSelectionChanged`) + alignement du menu
  contextuel carte agent sur le menu général ; **retour n°3** — confirmation
  SU003 en vue Journey (State : arcs + associations agents ; Event : arcs),
  factorisée dans `_confirm_component_deletion` partagée avec la vue Agents.
  Tests : 95 passed (pytest) + 10 offscreen PASSED. Kanban : Doing (retours
  en cours de traitement).
