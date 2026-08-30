# Règles de gestion - Planoscript

## Document Version
- **Version**: 2.0
- **Date**: 30-08-2026
- **Status**: Redesign

---

## RG01
- **Description** : Un projet est un document local au format JSON contenant les métadonnées du projet et une ou plusieurs cartes narratives.
- **Classification** : Logique applicative et données.

## RG002
- **Description** : Un seul projet peut être ouvert dans l'application à tout moment.
- **Classification** : Logique applicative et données.

## RG003
- **Description** : Un projet nouvellement créé est un projet non enregistré : il existe en mémoire mais n'est associé à aucun fichier tant que l'utilisateur ne l'a pas sauvegardé.
- **Classification** : Logique applicative et données.

## RG004
- **Description** : Chaque projet possède un identifiant stable (UUID), un nom, une date de création, une date de dernière modification et une version de format.
- **Classification** : Logique applicative et données.

## RG005
- **Description** : Le chemin du fichier est un état de l'application ; il ne constitue pas une donnée métier portable du projet.
- **Classification** : Logique applicative et données.

## RG006
- **Description** : Les projets enregistrés et ouverts avec succès sont ajoutés à la liste des projets récents. La liste est ordonnée du plus récemment ouvert au moins récemment ouvert et ne contient qu'une occurrence de chaque fichier. Son nombre maximal d'entrées est défini par la configuration de l'application. Les entrées correspondant à un fichier inexistant, inaccessible ou invalide sont retirées de la liste.
- **Classification** : Logique applicative et données.

## RG007
- **Description** : La commande "Save" est activée uniquement lorsqu'un projet ouvert est modifié. La commande "Save as..." est activée lorsqu'un projet est ouvert, qu'il soit modifié ou non. Lorsqu'aucun projet n'est ouvert, ces deux commandes sont désactivées.
- **Classification** : Logique applicative et données.

## RG008
- **Description** : Lorsqu'aucun projet n'est ouvert, les entrées "Files\Close", "Files\Save", "Files\Save as...", "Files\Export map", "Edit\*", "Display\*" et "Project\*" du menu sont désactivées (grisées).
- **Classification** : Logique applicative et données.

## RG009
- **Description** : Lorsqu'un projet est ouvert ou qu'un nouveau projet est créé alors qu'aucun projet n'était préalablement ouvert, les entrées"Files\Close", "Files\Save", "Files\Export map", "Edit\*", "Display\*" et "Project\*" du menu sont activées (grisées).
- **Classification** : Logique applicative et données.

## RG010
- **Description** : L'ouverture d'un projet ne remplace le projet courant qu'après lecture et validation réussies du fichier sélectionné. Si le fichier est inexistant, inaccessible, invalide ou incompatible, une erreur est affichée à l'utilisateur et le projet courant reste inchangé.
- **Classification** : Logique applicative et données.

## RG011
- **Description** : Chaque fichier projet comporte une version de format. L'application ouvre un projet uniquement si cette version est supportée ou peut être migrée de manière fiable vers une version supportée. Une migration ne doit jamais écraser le fichier d'origine sans action explicite de l'utilisateur.
- **Classification** : Logique applicative et données.

## RG012
- **Description** : Une sauvegarde ne remplace le fichier existant qu'après écriture complète et réussie de la nouvelle version. En cas d'échec de sauvegarde, le fichier précédemment enregistré doit rester exploitable et le projet doit conserver son état modifié. Après une sauvegarde réussie, la date de dernière modification du projet est mise à jour.
- **Classification** : Logique applicative et données.

## RG013
- **Description** : L'action « Enregistrer sous… » crée ou remplace un fichier à l'emplacement choisi par l'utilisateur après confirmation si un fichier existe déjà. Après une sauvegarde réussie, le fichier nouvellement choisi devient le fichier associé au projet ouvert. Le fichier précédemment associé au projet n'est ni renommé ni supprimé.
- **Classification** : Logique applicative et données.

## RG014
- **Description** : Un nouveau projet est nommé "Nouveau projet" et contient une carte narrative nommée "Carte narrative principale".
- **Classification** : Logique applicative et données.

## RG015
- **Description** : Un projet contient toujours au moins une carte narrative.
- **Classification** : Logique applicative et données.

## RG016
- **Description** : Une carte narrative contient toujours au moins un parcours.
- **Classification** : Logique applicative et données.

## RG017
- **Description** : La suppression d'une carte est irréversible et entraîne la suppression de tous les composants graphiques, relations et parcours qu'elle contient.
- **Classification** : Logique applicative et données.

## RG018
- **Description** : La suppression d'un composant entraîne la suppression automatique de toutes les relations qui le connectent à d'autres composants.
- **Classification** : Logique applicative et données.

## RG019
- **Description** : La suppression d'un parcours est impossible s'il s'agit du dernier parcours de la carte.
- **Classification** : Logique applicative et données.

## RG020
- **Description** : Chaque entité (projet, carte narrative) possède un identifiant stable (UUID).
- **Classification** : Logique applicative et données.

