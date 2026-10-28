# TSK17 — Ajustement esthétique : badge d'agents dans le coin bas-droit (2/3 dedans, 1/3 dehors)

- **Épic** : Ajustements esthétiques post-revue TSC (cohérence avec le repositionnement des badges d'évènement, TSK13)
- **Statut** : En revue (implémentation + retour de revue TSC traité — ratio 2/3 dedans / 1/3 dehors — attente validation TSC)
- **Date de début** : 28-10-2026
- **Dépendances** : #TSK05 (Done), #TSK13 (En revue)

## Périmètre

Placer le badge d'agents des nœuds d'état de la vue Journey dans le
**coin bas-droit du contour** du nœud, **2/3 dedans et 1/3 dehors**
(retour de revue TSC 28-10-2026 : la partie extérieure ne doit pas paraître
trop importante). Valeurs réelles : diamètre 16 px, partie dehors = 5 px
(1/3 arrondi à l'entier), donc 11 px dedans. Évolution du placement initial
(centré à cheval sur le coin, 8 px dehors) et de la version d'origine
(marge de 3 px à l'intérieur, TSK05). Même principe que le repositionnement
des badges d'évènement de la vue Agents (TSK13, validé TSC le 28-10-2026).

## Implémentation

- `src/ui/nodes/state_node.py` :
  - `_position_agent_badge()` : `outside = round(diameter / 3)` (= 5 px),
    `x = rect.width() - diameter + outside`,
    `y = rect.height() - diameter + outside` (au lieu de
    `- BADGE_MARGIN`, puis du centrage à cheval `w - d/2` de la
    première version TSK17).
  - Constante `BADGE_MARGIN = 3.0` supprimée (plus utilisée).
  - Docstring de classe et de méthode mises à jour (TSK17, TSC 28-10-2026).
- Tests : `tests/test_agents/offscreen_state_badges.py` — assertions de
  position mises à jour.

## Vérifications

- Pas de conflit avec les ports de connexion Journey (milieu des bords G/D,
  pas dans les coins).
- La scène Journey est extensible à l'infini : le débordement de 5 px reste
  dans l'espace libre autour du nœud.

## Journal

- 28-10-2026 : implémentation + tests (106 passed pytest, 10 offscreen
  PASSED) + doc (`98_layout_revision-FR.md`, `04_interface` FR/EN,
  kanban TSK16 — la marge du badge n'existe plus) + SESSIONS.md.
  Kanban : Doing → En revue (attente validation TSC).
- 28-10-2026 (retour de revue TSC) : ajustement du ratio — le badge est
  désormais **2/3 dedans, 1/3 dehors** du contour (partie dehors = 5 px
  sur un diamètre de 16, 1/3 arrondi à l'entier) au lieu d'être centré à
  cheval sur le coin. Tests mis à jour, doc mise à jour. Kanban : En
  revue (attente validation TSC).
