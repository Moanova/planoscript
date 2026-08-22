# Planoscript ::: Comportements attendus


## CM001 : Comportement attendu pour FN001
- **Étapes** :
  1. L'utilisateur clique sur le raccourci de l'application ou lance la commande de l'exécutable de l'application.
  2. La fenêtre d'application est ouverte au milieu de l'écran.
  3. Les entrées du menu spécifiques aux projets ouverts sont désactivées (grisées).
  4. Les icônes des barres d'outils sont désactivées (grisées).
  5. Un message d'accueil est affiché dans l'espace de travail avec un lien hypertexte pour la création d'un nouveau projet.
- **Critères d'acceptation** :
  - La fenêtre de l'application s'ouvre avec l'espace de travail vide.
  - Les entrées du menu et les icônes des barres d'outils sont désactivées (à l'exception des entrées du menu toujours actives).
  - Le message d'accueil permet de créer un nouveau projet (même action que celle de l'entrée "Nouveau..." du menu "Fichiers").


## CM002 : Comportement attendu pour FN002
- **Étapes** :
  1. L'utilisateur clique sur l'icône de fermeture de la fenêtre d'application ou sur l'entrée "Quitter" du menu Fichiers.
  2. Si le projet ouvert est modifié, une fenêtre de dialogue s'ouvre pour demander s'il doit être enregistré ou non. Sinon, action 6.
  3. Si l'utilisateur demande l'annulation, l'action est annulée.
  4. Si l'utilisateur demande l'enregistrement, le projet est enregistré, avec ou sans fenêtre de dialogue selon qu'il a déjà été enregistré une première fois ou non.
  5. Si l'utilisateur ne demande pas l'enregistrement, le projet n'est pas enregistré.
  6. La fenêtre de l'application est fermée et l'exécution de l'application prend fin.
- **Critères d'acceptation** :
  - La fenêtre de l'application se ferme après sauvegarde des projets modifiés s'il y a lieu.


## CM003 : Comportement attendu pour FN003
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "Historique des changements" du menu "À propos".
  2. Une fenêtre fille de la fenêtre d'application est ouverte et affiche le contenu du journal des changements avec une barre de défilement verticale
  3. Si l'utilisateur clique sur le bouton "Ok", la fenêtre est fermée.
- **Critères d'acceptation** :
  - La fenêtre fille s'ouvre avec le contenu du journal des changements.
  - La fenêtre se ferme quand l'utilisateur clique sur le bouton "Ok".


## CM004 : Comportement attendu pour FN004
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "À propos de Planoscript" du menu "À propos".
  2. Une fenêtre fille de la fenêtre d'application est ouverte et affiche le contenu du message avec une barre de défilement verticale
  3. Si l'utilisateur clique sur le bouton "Ok", la fenêtre est fermée.
- **Critères d'acceptation** :
  - La fenêtre fille s'ouvre avec le contenu du journal des changements.
  - La fenêtre se ferme quand l'utilisateur clique sur le bouton "Ok".


## CM005 : Comportement attendu pour FN005
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "Nouveau projet..." du menu Fichiers.
  2. Si un projet d'initialisation est ouvert, il est fermé.
  3. Si un projet est ouvert et modifié, une fenêtre de dialogue s'ouvre pour demander s'il doit être enregistré ou non. Sinon, action 7.
  4. Si l'utilisateur demande l'annulation, l'action est annulée.
  5. Si l'utilisateur demande l'enregistrement, le projet est enregistré, avec ou sans fenêtre de dialogue selon qu'il a déjà été enregistré une première fois ou non.
  6. Si l'utilisateur ne demande pas l'enregistrement, le projet est fermé sans être enregistré.
  7. Un nouveau projet d'initialisation est ouvert.
- **Critères d'acceptation** :
  - Un projet d'initialisation est créé et le projet qui était ouvert s'il y en avait un est fermé après avoir été enregistré si nécessaire et demandé par l'utilisateur.


