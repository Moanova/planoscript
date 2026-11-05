# TSK31 — Conception de l'export de la carte narrative (SU007)

- **Épic** : SU007 (export de carte) — tâche de conception
- **Statut** : En revue (01-11-2026) — validation embarquée avec TSK32
- **Date de création** : 01-11-2026
- **Dépendances** : aucune bloquante (TSK22–TSK29 Done : modèle parcours en place, utile pour la vue parcours de l'export)

## Objectif

Rédiger la note de conception de l'export de la carte narrative (SU007),
couvrant :

1. **Périmètre MVP** (SU007 §Périmètre) : export de lecture « par parcours »
   uniquement (dossier autonome HTML lisible dans un navigateur standard,
   sans serveur ni dépendance externe) ; export technique de réimport et
   lecture « par événements » hors périmètre MVP.
2. **Format et structure du dossier d'export** : dossier nommé d'après le
   nom physique de la carte narrative, fichier d'index + pages de
   navigation hypertexte (choix accueil : vue parcours ; page intermédiaire
   listant les parcours ; page de déroulement linéaire par parcours ;
   liens retour sommaire).
3. **Contenu restitué** : libellé en titre de paragraphe + `content` en
   corps de texte (libellé seul si contenu vide) ; ordre de déroulement
   = séquence prédécesseur→successeur du modèle (via les arcs et
   `Journey_node`), indépendant des positions graphiques.
4. **Point d'entrée UI** : menu `Files > Export Map` (actuellement stub
   `lambda: None` dans `main_window.py`) — boîte de dialogue de choix du
   dossier d'export, message de confirmation en barre d'info ; l'export ne
   marque ni la carte ni le projet comme modifiés.
5. **Impacts code prévus** : nouveau service d'export (ex.
   `core/services/export_service.py`) + use case `file_management` ;
   génération HTML autonome (CSS embarqué) ; gabarits de pages ; tests.
6. **Questions ouvertes pour TSC** : nommage du dossier (nom physique de
   la carte), format du fichier d'index (`index.html`), gestion des
   caractères spéciaux dans les noms de fichiers, export de la carte
   courante vs de toutes les cartes du projet (MVP : une seule carte).

## Livrable

- `docs/conception/export.md` (décisions + questions ouvertes pour TSC).
- Mise à jour des specs impactées si décision prise en séance
  (SU007, 03_features, 05_menu, 04_interface — FR/EN).

## Journal

- 01-11-2026 : tâche créée et passée en Doing (décision TSC 01-11-2026, enchaînée après validation de TSK29).
- 01-11-2026 : cadrage en séance — note `docs/conception/export.md` initialisée.
- 01-11-2026 (décisions actées suite) : liens **inertes** dans l'aperçu
  (le filtre FN029 commande le rendu, l'inverse impossible — aperçu
  strictement passif) ; export fichier **indépendant du filtre** ; aperçu =
  carte annotée par parcours, états uniques listés une seule fois (événements
  prédécesseurs + agents associés annotés de leur parcours via Journey_node) ;
  `sequence_order` révisé en tâche dédiée **TSK32** (recalcul par parcours à
  la construction, pas de second champ) ; événements pendants ignorés dans le
  déroulé + convention RG « branche terminée par un état Final » + marqueur en
  fin de déroulé (option b seule, décision TSC 01-11-2026 : aucune
  contrainte de modélisation — aperçus/exports possibles à tout stade ;
  contrôle de cohérence = post-MVP) ; infobulle = clé `note`.
- 01-11-2026 (suite) : retour critique TSC sur la restitution — structure
  centrée sur les états depuis l'état initial (événements prédécesseurs +
  agents associés par état, libellé + content + type + note en infobulle) ;
  sommaire des parcours en liens (1 seul lien si filtre actif) ; section
  agents détaillée ; section orphelins. Points techniques actés : ne pas
  utiliser `sequence_order` (non maintenu, max+1 à la création) mais un
  parcours en profondeur depuis l'état initial ; gérer les cycles longs
  (états déjà visités) ; restituer les composants pendants ; « description »
  = `note` (vocabulaire TSK26). À décider : liens cliquables dans l'aperçu
  readOnly, filtre vs export fichier.
 Décisions actées : troisième espace de travail « Export » en **lecture seule** (aucune interaction, ne touche jamais à `set_modified`) ; **régénération à la bascule sur l'onglet** (pas de temps réel) ; code « 2 espaces de travail » à mettre à jour (`currentTab()` testé à 6 endroits) ; aperçu **dynamique selon le filtre de parcours** (filtre actif → parcours actif, « All journeys » → tous les parcours). Point ouvert principal : contenu de l'aperçu (texte de lecture rendu vs HTML brut — recommandation : texte rendu pour l'aperçu, HTML à la demande via `Files > Export Map`).
- 01-11-2026 (clôture de la conception, kanban v30) : rédaction des spécifications — **SU010** (aperçu d'export) et **FN033** (FR/EN), mises à jour de `04_interface` (onglet « Export », menu View, checklist), `05_menu-EN.yaml` (entrée View › Export), `99_mvp_scope` (ligne Aperçu d'export). Création de **TSK33** (To do, → #TSK32) pour l'implémentation de l'aperçu ; la généralisation du code 2 → 3 espaces de travail y est consignée. TSK31 passe en En revue ; validation embarquée avec TSK32. Points ouverts restants (export.md §5) : format du dossier HTML exporté et dialogue `Files > Export Map` — rattachés à l'implémentation de FN013, hors aperçu in-app.
