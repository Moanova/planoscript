# Conception — Export de la carte narrative et aperçu d'export (SU007, TSK31)

- **Date** : 01-11-2026
- **Statut** : en cours de rédaction (TSK31, Doing) — décisions actées en §2, points ouverts en §4
- **Contexte** : SU007 (export d'une carte narrative en document autonome lisible
  dans un navigateur standard) ; fondations parcours en place (TSK22–TSK29 :
  `Journey_node`, filtre d'affichage FN029) ; menu `Files > Export Map`
  actuellement stub (`lambda: None` dans `main_window.py`)

## 1. Rappel du besoin (SU007)

- Export de lecture : dossier autonome (index + pages hypertexte), sans
  serveur ni dépendance externe, affiché dans Chrome/Firefox/Edge hors
  connexion.
- Deux modes de lecture prévus par SU007 : **vue parcours** (MVP) et **vue
  événements** (hors MVP).
- Contenu restitué par composant : libellé en titre + `content` en corps de
  texte (libellé seul si contenu vide) ; ordre = séquence
  prédécesseur→successeur du modèle (arcs + `Journey_node`), indépendant
  des positions graphiques.
- Export technique pour réimport : **hors périmètre MVP**.
- L'export ne marque ni la carte ni le projet comme modifiés.

## 2. Décisions actées (TSC, 01-11-2026)

1. **Aperçu d'export dans un troisième espace de travail** dédié (terme
   « espace de travail » acté même si impropre stricto sensu) : onglet
   « Export » à côté de « Events » et « Agents ».
2. **Lecture seule, aucune interaction** : le contenu n'est jamais édité
   dans l'app ; en conséquence la génération de l'aperçu **ne modifie
   jamais** `set_modified` (ni la carte ni le projet).
3. **Régénération à la bascule sur l'onglet Export** (et non à chaque
   modification du modèle) : le texte est regénéré quand l'utilisateur
   active l'onglet (et après un changement si l'onglet est déjà actif, via
   le signal métier de modification). Cela évite toute régénération
   coûteuse/inutile en arrière-plan et les problèmes de scroll/s cintillement.
4. **Mise à jour du code « deux espaces de travail »** : `tab_bar.currentTab()`
   est testé à plusieurs endroits (`== "Agents"`) pour le comportement des
   menus Agent, `_release_focus`, `_update_menu_state`, la création
   d'événement depuis la vue Agents, etc. Tout ce code doit passer à une
   logique explicite (ex. `currentTab() == "Agents"` reste correct, mais
   les branches « Events » implicites deviennent « tout sauf Agents » ou
   inversement) — à consigner et traiter à l'implémentation.
5. **L'aperçu est dynamique selon le filtre de parcours (FN029/TSK29)** :
   - filtre actif → aperçu du **parcours actif** ;
   - filtre désactivé (« All journeys ») → aperçu de **tous les parcours**
     (sommaire de tous les parcours, ou texte complet de la carte).

## 3. Architecture prévue (à affiner)

- Service d'export dédié (ex. `core/services/export_service.py`) :
  - `build_reading_text(narrative_map, journey=None)` → texte de lecture
    (libellé + content déroulés dans l'ordre prédécesseur→successeur ;
    `journey=None` = tous les parcours) ;
  - `export_map_html(project, narrative_map, dest_dir)` → dossier HTML
    autonome (pour `Files > Export Map`, hors aperçu).
- Use case `file_management` (ex. `ExportMapUseCase`) : génère le dossier,
  ne marque pas modifié.
- UI : `ExportWorkspace` (QWidget + QTextEdit readOnly) dans
  `src/ui/views/`, troisième page du `QStackedWidget` + onglet « Export » ;
  régénération déclenchée par `_on_tab_changed("Export")` et par le
  signal de modification si l'onglet est actif.

## 4. Points ouverts (à décider en séance TSK31)

1. **Contenu de l'aperçu** (point principal) : texte de lecture rendu
   (libellé + content, format lisible) **vs** HTML brut généré. Recommandation :
   texte de lecture rendu pour l'aperçu ; le HTML reste produit à la demande
   par `Files > Export Map`.
2. **Format de l'export de lecture** : HTML autonome statique (index.html +
   pages) conforme à SU007 — gabarits, CSS embarqué, encodage UTF-8,
   nommage du dossier (nom physique de la carte narrative, caractères
   spéciaux à traiter).
3. **Déroulement « par parcours »** : ordre des composants via les arcs et
   `Journey_node` (`sequence_order`) — comment ordonner quand un composant
   appartient à plusieurs parcours, et que faire des composants orphelins
   (hors tout parcours) dans l'export.
4. **Point d'entrée UI de l'export** : `Files > Export Map` (stub actuel) —
   boîte de dialogue de choix du dossier de destination + confirmation.
5. **Agents dans l'export** : SU007 parle de composants état/événement ;
   les associations agent-état et les agents (niveau projet) sont-ils
   restitués dans l'export de lecture ? (SU007 mentionne une lecture par
   relations d'agents en version ultérieure — hors MVP.)

## 5. Hors périmètre (acté)

- Export technique pour réimport (hors MVP, kanban « SU007 — Export
  technique pour réimport → hors périmètre »).
- Vue événements de l'export (version ultérieure).
- Lecture par relations d'agents (version ultérieure).
