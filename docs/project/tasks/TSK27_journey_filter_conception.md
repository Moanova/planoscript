# TSK27 — Conception du filtre d'affichage par parcours (FN029, RG042, SU006)

- **Épic** : EPC05 (SU005/SU006, gestion des parcours) — tâche de conception
- **Statut** : Doing
- **Date de création** : 31-10-2026
- **Dépendances** : TSK22–TSK25 Done (fondations parcours en place)

## Objectif

Rédiger la note de conception `docs/conception/journey_filter.md` couvrant
le filtre d'affichage par parcours (FN029, RG042, SU006) :

1. **État du filtre** : bascule « tous les parcours » / « parcours actif » ;
   valeur par défaut à l'ouverture ; **persistance** (RG041 : le zoom et la
   position des scrollbars ne sont pas persistés — décider si l'état du
   filtre l'est ou non, et où : `user_state.json` vs métadonnées graphiques
   vs rien).
2. **Sémantique de visibilité** (RG026, FN029) :
   - filtre actif → seules les relations (arcs + associations) rattachées
     au parcours actif sont visibles, plus les composants auxquels elles
     donnent appartenance ;
   - composants orphelins (sans aucune relation) et relations des autres
     parcours → visibles uniquement filtre désactivé ;
   - conséquences sur la vue Agents (matrice : filtrer les colonnes/états
     et les associations affichés, ou garder la matrice complète ?).
3. **Interaction avec l'édition** : création d'un composant/relation sous
   filtre actif (rattachement auto au parcours actif, RG052) ; suppression
   sous filtre ; navigation croisée (RG067) sous filtre.
4. **UI** : point d'entrée (menu Display > Journey, liste JourneyList
   existante TSK23 — case « All journeys » ?) ; rafraîchissement de la vue
   (quels items Qt masquer : `setVisible(False)` sur nodes/connections).
5. **Impacts** : modèle (aucun champ ajouté, RG034), view_model
   (état du filtre dans WorkspaceLayout ou user_state ?), use cases
   (aucun — purement visuel), tests prévus.

## Livrable

- `docs/conception/journey_filter.md` (décisions + questions ouvertes pour TSC).
- Mise à jour des specs impactées (FN029 état « Conçu », 05_menu si entrée
  ajoutée) — FR/EN.

## Journal

- 31-10-2026 : tâche créée et passée en Doing (séance du 31-10).

- 31-10-2026 : travaux de la séance (voir kanban v18 → En revue).
