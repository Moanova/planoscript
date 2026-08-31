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

---

## 2. Structure des cartes narratives

## RG015
- **Description** : Une carte narrative contient toujours au moins un parcours.
- **Classification** : Structure des cartes narratives.

## RG016
- **Description** : La suppression d'une carte narrative est irréversible et entraîne la suppression de tous les composants (états et événements), relations et parcours qu'elle contient.
- **Classification** : Structure des cartes narratives.

## RG017
- **Description** : La suppression d'un composant (état ou événement) entraîne la suppression automatique de toutes les relations qui le connectent à d'autres composants. Les noeuds d'état qui le référencent via une clé étrangère (événement prédécesseur, état ou événement successeur) sont mis à jour ou supprimés selon les règles de cohérence du graphe de la carte narrative.
- **Classification** : Structure des cartes narratives.

## RG018
- **Description** : La suppression d'un parcours est impossible s'il s'agit du dernier parcours de la carte.
- **Classification** : Structure des cartes narratives.

## RG019
- **Description** : Chaque entité (projet, carte narrative) possède un identifiant stable (UUID).
- **Classification** : Structure des cartes narratives.

## RG020
- **Description** : Chaque composant, relation et parcours possède un identifiant entier unique au sein de sa carte narrative. Le même identifiant peut exister dans deux cartes distinctes.
- **Classification** : Structure des cartes narratives.

## RG021
- **Description** : Le libellé d'un composant ou d'un parcours n'est pas contraint à l'unicité au sein d'une même carte narrative.
- **Classification** : Structure des cartes narratives.

## RG031
- **Description** : Chaque carte narrative possède un et un seul état initial. Cet état initial se retrouve obligatoirement dans tous les parcours. Tous les parcours commencent à cet état initial. Cet état est créé automatiquement par l'application et ne peut jamais être supprimé.
- **Classification** : Structure des cartes narratives.

## RG032
- **Description** : Chaque parcours valide et complet se termine par un état final. Cet état final peut être spécifique à chaque parcours, contrairement à l'état initial qui est commun à tous les parcours. En cours d'édition, un parcours peut temporairement ne pas comporter d'état final.
- **Classification** : Structure des cartes narratives.

## RG033
- **Description** : La séquence constitutive d'un parcours est définie par la succession d'état à évènement à état, et est matérialisée par un noeud d'état qui renseigne l'identifiant de l'événement précédent, l'identifiant de l'état et l'identifiant de l'événement suivant.
- **Classification** : Structure des cartes narratives.

## RG034
- **Description** : Un même composant (état ou événement) peut appartenir à plusieurs parcours sans duplication grâce à la gestion des noeuds d'état.
- **Classification** : Structure des cartes narratives.

## RG035
- **Description** : La séquence constitutive d'un parcours autorise qu'un même état ait plusieurs évènements prédécesseurs et successeurs, ainsi qu'un même événement ait plusieurs états prédécesseurs et successeurs.
- **Classification** : Structure des cartes narratives.

## RG036
- **Description** : La suppression d'un parcours supprime obligatoirement toutes les entrées des noeuds de parcours qui portent son identifiant.
- **Classification** : Structure des cartes narratives.

## RG037
- **Description** : La suppression d'un état ou d'un événement entraîne la suppression en cascade des références associées dans toutes les tables de données où son identifiant est utilisé comme clé étrangère. Un message d'information est affiché si le composant est référencé par au moins un autre élément.
- **Classification** : Structure des cartes narratives.

## RG038
- **Description** : Un état de type final ne peut apparaître que dans des noeuds d'état dont l'identifiant d'événement successeur est renseigné à 0.
- **Classification** : Structure des cartes narratives.

---

## 3. Logique des parcours et appartenance

## RG022
- **Description** : À la création d'une carte narrative, un parcours par défaut est automatiquement créé et activé.
- **Classification** : Logique des parcours et appartenance.

## RG023
- **Description** : Lors de la création d'un nouveau parcours, celui-ci devient automatiquement le parcours activé.
- **Classification** : Logique des parcours et appartenance.

## RG024
- **Description** : Tout composant nouvellement créé (état ou événement) est automatiquement rattaché au parcours actuellement activé.
- **Classification** : Logique des parcours et appartenance.

## RG025
- **Description** : Un composant (état ou événement) peut être rattaché simultanément à plusieurs parcours. Tout composant doit cependant rester rattaché à au moins un parcours à tout moment.
- **Classification** : Logique des parcours et appartenance.

## RG026
- **Description** : Les relations entre composants (état ou événement) n'ont pas de rattachement direct aux parcours. Une relation est implicite au sein d'un parcours si et seulement si ses deux composants extrémités sont tous deux rattachés à ce parcours.
- **Classification** : Logique des parcours et appartenance.

## RG027
- **Description** : L'appartenance d'un composant (état ou événement) à un ou plusieurs parcours est gérée via une liste à choix multiples dans les propriétés du composant. L'option est désactivée si un seul parcours existe dans la carte.
- **Classification** : Logique des parcours et appartenance.

