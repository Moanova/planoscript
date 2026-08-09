# Planoscript ::: Spécification de l'interface utilisateur


## Mise en page
- **Type** : 'Border Layout' (disposition en 5 zones : haut, gauche, droite, centre, bas).
  - **Haut** : Barre d'en-tête + Menu général.
  - **Gauche** : Barre des composants (largeur : 40px).
  - **Droite** : Barre des parcours (largeur : 40px).
  - **Centre** : Espace de travail (zone principale).
  - **Bas** :
    - **Gauche** : Barre d'information (largeur : 75% de la zone bas).
    - **Droite** : Barre de zoom (largeur : 25% de la zone bas).


## Composants de l'Interface

### 1. Barre d'en-tête de la fenêtre applicative
- **Éléments** :
  - **Nom de l'application** : "Planoscript" (aligné à gauche).
  - **Chemin du projet** :
    - Affiché à droite du nom.
    - Format : 'Chemin : /dossier/projet.json' ou 'Nom : Nouveau Projet' (si non sauvegardé).
    - Style : 'italique, gris (#666)'.


### 2. Menu général (Top)
- **Description** : Menu déroulant.
- **Position** : Sous la barre d'en-tête.
- **Contenu** : Voir [menu.yaml].
- **Style** :
  - Fond : '#ffffff' (blanc).
  - Police : 'Arial, 9pt'.
  - Séparateurs : Lignes grises ('#ccc') de 1px.


### 3. Barre des composants (Left)
- **Description** : Barre latérale pour gérer les composants de la carte narrative.
- **Largeur** : 40px.
- **Style** :
  - Fond : '#f8f8f8'.
  - Bordure droite : '1px solide #ddd'.
- **Éléments** :
  - **Liste des types de composants** (îcones cliquables) :
    - "Référence temporelle" (icône : ./application/asset/icon/calendar.svg).
    - "Référence spatiale" (icône : ./application/asset/icon/map-marker.svg).
    - "Agent" (icône : ./application/asset/icon/user.svg).
    - "État" (icône : ./application/asset/icon/picture.svg).
    - "Évènement" (icône : ./application/asset/icon/puzzle-piece.svg).
    - "Relation" (icône : ./application/asset/icon/link-alt.svg).
  - **Comportement** :
    - Cliquer sur un type de composant **ajoute un nouveau composant** dans l'espace de travail (au centre).
    - Les boutons ont un **style uniforme** :
      - Fond : '#ffffff'.
      - Bordure : '1px solide #ddd'.
      - Hover : Fond '#e6f7ff' (bleu clair).


### 4. Barre des parcours ou barre des relations (Right)
- **Description** : Barre latérale pour gérer les parcours de la carte narrative.
- **Largeur** : 40px.
- **Style** :
  - Fond : '#f8f8f8'.
  - Bordure gauche : '1px solide #ddd'.
- **Éléments** :
  - **Boutons d'action** (en haut) :
    - "Ajouter" (icône : ./application/asset/icon/add.svg) → Crée un nouveau parcours.
    - "Supprimer" (icône : ./application/asset/icon/cross-circle.svg) → Supprime le parcours sélectionné (désactivé si un seul parcours restant).
  - **Séparateur** : Ligne horizontale ('#ccc', 1px).
  - **Liste des parcours** :
    - Chaque parcours ou relation est un **élément cliquable** avec :
      - **Icône** : ./application/asset/icon/shuffle.svg.
      - **Nom** : Nom du parcours (ex : "Parcours A").
      - **État** : l'icône est surlignée si le parcours est affiché.
	  - **Couleur** : différente pour chaque parcours.
    - **Comportement** :
      - Cliquer sur un parcours **affiche/masque** ses composants/relations dans l'espace de travail.
      - **Par défaut** : Le premier parcours est toujours affiché.


### 5. Barre des onglets (Center)
- **Description** : Barre des onglets de sélection des vues du projet (parcours, relations, chapitres).
- **Hauteur** : 40px.
- **Style** :
  - Fond : '#f8f8f8'.
  - Police : 'Arial, 9pt'.
- **Fonctionnalité** :
  - Bascule sur l'espace de travail dont l'onglet a été sélectionné par clic utilisateur
- **Éléments** :
  - Onglet "Carte narrative".
  - Onglet "Historique des relations".
  - onglet "Chapitres".


