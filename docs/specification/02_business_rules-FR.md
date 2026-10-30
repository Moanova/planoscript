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
- **Description** : La suppression d'un composant (état ou événement) entraîne la suppression automatique de toutes les relations qui le connectent à d'autres composants. Les arcs état-évènement qui le référencent sont supprimés selon les règles de cohérence du graphe de la carte narrative.
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
- **Description** : Chaque carte narrative possède un et un seul état initial. Cet état est créé automatiquement par l'application et ne peut jamais être supprimé. L'état initial participe à tous les parcours existants dans la carte par l'intermédiaire de ses rattachements : chacun de ses arcs sortants rattaché à un parcours y fait participer l'état initial (RG026). Dans une carte cohérente, tous les parcours commencent à cet état initial ; l'application ne vérifie pas cette cohérence (hors périmètre MVP, SU005).
- **Classification** : Structure des cartes narratives.

## RG032
- **Description** : Chaque parcours valide et complet se termine par un état final. Cet état final peut être spécifique à chaque parcours, contrairement à l'état initial qui est commun à tous les parcours. En cours d'édition, un parcours peut temporairement ne pas comporter d'état final.
- **Classification** : Structure des cartes narratives.

## RG033
- **Description** : La séquence constitutive d'un parcours est définie par la succession d'état à évènement à état. Chaque relation orientée entre un état et un évènement est matérialisée par un arc état-évènement qui renseigne l'identifiant de l'état, l'identifiant de l'évènement et le sens de la relation (prédécesseur ou successeur). La succession d'état à évènement à état se reconstitue par chaînage des arcs à travers les états et les évènements qu'ils relient.
- **Classification** : Structure des cartes narratives.

## RG034
- **Description** : Un même composant (état ou événement) peut appartenir à plusieurs parcours sans duplication : ce sont les relations (arcs état-événement et associations agent-état) qui sont rattachées aux parcours par l'intermédiaire des nœuds de parcours (Journey_node), et l'appartenance du composant en est dérivée (RG026). Aucun champ de rattachement aux parcours n'existe sur le composant.
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
- **Description** : Un état de type final ne possède aucun arc état-évènement sortant, c'est-à-dire aucun arc le reliant à un évènement en tant que successeur.
- **Classification** : Structure des cartes narratives.

## RG060
- **Description** : Le type de l'état initial d'une carte narrative ne peut jamais être modifié. L'état initial conserve définitivement le type "Initial".
- **Classification** : Structure des cartes narratives.

## RG061
- **Description** : Le type "Initial" ne peut jamais être sélectionné pour un état autre que l'état initial de la carte narrative. Lors de la création ou de l'édition d'un état, le type "Initial" n'est pas proposé parmi les valeurs sélectionnables.
- **Classification** : Structure des cartes narratives.

## RG058
- **Description** : Une connexion bidirectionnelle directe entre un État et un Événement est interdite. Si une relation d'un État S vers un Événement E existe déjà (port de sortie de S connecté au port d'entrée de E), la création de la relation inverse de l'Événement E vers l'État S (port de sortie de E connecté au port d'entrée de S) est interdite, et inversement. Cette règle empêche les cycles directs de longueur 2 (État → Événement → État) dans le graphe de la carte narrative.
- **Classification** : Structure des cartes narratives.

---

## 3. Logique des parcours et appartenance

## RG022
- **Description** : À la création d'une carte narrative, un parcours par défaut est automatiquement créé et activé.
- **Classification** : Logique des parcours et appartenance.

## RG023
- **Description** : Lors de la création d'un nouveau parcours, celui-ci devient automatiquement le parcours activé. La duplication d'un parcours (FN025) crée un nouveau parcours sans modifier le parcours activé.
- **Classification** : Logique des parcours et appartenance.

## RG024
- **Description** : Aucun rattachement de parcours n'est créé pour un composant (état ou événement) nouvellement créé tant qu'il est isolé, c'est-à-dire sans aucune relation (RG052). Un composant appartient à un parcours dès qu'une relation le concernant y est rattachée (RG026). Inversement, si la dernière relation rattachée à un parcours qui fait appartenir un composant à ce parcours est détachée de ce parcours (RG027) ou supprimée, le composant cesse d'appartenir à ce parcours et peut redevenir orphelin de parcours.
- **Classification** : Logique des parcours et appartenance.

## RG025
- **Description** : Un composant (état ou événement) peut appartenir simultanément à plusieurs parcours, ou à aucun s'il est isolé (sans aucune relation).
- **Classification** : Logique des parcours et appartenance.

## RG026
- **Description** : Une relation (arc état-événement ou association agent-état) appartient aux parcours des noeuds de parcours (Journey_node) qui la référencent : de 1 à n parcours. L'appartenance d'un composant (état ou événement) à un parcours est dérivée : le composant appartient à un parcours si et seulement si au moins une de ses relations y est rattachée. Un composant sans aucune relation (orphelin) n'appartient à aucun parcours et n'est visible que lorsque le filtre par parcours est désactivé (FN029).
- **Classification** : Logique des parcours et appartenance.

## RG027
- **Description** : Le rattachement d'une relation (arc ou association agent-état) à un ou plusieurs parcours est géré via une liste à choix multiples des parcours, présentée dans les propriétés de la connexion (menu d'édition de la relation), et non dans les propriétés du composant. L'option est désactivée si un seul parcours existe dans la carte.
- **Classification** : Logique des parcours et appartenance.

## RG029
- **Description** : Il existe toujours un parcours par défaut.
- **Classification** : Logique des parcours et appartenance.

