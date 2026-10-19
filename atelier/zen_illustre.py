"""La pièce de Tiny Studio, dessinée en code : les murs, le sol, les cinq meubles de la wishlist
(dressing, bibliothèque, étagères déco, coiffeuse, coffre), le fauteuil, la table d'appoint et la
déco : rideaux, guirlande, tapis, cactus, et quelques objets (tri du 19 octobre 2026). Seuls les choix retenus par Pauline sont gardés ; les variantes essayées vivent dans
l'historique Git (ménage du 18 octobre 2026).

La direction artistique, niveau 3, « plus mignon » : le réalisme vient des proportions et des
matières, le côté mignon des formes (des meubles trapus, un bois épais, des angles très ronds,
des pieds en galette), l'illustration du rendu : des aplats à trois tons par volume, une seule
lumière venue de la droite (la fenêtre), des reflets en traits interrompus, quelques traits de
veinage, un léger tremblé, aucun contour noir.

Repère et projection : x longe le mur de droite (plan y = 0), y longe le mur de gauche (plan
x = 0), z monte. Une face tournée vers +x reçoit la lumière ; une face tournée vers +y est à
l'ombre.
"""
import math
import random

C30 = math.cos(math.radians(30))
S, OX, OY = 30, 390, 318


def p(x, y, z):
    return (OX + (x - y) * C30 * S, OY + (x + y) * 0.5 * S - z * S)


# ---------- Le dessin à la main ----------

def tremble(pt, force=0.35):
    """Un léger tremblé de main, toujours le même pour un même point de l'écran : deux faces qui
    partagent une arête tremblent ensemble, sans jour entre elles."""
    r = random.Random(hash((round(pt[0] * 2), round(pt[1] * 2))))
    return (pt[0] + r.uniform(-force, force), pt[1] + r.uniform(-force, force))


def chemin(pts, r=0.0, bombe=0.0):
    """Un contour aux angles arrondis de r pixels, aux côtés qui peuvent bomber vers l'extérieur."""
    n = len(pts)
    cx = sum(q[0] for q in pts) / n
    cy = sum(q[1] for q in pts) / n

    def vers(a, b, d):
        lg = math.dist(a, b) or 1
        t = min(d / lg, 0.45)
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    entree = [vers(pts[i], pts[i - 1], r) for i in range(n)]
    sortie = [vers(pts[i], pts[(i + 1) % n], r) for i in range(n)]
    d = [f"M{sortie[0][0]:.1f} {sortie[0][1]:.1f}"]
    for k in range(1, n + 1):
        i = k % n
        a, b = sortie[i - 1], entree[i]
        if bombe:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ex, ey = b[0] - a[0], b[1] - a[1]
            lg = math.hypot(ex, ey) or 1
            nx, ny = ey / lg, -ex / lg
            if nx * (mx - cx) + ny * (my - cy) < 0:
                nx, ny = -nx, -ny
            f = 2 * bombe * lg
            d.append(f"Q{mx + nx * f:.1f} {my + ny * f:.1f} {b[0]:.1f} {b[1]:.1f}")
        else:
            d.append(f"L{b[0]:.1f} {b[1]:.1f}")
        if r:
            d.append(f"Q{pts[i][0]:.1f} {pts[i][1]:.1f} {sortie[i][0]:.1f} {sortie[i][1]:.1f}")
    return " ".join(d) + " Z"


def face(points3d, couleur, r=0.0, bombe=0.0, extra=""):
    pts = [tremble(p(*q)) for q in points3d]
    return f'<path d="{chemin(pts, r, bombe)}" fill="{couleur}"{extra} />'


def trait(points3d, couleur, largeur=1.2, opacite=1.0):
    pts = [tremble(p(*q), 0.25) for q in points3d]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join(f"L{q[0]:.1f} {q[1]:.1f}" for q in pts[1:])
    return (f'<path d="{d}" fill="none" stroke="{couleur}" stroke-width="{largeur}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacite}" />')


def courbe(a, b, creux, couleur, largeur=1.0, opacite=0.55):
    """Un trait de veinage : une courbe douce, creusée de `creux` pixels."""
    a, b = p(*a), p(*b)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ex, ey = b[0] - a[0], b[1] - a[1]
    lg = math.hypot(ex, ey) or 1
    cx, cy = mx + ey / lg * creux, my - ex / lg * creux
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{cx:.1f} {cy:.1f} {b[0]:.1f} {b[1]:.1f}" fill="none" '
            f'stroke="{couleur}" stroke-width="{largeur}" stroke-linecap="round" opacity="{opacite}" />')


def boite(x0, x1, y0, y1, z0, z1, t, r=0.0, bombe=0.0, penche=0.0):
    """Un volume : sa silhouette arrondie dans le ton d'ombre, qui porte la rondeur et le bombé,
    puis ses trois faces visibles en aplat. t : (dessus, face tournée vers +x, face tournée vers +y)."""
    s = penche
    cote = [(x0, y1, z0), (x1, y1, z0), (x1, y1 + s, z1), (x0, y1 + s, z1)]
    avant = [(x1, y0, z0), (x1, y1, z0), (x1, y1 + s, z1), (x1, y0 + s, z1)]
    dessus = [(x0, y0 + s, z1), (x1, y0 + s, z1), (x1, y1 + s, z1), (x0, y1 + s, z1)]
    contour = [(x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y1 + s, z1), (x0, y0 + s, z1), (x1, y0 + s, z1)]
    rf = r * 0.45
    return face(contour, t[2], r, bombe) + face(cote, t[2], rf) + face(avant, t[1], rf) + face(dessus, t[0], rf)


OMBRES = []  # les ombres au sol, peintes avant tous les objets debout
OMBRES_MUR = []  # les ombres douces sur le mur de gauche, à côté des meubles hauts


def ombre_portee(x0, x1, y0, y1, hauteur=2.0, opacite=0.2):
    """L'ombre au sol d'un meuble, rejetée vers +y (à l'écran, vers la gauche) par la lumière de la
    fenêtre, en deux couches : une ombre de contact dense, juste au pied, et une ombre portée plus
    légère qui s'allonge avec la hauteur du meuble (revu le 19 octobre 2026). Elle est mise de côté
    et peinte avec les autres ombres, sous tous les objets : elle ne tombe que sur le sol."""
    longueur = 0.2 + 0.22 * hauteur
    # L'ombre portée suit le moment : le jour, la lumière de la fenêtre ; le soir, un soleil bas qui
    # l'allonge et l'adoucit ; la nuit, elle disparaît (la lumière vient des lampes et de la guirlande)
    OMBRES.append('<g class="vue vue-jour">' + ombre_sol_brute(x0, x1, y0, y1, longueur, opacite * 0.8) + '</g>'
                  + '<g class="vue vue-soir">' + ombre_sol_brute(x0, x1, y0, y1, longueur * 1.8, opacite * 0.65) + '</g>')
    OMBRES.append(ombre_sol_brute(x0 + 0.04, x1 - 0.02, y0 + 0.02, y1, 0.12, opacite * 0.9))
    return ""


def ombre_mur(y_bord, hauteur, profondeur=0.9, opacite=0.07):
    """L'ombre douce d'un meuble haut adossé au mur de gauche, posée sur le mur juste à côté de lui,
    côté +y (à l'écran, à sa gauche) : la lumière de la fenêtre arrive de l'autre côté."""
    pts = [(0.006, y_bord, 0), (0.006, y_bord + profondeur, 0), (0.006, y_bord + profondeur * 0.45, hauteur), (0.006, y_bord, hauteur)]
    OMBRES_MUR.append('<g class="ombre-mur">' + face(pts, "#5A3A26", r=10, extra=f' opacity="{opacite * 1.9:.3f}"') + '</g>')
    return ""


def ombre_ellipse(cx, cy, rx, ry, opacite):
    """L'ombre ronde d'un objet posé, mise de côté comme les autres. Elle part vers +y, loin de la
    fenêtre : à l'écran, vers le bas à gauche de l'objet (revu le 19 octobre 2026)."""
    cx, cy = cx - rx * 0.28, cy + ry * 0.3
    OMBRES.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{OMBRE}" opacity="{opacite}" />')
    return ""


def ombre_posee(cx, cy, rx, ry, opacite):
    """L'ombre d'un objet posé sur un meuble : dessinée sur place, sur le plateau, et décalée vers +y
    (à l'écran, vers le bas à gauche), comme les ombres du sol."""
    return f'<ellipse cx="{cx - rx * 0.28:.1f}" cy="{cy + ry * 0.3:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{OMBRE}" opacity="{opacite}" />'


def ombre_sol_brute(x0, x1, y0, y1, decalage, opacite):
    return face([(x0, y0, 0), (x1 + 0.1, y0, 0), (x1 + 0.1, y1 + decalage, 0), (x0, y1 + decalage, 0)],
                "#6E4426", r=9, extra=f' opacity="{opacite}"')


def disque(points_cercle, couleur, extra=""):
    pts = [p(*q) for q in points_cercle]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join(f"L{q[0]:.1f} {q[1]:.1f}" for q in pts[1:]) + " Z"
    return f'<path d="{d}" fill="{couleur}"{extra} />'


