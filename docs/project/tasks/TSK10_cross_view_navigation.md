# TSK10 — Navigation croisée entre vues avec focus (RG067)

- **Épic** : EPC03 — Implémenter la vue agents (SU009, FN032, RG067)
- **Statut** : Done (implémentation terminée, en attente du commit et des tests manuels de fin d'EPC03)
- **Date de début** : 15-10-2026
- **Dépendances** : #TSK08 (Done)

## Périmètre

Navigation croisée entre les deux espaces de travail, selon le contrat
spécifié dès la conception dans SU009 :

1. **Parcours → Agents** : le menu contextuel d'un node d'état propose
   « Show in agents view » ; l'application bascule sur l'onglet Agents et
   met en évidence la colonne de cet état (surbrillance + défilement).
2. **Agents → Parcours** : le menu contextuel d'une ligne d'agent de la
   matrice propose « Show in journey view » ; l'application bascule sur
   l'onglet Parcours et met en évidence l'ensemble des états associés à
   cet agent (nodes en surbrillance, reste du graphe atténué).

Le focus est régi par **RG067** : état visuel temporaire, ne marque ni
la carte ni le projet comme modifiés, non persisté, relâché par un clic
dans le vide ou la touche Échap.

## Règles et critères applicables

- **RG067** (contrat de focus, cf. ci-dessus).
- **SU009** : entrées « Voir dans la vue agents » / « Voir dans la vue
  parcours » ; le contrat commun est une méthode « mettre le focus sur
  une entité » (entité simple ou ensemble dérivé du modèle).
- **FN032** : la navigation ne marque ni la carte ni le projet comme
  modifiés.
- Patterns AGENTS.md : menu contextuel `menu.exec()` + dispatch ;
  communication workspace → MainWindow par signaux (découplage).

## État des lieux (existant mobilisable)

- Bascule d'onglets TSK07 : `tab_bar.setCurrentTab(name)` déclenche
  `_on_tab_changed` → changement de page + refresh de la matrice.
- Menu contextuel des State nodes (TSK04) : pattern établi dans
  `show_context_menu`, entrée « Associate agents... » à côté des
  Edit/Delete.
- Matrice TSK08/TSK09 : en-têtes avec IDs en `UserRole` ;
  `QTableWidget.scrollToItem` disponible pour le défilement ; la
  matrice n'a pas encore de menu contextuel.
- `JourneyWorkspace` : items de la scène, `set_selected_appearance` ;
  l'atténuation du graphe n'existe pas encore (à créer).
- Échap : aucun handler global dans MainWindow à ce stade.

## Plan d'implémentation

1. **Contrat de focus commun** : méthode `set_focus(entity_ids)` sur
   chaque vue, **relatif à la vue affichée** :
   - `JourneyWorkspace.set_focus(state_ids)` : surbrillance des nodes
     des états ciblés (contour bleu, réutilisation du style de
     sélection sans les sélectionner — le focus n'est pas la
     sélection, RG043 reste intangible), atténuation des autres items
     (opacité réduite).
   - `AgentsWorkspace.set_focus(state_id)` : surbrillance de la colonne
     (fond de ses cellules teinté) + `scrollToItem` sur la première
     cellule de la colonne.
   - Symétrique `clear_focus()` sur chaque vue : restauration des
     apparences normales.
   - Le focus ne touche ni `set_modified`, ni les layouts persistés
     (RG067).
2. **Sens Parcours → Agents** :
   - Entrée « Show in agents view » dans le menu contextuel des
     StateNode (`journey_workspace.py`, à côté de « Associate
     agents... »), dispatch vers un handler.
   - Le workspace émet un signal `focusStateInAgentsViewRequested(
     state_id)` (découplage) ; MainWindow : bascule
     `tab_bar.setCurrentTab("Agents")` puis
     `agents_page.set_focus(state_id)` (après le refresh déclenché par
     l'activation d'onglet, pour cibler la colonne reconstruite).
3. **Sens Agents → Parcours** :
   - Menu contextuel sur la matrice (`customContextMenuRequested`) :
     clic droit sur une cellule/ligne → menu « Show in journey view »
     sur l'agent de la ligne. (Le double-clic de SU009 est écarté : il
     entrerait en conflit avec l'édition de cellules TSK09 qui occupe
     déjà le simple clic ; à rediscuter si besoin.)
   - `AgentsWorkspace` émet
     `focusAgentInJourneyViewRequested(agent_id)` ; MainWindow :
     calcule les états associés à l'agent (`find_association`),
     bascule sur « Journey » puis `workspace.set_focus(state_ids)` ;
     si aucun état associé : message dans la barre d'infos
     (« Agent 'X' has no associated state ») sans bascule.
