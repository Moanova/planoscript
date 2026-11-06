# Note préparatoire à la conception du projet « hyperscript »

- **Date** : 2026-11-06
- **Statut** : acté en séance TSC — point de départ du nouveau projet
- **Contexte** : clôture de planoscript après correction des derniers bugs de la
  version actuelle, puis création d'un nouveau projet nommé **hyperscript**.
  Cette note synthétise la séance d'analyse menée à partir des deux cas de test
  (`docs/conception/02_persona_01_test_case-FR.md`,
  `docs/conception/02_persona_02_test_case-FR.md`) et des fichiers de projet
  réels sauvegardés depuis l'application (`testCase01.json` — persona Jen Yen,
  RPG à 3 alternatives ; `testCase02.json` — persona Tom Son, micro-série
  sentimentale à 10 personnages), analysés en séance (chargement via
  `Project.from_dict`, reconstruction du graphe, filtres et export exécutés).
- **Version EN** : à produire dans le nouveau projet (contenu identique).

---

## 1. Décisions de portée

1. **planoscript est clôturé** après correction des bugs listés en §7.
2. **Nouveau projet « hyperscript »**, dont le point de départ est cette note.
3. Le périmètre MVP d'hyperscript est à redéfinir à partir de cette note
   (points en suspens §8), notamment : plusieurs cartes narratives par projet
   (axe épisodes), relations agent-agent, contrôle de cohérence.

## 2. Sémantique actée (FR / EN)

| FR | EN | Remplace (planoscript) |
|---|---|---|
| **Bloc narratif** { Début ; Scène ; Branch ; Condition ; Fin } | **Narrative block** { Start ; Scene ; Branch ; Condition ; End } | State / Event (deux composants séparés) |
| **Transition** | **Transition** | arc State_to_event / Event_to_state |
| **Participation** | **Participation** | association State_agent_rel (agent ↔ état, non directionnelle) |
| **Relation** (typée) | **Relation** (typed) | — (hors MVP planoscript ; texte libre dans les faits) |
| **Agent** { Personnage ; Artefact } | **Agent** { Character ; Artefact } | Agent { Subject ; Object } |
| **Parcours** | **Journey** | Journey (« Version » retenu comme alternative — §8) |

- Un seul objet **Bloc narratif** pour tous les types ; le `typ` est choisi à la
  création et **immuable** ensuite (pattern déjà éprouvé pour `Initial`,
  RG061/RG062), avec un rendu visuel différent par type.
- « Relation » n'est plus un terme chapeau : il désigne exclusivement les
  relations agent-agent. Les menus ne l'utilisent plus comme umbrella.
- Le type d'état `Relation` (ex. S5 dans testCase02) disparaît : la scène
  concernée redevient une **Scène**.

## 3. Modèle de données acté

- **Projet** { id, lb, dates, agents[], narrative_maps[] } — agents au niveau
  projet ; la liste de cartes est **déjà prévue pour N cartes** (axe
  épisodes/saisons délégué aux cartes multiples).
- **Carte narrative** { id, lb, active_version_id, blocs[], transitions[],
  participations[], relations[], versions[] }
- **Bloc narratif** { id, lb, typ ∈ {Début, Scène, Branch, Condition, Fin},
  note, content, dates }
- **Transition** { id, from_block_id, to_block_id, note, dates } — dirigée
  bloc → bloc ; tout chaînage autorisé (plus de contrainte bipartite).
- **Participation** { id, block_id, agent_id, note, dates } — présence d'un
  agent dans un bloc (symétrique, vue matrice).
- **Relation** { id, block_id (ancre), agent_a_id, agent_b_id, typ, note,
  content, dates } — dirigée et typée, **ancrée à un bloc** : « à ce moment du
  récit, la relation A —typ→ B est vraie ». L'historique d'une paire =
  ses ancres ordonnées par rang du bloc ; l'état courant à un bloc = dernière
  ancre de rang ≤ rang du bloc (dérivé, jamais stocké).
- **Version/Parcours** { id, lb, default, note } + **nœud de version**
  { version_id, block_id, sequence_order } — le rattachement se fait **sur les
  blocs**, pas sur les transitions.
- **Agent** { id, lb, typ ∈ {Personnage, Artefact}, note, content, dates }.

## 4. Règles actées (invariants, appliqués par l'application)

- **Début** : unique, créé automatiquement, immuable ; peut porter la
  bifurcation (cas testCase01 : 3 transitions sortantes du bloc initial).
- **Fin** : degré sortant 0 ; on interdit d'y ajouter une transition sortante
  (pour prolonger : dupliquer le bloc en Scène).