def cercle_y(xc, yc, zc, r, n=40):
    """Un cercle debout dans un plan y = constante (un miroir contre le mur de droite)."""
    return [(xc + r * math.cos(2 * math.pi * k / n), yc, zc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


# ---------- Les matières : une palette courte, choisie à la main ----------

OMBRE = "#6E4426"


# ---------- Les formes du niveau 3 ----------
# r, rp : rondeur des angles des grands et des petits volumes, en pixels ; pl : épaisseur du bois ;
# tasse : tassement des meubles ; pied : hauteur des pieds ; bombe : bombé des
# silhouettes ; ep : épaisseur des tablettes ; montant : section des pieds de table.

N = dict(r=11.0, rp=5.0, pl=0.32, tasse=0.84, pied=0.34, pied_rond=True, bombe=0.012, cases=2,
         livre=(0.25, 0.34), livre_h_max=1.55, r_livre=5.0, plante="ronde", ep_cor=0.3, cor=0.18,
         ep=0.28, montant=0.32, tabouret=0.22)  # le niveau 3, « plus mignon », retenu par Pauline le 16 octobre 2026


def pied(px, py, haut, bois, demi=0.13):
    """Un pied de meuble : une galette ronde."""
    bx, by = p(px, py, 0)
    rx, ry = 1.2247 * 0.2 * S, 0.7071 * 0.2 * S
    hh = haut * S
    return (f'<ellipse cx="{bx:.1f}" cy="{by - hh / 2:.1f}" rx="{rx * 1.05:.1f}" ry="{hh / 2 + ry * 0.6:.1f}" fill="{bois["cote"]}" />'
            f'<ellipse cx="{bx + rx * 0.22:.1f}" cy="{by - hh / 2 - 1:.1f}" rx="{rx * 0.7:.1f}" ry="{hh / 2 + ry * 0.4:.1f}" fill="{bois["face"]}" />')


def tons(bois):
    return (bois["haut"], bois["face"], bois["cote"])


# Les couvertures : l'harmonie « Touches de cobalt », retenue par Pauline le 19 octobre 2026 :
# des neutres, du rose poudré, du kaki, et le cobalt pour seul accent froid
LIVRES = [("#F8F1E1", "#EADDC2", "#CBBC9F"),   # crème
          ("#EBD3AE", "#D9B98A", "#B9976A"),   # sable
          ("#D9DA9A", "#B9BA68", "#97984B"),   # kaki citron
          ("#A9BDF5", "#4A67D8", "#3550B4"),   # cobalt
          ("#F6D3DA", "#E9B5BE", "#C98F9B"),   # rose poudré
          ("#D9AE8B", "#B9875F", "#93603F"),   # noyer clair
          ("#D7E2F7", "#B3C6EE", "#8EA5D6")]   # bleu ciel
FEUILLE = dict(clair="#A3C77F", fonce="#6F9A55", nervure="#DCEFC0")
POT = dict(clair="#F6E9D3", ombre="#DCC3A0", bord="#FCF4E6")
TERRE_CUITE = dict(clair="#EBA383", ombre="#C97D5D", bord="#F5C3A6")
LINGE = ("#FAF4E8", "#EFE5D3", "#D9CCB4")
VERRE = "#DCE7EA"


# ---------- Les petits objets ----------


def feuille(bx, by, angle, longueur, largeur):
    """Une feuille pointue en deux tons, avec sa nervure claire."""
    a = math.radians(angle)
    dx, dy = math.sin(a), -math.cos(a)
    tx, ty = bx + dx * longueur, by + dy * longueur
    nx, ny = -dy, dx
    mx, my = bx + dx * longueur * 0.5, by + dy * longueur * 0.5
    c1 = (mx + nx * largeur, my + ny * largeur)
    c2 = (mx - nx * largeur, my - ny * largeur)
    return (f'<path d="M{bx:.1f} {by:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {bx:.1f} {by:.1f} Z" fill="{FEUILLE["clair"]}" />'
            f'<path d="M{bx:.1f} {by:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {tx:.1f} {ty:.1f} Z" fill="{FEUILLE["fonce"]}" />'
            f'<path d="M{bx:.1f} {by:.1f} Q{mx + nx * largeur * 0.15:.1f} {my + ny * largeur * 0.15:.1f} {tx:.1f} {ty:.1f}" '
            f'fill="none" stroke="{FEUILLE["nervure"]}" stroke-width="0.9" stroke-linecap="round" opacity="0.8" />')


def pot(sx, sy, w, h, POT=POT):
    """Un pot de céramique, crème par défaut, vu de biais : ombre à gauche, lumière à droite, bord clair."""
    bas = w * 0.38
    base_y = sy - h
    return (f'<path d="M{sx - w / 2:.1f} {base_y:.1f} L{sx + w / 2:.1f} {base_y:.1f} L{sx + bas:.1f} {sy - 3:.1f} '
            f'Q{sx + bas:.1f} {sy:.1f} {sx + bas - 3:.1f} {sy:.1f} L{sx - bas + 3:.1f} {sy:.1f} Q{sx - bas:.1f} {sy:.1f} {sx - bas:.1f} {sy - 3:.1f} Z" fill="{POT["ombre"]}" />'
            f'<path d="M{sx - w * 0.1:.1f} {base_y:.1f} L{sx + w / 2:.1f} {base_y:.1f} L{sx + bas:.1f} {sy - 3:.1f} '
            f'Q{sx + bas:.1f} {sy:.1f} {sx + bas - 3:.1f} {sy:.1f} L{sx - bas * 0.1:.1f} {sy:.1f} Z" fill="{POT["clair"]}" />'
            f'<rect x="{sx - w / 2 - 1.5:.1f}" y="{base_y - 2.5:.1f}" width="{w + 3:.1f}" height="{max(4, h * 0.2):.1f}" rx="2.5" fill="{POT["bord"]}" />'
            f'<path d="M{sx + w * 0.3:.1f} {base_y + 5:.1f} L{sx + w * 0.26:.1f} {sy - 5:.1f}" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity="0.6" />')


def parquet():
    """Le parquet du Zen, en aplat : de larges lames de bois miel clair posées en quinconce, trois
    tons tirés au hasard, des joints fins, et quelques traits de veinage."""
    W, D = 12, 12
    tons_lames = M("parquet")[:3]  # selon l'ensemble : miel doux, ou plus foncé
    rng = random.Random(12)
    out = [face([(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0)], tons_lames[0])]
    largeur = 0.75
    rang = 0
    y = 0.0
    while y < D - 0.01:
        y2 = min(y + largeur, D)
        x = -rng.uniform(0.5, 2.5) if rang % 2 else -rng.uniform(1.5, 3.0)
        while x < W:
            x2 = min(x + rng.uniform(2.6, 4.2), W)
            xa = max(x, 0)
            if x2 - xa > 0.05:
                out.append(face([(xa, y, 0), (x2, y, 0), (x2, y2, 0), (xa, y2, 0)], rng.choice(tons_lames)))
                out.append(trait([(x2, y + 0.02, 0), (x2, y2 - 0.02, 0)], M("parquet")[3], 1.0, 0.8))
                if rng.random() < 0.45:
                    xg = xa + (x2 - xa) * rng.uniform(0.2, 0.5)
                    out.append(courbe((xg, y + largeur * 0.4, 0), (min(xg + 1.1, x2 - 0.1), y + largeur * 0.45, 0), rng.uniform(-1.5, 1.5), M("parquet")[4], 0.9, 0.5))
            x = x2
        out.append(trait([(0, y2, 0), (W, y2, 0)], M("parquet")[3], 1.0, 0.85))
        y = y2
        rang += 1
    # L'ombre douce au pied des murs, en aplat
    out.append(face([(0, 0, 0), (W, 0, 0), (W, 0.45, 0), (0, 0.45, 0)], OMBRE, extra=' opacity="0.08"'))
    out.append(face([(0, 0, 0), (0.45, 0, 0), (0.45, D, 0), (0, D, 0)], OMBRE, extra=' opacity="0.1"'))
    return "".join(out)


# ---------- La coiffeuse ----------


def coiffeuse(meuble, badge):
    """La coiffeuse, contre le mur de droite, en teck : un bois blond et chaud qui ressort sur le
    bordeaux, une table à un tiroir, un miroir rond cerclé de chrome, une marguerite et un flacon de parfum ;
    devant, un tabouret au coussin léopard."""
    B = M("droite")  # en teck jusqu'au 17 octobre 2026, puis en laque crème
    x0, x1, y0, y1 = 8.95, 11.65, 0.1, 1.3
    z_plateau, ep = 2.3 - 1.4 * (1 - N["tasse"]), N["ep"]
    out = [ombre_portee(x0, x1, y0, y1 + 1.4, 2.4)]
    # Le miroir, contre le mur, derrière la table
    xm, ym, zm, rm = (x0 + x1) / 2, 0.3, z_plateau + ep + 1.35, 0.92
    for px in (xm - 0.75, xm + 0.75):
        out.append(boite(px - 0.09, px + 0.09, ym - 0.09, ym + 0.09, z_plateau + ep, zm + 0.2, tons(B), r=3))
    out.append(disque(cercle_y(xm, ym, zm, rm + 0.14), "#8E959D"))
    out.append(disque(cercle_y(xm + 0.03, ym + 0.01, zm + 0.02, rm + 0.08), CHROME))
    out.append(disque(cercle_y(xm, ym + 0.02, zm, rm - 0.02), VERRE))
    a, b = p(xm + 0.15, ym + 0.03, zm + 0.45), p(xm + 0.55, ym + 0.03, zm + 0.05)
    out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.8" />')
    a, b = p(xm + 0.05, ym + 0.03, zm + 0.1), p(xm + 0.25, ym + 0.03, zm - 0.1)
    out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.7" />')
    # Les pieds, la ceinture et son tiroir, le plateau
    g = N["montant"]
    for (px, py) in ((x0 + 0.15, y0 + 0.15), (x1 - 0.15 - g, y0 + 0.15), (x0 + 0.15, y1 - 0.15 - g), (x1 - 0.15 - g, y1 - 0.15 - g)):
        out.append(boite(px, px + g, py, py + g, 0, z_plateau - 0.3, tons(B), r=N["rp"] + 3))
    out.append(boite(x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, z_plateau - 0.62, z_plateau, tons(B), r=N["rp"] + 1))
    yf = y1 - 0.1 + 0.005
    out.append(face([(x0 + 0.5, yf, z_plateau - 0.55), (x1 - 0.5, yf, z_plateau - 0.55), (x1 - 0.5, yf, z_plateau - 0.08), (x0 + 0.5, yf, z_plateau - 0.08)], B["haut"], r=3))
    # Le bouton du tiroir, rond, en bois (en chrome jusqu'au 17 octobre 2026)
    out.append(bouton((x0 + x1) / 2, yf + 0.02, z_plateau - 0.31, (B["cote"], B["face"], B["reflet"]), rayon=4.4))
    out.append(boite(x0 - 0.06, x1 + 0.06, y0, y1 + 0.06, z_plateau, z_plateau + ep, tons(B), r=N["r"] - 1, bombe=N["bombe"]))
    zh = z_plateau + ep
    out.append(trait([(x0 + 0.2, y1 + 0.03, zh), (x0 + 1.6, y1 + 0.03, zh)], B["reflet"], 2.2))
    out.append(trait([(x0 + 1.9, y1 + 0.03, zh), (x1 - 0.2, y1 + 0.03, zh)], B["reflet"], 2.2))
    out.append(trait([(x1 + 0.05, y0 + 0.2, zh), (x1 + 0.05, y1 - 0.1, zh)], B["reflet"], 2.0, 0.9))
    out.append(pot_fleur(x1 - 0.45, (y0 + y1) / 2, zh, 1.2))  # à la place des fleurs séchées (18 octobre 2026)
    out.append(flacon_parfum(x0 + 0.7, (y0 + y1) / 2 + 0.1, zh))  # à la place du plateau rose (19 octobre 2026)
    # Le tabouret, devant
    tx0, tx1, ty0, ty1 = 9.75, 10.85, 1.75, 2.65
    gt = N["tabouret"] + 0.06
    for (px, py) in ((tx0 + 0.08, ty0 + 0.08), (tx1 - 0.08 - gt, ty0 + 0.08), (tx0 + 0.08, ty1 - 0.08 - gt), (tx1 - 0.08 - gt, ty1 - 0.08 - gt)):
        out.append(boite(px, px + gt, py, py + gt, 0, 1.1, tons(B), r=N["rp"] + 2))
    out.append(boite(tx0, tx1, ty0, ty1, 1.1, 1.26, tons(B), r=N["rp"] + 1))
    out.append(boite_tissu(tx0 + 0.04, tx1 - 0.04, ty0 + 0.04, ty1 - 0.04, 1.26, 1.58, r=N["r"] + 3, bombe=0.03 + 2 * N["bombe"],
                           motif="pois", silhouette="#C9879A"))
    out.append(trait([(tx1 - 0.08, ty0 + 0.25, 1.58), (tx1 - 0.08, ty1 - 0.4, 1.58)], "#FFFFFF", 1.8, 0.8))
    out.append(badge("coiffeuse", (x0 + x1) / 2, 0.3, zm + 1.65))
    return meuble("coiffeuse", "".join(out))


# ---------- La fenêtre ----------


FENETRE = dict(xa=3.8, xb=6.8, za=3.5, zb=6.9)


def fenetre():
    """La fenêtre du mur de droite, au-dessus de l'étagère : un ciel doux avec deux nuages, la cime
    d'un arbre dehors, des petits bois, et un cadre de bois en relief qui sort du mur, avec son
    rebord (refait le 19 octobre 2026 : le cadre plat donnait l'impression d'une fenêtre enfoncée
    derrière les rideaux)."""
    xa, xb, za, zb = FENETRE["xa"], FENETRE["xb"], FENETRE["za"], FENETRE["zb"]
    m = 0.2
    B = M("droite")
    out = [face([(xa - m - 0.06, 0.004, za - m - 0.1), (xb + m + 0.1, 0.004, za - m - 0.1), (xb + m + 0.1, 0.004, zb + m - 0.06), (xa - m - 0.06, 0.004, zb + m - 0.06)], "#3B2418", r=N["r"], extra=' opacity="0.08"')]
    out.extend(vues_fenetre(xa, xb, za, zb))
    # On ne garde du feuillage que ce qui est dans la vitre
    vitre = [p(xa, 0.01, za), p(xb, 0.01, za), p(xb, 0.01, zb), p(xa, 0.01, zb)]
    clip = '<clipPath id="vitre-zen"><polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in vitre) + '" /></clipPath>'
    out = [out[0], clip, '<g clip-path="url(#vitre-zen)">'] + out[1:] + ["</g>"]
    # Les petits bois, fins et en retrait (plus de reflets sur la vitre depuis le 19 octobre 2026)
    xm, zm = (xa + xb) / 2, (za + zb) / 2
    out.append(boite(xm - 0.06, xm + 0.06, 0.01, 0.06, za, zb, tons(B), r=1))
    out.append(boite(xa, xb, 0.01, 0.06, zm - 0.06, zm + 0.06, tons(B), r=1))
    # Le cadre en relief : les deux montants, puis la traverse du haut, qui couvre leurs têtes
    ep = 0.16
    out.append(boite(xa - m, xa, 0.0, ep, za, zb, tons(B), r=2))
    out.append(boite(xb, xb + m, 0.0, ep, za, zb, tons(B), r=2))
    out.append(boite(xa - m, xb + m, 0.0, ep, zb, zb + m, tons(B), r=3))
    out.append(trait([(xa - m + 0.1, ep + 0.005, zb + m - 0.04), (xb + m - 0.1, ep + 0.005, zb + m - 0.04)], B["reflet"], 1.6, 0.8))
    out.append(trait([(xb + m + 0.005, 0.03, zb - 0.1), (xb + m + 0.005, 0.03, za + 0.2)], B["reflet"], 1.6, 0.7))
    # Le rebord, qui déborde du cadre
    out.append(boite(xa - 0.35, xb + 0.35, 0.0, 0.34, za - m - 0.2, za, tons(B), r=N["rp"] + 1))
    out.append(trait([(xa - 0.2, 0.32, za), (xb + 0.2, 0.32, za)], B["reflet"], 2.0, 0.9))
    return "".join(out)


def vues_fenetre(xa, xb, za, zb):
    """Ce qu'on voit par la fenêtre, en trois moments, chacun dans son groupe (classes « vue-jour »,
    « vue-soir », « vue-nuit ») : la page n'en montre qu'un, selon l'heure de l'utilisateur.
    Le jour : un ciel bleu pâle, deux nuages blancs, la cime des arbres. Le soir : un ciel pêche et
    rose, le soleil bas, des nuages roses, des arbres plus sombres. La nuit : un ciel bleu nuit, la
    lune en croissant, des étoiles qui scintillent, les arbres en silhouette (19 octobre 2026)."""
    def plat(x, z, rx, ry, couleur, op=1.0, classe=""):
        sx, sy = p(x, 0.015, z)
        c = f' class="{classe}"' if classe else ""
        return f'<ellipse{c} transform="translate({sx:.1f} {sy:.1f}) skewY(30)" rx="{rx:.1f}" ry="{ry:.1f}" fill="{couleur}" opacity="{op}" />'

    def ciel(bas, haut):
        return (face([(xa, 0.01, za), (xb, 0.01, za), (xb, 0.01, zb), (xa, 0.01, zb)], bas, r=N["rp"])
                + face([(xa, 0.012, za + (zb - za) * 0.55), (xb, 0.012, za + (zb - za) * 0.55), (xb, 0.012, zb), (xa, 0.012, zb)], haut, r=N["rp"]))

    def nuages(couleur):
        return "".join(plat(x - 0.25 * k, z, 12 * k, 7 * k, couleur) + plat(x + 0.15 * k, z + 0.12 * k, 14 * k, 9 * k, couleur) + plat(x + 0.55 * k, z, 10 * k, 6 * k, couleur)
                       for (x, z, k) in ((xa + 0.9, zb - 0.8, 1.0), (xb - 0.8, zb - 1.5, 0.8)))

    def arbres(fonce, clair):
        return "".join(plat(x, z, rx, ry, c) for (x, z, rx, ry, c) in ((xa + 0.7, za + 0.55, 22, 18, fonce), (xa + 1.7, za + 0.4, 26, 20, clair),
                                                                       (xb - 0.9, za + 0.5, 24, 19, fonce), (xb - 0.2, za + 0.3, 18, 14, clair)))
    jour = ciel("#D7EAF0", "#C4E0EA") + nuages("#FFFFFF") + arbres("#9DBE83", "#B4CF97")
    soir = (ciel("#F8CDAA", "#EBB0BC") + plat(xb - 1.1, za + 1.35, 22, 22, "#FFE3A0", 0.45) + plat(xb - 1.1, za + 1.35, 13, 13, "#FFD27A")
            + nuages("#FBE0DA") + arbres("#7F9868", "#93A97A"))
    rng = random.Random(7)
    etoiles = "".join(plat(xa + rng.uniform(0.2, xb - xa - 0.2), za + rng.uniform(1.4, zb - za - 0.15), r, r, "#FFF6DA", 0.95, "etoile")
                      for r in [rng.choice((1.1, 1.4, 1.8)) for _ in range(14)])
    lx, lz = xa + 1.0, zb - 0.9
    lune = plat(lx, lz, 16, 16, "#FFF1C4", 0.18) + plat(lx, lz, 9, 9, "#FFF1C4") + plat(lx + 0.18, lz + 0.12, 8, 8, "#2B3966")
    nuit = ciel("#33427A", "#2B3966") + etoiles + lune + arbres("#283F40", "#33504C")
    return [f'<g class="vue vue-jour">{jour}</g>', f'<g class="vue vue-soir">{soir}</g>', f'<g class="vue vue-nuit">{nuit}</g>']


def ambiance(polygones, lueurs=""):
    """Le voile du moment, posé sur les murs ou le sol : chaud et léger le soir, bleu la nuit, avec
    par-dessus, la nuit, les lueurs de la guirlande et de la lampe."""
    def voile(couleur, opacite):
        return "".join(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in poly)}" fill="{couleur}" opacity="{opacite}" />' for poly in polygones)
    return f'<g class="vue vue-soir">{voile("#F39A6B", 0.07)}</g><g class="vue vue-nuit">{voile("#4A2C3A", 0.16)}{lueurs}</g>'


def voilage():
    """Le voilage, à la place des rideaux noués (19 octobre 2026) : deux pans de voile blanc, droits,
    sur une fine tringle de bois, en transparence devant la fenêtre ; ils tombent jusqu'au ras du
    sol, contre le mur, derrière l'étagère."""
    xa, xb, za, zb = FENETRE["xa"], FENETRE["xb"], FENETRE["za"], FENETRE["zb"]
    xm = (xa + xb) / 2
    yv, z_t, z_bas = 0.38, zb + 0.6, 0.14
    B = M("droite")
    out = [trait([(xa - 0.9, yv, z_t), (xb + 0.9, yv, z_t)], B["cote"], 3, 1),
           bouton(xa - 0.95, yv, z_t, (B["cote"], B["face"], B["reflet"]), rayon=3.8),
           bouton(xb + 0.95, yv, z_t, (B["cote"], B["face"], B["reflet"]), rayon=3.8)]
    for (g, d) in ((xa - 0.75, xm - 0.08), (xm + 0.08, xb + 0.75)):
        out.append(face([(g, yv, z_t - 0.05), (d, yv, z_t - 0.05), (d, yv, z_bas), (g, yv, z_bas)], "#FFFFFF", r=2, extra=' opacity="0.5"'))
        # Les plis, droits et réguliers, un peu plus opaques
        n = 6
        for k in range(1, n):
            x = g + (d - g) * k / n
            out.append(trait([(x, yv + 0.002, z_t - 0.08), (x, yv + 0.002, z_bas + 0.04)], "#FFFFFF", 3.2, 0.35))
            out.append(trait([(x + 0.09, yv + 0.002, z_t - 0.08), (x + 0.09, yv + 0.002, z_bas + 0.04)], "#D9CDBB", 1, 0.25))
        out.append(trait([(g, yv + 0.003, z_bas + 0.06), (d, yv + 0.003, z_bas + 0.06)], "#FFFFFF", 2.2, 0.6))
        for k in range(n + 1):
            sx, sy = p(g + (d - g) * k / n, yv, z_t - 0.02)
            out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.2" fill="none" stroke="{B["face"]}" stroke-width="1.3" />')
    return "".join(out)


def lueurs_nuit_murs():
    """La nuit, la guirlande éclaire le haut des murs en bandes de lumière chaude de plus en plus
    légères, et la lampe de table fait un halo sur le mur de gauche."""
    out = []
    for k in range(14):
        z0, z1 = H_MUR - 0.22 * (k + 1), H_MUR - 0.22 * k
        op = 0.1 * (1 - k / 14)
        out.append(pan_g(0, 12, z0, z1, "#FFD98A", f' opacity="{op:.3f}"') + pan_d(0, 12, z0, z1, "#FFD98A", f' opacity="{op:.3f}"'))
    for r in (2.6, 2.0, 1.4, 0.9):
        out.append(face(cercle_mur_g(11.2, 3.0, r), "#FFC977", extra=' opacity="0.1"'))
    return "".join(out)


def lueurs_nuit_sol():
    """La nuit, la lampe de table fait une petite flaque de lumière chaude autour du coin lecture, et
    une lumière de plafond, qu'on ne voit pas, éclaire doucement toute la pièce (19 octobre 2026)."""
    halos = "".join(face([(0.8 + r * math.cos(a) * 1.2, 11.2 + r * math.sin(a), 0) for a in [2 * math.pi * i / 40 for i in range(40)]],
                        "#FFC977", extra=' opacity="0.1"') for r in (3.4, 2.6, 1.8, 1.1))
    # Et une lumière de plafond qu'on ne voit pas, qui éclaire doucement le milieu de la pièce
    plafond = "".join(face([(6 + r * math.cos(a), 6 + r * math.sin(a), 0) for a in [2 * math.pi * i / 48 for i in range(48)]],
                           "#FFD9A0", extra=' opacity="0.1"') for r in (6.5, 5, 3.6))
    return halos + plafond


def cercle_mur_g(yc, zc, r, n=40):
    """Un cercle posé à plat sur le mur de gauche (x = 0)."""
    return [(0.006, yc + r * math.cos(2 * math.pi * k / n), zc + r * 0.8 * math.sin(2 * math.pi * k / n)) for k in range(n)]


def guirlande():
    """La guirlande lumineuse en haut des deux murs, comme dans la toute première version : un fil
    qui festonne d'un clou à l'autre, et des boules de coton qui brillent doucement, chacune à son
    rythme (l'animation est dans la feuille de style, classe « ampoule »)."""
    z_clou, creux, e = H_MUR - 0.45, 0.42, 0.18
    # Les deux murs, du fond de gauche vers l'angle, puis de l'angle vers le fond de droite
    trajets = [((e, 11.6), (e, e), 4), ((e, e), (11.6, e), 4)]
    fils, boules, clous = [], [], []
    for (a, b, n_festons) in trajets:
        n = 12 * n_festons
        prec = None
        for i in range(n + 1):
            t = i / n
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            u = (t * n_festons) % 1
            z = z_clou - creux * math.sin(math.pi * u)
            cur = p(x, y, z)
            if prec:
                fils.append(f"L{cur[0]:.1f} {cur[1]:.1f}")
            else:
                fils.append(f"M{cur[0]:.1f} {cur[1]:.1f}")
            if i % 12 == 0:
                clous.append(f'<circle cx="{cur[0]:.1f}" cy="{cur[1]:.1f}" r="1.8" fill="{M("gauche")["cote"]}" />')
            elif i % 4 == 2:
                boules.append(f'<g class="ampoule"><circle cx="{cur[0]:.1f}" cy="{cur[1] + 5:.1f}" r="5.2" fill="#FFF1C9" />'
                              f'<circle cx="{cur[0] + 1.4:.1f}" cy="{cur[1] + 3.6:.1f}" r="1.8" fill="#FFFFFF" opacity="0.85" /></g>')
            prec = cur
    return (f'<path class="fil" d="{" ".join(fils)}" fill="none" stroke="{M("gauche")["cote"]}" stroke-width="1.3" stroke-linejoin="round" />'
            + "".join(boules) + "".join(clous))


def recoins():
    """Les recoins s'assombrissent doucement, comme dans une vraie pièce : l'angle des deux murs et le
    pied des murs, en bandes de plus en plus légères (19 octobre 2026)."""
    out = []
    for k in range(5):
        e, op = 0.12 * (k + 1), 0.045
        out.append(pan_g(0, e * 1.2, 0, H_MUR, "#6E4426", f' opacity="{op}"') + pan_d(0, e * 1.2, 0, H_MUR, "#6E4426", f' opacity="{op}"'))
        out.append(pan_g(0, 12, 0, e * 0.9, "#6E4426", f' opacity="{op}"') + pan_d(0, 12, 0, e * 0.9, "#6E4426", f' opacity="{op}"'))
    return "".join(out)


def recoins_sol():
    """Le sol s'assombrit un peu au pied des deux murs, là où la lumière arrive moins."""
    out = []
    for k in range(4):
        e = 0.18 * (k + 1)
        out.append(face([(0, 0, 0), (12, 0, 0), (12, e, 0), (0, e, 0)], "#6E4426", extra=' opacity="0.035"'))
        out.append(face([(0, 0, 0), (e, 0, 0), (e, 12, 0), (0, 12, 0)], "#6E4426", extra=' opacity="0.035"'))
    return "".join(out)


def halo_fenetre():
    """Le jour, le mur s'éclaire autour de la fenêtre : un halo doux, plus fort près du cadre."""
    xa, xb, za, zb = FENETRE["xa"], FENETRE["xb"], FENETRE["za"], FENETRE["zb"]
    xm, zm = (xa + xb) / 2, (za + zb) / 2
    out = []
    for k, (rx, rz) in enumerate(((3.4, 3.0), (2.8, 2.5), (2.3, 2.1))):
        pts = [(xm + rx * math.cos(a), 0.003, zm + rz * math.sin(a)) for a in [2 * math.pi * i / 48 for i in range(48)]]
        out.append(face(pts, "#FFFBF0", extra=' opacity="0.22"'))
    return '<g class="vue vue-jour">' + "".join(out) + "</g>"


def lumiere_fenetre():
    """La lumière de la fenêtre posée au sol, en aplat très doux, vers l'intérieur de la pièce :
    dorée le jour, orangée le soir, un clair de lune la nuit."""
    xa, xb = FENETRE["xa"], FENETRE["xb"]
    tache = [(xa + 0.4, 1.5, 0), (xb + 0.4, 1.5, 0), (xb + 1.6, 5.0, 0), (xa + 1.6, 5.0, 0)]
    return "".join(f'<g class="vue vue-{moment}">' + face(tache, couleur, r=16, extra=f' opacity="{opacite}"') + "</g>"
                   for moment, couleur, opacite in (("jour", "#FFD99A", 0.3), ("soir", "#FFB07A", 0.28), ("nuit", "#BFD0F2", 0.14)))


# ---------- Les murs ----------
# Le papier peint est un motif posé à plat sur le plan du mur (u le long du mur, v vers le bas).

COULEUR_POIS = "#E9B5BE"  # rose poudré, choisi par Pauline le 18 octobre 2026
H_MUR = 9.0


def matrice_mur(cote, z_haut):
    """Envoie les coordonnées du motif (u le long du mur, v vers le bas depuis z_haut) sur le
    plan du mur : cote « g » pour le mur de gauche (x = 0), « d » pour celui de droite (y = 0)."""
    a = -C30 * S if cote == "g" else C30 * S
    return f"matrix({a:.3f} {0.5 * S:.3f} 0 {S} {OX:.1f} {OY - z_haut * S:.1f})"


def motif(ident, cote, w, h, contenu, z_haut=H_MUR):
    return (f'<pattern id="{ident}" patternUnits="userSpaceOnUse" width="{w}" height="{h}" '
            f'patternTransform="{matrice_mur(cote, z_haut)}">{contenu}</pattern>')


def pan_g(y0, y1, z0, z1, remplissage, extra=""):
    return face([(0.004, y0, z0), (0.004, y1, z0), (0.004, y1, z1), (0.004, y0, z1)], remplissage, extra=extra)


def pan_d(x0, x1, z0, z1, remplissage, extra=""):
    return face([(x0, 0.004, z0), (x1, 0.004, z0), (x1, 0.004, z1), (x0, 0.004, z1)], remplissage, extra=extra)


def plinthes(couleur="#E9C892", reflet="#F7E2BC"):
    """Les plinthes de bois clair au pied des deux murs, avec leur reflet."""
    return (pan_g(0, 12, 0, 0.38, couleur) + pan_d(0, 12, 0, 0.38, couleur)
            + trait([(0.01, 0.1, 0.36), (0.01, 11.9, 0.36)], reflet, 1.6, 0.9)
            + trait([(0.1, 0.01, 0.36), (11.9, 0.01, 0.36)], reflet, 1.6, 0.9))


def gros_pois_motif(pas=1.2, fond="#F1E4D3", pois="#C9692B", fil_clair="#FFFFFF", fil_sombre="#8A4416"):
    """Le papier peint aux gros pois, d'après la photo de Pauline : sur un fond crème, de grands
    ronds orange alignés en grille, presque jointifs, et sur tout le papier un fin tissage de lin,
    des fils clairs et sombres croisés. Un carreau porte un rond."""
    r = pas * 0.465
    out = [f'<rect width="{pas}" height="{pas}" fill="{fond}" />',
           f'<circle cx="{pas / 2:.3f}" cy="{pas / 2:.3f}" r="{r:.3f}" fill="{pois}" />']
    rng = random.Random(14)
    n = 26
    for k in range(n):
        pos = pas * (k + 0.5) / n
        for horizontal in (True, False):
            couleur = fil_clair if rng.random() < 0.5 else fil_sombre
            op = rng.uniform(0.05, 0.13)
            ep = rng.uniform(0.006, 0.014)
            d = f"M0 {pos:.3f} H{pas}" if horizontal else f"M{pos:.3f} 0 V{pas}"
            out.append(f'<path d="{d}" stroke="{couleur}" stroke-width="{ep:.3f}" opacity="{op:.2f}" />')
    return "".join(out)


def murs():
    """Les deux murs : à gauche, le papier peint aux gros pois rose poudré sur fond crème ; à droite,
    le blanc des carreaux clairs du tapis ; des plinthes dans le ton des meubles. Renvoie
    (définitions, dessin)."""
    ident = f"l-pois-{COULEUR_POIS[1:]}"
    defs = motif(ident, "g", 1.2, 1.2, gros_pois_motif(pois=COULEUR_POIS))
    out = pan_g(0, 12, 0, 9, f"url(#{ident})") + pan_d(0, 12, 0, 9, "#FAF3E8")
    return defs, out + plinthes(M("gauche")["cote"], M("gauche")["face"])


# ---------- Les bois du mobilier ----------

NOYER_MOYEN = dict(haut="#B07B57", face="#93603F", cote="#73472D", fond="#45291A", sol="#845537",
                   paroi="#845539", grain="#653F28", reflet="#E6BB96")  # le noyer doux de la palette (19 octobre 2026)
ROTIN = dict(haut="#F3D7A4", face="#E3BC7E", cote="#C39A5D", fond="#7E5C32", sol="#D6AE70",
             paroi="#D8B176", grain="#B68C50", reflet="#FFF2D8")

PARQUET_CLAIR = ("#D9B384", "#D1A978", "#E0BE91", "#B88D5C", "#C99E6D")  # le sol miel de la palette (19 octobre 2026)
# Le mobilier retenu par Pauline les 17 et 18 octobre 2026 : un parquet miel moyen, des meubles en noyer
MOBILIER = dict(parquet=PARQUET_CLAIR, gauche=NOYER_MOYEN, droite=NOYER_MOYEN, coffre=NOYER_MOYEN, pieds=NOYER_MOYEN)


def M(cle):
    """La couleur d'un élément du mobilier : parquet, meubles du mur de gauche, du mur de droite,
    coffre, pieds."""
    return MOBILIER[cle]
CHROME = "#C3C9D0"  # les boutons et les cerclages en métal argenté, plutôt que le laiton


# ---------- Les tissus, les petits objets, les boutons ----------

DEFS = []  # les motifs de tissu, ajoutés aux définitions de la pièce

LAQUE_CREME = dict(haut="#FBF5EA", face="#EADDC2", cote="#CDBB9C")  # la table d'appoint, en vert sauge jusqu'au 19 octobre 2026


def pois_motif(w=0.9, h=0.9, fond="#F4B3C1", pois="#FFF6EA"):
    """Des pois crème en quinconce sur un rose bonbon : deux pois par carreau, qui se raccordent
    sans couture."""
    return (f'<rect width="{w}" height="{h}" fill="{fond}" />'
            f'<circle cx="{w * 0.25:.3f}" cy="{h * 0.25:.3f}" r="{w * 0.13:.3f}" fill="{pois}" />'
            f'<circle cx="{w * 0.75:.3f}" cy="{h * 0.75:.3f}" r="{w * 0.13:.3f}" fill="{pois}" />')


def motifs_tissu(nom, contenu, w, h, echelle=0.3):
    """Un tissu à motif, posé sur les trois sortes de faces d'un volume : celles tournées vers +x,
    vers +y, et les dessus. Les motifs s'appellent nom-x, nom-y, nom-z."""
    k = S * echelle
    plans = {"x": f"matrix({-C30 * k:.3f} {0.5 * k:.3f} 0 {k:.3f} {OX} {OY})",
             "y": f"matrix({C30 * k:.3f} {0.5 * k:.3f} 0 {k:.3f} {OX} {OY})",
             "z": f"matrix({C30 * k:.3f} {0.5 * k:.3f} {-C30 * k:.3f} {0.5 * k:.3f} {OX} {OY})"}
    # Le dessin du motif, une seule fois ; chaque plan le reprend
    DEFS.append(f'<g id="{nom}-dessin">{contenu}</g>')
    for plan, m in plans.items():
        DEFS.append(f'<pattern id="{nom}-{plan}" patternUnits="userSpaceOnUse" width="{w}" height="{h}" patternTransform="{m}"><use href="#{nom}-dessin" /></pattern>')


def boite_tissu(x0, x1, y0, y1, z0, z1, r=12.0, bombe=0.0, motif="leopard", silhouette="#5A3E28"):
    """Un volume tendu d'un tissu à motif : la silhouette sombre, les trois faces au motif, puis un
    voile d'ombre sur la face de côté et un voile léger sur la face éclairée, pour garder le volume."""
    cote = [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
    avant = [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]
    dessus = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    contour = [(x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x1, y0, z1)]
    rf = r * 0.45
    return (face(contour, silhouette, r, bombe)
            + face(cote, f"url(#{motif}-y)", rf) + face(cote, "#1E1410", rf, extra=' opacity="0.28"')
            + face(avant, f"url(#{motif}-x)", rf) + face(avant, "#1E1410", rf, extra=' opacity="0.06"')
            + face(dessus, f"url(#{motif}-z)", rf))


CADRE = ("#FBF5EA", "#EADDC2", "#CDBB9C")  # le cadre crème, choisi par Pauline le 19 octobre 2026
PHOTO = "teckel"  # la photo du cadre : « teckel » (Popeye, l'easter egg de Popeye Prime) ou « mer »


def cadre(x, y, z):
    """Un petit cadre posé, avec une photo de bord de mer : un ciel pâle, un soleil, la mer en
    deux bleus, une plage de sable (le portrait d'avant, jusqu'au 19 octobre 2026)."""
    out = [boite(x - 0.05, x + 0.05, y - 0.32, y + 0.32, z, z + 0.85, CADRE or tons(M("gauche")), r=2)]
    xf = x + 0.055
    ya, yb, za, zb = y - 0.25, y + 0.25, z + 0.08, z + 0.77
    if PHOTO == "teckel":
        return "".join(out) + photo_teckel(xf, yb, zb)

    def bande(z0, z1, couleur):
        return face([(xf, ya, z0), (xf, yb, z0), (xf, yb, z1), (xf, ya, z1)], couleur)
    out.append(bande(za, zb, "#E4EEF6"))                       # le ciel
    sx, sy = p(xf, y + 0.08, z + 0.58)
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.6" fill="#F3DD90" />')
    out.append(bande(za + 0.2, za + 0.36, "#8FA6EC"))           # la mer au large
    out.append(bande(za + 0.14, za + 0.22, "#4A67D8"))          # la mer, plus près
    out.append(bande(za, za + 0.15, "#EBD3AE"))                 # la plage
    a, b = p(xf, ya + 0.08, za + 0.3), p(xf, ya + 0.2, za + 0.3)
    out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#FFFFFF" stroke-width="1" opacity="0.8" />')
    return "".join(out)


def photo_teckel(xf, y_gauche, z_haut):
    """L'easter egg de Popeye Prime : la photo de Popeye, teckel nain à poil ras fauve, collier rose
    et médaille en cœur, debout de profil dans l'herbe, sous un ciel pâle. Dessinée en centièmes
    d'unité dans le plan du cadre (u vers la droite de la photo, v vers le bas)."""
    sx, sy = p(xf, y_gauche, z_haut)
    k = S / 100
    m = f"matrix({C30 * k:.3f} {-0.5 * k:.3f} 0 {k:.3f} {sx:.1f} {sy:.1f})"
    fauve, ombre, clair = "#D9965A", "#B5713A", "#EDB884"
    return (f'<g transform="{m}">'
            f'<rect width="50" height="69" fill="#E4EEF6" /><rect y="44" width="50" height="25" fill="#B9C98F" /><rect y="44" width="50" height="4" fill="#CBD8A2" />'
            # la queue, les pattes du fond, le corps, les pattes de devant
            f'<path d="M10 41 Q4 36 6 31" fill="none" stroke="{ombre}" stroke-width="2.6" stroke-linecap="round" />'
            f'<rect x="13" y="44" width="3.6" height="9" rx="1.6" fill="{ombre}" /><rect x="31" y="44" width="3.6" height="9" rx="1.6" fill="{ombre}" />'
            f'<rect x="8" y="35" width="32" height="12" rx="6" fill="{fauve}" />'
            f'<path d="M12 38 Q24 36 36 38" fill="none" stroke="{clair}" stroke-width="1.6" stroke-linecap="round" opacity="0.8" />'
            f'<rect x="10" y="44" width="3.6" height="9.5" rx="1.6" fill="{fauve}" /><rect x="34" y="44" width="3.6" height="9.5" rx="1.6" fill="{fauve}" />'
            # la tête, le museau, la truffe, l'œil, l'oreille, le collier et sa médaille
            f'<ellipse cx="39" cy="31" rx="6.5" ry="6" fill="{fauve}" />'
            f'<ellipse cx="45.5" cy="33" rx="4" ry="2.8" fill="{fauve}" /><circle cx="48.6" cy="32.4" r="1.3" fill="#3B2418" />'
            f'<circle cx="40.8" cy="29.5" r="1.1" fill="#3B2418" />'
            f'<path d="M35 27 Q31 30 33 37 Q36 36 37 31 Z" fill="{ombre}" />'
            f'<path d="M34 36.5 Q38 39 42 36" fill="none" stroke="#E9A3B8" stroke-width="2.2" stroke-linecap="round" />'
            f'<path d="M38.2 39.4 q-1.2 -1.2 0 -2 q1.2 0.8 0 2 q1.2 -1.2 0 -2" fill="#F3DD90" /><circle cx="38.2" cy="39.2" r="1.1" fill="#F3DD90" />'
            f'</g>')


def flacon_parfum(x, y, z):
    """Un flacon de parfum ancien : un verre rond et facetté, un col doré, un bouchon en boule ;
    à côté, la poire du vaporisateur au bout d'un petit tuyau."""
    sx, sy = p(x, y, z)
    out = [ombre_posee(sx, sy, 11, 4, 0.18)]
    # Le verre, ombré à gauche, avec le parfum dedans
    out.append(f'<path d="M{sx - 9:.1f} {sy - 4:.1f} Q{sx - 11:.1f} {sy - 16:.1f} {sx:.1f} {sy - 19:.1f} Q{sx + 11:.1f} {sy - 16:.1f} {sx + 9:.1f} {sy - 4:.1f} '
               f'Q{sx:.1f} {sy + 1:.1f} {sx - 9:.1f} {sy - 4:.1f} Z" fill="#E7EEF0" />'
               f'<path d="M{sx - 8:.1f} {sy - 6:.1f} Q{sx - 9:.1f} {sy - 11:.1f} {sx - 8:.1f} {sy - 12:.1f} L{sx + 8:.1f} {sy - 12:.1f} Q{sx + 9:.1f} {sy - 11:.1f} {sx + 8:.1f} {sy - 6:.1f} '
               f'Q{sx:.1f} {sy - 1:.1f} {sx - 8:.1f} {sy - 6:.1f} Z" fill="#F2C98A" opacity="0.85" />'
               f'<path d="M{sx - 9:.1f} {sy - 4:.1f} Q{sx - 11:.1f} {sy - 16:.1f} {sx:.1f} {sy - 19:.1f} L{sx - 2:.1f} {sy - 1:.1f} Q{sx - 6:.1f} {sy - 2:.1f} {sx - 9:.1f} {sy - 4:.1f} Z" fill="#9AA6AE" opacity="0.18" />'
               f'<path d="M{sx + 4:.1f} {sy - 15:.1f} Q{sx + 7:.1f} {sy - 12:.1f} {sx + 7:.1f} {sy - 8:.1f}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.9" />')
    # Le col doré et le bouchon en boule
    out.append(f'<rect x="{sx - 3:.1f}" y="{sy - 23:.1f}" width="6" height="5" rx="1.5" fill="#D9A84A" />'
               f'<rect x="{sx:.1f}" y="{sy - 23:.1f}" width="2" height="5" fill="#F2D27E" />'
               f'<circle cx="{sx:.1f}" cy="{sy - 27:.1f}" r="4.4" fill="#8FA6EC" />'
               f'<circle cx="{sx + 1.2:.1f}" cy="{sy - 28.2:.1f}" r="1.4" fill="#FFFFFF" opacity="0.8" />')
    # Le petit tuyau et la poire du vaporisateur, posée sur le plateau à droite du flacon
    out.append(f'<path d="M{sx + 3:.1f} {sy - 21:.1f} Q{sx + 14:.1f} {sy - 22:.1f} {sx + 14:.1f} {sy - 9:.1f}" fill="none" stroke="#D9A84A" stroke-width="1.4" stroke-linecap="round" />'
               f'<ellipse cx="{sx + 15:.1f}" cy="{sy - 1:.1f}" rx="4.5" ry="1.6" fill="#3B2418" opacity="0.18" />'
               f'<ellipse cx="{sx + 14.5:.1f}" cy="{sy - 5:.1f}" rx="4.4" ry="4.6" fill="#8FA6EC" />'
               f'<circle cx="{sx + 15.8:.1f}" cy="{sy - 6.8:.1f}" r="1.2" fill="#FFFFFF" opacity="0.7" />')
    return "".join(out)


CHROMES = ("#8E959D", CHROME, "#F4F6F8")  # ombre, corps, reflet


def bouton(xf, y, z, t=CHROMES, rayon=4.6):
    """Un bouton rond et bombé, posé sur une face tournée vers +x : son ombre portée, son corps,
    son reflet."""
    sx, sy = p(xf, y, z)
    return (f'<circle cx="{sx - 1.2:.1f}" cy="{sy + 1.6:.1f}" r="{rayon:.1f}" fill="#3B2418" opacity="0.22" />'
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rayon:.1f}" fill="{t[0]}" />'
            f'<circle cx="{sx + rayon * 0.15:.1f}" cy="{sy - rayon * 0.15:.1f}" r="{rayon * 0.78:.1f}" fill="{t[1]}" />'
            f'<circle cx="{sx + rayon * 0.32:.1f}" cy="{sy - rayon * 0.32:.1f}" r="{rayon * 0.28:.1f}" fill="{t[2]}" />')


# ---------- Le dressing ouvert ----------


# Les vêtements du dressing ouvert : (sorte, longueur, couleurs claire, moyenne, sombre)
VETEMENTS = [("robe", 2.25, ("#F6D3DA", "#E9B5BE", "#C98F9B")),     # robe rose poudré
             ("manteau", 2.3, ("#E9C496", "#D2A06A", "#AE7C47")),    # manteau camel
             ("chemise", 1.55, ("#F8F1E1", "#EADDC2", "#CBBC9F")),  # chemise crème
             ("pull", 1.25, ("#D9DA9A", "#B9BA68", "#97984B")),     # pull kaki citron
             ("chemise", 1.5, ("#D7E2F7", "#B3C6EE", "#8EA5D6")),   # chemise bleu ciel
             ("robe", 2.0, ("#A9BDF5", "#4A67D8", "#3550B4"))]      # robe cobalt (harmonie du 19 octobre 2026)


def vetement(y, x0, x1, z_haut, sorte, longueur, c):
    """Un vêtement sur son cintre, pendu à la tringle : une silhouette plate dans le plan y,
    vue de biais, avec un pli et un liseré de lumière du côté de la fenêtre."""
    xm = (x0 + x1) / 2
    zb = z_haut - longueur
    if sorte == "robe":
        pts = [(xm - 0.12, z_haut), (x0 + 0.1, z_haut - 0.06), (x0, z_haut - 0.32), (x0 + 0.14, z_haut - 0.36),
               (x0 + 0.16, z_haut - 0.8), (x0 - 0.1, zb), (x1 + 0.1, zb), (x1 - 0.16, z_haut - 0.8),
               (x1 - 0.14, z_haut - 0.36), (x1, z_haut - 0.32), (x1 - 0.1, z_haut - 0.06), (xm + 0.12, z_haut)]
    elif sorte == "pull":
        pts = [(xm - 0.13, z_haut), (x0 + 0.04, z_haut - 0.08), (x0 - 0.02, zb + 0.1), (x0 + 0.06, zb),
               (x1 - 0.06, zb), (x1 + 0.02, zb + 0.1), (x1 - 0.04, z_haut - 0.08), (xm + 0.13, z_haut)]
    elif sorte == "manteau":
        # Long, un peu évasé vers le bas, les épaules carrées
        pts = [(xm - 0.12, z_haut), (x0 + 0.02, z_haut - 0.08), (x0 - 0.02, z_haut - 0.3), (x0 - 0.1, zb),
               (x1 + 0.1, zb), (x1 + 0.02, z_haut - 0.3), (x1 - 0.02, z_haut - 0.08), (xm + 0.12, z_haut)]
    else:  # chemise, veste : droites, un peu cintrées
        pts = [(xm - 0.1, z_haut), (x0 + 0.04, z_haut - 0.07), (x0 + 0.02, zb), (x1 - 0.02, zb),
               (x1 - 0.04, z_haut - 0.07), (xm + 0.1, z_haut)]
    out = [face([(x, y, z) for x, z in pts], c[1], r=4)]
    # Les manches, qui pendent le long du corps, par-dessus (19 octobre 2026 : on ne les voyait pas)
    longueur_manche = {"chemise": 1.1, "pull": 0.95, "manteau": 1.35}.get(sorte)
    if longueur_manche:
        zm = z_haut - longueur_manche
        for cote in (-1, 1):
            xe = x0 if cote < 0 else x1
            pts_m = [(xe - cote * 0.02, y + 0.004, z_haut - 0.05), (xe + cote * 0.11, y + 0.004, z_haut - 0.24), (xe + cote * 0.09, y + 0.004, zm),
                     (xe - cote * 0.1, y + 0.004, zm), (xe - cote * 0.13, y + 0.004, z_haut - 0.32)]
            out.append(face(pts_m, c[1], r=3))
            out.append(trait([(xe - cote * 0.1, y + 0.006, z_haut - 0.3), (xe - cote * 0.09, y + 0.006, zm + 0.05)], c[2], 1.6, 0.6))
            out.append(face([(xe + cote * 0.09, y + 0.006, zm + 0.1), (xe - cote * 0.1, y + 0.006, zm + 0.1), (xe - cote * 0.1, y + 0.006, zm), (xe + cote * 0.09, y + 0.006, zm)], c[2], r=1))
    # L'ombre du côté du mur, le pli du milieu, la lumière côté fenêtre
    out.append(trait([(x0 + 0.06, y, z_haut - 0.2), (x0 + 0.05, y, zb + 0.08)], c[2], 3.0, 0.55))
    out.append(trait([(xm + 0.05, y, z_haut - 0.45), (xm + 0.1, y, zb + 0.12)], c[2], 1.2, 0.5))
    out.append(trait([(x1 - 0.08, y, z_haut - 0.15), (x1 - 0.07 + (0.08 if sorte == "robe" else 0), y, zb + 0.1)], c[0], 1.8, 0.85))
    if sorte == "chemise":
        for k in range(4):
            sx, sy = p(xm + 0.02, y, z_haut - 0.25 - 0.3 * k)
            out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.1" fill="{c[2]}" />')
    if sorte == "manteau":
        # Les revers en V, la ceinture nouée, deux rangées de gros boutons
        out.append(face([(xm - 0.12, y, z_haut), (xm - 0.3, y, z_haut - 0.12), (xm, y, z_haut - 0.75), (xm + 0.3, y, z_haut - 0.12), (xm + 0.12, y, z_haut)], c[2], r=2))
        out.append(face([(xm - 0.08, y, z_haut - 0.02), (xm - 0.2, y, z_haut - 0.12), (xm, y, z_haut - 0.6), (xm + 0.2, y, z_haut - 0.12), (xm + 0.08, y, z_haut - 0.02)], c[1], r=2))
        zc = z_haut - 1.05
        out.append(face([(x0 - 0.03, y, zc - 0.07), (x1 + 0.03, y, zc - 0.07), (x1 + 0.03, y, zc + 0.07), (x0 - 0.03, y, zc + 0.07)], c[2], r=2))
        out.append(trait([(xm + 0.05, y, zc), (xm + 0.12, y, zc - 0.45)], c[2], 2.2, 1))
        for dz in (0.75, 0.9, 1.3, 1.5):
            for dx in (-0.12, 0.14):
                sx, sy = p(xm + dx, y, z_haut - dz)
                out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.7" fill="{c[2]}" />')
    if sorte == "veste":
        out.append(trait([(xm - 0.1, y, z_haut), (xm, y, z_haut - 0.55), (xm + 0.1, y, z_haut)], c[2], 1.6, 0.8))
    return "".join(out)


def crochet(y, xm, z_tringle, z_epaule):
    """Le crochet chromé d'un cintre : il monte du cintre, passe par-dessus la tringle et redescend
    de l'autre côté. Peint après la tringle, il passe devant elle."""
    points = [(xm, y, z_epaule + 0.14), (xm + 0.02, y, z_tringle - 0.08), (xm + 0.06, y, z_tringle),
              (xm + 0.03, y, z_tringle + 0.07), (xm - 0.03, y, z_tringle + 0.07), (xm - 0.06, y, z_tringle + 0.01)]
    return trait(points, "#9AA1A9", 1.3, 1)


def cintre(y, xm, z_epaule):
    """Le bois clair d'un cintre ; le vêtement pend dessous, sans toucher la tringle."""
    return trait([(xm - 0.42, y, z_epaule - 0.02), (xm, y, z_epaule + 0.14), (xm + 0.42, y, z_epaule - 0.02)], "#E2B47C", 2.2, 1)


def dressing_ouvert(meuble, badge):
    """Le dressing de boutique, d'après la photo de Pauline (19 octobre 2026) : une longue tringle
    chromée fixée au mur par deux potences, où pendent les vêtements ; dessous, un meuble bas en
    noyer tout arrondi, à deux tiroirs, sur des pieds en galette ; dessus, une paire de babies.
    Il remplace le dressing ouvert à montants et sa boîte à chapeau."""
    B = M("gauche")
    T = tons(B)
    dep, y0, y1 = 1.3, 0.8, 3.5  # moins large, et décalé vers l'angle de la pièce (19 octobre 2026)
    zl, zt = N["pied"], 1.05
    zr = 4.4                       # la tringle, assez haut pour que les vêtements ne touchent pas le meuble
    xm = 0.66                      # l'axe des cintres, à distance du mur
    out = [ombre_portee(0, dep, y0, y1, 1.4), ombre_mur(y1, 4.6, 1.0, 0.06)]
    # Le meuble bas : ses pieds, son corps arrondi, deux tiroirs à boutons de bois, un plateau qui déborde
    for (px, py) in ((0.3, y1 - 0.3), (dep - 0.3, y0 + 0.3), (dep - 0.3, y1 - 0.3)):
        out.append(pied(px, py, zl + 0.04, B))
    out.append(boite(0, dep, y0, y1, zl, zt, T, r=N["r"] + 5, bombe=N["bombe"]))
    xf = dep + 0.006
    for (ya, yb) in ((y0 + 0.2, (y0 + y1) / 2 - 0.06), ((y0 + y1) / 2 + 0.06, y1 - 0.2)):
        out.append(face([(xf, ya, zl + 0.12), (xf, yb, zl + 0.12), (xf, yb, zt - 0.1), (xf, ya, zt - 0.1)], B["haut"], r=N["r"]))
        out.append(trait([(xf + 0.002, ya + 0.12, zt - 0.14), (xf + 0.002, yb - 0.12, zt - 0.14)], B["reflet"], 1.4, 0.6))
        out.append(bouton(xf + 0.02, (ya + yb) / 2, (zl + zt) / 2 + 0.02, (B["cote"], B["face"], B["reflet"]), rayon=4.4))
    out.append(boite(-0.02, dep + 0.08, y0 - 0.08, y1 + 0.08, zt, zt + 0.2, T, r=N["r"] + 3, bombe=N["bombe"]))
    zh = zt + 0.2
    out.append(trait([(dep + 0.07, y0 + 0.15, zh), (dep + 0.07, y1 - 0.2, zh)], B["reflet"], 2.4, 0.9))
    # La tringle et la potence du fond
    chrome = (CHROME, "#A9AFB5", "#8E959D")
    out.append(boite(0, xm + 0.06, y0 + 0.1, y0 + 0.2, zr - 0.06, zr + 0.06, chrome, r=2))
    # La boîte à chapeau, sur le plateau, avant les vêtements qui passent devant elle (19 octobre 2026)
    out.append(boite_a_chapeau(0.62, y1 - 0.55, zh, 0.85))
    # Les vêtements, du fond vers l'avant, centrés sur la tringle
    n = len(VETEMENTS)
    crochets = []
    for k, (sorte, longueur, c) in enumerate(VETEMENTS):
        y = y0 + 0.45 + k * ((y1 - y0 - 0.9) / (n - 1))  # centrés sur la tringle (19 octobre 2026)
        z_epaule = zr - 0.42  # le vêtement pend sous la tringle, sans la toucher
        out.append(cintre(y, xm, z_epaule))
        crochets.append(crochet(y, xm, zr, z_epaule))
        out.append(vetement(y, xm - 0.46, xm + 0.46, z_epaule, sorte, longueur, c))
    # La tringle, par-dessus le bois des cintres : là où elle les croise, elle est devant eux
    out.append(trait([(xm, y0 + 0.1, zr), (xm, y1 - 0.1, zr)], "#8E959D", 3.4, 1))
    out.append(trait([(xm, y0 + 0.1, zr + 0.03), (xm, y1 - 0.1, zr + 0.03)], CHROMES[2], 1.2, 0.9))
    out.extend(crochets)  # seuls les crochets passent devant la tringle (19 octobre 2026)
    # La potence de devant, par-dessus, puis les chaussures sur le plateau
    out.append(boite(0, xm + 0.06, y1 - 0.2, y1 - 0.1, zr - 0.06, zr + 0.06, chrome, r=2))
    out.append(badge("dressing", 0.65, (y0 + y1) / 2, zr + 1.0))
    return meuble("dressing", "".join(out))


def boite_a_chapeau(x, y, z, taille=1.0, corps=("#F6EEDC", "#E9DCC2"), rayure="#D9C3A0",
                    ruban=("#E58FA8", "#C96F8C")):  # rose poudré, pour trancher sur la robe cobalt (19 octobre 2026)
    """Une boîte à chapeau ronde, refaite le 19 octobre 2026 : des rayures verticales régulières,
    découpées à la forme du cylindre, un couvercle qui déborde, un ruban qui passe au milieu et un
    nœud bien centré sur le dessus. Retirée puis remise sur le meuble du dressing le 19 octobre 2026."""
    sx, sy = p(x, y, z)
    k = S * taille
    rx, ry, h = 0.5 * k, 0.29 * k, 0.48 * k
    ident = f"chapeau-{sx:.0f}-{sy:.0f}"
    # Le corps : un cylindre vu de trois quarts, ombré à gauche
    corps_d = (f"M{sx - rx:.1f} {sy - h:.1f} L{sx - rx:.1f} {sy:.1f} A{rx:.1f} {ry:.1f} 0 0 0 {sx + rx:.1f} {sy:.1f} "
               f"L{sx + rx:.1f} {sy - h:.1f} A{rx:.1f} {ry:.1f} 0 0 1 {sx - rx:.1f} {sy - h:.1f} Z")
    out = [ombre_posee(sx, sy, rx * 1.05, ry * 1.05, 0.18),
           f'<clipPath id="{ident}"><path d="{corps_d}" /></clipPath>',
           f'<path d="{corps_d}" fill="{corps[0]}" />',
           f'<g clip-path="url(#{ident})">']
    # Les rayures : régulières sur le tour du cylindre, donc plus serrées vers les bords
    n = 9
    for i in range(n):
        a0, a1 = math.pi * (i + 0.25) / n, math.pi * (i + 0.6) / n
        u0, u1 = -math.cos(a0), -math.cos(a1)
        xa, xb = sx + u0 * rx, sx + u1 * rx
        ya, yb = sy + ry * math.sin(a0), sy + ry * math.sin(a1)
        out.append(f'<path d="M{xa:.1f} {sy - h - ry:.1f} L{xb:.1f} {sy - h - ry:.1f} L{xb:.1f} {yb:.1f} L{xa:.1f} {ya:.1f} Z" fill="{rayure}" />')
    # L'ombre douce du côté gauche, et le ruban qui descend au milieu
    out.append(f'<path d="M{sx - rx:.1f} {sy - h - ry:.1f} L{sx - rx * 0.35:.1f} {sy - h - ry:.1f} L{sx - rx * 0.35:.1f} {sy + ry:.1f} L{sx - rx:.1f} {sy + ry:.1f} Z" fill="{corps[1]}" opacity="0.55" />')
    out.append(f'<rect x="{sx - 3:.1f}" y="{sy - h:.1f}" width="6" height="{h + ry + 2:.1f}" fill="{ruban[0]}" />'
               f'<rect x="{sx - 3:.1f}" y="{sy - h:.1f}" width="2" height="{h + ry + 2:.1f}" fill="{ruban[1]}" />')
    out.append("</g>")
    # Le couvercle : un bandeau qui déborde, puis le dessus
    rc, hc = rx * 1.07, 0.1 * k
    zc = sy - h
    out.append(f'<path d="M{sx - rc:.1f} {zc - hc:.1f} L{sx - rc:.1f} {zc:.1f} A{rc:.1f} {ry * 1.07:.1f} 0 0 0 {sx + rc:.1f} {zc:.1f} '
               f'L{sx + rc:.1f} {zc - hc:.1f} Z" fill="{corps[1]}" />'
               f'<rect x="{sx - 3:.1f}" y="{zc - hc:.1f}" width="6" height="{hc + ry * 1.07:.1f}" fill="{ruban[0]}" />'
               f'<ellipse cx="{sx:.1f}" cy="{zc - hc:.1f}" rx="{rc:.1f}" ry="{ry * 1.07:.1f}" fill="{corps[0]}" />'
               f'<path d="M{sx + rc * 0.25:.1f} {zc - hc - ry * 0.8:.1f} Q{sx + rc * 0.8:.1f} {zc - hc - ry * 0.55:.1f} {sx + rc * 0.9:.1f} {zc - hc - ry * 0.1:.1f}" '
               f'fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" opacity="0.8" />')
    # Le ruban qui traverse le dessus, de l'arrière vers l'avant, puis le nœud au centre
    zt = zc - hc
    out.append(f'<path d="M{sx - 3:.1f} {zt - ry * 1.07:.1f} L{sx + 3:.1f} {zt - ry * 1.07:.1f} L{sx + 3:.1f} {zt + ry * 1.07:.1f} L{sx - 3:.1f} {zt + ry * 1.07:.1f} Z" fill="{ruban[0]}" />')
    bx, by = sx, zt
    out.append(f'<path d="M{bx:.1f} {by:.1f} C{bx - 7:.1f} {by - 9:.1f} {bx - 14:.1f} {by - 3:.1f} {bx - 11:.1f} {by + 2:.1f} C{bx - 8:.1f} {by + 5:.1f} {bx - 3:.1f} {by + 2:.1f} {bx:.1f} {by:.1f} Z" fill="{ruban[1]}" />'
               f'<path d="M{bx:.1f} {by:.1f} C{bx + 7:.1f} {by - 9:.1f} {bx + 14:.1f} {by - 3:.1f} {bx + 11:.1f} {by + 2:.1f} C{bx + 8:.1f} {by + 5:.1f} {bx + 3:.1f} {by + 2:.1f} {bx:.1f} {by:.1f} Z" fill="{ruban[0]}" />'
               f'<path d="M{bx - 1.5:.1f} {by + 1:.1f} L{bx - 5:.1f} {by + 9:.1f} L{bx - 2:.1f} {by + 8:.1f} Z" fill="{ruban[1]}" />'
               f'<path d="M{bx + 1.5:.1f} {by + 1:.1f} L{bx + 5:.1f} {by + 9:.1f} L{bx + 2:.1f} {by + 8:.1f} Z" fill="{ruban[0]}" />'
               f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="3" ry="2.6" fill="{ruban[0]}" />'
               f'<path d="M{bx + 5:.1f} {by - 4:.1f} q3 -1 5 1" fill="none" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round" opacity="0.6" />')
    return "".join(out)


# ---------- La bibliothèque, les étagères déco, le coffre ----------


def bobine(x, y, z0, z1, B, r=0.14):
    """Une colonne de bois tourné en bobines, comme les meubles à boules des années 70 : des
    boules empilées, chacune ombrée à gauche et éclairée à droite, avec son point de lumière."""
    rr = r * S
    n = max(2, round((z1 - z0) / (2 * r * 0.9)))
    pas = (z1 - z0) / n
    out = []
    for k in range(n):
        cx, cy = p(x, y, z0 + pas * (k + 0.5))
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="{B["cote"]}" />'
                   f'<circle cx="{cx + rr * 0.18:.1f}" cy="{cy - rr * 0.12:.1f}" r="{rr * 0.74:.1f}" fill="{B["face"]}" />'
                   f'<circle cx="{cx + rr * 0.42:.1f}" cy="{cy - rr * 0.36:.1f}" r="{rr * 0.2:.1f}" fill="{B["reflet"]}" opacity="0.85" />')
    return "".join(out)


