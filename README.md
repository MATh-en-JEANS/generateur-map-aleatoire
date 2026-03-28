# Generateur Procedural de Map Impossible

Ce projet genere automatiquement des cartes de jeu strategique volontairement impossibles a gagner.

L'idee est simple : un joueur doit survivre en evitant le **Palais** (lieu `5`). Or, la carte n'est conservee que si le programme prouve qu'en **10 jours maximum**, tous les joueurs finissent fatalement au Palais, quels que soient leurs choix.

## Concept

Le script modele un petit jeu sous forme de graphe :

- `4` lieux jouables : `1`, `2`, `3`, `4`
- `1` lieu fatal : le **Palais** (`5`)
- des routes entre les lieux `1` a `4`
- chaque route possede un type parmi `1`, `2`, `3`, `4`
- chaque jour, un seul type de route est actif

Si un joueur se trouve dans un lieu sans route disponible pour le type actif du jour, il est considere comme envoye au Palais et meurt.

## Ce Que Fait Le Script

Le fichier [`generateurMapAleatoire.py`](/f:/Python%20in%20Web/generateurMapAleatoire.py) :

- cree des cartes aleatoires
- cree un calendrier aleatoire de `10` jours
- simule toutes les positions encore survivables
- rejette les cartes ou une survie reste possible
- conserve uniquement les cartes ou la mort est inevitable pour tout le monde
- affiche le resultat en texte dans la console
- genere une image recapitulative de la carte, du calendrier et de la simulation

## Fonctionnement Interne

### 1. Generation de la carte

Pour chaque paire de lieux parmi `1`, `2`, `3`, `4`, le script ajoute aleatoirement `1` ou `2` routes typées.

Les fonctions principales liees a cette etape sont :

- [`generer_carte()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L93)
- [`CarteJeu`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L55)
- [`Route`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L38)

### 2. Generation du calendrier

Le script tire ensuite une suite de `10` jours. Chaque jour active un unique type de route parmi `1`, `2`, `3` ou `4`.

Fonction concernee :

- [`generer_calendrier()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L103)

### 3. Simulation

Le coeur du programme ne suit pas un seul joueur : il suit **l'ensemble des positions encore atteignables pour un joueur qui jouerait au mieux**.

Autrement dit :

- si au moins une strategie permet encore de survivre, la carte n'est pas valide
- si plus aucune position survivable n'existe, la mort est consideree comme inevitable

Fonctions concernees :

- [`simuler()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L110)
- [`simuler_depuis()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L134)
- [`simulation_detaillee()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L150)

### 4. Validation de la carte

Le programme boucle jusqu'a trouver une carte qui respecte la contrainte principale :

> aucun joueur ne peut survivre plus de `10` jours

Fonction concernee :

- [`generer_carte_valide()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L185)

### 5. Sortie texte et image

Une fois une carte valide trouvee, le script :

- affiche les connexions
- affiche une matrice d'adjacence
- affiche le calendrier des types actifs
- affiche une simulation detaillee jour par jour
- genere une image de synthese

Fonctions concernees :

- [`afficher_carte()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L205)
- [`afficher_matrice()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L229)
- [`afficher_calendrier()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L262)
- [`afficher_simulation()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L281)
- [`generer_image()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L631)
- [`main()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L676)

## Installation

### Prerequis

- Python 3
- `numpy`
- `matplotlib`

Installation rapide :

```bash
pip install numpy matplotlib
```

## Utilisation

Lancer le script avec :

```bash
python generateurMapAleatoire.py
```

Le programme :

- cherche une carte valide
- affiche son analyse dans la console
- sauvegarde une image de synthese

## Point Important Sur Le Chemin De Sortie

Dans l'etat actuel, l'image est enregistree via un chemin Windows code en dur dans le script :

```python
D:\math en jeans\images\map.png
```

Si ce dossier n'existe pas sur votre machine, il faut modifier la variable `chemin_image` dans [`main()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L676).

## Pourquoi Ce Projet Est Interessant

Ce script est un bon exemple de :

- generation procedurale
- modelisation par graphe
- simulation d'etats possibles
- validation automatique de contraintes
- visualisation de resultat avec `matplotlib`

Il peut servir comme base pour :

- un prototype de jeu
- un projet scolaire
- une exploration mathematique ou algorithmique
- une demonstration de recherche exhaustive sur un petit espace d'etats

## Limites Actuelles

- les parametres du jeu sont fixes dans le code
- il n'y a pas d'arguments en ligne de commande
- le chemin de sortie de l'image n'est pas configurable depuis l'exterieur
- le resultat est aleatoire d'une execution a l'autre

## Resume

Ce programme ne cherche pas une "bonne" carte : il cherche une carte **fatalement perdante**.

Sa force vient de la simulation : la carte n'est acceptee que si le script peut montrer qu'il n'existe **aucune strategie de survie** pour les joueurs.
