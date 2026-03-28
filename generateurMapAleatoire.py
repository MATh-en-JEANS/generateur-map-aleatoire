"""
Generateur procedural de map pour jeu strategique.

Regle : Le joueur doit eviter le Palais (Lieu 5).
        S'il y arrive, il meurt instantanement.

Contrainte : La map generee doit etre IMPOSSIBLE a gagner.
             Tous les joueurs atteignent le Palais en 10 jours maximum.

Fonctionnement :
  - Graphe de 5 lieux (1-4 + Palais)
  - Routes typees (1-4) entre les lieux 1-4
  - Chaque jour, 1 seul type de route est actif
  - Si aucun deplacement possible -> route automatique vers le Palais (mort)
  - Le generateur boucle jusqu'a trouver une map ou la mort est inevitable
"""

import random
import os
import argparse
from itertools import combinations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ── Configuration ─────────────────────────────────────────────────────────────

MAX_JOURS = 10
LIEUX = [1, 2, 3, 4]
TYPES_ROUTE = [1, 2, 3, 4]
PALAIS = 5


# ── Classes ───────────────────────────────────────────────────────────────────

class Route:
    """Route bidirectionnelle entre deux lieux, avec un type."""

    def __init__(self, lieu_a, lieu_b, type_route):
        self.lieu_a = lieu_a
        self.lieu_b = lieu_b
        self.type_route = type_route

    def destination(self, depuis):
        """Retourne l'autre extremite si la route part de 'depuis'."""
        if self.lieu_a == depuis:
            return self.lieu_b
        if self.lieu_b == depuis:
            return self.lieu_a
        return None


class CarteJeu:
    """Graphe representant la carte du jeu (lieux + routes)."""

    def __init__(self):
        self.routes = []

    def ajouter_route(self, lieu_a, lieu_b, type_route):
        self.routes.append(Route(lieu_a, lieu_b, type_route))

    def voisins(self, lieu, type_actif):
        """Lieux accessibles depuis 'lieu' via des routes du type actif."""
        result = set()
        for route in self.routes:
            if route.type_route == type_actif:
                dest = route.destination(lieu)
                if dest is not None:
                    result.add(dest)
        return result

    def types_disponibles(self, lieu):
        """Types de routes partant d'un lieu donne."""
        types = set()
        for route in self.routes:
            if route.destination(lieu) is not None:
                types.add(route.type_route)
        return types

    def routes_par_paire(self):
        """Dict {(a, b): [types]} regroupe par paire de lieux."""
        paires = {}
        for route in self.routes:
            cle = (min(route.lieu_a, route.lieu_b), max(route.lieu_a, route.lieu_b))
            paires.setdefault(cle, []).append(route.type_route)
        return paires


# ── Generation aleatoire ─────────────────────────────────────────────────────

def generer_carte():
    """Cree une carte aleatoire : 1 ou 2 routes typees par paire de lieux."""
    carte = CarteJeu()
    for a, b in combinations(LIEUX, 2):
        nb_routes = random.randint(1, 2)
        for _ in range(nb_routes):
            carte.ajouter_route(a, b, random.choice(TYPES_ROUTE))
    return carte


def generer_calendrier():
    """Cree un calendrier aleatoire : 1 type actif par jour, sur MAX_JOURS."""
    return [random.choice(TYPES_ROUTE) for _ in range(MAX_JOURS)]


# ── Simulation ────────────────────────────────────────────────────────────────

def simuler(carte, calendrier):
    """
    Verifie si TOUS les joueurs meurent dans le delai.

    Principe : on suit l'ensemble 'atteignable' = positions ou un joueur
    pourrait encore etre en vie (en faisant les meilleurs choix possibles).
    Si cet ensemble se vide, aucune strategie ne permet de survivre.

    Retourne (valide, jour_mort).
    """
    atteignable = set(LIEUX)

    for jour, type_actif in enumerate(calendrier, 1):
        suivant = set()
        for lieu in atteignable:
            suivant.update(carte.voisins(lieu, type_actif))
        atteignable = suivant

        if not atteignable:
            return True, jour

    return False, MAX_JOURS