### 6. Espace de travail (Center)
- **Description** : Espace de travail pour visualiser et éditer la carte narrative en mode parcours, relations ou chapitres.
- **Style** :
  - Fond : '#ffffff'.
  - Bordure : '1px solide #eee'.
- **Fonctionnalités** :
  - **Grille d'alignement** :
    - Pas : 20x20 pixels.
    - Visibilité : Toujours **active** (magnétisme) et toujours **visible**.
    - Couleur : '#e0e0e0' (gris très clair).
	- Subdivision de la grille : Carrés de 4 pas par 4 pas.
	- couleur des subdivisions : '#808080' (gris foncé).
  - **Glisser-déposer** :
    - Activé pour les **composants** et **relations**.
    - **Comportement** :
      - Les composants **s'accrochent à la grille** pendant le déplacement.
      - Les relations sont créées en **glissant depuis un point d'accroche** d'un composant vers un autre.
  - **Zoom** :
    - Plage : 10% à 300%.
    - **Comportement** :
      - Zoom centré sur la **souris** (PC) ou le **centre de l'écran** (tablette).
      - **Raccourcis** :
        - 'Ctrl +' : Zoom avant.
        - 'Ctrl -' : Zoom arrière.
        - 'Ctrl 0' : Réinitialiser le zoom.
  - **Défilement infini** :
    - Horizontal et vertical.
    - **Limite** : 2 000x& 500 pixels (pour éviter les crashes).
- **Éléments** :
  - **Composant** :
    - **Forme** : Rectangle (120x80px).
    - **Style** :
      - Fond : '#ffffff'.
      - Bordure : '1px solide #999'.
      - Ombre : '1px 1px 3px rgba(0,0,0,0.1)'.
    - **Icône** : à définir selon le type.
    - **Texte** :
      - **Nom** : En haut (gras, 12pt).
      - **Description** : En dessous (10pt, gris '#666').
    - **Points d'accroche** :
      - 4 points (haut, bas, gauche, droite) **visibles au survol** (carrés de 8px, couleur '#4CAF50').
  - **Relation** :
    - **Style** :
      - **Directionnelle** : Flèche (`→`) de couleur '#4CAF50'.
      - **Non directionnelle** : Ligne (`—`) de couleur '#999'.
    - **Épaisseur** : 2px.
    - **Annotation** :
      - Texte libre (10pt, noir '#000').
      - Position : **Au milieu de la relation** (avec un fond blanc semi-transparent pour la lisibilité).


### 7. Barre d'information (Bottom Left)
- **Description** : Affiche des informations contextuelles sur l'objet sélectionné.
- **Largeur** : 80% de la zone bas.
- **Hauteur** : 30px.
- **Style** :
  - Fond : '#f0f0f0'.
  - Bordure supérieure : '1px solide #ddd'.
- **Éléments** :
  - **Texte** :
    - Si un **composant** est sélectionné : Affiche son **nom + type + description**.
      Exemple : `"Agent n°1 : Agent de type subjectif."`
    - Si une **relation** est sélectionnée : Affiche ses **composants liés + annotation**.
      Exemple : `"Agent n°1 → Etat n°1 : 'Relation entre l'agent n°1 et l'état n°1'"`
    - Si **rien n'est sélectionné** : aucun affichage.


### 8. Barre de zoom (Bottom Right)
- **Description** : Contrôle du niveau de zoom.
- **Largeur** : 20% de la zone bas.
- **Hauteur** : 30px.
- **Style** :
  - Fond : '#f0f0f0'.
  - Bordure supérieure : '1px solide #ddd'.
- **Éléments** (de gauche à droite) :
  - **Bouton "Zoom arrière"** :
    - Icône : -.
    - Action : Réduit le zoom de 10%.
    - Raccourci : 'Ctrl -'.
  - **Curseur de zoom** :
    - Type : 'slider'.
    - Plage : 10% à 300%.
    - Valeur par défaut : 100%.
    - Incrément : 10%.
  - **Bouton "Zoom avant"** :
    - Icône : +.
    - Action : Augmente le zoom de 10%.
    - Raccourci : 'Ctrl +'.
  - **Bouton "Réinitialiser"** :
    - Icône : à définir.
    - Action : Réinitialise le zoom à 100%.
    - Raccourci : 'Ctrl 0'.
  - **Affichage du pourcentage** :
    - Texte : '"100%"' (mis à jour en temps réel).
    - Style : '8pt'.
