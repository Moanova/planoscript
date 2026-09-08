# Planoscript ::: Fonctionnalités

## Document Version
- **Version** : 2.0
- **Date** : 08-09-2026
- **Status** : Version corrigée et enrichie, réalignée sur les user stories v2.0 (29-08-2026) et sur le menu général v2.0 (27-08-2026)

---

## Décisions de périmètre (08-09-2026)
- La section "Affichage › Parcours" (*Display › Journey*) du menu est incohérente : elle est ignorée dans la présente spécification ; la description du menu sera corrigée ultérieurement.
- La fonctionnalité d'**import de carte narrative** est retirée du MVP.
- Le **renommage du projet** porte sur le libellé du projet : il s'agit d'un attribut métier modifiable dans une fenêtre d'édition (non encore définie), et non d'une option du menu.

## Rappel du périmètre MVP
- Un projet ne contient qu'une seule carte narrative (SU001, SU002).
- Seuls le renommage de la carte par défaut, la modification de son contenu et son export sont fonctionnels (SU002).
- Les barres d'outils "composants" et "parcours" ne sont pas implémentées : les actions correspondantes sont exclusivement accessibles par le menu (SU003, SU005).
- Le zoom n'est pas disponible (SU006).
- L'application cible exclusivement les PC sous Windows (SU006).
- L'export de lecture est limité au mode "par parcours" ; les modes "par événements" et "par relations entre agents" sont reportés (SU007).
- L'application n'analyse pas la cohérence des parcours (SU005).

---

# Application

## FN001 : Lancer l'application
- **Description** : Lancer l'application.
- **Références** : SU001 (accueil).
- **Comportement attendu** :
    - Au lancement, l'application affiche un écran d'accueil permettant notamment de créer un nouveau projet.
- **État** : Implémenté.

## FN002 : Quitter l'application
- **Description** : Quitter l'application.
- **Références** : SU001 ; menu "Files › Quit" (Ctrl+Q).
- **Comportement attendu** :
    - Si le projet courant est modifié, l'application propose "Enregistrer", "Ne pas enregistrer", "Annuler" avant de quitter.
    - L'annulation conserve le projet ouvert et l'application en cours d'exécution.
- **État** : Implémenté.

## FN003 : Afficher l'historique des changements
- **Description** : Afficher l'historique des changements de chaque version de l'application.
- **Références** : menu "About › Change Log".
- **Comportement attendu** :
    - Une boîte de dialogue présente la liste des versions et les changements associés.
- **État** : Implémenté.

## FN004 : Afficher l'information "à propos"
- **Description** : Afficher le message d'information "à propos" de l'application.
- **Références** : menu "About › About Planoscript".
- **Comportement attendu** :
    - Une boîte de dialogue présente les informations générales de l'application.
- **État** : Implémenté.

---

# Projet

## FN005 : Créer un nouveau projet
- **Description** : Créer un nouveau projet narratif.
- **Références** : SU001 ; menu "Files › New Project..." (Ctrl+N) ; écran d'accueil.
- **Comportement attendu** :
    - Le projet peut être créé depuis le menu, le raccourci clavier ou l'écran d'accueil.
    - Le nouveau projet est un projet non enregistré : il réside en mémoire et n'est associé à aucun fichier tant que l'utilisateur ne l'enregistre pas.
    - Il est nommé "New project" et contient une carte narrative nommée "Main narrative map".
    - Un seul projet peut être ouvert à la fois ; la création d'un nouveau projet remplace le projet courant (avec confirmation de sauvegarde si modifié).
    - Le projet possède un identifiant stable, un nom, une date de création, une date de dernière modification et une version de format ; le chemin du fichier est un état applicatif, non une donnée métier.
- **État** : Implémenté.

## FN006 : Ouvrir un projet
- **Description** : Ouvrir un projet depuis le système de fichiers.
- **Références** : SU001 ; menu "Files› Open..." (Ctrl+O).
- **Comportement attendu** :
    - L'utilisateur choisit un fichier de projet valide sur le système de fichiers.
    - En cas de fichier invalide, incompatible ou illisible, l'application affiche un message d'erreur clair et conserve le projet courant inchangé.
    - Si le projet courant est modifié, une confirmation de sauvegarde est proposée avant l'ouverture.
- **État** : Implémenté.

## FN007 : Ouvrir un projet récent
- **Description** : Ouvrir un projet depuis la liste des projets récents.
- **Références** : SU001 ; menu "Files › Recents Projects...".
- **Comportement attendu** :
    - Le menu "Recent Files" présente une liste dynamique des projets précédemment enregistrés ou ouverts.
    - La liste respecte la limite configurée de projets récents.
    - Les fichiers n'existant plus sont retirés de la liste.
    - Le même traitement des fichiers invalides et des confirmations de sauvegarde que FN006 s'applique.