def simuler_depuis(carte, calendrier, depart):
    """Simule depuis un lieu de depart. Retourne le jour de mort ou None."""
    atteignable = {depart}

    for jour, type_actif in enumerate(calendrier, 1):
        suivant = set()
        for lieu in atteignable:
            suivant.update(carte.voisins(lieu, type_actif))
        atteignable = suivant

        if not atteignable:
            return jour

    return None


def simulation_detaillee(carte, calendrier):
    """Trace jour par jour : qui meurt, qui survit, ou."""
    atteignable = set(LIEUX)
    trace = []

    for jour, type_actif in enumerate(calendrier, 1):
        suivant = set()
        morts = set()
        mouvements = {}

        for lieu in atteignable:
            voisins = carte.voisins(lieu, type_actif)
            if voisins:
                suivant.update(voisins)
                mouvements[lieu] = voisins
            else:
                morts.add(lieu)

        trace.append({
            "jour": jour,
            "type_actif": type_actif,
            "morts": morts,
            "vivants": suivant.copy(),
            "mouvements": mouvements,
        })

        atteignable = suivant
        if not atteignable:
            break

    return trace


# ── Boucle de generation avec validation ─────────────────────────────────────

def generer_carte_valide():
    """Genere des cartes jusqu'a en trouver une impossible a gagner."""
    tentatives = 0

    while True:
        tentatives += 1
        carte = generer_carte()
        calendrier = generer_calendrier()
        valide, jour_mort = simuler(carte, calendrier)

        if valide:
            return carte, calendrier, jour_mort, tentatives


# ── Affichage texte ───────────────────────────────────────────────────────────

SEP = "=" * 60
TIRET = "-" * 56


def afficher_carte(carte):
    """Affiche la liste des connexions de la carte."""
    print(f"\n{SEP}")
    print("  CARTE - Connexions entre lieux")
    print(SEP)

    paires = carte.routes_par_paire()
    for (a, b) in sorted(paires):
        types = paires[(a, b)]
        detail = " + ".join(f"Type {t}" for t in types)
        print(f"  Lieu {a} <---> Lieu {b}  |  {len(types)} route(s) : {detail}")

    print()
    print("  Routes speciales vers le Palais :")
    for lieu in LIEUX:
        types_dispo = carte.types_disponibles(lieu)
        types_manquants = set(TYPES_ROUTE) - types_dispo
        if types_manquants:
            manq = ", ".join(str(t) for t in sorted(types_manquants))
            print(f"  Lieu {lieu} ---> Palais  |  Tout-Type (si Type {manq} actif)")
        else:
            print(f"  Lieu {lieu} ---> Palais  |  Tout-Type (toutes routes couvertes)")


def afficher_matrice(carte):
    """Affiche la matrice d'adjacence (types de routes entre chaque paire)."""
    print(f"\n{SEP}")
    print("  MATRICE D'ADJACENCE (types de routes)")
    print(SEP)

    paires = carte.routes_par_paire()

    header = "         "
    for l in LIEUX:
        header += f" Lieu {l} "
    header += " Palais"
    print(header)

    for a in LIEUX:
        ligne = f"  Lieu {a}  "
        for b in LIEUX:
            if a == b:
                ligne += "   .   "
            else:
                cle = (min(a, b), max(a, b))
                types = paires.get(cle, [])
                t_str = ",".join(str(t) for t in types)
                ligne += f"  {t_str:^5s}"
        ligne += "    *  "
        print(ligne)

    print()
    print("  Legende : chiffres = types de route")
    print("            * = route Tout-Type (vers Palais)")
    print("            . = meme lieu")


