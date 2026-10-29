# Planoscript ::: Scenarii d'utilisation

## Document Version
- **Version**: 2.0
- **Date**: 29-08-2026
- **Status**: New version realigned with the latest redesign

---

## SU001 : Gérer un projet narratif
- **Description** : En tant qu'auteur, je peux créer, ouvrir, enregistrer, renommer et fermer un projet narratif afin de regrouper, retrouver et poursuivre le travail sur mes cartes narratives.
- **Complément** :
    - Un projet est un document local contenant les métadonnées du projet et une ou plusieurs cartes narratives.
    - Un seul projet peut être ouvert dans l'application à tout moment.
    - Un projet nouvellement créé est un projet non enregistré : il existe en mémoire mais n'est associé à aucun fichier tant que l'utilisateur ne l'a pas sauvegardé.
    - Chaque projet possède un identifiant stable, un nom, une date de création, une date de dernière modification et une version de format.
    - Le chemin du fichier est un état de l'application ; il ne constitue pas une donnée métier portable du projet.
    - Un nouveau projet est nommé "Nouveau projet" et contient une carte narrative nommée "Carte narrative principale".
- **Critères d'acceptation** :
    - L'utilisateur peut créer un projet depuis le menu, un raccourci clavier ou le message d'accueil.
    - L'utilisateur peut ouvrir un fichier projet valide depuis le système de fichiers.
    - En cas de fichier invalide, incompatible ou illisible, l'application affiche une erreur claire et conserve le projet ouvert inchangé.
    - L'utilisateur peut enregistrer un projet non enregistré en choisissant un nom et un emplacement.
    - L'utilisateur peut enregistrer les modifications d'un projet déjà associé à un fichier sans nouvelle boîte de dialogue.
    - L'utilisateur peut enregistrer une copie sous un autre nom ou dans un autre emplacement ; cette copie devient le projet ouvert courant.
    - L'utilisateur peut fermer un projet.
    - Si le projet est modifié lors d'une fermeture, d'une ouverture, d'une création ou d'une sortie, l'application propose : "Enregistrer", "Ne pas enregistrer", "Annuler".
    - Un projet enregistré est ajouté à la liste des projets récents.
    - La liste des projets récents respecte la limite configurée et retire les fichiers qui n'existent plus.
- **Périmètre MVP** :
    - Chaque projet ne contient qu'une seule carte narrative.


## SU002 : Gérer une carte narrative
- **Description** : En tant qu'auteur, je peux créer, nommer, dupliquer, supprimer et naviguer entre les cartes narratives d'un projet afin de structurer mon récit en fils alternatifs.
- **Complément** :
    - Une carte narrative est un élément de données stocké au sein du fichier projet. Elle appartient à un et un seul projet.
    - Chaque carte possède un identifiant stable, un nom, une date de création et une date de dernière modification.
    - Un projet contient toujours au moins une carte narrative.
    - La carte créée par défaut lors de la création d'un projet est nommée "Carte narrative principale".
    - La suppression d'une carte est irréversible et entraîne la suppression de tous les composants graphiques, relations et parcours qu'elle contient.
    - Une carte est considérée comme modifiée lorsque l'utilisateur : ajoute ou supprime un composant ou une relation ; modifie les données associées à un composant ou une relation ; modifie la position d'un composant dans l'espace de représentation graphique ; crée, modifie ou supprime un parcours ; modifie le rattachement de composants ou de relations à un parcours.
    - La modification du niveau de zoom ou de la position des barres de défilement de l'espace de représentation graphique ne constitue pas une modification de la carte.
    - La grille d'alignement des composants dans l'espace de visualisation est toujours visible et active pour chaque carte.
    - L'utilisateur peut exporter une carte narrative sous forme de fichier autonome, et importer une carte narrative depuis un fichier autonome dans le projet courant.
