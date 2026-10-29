# Planoscript ::: Spécification de l'interface utilisateur

## Version du document
- **Version** : 2.2
- **Date** : 28-10-2026
- **Statut** : Mise à jour rétrospective reflétant l'implémentation actuelle (dernier redesign + EPC01–EPC04 : gestion des agents, associations agent-état, vue agents ; TSK13 : révision mécanique création/édition agents et associations)

---

## Architecture générale de l'interface

### Disposition
- **Type** : Disposition verticale principale (QVBoxLayout) avec des sections distinctes.
- **Structure** :
  - **Haut** : Barre de menus intégrée (QMenuBar).
  - **Centre** : Espace de travail principal (EventsWorkspace).
  - **Bas** : Barre d'informations (75 %) + Barre de zoom (25 %) — *Barre de zoom actuellement désactivée*.

> **Note** : Les barres latérales (composants à gauche, parcours à droite) sont implémentées mais **non intégrées** à la fenêtre principale.

---

## Composants de l'interface

### 1. Barre de menus de la fenêtre d'application
- **Type** : QMenuBar native.
- **Position** : En haut de la fenêtre.
- **Style** :
  - Arrière-plan : `#ffffff` (blanc).
  - Police : Arial, 9 pt.
  - Couleur du texte : `#000000` (noir).
  - Éléments sélectionnés : Arrière-plan `#404040`, texte `#ffffff`.

