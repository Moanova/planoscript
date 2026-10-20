# TSK07 — Bascule d'espace de travail : barre d'onglets Parcours ↔ Agents

- **Épic** : EPC03 — Implémenter la vue agents (SU009)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : aucune

## Périmètre

Mise en place de la barre d'onglets « Parcours / Agents » et de la
bascule entre les deux espaces de travail de la fenêtre principale.
L'onglet « Parcours » héberge le `JourneyWorkspace` existant ;
l'onglet « Agents » hébergera la vue agents (matrice, TSK08) — dans
cette tâche, il affiche un espace réservé (placeholder) minimal, la
matrice n'étant pas encore implémentée. La barre d'onglets n'est visible
que lorsqu'un projet est ouvert (le message d'accueil occupe tout
l'espace sinon).

## Règles et critères applicables

- **SU009** : « L'utilisateur peut basculer entre la vue parcours et la
  vue agents via la barre d'onglets. »
- **04_interface-FR.md** (section 5) : barre d'onglets de 40 px,
  onglet « Parcours » actif par défaut, onglet « Agents » ; les onglets
  « Relations » et « Chapitres » sont des reliquats retirés du MVP.
  Styles spécifiés (arrière-plan `#f8f8f8`, sélection blanc + gras +
  bordure inférieure visible, survol `#e0e0e0`).
- **RG041/RG006** (par analogie) : la bascule d'onglet est un état
  d'affichage : elle ne marque pas le projet comme modifié et n'est pas
  conservée entre les sessions (l'onglet Parcours est actif à
  l'ouverture).

## État des lieux (existant mobilisable)

- `tab_bar.py` **n'existe pas** dans `src/ui/widgets/` (seul
  `info_bar.py` est présent) — la spécification d'interface (v2.0,
  « partiellement implémentée ») décrit un état antérieur ; la barre
  d'onglets est donc à créer intégralement.
- Zone centrale : `middle_section` (QGridLayout) reçoit soit le message
  d'accueil (sans projet), soit le `JourneyWorkspace` (projet ouvert).
- Le `JourneyWorkspace` est recréé à chaque ouverture/création de
  projet (`_init_workspace`).

## Plan d'implémentation

1. **`TabBar`** (`src/ui/widgets/tab_bar.py`) — sur la base de la
   spécification d'interface (hauteur 40 px, styles indiqués) :
   - Deux boutons d'onglet « Journey » / « Agents » (libellés en
     anglais, cohérents avec le reste de l'UI).
   - Signal `currentChanged(str)` émis avec le nom de l'onglet activé ;
     apparence sélection/survol gérée par feuille de style (QSS).
   - Constantes de classe pour les styles (convention AGENTS.md).
2. **Espace de travail en pile** (`QStackedWidget`) dans
   `main_window.py` :
   - `_init_ui` : la zone centrale devient un `QStackedWidget` contenant
     (a) le message d'accueil, (b) un conteneur « Journey » (TabBar +
     JourneyWorkspace), (c) un conteneur « Agents » (TabBar + placeholder
     pour la matrice de TSK08).
   - Sans projet : page accueil. Projet ouvert : page workspace, onglet
     « Journey » actif par défaut.
   - La TabBar est partagée visuellement au-dessus de la pile (une
     seule instance) ou dupliquée par page — à trancher : une seule
     instance au-dessus du `QStackedWidget` (source unique de l'état
     d'onglet, pas de désynchronisation possible).
3. **Bascule** :
   - Connexion du signal `currentChanged` au `setCurrentWidget` de la
     pile ; aucun traitement de données (lecture seule à ce stade).
   - L'état d'onglet n'est pas persisté (retour sur « Journey » à
     chaque ouverture de projet).
   - Compatibilité des raccourcis/menus existants : les entrées de menu
     qui ciblent le workspace (Edit/Delete/New node, association
     d'agents) restent fonctionnelles sur l'onglet Journey ; à tester
     pour vérifier qu'aucune action ne plante si l'onglet Agents est
     actif (les actions portent sur la sélection du JourneyWorkspace,
     qui est indépendante de la pile).
4. **Placeholder onglet Agents** (`src/ui/views/agents_workspace.py`,
   classe `AgentsWorkspace`) :
   - Widget minimal (fond blanc, message informatif « Agents view —
     not implemented yet » ou simple widget vide selon le style du
     projet). Créé maintenant pour que TSK08 remplace uniquement son
     contenu, sans toucher à la bascule.
5. **Tests** :
   - Test offscreen local (rédigé, non exécutable dans la sandbox) :
     création de la MainWindow sans projet (accueil visible, pas
     d'onglets), création d'un projet (onglets visibles, Journey actif),
     bascule Agents (page visible), retour Journey.
   - Suite unitaire existante inchangée (85 passed attendus).

## Décisions à valider

- **Une seule TabBar au-dessus du QStackedWidget** (recommandé : état
    d'onglet à source unique) vs une TabBar par page.
- **Placeholder minimal** pour l'onglet Agents (recommandé : message
    informatif, remplacé par la matrice en TSK08) vs widget vide.
- **Onglet actif non persisté** : « Journey » actif à chaque ouverture
    (conforme à la philosophie RG041 : les états d'affichage ne sont pas
    des données).

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen de la bascule : à exécuter localement (libGL).
4. Test manuel utilisateur : reporté en fin d'EPC03 (décision de
   cadrage).

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : trois décisions validées par l'utilisateur : TabBar unique
  au-dessus du QStackedWidget (source unique de l'état d'onglet, expliquée
  et validée) ; placeholder informatif pour l'onglet Agents ; onglet
  Journey actif non persisté à l'ouverture.
- 15-10-2026 : implémentation terminée :
  - `ui/widgets/tab_bar.py` (nouveau) : TabBar — boutons checkable
    Journey/Agents, QSS de la spécification d'interface (40 px,
    `#f8f8f8`, sélection blanc/gras/bordure bleue, survol `#e0e0e0`),
    signal `currentChanged(str)`, `setCurrentTab`/`forceCurrentTab`
    (le second sans émission, pour l'initialisation).
  - `ui/views/agents_workspace.py` (nouveau) : AgentsWorkspace
    placeholder (« Agents view — not implemented yet »), remplacé par
    la matrice en TSK08 sans toucher à la bascule.
  - `main_window.py` : zone centrale restructurée — TabBar unique +
    `QStackedWidget` (pages accueil / journey / agents) ; TabBar
    masquée sans projet, visible à l'ouverture avec Journey forcé ;
    `_init_workspace` repeuple la page journey (l'ancien vidage du
    middle_layout est remplacé par le vidage de journey_page) ;
    `_show_welcome_message` repeuple la page d'accueil et masque la
    TabBar ; handler `_on_tab_changed`.
  - Constat consigné : `tab_bar.py` était absent du dépôt (la
    spécification d'interface v2.0 le décrivait « partiellement
    implémenté » à tort) — la barre a été créée intégralement.
  - Vérifications : `py_compile` OK ; suite complète 85 passed ; test
    offscreen de bascule rédigé dans
    `tests/test_agents/offscreen_workspace_tabs.py` (local, libGL).
