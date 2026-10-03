# Test de création d'un projet PlanoScript (2026-10-03)

## Etape 1

### Action
- Création d'un projet.
- Sauvegarde sur le système de fichiers.

### Résultat
- Création d'un espace de travail.
- Matérialisation de l'état initial sur la grille d'affichage.
- Entrée "Save" du menu "Files" dégrisée.

### Donnée du projet
- Objet State :
  - id = 1 | typ = initial (nouveau).
- Objet Journey :
  - id = 1 (nouveau).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (nouveau).


---

## Etape 2

### Action
- création d'un évènement.
- Sauvegarde sur le système de fichiers.

### Résultat
- Matérialisation de l'évènement sur la grille d'affichage.
- Entrée "Save" du menu "Files" dégrisée.

### Données du projet
- Objet State :
  - id = 1 | typ = initial (inchangé).
- Objet Event :
  - id = 1 (nouveau).
- Objet Journey :
  - id = 1 (inchangé).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (inchangé).


---

## Etape 3

### Action
- Création d'une relation entre l'état initial et l'évènement.
- Sauvegarde sur le système de fichiers (avec l'option "Save as...").

### Résultat
- Matérialisation de la relation sur la grille d'affiachage.
- Entrée "Save" du menu "Files" toujours grisée.

### Données du projet
- Objet State :
  - id = 1 | typ = initial (inchangé).
- Objet Event :
  - id = 1 (inchangé).
- Objet Journey :
  - id = 1 (inchangé).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (inchangé).
  - id = 2 | from_event_id = 0 | state_id = 1 | to_event_id = 1 (nouveau).


---

### Etape 4

### Action
- Création d'un second état.
- Sauvegarde sur le système de fichiers.

### Résultat
- Matérialisation du nouvel état sur la grille d'affichage.
- Entrée "Save" du menu "Files" dégrisée.

### Données du projet
- Objet State :
  - id = 1 | typ = initial (inchangé).
  - id = 2 (nouveau).
- Objet Event :
  - id = 1 (inchangé).
- Objet Journey :
  - id = 1 (inchangé).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (inchangé).
  - id = 2 | from_event_id = 0 | state_id = 1 | to_event_id = 1 (inchangé).


---

### Etape 5

### Action
- Création d'une relation entre l'évènement et le second état.
- Sauvegarde sur le système de fichiers (avec l'option "Save as...").

### Résultat
- Matérialisation de la relation sur la grille d'affiachage.
- Entrée "Save" du menu "Files" toujours grisée.

### Données du projet
- Objet State :
  - id = 1 | typ = initial (inchangé).
  - id = 2 (inchangé).
- Objet Event :
  - id = 1 (inchangé).
- Objet Journey :
  - id = 1 (inchangé).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (inchangé).
  - id = 2 | from_event_id = 0 | state_id = 1 | to_event_id = 1 (inchangé).
  - id = 3 | from_event_id = 1 | state_id = 2 | to_event_id = 0 (nouveau).


---

### Etape 6

### Action
- Création d'un second évènement..
- Sauvegarde sur le système de fichiers.

### Résultat
- Matérialisation du nouvel évènement sur la grille d'affiachage.
- Entrée "Save" du menu "Files" dégrisée.

### Données du projet
- Objet State :
  - id = 1 | typ = initial (inchangé).
  - id = 2 (inchangé).
- Objet Event :
  - id = 1 (inchangé).
  - id = 2 (nouveau).
- Objet Journey :
  - id = 1 (inchangé).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (inchangé).
  - id = 2 | from_event_id = 0 | state_id = 1 | to_event_id = 1 (inchangé).
  - id = 3 | from_event_id = 1 | state_id = 2 | to_event_id = 0 (inchangé).


---

### Etape 7

### Action
- Création d'une relation entre le second état et le second évènement.
- Sauvegarde sur le système de fichiers (avec l'option "Save as...").

### Résultat
- Matérialisation de la relation sur la grille d'affiachage.
- Entrée "Save" du menu "Files" toujours grisée.

### Données du projet
- Objet State :
  - id = 1 | typ = initial (inchangé).
  - id = 2 (inchangé).
- Objet Event :
  - id = 1 (inchangé).
  - id = 2 (nouveau).
- Objet Journey :
  - id = 1 (inchangé).
- Objet state_node :
  - id = 1 | from_event_id = 0 | state_id = 1 | to_event_id = 0 (inchangé).
  - id = 2 | from_event_id = 0 | state_id = 1 | to_event_id = 1 (inchangé).
  - id = 3 | from_event_id = 1 | state_id = 2 | to_event_id = 0 (inchangé).
  - id = 4 | from_event_id = 0 | state_id = 2 | to_event_id = 2 (nouveau).