- **Menus disponibles** :
  - **Fichier** :
    - Nouveau projet... (Ctrl+N)
    - Ouvrir... (Ctrl+O)
    - Fermer (Ctrl+W)
    - Enregistrer (Ctrl+S) — Désactivé si le projet n'est pas modifié
    - Enregistrer sous... (Ctrl+Shift+S)
    - Exporter la carte — Non implémenté
    - Importer une carte — Non implémenté
    - Projets récents... — Non implémenté
    - Quitter (Ctrl+Q)
  
  - **Édition** :
    - Annuler (Ctrl+Z) — Non implémenté
    - Rétablir (Ctrl+Y) — Non implémenté
    - Historique — Non implémenté
    - Couper (Ctrl+X) — Non implémenté
    - Copier (Ctrl+C) — Non implémenté
    - Coller (Ctrl+V) — Non implémenté
    - Supprimer (Suppr) — Non implémenté

  - **Affichage** :
    - **Events** :
      - EventsList — Non implémenté
    - **Zoom** :
      - Zoom avant (Ctrl+=) — Non implémenté
      - Zoom arrière (Ctrl+-) — Non implémenté
      - Réinitialiser (Ctrl+0) — Non implémenté

  - **Projet** :
    - **Vue** :
      - Events — Non implémenté (la vue est active via la barre d'onglets, pas via ce menu)
      - Agents — Non implémenté (la vue est active via la barre d'onglets ; SU009 ; les entrées Relations et Chapitres sont des reliquats retirés du MVP)
    - **Composants...** :
      - **Agent** :
        - Nouveau... — Fonctionnel, comportement selon la vue active (FN031, TSK13 + revue TSC 28-10-2026) :
          - Vue « Events » : ouvre directement le dialogue « New Agent », pré-rempli avec un libellé par défaut « Agent {id} » (comme les états/événements), éditable dans le dialogue.
          - Vue « Agents » : création directe d'un agent dans la ligne de la matrice, avec le libellé par défaut (pas de dialogue).
          - Actif dès qu'un projet est ouvert, dans les deux vues.
        - Éditer — Fonctionnel, comportement selon la vue active (TSK13 + revue TSC 28-10-2026) :
          - Vue « Events » : ouvre un dialogue de sélection de l'agent à éditer, puis le dialogue « New Agent » pré-rempli ; actif dès qu'au moins un agent existe (la sélection se fait dans le dialogue).
          - Vue « Agents » : ouvre directement le dialogue d'édition de l'agent dont la carte est sélectionnée ; grisé si aucune carte agent n'est sélectionnée.
        - Supprimer — Fonctionnel, comportement selon la vue active (TSK13 + revue TSC 28-10-2026) :
          - Vue « Events » : dialogue de sélection de l'agent à supprimer, puis confirmation indiquant le nombre d'associations supprimées en cascade (RG064) ; actif dès qu'au moins un agent existe.
          - Vue « Agents » : suppression directe de l'agent dont la carte est sélectionnée, avec la même confirmation RG064 ; grisé si aucune carte agent n'est sélectionnée.
      - Menu global (barre de menus) : accessible depuis les vues « Events » et « Agents » ; le menu contextuel d'une carte agent (vue « Agents ») offre les mêmes actions « Edit Agent »/« Delete Agent », alignées sur le menu général.
      - **État** :
        - Nouveau... — Fonctionnel
        - Éditer — Non implémenté (actif si un node État est sélectionné)
        - Supprimer — Non implémenté (actif si un node État est sélectionné)
      - **Événement** :
        - Nouveau... — Fonctionnel
        - Éditer — Non implémenté (actif si un node Événement est sélectionné)
        - Supprimer — Non implémenté (actif si un node Événement est sélectionné)
    - **Relations...** :
      - Lier État et Événement — Fonctionnel
      - Associer des agents à un état — Fonctionnel (FN030, SU008 : dialogue d'association depuis le menu ou le menu contextuel d'un état)
      - Éditer — Non implémenté (actif si une relation est sélectionnée)
      - Supprimer — Non implémenté (actif si une relation est sélectionnée)

  - **À propos** :
    - Journal des modifications — Fonctionnel
    - À propos de Planoscript — Fonctionnel

- **Comportement** :
  - Les menus sont désactivés lorsqu'aucun projet n'est ouvert (RG007).
  - Le menu « Enregistrer » est désactivé si le projet n'est pas modifié.


### 2. Barre de titre de la fenêtre
- **Contenu** :
  - **Titre** : Format dynamique : `"Planoscript : {nom_projet} ({chemin_fichier})"` ou `"Planoscript : commencez votre nouveau projet"` si aucun projet n'est ouvert.
  - **Style** : Barre de titre native du système d'exploitation.


### 3. Barre de composants (Gauche) — *Implémentée mais non intégrée*
- **Fichier** : `./src/ui/widgets/components_toolbar.py`
- **Description** : Barre latérale de gestion des types de composants.
- **Largeur** : 40 px.
- **Style** :
  - Arrière-plan : `#f8f8f8`.
  - Bordure droite : `1px solid #ddd`.

- **Éléments** : Boutons avec icônes SVG (24×24 px) :
  - « Référence temporelle » (icône : `./src/ui/asset/icon/calendar.svg`)
  - « Référence spatiale » (icône : `./src/ui/asset/icon/map.svg`)
  - « Agent » (icône : `./src/ui/asset/icon/agent.svg`)
  - « État » (icône : `./src/ui/asset/icon/state.svg`)
  - « Événement » (icône : `./src/ui/asset/icon/event.svg`)
  - « Relation » (icône : `./src/ui/asset/icon/relation.svg`)

- **Style des boutons** :
  - Arrière-plan : `#ffffff`.
  - Bordure : `1px solid #ddd`.
  - Survol : Arrière-plan `#AABBCC`, bordure `#AABBCC`.
  - Enfoncé : Arrière-plan `#AABBCC`, bordure `2px solid #555555`.

- **Comportement** :
  - Émet un signal `component_selected` avec le type de composant.
  - Émet un signal `relation_selected` pour le bouton Relation.


### 4. Barre de parcours (Droite) — *Implémentée mais non intégrée*
- **Fichier** : `./src/ui/widgets/journeys_toolbar.py`
- **Description** : Barre latérale de gestion des parcours de la carte narrative.
- **Largeur** : 40 px.
- **Style** :
  - Arrière-plan : `#f8f8f8`.
  - Bordure gauche : `1px solid #ddd`.

- **Éléments** :
  - **Boutons d'action** (en haut) :
    - « Ajouter » (icône : `./src/ui/asset/icon/addJourney.svg`) → Crée un nouveau parcours.
    - « Supprimer » (icône : `./src/ui/asset/icon/delJourney.svg`) → Supprime le parcours sélectionné.
      - *Désactivé s'il ne reste qu'un seul parcours*.
  - **Séparateur** : Ligne horizontale (`#ccc`, 1 px).
  - **Liste des parcours** :
    - Chaque parcours est un bouton avec l'icône `./src/ui/asset/icon/journey.svg`.
    - **Nom** : Affiché dans l'infobulle.
    - **État** : Bouton coché si le parcours est actif.
    - **Couleur** : Arrière-plan `#AABBCC` lorsqu'il est sélectionné.

- **Comportement** :
  - Cliquer sur un parcours **affiche** ses composants/relations dans l'espace de travail.
  - **Par défaut** : Le premier parcours est toujours affiché et ne peut pas être supprimé.


### 5. Barre d'onglets (Centre) — *Partiellement implémentée*
- **Fichier** : `./src/ui/widgets/tab_bar.py`
- **Description** : Barre d'onglets pour basculer entre les vues du projet.
- **Hauteur** : 40 px.
- **Style** :
  - Arrière-plan : `#f8f8f8`.
  - Police : Arial, 9 pt.

- **Éléments** :
  - Onglet « Events » — **Actif par défaut**
  - Onglet « Agents » — **Fonctionnel** (second espace de travail, matrice agents × états — SU009, TSK07–TSK15)
  - Les onglets « Relations » et « Chapitres » sont des reliquats d'une version antérieure : ils ne font pas partie du MVP et sont retirés de la spécification.

- **Style des onglets** :
  - Arrière-plan : `#f8f8f8`.
  - Bordure inférieure : `2px solid transparent` (transparent lorsque non sélectionné).
  - Survol : Arrière-plan `#e0e0e0`.
  - Sélectionné : Arrière-plan `#ffffff`, texte en **gras**, bordure inférieure visible.


### 6. Espace de travail (Centre)
- **Fichier** : `./src/ui/views/events_workspace.py`
- **Description** : Espace de travail principal pour visualiser et éditer la carte narrative.
- **Classe** : `EventsWorkspace` (héritant de `QGraphicsView`).

- **Style** :
  - Arrière-plan : `#ffffff`.
  - Bordure : Aucune (intégrée dans QGraphicsView).

- **Fonctionnalités implémentées** :
  
  - **Grille d'alignement** :
    - **Grille principale** : Pas de 20×20 pixels, couleur `#e0e0e0`.
    - **Sous-grille** : Carrés de pas 4×4 (80×80 pixels), couleur `#808080`.
    - **Visibilité** : Toujours visible.
    - **Aimantation** : *Pas encore implémentée* — les nœuds ne s'alignent pas automatiquement.
    - **Optimisation** : La grille est redessinée dynamiquement uniquement pour la zone visible.

  - **Défilement** :
    - **Type** : Défilement infini (théoriquement).
    - **Barres de défilement** : Toujours visibles.
    - **Style des barres de défilement** :
      - Arrière-plan : `#f0f0f0`.
      - Curseur : `#c0c0c0`.
      - Boutons : `#e0e0e0`.
    - **Défilement automatique** : Lorsque la souris est proche des bords (marge de 50 px), la vue défile automatiquement.
    - **Limite de la scène** : 4000×4000 pixels par défaut, s'étend dynamiquement lorsque les nœuds la dépassent.

  - **Zoom** :
    - **Plage** : 10 % à 300 % (via `ZoomBar`).
    - **Comportement** : *Non connecté* — les contrôles de zoom existent mais ne sont pas reliés à la vue.
    - **Raccourcis** : *Non implémentés* (Ctrl+, Ctrl-, Ctrl+0).

  - **Glisser-déposer** :
    - **Activé** pour les nœuds et les relations.
    - **Comportement** :
      - Les nœuds peuvent être déplacés librement.
      - *Les nœuds ne s'alignent pas sur la grille* pendant le déplacement.
      - La scène s'étend automatiquement lorsqu'un nœud est traîné vers les bords.

  - **Menu contextuel** (clic droit ; indisponible pendant la création d'une relation) :
    - Sur la grille (hors nœuds et relations) : « New State », « New Event », « New Agent » (TSK13 : ouvre directement le dialogue « New Agent », sans bascule de vue), « Connect State and Event ».
    - Sur un nœud État : « Edit State », « Associate agents... » (FN030), « Show in agents view » (TSK10/RG067, désactivé si l'état n'a aucune association agent), « Delete State » (désactivé pour l'état initial, RG031 ; **confirmation SU003 si l'état est connecté à au moins un évènement et/ou associé à au moins un agent** — revue TSC 28-10-2026, cascade arcs + RG065).
    - Sur un nœud Événement : « Edit Event », « Delete Event » (**confirmation SU003 si l'évènement est connecté à au moins un état** — revue TSC 28-10-2026, cascade des arcs).
    - Sur une relation : « Edit Relation », « Delete Relation ».
    - Le clic sélectionne l'élément sous le curseur avant d'ouvrir le menu, de sorte que les actions s'appliquent à l'élément cliqué.

- **Éléments visuels** :

  - **Nœuds (Composants)** :
    - **Fichiers** : 
      - `./src/ui/nodes/base_node.py` (BaseNode)
      - `./src/ui/nodes/agent_node.py` (AgentNode)
      - `./src/ui/nodes/state_node.py` (StateNode)
      - `./src/ui/nodes/event_node.py` (EventNode)
    - **Types implémentés** : Agent, État, Événement.
    - **Types non implémentés** : Référence temporelle, Référence spatiale.
    - **Forme** : Rectangle (80×40 px par défaut).
    - **Style** :
      - Arrière-plan : `#f0f0f0` (gris clair).
      - Bordure : `1px solid #808080` (gris moyen).
      - Ombre : Aucune (à implémenter).
      - Sélection : Arrière-plan `#dce6ff` (bleu très clair), bordure `#0078d7` (bleu).
    - **Contenu** :
      - **Nom** : Texte en haut, Arial 10 pt **gras**.
      - **Description** : *Non affichée* — à implémenter.
    - **Badge sur les nœuds État** (TSK05) :
      - **Badge d'agents** (coin bas-droit de la carte, 2/3 dedans et 1/3 dehors du contour — TSK17, TSC 28-10-2026) : pastille avec compteur des agents associés à l'état (FN030) ; remplissage `#E5C07B`, contour `#F0F0F0`, texte `#1E1E1E` ; infobulle « Agents: ... ».
      - *Pas de badge d'évènement en vue Events* (revue TSC 28-10-2026, retour n°1 : les connexions y sont visibles, les badges surchargeraient les nœuds) — les badges d'évènement sont affichés sur les cartes d'état de la **vue agents** (voir section 6.bis).
    - **Points d'accroche** :
      - 4 points (haut, bas, gauche, droite) — *Pas encore visuellement implémentés*.
      - Devraient être visibles au survol (carrés de 8 px, couleur `#4CAF50`).

  - **Relations (Connexions)** :
    - **Fichier** : `./src/ui/nodes/connection.py`
    - **Classe** : `Connection` (héritant de `QGraphicsPathItem`).
    - **Style** :
      - **Directionnelle** : Ligne avec flèche, couleur à définir.
      - **Non directionnelle** : Ligne simple, couleur `#999`.
      - **Épaisseur** : 2 px.
    - **Annotation** :
      - *Non implémentée* — texte au milieu de la relation.
      - Devrait avoir un arrière-plan blanc semi-transparent pour la lisibilité.


### 6.bis. Vue agents (Espace de travail secondaire) — *Implémentée (TSK07–TSK15)*

- **Fichier** : `./src/ui/views/agents_workspace.py`
- **Description** : Second espace de travail dédié aux associations entre les agents du projet et les états de la carte narrative courante. Accessible via l'onglet « Agents » de la barre d'onglets. `QGraphicsView` (comme la vue Events, TSK15). Les créations/éditions d'agents et d'états y sont possibles via le menu global et les menus contextuels (TSK13).
- **Représentation** : Matrice agents × états en vue graphique.
  - Une carte par agent du projet (colonne de gauche, lignes) ; une carte par état de la carte narrative courante (ligne du haut, colonnes) ; une case à cocher 20×20 à chaque intersection.
  - Cartes 80×40 rendues comme les nœuds de la vue Events (surface `#2D2D2D`, contour teinté du type : or `#E5C07B` pour les états, cuivre `#D19A66` pour les agents) ; libellé tronqué à 8 caractères, infobulle immédiate au survol.
  - Grille de fond 120×80 (config `agents_view_cell_width`/`_height`) : chaque carte et chaque case est centrée dans sa cellule (marges 20 px pour les cartes, 50/30 px pour les cases). La grille est redessinée sur la zone visible (pattern vue Events) et la scène s'étend vers la droite/le bas uniquement : la matrice reste ancrée au coin haut-gauche.
  - L'ordre des colonnes suit la règle de gestion RG068 (ordre de création par défaut, réordonnancement manuel par glisser-déposer persistant, état initial épinglé en première colonne avec message de rejet dans la barre d'info).
  - Une cellule cochée matérialise une association agent-état (SU008). L'édition s'effectue en cliquant la case (TSK09).
- **Sélection des cartes (revue TSC 28-10-2026)** : comme dans la vue Events, un clic sur une carte la sélectionne (une seule carte sélectionnée à la fois, agents et états confondus) ; la sélection se matérialise par un **contour pointillé de la teinte du type** (charte 98 : sélection > survol > type). Le clic dans le vide désélectionne. Le glisser-déposer de réordonnancement (RG068) est maintenu : le clic sélectionne, le déplacement réordonne. Le clic droit sur une carte la sélectionne avant d'ouvrir le menu contextuel. La sélection pilote l'activation des entrées « Éditer »/« Supprimer » du sous-menu Agent en vue « Agents ».
- **Badges d'évènement sur les cartes état (TSK13, vue agents uniquement)** : deux pastilles avec compteur, même style que le badge d'agents de la vue Events mais en cuivre `#D19A66` (teinte du type Événement), **centrés verticalement, et sur l'axe horizontal 2/3 dedans / 1/3 dehors du contour** de la carte (5 px dehors sur un diamètre de 16 — TSK18, TSC 29-10-2026, même règle horizontale que le badge d'agents de la vue Events, TSK17) — toujours du même côté que les ports de connexion (entrant/sortant) des états en vue Events (côtés TSC 28-10-2026) : badge de **gauche** = nombre d'événements **sources** (arcs `Event_to_state` pointant vers cet état), badge de **droite** = nombre d'événements **cibles** (arcs `State_to_event` partant de cet état). Infobulle « Events (in): ... » / « Events (out): ... ». Masqués à 0 ; rafraîchis dynamiquement à la création/suppression d'une relation et au rafraîchissement de la matrice. Les cartes agent ne portent pas de badge d'évènement. En vue Events, les nœuds État ne portent que le badge d'agents (revue TSC 28-10-2026, retour n°1).
- **Contrat de focus (navigation croisée, TSK10/RG067, étendu par TSK13)** :
  - Méthode commune aux vues : « mettre le focus sur une entité » (état cible → surbrillance + défilement de la colonne, bande translucide sur la cellule ; agent cible → surbrillance des nodes des états associés dans la vue Events avec atténuation du reste du graphe ; état cible depuis la vue agents → bascule vers la vue Events et focus du node de l'état, TSK13).
  - Le focus est un état visuel temporaire (RG067) : ni marquage modifié, ni persistance. Un clic dans le vide ou la touche Échap le relâche.
- **Menus contextuels (TSK13, alignés sur le menu général par la revue TSC 28-10-2026)** :
  - Carte agent : « Edit Agent » et « Delete Agent » ont le même comportement que le menu général en vue « Agents » (édition/suppression directe de la carte sélectionnée — le clic droit sélectionne la carte cliquée ; « Delete Agent » avec confirmation RG064), « Show in events view » (TSK10).
  - Carte état : « Edit State » (dialogue pré-rempli), « Delete State » (désactivé pour l'état initial, RG031 ; confirmation si des arcs ou associations existent, cascade RG065), « Show in events view » (bascule vers la vue Events + focus du node, extension du contrat TSK10/RG067).
  - Grille (hors matrice) : « New Agent » (création directe dans la ligne de la matrice, reste dans la vue agents), « New State » (reste dans la vue agents ; la nouvelle colonne apparaît dans la matrice), « New Event » (crée le node dans la vue Events, bascule vers la vue Events et sélectionne le node — même comportement que le point 03).
- **Création d'un événement depuis la vue agents (TSK13)** : que la création parte du menu global « Project > Components... > Event > New... » ou du menu contextuel de la grille, la vue bascule sur « Events » une fois l'événement créé, et le node créé est sélectionné. La création d'un agent ou d'un état depuis la vue agents ne bascule pas la vue.
- **Rôles** :
  - Afficher les associations agent-état de la carte courante.
  - Éditer les associations (cocher/décocher).
  - Gérer les agents du projet via le menu global (sous-menu « Project > Components... > Agent » : Nouveau.../Éditer/Supprimer — FN031, TSK13) et via les menus contextuels (créer/éditer/supprimer un agent, éditer/supprimer un état).
### 7. Barre d'informations (Bas gauche)
- **Fichier** : `./src/ui/widgets/info_bar.py`
- **Description** : Affiche des informations contextuelles sur l'objet sélectionné.
- **Largeur** : 80 % de la zone inférieure (4/5 de la disposition).
- **Hauteur** : 30 px.
- **Style** :
  - Arrière-plan : `#f0f0f0`.
  - Bordure supérieure : `1px solid #ddd`.

- **Éléments** :
  - **Texte** : Label avec le style `font-size: 10pt; color: #666;`.
  - **Contenu** :
    - Si un **composant** est sélectionné : Affiche un message personnalisé.
    - Si une **relation** est sélectionnée : Affiche un message personnalisé.
    - Si **rien n'est sélectionné** : Vide.


### 8. Barre de zoom (Bas droite) — *Désactivée*
- **Fichier** : `./src/ui/widgets/zoom_bar.py`
- **Description** : Contrôle du niveau de zoom.
- **Largeur** : 20 % de la zone inférieure (1/5 de la disposition).
- **Hauteur** : 30 px.
- **Style** :
  - Arrière-plan : `#f0f0f0`.
  - Bordure supérieure : `1px solid #ddd`.
  - Bordure gauche : `1px solid #ddd`.

- **Éléments** (de gauche à droite) :
  - **Bouton « Zoom arrière »** :
    - Texte : « - »
    - Action : Diminue le zoom de 10 % — *Non connecté*.
    - Raccourci : Ctrl + - — *Non implémenté*.
  - **Curseur de zoom** :
    - Type : `QSlider` horizontal.
    - Plage : 10 % à 190 % (valeur interne, correspond à 10 %–300 % après mappage).
    - Valeur par défaut : 100 %.
    - Incrément : 10 %.
    - Infobulle : Affiche le pourcentage actuel.
  - **Bouton « Zoom avant »** :
    - Texte : « + »
    - Action : Augmente le zoom de 10 % — *Non connecté*.
    - Raccourci : Ctrl + + — *Non implémenté*.
  - **Bouton « Réinitialiser »** :
    - *Non implémenté* dans l'interface.
    - Raccourci : Ctrl 0 — *Non implémenté*.
  - **Affichage du pourcentage** :
    - *Non implémenté* — remplacé par l'infobulle du curseur.


### 9. Message d'accueil
- **Description** : Affiché lorsqu'aucun projet n'est ouvert.
- **Contenu** :
  ```html
  <h2>Construisez le plan de votre nouveau scénario.</h2>
  <p>Commencez par <a>créer un nouveau projet</a> ou ouvrez un projet existant.</p>
  ```
- **Style** : Texte centré avec un padding de 40 px.
- **Comportement** : Le lien « créer un nouveau projet » déclenche `_create_project()`.


---

## Fonctionnalités implémentées

### Fonctionnelles
- [x] Créer un nouveau projet
- [x] Ouvrir un projet existant
- [x] Fermer un projet avec confirmation
- [x] Enregistrer un projet (Ctrl+S)
- [x] Enregistrer sous... (Ctrl+Shift+S)
- [x] Afficher le message d'accueil
- [x] Créer des nœuds (Agent, État, Événement) via le menu
- [x] Créer des relations État-Événement
- [x] Sélection simple des nœuds et des relations
- [x] Déplacer les nœuds dans l'espace de travail
- [x] Défilement automatique lors du déplacement vers les bords
- [x] Extension dynamique de la scène
- [x] Affichage de la grille (20 px + 80 px)
- [x] Barre d'informations contextuelles
- [x] Gestion de l'état modifié du projet
- [x] Boîtes de dialogue « À propos » et « Journal des modifications »
- [x] Gestion des agents du projet (créer, éditer, supprimer avec cascade RG064 — FN031, TSK01/TSK02 ; sous-menu « Agent » Nouveau.../Éditer/Supprimer avec dialogue de sélection — TSK13)
- [x] Associations agent-état depuis la vue Events (dialogue « Associer des agents... » — FN030, TSK04)
- [x] Badges d'agents sur les nœuds d'état dans la vue Events (TSK05)
- [x] Badges d'évènement (source/cible) sur les cartes d'état dans la vue agents (TSK13 ; absents de la vue Events — revue TSC 28-10-2026)
- [x] Vue « Agents » : matrice agents × états en vue graphique, édition des cellules, ordre RG068, grille 120×80 (TSK07–TSK15, SU008/SU009)
- [x] Navigation croisée entre vues avec focus (RG067 — TSK10, étendu état→parcours par TSK13)
- [x] Menus contextuels des vues parcours et agents (création/édition/suppression agent, édition/suppression état, bascule après création d'événement — TSK13)

### Partiellement implémentées
- [ ] Barre de composants (existe mais non intégrée)
- [ ] Barre de parcours (existe mais non intégrée)
- [ ] Barre d'onglets (les deux onglets Events/Agents sont actifs)
- [ ] Barre de zoom (existe mais non connectée)
- [ ] Nœuds de référence temporelle (classe non implémentée)
- [ ] Nœuds de référence spatiale (classe non implémentée)

### Non implémentées
- [ ] Aimantation sur la grille
- [ ] Points d'accroche visibles sur les nœuds
- [ ] Annotation sur les relations
- [ ] Zoom fonctionnel (raccourcis et contrôles)
- [ ] Défilement infini complet (limité à 4000×4000)
- [ ] Sélection multiple
- [ ] Copier/Coller/Couper
- [ ] Annuler/Rétablir
- [ ] Historique des modifications
- [ ] Export/Import de carte
- [ ] Projets récents
- [ ] Suppression de relations (la suppression de nœuds État/Événement est fonctionnelle via les menus contextuels avec confirmation SU003 — TSK13 + revue TSC 28-10-2026)


---

## Structure des fichiers

```
./src/ui/
├── main_window.py          # Fenêtre principale
├── views/
│   └── events_workspace.py # Espace de travail
├── widgets/
│   ├── components_toolbar.py # Barre de composants (non intégrée)
│   ├── journeys_toolbar.py   # Barre de parcours (non intégrée)
│   ├── tab_bar.py           # Barre d'onglets (partiellement intégrée)
│   ├── info_bar.py          # Barre d'informations (intégrée)
│   └── zoom_bar.py          # Barre de zoom (non intégrée)
├── nodes/
│   ├── base_node.py         # Classe de base des nœuds
│   ├── agent_node.py        # Nœud Agent
│   ├── state_node.py        # Nœud État
│   ├── event_node.py        # Nœud Événement
│   └── connection.py         # Connexions entre nœuds
└── dialogs/
    ├── about_dialog.py       # Boîte de dialogue À propos
    └── change_log_dialog.py  # Boîte de dialogue Journal des modifications
```


---

## Notes de conception

1. **Architecture** : L'application suit une architecture en couches avec une séparation entre :
   - **UI** (`./src/ui/`) : Composants visuels
   - **Core** (`./src/core/`) : Modèles et services
   - **Use Cases** (`./src/usecases/`) : Logique applicative
2. **Pattern MVC** : Les classes UI utilisent des services et des use cases pour manipuler les données.
3. **Extensibilité** : Les barres latérales et la barre de zoom sont implémentées en tant que widgets séparés, prêts à être intégrés.
4. **Style** : L'application utilise des feuilles de style Qt (QSS) pour un rendu cohérent.
5. **Internationalisation** : Les textes sont actuellement uniquement en anglais. Une refactorisation pour l'i18n est recommandée.


---

## Prochaines étapes recommandées

1. **Intégrer les barres latérales** dans `main_window.py`
2. **Connecter le zoom** entre `ZoomBar` et `EventsWorkspace`
3. **Implémenter l'aimantation sur la grille**
4. **Ajouter les points d'accroche** sur les nœuds
5. **Connecter la barre d'onglets** pour basculer entre les vues
6. **Ajouter les fonctionnalités manquantes** (sélection multiple, copier/coller, etc.)
