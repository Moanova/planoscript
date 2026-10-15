# Règles de gestion - Planoscript

## Document Version
- **Version**: 2.1
- **Date**: 31-08-2026
- **Status**: Redesign

---

## 1. Gestion du projet et cycle de vie

## RG001
- **Description** : Un projet est un document local au format JSON contenant les métadonnées du projet et une ou plusieurs cartes narratives.
- **Classification** : Gestion du projet et cycle de vie.

## RG002
- **Description** : Un seul projet peut être ouvert dans l'application à tout moment.
- **Classification** : Gestion du projet et cycle de vie.

## RG003
- **Description** : Un projet nouvellement créé est un projet non enregistré : il existe en mémoire mais n'est associé à aucun fichier tant que l'utilisateur ne l'a pas sauvegardé.
- **Classification** : Gestion du projet et cycle de vie.

## RG004
- **Description** : Chaque projet possède un identifiant stable (UUID), un nom, une date de création, une date de dernière modification et une version de format.
- **Classification** : Gestion du projet et cycle de vie.

## RG005
- **Description** : Les projets enregistrés et ouverts avec succès sont ajoutés à la liste des projets récents. La liste est ordonnée du plus au moins récemment ouvert et ne contient qu'une occurrence de chaque fichier. Son nombre maximal d'entrées est défini par la configuration de l'application. Les entrées correspondant à un fichier inexistant, inaccessible ou invalide sont retirées de la liste.
- **Classification** : Gestion du projet et cycle de vie.

## RG006
- **Description** : La commande "Save" est activée uniquement lorsqu'un projet ouvert est modifié. La commande "Save as..." est activée lorsqu'un projet est ouvert, qu'il soit modifié ou non. Lorsqu'aucun projet n'est ouvert, ces deux commandes sont désactivées.
- **Classification** : Gestion du projet et cycle de vie.

## RG007
- **Description** : Lorsqu'aucun projet n'est ouvert, les entrées "Files\Close", "Files\Save", "Files\Save as...", "Files\Export map", "Edit\*", "Display\*" et "Project\*" du menu sont désactivées (grisées).
- **Classification** : Gestion du projet et cycle de vie.

## RG008
- **Description** : Lorsqu'un projet est ouvert ou qu'un nouveau projet est créé alors qu'aucun projet n'était préalablement ouvert, les entrées "Files\Close", "Files\Save", "Files\Export map", "Edit\*", "Display\*" et "Project\*" du menu sont activées.
- **Classification** : Gestion du projet et cycle de vie.

## RG009
- **Description** : L'ouverture d'un projet ne remplace le projet courant qu'après lecture et validation réussies du fichier sélectionné. Si le fichier est inexistant, inaccessible, invalide ou incompatible, une erreur est affichée à l'utilisateur et le projet courant reste inchangé.
- **Classification** : Gestion du projet et cycle de vie.

## RG010
- **Description** : Chaque fichier projet comporte une version de format. L'application ouvre un projet uniquement si cette version est supportée ou peut être migrée de manière fiable vers une version supportée. Une migration ne doit jamais écraser le fichier d'origine sans action explicite de l'utilisateur.
- **Classification** : Gestion du projet et cycle de vie.

## RG011
- **Description** : Une sauvegarde ne remplace le fichier existant qu'après écriture complète et réussie de la nouvelle version. En cas d'échec de sauvegarde, le fichier précédemment enregistré doit rester exploitable et le projet doit conserver son état modifié. Après une sauvegarde réussie, la date de dernière modification du projet est mise à jour.
- **Classification** : Gestion du projet et cycle de vie.

## RG012
- **Description** : L'action "Enregistrer sous..." crée ou remplace un fichier à l'emplacement choisi par l'utilisateur après confirmation si un fichier existe déjà. Après une sauvegarde réussie, le fichier nouvellement choisi devient le fichier associé au projet ouvert. Le fichier précédemment associé au projet n'est ni renommé ni supprimé.
- **Classification** : Gestion du projet et cycle de vie.

## RG013
- **Description** : Un nouveau projet est nommé "Nouveau projet" et contient une carte narrative nommée "Carte narrative principale".
- **Classification** : Gestion du projet et cycle de vie.

## RG014
- **Description** : Un projet contient toujours au moins une carte narrative.
- **Classification** : Gestion du projet et cycle de vie.

## RG046
- **Description** : L'application propose deux exports distincts : un export technique au format JSON (réimportable) et un export de lecture au format HTML (autonome).
- **Classification** : Gestion du projet et cycle de vie.

## RG047
- **Description** : L'export HTML génère un dossier nommé d'après la carte narrative, contenant un 'index.html' et les pages liées.
- **Classification** : Gestion du projet et cycle de vie.

## RG048
- **Description** : L'ordre de déroulement des parcours d'un export est déterminé par la séquence prédécesseur/successeur du modèle de données, indépendamment de la position graphique.
- **Classification** : Gestion du projet et cycle de vie.

## RG049
- **Description** : L'opération d'export ne marque pas la carte narrative ni le projet comme modifiés.
- **Classification** : Gestion du projet et cycle de vie.

## RG060
- **Description** : Avant de remplacer le projet courant (ex: ouverture d'un nouveau projet, création d'un nouveau projet, fermeture de l'application), l'application doit vérifier si le projet courant est modifié et non sauvegardé. Si c'est le cas, une alerte est affichée pour proposer à l'utilisateur de sauvegarder, ignorer les modifications, ou annuler l'opération.
- **Classification** : Gestion du projet et cycle de vie.

---