def afficher_calendrier(calendrier, jour_mort):
    """Affiche le calendrier avec indicateur du jour fatal."""
    print(f"\n{SEP}")
    print("  CALENDRIER - Type de route actif par jour")
    print(SEP)

    noms = {1: " I  ", 2: " II ", 3: "III ", 4: " IV "}

    for i, t in enumerate(calendrier, 1):
        barre = "##" * t
        if i == jour_mort:
            marqueur = "  << MORT INEVITABLE"
        elif i > jour_mort:
            marqueur = "     (non atteint)"
        else:
            marqueur = ""
        print(f"  Jour {i:2d}  |  Type {noms[t]}  |  {barre}{marqueur}")


def afficher_simulation(carte, calendrier, jour_mort):
    """Affiche la trace detaillee de la simulation."""
    print(f"\n{SEP}")
    print("  SIMULATION - Trace des deplacements")
    print(SEP)

    trace = simulation_detaillee(carte, calendrier)

    print(f"\n  Depart : joueurs presents aux Lieux {sorted(LIEUX)}")

    for etape in trace:
        jour = etape["jour"]
        typ = etape["type_actif"]
        morts = etape["morts"]
        vivants = etape["vivants"]
        mouvements = etape["mouvements"]

        print(f"\n  {'~' * 48}")
        print(f"  Jour {jour} - Route Type {typ} active")
        print(f"  {'~' * 48}")

        for src, dests in sorted(mouvements.items()):
            d_str = ", ".join(f"Lieu {d}" for d in sorted(dests))
            print(f"    Lieu {src} -> {d_str}  (Type {typ})")

        for m in sorted(morts):
            print(f"    Lieu {m} -> PALAIS  (aucune route Type {typ} disponible)")

        if vivants:
            v_str = ", ".join(f"Lieu {l}" for l in sorted(vivants))
            print(f"    -- Survivants : {v_str}")
        else:
            print(f"    -- TOUS LES JOUEURS SONT AU PALAIS --")

    print(f"\n  {TIRET}")
    print(f"  Analyse par position de depart :")
    for lieu in LIEUX:
        jour = simuler_depuis(carte, calendrier, lieu)
        if jour:
            print(f"    Depart Lieu {lieu} : mort inevitable au jour {jour}")
        else:
            print(f"    Depart Lieu {lieu} : survie possible (!)")
    print(f"  {TIRET}")


# ══════════════════════════════════════════════════════════════════════════════
#  VISUALISATION (matplotlib)
# ══════════════════════════════════════════════════════════════════════════════

# Couleurs par type de route
COULEURS_TYPE = {
    1: "#FF4757",   # Rouge
    2: "#2ED573",   # Vert
    3: "#1E90FF",   # Bleu
    4: "#FFA502",   # Orange
}

NOMS_ROMAINS = {1: "I", 2: "II", 3: "III", 4: "IV"}

# Positions fixes des noeuds (carre + palais en bas)
POS = {
    1: np.array([-1.5,  1.5]),
    2: np.array([ 1.5,  1.5]),
    3: np.array([-1.5, -0.6]),
    4: np.array([ 1.5, -0.6]),
    5: np.array([ 0.0, -2.9]),
}

NODE_R   = 0.32   # rayon des noeuds 1-4
PALACE_R = 0.44   # rayon du Palais
CURVE    = 0.45   # courbure des aretes doubles


# ── Utilitaires de dessin ─────────────────────────────────────────────────────

def _shorten(pa, pb, ra, rb):
    """Raccourcit un segment pour ne pas chevaucher les cercles des noeuds."""
    d = pb - pa
    length = np.linalg.norm(d)
    if length < ra + rb:
        return pa, pb
    u = d / length
    return pa + u * ra, pb - u * rb


def _bezier_points(pa, pb, offset, n=80):
    """Points d'une courbe de Bezier quadratique avec decalage lateral."""
    mid = (pa + pb) / 2.0
    d = pb - pa
    length = np.linalg.norm(d)
    normal = np.array([-d[1], d[0]]) / length
    ctrl = mid + normal * offset

    t = np.linspace(0, 1, n).reshape(-1, 1)
    pts = (1 - t) ** 2 * pa + 2 * (1 - t) * t * ctrl + t ** 2 * pb
    return pts


