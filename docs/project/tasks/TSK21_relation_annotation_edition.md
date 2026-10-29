# TSK21 — Édition des annotations (`note`) des 3 types de relations (FN021, SU004)

- **Épic** : Évolution du modèle de données / édition des relations
- **Statut** : To do (implémentation prévue lors d'une séance ultérieure ;
  la solution ci-dessous a été proposée et **validée par TSC le
  29-10-2026**)
- **Date de création** : 29-10-2026
- **Dépendances** : #TSK20 (clé `note` doit exister sur Event_to_state /
  State_to_event dans le modèle de données)

## Périmètre

Permettre de saisir/modifier l'annotation (`note`) des trois types de
relations :
- `Event_to_state` et `State_to_event` (arcs de la vue Events) ;
- `State_agent_rel` (associations agent-état, cases de la matrice de la
  vue Agents — la création/suppression reste gérée par les cases à
  cocher).

FN021 prévoit déjà l'édition des arcs via le panneau de propriétés
(menu « Project › Relations... › Edit ») ; rien n'existait pour
`State_agent_rel`.

## Solution validée (TSC 29-10-2026)

### A. Arcs Event_to_state / State_to_event (vue Events)

1. **Sélection de la connexion** (`Connection`) dans la vue Events, puis
   **clic droit → menu contextuel « Annoter la relation... »** — pattern
   établi `menu.exec()` + dispatch sur l'action retournée (AGENTS.md) ;
   entrée désactivée quand aucune connexion n'est sélectionnée. Le menu
   « Project › Relations... › Edit » (panneau de propriétés, FN021) reste
   le second point d'entrée prévu par la spec.
2. **Dialogue d'annotation** : `QDialog` avec un `QTextEdit` « Note »
   pré-rempli avec `relation.note`, boutons OK/Annuler (mêmes codes
   visuels que les autres dialogues, charte 98).
3. **Use case** `UpdateRelationUseCase.execute(relation, note=...)` :
   met à jour `relation.note` (chaîne vide → None),
   `modification_date_time`, appelle `project_service.set_modified(True)`.
4. **Infobulle** : la note s'affiche dans le tooltip de la connexion
   (au survol), comme le libellé aujourd'hui (FN021).

### B. State_agent_rel (vue Agents, matrice)

Le blocage : la case à cocher ne fait que créer/supprimer la relation,
il n'y a pas de « ligne de relation » sélectionnable. Solution retenue :

1. **Clic droit sur une case cochée** de la matrice → menu contextuel
   « Annoter l'association... » (entrée **désactivée si la case est
   décochée** — pas de relation à annoter). Réutilise le pattern « clic
   droit sélectionne avant d'ouvrir le menu » déjà en place sur les
   cartes. Alternative envisagée et écartée : double-clic sur la case
   (risque de conflit avec le simple clic qui bascule l'association).
2. **Même dialogue d'annotation** que A (composant réutilisable).
3. **Use case** `UpdateAgentStateAssociationUseCase.execute(relation,
   note=...)`, même contrat que A (note, modification_date_time,
   set_modified).
4. **La création par case à cocher reste inchangée** : la relation est
   créée avec `note` vide ; l'annotation est une édition a posteriori.
   La dissociation (décochage) supprime la relation et donc sa note
   (cascade RG063/RG065 inchangée).

### C. Unification

Même composant de dialogue et même pattern de use case pour les 3 types
de relation ; les identifiants de relation viennent de
`narrative_map.get_next_id(...)` côté création (inchangé).

## Impacts prévus

- `src/core/models/data_model.py` : rien (dépend de TSK20 pour les arcs).
- `src/ui/views/events_workspace.py` : menu contextuel sur `Connection`.
- `src/ui/views/agents_workspace.py` : menu contextuel sur `MatrixCheckItem`
  (case cochée uniquement).
- Nouveau dialogue `src/ui/dialogs/relation_dialog.py` + 2 use cases
  (`view_management/update_relation_usecase.py`,
  `agent_association/update_agent_state_association_usecase.py`).
- `src/ui/nodes/connection.py` : tooltip avec la note.
- Tests unitaires (use cases) + offscreen (menus contextuels des deux vues).

## Documentation

- `03_features-FR/EN.md` : FN021 passe de « Non implémenté » à
  « Implémenté » (3 types de relations) ;
- `04_interface-FR/EN.md` : menus contextuels (connexion vue Events, case
  cochée vue Agents), dialogue d'annotation, infobulle ;
- `01_user_stories-FR/EN.md` : SU004 ;
- `05_menu-*.yaml` si le menu « Relations... › Edit » évolue ;
- kanban, `SESSIONS.md`.

## Vérifications (à la mise en Doing)

1. `python -m py_compile` sur les fichiers modifiés.
2. `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Scripts offscreen : menu contextuel connexion (vue Events) et case
   cochée (vue Agents), saisie d'une note, persistance JSON
   (clé `note` sur les 3 types), rechargement.

## Journal

- 29-10-2026 : création de la tâche ; solution d'UI pour State_agent_rel
  (clic droit sur case cochée) proposée et validée TSC. Implémentation
  prévue en séance ultérieure.
