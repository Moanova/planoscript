# TSK11 — Révision esthétique du layout (thème sombre)

- **Épic** : aucune (tâche transversale UI)
- **Statut** : Doing
- **Date de début** : 24-10-2026
- **Dépendances** : aucune (TSK01–TSK10 Done)
- **Documents de support** : charte `docs/specification/98_layout_revision-FR.md`, maquette `docs/specification/97_layout_revision-EN.svg`

## Périmètre

Refonte du thème clair actuel vers le thème sombre de la charte 98, avec
centralisation de la palette dans `config.json` (convention AGENTS.md :
aucune valeur codée en dur pour l'UI). Hors périmètre : barres latérales
(gauche future, droite « Journey Filter » en chantier ultérieur — la maquette
les figure comme espaces réservés), migration de layouts persistés (le champ
`layout.color` n'est jamais renseigné par aucune fonctionnalité : aucun projet
ne contient de couleur persistée, les couleurs par défaut s'appliquent).

## Palette cible (charte 98)

| Rôle | Valeur |
|---|---|
| Fond principal | `#1E1E1E` |
| Surfaces (menus, panneaux, nœuds) | `#2D2D2D` |
| Bordures / séparateurs | `#383838` |
| Grille | `#333333` |
| Texte principal / secondaire | `#FFFFFF` / `#CCCCCC` |
| State (contour + libellé) | `#E5C07B` (or doux) |
| Event (contour + libellé) | `#D19A66` (cuivre) |
| Ancres (entrantes et sortantes) | `#F0F0F0` (blanc doux, unique) |
| Survol (contour continu) | `#F0F0F0` |
| Sélection | contour pointillé (6/4), teinte du type conservée |
| Connexions | pointillées `#CCCCCC` |
| Badge d'agents | remplissage `#E5C07B`, contour `#F0F0F0`, texte `#1E1E1E` |
| Onglets Journey/Agents | identiques et neutres (`#2D2D2D` / `#383838` / `#CCCCCC`) |

Règle de priorité des contours : sélection (pointillés) > survol (blanc doux
continu) > type (or ou cuivre). Un objet sélectionné affiche un contour
pointillé de la teinte de son type, y compris au survol.

Typographie : `Segoe UI, system-ui, sans-serif` — menus/libellés ~12 px,
texte des nœuds ~13 px, titres ~14 px gras. Arrondi des nœuds ~6 px.
Suppression des ombres sous les nœuds (aucun `QGraphicsDropShadowEffect`
n'existe dans le code : point à vérifier visuellement).

## Plan d'implémentation

### Étape 1 — Palette dans `config.json`

Ajouter les clés (valeurs par défaut = charte 98) :
`bg_primary`, `bg_surface`, `border_color`, `text_primary`,
`text_secondary`, `state_color`, `event_color`, `anchor_color`,
`hover_color`, `connection_color`, `badge_bg_color`, `badge_border_color`,
`badge_text_color`, `menu_hover_bg` ; mettre à jour `grid_minor_color` /
`grid_major_color` / `temp_connection_color` ; ajouter `node_font_family`,
`menu_font_size`, `node_font_size`, `node_title_font_size`.

### Étape 2 — Nœuds (`src/ui/nodes/`)

- `base_node.py` : remplacer les constantes de couleur en dur par lecture
  config (`_get_config`) ; fond `#2D2D2D`, contour du type, texte `#FFFFFF` ;
  polices Segoe UI (13 px nœud, 14 px gras titre) ; suppression des ombres ;
  ports : remplissage `#1E1E1E`, contour `#F0F0F0` (ancres) ;
  `set_selected_appearance` : contour **pointillé** de la teinte du type
  (remplace `SELECTED_BG_COLOR`/`SELECTED_BORDER_COLOR`) ;
  `hoverEnterEvent`/`hoverLeaveEvent` : contour `#F0F0F0` continu au survol,
  **priorité sélection > survol** (un nœud sélectionné reste pointillé même
  au survol — ajuster la logique hover pour ne pas écraser la sélection).
- `state_node.py` : `COLORS` → contour/libellé `#E5C07B`, fond `#2D2D2D`,
  texte `#FFFFFF` ; badge : `BADGE_BG_COLOR #E5C07B`,
  `BADGE_BORDER_COLOR #F0F0F0`, `BADGE_TEXT_COLOR #1E1E1E`.
- `event_node.py` : `COLORS` → contour/libellé `#D19A66`, fond `#2D2D2D`,
  texte `#FFFFFF`.
- `connection.py` : `DEFAULT_PEN` → `#CCCCCC` pointillé (`Qt.DashLine`,
  motif 6/4) ; `DEFAULT_SELECTED_PEN` → pointillé de la couleur de la
  connexion (déjà le comportement de `set_selected_appearance`) ;
  survol → `#F0F0F0` (remplace le bleu) ; la flèche reprend la couleur du
  trait (déjà le cas via `pen.color()`).

### Étape 3 — Vues et widgets

- `journey_workspace.py` : fond du canvas `#1E1E1E`
  (`scene.setBackgroundBrush`) ; grille via config (mise à jour des valeurs) ;
  scrollbars : fond `#2D2D2D`, poignée `#383838`/hover `#CCCCCC` ;
  connexion temporaire (rubber band) → `temp_connection_color` mis à jour.
- `tab_bar.py` : onglets identiques et neutres — fond `#2D2D2D`, contour
  `#383838`, libellé `#CCCCCC`, **plus de marqueur bleu** sur l'onglet actif ;
  survol discret.
- `info_bar.py` : fond `#2D2D2D`, séparateur `#383838`, texte `#CCCCCC`.
- `agents_workspace.py` (matrice) : thème sombre — fond `#1E1E1E`, en-têtes
  et cellules `#2D2D2D`, grille `#383838`, texte `#FFFFFF`/`#CCCCCC` ;
  teinte de focus (`_focus_color`, actuellement `QColor(220, 235, 255)`) →
  à redéfinir dans la palette sombre (proposition : surface surélevée
  `#383838` ou contour `#F0F0F0` — à valider en revue visuelle).

### Étape 4 — Fenêtre principale et dialogues

- `main_window.py` : stylesheet de la barre de menus → fond `#2D2D2D`,
  texte `#FFFFFF`, survol `#383838`, désactivé `#808080` ; menus déroulants
  idem ; page d'accueil : fond `#1E1E1E`, texte `#CCCCCC`, lien `#E5C07B` ;
  police Segoe UI ~12 px.
- Dialogues (`component_dialog.py`, `agent_dialog.py`,
  `agent_association_dialog.py`, `agent_management_dialog.py`,
  `about_dialog.py`, `change_log_dialog.py`) : thème sombre — surfaces
  `#2D2D2D`, texte `#FFFFFF`/`#CCCCCC`, bordures `#383838` ; messages
  d'erreur : conserver une couleur lisible sur fond sombre (proposition
  `#D19A66` cuivre ou rouge adouci — à valider).

### Étape 5 — Vérifications

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite de tests complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen jetable (non commité, pattern
   `tests/test_agents/offscreen_state_badges.py`) : instancier nœuds
   State/Event + connexion, vérifier par rendu `QImage` les points visuels :
   fond `#1E1E1E`, contours or/cuivre, sélection pointillée de la teinte du
   type, survol `#F0F0F0`, ancres `#F0F0F0`, connexion pointillée `#CCCCCC`,
   badge `#E5C07B`/`#F0F0F0`/`#1E1E1E`.
4. Vérification manuelle de l'absence d'ombres sous les nœuds (point 10 de
   la charte — aucun effet d'ombre trouvé dans le code à date).

## Décisions actées

- **Badges d'agents** : remplissage `#E5C07B` (teinte des objets State, le
  badge n'apparaît que sur les nœuds d'état), contour `#F0F0F0`, texte
  `#1E1E1E` (lisibilité sur fond clair). Consigné dans la charte 98 (section 5
  et variables CSS `--badge-*`).
- **Dialogues** : le thème sombre s'applique aussi aux dialogues (charte 98,
  point 14).
- **Journey Filter** : hors périmètre — placeholder non fonctionnel envisagé
  puis écarté ; la barre latérale droite fera l'objet d'un chantier ultérieur,
  y compris la décision de sa présence dans les deux espaces de travail
  (charte 98, point 12 et section 7).
- **Barre latérale gauche** : n'existe pas à ce jour ; pourra être ajoutée plus
  tard, hors périmètre (charte 98, point 11).
- **Couleurs de layout persistées** (`NodeLayout.color` /
  `ConnectionLayout.color`) : aucune migration nécessaire — le champ n'est
  jamais renseigné (aucune fonctionnalité utilisateur ne permet de colorer un
  nœud/une connexion ; `Connection.set_color` n'a aucun appelant). Les
  couleurs par défaut de la charte s'appliquent à tous les projets.
- **Centralisation** : toute la palette passe par `config.json` via
  `config_loader.get` (convention AGENTS.md).

## Points ouverts (à valider en revue visuelle)

- Teinte de focus de la matrice agents en thème sombre.
- Couleur des messages d'erreur des dialogues sur fond sombre.
- Connexion temporaire (rubber band) : `#CCCCCC` pointillé ou `#F0F0F0` ?

## Choix par défaut retenus (implémentation, à réévaluer en test visuel)

- **Focus matrice agents** : `focus_color = #383838` (surface surélevée
  discrète, lisible sur `#1E1E1E`) ;
- **Messages d'erreur des dialogues** : `error_color = #D19A66` (cuivre,
  teinte Event de la charte, lisible sur fond sombre) ;
- **Connexion temporaire (rubber band)** : `temp_connection_color = #CCCCCC`
  (gris clair, cohérent avec les connexions pointillées).

## Journal

- 24-10-2026 : passage en Doing. Mise à jour de la charte 98 (badges,
  dialogues, retrait des barres latérales du périmètre). Plan établi.
- 24-10-2026 : implémentation terminée.
  - Étape 1 : palette complète dans `config.json` (clés `bg_primary`,
    `bg_surface`, `border_color`, `text_primary`, `text_secondary`,
    `state_color`, `event_color`, `anchor_color`, `hover_color`,
    `connection_color`, `badge_*`, `menu_hover_bg`, `error_color`,
    `focus_color`, `node_font_family`, `node_corner_radius_px`,
    `menu/node/node_title_font_size_px`) ; nouveau module
    `src/ui/utils/theme.py` (constantes + stylesheets construits, fallback
    = charte 98).
  - Étape 2 : nœuds — `base_node.py` (couleurs via theme, ports
    `#1E1E1E`/`#F0F0F0`, sélection = contour pointillé 6/4 de la teinte du
    type avec priorité sélection > survol via `_apply_outline`, arrondi 6 px
    via `paint`/`shape`/`boundingRect` sur `QPainterPath.addRoundedRect`,
    libellé de type « State »/« Event » en couleur du type, 14 px gras,
    polices Segoe UI) ; `state_node.py` (or doux + badge
    `#E5C07B`/`#F0F0F0`/`#1E1E1E`) ; `event_node.py` (cuivre) ;
    `connection.py` (pointillé `#CCCCCC` 6/4, survol `#F0F0F0` continu).
    Note : `setDashPattern` produit `CustomDashLine` (et non `DashLine`) —
    le test offscreen accepte les deux.
  - Étape 3 : `journey_workspace.py` (fond scène `#1E1E1E`, scrollbars via
    `theme.SCROLLBAR_STYLESHEET`, grille `#333333` via config) ;
    `tab_bar.py` (onglets identiques et neutres, plus de marqueur bleu) ;
    `info_bar.py` (fond `#2D2D2D`, texte `#CCCCCC`) ;
    `agents_workspace.py` (stylesheet sombre + `_focus_color` via config).
  - Étape 4 : `main_window.py` (menu bar via `theme.MENU_BAR_STYLESHEET`,
    page d'accueil sombre, lien `#E5C07B`) ; 6 dialogues en
    `theme.DIALOG_STYLESHEET` (erreurs en `#D19A66`) ; `main.py` applique
    `theme.APP_STYLESHEET` sur la QApplication (QMessageBox, menus
    contextuels orphelins) ; menus contextuels des deux vues en
    `theme.CONTEXT_MENU_STYLESHEET`.
  - Étape 5 : vérifications — `py_compile` OK sur tous les fichiers
    modifiés ; `pytest tests/ -q` : **95 passed** (hors
    `tests/test_application`, skippé sans session GUI/pywinauto) ;
    test offscreen jetable TSK11 : **27/27 PASS** (couleurs nœuds, sélection
    pointillée, priorité survol, ancres, badge, connexion pointillée, fond
    canvas, rendu QImage pixel par pixel) ; smoke tests offscreen : fenêtre
    principale + 5 dialogues instanciés sans erreur ; tests offscreen
    existants (`offscreen_state_badges.py`, `offscreen_anomaly_regression.py`)
    toujours OK.
  - Point 10 de la charte (ombres) : aucun `QGraphicsDropShadowEffect`
    n'existait dans le code — rien à supprimer, confirmé.
