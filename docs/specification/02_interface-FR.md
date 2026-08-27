# Planoscript ::: Spécification de l'interface utilisateur

## Version du document
- **Version** : 2.0
- **Date** : 27-08-2026
- **État** : Mise à jour rétrospective pour refléter l'implémentation actuelle
- **Basé sur** : Code source dans `./src/ui/main_window.py` et modules associés

---

## Architecture générale de l'interface

### Mise en page
- **Type** : Disposition verticale principale (QVBoxLayout) avec sections distinctes.
- **Structure** :
  - **Haut** : Barre de menu intégrée (QMenuBar).
  - **Centre** : Espace de travail principal (JourneyWorkspace).
  - **Bas** : Barre d'information (75%) + Barre de zoom (25%) - *Barre de zoom actuellement désactivée*.

> **Note** : Les barres latérales (composants à gauche, parcours à droite) sont implémentées mais **non intégrées** dans la fenêtre principale.

---

## Composants de l'Interface

### 1. Barre de menu de la fenêtre applicative
- **Type** : QMenuBar natif.
- **Position** : En haut de la fenêtre.
- **Style** :
  - Fond : `#ffffff` (blanc).
  - Police : Arial, 9pt.
  - Couleur du texte : `#000000` (noir).
  - Éléments sélectionnés : Fond `#404040`, texte `#ffffff`.

- **Menus disponibles** :
  - **Fichiers** :
    - New Project... (Ctrl+N)
    - Open... (Ctrl+O)
    - Close (Ctrl+W)
    - Save (Ctrl+S) - Désactivé si projet non modifié
    - Save as... (Ctrl+Shift+S)
    - Export Map - Non implémenté
    - Import Map - Non implémenté
    - Recent Projects... - Non implémenté
    - Quit (Ctrl+Q)
  
  - **Edit** :
    - Undo (Ctrl+Z) - Non implémenté
    - Redo (Ctrl+Y) - Non implémenté
    - History - Non implémenté
    - Cut (Ctrl+X) - Non implémenté
    - Copy (Ctrl+C) - Non implémenté
    - Paste (Ctrl+V) - Non implémenté
    - Delete (Del) - Non implémenté

  - **Display** :
    - **Journey** :
      - JourneyList - Non implémenté
    - **Zoom** :
      - Zoom in (Ctrl+=) - Non implémenté
      - Zoom out (Ctrl+-) - Non implémenté
      - Reset (Ctrl+0) - Non implémenté

  - **Project** :
    - **View** :
      - Journey - Non implémenté
      - Relations - Non implémenté
      - Chapters - Non implémenté
    - **Components...** :
      - Agent - Fonctionnel
      - État - Fonctionnel
      - Event - Fonctionnel
    - **Relations...** :
      - Link State and Event - Fonctionnel

  - **About** :
    - Change Log - Fonctionnel
    - About Planoscript - Fonctionnel

- **Comportement** :
  - Les menus sont désactivés quand aucun projet n'est ouvert (RG007).
  - Le menu "Save" est désactivé si le projet n'est pas modifié.


### 2. Barre d'en-tête de la fenêtre
- **Contenu** :
  - **Titre** : Format dynamique : `"Planoscript : {nom_projet} ({chemin_fichier})"` ou `"Planoscript : start your new project"` si aucun projet n'est ouvert.
  - **Style** : Titre de fenêtre natif du système d'exploitation.


### 3. Barre des composants (Left) - *Implémentée mais non intégrée*
- **Fichier** : `./src/ui/widgets/components_toolbar.py`
- **Description** : Barre latérale pour gérer les types de composants.
- **Largeur** : 40px.
- **Style** :
  - Fond : `#f8f8f8`.
  - Bordure droite : `1px solid #ddd`.

- **Éléments** : Boutons avec icônes SVG (24x24px) :
  - "Référence temporelle" (icône : `./src/ui/asset/icon/calendar.svg`)
  - "Référence spatiale" (icône : `./src/ui/asset/icon/map.svg`)
  - "Agent" (icône : `./src/ui/asset/icon/agent.svg`)
  - "État" (icône : `./src/ui/asset/icon/state.svg`)
  - "Évènement" (icône : `./src/ui/asset/icon/event.svg`)
  - "Relation" (icône : `./src/ui/asset/icon/relation.svg`)

