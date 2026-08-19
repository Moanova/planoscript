# Planoscript ::: Scenarii d'utilisation


## SU001 : Gérer un projet narratif
- **Description** : En tant qu'auteur, je peux créer, ouvrir, enregistrer, renommer, fermer ou supprimer un projet narratif afin de regrouper, retrouver et poursuivre le travail sur mes cartes narratives.
- **Complément** :
    - Un projet est un document local contenant les métadonnées du projet et une ou plusieurs cartes narratives.
    - Un seul projet peut être ouvert dans l'application à un instant donné.
    - Un projet nouvellement créé est un projet non enregistré : il existe en mémoire mais n'est associé à aucun fichier tant que l'utilisateur ne l'a pas sauvegardé.
    - Chaque projet possède un identifiant stable, un nom, une date de création, une date de dernière modification et une version de format.
    - Le chemin du fichier est un état de l'application ; il ne constitue pas une donnée métier portable du projet.
    - Un nouveau projet est nommé « Nouveau projet » et contient une carte narrative nommée « Carte narrative principale ».
- **Critères d'acceptation** :
    - L'utilisateur peut créer un projet depuis le menu, un raccourci clavier ou le message d'accueil.
    - L'utilisateur peut ouvrir un fichier projet valide depuis le système de fichiers.
    - En cas de fichier invalide, incompatible ou illisible, l'application affiche une erreur claire et conserve le projet ouvert inchangé.
    - L'utilisateur peut enregistrer un projet non enregistré en choisissant un nom et un emplacement.
    - L'utilisateur peut enregistrer les modifications d'un projet déjà associé à un fichier sans nouvelle boîte de dialogue.
    - L'utilisateur peut enregistrer une copie sous un autre nom ou dans un autre emplacement ; cette copie devient le projet ouvert courant.
    - L'utilisateur peut fermer un projet.
    - Si le projet est modifié lors d'une fermeture, d'une ouverture, d'une création ou d'une sortie, l'application propose : Enregistrer, Ne pas enregistrer, Annuler.
    - Un projet enregistré est ajouté à la liste des projets récents.
    - La liste des projets récents respecte la limite configurée et retire les fichiers qui n'existent plus.
    - L'utilisateur peut supprimer un projet depuis l'application après confirmation explicite. Le fichier projet et ses fichiers auxiliaires sont envoyés à la corbeille, puis retirés des projets récents.
- **Fonctionnalités associées** :
    - [ FN005 ] : Créer un nouveau projet.
    - [ FN006 ] : Ouvrir un projet depuis le système de fichiers.
    - [ FN007 ] : Ouvrir un projet de la liste des projets récents.
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.
    - [ FN010 ] : Fermer le projet.
    - [ FN011 ] : Supprimer un projet.
- **Règles de gestion associées** :
    - [ RG001 ] à [ RG006 ]
    - [ RG013 ] à [ RG018 ]


## SU002 : Gérer une carte narrative.
- **Description** : En tant qu'auteur, je peux créer, modifier ou supprimer une carte narrative afin de structurer mon récit.
- **Complément** :
    - Chaque carte est nommée.
    - La grille d'alignement des composants dans l'espace de visualisation est toujours visible et active.
- **Critères d'acceptation** :
    - la création des composants, leur visualisation et le glisser-déposer fonctionnent sans latence notable (<= 200 ms).
    - Chaque carte peut être créée, dupliquée, modifiée ou supprimée à partir du menu général et de la barre d'outils, ou bien du menu contextuel lorsqu'aucune carte n'est chargée.
    - Chaque carte peut être sauvegardée dans un dossier utilisateur.
    - Chaque carte sauvegardée dans un dossier utilisateur peut être importée dans un projet.


## SU003 : Gérer un composant de carte narrative.
- **Description** : En tant qu'auteur, je peux créer, modifier ou supprimer un composant de carte narrative afin de définir le contenu de mon récit.
- **Complément** :
    - Le type des composants est défini par le modèle de données applicatif, i.e
      - référence temporelle,
      - référence spatiale,
      - agent,
      - état,
      - évènement.
    - Chaque composant unitaire est nommé et sa description est en format texte libre.
    - Chaque composant est représenté par une îcone spécifique à son type.
    - Chaque composant est déplaçable dans l'espace de visualisation mais non dimensionnable.
    - Chaque composant est porteur de quatre points d'accroche pour gérer ses relations (gauche, droite, haut, bas), chacun matérialisé par un petit carré actif.
- **Critères d'acceptation** :
    - Chaque composant peut être positionné et repositionné par sélection au moyen d'une souris (sur PC), d'un stylet et de façon tactile (sur tablette).
    - Chaque composant peut être créé, dupliqué, modifié ou supprimé à partir du menu général, de la barre d'outils ou du menu contextuel.
    - Chaque composant fait toujours partie d'au moins un parcours.


