# TSK14 — Barre latérale gauche de contrôle

- **Épic** : aucune (évolution structurelle de l'interface)
- **Statut** : To do
- **Date de création** : 24-10-2026
- **Dépendances** : #TSK11 (Done — le thème sombre est le cadre visuel de référence)

## Périmètre

Ajout d'une **barre latérale gauche** dans la fenêtre principale, dédiée
au contrôle : création des **agents**, des **états**, des **événements** et
des **relations**.

La charte 98 (section 4, point 11 ; section 7) acte ce principe : « Une
barre latérale gauche pourra être ajoutée plus tard ». Le panneau central
s'étendra sur la largeur restante entre la barre latérale gauche et le bord
de la fenêtre (la barre latérale droite « Journey Filter » reste un chantier
séparé, hors périmètre de cette tâche).

## Éléments à préciser avant passage en Doing

- Largeur du panneau et codes visuels (la charte 98 prévoit surface
  `#2D2D2D`, séparateurs `#383838` — à confirmer).
- Forme des contrôles : boutons, liste d'outils, palette d'outils ?
- Comportement de création d'une relation (mode rubber band existant dans
  `JourneyWorkspace`) : la barre déclenche-t-elle le mode, ou se contente-t-elle
  de créer les composants ?
- Présence/absence du panneau selon les espaces de travail (Journey /
  Agents) — même question que pour le futur Journey Filter.
- Interactions avec les raccourcis clavier et les menus existants (pas de
  doublon de fonctionnalité).

## Contexte (existant mobilisable)

- Création d'état/événement : menu contextuel du canvas
  (`JourneyWorkspace.show_context_menu`) et menu Files/Edit.
- Création d'agent : `Project > Manage agents` + création intégrée au
  dialogue d'association (TSK04).
- Création de relation : mode rubber band dans `JourneyWorkspace`
  (SU004, RG054/RG058).
- Association agent-état : dialogue TSK04, matrice TSK09.
- Architecture : UI → use cases → services → models (AGENTS.md) ; signaux
  plutôt qu'appels de méthodes privées entre composants.

## Journal

- 24-10-2026 : tâche créée à la demande de TSC, en attente de cadrage
  (prochaine séance).