## RG028
- **Description** : L'utilisateur ne peut pas retirer un composant (état ou événement) de son dernier parcours.
- **Classification** : Logique des parcours et appartenance.

## RG029
- **Description** : Il existe toujours un parcours par défaut. Les noeuds orphelins après suppression d'un parcours sont automatiquement basculés vers le parcours par défaut.
- **Classification** : Logique des parcours et appartenance.

## RG030
- **Description** : Lorsque l'utilisateur retire un composant (état ou événement) d'un parcours, l'application vérifie si ce composant est relié à un autre composant toujours rattaché à ce parcours. Si c'est le cas, l'application lève une alerte : l'utilisateur peut annuler le retrait, ou confirmer la suppression de la relation incohérente.
- **Classification** : Logique des parcours et appartenance.

## RG052
- **Description** : À chaque création d'un état isolé, l'application crée implicitement un noeud d'état avec l'identifiant de l'événement prédécesseur renseigné avec la valeur 0, l'identifiant de l'état renseigné avec la valeur du nouvel état, et l'identifiant de l'événement successeur renseigné avec la valeur 0.
- **Classification** : Logique des parcours et appartenance.

## RG053
- **Description** : À chaque création d'un événement isolé, l'application crée implicitement un noeud d'état avec l'identifiant de l'événement prédécesseur renseigné avec la valeur du nouvel événement, l'identifiant d'état renseigné avec la valeur 0, et l'identifiant de l'événement successeur renseigné avec la valeur 0.
- **Classification** : Logique des parcours et appartenance.

## RG054
- **Description** : Lorsqu'un utilisateur établit une relation entre un état et un événement, un nouveau noeud d'état est créé s'il n'en existe pas déjà un implicite ; sinon, le noeud d'état préexistant est mis à jour, conformément à la règle de non-duplication de triplet.
- **Classification** : Logique des parcours et appartenance.

## RG055
- **Description** : Un seul parcours peut être défini comme le parcours par défaut de sa carte narrative. Si le parcours par défaut est supprimé, l'application désigne automatiquement le plus ancien parcours restant comme nouveau parcours par défaut.
- **Classification** : Logique des parcours et appartenance.

## RG056
- **Description** : La suppression d'un état ou d'un événement entraîne la suppression en cascade de tous les noeuds d'état qui le référencent, puis de tous les noeuds de parcours.
- **Classification** : Logique des parcours et appartenance.

## RG057
- **Description** : Un noeud d'état implicite (dont l'identifiant d'événement successeur ou l'identifiant d'état est renseigné avec la valeur 0) est supprimé automatiquement dès qu'il est mis à jour avec une relation complète, sauf s'il est le point de départ de plusieurs embranchements.
- **Classification** : Logique des parcours et appartenance.

---

## 4. Visualisation et interaction

## RG039
- **Description** : La position d'un composant (état ou événement) est définie par des coordonnées (x, y) conservées dans un fichier de métadonnées graphiques associé au fichier de données du projet.
- **Classification** : Visualisation et interaction.

## RG040
- **Description** : Les composants (état ou événement) s'alignent automatiquement sur la grille d'alignement lors de leur création et de leur déplacement.
- **Classification** : Visualisation et interaction.

## RG041
- **Description** : La modification du niveau de zoom ou de la position des barres de défilement ne constitue pas une modification de la carte ni du projet.
- **Classification** : Visualisation et interaction.

## RG042
- **Description** : À tout moment, soit tous les parcours, soit un seul parcours sont/est visualisé dans l'espace de représentation, selon l'activation ou non du filtre de parcours.
- **Classification** : Visualisation et interaction.

## RG043
- **Description** : À tout moment, un seul composant est sélectionné dans l'espace de travail. La création ou le clic sur un composant le sélectionne et déselectionne le précédent. Un clic sur l'espace de travail en dehors de tout composant déselectionne le composant actuel.
- **Classification** : Visualisation et interaction.

## RG044
- **Description** : Un composant ne peut être créé à des coordonnées qui chevauchent celles d'un composant existant. L'application vérifie la position avant la création et ajuste les coordonnées du nouveau composant pour éviter tout chevauchement, en appliquant une translation latérale ou verticale selon les caractéristiques de l'espace de représentation graphique.
- **Classification** : Visualisation et interaction.

## RG045
- **Description** : Lorsqu'un composant est déplacé par l'utilisateur et que ses coordonnées dépassent la partie visible de l'espace de travail, l'application déplace la barre de défilement correspondante (latérale ou verticale) pour maintenir le composant visible selon ses coordonnées courantes.
- **Classification** : Visualisation et interaction.

---

## 5. Architecture technique et modèle de données

## RG050
- **Description** : La valeur 0 (zéro) dans un champ de référence prédécesseur ou successeur ('from_event_id', 'to_event_id') signifie l'absence de prédécesseur ou de successeur. Cela correspond au premier ou au dernier élément d'une séquence de carte narrative.
- **Classification** : Architecture technique et modèle de données.

## RG051
- **Description** : Les métadonnées de représentation graphique sont stockées dans un fichier dédié associé au fichier de données du projet.
- **Classification** : Architecture technique et modèle de données.