## RG052
- **Description** : Aucun noeud de parcours n'est créé pour un composant isolé (état ou événement sans relation). Le rattachement d'une relation à un parcours s'effectue à la création de la connexion (ou de l'association agent-état) : un noeud de parcours référençant l'arc (ou l'association) est alors créé dans le parcours actuellement activé. Il peut également être ajouté ou retiré ultérieurement via le menu d'édition de la relation (RG027).
- **Classification** : Logique des parcours et appartenance.

## RG054
- **Description** : Lorsqu'un utilisateur établit une relation entre un état et un évènement, l'application crée un nouvel arc état-évènement renseignant l'état, l'évènement et le sens de la relation (prédécesseur ou successeur). Deux arcs identiques ne peuvent exister pour le même état, le même évènement et le même sens.
- **Classification** : Logique des parcours et appartenance.

## RG055
- **Description** : Un seul parcours peut être défini comme le parcours par défaut de sa carte narrative. Si le parcours par défaut est supprimé, l'application désigne automatiquement le plus ancien parcours restant comme nouveau parcours par défaut.
- **Classification** : Logique des parcours et appartenance.

## RG056
- **Description** : La suppression d'un état ou d'un évènement entraîne la suppression en cascade de tous les arcs état-évènement qui le référencent, puis de tous les nœuds de parcours qui référencent les arcs supprimés.
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

## RG059
- **Description** : La représentation visuelle d'une connexion (relation) entre deux composants ne doit jamais chevaucher un composant qui n'en est ni la source ni la cible. À la création d'une connexion, l'application détecte si le tracé de la connexion est susceptible de traverser un composant tiers et, le cas échéant, ajuste automatiquement le routage de la connexion pour contourner ce composant. Cette détection et ce réajustement sont également effectués lorsqu'un composant est déplacé par l'utilisateur et que sa nouvelle position provoque le chevauchement d'une connexion existante dont il n'est pas extrémité. L'ajustement du routage ne modifie ni les coordonnées des composants ni les données du projet ; il ne porte que sur la représentation graphique de la connexion.
- **Classification** : Visualisation et interaction.

---

## 5. Architecture technique et modèle de données

## RG050
- **Description** : L'absence de prédécesseur ou de successeur pour un état est matérialisée par l'absence d'arc état-évènement dans le sens correspondant. Un état sans arc entrant est le premier élément d'une séquence ; un état sans arc sortant est le dernier élément.
- **Classification** : Architecture technique et modèle de données.

## RG051
- **Description** : Les métadonnées de représentation graphique sont stockées dans un fichier dédié associé au fichier de données du projet.
- **Classification** : Architecture technique et modèle de données.

## 2. Structure des cartes narratives

## RG061
- **Description** : Le type de l'état initial d'une carte narrative ne peut jamais être modifié. L'état initial conserve définitivement le type "Initial".
- **Classification** : Structure des cartes narratives.

## RG062
- **Description** : Le type "Initial" ne peut jamais être sélectionné pour un état autre que l'état initial de la carte narrative. Lors de la création ou de l'édition d'un état, le type "Initial" n'est pas proposé parmi les valeurs sélectionnables.
- **Classification** : Structure des cartes narratives.

## RG063
- **Description** : Entre un agent et un état donnés d'une même carte narrative, il ne peut exister qu'une seule association. Toute tentative de création d'une association en double est ignorée ou refusée par l'application.
- **Classification** : Structure des cartes narratives.

## RG064
- **Description** : La suppression d'un agent supprime en cascade toutes les associations agent-état qui référencent son identifiant. Un message d'information est affiché si l'agent est associé à au moins un état.
- **Classification** : Structure des cartes narratives.

## RG065
- **Description** : La suppression d'un état supprime en cascade toutes les associations agent-état qui référencent son identifiant. Un message d'information est affiché si l'état est associé à au moins un agent.
- **Classification** : Structure des cartes narratives.

## RG066
- **Description** : Toute association agent-état appartient à au moins un parcours à tout moment. À sa création, elle est rattachée au parcours actuellement activé (ou au parcours par défaut si aucun parcours n'est activé), via un noeud de parcours référençant l'association (Journey_node.state_agent_rel_id). Si la suppression d'un parcours la rend orpheline de tout parcours, elle est automatiquement basculée vers le parcours par défaut. Le fait qu'un même couple d'agents se rencontre dans plusieurs parcours est modélisé par des états distincts, chacun rattaché au parcours concerné. Le filtrage de l'affichage par parcours s'applique aux associations agent-état comme aux autres relations.
- **Classification** : Structure des cartes narratives.

## RG068
- **Description** : Les colonnes de la matrice agents × états de la vue agents sont ordonnées par défaut par ordre de création des états (identifiant croissant). L'utilisateur peut réordonner les colonnes ; cet ordre personnalisé est rémanent : il est conservé dans les métadonnées graphiques (fichier de mise en page) associées au projet, entre les sessions. L'état initial occupe toujours la première colonne et ne peut pas être déplacé (RG031 : tous les parcours commencent à cet état). Tout état nouvellement créé apparaît en fin d'ordre. En cas d'anomalie dans l'ordre sauvegardé (état absent ou inconnu), l'application applique l'ordre de création en repli. L'ordre des colonnes ne constitue pas une donnée narrative : sa modification ne marque pas la carte comme modifiée. Les lignes (agents) suivent la même règle : ordre de création par défaut, réordonnancement manuel rémanent autorisé.
- **Classification** : Visualisation et interaction.

## RG067
- **Description** : Le focus de navigation croisée entre les vues (vue Events, vue agents) est un état visuel temporaire : il ne marque ni la carte ni le projet comme modifiés, et n'est pas conservé dans les métadonnées graphiques ni entre les sessions.
- **Classification** : Visualisation et interaction.