def _draw_edge(ax, pa, pb, color, offset=0, lw=3.0):
    """Trace une arete (droite ou courbee) et retourne son point central."""
    if offset == 0:
        ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                color=color, linewidth=lw, alpha=0.75,
                solid_capstyle="round", zorder=2)
        return (pa + pb) / 2.0
    else:
        pts = _bezier_points(pa, pb, offset)
        ax.plot(pts[:, 0], pts[:, 1],
                color=color, linewidth=lw, alpha=0.75,
                solid_capstyle="round", zorder=2)
        return pts[len(pts) // 2]


def _draw_badge(ax, pos, type_route):
    """Petit cercle colore avec le numero du type de route."""
    c = plt.Circle(pos, 0.17, facecolor=COULEURS_TYPE[type_route],
                   edgecolor="white", linewidth=1.5, zorder=8)
    ax.add_patch(c)
    ax.text(pos[0], pos[1], str(type_route),
            ha="center", va="center",
            fontsize=9, fontweight="bold", color="white", zorder=9)


# ── Panneau : Graphe ──────────────────────────────────────────────────────────

def _dessiner_graphe(ax, carte):
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-4.2, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")

    paires = carte.routes_par_paire()

    # ---- Aretes en pointilles vers le Palais ----
    for lieu in LIEUX:
        pa, pb = _shorten(POS[lieu], POS[5], NODE_R, PALACE_R)
        ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                color="#555555", linewidth=1.3, linestyle="--",
                alpha=0.45, zorder=1)
        # petite fleche au bout
        d = POS[5] - POS[lieu]
        u = d / np.linalg.norm(d)
        ax.annotate("", xy=tuple(pb), xytext=tuple(pb - u * 0.18),
                     arrowprops=dict(arrowstyle="-|>", color="#555555",
                                     lw=1.3, mutation_scale=12),
                     zorder=1)

    # ---- Aretes entre lieux 1-4 ----
    for (a, b), types in paires.items():
        pa_full, pb_full = POS[a], POS[b]
        pa, pb = _shorten(pa_full, pb_full, NODE_R, NODE_R)

        if len(types) == 1:
            mid = _draw_edge(ax, pa, pb, COULEURS_TYPE[types[0]])
            _draw_badge(ax, mid, types[0])
        else:
            mid1 = _draw_edge(ax, pa, pb, COULEURS_TYPE[types[0]], offset=CURVE)
            _draw_badge(ax, mid1, types[0])
            mid2 = _draw_edge(ax, pa, pb, COULEURS_TYPE[types[1]], offset=-CURVE)
            _draw_badge(ax, mid2, types[1])

    # ---- Noeuds 1-4 ----
    for lieu in LIEUX:
        x, y = POS[lieu]
        types_dispo = carte.types_disponibles(lieu)

        # halo
        ax.add_patch(plt.Circle((x, y), NODE_R + 0.09,
                                color="#5DADE2", alpha=0.12, zorder=3))
        # cercle
        ax.add_patch(plt.Circle((x, y), NODE_R,
                                facecolor="#1A5276", edgecolor="#5DADE2",
                                linewidth=2.5, zorder=4))
        # numero
        ax.text(x, y, str(lieu), ha="center", va="center",
                fontsize=18, fontweight="bold", color="white", zorder=5)
        # label
        ax.text(x, y - NODE_R - 0.18, f"Lieu {lieu}",
                ha="center", va="top",
                fontsize=9, color="#AEB6BF", zorder=5)

        # indicateurs de types disponibles (4 petits ronds sous le label)
        dot_y = y - NODE_R - 0.48
        for j, t in enumerate(TYPES_ROUTE):
            dot_x = x + (j - 1.5) * 0.19
            available = t in types_dispo
            c = COULEURS_TYPE[t] if available else "#333333"
            a = 0.9 if available else 0.25
            ax.add_patch(plt.Circle((dot_x, dot_y), 0.065,
                                    facecolor=c, edgecolor="none",
                                    alpha=a, zorder=5))

    # ---- Palais ----
    px, py = POS[5]
    ax.add_patch(plt.Circle((px, py), PALACE_R + 0.12,
                            color="#E74C3C", alpha=0.12, zorder=3))
    ax.add_patch(plt.Circle((px, py), PALACE_R,
                            facecolor="#78281F", edgecolor="#E74C3C",
                            linewidth=3, zorder=4))
    ax.text(px, py + 0.05, "5", ha="center", va="center",
            fontsize=20, fontweight="bold", color="white", zorder=5)
    ax.text(px, py - PALACE_R - 0.22, "PALAIS  (Mort)",
            ha="center", va="top",
            fontsize=11, fontweight="bold", color="#E74C3C", zorder=5)

    # ---- Legende ----
    handles = [mpatches.Patch(color=COULEURS_TYPE[t], label=f"Route Type {t}")
               for t in TYPES_ROUTE]
    handles.append(plt.Line2D([0], [0], color="#555555", linestyle="--",
                              linewidth=1.3, label="Tout-Type -> Palais"))
    ax.legend(handles=handles, loc="upper left", fontsize=9,
              facecolor="#16213E", edgecolor="#333333", labelcolor="white",
              framealpha=0.92)

    ax.set_title("Carte du Jeu", fontsize=16, fontweight="bold",
                 color="white", pad=15)


