# TSK31 — Conception de l'export de la carte narrative (SU007)

- **Épic** : SU007 (export de carte) — tâche de conception
- **Statut** : En cours (Doing, 01-11-2026)
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