def biblio_festons(meuble, badge):
    """La bibliothèque à bobines : quatre colonnes de bois tourné aux coins, quatre tablettes, pas de fond.
    Sur les tablettes, des livres debout (les couchés faisaient des piles de pulls) ; dessus, un portrait encadré."""
    B = M("gauche")
    T = tons(B)
    dep, y0, y1 = 1.0, 4.7, 7.9
    ep = 0.2
    niveaux = (0.4, 1.5, 2.6, 3.7)
    zh = niveaux[-1] + ep
    out = [ombre_portee(0, dep, y0, y1, 4.1, 0.16), ombre_mur(y1, 4.1, 1.1, 0.07)]
    # Plus de fond : on voit le papier peint entre les livres (19 octobre 2026). Les colonnes sont
    # posées sur les coins des tablettes ; celles des coins de côté, tout au bord, pour tomber
    # exactement sur la pointe des planches comme les autres
    for (cx, cy) in ((0.14, y0 + 0.14), (0.03, y1 - 0.03)):
        out.append(bobine(cx, cy, 0, zh + 0.3, B))
    yi0, yi1 = y0 + 0.3, y1 - 0.3
    rangs = [lambda z: livres_debout(0.12, dep - 0.1, yi0, yi0 + 1.5, z, 0.76, 31) + livres_debout(0.12, dep - 0.1, yi0 + 1.85, yi1, z, 0.7, 35),
             lambda z: livres_debout(0.12, dep - 0.1, yi0 + 0.5, yi1 - 0.4, z, 0.74, 32),
             lambda z: livres_debout(0.12, dep - 0.1, yi0, yi0 + 1.2, z, 0.74, 34) + livres_debout(0.12, dep - 0.1, yi1 - 0.9, yi1, z, 0.7, 36)]
    for k, zk in enumerate(niveaux):
        out.append(boite(0, dep, y0, y1, zk, zk + ep, T, r=2))  # des coins presque vifs, pour que les planches touchent les colonnes
        out.append(trait([(dep, y0 + 0.25, zk + ep), (dep, y0 + 1.9, zk + ep)], B["reflet"], 2.0, 0.85))
        if k < 3:
            out.append(rangs[k](zk + ep))  # des livres, rien d'autre (19 octobre 2026)
    for (cx, cy) in ((dep - 0.05, y0 + 0.05), (dep - 0.14, y1 - 0.14)):
        out.append(bobine(cx, cy, 0, zh + 0.3, B))
    # Les tablettes restent libres ; dessus, le seul portrait (tri de la déco, 19 octobre 2026)
    out.append(cadre(0.45, y1 - 0.85, zh))
    out.append(badge("bibliotheque", 0.5, (y0 + y1) / 2, zh + 1.7))
    return meuble("bibliotheque", "".join(out))