# ── Panneau : Calendrier ─────────────────────────────────────────────────────

def _dessiner_calendrier_img(ax, calendrier, jour_mort):
    ax.axis("off")
    n = len(calendrier)
    ax.set_xlim(-0.8, 3.0)
    ax.set_ylim(-0.5, n + 0.8)

    for i, t in enumerate(calendrier):
        jour = i + 1
        y = n - 1 - i  # jour 1 en haut

        alpha = 1.0 if jour <= jour_mort else 0.2
        color = COULEURS_TYPE[t]

        # barre coloree
        rect = plt.Rectangle((0.6, y + 0.08), 1.6, 0.84,
                              facecolor=color, alpha=alpha,
                              edgecolor="#0D1117", linewidth=2, zorder=2)
        ax.add_patch(rect)

        # bordure rouge jour fatal
        if jour == jour_mort:
            bord = plt.Rectangle((0.53, y + 0.01), 1.74, 0.98,
                                 facecolor="none", edgecolor="#FF0000",
                                 linewidth=3.5, zorder=3, linestyle="-")
            ax.add_patch(bord)
            ax.text(2.45, y + 0.5, "MORT", ha="left", va="center",
                    fontsize=8, fontweight="bold", color="#FF4757", zorder=4)

        # label jour
        c_txt = "white" if jour <= jour_mort else "#444444"
        ax.text(0.25, y + 0.5, f"J{jour:>2d}", ha="center", va="center",
                fontsize=10, fontweight="bold", color=c_txt, zorder=4)

        # label type
        ax.text(1.4, y + 0.5, NOMS_ROMAINS[t], ha="center", va="center",
                fontsize=13, fontweight="bold", color="white",
                alpha=alpha, zorder=4)

    ax.set_title("Calendrier", fontsize=14, fontweight="bold",
                 color="white", pad=12)


# ── Panneau : Simulation ─────────────────────────────────────────────────────