- **Branch** : degré sortant ≥ 2 ; **promotion automatique unidirectionnelle**
  Scène → Branch quand une 2e transition sortante est créée (jamais l'inverse).
  Ses transitions mènent soit à des blocs **Condition** (branche gardée), soit
  directement à des Scènes (choix libre, libellé en note de transition).
- **Condition** : exactement 1 transition entrante (depuis une Branch) et
  1 sortante (vers la scène gardée). Porte la condition structurée : kind
  (choix / artefact / compétence / flag), ref vers un agent Artefact, label.
  Chaîner des blocs Condition = ET ; deux Condition issus d'une même Branch = OU.
- **Appartenance à une version dérivée** (règle uniforme) : une Transition
  appartient à une version ssi **ses deux extrémités** y appartiennent ; une
  Participation ou une Relation y appartient ssi son **bloc d'ancrage** y
  appartient. (Résout par construction la pollution croisée des associations
  constatée dans testCase01.)
- **Séquence** : DFS depuis le Début sur les transitions de la version, branches
  explorées par id de transition croissant, mémoïsation des cycles, repli
  déterministe pour les blocs inatteignables (analogue RG069).
- **Unicité** : une transition par paire ordonnée de blocs ; (bloc, paire,
  typ) unique pour les relations ; une participation unique par (bloc, agent).
- **Cascades** : suppression d'un agent → ses participations et relations ;
  suppression d'un bloc → ses transitions, participations, relations ancrées,
  nœuds de version ; suppression d'une transition → nœuds de version
  référençant. **Ne pas reproduire le bug planoscript** `connection.py:811`
  (suppression d'arc sans nettoyage des nœuds de parcours — voir §7).

## 5. Vues (espaces de travail)

1. **Vue Blocs** (ex-vue Events) : graphe des blocs, rendu par type ;
   filtre par version (non persisté) ; badges de participations.
2. **Vue Agents** : matrice agents × blocs des Participations.
3. **3e espace de travail « Relations »** (déjà anticipé par
   `99_mvp_scope-FR.md` §5) : graphe des agents, arcs étiquetés par typ,
   annotés des blocs d'ancrage ; navigation croisée vers le bloc dans la vue
   Blocs (analogue RG067).
4. **Vue Export** : aperçu de lecture par version.

## 6. Export

- Texte de lecture par version : blocs dans l'ordre de séquence ; transitions
  rendues en ligne ; conditions rendues sur leur branche (« → si artefact
  « clé USB » : … ») ; relations listées sous leur bloc d'ancrage ; section
  finale « état des relations » (dernier typ par paire).
- Export technique formaté pour l'équipe de développement (persona Jen Yen,
  frustration n°3) : à concevoir.

## 7. Constats des deux cas de test et bugs planoscript à corriger avant clôture

**Cas n°1 (Jen Yen, `testCase01.json`)** — pattern retenu : préfixe/suffixe
communs + un parcours par alternative (fonctionne, RG069 vérifié). Incorrections
relevées :
- **Nœud fantôme** : `journey_node#22` référence l'arc supprimé `s2e#5` →
  **corrigé (TSK35, 06-11-2026)** : `Connection.delete_arc_or_association`
  passe par `ArcService.delete_relation` (suppression des `Journey_node`
  référençant + recompute RG069 ; code mort `set_modified` retiré) et
  `ProjectService.load_project` purge les nœuds orphelins au chargement
  (`ArcService.prune_orphan_journey_nodes`). Dette TSK34 restante : passage
  complet par use cases.
- **Pollution croisée des associations entre parcours** (états de branches
  étrangères visibles sous le filtre d'un autre parcours) → **corrigée
  (TSK35)** : RG026 révisée FR/EN, appartenance dérivée des arcs seuls, une
  association n'est visible que si son état l'est ; également résolue par la
  dérivation §4 dans le nouveau modèle. Autres constats : libellés dupliqués
  (`Ett 03P2` ×2…) ; notes de parcours copiées ; jours J1/J2 fusionnés dans
  un même `content`.

**Cas n°2 (Tom Son, `testCase02.json`)** — graphe linéaire propre. Constats :
relations uniquement en texte libre (notes d'agents), 4 agents sur 10 sans
aucune association, fin du récit non marquée `Final`. Besoins : relations
agent-agent typées (fait/rumeur) séquencées sur le récit → d'où le modèle §3.

**Bug latent export** (à corriger avant clôture) : `ExportService`
(`src/core/services/export_service.py:~187`) — `_esc(rel.agent_id)` plante
avec un `int` si l'agent n'est pas dans la liste passée à `build_reading_text`.

## 8. Points en suspens

- **« Version » vs « Parcours »** comme terme pour Journey (Version retenu comme
  alternative ; parle bien aux deux personas).
- **Libellé FR affiché pour `Branch`** (proposé en séance : Bascule /
  Embranchement / Choix).
- **Typage des Relations** : texte libre vs liste de valeurs enrichissable par
  l'auteur.
- **N cartes narratives par projet dans le périmètre MVP d'hyperscript**
  (axe épisodes/saisons ; le modèle l'anticipe, le MVP planoscript l'excluait).
- Détails des invariants (cycles autorisés ?, unicité exacte des transitions).
- Maquette du 3e espace de travail « Relations ».
- **Migration** des projets planoscript existants (State/Event → Bloc avec typ
  mappé ; arcs → Transitions ; nœuds de parcours arc → bloc ; associations →
  Participations).
- **Contrôle de cohérence** (impasses, branches non terminées, Branch à une
  seule branche, Fin non atteinte) : à réévaluer pour hyperscript — besoin
  persona 1 « aucune impasse narrative » ; permet de distinguer fin
  intentionnelle (Fin) d'une branche morte.
- Exports (lecture + technique dev), zoom, annuler/rétablir : à re-périmétrer.

## 9. Prochaines étapes

1. Corriger les bugs §7 dans planoscript, clôturer le projet.
2. Créer le dépôt **hyperscript** avec cette note comme point de départ, puis
   rédiger les specs FR/EN (user stories, règles de gestion, features,
   interface, menu, modèle de données, périmètre MVP) et le kanban.