- **Critères d'acceptation** :
    - L'utilisateur peut créer une nouvelle carte depuis le menu "Projet".
    - L'utilisateur peut renommer une carte en éditant directement son libellé ou via une boîte de dialogue dédiée.
    - L'utilisateur peut dupliquer une carte ; la copie porte automatiquement un nom distinctif (ex. : "Nom (copie)") et un nouvel identifiant stable.
    - L'utilisateur peut supprimer une carte avec confirmation si elle contient des composants ; la suppression est refusée avec un message explicite si la carte est la dernière du projet.
    - L'utilisateur peut naviguer entre les cartes du projet depuis le menu "Projet".
    - L'utilisateur peut exporter une carte narrative dans un emplacement choisi.
    - L'utilisateur peut importer une carte narrative depuis un fichier valide dans le projet courant ; en cas de fichier invalide, incompatible ou illisible, l'application affiche une erreur claire et conserve le projet ouvert inchangé.
    - Toute création, renommage, duplication ou suppression de carte marque le projet comme modifié.
    - Toute modification au sens défini dans le complément met à jour la date de dernière modification de la carte et celle du projet.
- **Périmètre MVP** :
    - Chaque projet ne contient qu'une seule carte narrative. Par conséquent, la création, la duplication, la suppression, la navigation entre cartes et la réorganisation de l'ordre des cartes ne sont pas disponibles.
    - Seuls le renommage de la carte par défaut, la modification de son contenu et l'export de carte sont fonctionnels.


## SU003 : Gérer un composant de carte narrative
- **Description** : En tant qu'auteur, je peux créer, nommer, déplacer, modifier ou supprimer un composant de carte narrative afin de définir le contenu des enchaînements de mon récit.
- **Complément** :
    - Les types de composants sont définis par le modèle de données applicatif : agent, état, évènement.
    - Chaque composant possède un identifiant entier unique au sein de la carte narrative à laquelle il appartient. Le même identifiant peut exister dans deux cartes distinctes.
    - Le libellé d'un composant n'est pas contraint à l'unicité au sein d'une même carte narrative.
    - Chaque composant est représenté visuellement par une icône spécifique à son type.
    - Chaque composant est déplaçable dans l'espace de visualisation mais non dimensionnable.
    - Chaque composant dispose de deux ports d'accroche, respectivement entrant et sortant (gauche et droite), matérialisés par des carrés actifs, destinés à la création des relations.
    - La position d'un composant dans l'espace de visualisation est définie par des coordonnées (x, y) qui sont conservées dans un fichier de métadonnées graphiques associé au fichier de données du projet.
    - Les composants s'alignent automatiquement sur la grille d'alignement de l'espace de visualisation lors de leur création et de leur déplacement.
    - À la création d'une carte narrative, un parcours par défaut est automatiquement créé et activé.
    - Tout composant nouvellement créé est automatiquement rattaché au parcours actuellement activé.
    - Un composant ne peut jamais exister en dehors d'un parcours. L'utilisateur peut modifier le rattachement d'un composant à un autre parcours existant, mais ne peut le retirer de son dernier parcours.
    - La suppression d'un composant entraîne automatiquement la suppression en cascade de toutes les relations qui le connectent à d'autres composants.
- **Critères d'acceptation** :
    - L'utilisateur peut créer un composant depuis le menu général, la barre d'outils ou le menu contextuel.
    - Lors de la création, le composant est automatiquement rattaché au parcours activé et positionné sur la grille à l'emplacement désigné par l'utilisateur.
    - L'utilisateur peut dupliquer un composant ; la copie porte automatiquement un nom distinctif et un nouvel identifiant, et est rattachée au parcours activé.
    - L'utilisateur peut modifier les attributs éditables d'un composant via un panneau de propriétés.
    - L'utilisateur peut modifier la liste des parcours auxquels un composant est rattaché, parmi les parcours existants de la carte.
    - L'utilisateur ne peut pas retirer un composant de son parcours s'il n'a qu'un rattachement unique ; l'application empêche cette action ou ne propose pas l'option.
    - L'utilisateur peut supprimer un composant avec confirmation si des données sont associées ; la suppression entraîne la suppression en cascade des relations concernées.
    - L'utilisateur peut positionner et repositionner un composant par glisser-déposer au moyen d'une souris (sur PC), d'un stylet ou en mode tactile (sur tablette).
    - Lors du déplacement, le composant s'aligne automatiquement sur la grille de l'espace de visualisation.
    - Le composant conserve sa position (coordonnées x, y) entre les sessions via le fichier de métadonnées graphiques associé.
    - Le composant est représenté par l'icône correspondant à son type et dispose de deux points d'accroche actifs (entrant et sortant).
    - Le composant n'est pas redimensionnable par l'utilisateur.
    - L'utilisateur peut choisir de visualiser l'ensemble des composants et relations de la carte, ou uniquement ceux appartenant au parcours activé.
    - Toute création, duplication, modification de données, déplacement ou suppression de composant marque la carte comme modifiée, et par conséquent le projet comme modifié.