def enfilade_tiroirs(meuble, badge):
    """Le meuble à tiroirs : un corps en bois tout rond sur des pieds en bobines, trois tiroirs
    carrés côte à côte, chacun avec son bouton en forme de fleur, d'une couleur différente (six
    tiroirs d'abord, puis trois empilés) ; un plateau épais, au dessus libre, sous la fenêtre."""
    B = M("droite")
    T = tons(B)
    x0, x1, y0, y1 = 3.1, 7.5, 0.1, 1.3
    zl, zt = N["pied"], N["pied"] + 1.56  # trois tiroirs carrés côte à côte, sur des pieds en galette (19 octobre 2026)
    out = [ombre_portee(x0, x1, y0, y1, 2.2, 0.22)]
    for (px, py) in ((x1 - 0.25, y0 + 0.25), (x0 + 0.25, y1 - 0.25), (x1 - 0.25, y1 - 0.25)):
        out.append(pied(px, py, zl + 0.04, B))
    out.append(boite(x0, x1, y0, y1, zl, zt, T, r=N["r"] + 2, bombe=N["bombe"]))
    yf = y1 + 0.006
    m, g = 0.14, 0.08
    larg = (x1 - x0 - 2 * m - 2 * g) / 3
    haut = zt - zl - 2 * m
    k = 0
    for rang in range(1):
        za = zl + m
        for col in range(3):
            a = x0 + m + col * (larg + g)
            b = a + larg
            out.append(face([(a, yf, za), (b, yf, za), (b, yf, za + haut), (a, yf, za + haut)], B["paroi"], r=N["rp"] + 2))
            out.append(trait([(a + 0.1, yf + 0.002, za + haut - 0.05), (b - 0.1, yf + 0.002, za + haut - 0.05)], B["reflet"], 1.4, 0.55))
            out.append(trait([(a + 0.08, yf + 0.002, za + 0.04), (b - 0.08, yf + 0.002, za + 0.04)], B["fond"], 1.2, 0.35))
            # Un bouton rond en bois, comme celui de la coiffeuse (des fleurs jusqu'au 18 octobre 2026)
            out.append(bouton((a + b) / 2, yf + 0.02, za + haut * 0.55, (B["cote"], B["face"], B["reflet"]), rayon=4.6))
            k += 1
    ep = N["ep"]
    out.append(boite(x0 - 0.1, x1 + 0.1, y0, y1 + 0.1, zt, zt + ep, T, r=N["r"], bombe=N["bombe"]))
    zh = zt + ep
    out.append(trait([(x0 + 0.2, y1 + 0.13, zh), (x1 - 0.15, y1 + 0.13, zh)], B["reflet"], 2.6, 0.9))
    out.append(trait([(x1 + 0.11, y0 + 0.2, zh - 0.06), (x1 + 0.11, y1 - 0.1, zh - 0.06)], B["reflet"], 2.0, 0.8))
    if "radio" in ETAGERE:
        out.append(radio_retro(x0 + 0.55, x0 + 1.75, y0 + 0.3, y0 + 0.95, zh))
    if "plante" in ETAGERE:
        out.append(PLANTES[PLANTE](x1 - 0.85, (y0 + y1) / 2 + 0.1, zh))  # à la place du pothos puis du pilea (19 octobre 2026)
    out.append(badge("deco", (x0 + x1) / 2, (y0 + y1) / 2, zh + 2.0))
    return meuble("deco", "".join(out))


