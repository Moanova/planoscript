# AGENTS.md — Planoscript

Règles de travail pour tout agent IA intervenant sur ce dépôt.

## Vue d'ensemble

Planoscript est un éditeur graphique de cartes narratives :
application desktop PySide6 (Python >= 3.10) composée d'états (States),
d'événements (Events) et d'agents reliés par des arcs, avec sauvegarde JSON
et layout visuel persistant. MVP : deux espaces de travail — vue Parcours
(Journey) et vue Agents (matrice agents × états, SU008/SU009) —, une seule
carte narrative par projet, sélection unique (pas de rubber band
multi-sélection).

## Commandes

- Lancer l'application : `python src/main.py` (depuis la racine du dépôt)
- Lancer les tests : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`
  - `tests/test_application/` (pywinauto, FNxxx) est automatiquement skipped
    sans session GUI.
- Vérifier la syntaxe : `python -m py_compile <fichiers modifiés>`

## Pièges connus

- **Single-instance** : `src/main.py` contient un garde `QLocalServer`. Si une
  instance tourne déjà, un nouveau lancement **se termine silencieusement**.
  Toujours fermer complètement l'instance en cours avant de tester une
  modification (sinon on teste l'ancien code).
- Le working tree contient fréquemment du travail non commité : jamais de
  reset/checkout destructif, et pas de commit sans instruction explicite de
  l'utilisateur.

## Architecture

Flux : UI → use cases → services → models. L'UI ne modifie jamais
directement le modèle métier : passer par les use cases/services.

```
src/
├── main.py                          # Point d'entrée (QApplication, single-instance)
├── config/                          # config.json + user_state.json et leurs loaders
├── core/
│   ├── models/                      # data_model (entités métier), view_model (layouts, enums)
│   └── services/                    # ProjectService, ArcService, LayoutService, ...
├── usecases/                        # project_management, file_management, view_management
└── ui/
    ├── main_window.py               # Fenêtre principale, barre de menus, orchestration
    ├── views/journey_workspace.py   # Vue graphique (QGraphicsView)
    ├── nodes/                       # base_node, state_node, event_node, agent_node, connection
    ├── widgets/                     # info_bar, ...
    ├── utils/                       # ui_utils
    └── dialogs/                     # about_dialog, change_log_dialog, component_dialog
```

## Règles métier et exigences

- Chaque règle métier RG0xx est définie dans
  `docs/specification/02_business_rules-FR.md` (versions EN/FR dans
  `docs/specification/`), référencée en commentaire dans le code qui
  l'implémente, et couverte par un test (ex. `tests/test_relations/`).
- Toute modification d'une règle métier implique la mise à jour du test
  correspondant.
- Les user stories (SUxxx) sont dans `docs/specification/01_user_stories-*.md` ;
  les tests d'application (pywinauto) suivent la nomenclature `test_fnXXX_*.py`
  et sont spécifiés dans `tests/SPECIFICATION.md`.
- Les entrées de menu non implémentées sont stubbées dans `main_window.py`
  par `self.menu_actions['clé'] = ... addAction(..., lambda: None)` : les
  conserver lors des refactors de menus (les épiques EPC01-EPC03 réactiveront
  certaines d'entre elles).

## Documentation à recharger en début de séance

Au début de chaque séance de travail, recharger dans le contexte (sans que
cela dispense de relire la section ciblée au moment d'une modification) :

- Tous les documents de `docs/specification/` (versions FR ou EN au choix, le
  contenu est identique) : user stories, règles de gestion, features,
  interface, menu, data model, périmètre MVP.
- `docs/project/kanban.md` (état des tâches, dépendances, fichier de détail
  de la tâche en cours dans `docs/project/tasks/`).

## Suivi de projet

- L'avancement est suivi dans `docs/project/kanban.md` (épiques EPCnn,
  tâches TSKnn, dépendances `→ #TSKnn` déclarées uniquement sur la tâche
  dépendante).
- Le détail d'une tâche TSKnn (analyse, décisions, journal) est consigné dans
  `docs/project/tasks/TSKnn_*.md`, créé au passage en Doing.
- Une tâche ne passe en Doing que si ses dépendances sont en Done.
- L'avancement décrit dans `docs/project/kanban.md` est aussi reporté dans le board planoscript du service miro.com.

## Conventions

- Aucune valeur codée en dur pour l'UI : passer par config.json
  (`config.config_loader.get` avec valeur par défaut) ou par une constante de
  classe (ex. `HIT_AREA_WIDTH`).
- Docstrings et commentaires de code : anglais. Messages de commit : français,
  préfixés par la date (ex. `2026-10-10 : ...`).
- Diff minimal : ne pas modifier ce qui n'est pas demandé ; retirer
  complètement le code mort (pas de `_unused`, pas de shims de compatibilité).
- Découplage Qt : le workspace communique avec MainWindow via des signaux
  plutôt que par appel de méthodes privées d'un autre composant.

## Patterns UI établis (ne pas faire régresser)

- **Hit-testing** : zone cliquable définie par `shape()` (QPainterPathStroker)
  avec un `boundingRect()` couvrant la zone — jamais la seule épaisseur du
  stylo (voir `Connection.shape`).
- **Infobulles** : affichage immédiat dans `hoverEnterEvent` via
  `QToolTip.showText()` ; le workspace avale l'événement `ToolTip` automatique
  de Qt (`JourneyWorkspace.viewportEvent`). Ne pas réintroduire le mécanisme
  automatique (délai système + infobulle en double).
- **Menu contextuel** : pattern `menu.exec()` + dispatch sur l'action retournée
  (voir `JourneyWorkspace.show_context_menu`) — pas de timer, pas de drapeaux
  d'état, une seule connexion par signal.
- **Feedback de sélection** : brancher `set_selected_appearance` via
  `itemChange(ItemSelectedChange)` (pattern commun à BaseNode et Connection).
- **Sélection au clic droit** : sélectionner l'item sous le curseur avant
  d'ouvrir le menu contextuel.

## Vérifications attendues après chaque modification

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite de tests complète (commande ci-dessus).
3. Pour l'UI Qt : test ciblé offscreen (script jetable, non commité) —
   instancier le composant réel, simuler les événements Qt, vérifier par rendu
   `QImage` si le point à valider est visuel.
4. Ne pas lancer l'application en tâche de fond pour tester : préférer les
   tests offscreen (voir single-instance).