## CM006 : Comportement attendu pour FN006
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "Ouvrir..." du menu Fichiers.
  2. Si un projet d'initialisation est ouvert, il est fermé.
  3. Si un projet est ouvert et modifié, une fenêtre de dialogue s'ouvre pour demander s'il doit être enregistré ou non. Sinon, action 7.
  4. Si l'utilisateur demande l'annulation, l'action est annulée.
  5. Si l'utilisateur demande l'enregistrement, le projet est enregistré, avec ou sans fenêtre de dialogue selon qu'il a déjà été enregistré une première fois ou non.
  6. Si l'utilisateur ne demande pas l'enregistrement, le projet est fermé sans être enregistré.
  7. Le projet sélectionné est ouvert.
- **Critères d'acceptation** :
  - Le projet sélectionné est ouvert et le projet qui était ouvert s'il y en avait un est fermé après avoir été enregistré si nécessaire et demandé par l'utilisateur.


## CM007 : Comportement attendu pour FN007
- **Étapes** :
  1. L'utilisateur clique sur le raccourci du projet à ouvrir dans le menu Fichiers.
  2. Si un projet d'initialisation est ouvert, il est fermé.
  3. Si un projet est ouvert et modifié, une fenêtre de dialogue s'ouvre pour demander s'il doit être enregistré ou non. Sinon, action 7.
  4. Si l'utilisateur demande l'annulation, l'action est annulée.
  5. Si l'utilisateur demande l'enregistrement, le projet est enregistré, avec ou sans fenêtre de dialogue selon qu'il a déjà été enregistré une première fois ou non.
  6. Si l'utilisateur ne demande pas l'enregistrement, le projet est fermé sans être enregistré.
  7. Le projet sélectionné est ouvert.
- **Critères d'acceptation** :
  - Le projet sélectionné est ouvert et le projet qui était ouvert s'il y en avait un est fermé après avoir été enregistré si nécessaire et demandé par l'utilisateur.


## CM008 : Comportement attendu pour FN008
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "Enregistrer" du menu Fichiers.
  2. Si le projet n'a jamais été enregistré, une fenêtre de dialogue s'ouvre pour sélectionner le nom et le chemin d'enregistrement. Sinon, il est enregistré sans dialogue avec les nom et chemin existants.
  3. Le projet est enregistré.
- **Critères d'acceptation** :
  - Le projet est enregistré dans le dossier demandé avec le nom demandé.


## CM009 : Comportement attendu pour FN009
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "Enregistrer sous..." du menu Fichiers.
  2. Une fenêtre de dialogue s'ouvre pour sélectionner le nom et le chemin d'enregistrement, même si le projet a déjà été enregistré préalablement.
  3. Le projet est enregistré.
- **Critères d'acceptation** :
  - Le projet est enregistré dans le dossier demandé avec le nom demandé.


## CM010 : Comportement attendu pour FN010
- **Étapes** :
  1. L'utilisateur clique sur l'entrée "Fermer" du menu Fichiers.
  2. Si le projet a été modifié, une fenêtre de dialogue est ouverte pour demander son enregistrement ou non, ou l'annulation de l'action. Si la réponse est non, aller à l'étape 6. Sur demande d'annulation, interrompre l'action.
  3. Si l'utilisateur a demandé l'enregistrement du projet et que celui-ci n'a jamais été enregistré, une fenêtre de dialogue s'ouvre pour sélectionner le nom et le chemin d'enregistrement. Sur demande d'annulation, fin de l'action.
  4. Si l'utilisateur a demandé l'enregistrement du projet et que celui-ci a déjà été enregistré, il est enregistré sous son nom et au chemin définis.
  5. Le projet est enregistré s'il a été modifié et que l'utilisateur a demandé son enregistrement.
  6. Le projet est fermé.
- **Critères d'acceptation** :
  - Le projet est fermé après avoir été enregistré si nécessaire et demandé par l'utilisateur.
