# TSK16 — Paramétrer dans config.json les dimensions de la vue Events

- **Épic** : aucune (hygiène technique)
- **Statut** : Doing
- **Date de création** : 31-10-2026
- **Dépendances** : aucune

## Périmètre

Sortir de constantes de classe les dimensions de la vue Events et les
paramétrer dans `src/config/config.json` (règle AGENTS.md : aucune valeur
codée en dur pour l'UI) :

| Constante actuelle | Fichier | Clé config.json proposée |
|---|---|---|
| `BaseNode.PORT_SIZE = 8` (taille des ports) | `src/ui/nodes/base_node.py` | `events_view_port_size_px` |
| `BaseNode.PORT_MARGIN = 4` (marge des ports) | `src/ui/nodes/base_node.py` | `events_view_port_margin_px` |
| `StateNode.BADGE_DIAMETER = 16.0` | `src/ui/nodes/state_node.py` | `events_view_badge_diameter_px` |
| `Connection.HIT_AREA_WIDTH = 12.0` | `src/ui/nodes/connection.py` | `events_view_hit_area_width_px` |

Notes :
- `PORT_MARGIN` est déclaré mais jamais utilisé dans le code actuel :
  il est quand même sorti en config (la constante de classe disparaît,
  la clé documente la marge prévue).
- `MatrixCard.EVENT_BADGE_DIAMETER = 16.0` (vue Agents) est hors périmètre
  de la tâche (vue Events uniquement) — laissé en constante de classe.
- Valeurs par défaut identiques aux constantes actuelles (8 / 4 / 16.0 /
  12.0) pour un comportement inchangé si la clé est absente.

## Journal

- 31-10-2026 : tâche passée en Doing.

- 31-10-2026 : travaux de la séance (voir kanban v18 → En revue).