- **Style des boutons** :
  - Fond : `#ffffff`.
  - Bordure : `1px solid #ddd`.
  - Hover : Fond `#AABBCC`, bordure `#AABBCC`.
  - Pressed : Fond `#AABBCC`, bordure `2px solid #555555`.

- **Comportement** :
  - Émet un signal `component_selected` avec le type de composant.
  - Émet un signal `relation_selected` pour le bouton Relation.


### 4. Barre des parcours (Right) - *Implémentée mais non intégrée*
- **Fichier** : `./src/ui/widgets/journeys_toolbar.py`
- **Description** : Barre latérale pour gérer les parcours de la carte narrative.
- **Largeur** : 40px.
- **Style** :
  - Fond : `#f8f8f8`.
  - Bordure gauche : `1px solid #ddd`.

- **Éléments** :
  - **Boutons d'action** (en haut) :
    - "Ajouter" (icône : `./src/ui/asset/icon/addJourney.svg`) → Crée un nouveau parcours.
    - "Supprimer" (icône : `./src/ui/asset/icon/delJourney.svg`) → Supprime le parcours sélectionné.
      - *Désactivé si un seul parcours reste*.
  - **Séparateur** : Ligne horizontale (`#ccc`, 1px).
  - **Liste des parcours** :
    - Chaque parcours est un bouton avec icône `./src/ui/asset/icon/journey.svg`.
    - **Nom** : Affiché dans le tooltip.
    - **État** : Bouton coché si le parcours est actif.
    - **Couleur** : Fond `#AABBCC` quand sélectionné.

- **Comportement** :
  - Cliquer sur un parcours **affiche** ses composants/relations dans l'espace de travail.
  - **Par défaut** : Le premier parcours est toujours affiché et ne peut pas être supprimé.


### 5. Barre des onglets (Center) - *Partiellement implémentée*
- **Fichier** : `./src/ui/widgets/tab_bar.py`
- **Description** : Barre d'onglets pour basculer entre les vues du projet.
- **Hauteur** : 40px.
- **Style** :
  - Fond : `#f8f8f8`.
  - Police : Arial, 9pt.

- **Éléments** :
  - Onglet "Parcours" - **Actif par défaut**
  - Onglet "Relations" - *Non implémenté*
  - Onglet "Chapitres" - *Non implémenté*

- **Style des onglets** :
  - Fond : `#f8f8f8`.
  - Bordure inférieure : `2px solid transparent` (transparent quand non sélectionné).
  - Hover : Fond `#e0e0e0`.
  - Sélectionné : Fond `#ffffff`, texte en **gras**, bordure inférieure visible.


### 6. Espace de travail (Center)
- **Fichier** : `./src/ui/views/journey_workspace.py`
- **Description** : Espace de travail principal pour visualiser et éditer la carte narrative.
- **Classe** : `JourneyWorkspace` (héritant de `QGraphicsView`).

- **Style** :
  - Fond : `#ffffff`.
  - Bordure : Aucune (intégré dans QGraphicsView).

- **Fonctionnalités implémentées** :
  
  - **Grille d'alignement** :
    - **Grille principale** : Pas de 20x20 pixels, couleur `#e0e0e0`.
    - **Sous-grille** : Carrés de 4x4 pas (80x80 pixels), couleur `#808080`.
    - **Visibilité** : Toujours visible.
    - **Magnétisme** : *Non encore implémenté* - les nœuds ne s'accrochent pas automatiquement.
    - **Optimisation** : La grille est redessinée dynamiquement uniquement pour la zone visible.

  - **Défilement** :
    - **Type** : Défilement infini (théoriquement).
    - **Barres de défilement** : Toujours visibles.
    - **Style des barres** :
      - Fond : `#f0f0f0`.
      - Poignée : `#c0c0c0`.
      - Boutons : `#e0e0e0`.
    - **Auto-défilement** : Quand la souris est près des bords (marge de 50px), la vue défile automatiquement.
    - **Limite de la scène** : 4000x4000 pixels par défaut, s'étend dynamiquement quand les nœuds dépassent.

  - **Zoom** :
    - **Plage** : 10% à 300% (via `ZoomBar`).
    - **Comportement** : *Non connecté* - les contrôles de zoom existent mais ne sont pas connectés à la vue.
    - **Raccourcis** : *Non implémentés* (Ctrl+, Ctrl-, Ctrl+0).

  - **Glisser-déposer** :
    - **Activé** pour les nœuds et relations.
    - **Comportement** :
      - Les nœuds peuvent être déplacés librement.
      - *Les nœuds ne s'accrochent pas à la grille* pendant le déplacement.
      - La scène s'étend automatiquement quand un nœud est déplacé vers les bords.

