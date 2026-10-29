# TSK20 — Modèle de données : clé `content` (Agent/State/Event) et `note` sur les arcs (Event_to_state, State_to_event)

- **Épic** : Évolution du modèle de données (hors epic existante)
- **Statut** : En revue (implémentation + tests faits — attente validation TSC)
- **Date de création** : 29-10-2026
- **Dépendances** : aucune
- **Décision TSC** : 29-10-2026 — périmètre confirmé après analyse :
  `content` ajouté **après** `note` dans Agent, State, Event ;
  `note` ajouté dans **Event_to_state** et **State_to_event**
  (`State_agent_rel` possède déjà `note` — inchangé).

## Motivation

Séparer deux rôles aujourd'hui confondus dans `note` :
- **`note`** = quelques notes de résumé qui décrivent l'objet (champ
  conservé, rôle inchangé ; zone de saisie réduite dans les dialogues) ;
- **`content`** = contenu narratif proprement dit (nouveau champ, même
  définition `{"type": "string", "description": ...}`, zone de saisie
  plus grande dans les dialogues).

Définition retenue (EN, pour Agent — idem pour State/Event avec le nom
de l'objet) :
```json
"content": {
   "type": "string",
   "description": "Narrative content for the agent"
}
```

## 1. Modèle de données

- `docs/specification/07_data_model-FR.json` et `-EN.json` :
  - `Agent`, `State`, `Event` : propriété `content` placée juste après
    `note` (FR : « Contenu narratif de l'agent / de l'état / de
    l'événement ») ;
  - `Event_to_state`, `State_to_event` : propriété `note` ajoutée, même
    définition que les autres objets (FR : « Annotation de la relation
    ... » / EN : « Annotation of the ... relationship ») ;
  - `State_agent_rel` : inchangé (`note` déjà présent).
- `src/core/models/data_model.py` :
  - `content: Optional[str] = None` après `note` dans `Agent`, `State`,
    `Event` ;
  - `note: Optional[str] = None` dans `Event_to_state`, `State_to_event`.
- **Pas de migration** : `to_dict`/`from_dict` sont génériques
  (`asdict` + filtre sur `__dataclass_fields__`) ; un projet existant
  sans `content`/`note` charge avec `None` (champs optionnels).

## 2. Report des impacts sur le code actif

- **Dialogues de création/édition** (`src/ui/dialogs/component_dialog.py`
  pour State/Event, `agent_dialog.py` pour Agent) :
  - ajouter un second champ `QTextEdit` « Content » (plus grand), réduire
    la zone « Note » (hauteur max / champ compact) — dimensions via
    config.json si cohérent avec la convention AGENTS.md ;
  - `get_values()` renvoie aussi `content`.
- **Use cases** : `create_node_usecase.py`, `update_component_usecase.py`
  (State/Event), `create_agent_usecase.py`, `update_agent_usecase.py`
  (Agent) : paramètre `content` optionnel, même pattern que `note`
  (« None = conserver la valeur actuelle », chaîne vide → None).
- **UI** : tooltips (`base_node.py:188-193`, `matrix_card.py`
  `_tooltip_text`) affichent `note` — décision à prendre : `content`
  dans l'infobulle longue uniquement, pas dans le tooltip court.
- **Tests** : `tests/test_components/test_update_component_usecase.py`,
  `tests/test_agents/test_agent_usecases.py`, offscreen
  `offscreen_anomaly_regression.py`, `offscreen_tsk13_agent_mechanics.py`
  (références à `note` à compléter pour `content`).

## 3. Documentation

- `07_data_model-FR/EN.json` (cf. §1) ;
- `03_features-FR/EN.md` (champs éditables des composants) ;
- `04_interface-FR/EN.md` (dialogues : champs Note/Content + dimensions) ;
- `02_business_rules-FR/EN.md` si une RG décrit les attributs éditables ;
- kanban (cette tâche), `SESSIONS.md`.

## Vérifications

1. `python -m py_compile` sur les fichiers modifiés.
2. `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` (106 passed).
3. Les 10 scripts `tests/test_agents/offscreen_*.py` PASSED.
4. Test de round-trip : sérialiser un projet avec `content`/`note`,
   recharger, vérifier les valeurs ; charger un projet ancien sans ces
   clés → `None`, pas d'erreur.

## Journal

- 29-10-2026 : création de la tâche (demande TSC 29-10-2026, périmètre
  confirmé après analyse : `note` manque réellement sur les arcs
  Event_to_state/State_to_event ; State_agent_rel l'a déjà).
- 29-10-2026 : implémentation — `data_model.py` (content après note dans
  Agent/State/Event ; note dans Event_to_state/State_to_event) ; use
  cases create/update agent + update component (paramètre `content`,
  pattern « None = conserver ») ; dialogues `component_dialog.py` /
  `agent_dialog.py` (Note compact `dialog_note_max_height_px`=60, Content
  grand `dialog_content_min_height_px`=160, nouvelles clés config.json) ;
  câblage `main_window.py` + `agent_association_dialog.py` ; tests
  unitaires (+4 content) ; stubs offscreen mis à jour ; doc
  `07_data_model` FR/EN, `03_features` FR/EN, `04_interface` FR/EN.
  Vérifications : py_compile OK, pytest 110 passed, 10 offscreen PASSED,
  round-trip JSON (content/note sérialisés, rechargés, et projets anciens
  sans ces clés → None sans erreur). Kanban : Doing → En revue.