## RG021
- **Description** : Chaque composant, relation et parcours possède un identifiant entier unique au sein de sa carte narrative. Le même identifiant peut exister dans deux cartes distinctes.
- **Classification** : Logique applicative et données.

## RG022
- **Description** : Le libellé d'un composant ou d'un parcours n'est pas contraint à l'unicité au sein d'une même carte narrative.
- **Classification** : Logique applicative et données.

## RG023
- **Description** : À la création d'une carte narrative, un parcours par défaut est automatiquement créé et activé.
- **Classification** : Logique des cartes narratives.

## RG024
- **Description** : Lors de la création d'un nouveau parcours, celui-ci devient automatiquement le parcours activé.
- **Classification** : Logique des cartes narratives.

## RG025
- **Description** : Tout composant nouvellement créé (état ou évènement) est automatiquement rattaché au parcours actuellement activé.
- **Classification** : Logique des cartes narratives.

## RG026
- **Description** : Un composant (état ou évènement) peut être rattaché simultanément à plusieurs parcours. Tout composant doit cependant rester rattaché à au moins un parcours à tout moment.
- **Classification** : Logique des cartes narratives.

## RG027
- **Description** : Les relations entre composants (éat ou évènement) n'ont pas de rattachement direct aux parcours. Une relation est implicite au sein d'un parcours si et seulement si ses deux composants extrémités sont tous deux rattachés à ce parcours.
- **Classification** : Logique des cartes narratives.

## RG028
- **Description** : L'appartenance d'un composant (état ou évènement) à un ou plusieurs parcours est gérée via une liste à choix multiples dans les propriétés du composant. L'option est désactivée si un seul parcours existe dans la carte.
- **Classification** : Logique des cartes narratives.

## RG029
- **Description** : L'utilisateur ne peut pas retirer un composant (état ou évènement) de son dernier parcours.
- **Classification** : Logique des cartes narratives.

## RG030
- **Description** : Il existe toujours un parcours par défaut. Les noeuds orphelins après suppression d'un parcours sont automatiquement basculés vers le parcours par défaut.
- **Classification** : Logique des cartes narratives.

## RG031
- **Description** : Lors de la suppression d'un parcours, l'application identifie les composants (état ou évènement) qui lui sont exclusivement rattachés. Pour chacun, l'utilisateur doit obligatoirement choisir un nouveau parcours de rattachement via une fenêtre dédiée.
- **Classification** : Logique des cartes narratives.

## RG032
- **Description** : Lorsque l'utilisateur retire un composant (état ou évènement) d'un parcours, l'application vérifie si ce composant est relié à un autre composant toujours rattaché à ce parcours. Si c'est le cas, l'application lève une alerte : l'utilisateur peut annuler le retrait, ou confirmer la suppression de la relation incohérente.
- **Classification** : Logique des cartes narratives.

## RG033
- **Description** : Chaque carte narrative admet un et un seul état initial. Cet état initial se retrouve obligatoirement dans tous les parcours. Tous les parcours commencent à cet état initial.
- **Classification** : Logique des cartes narratives.