- **Éléments visuels** :

  - **Nœuds (Composants)** :
    - **Fichiers** : 
      - `./src/ui/nodes/base_node.py` (BaseNode)
      - `./src/ui/nodes/agent_node.py` (AgentNode)
      - `./src/ui/nodes/state_node.py` (StateNode)
      - `./src/ui/nodes/event_node.py` (EventNode)
    - **Types implémentés** : Agent, État, Évènement.
    - **Types non implémentés** : Référence temporelle, Référence spatiale.
    - **Forme** : Rectangle (120x80px par défaut).
    - **Style** :
      - Fond : `#f0f0f0` (gris clair).
      - Bordure : `1px solid #808080` (gris moyen).
      - Ombre : Aucune (à implémenter).
      - Sélection : Fond `#dce6ff` (bleu très clair), bordure `#0078d7` (bleu).
    - **Contenu** :
      - **Nom** : Texte en haut, police Arial 10pt **gras**.
      - **Description** : *Non affichée* - à implémenter.
    - **Points d'accroche** :
      - 4 points (haut, bas, gauche, droite) - *Non encore implémentés visuellement*.
      - Devraient être visibles au survol (carrés de 8px, couleur `#4CAF50`).

  - **Relations (Connexions)** :
    - **Fichier** : `./src/ui/nodes/connection.py`
    - **Classe** : `Connection` (héritant de `QGraphicsPathItem`).
    - **Style** :
      - **Directionnelle** : Ligne avec flèche, couleur à définir.
      - **Non directionnelle** : Ligne simple, couleur `#999`.
      - **Épaisseur** : 2px.
    - **Annotation** :
      - *Non implémentée* - texte au milieu de la relation.
      - Devrait avoir un fond blanc semi-transparent pour la lisibilité.


### 7. Barre d'information (Bottom Left)
- **Fichier** : `./src/ui/widgets/info_bar.py`
- **Description** : Affiche des informations contextuelles sur l'objet sélectionné.
- **Largeur** : 80% de la zone bas (4/5 du layout).
- **Hauteur** : 30px.
- **Style** :
  - Fond : `#f0f0f0`.
  - Bordure supérieure : `1px solid #ddd`.

- **Éléments** :
  - **Texte** : Label avec style `font-size: 10pt; color: #666;`.
  - **Contenu** :
    - Si un **composant** est sélectionné : Affiche un message personnalisé.
    - Si une **relation** est sélectionnée : Affiche un message personnalisé.
    - Si **rien n'est sélectionné** : Vide.


### 8. Barre de zoom (Bottom Right) - *Désactivée*
- **Fichier** : `./src/ui/widgets/zoom_bar.py`
- **Description** : Contrôle du niveau de zoom.
- **Largeur** : 20% de la zone bas (1/5 du layout).
- **Hauteur** : 30px.
- **Style** :
  - Fond : `#f0f0f0`.
  - Bordure supérieure : `1px solid #ddd`.
  - Bordure gauche : `1px solid #ddd`.

- **Éléments** (de gauche à droite) :
  - **Bouton "Zoom arrière"** :
    - Texte : "-"
    - Action : Réduit le zoom de 10% - *Non connecté*.
    - Raccourci : Ctrl - - *Non implémenté*.
  - **Curseur de zoom** :
    - Type : `QSlider` horizontal.
    - Plage : 10% à 190% (valeur interne, correspond à 10%-300% après mapping).
    - Valeur par défaut : 100%.
    - Incrément : 10%.
    - Tooltip : Affiche le pourcentage actuel.
  - **Bouton "Zoom avant"** :
    - Texte : "+"
    - Action : Augmente le zoom de 10% - *Non connecté*.
    - Raccourci : Ctrl + - *Non implémenté*.
  - **Bouton "Réinitialiser"** :
    - *Non implémenté* dans l'interface.
    - Raccourci : Ctrl 0 - *Non implémenté*.
  - **Affichage du pourcentage** :
    - *Non implémenté* - remplacé par le tooltip du slider.


### 9. Message de bienvenue
- **Description** : Affiché quand aucun projet n'est ouvert.
- **Contenu** :
  ```html
  <h2>Build the plan of your new script.</h2>
  <p>Start by <a>creating a new project</a> or open an existing project.</p>
  ```
