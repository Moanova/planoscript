# Planoscript ::: Périmètre MVP
- **Version** : 0.1.0-alpha
- **Statut** : À valider
- **Date** : 2026-08-26

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
| Projet          | Créer, ouvrir, enregistrer, enregistrer sous, fermer un projet         | SU001 |
| Carte narrative | Une carte narrative unique par projet                                  | SU002 |
| Composants      | Créer, déplacer, sélectionner et afficher les cinq types de composants | SU003 |
| Relations       | Créer et afficher les relations initialement supportées                | SU004 |
| Visualisation   | Vue Parcours, grille, déplacement, défilement                          | SU006 |
| Persistance     | Sauvegarde locale des données et de la mise en page                    | RG003 |
| Export          | Export local pour lecture dans un navigateur                           | SU007 |

## 4. Exclus du MVP
| Domaine           | Fonctionnalités exclues                               | Motif / condition de réintégration                                    |
|---|---|---|
| Cartes            | Importer, exporter, dupliquer ou supprimer une carte  | À prioriser après validation de la carte principale                   |
| Qualité narrative | Détection d’impasses, incohérences ou contradictions  | Dépend de règles métier plus détaillées                               |
| Historique        | Annuler/rétablir et historique des modifications      | À ajouter après stabilisation des opérations d’édition                |

## 5. Décisions de périmètre
- Un seul projet peut être ouvert à la fois.
- Un projet contient une et une seule carte narrative.
- Les barres latérales d'outils ne seront pas implémentées.
- Le zoom de la visualisation de la carte n'est pas disponible.
- Les données narratives et les informations de mise en page doivent pouvoir être restaurées après fermeture et réouverture du projet.
- La vue alternative des relations entre agents ne s'est pas disponible ; ele sera implémentée dans une version ultérieure.
- L'export technique pour réimport dans un autre projet n'est pas disponible.
- La lecture par événements de l'export n'est pas disponible ; elle sera implémentée dans une version ultérieure.
- La cohérence de parcours n'est pas analysée : les enchaînements brisés ne seront donc pas détectés.
	
## 6. Critères de sortie du MVP
Le MVP est considéré comme prêt à être testé lorsque l’utilisateur peut :
1. créer un projet ;
2. créer un parcours complet ;
3. créer des parcours alternatifs ;
4. enregistrer puis rouvrir le projet ;
5. retrouver le projet dans l'état dans lequel il a été sauvegardé pour ce qui est de la représentation graphique de la carte narrative ;
6. fermer l’application sans perdre involontairement un travail modifié ;
7. exporter la carte narrative du projet.

## 8. Évolutions prévues après le MVP
- Gestion de multiples cartes narratives dans un même projet.
- Validation de cohérence narrative.
- Lecture par évènement de l'export.
- Export technique des cartes narratives pour réimport dans d'autres projets.
- Annuler/rétablir.