- **État** : Non implémenté (entrée de menu présente, fonctionnalité absente). Fonctionnalité requise par SU001 : à prévoir au planning.

## FN008 : Enregistrer le projet
- **Description** : Enregistrer le projet.
- **Références** : SU001 ; menu "Files › Save" (Ctrl+S).
- **Comportement attendu** :
    - Si le projet est déjà associé à un fichier, l'enregistrement s'effectue sans nouvelle boîte de dialogue.
    - Si le projet n'a jamais été enregistré, l'application demande un nom et un emplacement (comportement équivalent à FN009).
    - L'action est désactivée tant que le projet n'est pas modifié.
    - L'enregistrement ajoute le projet à la liste des projets récents.
- **État** : Implémenté.

## FN009 : Enregistrer le projet sous...
- **Description** : Enregistrer le projet sous un autre nom ou dans un autre emplacement.
- **Références** : SU001 ; menu "Files › Save As..." (Ctrl+Shift+S).
- **Comportement attendu** :
    - L'utilisateur choisit un nom et un emplacement.
    - La copie enregistrée devient le projet courant.
    - L'action ajoute le projet à la liste des projets récents.
- **État** : Implémenté.

## FN010 : Fermer le projet
- **Description** : Fermer le projet courant.
- **Références** : SU001 ; menu "Files › Close" (Ctrl+W).
- **Comportement attendu** :
    - Si le projet est modifié, l'application propose "Enregistrer", "Ne pas enregistrer", "Annuler".
    - Après fermeture, aucun projet n'est ouvert (retour à l'écran d'accueil).
- **État** : Implémenté.

## FN011 : Modifier le libellé du projet
- **Description** : Modifier le libellé (nom) du projet courant.
- **Références** : SU001 (attribut "name" du projet). **Hors menu** : aucune option de menu dédiée.
- **Comportement attendu** :
    - Le libellé du projet est un attribut métier modifiable via une fenêtre d'édition du projet (spécification de cette fenêtre à venir).
    - Toute modification du libellé met à jour la date de dernière modification et marque le projet comme modifié.
    - Le libellé n'est pas contraint à l'unicité.
- **État** : Non implémenté (fenêtre d'édition non définie).

---

# Carte narrative

## FN012 : Renommer la carte narrative
- **Description** : Renommer la carte narrative du projet.
- **Références** : SU002 (périmètre MVP : seul le renommage de la carte par défaut est disponible).
- **Comportement attendu** :
    - Le renommage s'effectue par édition directe du libellé ou via une boîte de dialogue dédiée.
    - Tout renommage marque la carte, et donc le projet, comme modifié, et met à jour les dates de dernière modification.
- **État** : Non documenté dans le menu.

## FN013 : Exporter la carte narrative en document de lecture
- **Description** : Exporter la carte narrative courante en document autonome de lecture, consultable dans un navigateur standard.
- **Références** : SU002 (export de carte), SU007 ; menu "Files › Export Map".
- **Comportement attendu** :
    - L'export est lancé depuis le menu "Files" (la barre d'outils n'existe pas en MVP).
    - L'export génère un dossier nommé d'après le nom de la carte, contenant un fichier index et toutes les pages nécessaires à la navigation hypertexte.
    - Le document est autonome : aucun serveur, aucune connexion Internet, aucune dépendance externe ; il s'affiche correctement dans Chrome, Firefox et Edge.
    - La page d'accueil propose le choix du mode de lecture ; en MVP, seul le mode "par parcours" est disponible.
    - En mode "parcours" : une page intermédiaire liste les parcours de la carte ; le choix d'un parcours affiche la séquence linéaire complète de ses composants.
    - Chaque composant est rendu par son libellé (titre de paragraphe) et sa description (corps de texte) ; si la description est vide, seul le libellé est affiché.
    - L'ordre de lecture est déterminé par la relation prédécesseur › successeur du modèle de données, indépendamment des positions graphiques.
    - Chaque page de lecture offre un lien de retour vers la table des matières.
    - L'export ne marque ni la carte ni le projet comme modifiés.
- **État** : Non implémenté.
- **Note** : l'export technique destiné à la réimportation (format autonome de carte) est reporté, de fait que l'import de carte narrative est exclu du MVP.

---

# Composants de la carte narrative

## FN014 : Créer un composant
- **Description** : Créer un composant de type agent, état ou événement dans la carte narrative.
- **Références** : SU003 ; menu "Project › Components... › Agent / State / Event".
- **Comportement attendu** :
    - En MVP, la création s'effectue exclusivement depuis le menu (pas de barre d'outils).
    - Le composant est créé avec un identifiant entier unique dans la carte, le libellé par défaut du type, et l'icône correspondant à son type.
    - Il est positionné à l'emplacement désigné par l'utilisateur, aligné sur la grille d'alignement (toujours visible et active).
    - Il est automatiquement rattaché au parcours actif ; un composant ne peut jamais exister hors d'un parcours.
    - Il présente deux ports d'attachement actifs : entrant (gauche) et sortant (droite).
    - Il n'est pas redimensionnable.
    - Toute création marque la carte, et donc le projet, comme modifié.
