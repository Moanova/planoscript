# TSK28 — Duplication d'un composant (SU003, FN016)

- **Épic** : aucune (SU003, hors EPC05)
- **Statut** : Doing
- **Date de création** : 31-10-2026
- **Dépendances** : aucune (TSK22 Done : rattachement au parcours actif disponible)

## Périmètre (SU003 / FN016)

- Dupliquer un composant State ou Event existant (pas l'agent : les agents
  sont portés par le projet, pas par la carte — SU008 ; la duplication
  d'agent n'est pas dans FN016).
- La copie porte un **nom distinctif** (`{lb} (copy)`, comme TSK24 pour les
  parcours) et un **nouvel identifiant** (RG020).
- La copie hérite des attributs éditables du source : `typ` (State),
  `note`, `content`.
- **Rattachement aux parcours** : la copie est un composant isolé à la
  création (aucun arc) → aucun `Journey_node` (RG024/RG052 révisées :
  le rattachement se fait sur les relations, pas sur les composants).
  Le critère SU003 « rattachée au parcours actif » est satisfait de facto
  via RG024 révisée (conception `journey_attachment.md`) : pas de nœud de
  parcours pour un composant sans relation.
- **Position** : la copie est placée à côté du source (décalage d'une
  cellule de grille, RG044 anti-chevauchement appliqué), alignée sur la
  grille (RG040).
- **Relations** : non copiées (une relation relie deux composants ; la
  dupliquer impliquerait de dupliquer l'autre extrémité — hors périmètre
  FN016).
- Toute duplication marque la carte/projet comme modifié.

## Points d'entrée UI

- Menu contextuel d'un node State/Event (vue Events) : « Duplicate State » /
  « Duplicate Event ».
- Menus `Project > Components... > State/Event` : entrée « Duplicate... »
  active si un node du type est sélectionné (cohérent avec Edit/Delete).

## Implémentation prévue

- Use case `DuplicateComponentUseCase` (src/usecases/view_management/) :
  copie de l'entité métier + création du `NodeLayout` décalé.
- `MainWindow._duplicate_selected_component(type)` + entrées de menu.
- Tests unitaires `tests/test_components/test_component_duplication.py`.

## Journal

- 31-10-2026 : tâche passée en Doing (reprise de la ligne SU003/FN016 du To do).

- 31-10-2026 : travaux de la séance (voir kanban v18 → En revue).
