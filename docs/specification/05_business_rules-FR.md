# Règles de gestion - Planoscript


## RG001
- **Description** :
    Un projet d'initialisation est caractérisé par la valorisation des attributs "id", "lb" et "creation_date_time" avec l'attribut narrative_map non renseigné.
    La valeur de l'attribut "id" est renseignée à la création par l'application.
    La valeur de l'attribut "lb" est renseignée à "Nouveau projet".
    La valeur de l'attribut "creation_date_time" est renseignée avec la date et l'heure de création du projet par l'application.
- **Fonctionnalités associées** :
    - [ FN005 ] : Créer un nouveau projet.



## RG002
- **Descrpition** :
    Lorsque le projet ouvert est le projet d'initialisation et qu'un projet est à créer ou à ouvrir, alors le projet d'initialisation est préalablement fermé.
- **Fonctionnalités associées** :
    - [ FN005 ] : Créer un nouveau projet.
    - [ FN006 ] : Ouvrir un projet.
    - [ FN007 ] : Ouvrir un projet récent.


## RG003
- **Description** :
    Si au moins une modification est apportée à un projet d'initialisation ou s'il a été enregistré sur le système de fichiers par l'utilisateur même sans modification, il n'est plus considéré comme tel.
- **Fonctionnalités associées** :
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


## RG004
- **Description** :
    Un projet est considéré comme modifié lorsque sa structure diffère de celle du projet d'initalisation ou de la version qui est enregistrée sur le système de fichiers.
- **Fonctionnalités associées** :
    - A définir


## RG005
- **Description** :
    Les n projets ouverts et enregistrés lors des utilisations précédentes de l'application peuvent être réouverts directement par un raccourci du menu Fichiers.
    Avec n un paramètre de configuration de l'application.
- **Fonctionnalités associées** :
    - [ FN007 ] : Ouvrir un projet récent.


## RG006
- **Description** :
    Si le projet n'a pas été modifié, l'option "Enregistrer" du menu Fichiers est désactivée. Sinon, elle est activée.
- **Fonctionnalités associées** :
    - [ FN008 ] : Enregistrer le projet.


## RG007
- **Description** :
    Lorsqu'aucun projet n'est ouvert, les entrées suivantes du menu sont désactivées (grisées).
      - Fichiers\Fermer
      - Fichiers\Enregistrer
      - Fichiers\Enregistrer sous...
      - Fichiers\Exporter carte
      - Édition\Annuler
      - Édition\Rétablir
      - Édition\Historique
      - Édition\Couper
      - Édition\Copier
      - Édition\Coller
      - Édition\Supprimer
      - Affichage\Parcours\ListeParcours
      - Affichage\Zoom\Zoom avant
      - Affichage\Zoom\Zoom arrière
      - Affichage\Zoom\Restaurer zoom
      - Projet\Vue\Carte des parcours
      - Projet\Vue\Carte des relations
      - Projet\Vue\Chapitres
      - Projet\Composants...\Réf. temporelle
      - Projet\Composants...\Réf. spatiale
      - Projet\Composants...\Agent
      - Projet\Composants...\État
      - Projet\Composants...\Évènement
      - Projet\Relations...\Agent à agent
      - Projet\Relations...\Agent à état
      - Projet\Relations...\État à évènement
- **Fonctionnalités associées** :
    - [ FN001 ] : Lancer l'application


## RG008
- **Description** :
    Lorsqu'un projet est ouvert ou qu'un nouveau projet est créé alors qu'aucun projet n'était préalablement ouvert, les entrées suivantes du menu sont activées (grisées).
      - Fichiers\Fermer
      - Fichiers\Enregistrer sous...
      - Fichiers\Exporter carte
      - Édition\Couper
      - Édition\Copier
      - Édition\Coller
      - Affichage\Parcours\ListeParcours
      - Affichage\Zoom\Zoom avant
      - Affichage\Zoom\Zoom arrière
      - Affichage\Zoom\Restaurer zoom
      - Projet\Vue\Carte des parcours
      - Projet\Vue\Carte des relations
      - Projet\Vue\Chapitres
      - Projet\Composants...\Réf. temporelle
      - Projet\Composants...\Réf. spatiale
      - Projet\Composants...\Agent
      - Projet\Composants...\État
      - Projet\Composants...\Évènement
      - Projet\Relations...\Agent à agent
      - Projet\Relations...\Agent à état
      - Projet\Relations...\État à évènement
- **Fonctionnalités associées** :
    - [ FN005 ] : Créer un nouveau projet.
    - [ FN006 ] : Ouvrir un projet.
    - [ FN007 ] : Ouvrir un projet récent.


## RG009
- **Description** :
    Lorsqu'un composant est créé dans l'espace de travail, il est automatiquement sélectionné. Si un autre composant est déjà sélectionné, alors il est déselectionné.
    Lorsqu'un composant est sélectionné et que l'utilisateur clique sur l'espace de travail en dehors de tout composant, alors il est déselectionné.
    Lorsque l'utilisateur clique sur un composant de l'espace qui n'est pas sélectionné, alors il est sélectionné.  Si un autre composant est déjà sélectionné, alors il est déselectionné.
    A tout moment, il y a 0 ou 1 composant sélectionné dans l'espace de travail.
- **Fonctionnalités associées** : indéterminé à date.


## RG010
- **Description** :
    Lorsqu'un composant est créé dans l'espace de travail et que ses coordonnées chevauchent celle d'un autre composant, alors elles sont modifiées pour éviter le chevauchement en laissant un espace entre les deux composants.
	La translation des coordonnées est latérale ou verticale selon ce qui est permis par les limites de l'espace de travail.
- **Fonctionnalités associées** : indéterminé à date.


## RG011
- **Description** :
    Un composant ne peut jamais être déplacé par l'utilisateur en dehors des limites de l'espace de travail. Les coordonnées de chaque composant sont toujours telles qu'il est défini dans son intégralité dans l'espace de travail.
- **Fonctionnalités associées** : indéterminé à date.


## RG012
- **Description** :
    Lorsqu'un composant est déplacé par l'utilisateur et que ses coordonnées dépassent la partie visible de l'espace de travail, alors la barre de défilement correspondante, latérale ou verticale, est activée selon les coordonnées courantes du composant.
- **Fonctionnalités associées** : indéterminé à date.
