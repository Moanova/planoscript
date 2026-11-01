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

## 4. Restitution de l'aperçu (propositions TSC 01-11-2026, à valider)

Structure centrée sur les **états**, en partant de l'état initial (unique,
RG031) :

1. **Sommaire des parcours** : tous les parcours accessibles depuis l'état
   initial, chacun par lien hypertexte. Filtre FN029 actif → un seul lien
   (le parcours actif) ; filtre désactivé → tous les parcours.
2. **Déroulé d'un parcours** : états présentés dans leur ordre de succession.
   Pour chaque état (sauf l'initial) : le ou les **événements prédécesseurs**
   listés, ainsi que le ou les **agents associés**. Pour chaque composant :
   libellé + `content` en corps de texte, **type** (état : Initial/Action/
   Relation/Final ; agent : Sujet/Objet), et **`note` en infobulle au survol**
   (le modèle n'a pas de « description » — TSK26 a acté note/content ; dans
   l'aperçu QTextEdit readOnly, infobulle via mécanisme custom `anchorAt` +
   QToolTip ; dans l'export HTML, attribut `title` natif).
3. **Section agents** (niveau projet) : listée avant ou après le déroulé des
   parcours ; dans le déroulé, seuls les **libellés** des agents apparaissent,
   avec lien hypertexte vers leur description détaillée dans cette section.
4. **Section composants orphelins** (après parcours et agents) : listés
   explicitement.

### Décisions actées (TSC 01-11-2026, suite)

- **Ordre de succession** : la sémantique de `Journey_node.sequence_order`
  est révisée — ordre **réel** de succession, recalculé **par parcours** à
  la construction/modification de la carte (pas à la génération de
  l'export). Tâche dédiée **TSK32** (à traiter avant l'implémentation de
  l'aperçu d'export) : recalcul par parcours en profondeur depuis l'état
  initial, restreint aux arcs rattachés au parcours, aux points
  `ArcService.create_arc` / `delete_related_arcs` / attach-detach RG027 /
  cascades. **Pas de second champ** : la clé JSON `sequence_order` est
  conservée, seule sa sémantique change (les anciennes valeurs sont
  recalculées au chargement).
- **Rendu de l'aperçu** : QTextEdit/QTextBrowser render un sous-ensemble
  HTML 4 (titres, gras, paragraphes, ancres, listes) → l'aperçu est un
  rendu HTML léger, pas du texte brut. Infobulle sur les ancres : mécanisme
  custom (`anchorAt` + `QToolTip.showText`, pattern des nœuds du workspace).
- **Liens inertes (acté)** : le filtre FN029 commande le rendu de l'aperçu ;
  aucun clic dans l'aperçu ne modifie le filtre ni ne régénère rien —
  l'aperçu est strictement passif (lecture seule).
- **Export fichier vs aperçu** : l'export sur le système de fichiers est
  **indépendant du filtre** (carte complète, RG041) ; l'aperçu in-app
  reflète le filtre actif.
- **Restitution centrée états, carte annotée** : les états sont uniques
  (IDs uniques par type) et listés une seule fois, dans l'ordre
  topologique depuis l'état initial ; pour chaque état (sauf l'initial),
  on liste ses **événements prédécesseurs** et ses **agents associés**, en
  annotant chaque relation de son/ses parcours (via `Journey_node`). Sous
  filtre actif, seules les relations du parcours actif sont listées.
- **Événements pendants** (arc entrant sans arc sortant) : ignorés dans le
  déroulé, MAIS avec la convention RG « toute branche se termine par un
  état (Final) » + filet de sécurité : les événements sans état successeur
  sont listés en fin de déroulé avec un marqueur (sinon perte silencieuse).
- **Vocabulaire** : pas de « description » dans le modèle — la note en
  infobulle porte la clé **`note`** (TSK26).
- **Nommage du dossier d'export** : hors périmètre de l'aperçu UI (niveau
  gestion de fichiers projet, traité avec `Files > Export Map`).

## 5. Points ouverts restants

1. **Format de l'export de lecture (fichier)** : HTML autonome statique
   conforme à SU007 — gabarits, CSS embarqué, UTF-8.
2. **Point d'entrée UI de l'export fichier** : `Files > Export Map` (stub) —
   boîte de dialogue de choix du dossier + confirmation.

## 6. Hors périmètre (acté)

- Export technique pour réimport (hors MVP, kanban « SU007 — Export
  technique pour réimport → hors périmètre »).
- Vue événements de l'export (version ultérieure).
- Lecture par relations d'agents (version ultérieure).