- **Périmètre MVP** :
    - La barre d'outils des composants n'est pas implémentée. Les actions associées ne sont donc gérées que par menu.


## SU004 : Gérer une relation entre composants de carte narrative
- **Description** : En tant qu'auteur, je peux créer, annoter, modifier ou supprimer une relation entre deux composants de carte narrative afin de définir les enchaînements de mon récit.
- **Complément** :
    - Une relation est un élément de données appartenant à une carte narrative. Elle possède un identifiant entier unique au sein de cette carte, selon le même mécanisme que les composants.
    - Les attributs éditables d'une relation dépendent de son type selon le modèle de données. En règle générale, les attributs obligatoires sont identiques à ceux des composants.
    - Une relation relie toujours exactement deux composants distincts d'une même carte narrative. Un composant ne peut jamais être en relation avec lui-même.
    - Entre deux composants donnés, il ne peut exister qu'une seule relation.
    - Les relations n'ont pas de lien direct avec les parcours. Elles appartiennent indirectement à un ou plusieurs parcours par le biais des composants source et cible qu'elles connectent.
    - La suppression d'une relation est indépendante de celle des composants, hormis la suppression en cascade définie dans le scénario SU003.
    - L'étiquette d'une relation (annotation textuelle) est affichée dans une infobulle au survol.
    - Les relations sont directionnelles : la sortie du composant A et connectée à l'entrée du composant B, et la sortie du composant B est connectée à l'entrée du composant C...etc.
    - Deux composants du même type ne peuvent jamais être reliés entre eux : un état est nécessairement relié à un évènement, et un évènement est nécessairement relié à un état.
- **Critères d'acceptation** :
    - L'utilisateur peut initier la création d'une relation depuis la barre d'outils, le menu "Projet" ou le menu contextuel.
    - Lors de la création, l'utilisateur sélectionne un composant source. Si aucun composant n'était actif, il devient actif. Un lien visuel suit alors les mouvements du curseur jusqu'à ce que l'utilisateur clique sur le point d'accroche d'un composant cible.
    - L'application empêche la création d'une relation dont le composant source et le composant cible sont identiques.
    - L'application empêche la création d'une relation dont le composant source et le composant cible sont du même type.
    - L'application empêche la création d'une relation dupliquée entre deux composants déjà reliés.
    - L'utilisateur peut annoter une relation par du texte libre via un dialogue d'édition (TSK21 : champ « Note » + liste des parcours de la carte, cochable — RG027 révisée).
    - Points d'entrée de l'édition (TSK21) : menu contextuel de la connexion (vue Events), menu « Project › Relations... › Edit », clic droit sur une case cochée de la matrice (vue Agents, associations agent-état).
    - Une relation ne peut pas être déplacée en tant que telle mais suit le déplacement du composant auquel elle est rattachée.
    - Si la modification d'une relation entraîne un changement de composant source ou cible, l'application émet une alerte, supprime implicitement la relation existante et en crée une nouvelle avec la nouvelle connection source/cible.
    - L'utilisateur peut supprimer une relation avec confirmation préalable.
    - L'étiquette d'une relation est consultable via une infobulle au survol du trait représentatif.
    - Toute création, modification d'annotation, déplacement ou suppression de relation marque la carte comme modifiée, et par conséquent le projet comme modifié.
- **Périmètre MVP** :
    - La barre d'outils des composants n'est pas implémentée. Les actions associées ne sont donc gérées que par menu.


