# Charte UI Planoscript — Refonte thème sombre

Document projet : synthèse des changements à apporter à l'interface de planoscript pour l'aligner sur la nouvelle esthétique attendue (thème sombre de type VS Code / Fluent Design).


## 1. Diagnostic de l'état actuel

L'interface actuelle de planoscript repose sur un thème clair :
- Arrière-plan gris clair (#F5F5F5), panneaux blancs (#FFFFFF), texte noir, bordures gris clair (#CCCCCC) ;
- Accents pastel dispersés : bleu clair (#E6F2FF) pour l'onglet sélectionné, vert (#C8E6C9) pour les objets State, violet (#E1BEE7) pour les objets Event, cercles rouges et verts pour les points d'ancrage, contour bleu clair au survol ;
- Noeuds arrondis avec ombres subtiles, grille claire dans le panneau central.

La cible est un thème sombre : arrière-plan #1E1E1E, surfaces #2D2D2D, texte blanc/gris clair, séparateurs #383838, accent unique bleu #0078D4, arrondis légers, absence d'ombres. Sur la structure et le traitement des surfaces, planoscript adopte intégralement ces codes ; seule la couleur d'accent est réinterprétée en or doux #E5C07B afin d'obtenir une palette fonctionnelle appariée, conformément à la décision projet.

## 2. Palette cible

| Rôle | Couleur actuelle | Couleur cible | Code hexadécimal |
|---|---|---|---|
| Arrière-plan principal | Gris clair | Gris très sombre | `#1E1E1E` |
| Surfaces (barre de menus, panneaux, nœuds) | Blanc | Gris sombre | `#2D2D2D` |
| Bordures et séparateurs | Gris clair | Gris sombre discret | `#383838` |
| Lignes de grille | Gris clair | Gris très discret | `#333333` |
| Texte principal | Noir | Blanc | `#FFFFFF` |
| Texte secondaire | Noir | Gris clair | `#CCCCCC` |
| Onglets Journey / Agents | Onglet actif en bleu pastel | Traitement identique neutre : contour `#383838`, libellé `#CCCCCC` |
| Objets State | Vert pastel #C8E6C9 | Or doux | `#E5C07B` |
| Objets Event | Violet pastel #E1BEE7 | Cuivre | `#D19A66` |
| Points d'ancrage (entrants et sortants) | Rouge et vert | Blanc doux unique | `#F0F0F0` |
| Contour au survol | Bleu clair | Blanc doux | `#F0F0F0` |

### Justification de l'appariement

La palette fonctionnelle (State, Event, ancres, survol) abandonne le bleu et le violet au profit d'une famille chromatique unique, chaude et désaturée, inspirée de la palette « One Dark » : toutes les teintes partagent une luminosité perçue et une saturation comparables, ce qui les rend appariées entre elles et cohérentes sur les surfaces sombres (#1E1E1E, #2D2D2D) :

- L'or doux #E5C07B et le cuivre #D19A66 sont deux teintes chaudes adjacentes mais clairement distinctes : l'or désigne les objets State, le cuivre les objets Event ;
- Le blanc doux #F0F0F0 sert à la fois au survol et aux points d'ancrage : il se lit comme un éclaircissement neutre, sans introduire de teinte supplémentaire, et offre un contraste maximal (environ 12 pour 1 sur #2D2D2D) ;
- La sélection ne nécessite aucune couleur dédiée : elle est matérialisée par le passage du contour de l'objet en pointillés, la teinte du contour restant celle du type de l'objet.

Règle de priorité des contours : sélection (pointillés) > survol (blanc doux) > type (or ou cuivre). Un objet survolé affiche un contour blanc doux continu ; un objet sélectionné affiche un contour pointillé de la teinte de son type, y compris au survol.

## 3. Typographie

- Famille : `Segoe UI, system-ui, sans-serif` ;
- Menus et libellés de panneaux : environ 12 px ;
- Texte des nœuds (libellé des états, événements et agents, vues Journey et Agents) : 9 pt, taille de l'infobulle (révision TSC 28-10-2026) ;
- Titres et libellés de type d'objet : environ 14 px, gras.

## 4. Synthèse des changements

1. Inversion globale du thème : passage d'un thème clair à un thème sombre. L'arrière-plan principal devient #1E1E1E ; la barre de menus et les panneaux deviennent #2D2D2D ; les bordures et séparateurs deviennent #383838.
2. Texte : le texte principal passe en blanc (#FFFFFF), le texte secondaire (libellés d'onglets, éléments inactifs) en gris clair (#CCCCCC).
3. Onglets : les onglets Journey et Agents adoptent un traitement identique et neutre (contour #383838, libellé gris clair #CCCCCC), en remplacement de la marque bleu pastel #E6F2FF sur l'onglet actif.
4. Objets du diagramme : les nœuds adoptent une surface unifiée #2D2D2D sans ombre, avec un arrondi d'environ 6 px. La distinction de type se fait par le contour et le libellé de type :
   - Objets State : contour et libellé or doux #E5C07B ;
   - Objets Event : contour et libellé cuivre #D19A66.
   Les fonds verts et violets passés sont supprimés.
5. Points d'ancrage : les cercles entrants (rouges) et sortants (verts) sont remplacés par une couleur unique blanc doux #F0F0F0 (contour sur fond sombre), appliquée à toutes les ancres.
6. Survol : le contour bleu clair actuel est remplacé par le blanc doux #F0F0F0, lecture neutre cohérente avec les ancres.
7. Sélection : un objet sélectionné se signale par un contour en pointillés (motif d'environ 6 px / 4 px), la teinte du contour restant celle du type de l'objet. Aucune couleur dédiée n'est nécessaire.
8. Connexions : les liaisons pointillées passent en gris clair #CCCCCC sur fond sombre.
9. Grille : les lignes de la grille du panneau central passent à #333333 sur fond #1E1E1E.
10. Ombres : suppression des ombres portées sous les nœuds, conformément au style minimaliste de la cible.
11. Barre latérale gauche : aucune barre latérale n'existe à ce jour dans l'application. Le panneau central s'étend sur toute la largeur de la fenêtre. Une barre latérale gauche pourra être ajoutée plus tard ; elle n'est pas partie de cette révision.
12. Barre latérale droite (Journey Filter) : **hors périmètre de cette révision**. L'ajout du panneau « Journey Filter » (environ 240 px, sur le côté droit de la fenêtre) fera l'objet d'un chantier ultérieur, de même que la décision de sa présence ou non dans chacun des deux espaces de travail (Journey et Agents). À ce stade, aucune barre latérale droite n'est créée ; la maquette (97_layout_revision-EN.svg) la figure comme espace réservé.
13. Onglets : les onglets Journey et Agents demeurent à leur emplacement actuel, c'est-à-dire en haut à gauche de la fenêtre, directement sous la barre de menus ; tous deux partagent exactement la même apparence : surface #2D2D2D, contour #383838, libellé gris clair #CCCCCC.
14. Boîtes de dialogue : le thème sombre s'applique également aux dialogues de l'application (édition d'un composant, gestion des agents, « À propos », etc.) : surfaces #2D2D2D, texte principal #FFFFFF, texte secondaire #CCCCCC, bordures et séparateurs #383838.

## 5. Sémantique des couleurs d'état

| État | Élément concerné | Couleur |
|---|---|---|
| Type State | Contour et libellé | `#E5C07B` |
| Type Event | Contour et libellé | `#D19A66` |
| Survol | Contour de l'objet (continu) | `#F0F0F0` |
| Sélection | Contour de l'objet, en pointillés | Teinte du type (`#E5C07B` ou `#D19A66`) |
| Ancres (entrantes et sortantes) | Cercles de connexion | `#F0F0F0` |
| Badge d'agents (pastille sur les nœuds d'état de la vue parcours, coin bas-droit, 2/3 dedans et 1/3 dehors du contour — TSK17, TSC 28-10-2026) | Remplissage / contour / texte | `#E5C07B` / `#F0F0F0` / `#1E1E1E` |
| Badges d'évènement (deux pastilles sur les cartes d'état de la vue agents : gauche = événements sources entrants, droite = événements cibles sortants ; centrés verticalement, à cheval sur les bords G/D — coordonnées des ports de connexion de la vue parcours, TSC 28-10-2026) | Remplissage / contour / texte | `#D19A66` / `#F0F0F0` / `#1E1E1E` |

Règle de priorité des contours : sélection > survol > type. Un objet survolé affiche un contour blanc doux continu ; un objet sélectionné affiche un contour pointillé de la teinte de son type, même au survol.

## 6. Variables CSS de référence

```css
:root {
  --bg-primary: #1E1E1E;
  --bg-surface: #2D2D2D;
  --text-primary: #FFFFFF;
  --text-secondary: #CCCCCC;
  --border: #383838;
  --grid-line: #333333;
  --accent: #E5C07B;        /* réserve d'accent, non affectée aux onglets (identiques et neutres) */
  --state: #E5C07B;         /* objets State */
  --event: #D19A66;         /* objets Event */
  --anchor: #F0F0F0;        /* points d'ancrage entrants et sortants */
  --hover: #F0F0F0;         /* contour au survol */
  --connection: #CCCCCC;   /* liaisons pointillées */
  --badge-bg: #E5C07B;     /* remplissage des badges d'agents (teinte des objets State) */
  --badge-border: #F0F0F0; /* contour des badges d'agents */
  --badge-text: #1E1E1E;   /* texte des badges d'agents (lisible sur fond clair) */
  --event-badge-bg: #D19A66; /* remplissage des badges d'évènement sur les cartes d'état de la vue agents (teinte des objets Event, même style que les badges d'agents) */
  --selected-style: dashed; /* sélection : contour pointillé, teinte du type conservée */
  --radius: 6px;
  font-family: "Segoe UI", system-ui, sans-serif;
}
```

## 7. Structure

La hiérarchie structurelle existante est conservée pour la barre de menus (Files, Edit, Display, Project, About) et les onglets Journey/Agents, qui demeurent en haut à gauche de la fenêtre, directement sous la barre de menus, à leur emplacement actuel. Aucune barre latérale n'existe à ce jour : le panneau central quadrillé s'étend sur toute la largeur de la fenêtre. Une barre latérale gauche pourra être ajoutée plus tard, et une barre latérale droite « Journey Filter » (environ 240 px, espace réservé figuré dans la maquette) fera l'objet d'un chantier ultérieur, y compris la décision de sa présence dans les deux espaces de travail ; ce panneau n'est pas créé dans cette révision. Seules les couleurs, les ombres et les finitions sont modifiées.
