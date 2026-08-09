# Planoscript ::: Scenarii d'utilisation


##SU001 : Créer un projet
- **Description** : En tant qu'auteur, je peux créer, modifier ou supprimer un projet afin de construire un réçit.
- **Complément** :
    - Chaque projet est nommé.
    - Chaque projet peut contenir une ou plusieurs cartes narratives.
- **Critères d'acceptation** :
    - Chaque projet peut être sauvegardé dans un dossier utilisateur.
    - Chaque projet sauvegardé peut être ouvert depuis son dossier utilisateur.
    - Les derniers projets récemment créés ou modifiés peuvent être ouverts par raccourci.
- **Fonctionnalitées associées** :
    - [ FN005 ] : Créer un nouveau projet d'initialisation.
    - [ FN006 ] : Ouvrir un projet depuis le système de fichiers.
    - [ FN007 ] : Ouvrir un projet de la liste des projets récents.
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.
    - [ FN010 ] : Fermer le projet.


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