ETAGERE = ("radio", "plante")  # la radio et le pothos, choisis par Pauline le 19 octobre 2026


RADIO = ("#F8F1E1", "#EADDC2", "#CBBC9F")  # le boîtier crème, aux touches roses (choix de Pauline, 19 octobre 2026)
RADIO_ROSE = ("#F6D3DA", "#E9B5BE", "#C98F9B")


def radio_retro(x0, x1, y0, y1, z):
    """Une petite radio des années 50 : un boîtier crème aux angles ronds, un haut-parleur rond rose
    à trous, deux boutons roses, une antenne chromée."""
    corps = RADIO
    h = 0.62
    out = [boite(x0, x1, y0, y1, z, z + h, corps, r=7, bombe=0.01)]
    yf = y1 + 0.005
    xh, zh = x0 + 0.42, z + h * 0.5
    out.append(trait([(x0 + 0.15, y1 + 0.01, z + h - 0.08), (x1 - 0.15, y1 + 0.01, z + h - 0.08)], "#FFFFFF", 1.4, 0.6))
    out.append(trait([(x0 + 0.15, y1 + 0.01, z + 0.09), (x1 - 0.15, y1 + 0.01, z + 0.09)], "#FFFFFF", 1.4, 0.6))
    out.append(disque(cercle_y(xh, yf, zh, 0.22), RADIO_ROSE[2]))
    out.append(disque(cercle_y(xh + 0.01, yf, zh + 0.01, 0.18), RADIO_ROSE[1]))
    for (dx, dz) in ((-0.08, 0.06), (0.0, 0.06), (0.08, 0.06), (-0.08, -0.03), (0.0, -0.03), (0.08, -0.03), (-0.04, -0.11), (0.04, -0.11)):
        sx, sy = p(xh + dx, yf, zh + dz)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1" fill="{RADIO_ROSE[2]}" opacity="0.9" />')
    for dz in (0.12, -0.12):
        sx, sy = p(x1 - 0.3, yf, zh + dz)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.6" fill="{RADIO_ROSE[2]}" /><circle cx="{sx + 0.3:.1f}" cy="{sy - 0.3:.1f}" r="2" fill="{RADIO_ROSE[1]}" /><circle cx="{sx + 0.7:.1f}" cy="{sy - 0.7:.1f}" r="1" fill="#FFFFFF" opacity="0.7" />')
    out.append(trait([(x1 - 0.3, y0 + 0.3, z + h), (x1 - 0.05, y0 + 0.15, z + h + 0.75)], "#9AA1A9", 1.6, 1))
    a = p(x1 - 0.05, y0 + 0.15, z + h + 0.75)
    out.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="1.8" fill="#C3C9D0" />')
    return "".join(out)