def _dessiner_simulation_img(ax, carte, calendrier, jour_mort):
    ax.axis("off")

    trace = simulation_detaillee(carte, calendrier)
    nb_cols = jour_mort + 1   # jour 0 (depart) + jours 1..jour_mort

    cw = min(1.0, 8.0 / nb_cols)   # largeur de cellule adaptative
    ch = 0.72

    ax.set_xlim(-1.2, nb_cols * cw + 1.0)
    ax.set_ylim(-2.8, 4 * ch + 1.6)

    # construire la grille vivant/mort
    alive = [[False] * nb_cols for _ in range(4)]
    for i in range(4):
        alive[i][0] = True          # jour 0 : tout le monde vivant
    for step in trace:
        j = step["jour"]
        if j >= nb_cols:
            break
        for i, lieu in enumerate(LIEUX):
            alive[i][j] = lieu in step["vivants"]

    # dessiner les cellules
    for i in range(4):
        y = (3 - i) * ch
        for j in range(nb_cols):
            x = j * cw
            if alive[i][j]:
                fc, txt, tc = "#27AE60", "V", "white"
            else:
                fc, txt, tc = "#2C3E50", "X", "#E74C3C"

            rect = plt.Rectangle((x + 0.04, y + 0.04),
                                 cw - 0.08, ch - 0.08,
                                 facecolor=fc, edgecolor="#0D1117",
                                 linewidth=2, zorder=2)
            ax.add_patch(rect)
            ax.text(x + cw / 2, y + ch / 2, txt,
                    ha="center", va="center",
                    fontsize=9, fontweight="bold", color=tc, zorder=3)

    # labels lignes (lieux)
    for i, lieu in enumerate(LIEUX):
        y = (3 - i) * ch
        ax.text(-0.2, y + ch / 2, f"L{lieu}",
                ha="right", va="center",
                fontsize=10, fontweight="bold", color="white")

    # labels colonnes (jours)
    for j in range(nb_cols):
        x = j * cw
        label = "Dep" if j == 0 else f"J{j}"
        ax.text(x + cw / 2, 4 * ch + 0.35, label,
                ha="center", va="center",
                fontsize=8, fontweight="bold", color="#AEB6BF")

    # legende heatmap
    ax.text(nb_cols * cw + 0.4, 3 * ch + ch / 2, "V = vivant",
            fontsize=8, color="#27AE60", va="center")
    ax.text(nb_cols * cw + 0.4, 2 * ch + ch / 2, "X = mort",
            fontsize=8, color="#E74C3C", va="center")

    # analyse par position de depart
    y_text = -0.6
    ax.text(0, y_text, "Analyse par depart :",
            fontsize=9, fontweight="bold", color="white")
    y_text -= 0.5
    for lieu in LIEUX:
        jour = simuler_depuis(carte, calendrier, lieu)
        if jour is not None:
            ax.text(0, y_text,
                    f"  Lieu {lieu}  ->  mort jour {jour}",
                    fontsize=9, color="#E74C3C")
        else:
            ax.text(0, y_text,
                    f"  Lieu {lieu}  ->  survie possible",
                    fontsize=9, color="#2ED573")
        y_text -= 0.45

    ax.set_title("Simulation  (V = vivant, X = mort)",
                 fontsize=14, fontweight="bold", color="white", pad=12)


# ── Fonction principale d'image ───────────────────────────────────────────────

def generer_image(carte, calendrier, jour_mort, chemin):
    """Genere une image complete : graphe + calendrier + simulation."""
    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)

    fig = plt.figure(figsize=(22, 12))
    fig.patch.set_facecolor("#0D1117")

    gs = fig.add_gridspec(2, 5, hspace=0.45, wspace=0.5,
                          left=0.02, right=0.98, top=0.90, bottom=0.06)

    ax_graph = fig.add_subplot(gs[:, 0:3])    # gauche : graphe
    ax_cal   = fig.add_subplot(gs[0, 3:])     # haut-droite : calendrier
    ax_sim   = fig.add_subplot(gs[1, 3:])     # bas-droite  : simulation

    for ax in (ax_graph, ax_cal, ax_sim):
        ax.set_facecolor("#16213E")
        for spine in ax.spines.values():
            spine.set_visible(False)

    _dessiner_graphe(ax_graph, carte)
    _dessiner_calendrier_img(ax_cal, calendrier, jour_mort)
    _dessiner_simulation_img(ax_sim, carte, calendrier, jour_mort)

    # titre principal
    fig.suptitle(
        "GENERATEUR PROCEDURAL  —  Tous les chemins menent au Palais",
        fontsize=22, fontweight="bold", color="white", y=0.96)

    # bandeau resultat en bas
    fig.text(0.5, 0.015,
             f"Mort inevitable au jour {jour_mort}/{MAX_JOURS}"
             f"  —  La map est IMPOSSIBLE a gagner",
             ha="center", va="center", fontsize=15, fontweight="bold",
             color="#E74C3C",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#1A1A2E",
                       edgecolor="#E74C3C", linewidth=2))

    fig.savefig(chemin, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"\n  Image sauvegardee : {chemin}")


