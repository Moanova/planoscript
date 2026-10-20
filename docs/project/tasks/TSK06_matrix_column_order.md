# TSK06 — Règle de gestion de l'ordre des colonnes de la matrice

- **Épic** : EPC03 — Implémenter la vue agents (SU009)
- **Statut** : Done (conception consignée, en attente du commit)
- **Date de début** : 15-10-2026
- **Dépendances** : aucune

## Périmètre

Tâche de conception : déterminer et consigner la règle de gestion de
l'ordre des colonnes de la matrice agents × états, avant
l'implémentation de la vue agents (TSK08). Aucune implémentation de code
dans cette tâche.

## Analyse des options

1. **Ordre de création** (id croissant) : stable, complet, trivial.
2. **Ordre du parcours activé** (séquence RG033) : narrativement
   pertinent mais inadapté au MVP (RG052 : états isolés sans position ;
   pas de filtre de parcours actif ; enchaînements brisés non analysés).
3. **Ordre alphabétique du libellé** : instable au renommage (RG021 :
   libellés non uniques).
4. **Ordre manuel persisté** : contrôle total, mais jamais spécifié.
5. Hybride parcours/création : branche parcours = code mort en MVP.

## Décision (validée par l'utilisateur)

Combinaison des options 1 et 4 :
- **Par défaut** : ordre de création des états (id croissant).
- **Réordonnancement manuel** autorisé, **rémanent** : l'ordre
  personnalisé est conservé dans les **métadonnées graphiques** (fichier
  de mise en page) associées au projet, entre les sessions — ce n'est
  pas une donnée narrative, sa modification ne marque pas la carte
  comme modifiée.
- **État initial toujours en première colonne et non déplaçable**
  (cohérent avec RG031 : tous les parcours commencent à cet état).
- **Nouvel état créé** : apparaît en fin d'ordre.
- **Repli** : en cas d'anomalie dans l'ordre sauvegardé (état absent ou
  inconnu), retour à l'ordre de création.
- **Lignes (agents)** : même règle (ordre de création par défaut,
  réordonnancement manuel rémanent autorisé).
- **États finaux / filtre de parcours** : ignorés en MVP (pas de filtre
  actif ; toute règle anticipée serait spéculative). La question sera
  reprise si FN029 (filtrage par parcours) est implémenté.

## Livrables

- **RG068** ajoutée dans `docs/specification/02_business_rules-FR.md`
  et `02_business_rules-EN.md` (classification : Visualisation et
  interaction).
- **SU009** mis à jour dans `01_user_stories-FR.md` et
  `01_user_stories-EN.md` : complément et critère d'acceptation
  référencent désormais RG068 (plus de « règle à déterminer »).

## Impact sur les tâches suivantes

- **TSK08** (affichage matrice) : applique l'ordre via la liste
  sauvegardée + tri de repli ; état initial non déplaçable ;
  glisser-déposer de colonnes (interaction Qt) ; persistance dans le
  `WorkspaceLayout` (fichier de mise en page).
- **TSK09** (édition) : sans changement lié à l'ordre.
- Le stockage concret (champ `column_order` du `WorkspaceLayout`,
  listes d'IDs) sera conçu dans le plan de TSK08.

## Vérifications attendues

1. Cohérence RG068 ↔ SU009 FR/EN (relue après écriture).
2. Pas de code modifié : pas de tests à exécuter.

## Journal des travaux

- 15-10-2026 : analyse des 5 options, discussion avec l'utilisateur,
  décision validée (combinaison création par défaut + réordonnancement
  manuel rémanent + état initial épinglé), RG068 rédigée en FR/EN,
  SU009 mis à jour en FR/EN.