def tulipes(x, y, z):
    """Un bouquet de tulipes dans un vase crème tout rond au col court : cinq tiges qui s'ouvrent en
    éventail, des têtes en coupe rose poudré, pêche et blanches, deux longues feuilles. Des fleurs
    plutôt qu'une plante, à la demande de Pauline (19 octobre 2026)."""
    sx, sy = p(x, y, z)
    r = 10
    col_y = sy - 2 * r + 1
    out = [ombre_posee(sx, sy, r * 1.1, 4, 0.16)]
    # Les deux feuilles, derrière les tiges
    for (sens, haut) in ((-1, 24), (1, 20)):
        out.append(f'<path d="M{sx:.1f} {col_y:.1f} Q{sx + sens * 3:.1f} {col_y - haut * 0.6:.1f} {sx + sens * 12:.1f} {col_y - haut:.1f} '
                   f'Q{sx + sens * 6:.1f} {col_y - haut * 0.45:.1f} {sx + sens * 1.5:.1f} {col_y:.1f} Z" fill="{FEUILLE["fonce"]}" />')
    fleurs = (("#F6D3DA", "#E9B5BE", "#C98F9B"), ("#FBD9C2", "#F7B98F", "#E0905E"), ("#FFFFFF", "#F6EEE2", "#E2D5C1"),
              ("#F6D3DA", "#E9B5BE", "#C98F9B"), ("#FBD9C2", "#F7B98F", "#E0905E"))
    for (dx, haut, c) in zip((-11, -5, 1, 7, 12), (26, 34, 38, 32, 24), fleurs):
        tx, ty = sx + dx, col_y - haut
        # La tige finit sous la coupe, au point où la fleur, inclinée, est attachée
        incl = math.radians(dx * 1.2)
        bx, by = tx - 1.5 * math.sin(incl), ty + 1.5 * math.cos(incl)
        out.append(f'<path d="M{sx + dx * 0.15:.1f} {col_y + 1:.1f} Q{sx + dx * 0.3:.1f} {col_y - haut * 0.55:.1f} {bx:.1f} {by:.1f}" '
                   f'fill="none" stroke="#6F9A55" stroke-width="1.5" stroke-linecap="round" />')
        out.append(f'<g transform="translate({tx:.1f} {ty:.1f}) rotate({dx * 1.2:.0f})">'
                   f'<path d="M-5 0 Q-6.5 -7 -3.5 -10.5 L0 -7.5 L3.5 -10.5 Q6.5 -7 5 0 Q0 4.5 -5 0 Z" fill="{c[2]}" />'
                   f'<path d="M-4 0.5 Q-5 -6 -2.5 -9 L0 -6.5 L2.5 -9 Q5 -6 4 0.5 Q0 3.5 -4 0.5 Z" fill="{c[1]}" />'
                   f'<path d="M-2 0 Q-2.5 -6 0 -9.5 Q2.5 -6 2 0 Q0 1.5 -2 0 Z" fill="{c[0]}" /></g>')
    # Le vase : une boule crème et un col court, ombrés à gauche
    out.append(f'<rect x="{sx - 4:.1f}" y="{col_y - 1:.1f}" width="8" height="5" rx="1.5" fill="#E5D8C3" />'
               f'<ellipse cx="{sx:.1f}" cy="{col_y - 1:.1f}" rx="4.5" ry="1.4" fill="#FBF5EA" />'
               f'<circle cx="{sx:.1f}" cy="{sy - r:.1f}" r="{r:.1f}" fill="#E5D8C3" />'
               f'<circle cx="{sx + 1.5:.1f}" cy="{sy - r - 0.8:.1f}" r="{r - 1.6:.1f}" fill="#FBF5EA" />'
               f'<path d="M{sx + 4:.1f} {sy - r - 5:.1f} Q{sx + 7:.1f} {sy - r - 2:.1f} {sx + 7:.1f} {sy - r + 2:.1f}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" />')
    return "".join(out)


PLANTES = {"tulipes": tulipes}  # la sansevieria, l'échévéria et la plante araignée, proposées le même jour, sont dans l'historique Git
PLANTE = "tulipes"  # ce qui fleurit sur l'étagère : des tulipes, choisies par Pauline le 19 octobre 2026


def livres_debout(x0, x1, ya, yb, z, haut, graine):
    """Une rangée de livres debout, de largeurs et de hauteurs variées, avec leurs filets."""
    rng = random.Random(graine)
    out, y = [], ya
    while True:
        w = rng.uniform(0.26, 0.32)
        if y + w > yb:
            break
        t = LIVRES[rng.randrange(len(LIVRES))]
        h = haut * rng.uniform(0.86, 1.0)
        xr = x1  # le dos des livres bien aligné au bord de la tablette (19 octobre 2026)
        out.append(boite(x0, xr, y, y + w, z, z + h, t, r=N["r_livre"] * 0.8))
        if rng.random() < 0.6:
            for zz in (z + h * 0.15, z + h * 0.85):
                out.append(trait([(xr, y + 0.03, zz), (xr, y + w - 0.03, zz)], t[2], 1.0, 0.9))
        y += w
    return "".join(out)


def coffre_osier(meuble, badge):
    """Le coffre en osier : un corps tressé miel, un couvercle bombé cerclé de laque noire, une
    poignée de cuir noir sur le côté, un linge plié dessus."""
    V = ROTIN
    x0, x1, y0, y1 = 10.45, 11.95, 7.7, 10.0
    z0, zc, zl = 0.16, 1.15, 1.6
    ym = (y0 + y1) / 2
    out = [ombre_portee(x0, x1, y0, y1, 2.2, 0.22)]
    for (px, py) in ((x0 + 0.25, y1 - 0.25), (x1 - 0.25, y0 + 0.25), (x1 - 0.25, y1 - 0.25)):
        out.append(pied(px, py, z0 + 0.04, M("pieds"), demi=0.1))
    out.append(boite(x0, x1, y0, y1, z0, zc, tons(V), r=N["r"], bombe=N["bombe"]))
    # Le tressage : des rangs sur les deux faces visibles, et des montants
    for k in range(1, 7):
        zz = z0 + (zc - z0) * k / 7
        out.append(trait([(x1 + 0.005, y0 + 0.1, zz), (x1 + 0.005, y1 - 0.1, zz)], V["grain"], 1.2, 0.85))
        out.append(trait([(x0 + 0.1, y1 + 0.005, zz), (x1 - 0.1, y1 + 0.005, zz)], V["fond"], 1.1, 0.6))
    yy = y0 + 0.25
    while yy < y1 - 0.15:
        out.append(trait([(x1 + 0.006, yy, z0 + 0.06), (x1 + 0.006, yy, zc - 0.04)], V["cote"], 1.0, 0.7))
        yy += 0.3
    out.append(boite(x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, zc, zl, tons(V), r=N["r"] + 6, bombe=0.04))
    # Un bord de couvercle tressé, dans l'osier même
    out.append(trait([(x1 + 0.055, y0 + 0.05, zc + 0.04), (x1 + 0.055, y1 + 0.02, zc + 0.04)], V["cote"], 3.0, 0.9))
    out.append(trait([(x0 + 0.05, y1 + 0.055, zc + 0.04), (x1 + 0.03, y1 + 0.055, zc + 0.04)], V["fond"], 3.0, 0.6))
    out.append(trait([(x1 + 0.03, y0 + 0.25, zl), (x1 + 0.03, y1 - 0.25, zl)], V["reflet"], 2.4, 0.8))
    out.append(badge("coffre", (x0 + x1) / 2, (y0 + y1) / 2, 3.0))
    return meuble("coffre", "".join(out))


