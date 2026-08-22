# Règles de gestion - Planoscript


## RG001
- **Description** :
    Un projet créé par l'utilisateur est un projet non enregistré.
    Il possède un identifiant, le libellé « Nouveau projet », une date de création et une carte narrative nommée « Carte narrative principale ».
    Un projet non enregistré n'est associé à aucun fichier sur le système de fichiers.
    Sa création seule ne le marque pas comme modifié.
- **Fonctionnalités associées** :
    - [ FN005 ] : Créer un nouveau projet.



## RG002
- **Description** :
    L'application ne peut ouvrir qu'un seul projet à la fois.
    Lorsqu'un utilisateur crée un projet, ouvre un projet ou sélectionne un projet récent alors qu'un autre projet est ouvert, le projet courant doit être fermé avant l'ouverture du nouveau projet.
    Si le projet courant est modifié, l'utilisateur peut l'enregistrer, fermer sans enregistrer ou annuler l'action.
- **Fonctionnalités associées** :
    - [ FN005 ] : Créer un nouveau projet.
    - [ FN006 ] : Ouvrir un projet.
    - [ FN007 ] : Ouvrir un projet récent.
    - [ FN010 ] : Fermer le projet.
    - [ FN002 ] : Quitter l'application.


## RG003
- **Description** :
    Un projet non enregistré devient un projet enregistré lorsqu'il est sauvegardé avec succès dans un fichier choisi par l'utilisateur.
    À partir de cette sauvegarde, le projet est associé à ce fichier et peut être enregistré directement à la même adresse.
    Le chemin du fichier est un état de l'application ; il ne constitue pas une donnée métier portable du projet et ne doit pas être utilisé comme identifiant du projet.
- **Fonctionnalités associées** :
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


## RG004
- **Description** :
    Un projet est considéré comme modifié lorsqu'une donnée persistée diffère de sa dernière version enregistrée.
    Sont notamment concernés la création, modification ou suppression d'une carte narrative, d'un composant, d'une relation, d'un parcours ou d'un chapitre, ainsi que la modification d'une donnée de présentation persistée telle que la position d'un composant ou la configuration d'une vue.
    Un projet chargé depuis un fichier ou sauvegardé avec succès n'est pas modifié.
- **Fonctionnalités associées** :
    - À associer à toutes les fonctionnalités modifiant les données du projet.


## RG005
- **Description** :
    Les projets enregistrés et ouverts avec succès sont ajoutés à la liste des projets récents.
    La liste est ordonnée du plus récemment ouvert au moins récemment ouvert et ne contient qu'une occurrence de chaque fichier.
    Son nombre maximal d'entrées est défini par la configuration de l'application.
    Les entrées correspondant à un fichier inexistant, inaccessible ou invalide sont retirées de la liste.
- **Fonctionnalités associées** :
    - [ FN006 ] : Ouvrir un projet.
    - [ FN007 ] : Ouvrir un projet récent.
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


## RG006
- **Description** :
    La commande « Enregistrer » est activée uniquement lorsqu'un projet ouvert est modifié.
    La commande « Enregistrer sous… » est activée lorsqu'un projet est ouvert, qu'il soit modifié ou non.
    Lorsqu'aucun projet n'est ouvert, ces deux commandes sont désactivées.
- **Fonctionnalités associées** :
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


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


## RG013
- **Description** :
    L'identifiant du projet est stable pendant toute sa durée de vie.
    Renommer, enregistrer sous un autre nom ou déplacer le fichier d'un projet ne modifie pas son identifiant.
    Le nom du fichier et le chemin de sauvegarde peuvent différer du libellé affiché du projet.
- **Fonctionnalités associées** :
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


## RG014
- **Description** :
    L'ouverture d'un projet ne remplace le projet courant qu'après lecture et validation réussies du fichier sélectionné.
    Si le fichier est inexistant, inaccessible, invalide ou incompatible, une erreur est affichée à l'utilisateur et le projet courant reste inchangé.
- **Fonctionnalités associées** :
    - [ FN006 ] : Ouvrir un projet.
    - [ FN007 ] : Ouvrir un projet récent.


## RG015
- **Description** :
    Chaque fichier projet comporte une version de format.
    L'application ouvre un projet uniquement si cette version est supportée ou peut être migrée de manière fiable vers une version supportée.
    Une migration ne doit jamais écraser le fichier d'origine sans action explicite de l'utilisateur.
- **Fonctionnalités associées** :
    - [ FN006 ] : Ouvrir un projet.
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


## RG016
- **Description** :
    Une sauvegarde ne remplace le fichier existant qu'après écriture complète et réussie de la nouvelle version.
    En cas d'échec de sauvegarde, le fichier précédemment enregistré doit rester exploitable et le projet doit conserver son état modifié.
    Après une sauvegarde réussie, la date de dernière modification du projet est mise à jour.
- **Fonctionnalités associées** :
    - [ FN008 ] : Enregistrer le projet.
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.


## RG017
- **Description** :
    L'action « Enregistrer sous… » crée ou remplace un fichier à l'emplacement choisi par l'utilisateur après confirmation si un fichier existe déjà.
    Après une sauvegarde réussie, le fichier nouvellement choisi devient le fichier associé au projet ouvert.
    Le fichier précédemment associé au projet n'est ni renommé ni supprimé.
- **Fonctionnalités associées** :
    - [ FN009 ] : Enregistrer le projet sous un nom explicite.
