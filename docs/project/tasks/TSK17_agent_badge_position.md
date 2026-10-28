# TSK17 — Ajustement esthétique : badge d'agents centré sur le coin bas-droit

- **Épic** : Ajustements esthétiques post-revue TSC (cohérence avec le repositionnement des badges d'évènement, TSK13)
- **Statut** : En revue (implémentation + tests terminés, attente validation TSC)
- **Date de début** : 28-10-2026
- **Dépendances** : #TSK05 (Done), #TSK13 (En revue)

## Périmètre

Décaler le badge d'agents des nœuds d'état de la vue Journey pour qu'il soit
**centré sur le coin bas-droit du contour** du nœud — à cheval sur les axes X
et Y (débordement de 8 px vers la droite et vers le bas, diamètre 16) — au
lieu d'être à l'intérieur du coin avec une marge de 3 px. Même principe que le
repositionnement des badges d'évènement de la vue Agents (TSK13, validé TSC
le 28-10-2026).

## Implémentation

- `src/ui/nodes/state_node.py` :
  - `_position_agent_badge()` : `x = rect.width() - diameter / 2`,
    `y = rect.height() - diameter / 2` (au lieu de `- BADGE_MARGIN`).
  - Constante `BADGE_MARGIN = 3.0` supprimée (plus utilisée).
  - Docstring de classe et de méthode mises à jour (TSK17, TSC 28-10-2026).
- Tests : `tests/test_agents/offscreen_state_badges.py` — assertions de
  position mises à jour.

## Vérifications

- Pas de conflit avec les ports de connexion Journey (milieu des bords G/D,
  pas dans les coins).
- La scène Journey est extensible à l'infini : le débordement de 8 px reste
  dans l'espace libre autour du nœud.

## Journal

- 28-10-2026 : implémentation + tests (106 passed pytest, 10 offscreen
  PASSED) + doc (`98_layout_revision-FR.md`, `04_interface` FR/EN,
  kanban TSK16 — la marge du badge n'existe plus) + SESSIONS.md.
  Kanban : Doing → En revue (attente validation TSC).
