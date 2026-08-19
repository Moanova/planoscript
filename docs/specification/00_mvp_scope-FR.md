# Planoscript ::: Périmètre MVP
- **Version** : 0.1.0-alpha
- **Statut** : À valider
- **Date** : 2026-08-19

## 1. Objectif du MVP
Permettre à un auteur de créer et de sauvegarder localement un projet constitué d'une carte narrative composée de composants et de relations simples et de l'exporter de façon lisible.
Le MVP doit permettre de vérifier que la représentation graphique apporte une valeur réelle à la structuration d’un récit et que l'export est compréhensible.

## 2. Public cible
- Scénariste indépendant.
- Utilisateur non technique.
- Usage individuel, sur poste local.

## 3. Inclus dans le MVP
| Domaine         | Fonctionnalités incluses                                               | Références |
|---|---|---|
| Projet          | Créer, ouvrir, enregistrer, enregistrer sous, fermer un projet         | SU001, FN005 à FN010 |
| Carte narrative | Une carte narrative unique par projet                                  | SU002 |
| Composants      | Créer, déplacer, sélectionner et afficher les cinq types de composants | SU003 |
| Relations       | Créer et afficher les relations initialement supportées                | SU004 |
| Visualisation   | Vue Parcours, grille, déplacement, défilement                          | SU006 |
| Persistance     | Sauvegarde locale des données et de la mise en page                    | RG003, RG004, RG016 |
| Export          | Export local pour lecture dans un navigateur                           | SU007 |

## 4. Exclus du MVP
| Domaine           | Fonctionnalités exclues                               | Motif / condition de réintégration                                    |
|---|---|---|
| Administration    | Supprimer un projet et son arborescence de fichiers   | À prévoir lorsque le format de stockage multi-fichiers sera stabilisé |
| Cartes            | Importer, exporter, dupliquer ou supprimer une carte  | À prioriser après validation de la carte principale                   |
| Parcours          | Gestion complète de plusieurs parcours                | Dépend de la clarification du modèle d’appartenance                   |
| Chapitres         | Vue et gestion des chapitres                          | Dépend de la définition métier des chapitres                          |
| Collaboration     | Édition simultanée, partage en ligne, gestion d’accès | Hors périmètre local du MVP                                           |
| Qualité narrative | Détection d’impasses, incohérences ou contradictions  | Dépend de règles métier plus détaillées                               |
| Historique        | Annuler/rétablir et historique des modifications      | À ajouter après stabilisation des opérations d’édition                |

## 5. Décisions de périmètre
- Un seul projet peut être ouvert à la fois.
- Un nouveau projet contient une carte narrative principale.
- Le projet peut être stocké dans une arborescence de fichiers, mais sa structure exacte sera définie avant l’implémentation de FN011.
- La suppression de projet est conservée dans les spécifications, mais explicitement exclue du MVP.
- Les données narratives et les informations de mise en page doivent pouvoir être restaurées après fermeture et réouverture du projet.

## 6. Critères de sortie du MVP
Le MVP est considéré comme prêt à être testé lorsque l’utilisateur peut :
1. créer un projet ;
2. ajouter les cinq types de composants ;
3. déplacer les composants sur la carte ;
4. créer les relations supportées ;
5. enregistrer puis rouvrir le projet ;
6. retrouver les composants, relations et positions précédemment sauvegardés ;
7. fermer l’application sans perdre involontairement un travail modifié ;
8. exporter la carte narrative principale du projet.

## 7. Questions ouvertes
- Quel est le format final de stockage : fichier unique, dossier projet ou bundle ?
- Quelles relations doivent être incluses dès le MVP ?
- Un parcours par défaut suffit-il pour le premier test utilisateur ?
- Le zoom et la position de la vue doivent-ils être persistés ?
- Quels scénarios des cas de test doivent être réalisables dès le MVP ?

## 8. Évolutions prévues après le MVP
- Gestion complète des parcours et chapitres.
- Suppression administrative de projet et de ses fichiers associés.
- Validation de cohérence narrative.
- Annuler/rétablir.
