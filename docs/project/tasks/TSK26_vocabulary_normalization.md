# TSK26 — Normalisation du vocabulaire (arc / connection / association / relation)

- **Épic** : transverse (déplacée hors EPC05 à sa clôture, 30-10-2026)
- **Statut** : Doing
- **Date de création** : 30-10-2026 (déplacée du To do le 31-10-2026)
- **Dépendances** : aucune

## Vocabulaire acté (TSC 29-10-2026, `docs/conception/journey_attachment.md` §1)

- **arc** : donnée métier directionnelle (`State_to_event` / `Event_to_state`) — code : `ArcService`.
- **connection** : objet visuel UI (classe `Connection`, `ConnectionLayout`).
- **association** : donnée métier `State_agent_rel`.
- **relation** : terme chapeau réservé aux specs et aux menus (arc ∪ association) ; à ne plus utiliser pour désigner un objet précis dans le code.

## Travaux prévus

1. Audit `arc`/`connection`/`relation` dans tout le code (src/, tests/) et
   correction des usages ambigus (ex. variables/paramètres nommés
   `relation` désignant un arc → `arc` ; un objet visuel → `connection`).
2. Inverser l'ordre des clés `state_to_event_id` / `event_to_state_id` dans
   `Journey_node` (`src/core/models/data_model.py`) : `state_to_event_id`
   en premier (une carte commence toujours par l'état initial).
   - `to_dict()` utilise `asdict` (ordre des champs du dataclass) → l'ordre
     JSON suit automatiquement.
   - Mettre à jour `docs/specification/07_data_model-*.json` en cohérence.
3. Autres points ambigus relevés au fil de l'audit.

## Hors périmètre

- Pas de renommage de classes/fichiers (diff minimal) ; seulement
  l'ordre des champs et le vocabulaire des variables/paramètres/docstrings
  quand ils contredisent la distinction actée.

## Journal

- 30-10-2026 : tâche créée à la clôture d'EPC05.
- 31-10-2026 : passée en Doing.

- 31-10-2026 : travaux de la séance (voir kanban v18 → En revue).
