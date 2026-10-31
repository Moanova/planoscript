# Conception — Rattachement des relations (arcs et associations agent-état) aux parcours

- **Date** : 29-10-2026
- **Statut** : validé TSC 29-10-2026 (décisions actées en séance)
- **Contexte** : EPC05 (SU005, FN023–FN027), préparation de TSK22–TSK25
- **Spécifications impactées** : RG026, RG027, RG031, RG052, RG066 (révisée), RG029, RG055, RG058 ; FN019, FN027, FN029 ; modèle de données `07_data_model-FR/EN.json` (`Journey_node.state_agent_rel_id` ajouté)

---

## 1. Vocabulaire

- **Composant** : entité `State`, `Event` ou `Agent`.
- **Arc** (terme des règles de gestion) = une instance de `State_to_event` (sortant d'un état : S → E) ou de `Event_to_state` (entrant dans un état : E → S). Dans l'UI, c'est l'objet `Connection`.
- **Connexion** (terme UI) = l'action de l'utilisateur créant un arc entre deux composants ; un seul arc est créé par connexion, son type dépend du sens (source → cible).
- **Association agent-état** = une instance de `State_agent_rel`.
- **Parcours** = entité `Journey` ; `Journey_node` = table de liaison entre un parcours et un arc (ou une association agent-état).

La direction d'un arc est portée par la table, pas par un champ : depuis un état S, `State_to_event.state_id = S` donne les événements suivants, `Event_to_state.state_id = S` les événements précédents (et symétriquement depuis un événement). Aucun champ de direction supplémentaire n'est nécessaire.

### Normalisation des termes (actée TSC 29-10-2026, complétée TSC 31-10-2026 ; audit complet dans TSK26)

- **arc** : objet métier directionnel du modèle de données (`State_to_event` / `Event_to_state`) — terme des règles RG054+ ; utilisé dans le code (`ArcService`).
- **connexion** : objet visuel de la couche UI (classe `Connection`, `ConnectionLayout`) — la ligne entre deux nœuds ; « connexion (tracé temporaire) » désigne aussi le tracé en cours de création (SU004/FN020).
- **association** : objet métier `State_agent_rel` (code : `AssociateAgentStateUseCase`...).
- **relation** : terme chapeau réservé aux spécifications et aux menus (arc ∪ association) ; à ne plus utiliser pour désigner un objet précis dans le code. Exception : le type d'état "Relation" (`State.typ`) conserve ce terme.
- **composant / nœud** (TSC 31-10-2026) : composant = objet métier (agent au niveau projet ; état/événement au niveau carte narrative) ; nœud = objet graphique (classe `*Node`).
- **arc / ports** (TSC 31-10-2026) : prédécesseur/successeur pour la direction d'un arc ; entrant/sortant pour les ports (gauche/droite).

## 2. Principes retenus

1. **Les arcs ne sont créés que par connexion utilisateur** (tracé temporaire sur la connexion). Pas de création implicite d'arc à la création d'un State/Event (l'ancien mécanisme `State_node(from_event_id=0, …)` a été supprimé le 03-10-2026, commit 5ddbcb1).
2. **Objets orphelins acceptés** : un composant non connecté n'a aucun arc, donc aucun `Journey_node` ; il est invisible quand le filtre parcours est actif (FN029), visible sinon.
3. **`Journey_node` est la seule table de liaison** vers les parcours. Aucun champ `journey_ids` sur State/Event : l'appartenance d'un composant à un parcours est **dérivée** (un composant appartient à un parcours ssi au moins un de ses arcs y est rattaché par un nœud).
4. **Rattachement explicite par l'utilisateur sur la connexion** (menu Edit de la connexion, liste à choix multiple des parcours — RG027/FN019 repositionnées de la propriété du composant vers la connexion). Un arc peut appartenir à **1 ou n parcours** : n `Journey_node` référençant le même arc.
5. **Rattachement automatique au parcours actif** : à la création d'une connexion (ou d'une association agent-état), un `Journey_node` est créé dans le parcours actif (`NarrativeMap.active_journey_id`, à ajouter — TSK22), référençant l'arc (`state_to_event_id` / `event_to_state_id`) ou l'association (`state_agent_rel_id`).
6. **Nœud partiel valide** : chaque champ d'arc de `Journey_node` peut être `null` indépendamment (déjà prévu pour l'état initial / l'état final) ; un nœud avec un seul champ renseigné est normal.
7. **Suppression d'une connexion** = suppression de l'arc + de tous les `Journey_node` qui le référençaient (RG056). Les composants restent, éventuellement orphelins.
8. **Suppression d'un parcours** (TSK25) : les arcs et associations restent ; leurs `Journey_node` orphelins basculent vers le parcours par défaut (RG029, RG066 révisée). Dernier parcours non supprimable (RG055).
9. **RG058 inchangée** : pas de paire d'arcs forward/backward ; un cycle direct S→E→S reste interdit.

## 3. Exemple de référence

Carte : `S1(Initial) —a1→ E1 —a2→ S2 —a3→ E2 —a4→ S3(Final)`, avec a1, a3 dans `State_to_event` et a2, a4 dans `Event_to_state`. Parcours J1 = chemin complet, J2 = branche S1→E1→S2.

`Journey_node` (un nœud par arc rattaché à un parcours) :

| id | journey_id | state_to_event_id | event_to_state_id | state_agent_rel_id | sequence_order |
|---|---|---|---|---|---|
| n1 | J1 | a1 | null | null | 1 |
| n2 | J1 | null | a2 | null | 2 |
| n3 | J1 | a3 | null | null | 3 |
| n4 | J1 | null | a4 | null | 4 |
| n5 | J2 | a1 | null | null | 1 |
| n6 | J2 | null | a2 | null | 2 |

- a1 appartient à J1 et J2 (n1, n5) : 1 arc dans n parcours. ✓
- S2 ∈ J1 (via n2/n3) et ∈ J2 (via n6) : appartenance dérivée. ✓
- S3 ∈ J1 uniquement (via n4). Un composant peut n'appartenir qu'à un sous-ensemble des parcours.
- Retrait de a2 de J2 (décocher la connexion a2 dans J2) : suppression de n6 ; S2 sort de J2 s'il n'y reste aucun autre arc.

## 4. Réécriture des règles (à faire dans TSK22, FR/EN)

- **RG026** (nouvelle rédaction) : une relation (arc ou association agent-état) appartient aux parcours des `Journey_node` qui la référencent (1 à n). L'appartenance d'un composant à un parcours est dérivée : au moins un de ses arcs y est rattaché. Un composant non connecté (orphelin) n'appartient à aucun parcours et n'est visible que hors filtre parcours (FN029).
- **RG027** : le rattachement d'une relation aux parcours se gère via une liste à choix multiple **sur la connexion** (menu Edit de la connexion), parmi les parcours existants ; désactivée si un seul parcours existe.
- **RG031** : l'état initial participe à tous les parcours existants par l'intermédiaire de ses rattachements (ses arcs sortants rattachés aux différents parcours).
- **RG052** : le rattachement d'un arc à un parcours s'effectue à la création de la connexion (nœud créé dans le parcours actif) et/ou via le menu Edit de la connexion ; aucun nœud n'est créé pour un composant isolé.

## 5. Impacts code (TSK22 et suivants)

- `Journey_node.state_agent_rel_id: Optional[int]` à ajouter dans `src/core/models/data_model.py` (déjà dans les specs JSON).
- `NarrativeMap.active_journey_id: Optional[int]` à ajouter (parcours actif, RG022/RG023), persisté en JSON.
- Use cases TSK22 : créer/renommer/activer un parcours ; rattacher/détacher un arc ou une association à un parcours (création/suppression de `Journey_node`) ; création automatique du nœud au parcours actif lors de `ArcService.create_arc` et de la création d'un `State_agent_rel`.
- Cascade RG056 étendue aux `Journey_node` référençant l'arc supprimé.
- `sequence_order` : sémantique exacte à affiner au traitement de la tâche concernée (focus prévu).
- Nœud partagé (arc + `state_agent_rel_id` sur le même nœud) : à discuter au traitement de la tâche (prévu : impossible en pratique, un nœud = une appartenance).

## 6. Hors périmètre

- Pas de création implicite d'arcs à la création des composants.
- Pas de champ d'appartenance sur State/Event/Agent.
- Pas de détection de cohérence narrative (enchaînements brisés) — hors MVP (99_mvp_scope).
- Schéma `dataModel.drawio/svg` mis à jour séparément par TSC (commit eb03f6f).