4. **Relâchement du focus (RG067)** :
   - `QShortcut(QKeySequence(Qt.Key_Escape))` sur MainWindow →
     `clear_focus()` sur la vue affichée.
   - Clic dans le vide : la vue parcours relâche dans
     `mousePressEvent` quand aucun item n'est sous le curseur ;
     la matrice relâche sur clic dans une zone sans cellule ou sur
     l'en-tête (clic de cellule = édition TSK09, on n'y touche pas).
5. **Tests** :
   - Suite unitaire : rien de testable sans Qt en plus (les états
     associés à un agent sont couverts par les tests d'association) ;
     un test pur possible sur la fonction « IDs des états associés à
     un agent » si elle est isolée (petit helper réutilisable).
   - Test offscreen local (rédigé, libGL) : focus colonne matrice,
     focus nodes parcours, relâchement Échap, message « no associated
     state ».
   - Test manuel : fin d'EPC03.

## Décisions à valider

- **Double-clic écarté** au profit du menu contextuel seul (le simple
    clic édite déjà la cellule, le double-clic serait ambigu). SU009
    mentionnait « ou un double-clic » : choix de la variante menu.
- **Focus ≠ sélection** : le focus met en surbrillance sans modifier la
    sélection courante (RG043 : la sélection reste unique et
    intangible ; RG067 : le focus est un état visuel distinct).
- **Atténuation du graphe** : opacité réduite des nodes non ciblés
    uniquement dans le sens Agents → Parcours (ensemble d'états) ; le
    sens Parcours → Agents n'atténue pas (une seule colonne visée).

## Vérifications attendues

1. `python -m py_compile` sur chaque fichier modifié.
2. Suite complète : `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
3. Test offscreen local (libGL) : deux sens + relâchement + cas limite.
4. Test manuel utilisateur : fin d'EPC03 (décision de cadrage) — cette
   tâche étant la dernière, elle déclenche la campagne de tests
   manuels.

## Journal des travaux

- 15-10-2026 : analyse, plan établi, passage en Doing.
- 15-10-2026 : trois décisions validées par l'utilisateur : double-clic
  écarté (menu contextuel seul, le clic édite déjà la cellule TSK09) ;
  focus distinct de la sélection (RG043 intangible) ; atténuation
  asymétrique (graphe atténué uniquement Agents → Parcours).
- 15-10-2026 : implémentation terminée :
  - `journey_workspace.py` : `set_focus(state_ids)` (nodes ciblés opacité
    1.0, reste 0.25 — atténuation), `clear_focus()`, `has_focus()` ;
    signal `focusStateInAgentsViewRequested(state_id)` ; entrée « Show
    in agents view » dans le menu contextuel des StateNode ; relâchement
    au clic dans le vide dans `mousePressEvent`.
  - `agents_workspace.py` : `set_focus(state_id)` (colonne teintée bleu
    clair + scrollToItem), `clear_focus()`, `has_focus()` ; menu
    contextuel de ligne « Show in journey view » (CustomContextMenu,
    clic dans le vide = relâchement) ; signal
    `focusAgentInJourneyViewRequested(agent_id)`.
  - `main_window.py` : handlers `_focus_state_in_agents_view` (bascule
    puis focus après le refresh d'onglet) et
    `_focus_agent_in_journey_view` (états associés via
    `state_agent_rel`, message « no associated state » sans bascule) ;
    `_release_focus` lié au raccourci Échap (QShortcut global) qui
    relâche la vue affichée.
  - RG067 respecté : aucun `set_modified`, aucune écriture de layout ;
    le focus n'est pas la sélection (aucun appel à setSelected).
  - Vérifications : `py_compile` OK ; suite complète 95 passed ; test
    offscreen rédigé dans
    `tests/test_agents/offscreen_cross_view_navigation.py` (local,
    libGL) : deux sens, relâchement Échap, cas agent sans association,
    projet non marqué modifié.
