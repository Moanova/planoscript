# Conception — Filtre d'affichage par parcours (FN029, RG042, SU006)

- **Date** : 31-10-2026
- **Statut** : conception proposée (TSK27) — à valider TSC
- **Contexte** : EPC05 (SU005/SU006), fondations en place (TSK22–TSK25) ;
  rattachement des relations aux parcours via `Journey_node`
  (`docs/conception/journey_attachment.md`)
- **Spécifications impactées** : FN029, RG026, RG042, RG067, SU006 ;
  `04_interface`, `05_menu` ; `view_model.WorkspaceLayout`

---

## 1. Rappel du besoin (FN029 / RG042)

À tout moment, soit **tous** les composants et relations de la carte sont
affichés, soit **seulement ceux du parcours actif**. La bascule d'un parcours
à l'autre met à jour l'affichage instantanément. Le filtrage ne marque pas
la carte comme modifiée.

## 2. Sémantique de visibilité (décision proposée)

La visibilité est **dérivée du modèle** (RG026), jamais stockée :

- **Filtre actif (parcours J actif)** :
  - visibles : les relations (arcs `State_to_event`/`Event_to_state` et
    associations `State_agent_rel`) possédant un `Journey_node` dans J ;
  - visibles : les composants (State/Event) auxquels au moins une de ces
    relations donne appartenance (dérivation RG026) ;
  - masqués : relations des autres parcours, composants n'appartenant qu'à
    d'autres parcours, et **composants orphelins** (sans aucune relation).
- **Filtre désactivé (« tous les parcours »)** : tout est visible, y compris
  les orphelins.

Implémentation UI : `setVisible(bool)` sur les `BaseNode` et `Connection`
de la vue Events. Aucun changement du modèle ni des layouts : le filtre est
un état purement visuel de la scène.

## 3. État du filtre et persistance (décision proposée)

- **État** : `journey_filter_active: bool` + parcours actif existant
  (`NarrativeMap.active_journey_id`, RG022/RG023). Valeur par défaut à
  l'ouverture d'un projet : **filtre actif** (cohérent avec SU006 : « un
  filtre de parcours permet d'afficher soit tous les parcours, soit le
  parcours sélectionné » — le parcours actif est le mode de travail par
  défaut, le mode « tout afficher » sert à auditer la carte complète).
- **Persistance** : **non persisté entre les sessions**, comme le zoom et
  la position des scrollbars (RG041 : ces états de visualisation ne sont pas
  des données métier). Stocké en mémoire uniquement (attribut de
  `EventsWorkspace`), pas dans `WorkspaceLayout` ni dans `user_state.json`.
  *Question ouverte TSC* : persister le filtre dans `user_state.json`
  (état applicatif global) pour rouvrir l'application dans le même mode ?
  Recommandation : non (RG041 élargi aux états de visualisation).
- **Activation/désactivation** : le filtre s'applique au **parcours actif** ;
  activer un autre parcours (JourneyList, FN026) met à jour l'affichage si
  le filtre est actif.

## 4. Point d'entrée UI (décision proposée)

- `Display > Journey > JourneyList` (TSK23) : ajouter en tête de la liste
  dynamique une entrée cochable **« All journeys »** (checkable, cochée
  quand le filtre est désactivé). Cocher un parcours de la liste =
  activer ce parcours **et** le filtre ; cocher « All journeys » =
  désactiver le filtre (le parcours actif reste actif pour l'édition,
  RG052).
- La coche reflète l'état : « All journeys » cochée ⇔ filtre off ; sinon
  c'est le parcours actif qui est coché.
- Aucun raccourci clavier ajouté en MVP.

## 5. Interaction avec la vue Agents

- La matrice agents × états affiche **toutes** les associations de la carte,
  quel que soit le filtre (SU009 : la vue agents est un espace de travail
  indépendant du graphe des enchaînements). Les associations restent
  rattachées aux parcours (RG066) mais la matrice n'est pas filtrée.
  *Question ouverte TSC* : filtrer les colonnes (états) de la matrice sous
  filtre actif ? Recommandation : non — la matrice sert justement à voir
  l'ensemble des associations hors contexte de parcours.

## 6. Interaction avec l'édition sous filtre actif

- **Création d'un composant** : le node est créé isolé (aucun `Journey_node`,
  RG024) → **invisible sous filtre actif** jusqu'à sa première connexion.
  Comportement retenu : la création bascule automatiquement le filtre sur
  « tous les parcours » le temps de la connexion, ou affiche un message
  d'information (« le nouveau composant n'est visible qu'en désactivant le
  filtre parcours »). Recommandation : message dans la barre d'info, pas de
  bascule automatique (le filtre est un choix explicite de l'utilisateur).
- **Création d'une relation** : arc créé + `Journey_node` dans le parcours
  actif (RG052) → la connexion et les deux composants deviennent visibles
  instantanément (ils appartiennent désormais au parcours actif).
- **Suppression d'une relation / d'un composant** : recalcul de la
  visibilité (un composant peut redevenir orphelin → masqué sous filtre).
- **Navigation croisée (RG067)** : le focus reste un état visuel temporaire ;
  s'il cible un élément masqué par le filtre, basculer d'abord sur « tous
  les parcours » puis appliquer le focus (sinon le focus serait invisible).

## 7. Rafraîchissement

- Un point d'entrée unique `EventsWorkspace.apply_journey_filter()` :
  recalcule la visibilité de chaque node/connection à partir du modèle
  (relations du parcours actif → composants dérivés ; le reste masqué).
  Appelé après : activation d'un parcours, bascule du filtre, création/
  suppression de relation, rattachement/détachement (RG027), suppression de
  composant, chargement de projet.
- Coût : O(nodes + relations), négligeable jusqu'à 100 composants (SU006).

## 8. Impacts code prévus (prochaine tâche d'implémentation)

- `EventsWorkspace` : attribut `journey_filter_active`, méthode
  `apply_journey_filter()`, appels aux points de rafraîchissement existants.
- `MainWindow._rebuild_journey_list_menu` : entrée « All journeys » ;
  `_activate_journey` déclenche le recalcul si le filtre est actif.
- `view_model` : **aucun** champ ajouté (état visuel uniquement).
- Specs : FN029 passe de « Non documenté » à « Implémenté » ; `05_menu`
  documente l'entrée « All journeys » ; `04_interface` section 6.
- Tests : `tests/test_visualization/test_journey_filter.py` (visibilité
  dérivadaire, orphelins, bascule, persistance refusée) + test offscreen.

## 9. Hors périmètre

- Filtrage partiel multi-parcours (sélection de plusieurs parcours à
  afficher) — hors MVP (RG042 : soit tous, soit un seul).
- Cohérence narrative (enchaînements brisés) — hors MVP (SU005).
