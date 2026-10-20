# TSK05 — Badges d'agents sur les nodes d'état dans la vue parcours

- **Épic** : EPC02 — Associer des agents à un état (FN030, SU008)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK03 (Done)

## Périmètre

Représentation visuelle des associations agent-état dans la vue parcours :
tout agent associé à au moins un état est visible sous forme de badge sur
le node de cet état (SU008 : « Les agents associés à un état sont
représentés dans la vue parcours par des badges d'agents affichés sur le
node de l'état »). Comprenant l'affichage initial (à l'ouverture du
projet) et le rafraîchissement après toute modification des associations
(dialogue de TSK04, suppression d'agent TSK02, suppression d'état).

## Règles et critères applicables

- **SU008** : badge par agent associé, affiché sur le node de l'état.
- **FN030** : « Les agents associés à un état sont représentés par des
  badges sur le node de l'état dans la vue parcours. »
- **RG066** : les associations sont indépendantes des parcours ; les
  badges ne dépendent d'aucun filtrage de parcours (MVP : pas de filtre
  actif de toute façon).
- Aucune précision de la spécification sur la forme exacte du badge
  (contenu, position, style) : c'est un point de conception UI à trancher
  ci-dessous.

## État des lieux (existant mobilisable)

- `StateNode` hérite de `TypedNode`/`BaseNode` (`QGraphicsRectItem`) :
  rectangle 80×40 (config `node_default_width/height`), label tronqué à
  8 caractères en haut-gauche, ports rouge/vert à gauche/droite,
  infobulle alimentée par `update_entity_data()`.
- `update_entity_data()` (BaseNode) rafraîchit label + tooltip : point
  d'accroche naturel pour rafraîchir aussi les badges.
- `JourneyWorkspace.create_node_from_data` crée les nodes visuels ;
  le workspace connaît `narrative_map` (accès aux `state_agent_rel`).
- Convention AGENTS.md : aucune valeur codée en dur pour l'UI → passer
  par `config.json` ou une constante de classe.

## Plan d'implémentation

1. **Conception du badge** (à valider) :
   - **Forme recommandée** : initiales du libellé de l'agent (2 lettres,
     ex. « He » pour « Hero ») dans une pastille circulaire de 14 px,
     alignées **sous le label du node**, à l'horizontale, débordant
     légèrement du bord inférieur du rectangle si nécessaire. Nombre
     limité : si plus de badges que la place disponible (max ~4 sur 80 px
     de large), afficher les premiers puis un badge « +n ».
   - Couleurs : pastille par défaut (fond gris clair, bordure noire,
     texte noir), différenciation sujet/objet non requise par la
     spécification — MVP : une seule apparence.
   - Constantes de classe `StateNode` : `BADGE_DIAMETER`, `BADGE_SPACING`,
     `MAX_BADGES` (convention AGENTS.md : constantes de classe admises).
   - **Infobulle** : le tooltip du node liste les agents associés
     (ajout d'une section « Agents: A, B » via `update_entity_data`).
2. **`StateNode.refresh_agent_badges(agents)`** :
   - Méthode dédiée (les autres types de nodes n'ont pas de badges) qui
     reconstruit les items de badge (détruit/recrée des
     `QGraphicsEllipseItem` + `QGraphicsTextItem` enfants) à partir de la
     liste des agents associés passée en paramètre.
   - Les badges sont non sélectionnables et non interactifs (pas de clic,
     pas d'obstruction de la sélection : `ItemIsSelectable` à False).
3. **Alimentation des données → vue** :
   - `StateNode` reçoit les agents associés via le workspace :
     `JourneyWorkspace` expose une méthode
     `refresh_state_badges(state_node)` qui calcule la liste des agents
     associés à l'état (`find_association` sur chaque agent du projet)
     et appelle `refresh_agent_badges`.
   - **Affichage initial** : à la création des nodes
     (`create_node_from_data`) et au chargement d'un projet
     (parcours de tous les State nodes).
   - **Rafraîchissement** : MainWindow appelle le rafraîchissement du
     node concerné après : fermeture du dialogue d'association (TSK04,
     l'état ciblé est connu), suppression d'agent (TSK02 : rafraîchir
     tous les State nodes), suppression d'état (le node disparaît, rien
     à faire), édition d'agent (le libellé peut changer → initiales à
     rafraîchir : rafraîchir tous les State nodes).
4. **Tests** :
   - La logique de calcul des initiales et de la troncature « +n » peut
     être isolée dans une fonction pure testable sans Qt (ex. :
     `_badge_texts(agents, max_badges)` en `@staticmethod`) → tests
     unitaires `tests/test_agents/test_state_badges.py`.
   - Le rendu (pastilles, positions) relève du test offscreen local
     (rendu `QImage`, convention AGENTS.md point 3) et du test manuel
     de fin d'EPC03.

## Décisions à valider

- **Forme du badge** : initiales dans pastille circulaire 14 px sous le
    label, max 4 puis « +n » ; apparence unique (pas de
    différenciation sujet/objet en MVP). Alternative : pastille
    rectangulaire, ou pastille en bordure basse du node.
- **Position** : sous le label, dans le rectangle du node. Alternative :
    rangée sous le node (débordante), ou bord supérieur.
- Ces choix visuels pourront être ajustés lors du test manuel de fin
  d'EPC03 sans impact sur l'architecture (méthode isolée dans StateNode).

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen de rendu (jetable, local) : créer un état avec 1, 2, 5
   agents associés, vérifier le nombre et la disposition des pastilles
   par rendu QImage.
4. Test manuel utilisateur : reporté en fin d'EPC03 (décision de
   cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : conception rediscutée avec l'utilisateur et validée :
  **pastille unique** (et non une pastille par agent) pour préserver la
  lisibilité — compteur des agents associés, masquée à 0, « 9+ » au-delà
  de 9, **non interactive** (pas de clic sur la pastille, pas de
  sous-menu dans le menu contextuel) ; position **bas-droit** du node ;
  consultation nominative via l'infobulle (3 premiers libellés puis
  « +n more ») et via le dialogue « Associate agents... » (liste
  complète et éditable, TSK04).
- 15-10-2026 : implémentation terminée :
  - `core/services/agent_badge_service.py` : logique pure sans Qt
    (badge_text, badge_visible, tooltip_agents_line) — testable en
    tests unitaires.
  - `state_node.py` (v2) : pastille unique bas-droit (constantes de
    classe BADGE_*), `refresh_agent_badge(count, agent_labels)` ;
    tooltip enrichi d'une ligne « Agents: ... » via
    `update_entity_data` surchargé ; repositionnement après resize
    (`update_from_layout`).
  - `journey_workspace.py` : `refresh_state_badge(node)` (calcul des
    agents associés via `find_association`) et
    `refresh_all_state_badges()` ; badge initialisé dans
    `create_node_from_data` (couvre chargement de projet et création).
  - `main_window.py` : rafraîchissement après le dialogue
    d'association (node ciblé), après édition d'agent (tooltips) et
    après suppression d'agent (cascade) via
    `_refresh_all_state_badges()`.
  - Tests : `tests/test_agents/test_agent_badge_service.py` (9 tests,
    logique pure) ; test offscreen de rendu rédigé dans
    `tests/test_agents/offscreen_state_badges.py` (à exécuter
    localement). Suite complète : 85 passed.
