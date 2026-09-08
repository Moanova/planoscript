# Planoscript ::: Spécification de l'interface utilisateur

## Version du document
- **Version** : 2.0
- **Date** : 27-08-2026
- **Statut** : Mise à jour rétrospective reflétant l'implémentation actuelle (dernier redesign)

---

## Architecture générale de l'interface

### Disposition
- **Type** : Disposition verticale principale (QVBoxLayout) avec des sections distinctes.
- **Structure** :
  - **Haut** : Barre de menus intégrée (QMenuBar).
  - **Centre** : Espace de travail principal (JourneyWorkspace).
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
    - **Parcours** :
      - Liste des parcours — Non implémenté
    - **Zoom** :
      - Zoom avant (Ctrl+=) — Non implémenté
      - Zoom arrière (Ctrl+-) — Non implémenté
      - Réinitialiser (Ctrl+0) — Non implémenté

  - **Projet** :
    - **Vue** :
      - Parcours — Non implémenté
      - Relations — Non implémenté
      - Chapitres — Non implémenté
    - **Composants...** :
      - Agent — Fonctionnel
      - État — Fonctionnel
      - Événement — Fonctionnel
    - **Relations...** :
      - Lier État et Événement — Fonctionnel

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
  - Onglet « Parcours » — **Actif par défaut**
  - Onglet « Relations » — *Non implémenté*
  - Onglet « Chapitres » — *Non implémenté*

- **Style des onglets** :
  - Arrière-plan : `#f8f8f8`.
  - Bordure inférieure : `2px solid transparent` (transparent lorsque non sélectionné).
  - Survol : Arrière-plan `#e0e0e0`.
  - Sélectionné : Arrière-plan `#ffffff`, texte en **gras**, bordure inférieure visible.


### 6. Espace de travail (Centre)
- **Fichier** : `./src/ui/views/journey_workspace.py`
- **Description** : Espace de travail principal pour visualiser et éditer la carte narrative.
- **Classe** : `JourneyWorkspace` (héritant de `QGraphicsView`).

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

- **Éléments visuels** :

  - **Nœuds (Composants)** :
    - **Fichiers** : 
      - `./src/ui/nodes/base_node.py` (BaseNode)
      - `./src/ui/nodes/agent_node.py` (AgentNode)
      - `./src/ui/nodes/state_node.py` (StateNode)
      - `./src/ui/nodes/event_node.py` (EventNode)
    - **Types implémentés** : Agent, État, Événement.
    - **Types non implémentés** : Référence temporelle, Référence spatiale.
    - **Forme** : Rectangle (120×80 px par défaut).
    - **Style** :
      - Arrière-plan : `#f0f0f0` (gris clair).
      - Bordure : `1px solid #808080` (gris moyen).
      - Ombre : Aucune (à implémenter).
      - Sélection : Arrière-plan `#dce6ff` (bleu très clair), bordure `#0078d7` (bleu).
    - **Contenu** :
      - **Nom** : Texte en haut, Arial 10 pt **gras**.
      - **Description** : *Non affichée* — à implémenter.
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

### Partiellement implémentées
- [ ] Barre de composants (existe mais non intégrée)
- [ ] Barre de parcours (existe mais non intégrée)
- [ ] Barre d'onglets (existe mais seul « Parcours » est actif)
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
- [ ] Vue « Relations »
- [ ] Vue « Chapitres »
- [ ] Suppression de nœuds/relations


---

## Structure des fichiers

```
./src/ui/
├── main_window.py          # Fenêtre principale
├── views/
│   └── journey_workspace.py # Espace de travail
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
2. **Connecter le zoom** entre `ZoomBar` et `JourneyWorkspace`
3. **Implémenter l'aimantation sur la grille**
4. **Ajouter les points d'accroche** sur les nœuds
5. **Connecter la barre d'onglets** pour basculer entre les vues
6. **Ajouter les fonctionnalités manquantes** (sélection multiple, copier/coller, etc.)