## SU004 : Gérer une relation entre composants de carte narrative.
- **Description** : En tant qu'auteur je peux créer, modifier ou supprimer une relation entre composants de carte narrative afin de définir les enchaînements et les relations de mon récit.
- **Complément** :
    - Chaque relation est établie entre les points d'accroche respectifs des composants associés.
    - Chaque relation peut être annotée par du texte libre.
    - Les relations des composants entre eux peuvent être directionnelles ou non selon les règles de gestion spécifiques.
- **Critères d'acceptation** :
    - La visualisation des relations est optimisée pour maximiser leur lisibilité et minimiser les chevauchements.
    - Chaque relation peut être créée, modifiée ou supprimée à partir du menu général, de la barre d'outils ou du menu contextuel pour le composant sélectionné.
    - Chaque relation fait toujours partie d'au moins un parcours.


## SU005 : Gérer un parcours narratif.
- **Description** : En tant qu'auteur, je peux créer, modifier ou supprimer un parcours narratif afin de structurer les alternatives de mon récit.
- **Complément** :
    - Chaque carte contient toujours au moins un parcours.
    - Chaque parcours est défini par un sous-ensemble des composants et des relations de la carte auquel il apartient, et qui définissent une version spécifique du réçit.
    - Chaque composant et chaque relation de la carte peut faire partie de tous les parcours, de plusieurs ou d'un seul.
- **Critères d'acceptation** :
    - Chaque composant ou relation créée est automatiquement rattaché au parcours par défaut de la carte narrative.
    - Le parcours par défaut est initialisé par l'application mais peut être modifié par l'utilisateur.
    - Chaque parcours peut être créé, modifié ou supprimé à partir du menu général, de la barre des parcours ou du menu contextuel à partir du composant ou de la relation sélectionnée.
    - En cas de suppression d'un parcours lorsqu'il y en a plusieurs, alors tous les composants et relations associées doivent être réassociées à un nouveau parcours.
    - En cas de suppression de parcours lorsqu'il n'y en a qu'un seul, alors un nouveau parcours par défaut est automatiquement créé, et tous les composants et toutes les relations y sont rattachés.
    - La bascule d'un parcours à un autre est possible à partir du menu général, de la barre des parcours ou du menu contextuel.


## SU006 : Visualiser une carte narrative.
- **Description** : En tant qu'auteur, je peux visualiser une carte narrative afin de valider mon récit.
- **Complément** :
    - La visualisation peut êre orientée parcours ou relations.
	- Une visualisation additionnelle représente l'enchaînement des chapitres et des parcours constituant un chapitre.
    - L'espace de visualisation est virtuellement illimité (limité par les capacités du système d'exploitation).
    - La navigation dans l'espace de visualisation est possible au moyen de barres de défilement horizontal et vertical.
    - La visualisation peut être réduite ou agrandie au moyen du menu d'affichage, de la barre de zoom, de la molette de la souris (sur PC), ou par mouvement tactile (sur tablette).
    - Chaque composant de le carte est positionné dans l'espace de visualisation sur une grille d'alignement de 20 pixels sur 20.
    - En mode parcours, la visualisation de la carte peut être limitée à un, plusieurs ou tous les parcours à partir de la barre des parcours selon le choix de l'utilisateur.
	- En mode relations, la visualisation de la carte peut être limitée à une, plusieurs ou toutes les relations à partir de la barre des relations selon le choix de l'utilisateur.
- **Critères d'acceptation** :
    - La visualisation s’adapte aux supports et aux tailles d’écran sans perte de fonctionnalité.
      - PC : 1280x720 (HD), 1920x1080 (Full HD), 2560x1440 (QHD).
      - Tablette : 1024x768 (iPad), 2048x1536 (iPad Pro), 1200x1920 (Android).
    - La visualisation passe en mode portrait ou paysage sans perte de fonctionnalité (ex : les barres d’outils restent accessibles).
    - L'espace de visualisation peut être déployé jusqu’à 10 000 x 10 000 pixels sans crash.
    - Le temps de réponse est acceptable sur tous les appareils (le chargement d'une séquence de 250 composants prend une seconde au plus sur PC et deux secondes au plus sur tablette).


## SU007 : Exporter une carte narrative.
- **Description** : En tant qu'auteur, je peux exporter une carte narrative afin de la lire au format hypertexte.
- **Complément** :
    - Le document d'export est autonome et ne nécessite ni serveur ni dépendance externe.
    - Le document d'export contient les métadonnées de la carte narrative.
    - Le document d'export est lisible directement dans un navigateur standard.
    - Le document d'export débute par un sommaire afin de sélectionner le parcours à dérouler.
	- Le document d'export propose le déroulement des réçits selon la vue parcours ou bien la vue relations.
- **Critères d'acceptation** :
    - Le document d'export est compatible avec tous les navigateurs courants.
    - Le document d'export permet de dérouler chaque parcours de façon linéaire.
    - Le document d'export est nommé d'après le nom physique de la carte narrative.