- **État** : Partiellement implémenté (création via menu, positionnée au centre de l'espace de travail — à aligner sur le comportement attendu "emplacement désigné par l'utilisateur").

## FN015 : Modifier les attributs d'un composant
- **Description** : Modifier les attributs éditables d'un composant via son panneau de propriétés.
- **Références** : SU003.
- **Comportement attendu** :
    - Le panneau de propriétés présente les attributs éditables selon le type du composant (agent, état, événement).
    - Le libellé n'est pas contraint à l'unicité au sein de la carte.
    - Toute modification d'attribut marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN016 : Dupliquer un composant
- **Description** : Dupliquer un composant existant.
- **Références** : SU003.
- **Comportement attendu** :
    - La copie porte un nom distinct et un nouvel identifiant.
    - La copie est rattachée au parcours actif.
    - Toute duplication marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN017 : Déplacer un composant
- **Description** : Positionner ou repositionner un composant dans l'espace de visualisation.
- **Références** : SU003, SU006.
- **Comportement attendu** :
    - Le déplacement s'effectue par glisser-déposer à la souris (PC), au stylet ou en mode tactile (tablette).
    - Lors du déplacement, le composant s'aligne automatiquement sur la grille.
    - La position (x, y) est conservée entre les sessions via le fichier de métadonnées graphiques associé au projet.
    - Le composant n'est pas redimensionnable.
    - Tout déplacement marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN018 : Supprimer un composant
- **Description** : Supprimer un composant de la carte narrative.
- **Références** : SU003.
- **Comportement attendu** :
    - Si des données sont associées au composant, une confirmation est demandée.
    - La suppression entraîne la suppression en cascade de toutes les relations reliant le composant aux autres composants.
    - Toute suppression marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN019 : Gérer l'appartenance d'un composant aux parcours
- **Description** : Modifier la liste des parcours auxquels un composant est rattaché.
- **Références** : SU003, SU005.
- **Comportement attendu** :
    - L'appartenance est gérée via une liste à choix multiple dans les propriétés du composant, parmi les parcours existants de la carte.
    - Un composant doit rester rattaché à au moins un parcours : le retrait du dernier rattachement est impossible (option non proposée ou action bloquée).
    - L'option est désactivée si la carte ne comporte qu'un seul parcours.
    - Toute modification de rattachement marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

---

# Relations entre composants

## FN020 : Créer une relation
- **Description** : Créer une relation orientée entre deux composants de la carte narrative.
- **Références** : SU004 ; menu "Project › Relations... › Connect State and Event".
- **Comportement attendu** :
    - En MVP, la création est initiée depuis le menu (pas de barre d'outils).
    - L'utilisateur sélectionne un composant source ; si aucun composant n'est actif, il devient actif. Un lien visuel suit alors le curseur jusqu'au clic sur le port d'attache du composant cible.
    - La relation est orientée : la sortie du composant source est connectée à l'entrée du composant cible.
    - L'application refuse la création si : source et cible sont identiques ; source et cible sont de même type (un état se connecte nécessairement à un événement, et réciproquement) ; une relation existe déjà entre les deux composants, dans le même sens ou dans le sens opposé.
    - La relation est représentée par une ligne ; elle suit les déplacements des composants qu'elle relie et n'est pas déplaçable en tant que telle.
    - Toute création marque la carte, et donc le projet, comme modifié.
- **État** : Implémenté (mode de création via menu).

## FN021 : Annoter et modifier une relation
- **Description** : Annoter une relation d'un texte libre et modifier ses attributs éditables.
- **Références** : SU004.
- **Comportement attendu** :
    - L'annotation s'effectue via le panneau de propriétés de la relation.
    - Le libellé de la relation est affiché dans une infobulle au survol de la ligne représentative.
    - Si une modification entraîne un changement de composant source ou cible, l'application émet une alerte, supprime implicitement la relation existante et crée une nouvelle relation avec les nouvelles extrémités.
    - Toute modification marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN022 : Supprimer une relation
- **Description** : Supprimer une relation entre deux composants.
- **Références** : SU004.
- **Comportement attendu** :
    - Une confirmation est demandée avant la suppression.
    - La suppression d'une relation est indépendante de celle des composants (hors cascade de FN018).
    - Toute suppression marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

---

# Parcours narratifs

## FN023 : Créer un parcours
- **Description** : Créer un parcours narratif dans la carte.
- **Références** : SU005 ; menu "Project" (la barre latérale de parcours n'existe pas en MVP).
- **Comportement attendu** :
    - Le nouveau parcours reçoit un identifiant unique, un nom par défaut et une description vide.
    - Le nouveau parcours est automatiquement activé et devient le parcours courant.
    - Tout composant créé par la suite est rattaché à ce parcours.
    - Toute création marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN024 : Renommer et décrire un parcours
- **Description** : Modifier le libellé et la description d'un parcours.
- **Références** : SU005.
- **Comportement attendu** :
    - La modification s'effectue via une boîte de dialogue ou un panneau de propriétés.
    - Toute modification marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN025 : Dupliquer un parcours
- **Description** : Dupliquer un parcours existant.
- **Références** : SU005.
- **Comportement attendu** :
    - La copie porte un nom distinct et un nouvel identifiant.
    - Les composants rattachés au parcours source sont également rattachés à la copie.
    - Toute duplication marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN026 : Activer un parcours
- **Description** : Activer un parcours comme parcours courant pour l'édition.
- **Références** : SU005 ; menu "Project" (la barre latérale de parcours n'existe pas en MVP).
- **Comportement attendu** :
    - L'activation s'effectue depuis la liste des parcours.
    - Le parcours activé devient le parcours courant : les nouveaux composants y sont rattachés et le filtrage d'affichage s'y applique (cf. FN029).
    - L'activation marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

## FN027 : Supprimer un parcours
- **Description** : Supprimer un parcours de la carte narrative.
- **Références** : SU005.
- **Comportement attendu** :
    - La suppression du dernier parcours de la carte est impossible : l'application affiche un message explicatif.
    - Dans les autres cas, une confirmation est demandée.
    - L'application identifie les composants rattachés exclusivement au parcours supprimé ; pour chacun, l'utilisateur choisit obligatoirement un nouveau parcours de rattachement via une fenêtre dédiée.
    - Toute suppression marque la carte, et donc le projet, comme modifié.
- **État** : Non documenté dans le menu.

---

# Visualisation

## FN028 : Naviguer dans l'espace de visualisation
- **Description** : Naviguer dans l'espace graphique de représentation de la carte narrative.
- **Références** : SU006.
- **Comportement attendu** :
    - La navigation s'effectue par les ascenseurs horizontal et vertical.
    - L'espace de visualisation est virtuellement illimité (dans les limites du système d'exploitation).
    - La grille d'alignement des composants est toujours visible et active.
    - Les positions des ascenseurs et le niveau de zoom ne constituent pas des données métier : ils ne sont pas conservés entre les sessions et ne marquent pas la carte comme modifiée.
    - L'interface reste pleinement fonctionnelle pour une fenêtre d'au moins 1280×720.
- **État** : Non documenté dans le menu (zoom non disponible en MVP).

## FN029 : Filtrer l'affichage par parcours
- **Description** : Afficher soit tous les composants et relations de la carte, soit seulement ceux du parcours actif.
- **Références** : SU006.
- **Comportement attendu** :
    - Le filtre permet de basculer entre "tout afficher" et "parcours actif".
    - Le cas échéant, la bascule d'un parcours à l'autre met à jour instantanément l'affichage : seuls les composants rattachés au parcours sélectionné et les relations entre ces composants sont représentés.
    - Le filtrage ne marque pas la carte comme modifiée.
- **État** : Non documenté dans le menu (section "Display › Journey" du menu ignorée en attendant sa correction).

---

# Hors périmètre MVP (reportées)

- Opérations multi-cartes : création, duplication, suppression et navigation entre plusieurs cartes narratives d'un même projet (SU001, SU002 — MVP : une seule carte par projet).
- Import de carte narrative depuis un fichier autonome (SU002 — retiré du MVP par décision du 08-09-2026).
- Export technique de carte destiné à la réimportation (SU007 — reporté, de fait de l'exclusion de l'import).
- Export de lecture "par événements" et "par relations entre agents" (SU007).
- Zoom de l'espace de visualisation (SU006).
- Barres d'outils "composants" et "parcours" (SU003, SU005 — actions par menu uniquement).
- Analyse de cohérence des parcours (SU005).
- Menu "Edit" (annuler, rétablir, historique, couper, copier, coller, supprimer) : absent des user stories et non implémenté ; à trancher (retrait du menu ou spécification ultérieure).
- Vue alternative "Relations" entre agents (SU006).