ORANGE_TISSU = ("#F7B07F", "#F08A4B", "#D16A2E")  # l'orange du fauteuil, adouci par la palette (19 octobre 2026)


ACCOUDOIRS = "devant"  # le dossier fait toute la largeur, les accoudoirs partent de sa face avant (choix de Pauline, 19 octobre 2026)


def fauteuil_rose():
    """Le fauteuil du coin lecture : un fauteuil cozy et mignon en tissu orange (rose jusqu'au 17 octobre 2026), large et bas, à
    l'assise profonde, aux accoudoirs dodus plus bas que le dossier, un dossier arrondi, un coussin bonbon White Rabbit (le petit coussin crème est retiré le 19 octobre 2026), sur des pieds boules en teck. Construit comme le
    canapé que Pauline avait aimé, en une place, aux proportions d'un vrai fauteuil."""
    x0, x1, y0, y1 = 0.35, 1.95, 8.6, 10.6
    T = ORANGE_TISSU
    zs = 0.26                      # le dessous de l'assise, au-dessus des pieds
    rb = N["r"] + 6
    out = [ombre_portee(x0, x1, y0, y1, 2.05), ombre_mur(y1, 2.05, 0.8, 0.07)]
    for (px, py) in ((x1 - 0.25, y0 + 0.25), (x1 - 0.25, y1 - 0.25), (x0 + 0.25, y1 - 0.25)):
        out.append(pied(px, py, zs + 0.04, M("pieds"), demi=0.1))
    # Le dossier et l'accoudoir du fond, selon la construction choisie (ACCOUDOIRS, 19 octobre 2026) :
    # « encadrent » : les accoudoirs vont du mur à l'avant, le dossier est pris entre eux ;
    # « devant » : le dossier fait toute la largeur, les accoudoirs partent de sa face avant ;
    # « roules » : comme « devant », avec des accoudoirs bas surmontés d'un gros boudin arrondi
    def accoudoir(ya, yb):
        if ACCOUDOIRS == "encadrent":
            return boite(x0, x1, ya, yb, zs, 1.3, T, r=rb, bombe=0.03 + N["bombe"])
        if ACCOUDOIRS == "devant":
            return boite(x0 + 0.5, x1, ya, yb, zs, 1.3, T, r=rb, bombe=0.03 + N["bombe"])
        return (boite(x0 + 0.5, x1 - 0.04, ya + 0.04, yb - 0.04, zs, 1.05, T, r=rb, bombe=0.02)
                + boite(x0 + 0.46, x1 + 0.02, ya - 0.03, yb + 0.03, 1.0, 1.42, T, r=rb + 8, bombe=0.06))
    dossier = (boite(x0, x0 + 0.58, y0 + 0.46, y1 - 0.46, zs, 2.05, T, r=rb + 4, bombe=0.03 + N["bombe"]) if ACCOUDOIRS == "encadrent"
               else boite(x0, x0 + 0.58, y0, y1, zs, 2.05, T, r=rb + 4, bombe=0.03 + N["bombe"]))
    if ACCOUDOIRS == "encadrent":
        out += [accoudoir(y0, y0 + 0.46), dossier]   # l'accoudoir du fond est derrière le dossier
    else:
        out += [dossier, accoudoir(y0 - 0.1, y0 + 0.36)]  # un peu décalé vers la bibliothèque, à la demande de Pauline
    out.append(boite(x0 + 0.45, x1 - 0.04, y0 + 0.46, y1 - 0.4, zs, 0.82, T, r=N["r"]))
    # Le coussin d'assise s'arrête avant l'accoudoir du fond, dont on voit le flanc (19 octobre 2026)
    out.append(boite(x0 + 0.5, x1 - 0.02, y0 + 0.54, y1 - 0.44, 0.82, 1.16, T, r=rb, bombe=0.035))
    out.append(trait([(x1 - 0.05, y0 + 0.72, 1.16), (x1 - 0.05, y1 - 0.75, 1.16)], "#FFE6CC", 2.0, 0.85))
    # En biais sur l'assise, contre le dossier : à l'écran, il est couché à l'horizontale (19 octobre 2026)
    out.append(coussin_bonbon((x0 + 0.52, y0 + 1.42, 1.16), (x0 + 1.3, y0 + 0.64, 1.16)))
    out.append(accoudoir(y1 - 0.46, y1))
    # Les reflets du tissu, sur le haut du dossier et des accoudoirs
    out.append(trait([(x0 + 0.56, y0 + 0.4, 2.05), (x0 + 0.56, y1 - 0.5, 2.05)], "#FFE6CC", 2.2, 0.85))
    z_haut = 1.42 if ACCOUDOIRS == "roules" else 1.3
    for ya in (y0 - 0.1, y1 - 0.46):
        out.append(trait([(x1 - 0.05, ya + 0.12, z_haut), (x1 - 0.05, ya + 0.36, z_haut)], "#FFE6CC", 2.0, 0.85))
    return "".join(out)


def coussin_bonbon(arriere, avant):
    """Le coussin bonbon White Rabbit, d'après la photo de Pauline (19 octobre 2026) : un traversin
    crème posé sur l'assise, du dossier vers l'avant, l'emballage du bonbon imprimé dessus (deux filets rouges,
    l'ovale noir, le lapin blanc cerné de bleu, les taches rouge et bleue, le nom en rouge), et aux
    deux bouts l'emballage tortillé, bleu aux lapins blancs. Dessiné à l'écran le long de son axe,
    en volume : un dégradé de cylindre sur le corps, des bouts ombrés et plissés."""
    r = 6.6                                    # le rayon du traversin, en pixels
    a, b = p(arriere[0], arriere[1], arriere[2] + r / S), p(avant[0], avant[1], avant[2] + r / S)
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    longueur = math.hypot(b[0] - a[0], b[1] - a[1])
    angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    lb = longueur * 0.33                       # la demi-longueur du corps
    bleu, rouge = "#2F5BD6", "#E2453F"
    # Les dégradés du cylindre, perpendiculaires à l'axe : clair en haut (la lumière), ombré en bas
    defs = (f'<defs><linearGradient id="bonbon-corps" gradientUnits="userSpaceOnUse" x1="0" y1="{-r}" x2="0" y2="{r}">'
            '<stop offset="0" stop-color="#FFFFFF" /><stop offset="0.3" stop-color="#FBF7EE" /><stop offset="0.75" stop-color="#E9E1D2" />'
            '<stop offset="1" stop-color="#CFC3AE" /></linearGradient>'
            f'<linearGradient id="bonbon-bout" gradientUnits="userSpaceOnUse" x1="0" y1="{-r * 1.4:.1f}" x2="0" y2="{r * 1.4:.1f}">'
            '<stop offset="0" stop-color="#5C82F0" /><stop offset="0.45" stop-color="#2F5BD6" /><stop offset="1" stop-color="#1E3E9E" /></linearGradient></defs>')

    def bout(sens):
        """L'emballage tortillé d'un bout : l'éventail bleu, plissé, aux lapins blancs, puis le pincement."""
        x0, x1 = sens * lb, sens * (longueur / 2 + 1.5)
        bout_long = abs(x1 - x0)
        # L'éventail aux coins arrondis (19 octobre 2026 : plus de pointes)
        e = (f'M{x0 + sens * 2.2:.1f} 0 Q{x0 + sens * 4.5:.1f} {-r * 0.95:.1f} {x1 - sens * 1.4:.1f} {-r * 1.22:.1f} '
             f'Q{x1 + sens * 0.4:.1f} {-r * 1.42:.1f} {x1 + sens * 0.9:.1f} {-r * 0.8:.1f} '
             f'Q{x1 + sens * 1.7:.1f} 0 {x1 + sens * 0.9:.1f} {r * 0.8:.1f} '
             f'Q{x1 + sens * 0.4:.1f} {r * 1.42:.1f} {x1 - sens * 1.4:.1f} {r * 1.22:.1f} '
             f'Q{x0 + sens * 4.5:.1f} {r * 0.95:.1f} {x0 + sens * 2.2:.1f} 0 Z')
        lapins = "".join(f'<ellipse cx="{x0 + sens * bout_long * d:.1f}" cy="{h:.1f}" rx="1.4" ry="0.95" fill="#FFFFFF" />'
                         for d, h in ((0.5, -2.4), (0.62, 2.4), (0.85, -5.2), (0.88, 5.0)))
        plis = "".join(f'<path d="M{x0 + sens * 2.6:.1f} {k * 0.4:.1f} L{x1 - sens * 0.4:.1f} {k * 1.5:.1f}" stroke="#1B3890" stroke-width="0.6" opacity="0.55" />'
                       for k in (-3, -1, 1, 3))
        reflet = (f'<path d="M{x0 + sens * 3.5:.1f} {-r * 0.55:.1f} Q{x0 + sens * bout_long * 0.6:.1f} {-r * 0.95:.1f} {x1 - sens * 1:.1f} {-r * 1.1:.1f}" '
                  'fill="none" stroke="#9DB6FF" stroke-width="1" stroke-linecap="round" opacity="0.8" />')
        pince = (f'<ellipse cx="{x0 + sens * 1.3:.1f}" cy="0" rx="1.8" ry="{r * 0.42:.1f}" fill="#1E3E9E" />'
                 f'<ellipse cx="{x0 + sens * 1.1:.1f}" cy="-0.6" rx="1" ry="{r * 0.25:.1f}" fill="#5C82F0" />')
        return '<path d="' + e + '" fill="url(#bonbon-bout)" />' + plis + lapins + reflet + pince
    corps = (f'<rect x="{-lb:.1f}" y="{-r:.1f}" width="{2 * lb:.1f}" height="{2 * r:.1f}" rx="{r * 0.5:.1f}" fill="url(#bonbon-corps)" />'
             # L'imprimé : deux filets rouges, le nom, l'ovale noir et son lapin, les taches
             f'<path d="M{-lb * 0.62:.1f} {-r * 0.8:.1f} V{r * 0.35:.1f} M{-lb * 0.5:.1f} {-r * 0.8:.1f} V{r * 0.35:.1f}" stroke="{rouge}" stroke-width="0.7" />'
             f'<path d="M{-lb * 0.3:.1f} {-r * 0.62:.1f} H{lb * 0.45:.1f}" stroke="{rouge}" stroke-width="1" stroke-dasharray="1.2 0.5" />'
             f'<ellipse cx="{lb * 0.05:.1f}" cy="{r * 0.12:.1f}" rx="{r * 0.92:.1f}" ry="{r * 0.58:.1f}" fill="#1E1E24" />'
             f'<ellipse cx="{-lb * 0.06:.1f}" cy="{r * 0.27:.1f}" rx="{r * 0.48:.1f}" ry="{r * 0.26:.1f}" fill="#FFFFFF" stroke="{bleu}" stroke-width="0.7" />'
             f'<path d="M{-lb * 0.15:.1f} {r * 0.12:.1f} l-0.5 -2.9 M{-lb * 0.08:.1f} {r * 0.12:.1f} l0.2 -2.9" stroke="#FFFFFF" stroke-width="1" stroke-linecap="round" />'
             f'<circle cx="{lb * 0.3:.1f}" cy="{-r * 0.1:.1f}" r="1.3" fill="{rouge}" /><circle cx="{lb * 0.13:.1f}" cy="{r * 0.02:.1f}" r="1" fill="{bleu}" />'
             f'<path d="M{lb * 0.24:.1f} {r * 0.7:.1f} q1.7 -1.3 3.4 0" fill="{rouge}" />'
             # La lumière sur le haut du cylindre, et l'ombre douce le long du bas
             f'<path d="M{-lb * 0.85:.1f} {-r * 0.6:.1f} H{lb * 0.8:.1f}" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity="0.85" />'
             f'<path d="M{-lb * 0.9:.1f} {r * 0.85:.1f} H{lb * 0.9:.1f}" stroke="#B8AA92" stroke-width="1.2" stroke-linecap="round" opacity="0.5" />')
    ombre = (f'<ellipse cx="{cx - 2:.1f}" cy="{cy + r + 1.5:.1f}" rx="{longueur * 0.45:.1f}" ry="3" fill="#3B2418" opacity="0.16" '
             f'transform="rotate({angle:.1f} {cx:.1f} {cy:.1f})" />')
    return ombre + f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({angle:.1f})">' + defs + bout(1) + bout(-1) + corps + '</g>'