def normaliser_chemin_export(chemin_sortie):
    """
    Normalise le chemin d'export.

    Si l'utilisateur fournit un dossier, le fichier `map.png` est ajoute.
    Si aucun chemin n'est fourni, on utilise `exports/map.png`.
    """
    if not chemin_sortie:
        chemin_sortie = os.path.join("exports", "map.png")

    chemin_sortie = os.path.expanduser(chemin_sortie)

    if os.path.isdir(chemin_sortie):
        return os.path.join(chemin_sortie, "map.png")

    _, extension = os.path.splitext(chemin_sortie)
    if not extension:
        return os.path.join(chemin_sortie, "map.png")

    return chemin_sortie


def choisir_chemin_export(chemin_defaut):
    """
    Ouvre une boite de dialogue pour choisir le fichier d'export.

    Si la selection graphique est indisponible ou annulee, le chemin
    par defaut est conserve.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("\n  Selection graphique indisponible : tkinter n'est pas disponible.")
        return chemin_defaut

    initial_dir = os.path.dirname(chemin_defaut) or os.getcwd()
    initial_file = os.path.basename(chemin_defaut) or "map.png"

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        chemin = filedialog.asksaveasfilename(
            title="Choisir l'emplacement d'exportation de l'image",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".png",
            filetypes=[
                ("Image PNG", "*.png"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        root.destroy()
    except Exception as exc:
        print("\n  Impossible d'ouvrir la selection graphique.")
        print(f"  Export par defaut conserve : {chemin_defaut}")
        print(f"  Detail : {exc}")
        return chemin_defaut

    if not chemin:
        print("\n  Aucun emplacement selectionne.")
        print(f"  Export par defaut conserve : {chemin_defaut}")
        return chemin_defaut

    if not os.path.splitext(chemin)[1]:
        chemin += ".png"

    return chemin


def analyser_arguments():
    """Analyse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description=(
            "Genere une carte procedurale impossible a gagner et exporte "
            "une image de synthese."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Chemin d'export de l'image. Vous pouvez fournir un fichier "
            "(ex: exports/map.png) ou un dossier (ex: exports). "
            "Si l'option est omise, une fenetre de selection s'ouvre."
        ),
    )
    return parser.parse_args()


# ── Point d'entree ────────────────────────────────────────────────────────────

def main():
    args = analyser_arguments()
    chemin_image = normaliser_chemin_export(args.output)
    if args.output:
        print(f"\n  Export configure par argument : {chemin_image}")
    else:
        print("\n  Ouverture de la selection d'emplacement pour l'image...")
        chemin_image = choisir_chemin_export(chemin_image)

    print(f"\n{SEP}")
    print("  GENERATEUR PROCEDURAL DE MAP")
    print("  Jeu Strategique - Tous les chemins menent au Palais")
    print(SEP)

    print("\n  Generation en cours...")

    carte, calendrier, jour_mort, tentatives = generer_carte_valide()

    print(f"  Carte valide trouvee en {tentatives} tentative(s) !\n")

    # Affichage console
    afficher_carte(carte)
    afficher_matrice(carte)
    afficher_calendrier(calendrier, jour_mort)
    afficher_simulation(carte, calendrier, jour_mort)

    print(f"\n{SEP}")
    print(f"  RESULTAT FINAL")
    print(f"  Mort inevitable de TOUS les joueurs au jour : {jour_mort}/{MAX_JOURS}")
    print(f"  La map est IMPOSSIBLE a gagner.")
    print(f"{SEP}\n")

    # Generation de l'image
    generer_image(carte, calendrier, jour_mort, chemin_image)


if __name__ == "__main__":
    main()
