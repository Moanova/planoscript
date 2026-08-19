# Planoscript ::: Fonctionnalités


## FN001 : Lancer l'application
- **Description** : Lancer l'application.
- **Comportement attendu** :
    - [ CM001 ] : Comportement attendu pour FN001.


## FN002 : Quitter l'application
- **Description** : Quitter l'application.
- **Comportement attendu** :
    - [ CM002 ] : Comportement attendu pour FN002.


## FN003 : Afficher l'historique des changements
- **Description** : Afficher l'historique des changements de chaque version de l'application.
- **Comportement attendu** :
    - [ CM003 ] : Comportement attendu pour FN003.


## FN004 : Afficher l'information "à propos"
- **Description** : Afficher le message d'information "à propos" de l'application.
- **Comportement attendu** :
    - [ CM004 ] : Comportement attendu pour FN004.


## FN005 : Créer un nouveau projet
- **Description** : Créer un nouveau projet d'initialisation.
- **Comportement attendu** :
    - [ CM005 ] : Comportement attendu pour FN005.


## FN006 : Ouvrir un projet
- **Description** : Ouvrir un projet depuis le système de fichiers.
- **Comportement attendu** :
    - [ CM006 ] : Comportement attendu pour FN006.


## FN007 : Ouvrir un projet récent
- **Description** : Ouvrir un projet de la liste des projets récents.
- **Comportement attendu** :
    - [ CM007 ] : Comportement attendu pour FN007.


## FN008 : Enregistrer le projet
- **Description** : Enregistrer le projet.
- **Comportement attendu** :
    - [ CM008 ] : Comportement attendu pour FN008.


## FN009 : Enregistrer le projet sous un nom explicite
- **Description** : Enregistrer le projet sous un nom explicite.
- **Comportement attendu** :
    - [ CM009 ] : Comportement attendu pour FN009.


## FN010 : Fermer le projet
- **Description** : Fermer le projet.
- **Comportement attendu** :
    - [ CM010 ] : Comportement attendu pour FN010.


## FN011 : Supprimer un projet
- **Description** :
  Supprimer un projet enregistré et ses fichiers auxiliaires associés depuis
  l’application.

  La suppression s’applique uniquement à un projet associé à un fichier.
  Un projet non enregistré ne peut pas être supprimé : il peut seulement être
  fermé sans être enregistré.

  Le projet à supprimer ne doit pas être ouvert. S’il est ouvert, il doit être
  fermé avant de pouvoir être supprimé.

- **Comportement attendu** :
  - [ CM011 ] : Comportement attendu pour FN011.

- **Règles de gestion associées** :
  - [ RG002 ] : Remplacement du projet courant.
  - [ RG005 ] : Projets récents.
  - [ RG018 ] : Suppression d’un projet.