- **Style** : Texte centré avec padding de 40px.
- **Comportement** : Le lien "creating a new project" déclenche `_create_project()`.


---

## Fonctionnalités implémentées

### ✅ Fonctionnel
- [x] Création d'un nouveau projet
- [x] Ouverture d'un projet existant
- [x] Fermeture d'un projet avec confirmation
- [x] Sauvegarde d'un projet (Ctrl+S)
- [x] Sauvegarde sous un autre nom (Ctrl+Shift+S)
- [x] Affichage du message de bienvenue
- [x] Création de nœuds (Agent, État, Évènement) via menu
- [x] Création de relations State-Event
- [x] Sélection simple des nœuds et relations
- [x] Déplacement des nœuds dans l'espace de travail
- [x] Défilement automatique quand on déplace vers les bords
- [x] Extension dynamique de la scène
- [x] Affichage de la grille (20px + 80px)
- [x] Barre d'information contextuelle
- [x] Gestion de l'état modifié du projet
- [x] Dialogues "About" et "Change Log"

### ⚠️ Partiellement implémenté
- [ ] Barre des composants (existe mais non intégrée)
- [ ] Barre des parcours (existe mais non intégrée)
- [ ] Barre d'onglets (existe mais seul "Parcours" est actif)
- [ ] Barre de zoom (existe mais non connectée)
- [ ] Nœuds Référence temporelle (classe non implémentée)
- [ ] Nœuds Référence spatiale (classe non implémentée)

### ❌ Non implémenté
- [ ] Magnétisme de la grille
- [ ] Points d'accroche visibles sur les nœuds
- [ ] Annotation sur les relations
- [ ] Zoom fonctionnel (raccourcis et contrôles)
- [ ] Défilement infini complet (limité à 4000x4000)
- [ ] Sélection multiple
- [ ] Copier/Coller/Couper
- [ ] Annuler/Refaire
- [ ] Historique des modifications
- [ ] Export/Import de cartes
- [ ] Projets récents
- [ ] Vue "Relations"
- [ ] Vue "Chapitres"
- [ ] Suppression de nœuds/relations


---

## Structure des fichiers

```
./src/ui/
├── main_window.py          # Fenêtre principale
├── views/
│   └── journey_workspace.py # Espace de travail
├── widgets/
│   ├── components_toolbar.py # Barre des composants (non intégrée)
│   ├── journeys_toolbar.py   # Barre des parcours (non intégrée)
│   ├── tab_bar.py           # Barre d'onglets (partiellement intégrée)
│   ├── info_bar.py          # Barre d'information (intégrée)
│   └── zoom_bar.py          # Barre de zoom (non intégrée)
├── nodes/
│   ├── base_node.py         # Classe de base pour les nœuds
│   ├── agent_node.py        # Nœud Agent
│   ├── state_node.py        # Nœud État
│   ├── event_node.py        # Nœud Évènement
│   └── connection.py         # Connexions entre nœuds
└── dialogs/
    ├── about_dialog.py       # Dialogue À propos
    └── change_log_dialog.py  # Dialogue Journal des modifications
```


---

## Notes de conception

1. **Architecture** : L'application suit une architecture en couches avec séparation entre :
   - **UI** (`./src/ui/`) : Composants visuels
   - **Core** (`./src/core/`) : Modèles et services
   - **Use Cases** (`./src/usecases/`) : Logique applicative

2. **Pattern MVC** : Les classes UI utilisent des services et des cas d'utilisation pour manipuler les données.

3. **Évolutivité** : Les barres latérales et la barre de zoom sont implémentées comme des widgets séparés, prêts à être intégrés.

4. **Style** : L'application utilise des feuilles de style Qt (QSS) pour un rendu cohérent.

5. **Internationalisation** : Les textes sont actuellement en français et en anglais (mélangés). Une refactorisation pour l'i18n est recommandée.


---

## Prochaines étapes recommandées

1. **Intégrer les barres latérales** dans `main_window.py`
2. **Connecter le zoom** entre `ZoomBar` et `JourneyWorkspace`
3. **Implémenter le magnétisme** de la grille
4. **Ajouter les points d'accroche** sur les nœuds
5. **Connecter la barre d'onglets** pour changer de vue
6. **Implémenter les nœuds manquants** (TimeRef, SpaceRef)
7. **Ajouter les fonctionnalités manquantes** (sélection multiple, copier/coller, etc.)