def table_toupie(x, y):
    """Une table d'appoint laquée crème, faite de disques empilés comme des toupies, et
    dessus, au centre, une lampe champignon chromée allumée, d'après la dernière photo."""
    sx, sy = p(x, y, 0)
    k = S
    rx = 0.5 * k * 1.22
    out = [ombre_ellipse(sx, sy, rx * 1.05, rx * 0.55, 0.2)]
    # Trois toupies empilées, de bas en haut, puis le plateau
    y_cour = sy
    for _ in range(3):
        h = 0.48 * k
        cy = y_cour - h / 2
        out.append(f'<ellipse cx="{sx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{h * 0.58:.1f}" fill="{LAQUE_CREME["cote"]}" />'
                   f'<ellipse cx="{sx + rx * 0.12:.1f}" cy="{cy - 1:.1f}" rx="{rx * 0.78:.1f}" ry="{h * 0.5:.1f}" fill="{LAQUE_CREME["face"]}" />'
                   f'<path d="M{sx + rx * 0.45:.1f} {cy - h * 0.3:.1f} Q{sx + rx * 0.8:.1f} {cy - h * 0.1:.1f} {sx + rx * 0.7:.1f} {cy + h * 0.2:.1f}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.7" />')
        y_cour -= h * 0.82
    plateau = y_cour - 2
    out.append(f'<ellipse cx="{sx:.1f}" cy="{plateau + 4:.1f}" rx="{rx * 1.05:.1f}" ry="{rx * 0.5:.1f}" fill="{LAQUE_CREME["cote"]}" />'
               f'<ellipse cx="{sx:.1f}" cy="{plateau:.1f}" rx="{rx * 1.05:.1f}" ry="{rx * 0.5:.1f}" fill="{LAQUE_CREME["haut"]}" />'
               f'<path d="M{sx + rx * 0.2:.1f} {plateau - rx * 0.35:.1f} Q{sx + rx * 0.75:.1f} {plateau - rx * 0.25:.1f} {sx + rx * 0.9:.1f} {plateau:.1f}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.8" />')
    # La lampe champignon chromée, au centre du plateau
    lx, ly = sx, plateau + 1
    out.append(f'<circle cx="{lx:.1f}" cy="{ly - 34:.1f}" r="34" fill="#FFD98A" opacity="0.18" />'
               f'<g class="vue vue-nuit"><circle cx="{lx:.1f}" cy="{ly - 34:.1f}" r="50" fill="#FFC977" opacity="0.14" />'
               f'<circle cx="{lx:.1f}" cy="{ly - 34:.1f}" r="36" fill="#FFE3A6" opacity="0.18" /></g>')
    out.append(f'<rect x="{lx - 7:.1f}" y="{ly - 30:.1f}" width="14" height="30" rx="2" fill="#7D838A" />'
               f'<rect x="{lx - 3:.1f}" y="{ly - 30:.1f}" width="5" height="30" fill="#E9ECEF" />'
               f'<rect x="{lx + 3:.1f}" y="{ly - 30:.1f}" width="3" height="30" fill="#A9AFB5" />'
               f'<ellipse cx="{lx:.1f}" cy="{ly - 31:.1f}" rx="13" ry="3.2" fill="#FFF1C8" />'
               f'<path d="M{lx - 15:.1f} {ly - 32:.1f} Q{lx - 15:.1f} {ly - 52:.1f} {lx:.1f} {ly - 52:.1f} Q{lx + 15:.1f} {ly - 52:.1f} {lx + 15:.1f} {ly - 32:.1f} Z" fill="#8A9097" />'
               f'<path d="M{lx - 6:.1f} {ly - 51:.1f} Q{lx + 8:.1f} {ly - 51:.1f} {lx + 11:.1f} {ly - 33:.1f} L{lx + 2:.1f} {ly - 33:.1f} Q{lx - 1:.1f} {ly - 46:.1f} {lx - 6:.1f} {ly - 51:.1f} Z" fill="#DDE1E5" />'
               f'<path d="M{lx - 2:.1f} {ly - 48:.1f} Q{lx + 4:.1f} {ly - 47:.1f} {lx + 6:.1f} {ly - 40:.1f}" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" />')
    # Une tasse de café fumante, vert foncé, sans anse (19 octobre 2026), à côté de la lampe
    mx, my = sx - rx * 0.6, plateau + 3
    out.append(
               f'<rect x="{mx - 5.5:.1f}" y="{my - 11:.1f}" width="11" height="11" rx="2.6" fill="#355E40" />'
               f'<rect x="{mx - 0.5:.1f}" y="{my - 11:.1f}" width="6" height="11" rx="2.4" fill="#4E7D58" />'
               f'<ellipse cx="{mx:.1f}" cy="{my - 11:.1f}" rx="5.5" ry="1.8" fill="#7FA488" />'
               f'<ellipse cx="{mx:.1f}" cy="{my - 10.6:.1f}" rx="4.2" ry="1.2" fill="#9A6A48" />'
               f'<path d="M{mx - 1:.1f} {my - 15:.1f} q-3 -4 0 -8 q3 -4 0 -8" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" opacity="0.8" />')
    return "".join(out)


# ---------- La déco, jamais cliquable ----------
# La lueur de la lampe est posée sur le sol, sous les meubles : elle réchauffe la pièce sans
# voiler le mobilier (leçon de la v3). Plus de lueurs sur les murs (19 octobre 2026).


TAPIS = dict(dessus="#F3E8D3", tranche="#D6C3A2", reflet="#FFFBF2", ombre="#E7D8BC", couture="#9E3B4F")  # crème aux coutures bordeaux (19 octobre 2026, kaki citron avant)


def grand_tapis(x0, x1, y0, y1):
    """Le grand tapis du milieu de la pièce : uni, en forme organique arrondie comme une flaque
    douce, crème, au bord roulé et à la couture piquée bordeaux."""
    e = 0.07
    T = TAPIS
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2

    def contour(k, z, dx=0.0, dy=0.0, n=96):
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            f = 1 + 0.09 * math.sin(3 * a + 0.4) + 0.05 * math.sin(5 * a + 1.3)
            pts.append((cx + dx + k * rx * f * math.cos(a), cy + dy + k * ry * f * math.sin(a), z))
        return pts
    out = [disque(contour(1.02, 0, 0.12, 0.25), OMBRE, ' opacity="0.12"'),
           disque(contour(1.0, 0), T["tranche"]),
           disque(contour(1.0, e), T["dessus"]),
           disque(contour(0.9, e), T["ombre"]),
           disque(contour(0.88, e), T["dessus"])]
    # La couture piquée, comme sur un tapis tufté
    pts = [p(*q) for q in contour(0.8, e)]
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} " + " ".join(f"L{a:.1f} {b:.1f}" for a, b in pts[1:]) + " Z"
    out.append(f'<path d="{d}" fill="none" stroke="{T["couture"]}" stroke-width="1.6" stroke-dasharray="5 4" stroke-linecap="round" opacity="0.9" />')
    out.append(trait(contour(0.97, e)[-14:] + contour(0.97, e)[:6], T["reflet"], 2.6, 0.9))
    return "".join(out)


def decor_mcm():
    """La déco cozy : ce qui est posé à plat (tapis, lumière au sol), puis les objets debout avec
    leur emprise au sol."""
    # Un seul grand tapis au milieu de la pièce, à la place des deux petits (Pauline, 17 octobre 2026)
    a_plat = [grand_tapis(2.6, 9.8, 2.9, 9.7), flaque(1.3, 11.0, 66, 38, 0.22)]
    # La plante, à gauche du coffre, un peu en retrait pour ne pas le cacher
    debout = [((10.4, 11.4, 11.1, 12.0), cactus_pot(10.9, 11.55))]
    return "".join(a_plat), debout


def flaque(x, y, rx, ry, opacite=0.16):
    """Une flaque de lumière chaude au sol, en aplat, posée avant les meubles."""
    sx, sy = p(x, y, 0)
    return f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#FFD98A" opacity="{opacite}" />'


def pot_fleur(x, y, z, taille=1.0):
    """Le vase de la coiffeuse : un soliflore bleu cobalt au long col, et une marguerite blanche au
    cœur jaune sur une tige qui penche un peu, avec deux longues feuilles."""
    sx, sy = p(x, y, z)
    k = S * taille
    h = 0.78 * k
    pied_y = sy - h
    cx, cy = sx + 3, pied_y - 0.75 * k
    out = [f'<path d="M{sx:.1f} {pied_y + 2:.1f} Q{sx - 3:.1f} {pied_y - 0.5 * k:.1f} {cx:.1f} {cy + 6:.1f}" fill="none" '
           f'stroke="#6F9A55" stroke-width="2.2" stroke-linecap="round" />',
           feuille(sx - 1, pied_y + 1, -28, 0.62 * k, 0.11 * k), feuille(sx + 1, pied_y + 1, 22, 0.5 * k, 0.1 * k)]
    # La marguerite : douze pétales blancs autour d'un cœur jaune
    for i in range(12):
        a = 2 * math.pi * i / 12
        px, py = cx + 7 * math.cos(a), cy + 6 * math.sin(a)
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="4.2" ry="2.1" fill="{"#FFFFFF" if i % 2 else "#F7F1E6"}" '
                   f'transform="rotate({math.degrees(a):.0f} {px:.1f} {py:.1f})" />')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#E9A82E" />'
               f'<circle cx="{cx + 0.8:.1f}" cy="{cy - 0.8:.1f}" r="2.8" fill="#F5C64C" />')
    # Le soliflore : une boule et un long col, ombrés à gauche, éclairés à droite
    c = ("#A9BDF5", "#4A67D8", "#3550B4")
    r = 0.22 * k
    by = sy - r * 0.95
    out.append(f'<rect x="{sx - 0.055 * k:.1f}" y="{sy - h:.1f}" width="{0.11 * k:.1f}" height="{h - r:.1f}" rx="2" fill="{c[2]}" />'
               f'<rect x="{sx - 0.01 * k:.1f}" y="{sy - h:.1f}" width="{0.06 * k:.1f}" height="{h - r:.1f}" rx="2" fill="{c[1]}" />'
               f'<ellipse cx="{sx:.1f}" cy="{sy - h:.1f}" rx="{0.08 * k:.1f}" ry="{0.035 * k:.1f}" fill="{c[0]}" />'
               f'<ellipse cx="{sx:.1f}" cy="{by:.1f}" rx="{r:.1f}" ry="{r * 0.95:.1f}" fill="{c[2]}" />'
               f'<ellipse cx="{sx + r * 0.15:.1f}" cy="{by - r * 0.08:.1f}" rx="{r * 0.76:.1f}" ry="{r * 0.78:.1f}" fill="{c[1]}" />'
               f'<ellipse cx="{sx + r * 0.42:.1f}" cy="{by - r * 0.35:.1f}" rx="{r * 0.16:.1f}" ry="{r * 0.26:.1f}" fill="#FFFFFF" opacity="0.7" />')
    return "".join(out)


def cactus_pot(x, y):
    """Un cactus tout rond et dodu, à deux bras levés, dans un pot en terre cuite : des côtes
    claires, de petites épines, et une fleur rouge sur la tête (rose jusqu'au 18 octobre 2026)."""
    sx, sy = p(x, y, 0)
    w, h = 1.0 * S, 0.8 * S
    base_y = sy - h
    vert, clair, cote = "#7FAE63", "#A6CC87", "#5E8A4C"
    out = [ombre_ellipse(sx, sy + 2, w * 0.7, w * 0.3, 0.17)]
    # Les deux bras, derrière le corps
    for (bx, by, hx, hy) in ((-11, -34, -24, -60), (11, -46, 23, -70)):
        d = f"M{sx + bx:.1f} {base_y + by:.1f} L{sx + hx:.1f} {base_y + by:.1f} L{sx + hx:.1f} {base_y + hy:.1f}"
        out.append(f'<path d="{d}" fill="none" stroke="{cote}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" />'
                   f'<path d="{d}" fill="none" stroke="{vert}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" />'
                   f'<path d="M{sx + hx + 2:.1f} {base_y + by - 3:.1f} L{sx + hx + 2:.1f} {base_y + hy + 2:.1f}" stroke="{clair}" stroke-width="2.4" stroke-linecap="round" />')
    # Le corps, ses côtes, ses épines
    out.append(f'<rect x="{sx - 13:.1f}" y="{base_y - 80:.1f}" width="26" height="84" rx="13" fill="{cote}" />'
               f'<rect x="{sx - 11:.1f}" y="{base_y - 78:.1f}" width="22" height="80" rx="11" fill="{vert}" />'
               f'<rect x="{sx - 1:.1f}" y="{base_y - 75:.1f}" width="9" height="72" rx="4.5" fill="{clair}" />')
    for dx in (-6, 0.5, 7):
        out.append(f'<path d="M{sx + dx:.1f} {base_y - 72:.1f} V{base_y - 4:.1f}" stroke="{cote}" stroke-width="1" opacity="0.45" />')
    for (dx, dy) in ((-8, -60), (-3, -40), (5, -64), (9, -30), (-7, -18), (3, -12), (-9, -48), (6, -50)):
        out.append(f'<path d="M{sx + dx - 1.5:.1f} {base_y + dy:.1f} h3 M{sx + dx:.1f} {base_y + dy - 1.5:.1f} v3" stroke="#FFFFFF" stroke-width="0.9" opacity="0.85" />')
    # La fleur rose sur la tête
    fx, fy = sx + 1, base_y - 80
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        out.append(f'<ellipse cx="{fx + 5 * math.cos(a):.1f}" cy="{fy + 4 * math.sin(a):.1f}" rx="4.6" ry="3.6" fill="#E2453F" />')
    out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3" fill="#F2C14E" />')
    out.append(pot(sx, sy, w, h, TERRE_CUITE))
    return "".join(out)


def derriere(a, b):
    """Vrai si l'emprise a est entièrement derrière l'emprise b, le long de x ou de y : dans
    notre vue, plus x ou y est grand, plus un objet est proche de nous."""
    return a[1] <= b[0] + 1e-6 or a[3] <= b[2] + 1e-6


def ordonner(objets):
    """Le tri des moteurs isométriques : un objet n'est peint qu'une fois peints tous ceux qui
    sont derrière lui. Trier par le coin avant ne suffit pas pour un meuble long : l'armoire,
    longue le long du mur, passait devant la plante pourtant plus avancée dans la pièce."""
    reste, ordre = list(objets), []
    while reste:
        libres = [o for o in reste
                  if not any(derriere(d[0], o[0]) and not derriere(o[0], d[0]) for d in reste if d is not o)]
        choix = min(libres or reste, key=lambda o: o[0][0] + o[0][1] + o[0][2] + o[0][3])
        ordre.append(choix)
        reste.remove(choix)
    return ordre


def zen(meuble, badge):
    """La pièce : les murs et la fenêtre, puis ce qui est posé au sol (tapis, lumière, ombres),
    puis le mobilier et le décor debout, rangés par emprise au sol, en aplats nets."""
    OMBRES.clear()
    OMBRES_MUR.clear()
    a_plat, debout = decor_mcm()
    # L'emprise de chaque meuble, corniche, plateau et tabouret compris
    DEFS.clear()
    motifs_tissu("pois", pois_motif(), 0.9, 0.9, echelle=0.45)  # le léopard, remplacé par des pois le 17 octobre 2026
    meubles = [((0.0, 1.4, 0.68, 3.6), dressing_ouvert(meuble, badge)),
               ((3.0, 7.6, 0.1, 1.45), enfilade_tiroirs(meuble, badge)),
               ((0.0, 1.1, 4.62, 7.98), biblio_festons(meuble, badge)),
               ((0.35, 1.95, 8.6, 10.6), fauteuil_rose()),
               ((0.4, 1.2, 10.85, 11.65), table_toupie(0.8, 11.25)),
               ((8.89, 11.71, 0.1, 2.65), coiffeuse(meuble, badge)),
               ((10.4, 12.0, 7.65, 10.05), coffre_osier(meuble, badge))]
    tout = ordonner(meubles + debout)
    # Ce qui est posé au sol (tapis, lumière, ombres) est découpé à la forme du parquet : rien ne
    # déborde sur le socle de la pièce
    sol = [p(0, 0, 0), p(12, 0, 0), p(12, 12, 0), p(0, 12, 0)]
    decoupe = ('<clipPath id="sol-zen"><polygon points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in sol) + '" /></clipPath>')
    papier_defs, papier = murs()
    # Les murs restent lisses, hors du grain de papier : sur les photos de Pauline, ils sont unis
    murs_lisses = "<defs>" + papier_defs + "".join(DEFS) + "</defs>" + papier
    mur_g = [p(0, 0, 0), p(0, 12, 0), p(0, 12, H_MUR), p(0, 0, H_MUR)]
    mur_d = [p(0, 0, 0), p(12, 0, 0), p(12, 0, H_MUR), p(0, 0, H_MUR)]
    au_mur = (recoins() + ambiance([mur_g, mur_d], lueurs_nuit_murs()) + halo_fenetre() + "".join(OMBRES_MUR)
              + fenetre() + voilage() + guirlande())
    # Plus de grain de papier : sur le mobilier, il faisait un pointillé (retour de Pauline, 17 octobre 2026)
    return (murs_lisses + '<g class="zen-illustre">' + au_mur + decoupe
            + '<g clip-path="url(#sol-zen)">' + recoins_sol() + lumiere_fenetre() + a_plat + ambiance([sol], lueurs_nuit_sol()) + "".join(OMBRES) + '</g>'
            + '<g class="objets">' + "".join(svg for _, svg in tout) + "</g></g>")