## SU005 : Gérer un parcours narratif
- **Description** : En tant qu'auteur, je peux créer, nommer, décrire, dupliquer, activer, modifier ou supprimer un parcours narratif afin de définir les fils alternatifs de mon récit.
- **Complément** :
    - Un parcours narratif est un élément de données appartenant à une carte narrative. Il possède un identifiant entier unique au sein de cette carte, selon le même mécanisme que les composants et les relations.
    - Les attributs éditables d'un parcours sont son libellé et sa description.
    - Chaque carte narrative contient toujours au moins un parcours.
    - Lors de la création d'une carte narrative, l'application crée automatiquement un parcours initial, l'active et lui attribue un nom par défaut.
    - Un composant peut être rattaché simultanément à plusieurs parcours. Tout composant doit cependant rester rattaché à au moins un parcours à tout moment.
    - Les relations entre composants n'ont pas de rattachement direct aux parcours. Une relation est implicite au sein d'un parcours si et seulement si ses deux composants connectés sont tous deux rattachés à ce parcours.
    - Lors de la création d'un nouveau parcours, celui-ci devient automatiquement le parcours activé.
    - Tout composant nouvellement créé est automatiquement rattaché au parcours actuellement activé.
    - La suppression d'un parcours est impossible s'il s'agit du dernier parcours de la carte ; l'application affiche un message explicatif.
- **Critères d'acceptation** :
    - L'utilisateur peut créer un nouveau parcours depuis la barre d'outils latérale des parcours ou le menu "Projet". Le nouveau parcours est automatiquement activé et devient le parcours courant.
    - L'utilisateur peut renommer un parcours et modifier sa description via une boîte de dialogue ou un panneau de propriétés.
    - L'utilisateur peut dupliquer un parcours ; la copie porte automatiquement un nom distinctif et un nouvel identifiant. Les composants rattachés au parcours source sont également rattachés au parcours dupliqué.
    - L'utilisateur peut activer un parcours en le sélectionnant dans la liste de la barre d'outils latérale des parcours ou depuis le menu "Projet". Le parcours activé devient le parcours courant pour l'édition.
    - L'utilisateur peut supprimer un parcours avec confirmation préalable, sous réserve qu'il ne s'agisse pas du dernier parcours de la carte.
    - Lors de la suppression d'un parcours, l'application identifie les composants qui lui sont exclusivement rattachés. Pour chacun, l'utilisateur doit obligatoirement choisir un nouveau parcours de rattachement via une fenêtre dédiée.
    - L'appartenance d'un composant à un ou plusieurs parcours est gérée via une liste à choix multiples dans les propriétés du composant. L'option est désactivée si un seul parcours existe dans la carte.
    - Toute création, renommage, duplication, activation, suppression ou modification des rattachements d'un parcours marque la carte comme modifiée, et par conséquent le projet comme modifié.
- **Périmètre MVP** :
    - La barre d'outils des parcours n'est pas implémentée. Les actions associées ne sont donc gérées que par menu.
    - La cohérence de parcours n'est pas analysée : l'application ne détecte pas si un parcours présente des enchaînements brisés (un évènement dont l'état au quel il est connecté appartient à un autre parcours, ou vice-versa); cela fera l'objet d'une fonctionnalité ultérieure.


## SU006 : Visualiser une carte narrative
- **Description** : En tant qu'auteur, je peux visualiser et naviguer dans l'espace de représentation graphique d'une carte narrative afin de consulter, structurer et valider mon récit.
- **Complément** :
    - L'espace de visualisation est virtuellement illimité dans ses dimensions (limité par les capacités du système d'exploitation).
    - La navigation s'effectue au moyen de barres de défilement horizontal et vertical.
    - La grille d'alignement des composants est toujours visible et active.
    - Un filtre de parcours permet d'afficher, soit tous les parcours existants, soit le parcours sélectionné Le basculement d'un parcours à un autre met à jour l'affichage pour ne représenter que les composants rattachés à ce parcours et les relations entre ses composants.
    - La position des barres de défilement et le niveau de zoom ne constituent pas des données métier ; ils ne sont pas conservés entre les sessions.