## RG034
- **Description** : Chaque parcours se termine par un état final. Cet état final peut être spécifique à chaque parcours (contrairement à l'état initial qui est commun à tous les parcours).
- **Classification** : Logique des cartes narratives.

## RG035
- **Description** : La séquence constitutive d'un parcours est définie par la succession d'état à évènement à état, et est matérialisée par un noeud d'état qui renseigne l'identifiant de l'évènement précédent, l'identifiant de l'état et l'identifiant de l'évènement suivant.
- **Classification** : Logique des cartes narratives.

## RG036
- **Description** : Un même composant (état ou événement) peut appartenir à plusieurs parcours sans duplication grâce à la gestion des noeuds d'état.
- **Classification** : Logique des cartes narratives.

## RG037
- **Description** : La séquence constitutive d'un parcours autorise qu'un même état ait plusieurs évènements prédécesseurs et successeurs, ainsi qu'un même évènement ait plusieurs états prédécesseurs et successeurs.
- **Classification** : Logique des cartes narratives.

## RG038
- **Description** : La suppression d'un parcours supprime obligatoirement toutes les entrées des noeuds de parcours qui portent son identifiant.
- **Classification** : Logique des cartes narratives.

## RG039
- **Description** : La suppression d'un événement entraîne la suppression en cascade des références associées dans toutes les tables qui ont son identifiant en clé étrangère. Un avertissement est émis si l'événement est lié à au moins un autre composant.
- **Classification** : Logique des cartes narratives.

## RG040
- **Description** : La position d'un composant (état ou évènement) est définie par des coordonnées (x, y) conservées dans un fichier de métadonnées graphiques associé au fichier de données du projet.
- **Classification** : Visualisation des parcours.

## RG041
- **Description** : Les composants (état ou évènement) s'alignent automatiquement sur la grille d'alignement lors de leur création et de leur déplacement.
- **Classification** : Visualisation des parcours.

## RG042
- **Description** : La modification du niveau de zoom ou de la position des barres de défilement ne constitue pas une modification de la carte ni du projet.
- **Classification** : Visualisation des parcours.

## RG043
- **Description** : À tout moment, soit tous les parcours, soit un seul parcours sont/est visualisé dans l'espace de représentation, selon l'activation ou non du filtre de parcours.
- **Classification** : Visualisation des parcours.

## RG044
- **Description** : Lorsqu'un composant (état ou évènement) est créé dans l'espace de travail, il est automatiquement sélectionné. Si un autre composant est déjà sélectionné, alors il est déselectionné. Lorsqu'un composant est sélectionné et que l'utilisateur clique sur l'espace de travail en dehors de tout composant, alors il est déselectionné. Lorsque l'utilisateur clique sur un composant de l'espace qui n'est pas sélectionné, alors il est sélectionné.  Si un autre composant est déjà sélectionné, alors il est déselectionné.
- **Classification** : Visualisation des parcours.

## RG045
- **Description** : Lorsqu'un composant est créé dans l'espace de travail à des coordonnées qui chevauchent celle d'un autre composant, elles sont modifiées pour éviter le chevauchement en laissant un espace entre les deux composants, selon un translation latérale ou verticale selon l'état de l'espace de rerésentation graphique.
- **Classification** : Visualisation des parcours.

## RG046
- **Description** : Lorsqu'un composant est déplacé par l'utilisateur et que ses coordonnées dépassent la partie visible de l'espace de travail, alors la barre de défilement correspondante, latérale ou verticale, est activée selon les coordonnées courantes du composant.
- **Classification** : Visualisation des parcours.

## RG047
- **Description** : L'application propose deux exports distincts : un export technique au format JSON (réimportable) et un export de lecture au format HTML (autonome).
- **Classification** : Export.

## RG048
- **Description** : L'export HTML génère un dossier nommé d'après la carte narrative, contenant un 'index.html' et les pages liées.
- **Classification** : Export.

## RG049
- **Description** : L'ordre de déroulement des parcours d'un export est déterminé par la séquence prédécesseur/successeur du modèle de données, indépendamment de la position graphique.
- **Classification** : Export.

## RG050
- **Description** : L'opération d'export ne marque pas la carte narrative ni le projet comme modifiés.
- **Classification** : Export.

## RG051
- **Description** : La valeur 0 (zéro) dans un champ de référence prédécesseur ou successeur ('from_event_id', 'to_event_id') signifie l'absence de prédécesseur ou de successeur. Cela correspond au premier ou au dernier élément d'une séquence de carte narrative.
- **Classification** : Architecture technique.

## RG052
- **Description** : Les métadonnées de représentation graphique sont stockées dans un fichier dédié associé au fichier de données du projet.
- **Classification** : Architecture technique.

## RG053
- **Description** : À chaque création d'un état isolé, l'application crée implicitement un noeud d'état avec l'identifiant de l'évènement prédécesseur renseigné avec la valeur 0, l'identifiant de l'état renseigné avec la valeur du nouvel état, et l'identifiant de l'évènement successeur renseigné avec la valeur 0.
- **Classification** : Logique des cartes narratives.

## RG054
- **Description** : À chaque création d'un événement isolé, l'application crée implicitement un noeud d'état avec l'identifiant de l'évènement prédécesseur renseigné avec la valeur du nouvel évènement, l'identifiant d'état renseigné avec la valeur 0, et l'identifiant de l'évènement successeur renseigné avec la valeur 0.
- **Classification** : Logique des cartes narratives.

## RG055
- **Description** : Lorsqu'un utilisateur établit une relation entre un état et un événement, le noeud d'état préexistant est mis à jour, ou bien un nouveau noeud d'état est créé selon les règles du graphe (pas de duplication de triplet).
- **Classification** : Logique des cartes narratives.

## RG056
- **Description** : Une carte narrative contient un et un seul état d'initialisation. Cet état est créé automatiquement par l'application et ne peut jamais être supprimé.
- **Classification** : Logique des cartes narratives.

## RG057
- **Description** : Un état de type final ne peut apparaître que dans des noeuds d'état dont l'identifiant d'évènement successeur est renseigné à 0.
- **Classification** : Logique des cartes narratives.

## RG058
- **Description** : Un seul parcours peut être défini comme le parcours par défaut de sa carte narrative. Si le parcours par défaut est supprimé, l'application désigne automatiquement le plus ancien parcours restant comme nouveau parcours par défaut.
- **Classification** : Logique des cartes narratives.

## RG059
- **Description** : La suppression d'un état ou d'un événement entraîne la suppression en cascade de tous les noeuds d'état qui le référencent, puis de tous les noeuds de parcours.
- **Classification** : Logique des cartes narratives.

## RG060
- **Description** : Un noeud d'état implicite (dont l'identifiant d'évènement successeur ou l'identifiant d'état est renseigné avec la valeur 0) est supprimé automatiquement dès qu'il est mis à jour avec une relation complète, sauf s'il est le point de départ de plusieurs embranchements.
- **Classification** : Logique des cartes narratives.
