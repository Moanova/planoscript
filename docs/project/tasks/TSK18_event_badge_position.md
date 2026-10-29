# TSK18 — Ajustement esthétique : badges d'évènement de la vue Agents, 2/3 dedans / 1/3 dehors sur l'axe horizontal

- **Épic** : Ajustements esthétiques post-revue TSC (cohérence avec TSK17)
- **Statut** : En revue (implémentation + tests faits — attente validation TSC)
- **Date de début** : 29-10-2026
- **Dépendances** : #TSK13 (Done)

## Périmètre

Modifier uniquement le **positionnement horizontal** des deux badges
d'évènement des cartes d'état de la vue Agents (matrice) : le badge de
gauche (évènements sources) est légèrement décalé vers la **droite**, le
badge de droite (évènements cibles) vers la **gauche**, pour que la
partie extérieure au contour de la carte soit moins importante que la
partie intérieure — **2/3 dedans, 1/3 dehors** au lieu du 1/2–1/2
actuel (centrage à cheval sur le bord). Valeurs réelles : diamètre 16 px,
partie dehors = 5 px (1/3 arrondi à l'entier), donc 11 px dedans.
L'axe vertical reste inchangé (centrage vertical). Même principe que
l'axe horizontal du badge d'agents des nœuds d'état de la vue Journey
(TSK17, TSC 28-10-2026).

## Implémentation

- `src/ui/nodes/matrix_card.py` :
  - `_position_event_badges()` : `outside = round(diameter / 3)` (= 5 px),
    badge gauche `setPos(-outside, y)`, badge droit
    `setPos(rect.width() - diameter + outside, y)` (au lieu de `-d/2` et
    `w - d/2`). Axe vertical inchangé : `y = h/2 - d/2`.
  - Docstrings/commentaires mis à jour (TSK18).
- Tests : `tests/test_agents/offscreen_tsk13_agent_mechanics.py` —
  assertions de position X mises à jour (centres à 3 px et w-3 px du
  bord dans le repère local, axe Y inchangé).
- Doc : `docs/specification/04_interface-FR.md` / `-EN.md` (section 6.bis),
  `docs/specification/98_layout_revision-FR.md` (ligne badges d'évènement).

## Vérifications

- `python -m py_compile` sur les fichiers modifiés.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
- Test offscreen ciblé : `QT_QPA_PLATFORM=offscreen python
  tests/test_agents/offscreen_tsk13_agent_mechanics.py`.

## Journal

- 29-10-2026 : création de la tâche (demande TSC 29-10-2026) — ratio
  2/3 dedans / 1/3 dehors sur l'axe horizontal uniquement.
- 29-10-2026 : implémentation (`matrix_card.py` : `outside =
  round(diameter/3)` = 5 px, badge gauche `x = -outside`, badge droit
  `x = w - d + outside`, axe Y inchangé) + test offscreen TSK13 mis à
  jour + doc (04_interface FR/EN, charte 98). Vérifications : py_compile
  OK, pytest 106 passed, 10 offscreen PASSED (dont TSK13 avec les
  nouvelles assertions de position), test jetable de rendu QImage :
  géométrie -5 / w-16+5 et mesure pixel ~5 px dehors / ~11 px dedans,
  confirmé visuellement sur le rendu. Kanban : Doing → En revue.