- **Critères d'acceptation** :
    - L'application s'adapte à la taille de la fenêtre sans perte de fonctionnalité ; les barres d'outils (composants et parcours) restent accessibles.
    - L'utilisateur peut naviguer dans l'espace de visualisation au moyen des barres de défilement horizontal et vertical.
    - L'espace de visualisation supporte un déploiement étendu sans dégradation de stabilité.
    - Si le filtre de parcours est activé, l'utilisateur peut basculer d'un parcours à un autre via la barre d'outils des parcours ou le menu "Projet" ; l'affichage se met à jour instantanément.
    - Les composants et les relations du parcours affiché sont rendus selon leurs coordonnées et leur représentation graphique définies dans les métadonnées du projet.
    - Les composants s'alignent sur la grille d'alignement lors de leur création et de leur déplacement.
    - les modifications de position des barres de défilement ne marquent pas la carte comme modifiée.
    - L'interface reste pleinement fonctionnelle pour une taille de fenêtre minimale de 1280×720.
    - Le temps de réponse entre une action utilisateur (création, déplacement, suppression d'un composant) et la mise à jour de l'affichage est immédiat (sans latence perceptible) pour une carte contenant jusqu'à 100 composants.
    - L'application reste stable lors de la navigation dans un espace de visualisation de 10 000×10 000 pixels.
- **Périmètre MVP** :
    - Les barres d'outils de composants et de parcours ne sont pas disponibles.
    - Le zoom n'est pas disponible.
    - L'application cible exclusivement les PC sous Windows.
    - La vue des relations entre agents (relations d'agent à agent) n'est pas disponible ; si elle est réalisée un jour, elle constituera un troisième espace de travail distinct. La vue agents (matrice des associations agent-état, SU009) fait partie du MVP.
	

## SU007 : Exporter une carte narrative
- **Description** : En tant qu'auteur, je peux exporter une carte narrative sous la forme d'un document autonome lisible dans un navigateur standard afin de valider mon récit et le partager avec mon équipe.
- **Complément** :
    - L'application propose deux exports distincts pour une carte narrative : un export technique destiné à la réimportation dans un autre projet, et un export de lecture destiné à la consultation hors application.
    - Le document d'export de lecture est autonome : il ne nécessite aucun serveur, aucune connexion Internet et aucune dépendance externe.
    - L'export génère un dossier nommé d'après le nom physique de la carte narrative. Ce dossier contient un fichier d'index et l'ensemble des pages nécessaires à la navigation hypertexte.
    - Le contenu restitué pour chaque composant est constitué de son libellé (affiché comme titre de paragraphe) et de sa description (corps du texte). Si la description est vide, seul le libellé est affiché.
    - L'ordre de déroulement est déterminé par la séquence de prédécesseur à successeur définie dans le modèle de données applicatif, indépendamment de la position des composants dans l'espace de visualisation graphique.
    - L'export propose deux modes de lecture :
        1. **Vue parcours** : le lecteur sélectionne un parcours dans le sommaire et accède à une page affichant l'intégralité de la séquence de ses composants de façon linéaire.
        2. **Vue événements** : le lecteur accède à une page présentant le premier événement de la carte, puis déroule linéairement la séquence des événements jusqu'au premier embranchement (c'est-à-dire un événement possédant des successeurs dans plusieurs parcours distincts). À cet embranchement, des liens hypertexte permettent de choisir le parcours souhaité ; chaque lien indique le nom du parcours correspondant entre parenthèses. Le choix d'un lien ouvre une nouvelle page reprenant le déroulement linéaire jusqu'au prochain embranchement, et ainsi de suite.
    - Chaque page de déroulement propose un lien de retour vers le sommaire. Dans la vue événements, chaque page propose également un lien vers la page précédente (celle ayant mené à l'embranchement).
- **Critères d'acceptation** :
    - L'utilisateur peut lancer l'export de la carte narrative courante depuis le menu "Fichier" ou la barre d'outils.
    - L'application génère un dossier d'export nommé d'après le nom de la carte narrative, contenant un fichier d'index et l'ensemble des pages nécessaires.
    - Le document s'affiche correctement dans les navigateurs standards (Chrome, Firefox, Edge) sans connexion Internet.
    - La page d'accueil propose le choix entre la lecture par parcours et la lecture par événements.
    - En mode **parcours**, une page intermédiaire liste l'ensemble des parcours de la carte ; le clic sur un parcours affiche une page de déroulement linéaire complet de sa séquence de composants.
    - En mode **événements**, la première page affiche le premier événement déterminé par l'application à partir du modèle de données, puis déroule linéairement les événements jusqu'au premier embranchement ; à chaque embranchement, la page affiche des liens hypertexte vers chaque parcours possible, avec le nom du parcours correspondant entre parenthèses ; le choix d'un lien hypertexte ouvre une nouvelle page poursuivant le déroulement linéaire jusqu'au prochain embranchement.
    - Chaque page de déroulement dispose d'un lien de retour vers le sommaire. Chaque page de la vue événements dispose d'un lien vers la page précédente.
    - L'opération d'export ne marque pas la carte narrative ni le projet comme modifiés.
- **Périmètre MVP** :
    - L'export technique pour réimport dans un autre projet n'est pas disponible.
    - La lecture par événements n'est pas disponible ; elle sera implémentée dans une version ultérieure.
    - La lecture par relations entre agents (relations d'agent à agent) n'est pas disponible ; elle sera implémentée dans une version ultérieure.

## SU008 : Gérer les associations agent-état

- **Description** : En tant qu'auteur, je peux associer un agent à zéro, un ou plusieurs états, et réciproquement associer un état à zéro, un ou plusieurs agents, afin de définir qui intervient dans chaque étape de mon récit.

- **Complément** :
    - Un agent est un élément de données appartenant au projet (et non à une carte narrative). Un état appartient à une carte narrative. L'association agent-état est portée par la carte narrative au sein de la table des relations état-agent.
    - La relation agent-état est non orientée et porte une note optionnelle.
    - Un même agent peut être associé à 0, 1 ou n états distincts. Un même état peut être associé à 0, 1 ou n agents distincts.
    - Entre un agent et un état donnés, il ne peut exister qu'une seule association (pas de doublon).
    - La relation agent-état est indépendante des parcours : elle ne dépend que des composants qu'elle relie.
    - Les associations agent-état sont éditées depuis deux points d'entrée distincts, tous deux persistants :
        1. Depuis la vue Events : le menu contextuel d'un état propose « Associer des agents... ». Un dialogue dédié liste l'ensemble des agents du projet avec leur état d'association courant (coché/décoché) pour cet état ; cocher associe, décocher dissocie. Le dialogue permet également de créer un nouvel agent et de l'associer en une seule opération.
        2. Depuis la vue agents (matrice agents × états) : la cellule à l'intersection d'un agent et d'un état matérialise l'association ; cocher la cellule associe, la décocher dissocie.
    - Les deux points d'entrée modifient la même donnée métier. Toute association ou dissociation est immédiatement répercutée dans l'autre vue.
    - Les agents associés à un état sont représentés dans la vue Events par des badges d'agents affichés sur le node de l'état.

- **Critères d'acceptation** :
    - L'utilisateur peut associer un agent à un état depuis le menu contextuel de l'état dans la vue Events.
    - L'utilisateur peut associer un agent à un état depuis la matrice de la vue agents.
    - L'utilisateur peut dissocier un agent d'un état depuis l'un ou l'autre point d'entrée.
    - L'utilisateur peut créer un nouvel agent depuis le dialogue d'association de la vue Events et l'associer immédiatement à l'état courant.
    - L'application empêche la création d'une association en double entre un agent et un état.
    - La suppression d'un agent supprime en cascade toutes ses associations avec les états, avec confirmation préalable.
    - La suppression d'un état supprime en cascade toutes ses associations avec les agents.
    - Les associations créées ou supprimées depuis une vue sont immédiatement visibles dans l'autre vue.
    - Tout agent associé à au moins un état est visible sous forme de badge sur le node de cet état dans la vue Events.
    - Toute association, dissociation ou création d'agent marque la carte, et donc le projet, comme modifiés.

- **Périmètre MVP** :
    - Les associations agent-état font partie du MVP ; les deux points d'entrée (vue Events et matrice de la vue agents) sont spécifiés pour le MVP.
    - La note optionnelle portée par la relation agent-état n'est pas éditable dans le MVP.
    - Les relations entre agents (graphe d'interactions agent-agent) sont exclues du modèle de données applicatif et du MVP : un agent n'est jamais directement relié à un autre agent.

## SU009 : Gérer la vue agents

- **Description** : En tant qu'auteur, je peux visualiser et éditer les associations entre les agents du projet et les états de la carte narrative dans un second espace de travail dédié, afin de gérer les agents indépendamment du graphe des enchaînements.

- **Complément** :
    - La vue agents est un espace de travail distinct de la vue Events, présenté dans la barre d'onglets sous l'onglet « Agents » (TSK07). Les états et les événements forment un graphe de flux (d'un état initial vers des états finaux) ; la relation agent-état est une relation d'appartenance, représentée par une matrice et non par un graphe de flux.
    - La vue agents se présente sous la forme d'une matrice agents × états : une ligne par agent du projet, une colonne par état de la carte narrative courante.
    - L'ordre des colonnes est défini par la règle de gestion RG068 : par défaut, ordre de création des états (identifiant croissant) ; l'utilisateur peut réordonner les colonnes, cet ordre personnalisé étant conservé dans les métadonnées graphiques du projet entre les sessions ; l'état initial occupe toujours la première colonne et ne peut pas être déplacé ; tout état nouvellement créé apparaît en fin d'ordre. Les lignes (agents) suivent la même règle. Chaque colonne affiche le libellé de l'état (tronqué selon les règles d'affichage courantes) ; le type de l'état est matérialisé par la couleur du contour de la carte et précisé dans l'infobulle (révision TSK12, point 03 : le libellé de type est supprimé).
    - Une cellule cochée matérialise l'association entre l'agent de la ligne et l'état de la colonne. L'édition s'effectue en cochant/décochant la cellule.
    - Les agents sont portés par le projet : la vue agents est unique pour l'ensemble du projet, contrairement à la vue Events qui est liée à une carte narrative.
    - L'application autorise l'édition sans contrôle de complétude : un état peut temporairement n'être associé à aucun agent (philosophie identique à la règle des états finaux manquants en cours d'édition). Des règles de complétude pourront être ajoutées ultérieurement sous forme d'avertissements non bloquants.
    - Les règles de gestion de la matrice (agent-état) sont définies dans SU008.
    - Navigation croisée entre vues (P2) :
        - Depuis la vue Events, le menu contextuel d'un état propose « Voir dans la vue agents » : l'application bascule vers la vue agents et met en évidence la colonne de cet état (surbrillance + défilement).
        - Depuis la vue agents, le menu contextuel d'un agent (ou un double-clic sur sa ligne) propose « Voir dans la vue Events » : l'application bascule vers la vue Events et met en évidence l'ensemble des états associés à cet agent (les nodes concernés passent en surbrillance, le reste du graphe est atténué).
        - Le contrat commun aux deux vues est une méthode « mettre le focus sur une entité » (entité simple ou ensemble dérivé du modèle). Le focus est un état visuel temporaire : il ne marque pas le projet comme modifié et n'est pas conservé dans les métadonnées graphiques. Un clic dans le vide ou la touche Échap relâche le focus.
        - Ces navigations croisées sont reportées en priorité P2 ; le contrat de focus est néanmoins spécifié dès la conception pour éviter toute refonte ultérieure.

- **Critères d'acceptation** :
    - L'utilisateur peut basculer entre la vue Events et la vue agents via la barre d'onglets.
    - La matrice affiche une ligne par agent du projet et une colonne par état de la carte courante.
    - L'utilisateur peut cocher/décocher une cellule pour associer/dissocier un agent et un état.
    - Les associations modifiées depuis la vue Events sont immédiatement répercutées dans la matrice, et réciproquement.
    - L'ordre des colonnes respecte la règle de gestion RG068 (ordre de création par défaut, réordonnancement manuel rémanent, état initial toujours en première colonne).
    - L'utilisateur peut créer, renommer, modifier ou supprimer un agent depuis la vue agents.
    - (P2) L'utilisateur peut basculer vers la vue agents ciblée sur un état depuis le menu contextuel de cet état dans la vue Events.
    - (P2) L'utilisateur peut basculer vers la vue Events ciblée sur les états d'un agent depuis la vue agents.
    - Le focus de navigation ne marque pas le projet comme modifié et n'est pas conservé entre les sessions.

- **Périmètre MVP** :
    - La vue agents (matrice agents × états) fait partie du MVP et sera implémentée en tant que second espace de travail.
    - La navigation croisée entre vues est reportée en priorité P2 ; le contrat de focus est néanmoins spécifié dès la conception pour éviter toute refonte ultérieure.
    - Les relations entre agents sont exclues : la vue agents ne représente que les associations agent-état.
