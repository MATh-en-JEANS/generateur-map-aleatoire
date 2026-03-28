# Générateur Procédural de Map Impossible

Ce projet génère automatiquement des cartes de jeu stratégique volontairement impossibles à gagner.

L'idée est simple : un joueur doit survivre en évitant le **Palais** (lieu `5`). Or, la carte n'est conservée que si le programme prouve qu'en **10 jours maximum**, tous les joueurs finissent fatalement au Palais, quels que soient leurs choix.

## Concept

Le script modélise un petit jeu sous forme de graphe :

- `4` lieux jouables : `1`, `2`, `3`, `4`
- `1` lieu fatal : le **Palais** (`5`)
- des routes entre les lieux `1` à `4`
- chaque route possède un type parmi `1`, `2`, `3`, `4`
- chaque jour, un seul type de route est actif

Si un joueur se trouve dans un lieu sans route disponible pour le type actif du jour, il est considéré comme envoyé au Palais et meurt.

## Ce Que Fait Le Script

Le fichier [`generateurMapAleatoire.py`](/f:/Python%20in%20Web/generateurMapAleatoire.py) :

- crée des cartes aléatoires
- crée un calendrier aléatoire de `10` jours
- simule toutes les positions encore survivables
- rejette les cartes où une survie reste possible
- conserve uniquement les cartes où la mort est inévitable pour tout le monde
- affiche le résultat en texte dans la console
- génère une image récapitulative de la carte, du calendrier et de la simulation

## Fonctionnement Interne

### 1. Génération de la carte

Pour chaque paire de lieux parmi `1`, `2`, `3`, `4`, le script ajoute aléatoirement `1` ou `2` routes typées.

Les fonctions principales liées à cette étape sont :

- [`generer_carte()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L93)
- [`CarteJeu`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L55)
- [`Route`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L38)

### 2. Génération du calendrier

Le script tire ensuite une suite de `10` jours. Chaque jour active un unique type de route parmi `1`, `2`, `3` ou `4`.

Fonction concernée :

- [`generer_calendrier()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L103)

### 3. Simulation

Le cœur du programme ne suit pas un seul joueur : il suit **l'ensemble des positions encore atteignables pour un joueur qui jouerait au mieux**.

Autrement dit :

- si au moins une stratégie permet encore de survivre, la carte n'est pas valide
- si plus aucune position survivable n'existe, la mort est considérée comme inévitable

Fonctions concernées :

- [`simuler()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L110)
- [`simuler_depuis()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L134)
- [`simulation_detaillee()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L150)

### 4. Validation de la carte

Le programme boucle jusqu'à trouver une carte qui respecte la contrainte principale :

> aucun joueur ne peut survivre plus de `10` jours

Fonction concernée :

- [`generer_carte_valide()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L185)

### 5. Sortie texte et image

Une fois une carte valide trouvée, le script :

- affiche les connexions
- affiche une matrice d'adjacence
- affiche le calendrier des types actifs
- affiche une simulation détaillée jour par jour
- génère une image de synthèse

Fonctions concernées :

- [`afficher_carte()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L205)
- [`afficher_matrice()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L229)
- [`afficher_calendrier()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L262)
- [`afficher_simulation()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L281)
- [`generer_image()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L631)
- [`main()`](/f:/Python%20in%20Web/generateurMapAleatoire.py#L676)

## Installation

### Prérequis

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

Par défaut, le programme ouvre une fenêtre système "Enregistrer sous" pour vous laisser choisir l'emplacement d'exportation de l'image.

Choisir un fichier de sortie précis :

```bash
python generateurMapAleatoire.py --output exports/map.png
```

Choisir seulement un dossier d'export :

```bash
python generateurMapAleatoire.py --output exports
```

Le programme :

- cherche une carte valide
- affiche son analyse dans la console
- sauvegarde une image de synthèse

## Point Important Sur Le Chemin De Sortie

L'image n'est plus enregistrée dans un chemin codé en dur.

Par défaut, le script ouvre un explorateur de fichiers pour vous laisser choisir le nom du fichier et le dossier de sortie.

Si cette fenêtre est annulée ou ne peut pas s'ouvrir, l'image est exportée dans :

```python
exports/map.png
```

Vous pouvez maintenant choisir l'emplacement avec l'option `--output`.

Exemples :

```bash
python generateurMapAleatoire.py --output exports/map.png
python generateurMapAleatoire.py --output "D:\\Mes Images\\map.png"
python generateurMapAleatoire.py --output "D:\\Mes Images"
```

Si vous fournissez un dossier au lieu d'un nom de fichier, le script créera automatiquement `map.png` dans ce dossier.

## Pourquoi Ce Projet Est Intéressant

Ce script est un bon exemple de :

- génération procédurale
- modélisation par graphe
- simulation d'états possibles
- validation automatique de contraintes
- visualisation de résultat avec `matplotlib`

Il peut servir comme base pour :

- un prototype de jeu
- un projet scolaire
- une exploration mathématique ou algorithmique
- une démonstration de recherche exhaustive sur un petit espace d'états

## Limites Actuelles

- les paramètres du jeu sont fixes dans le code
- il n'y a pas d'arguments en ligne de commande
- le chemin de sortie de l'image n'est pas configurable depuis l'extérieur
- le résultat est aléatoire d'une exécution à l'autre

## Résumé

Ce programme ne cherche pas une "bonne" carte : il cherche une carte **fatalement perdante**.

Sa force vient de la simulation : la carte n'est acceptée que si le script peut montrer qu'il n'existe **aucune stratégie de survie** pour les joueurs.
