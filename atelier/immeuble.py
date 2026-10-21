"""L'immeuble de la porte d'entrée : le studio fermé, vu de dehors (21 octobre 2026), d'après les
deux références de Pauline : un petit immeuble d'habitation, pas un café. Un rendu « argile » :
une seule famille de couleur (le rose terracotta, proche du rose de l'app), des volumes simples et
ronds comme le mobilier, des traits épais, des fenêtres allumées au crépuscule.

Deux étages : le studio est au rez-de-chaussée, sa porte au milieu du pan de gauche ; au-dessus,
l'étage d'un voisin, avec son balcon et sa guirlande. Un plancher droit fait le tour des deux
façades entre les deux niveaux, et se prolonge en sol du balcon. Sur le toit, une cheminée et une
antenne ; sur le trottoir, un lampadaire.

Retours de Pauline du 21 octobre 2026 : retirer les détails trop petits (grille d'égout, interphone,
joints du trottoir, lames fines), des traits plus épais, des cadres de fenêtres plus épais, un
plancher d'étage droit, une barrière sur les trois côtés du balcon, une guirlande plus haute aux
boules régulièrement espacées, une antenne plus franche, des contrastes plus marqués entre ombre
et lumière.

Même repère, même projection et même lumière que la pièce : la lumière vient de la droite, une face
tournée vers +x est éclairée, une face tournée vers +y est à l'ombre, les dessus sont les plus clairs.

Usage, depuis maquette/ : python3 atelier/immeuble.py index.html
Il insère dans la page, entre les marqueurs <!-- IMMEUBLE --> et <!-- /IMMEUBLE -->, un modèle
(<template id="immeuble">) : un SVG à poser par-dessus la pièce, au même repère, en cinq calques (le
sol, les murs, les battants de la porte, ce qui est posé devant, le toit), pour que l'entrée les
fasse partir un à un. Il dépasse le cadre de la pièce : la page élargit le viewBox de la porte
d'entrée (VIEWBOX, repris dans data-viewbox). Mis au point dans planches/navigation.html."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import piece_par_defaut as P  # noqa: E402

W, D = 12, 12
ZP = -0.7           # le dessus du trottoir ; le sol du studio est à 0, une marche plus haut
H1 = 9.6            # le plancher de l'étage
EP = 0.55           # son épaisseur
H2 = 14.6           # le haut de l'étage, sous le toit
XC = 5.75           # le milieu du pan de gauche, où est la porte
VIEWBOX = "15 -200 750 975"
ROND = 4.2          # le côté mimi, comme pour le mobilier : des angles bien ronds
DEFS = []

# ---------- La palette : une seule couleur, des tons nettement séparés ----------
# Trois familles de faces : les dessus, les plus clairs ; les faces au soleil (+x) ; les faces à
# l'ombre (+y), nettement plus sombres
MUR_SOLEIL = ("#F9D3C6", "#F1BFB0")   # haut et bas du pan éclairé
MUR_OMBRE = ("#CE8F80", "#BE7E71")    # haut et bas du pan à l'ombre
VOLUME = ("#FCE4DB", "#F4C3B4", "#C4837A")   # dessus, face au soleil, face à l'ombre
SOMBRE = ("#C88778", "#B3746A", "#955A50")
SOCLE = ("#F5CFC3", "#E6AE9E", "#B37669")
TROTTOIR = ("#FDEAE3", "#F3CCBF", "#C99082")
CADRE_SOLEIL = "#B97A6D"   # les cadres des fenêtres, épais, plus sombres que le mur
CADRE_OMBRE = "#8F564C"
VERRE_CHAUD = ("#FFF8EC", "#FFDDAE")
VERRE_ROSE = ("#FFE0EA", "#F59AB6")
VERRE_ETEINT = ("#9A6156", "#7F4B42")
OMBRE = "#6E3B33"
VERTS = ("#6F9160", "#89AC74", "#A6C58D")


def q(x, y, z):
    return P.p(x, y, z)


def forme(points3d, fill, r=0.0, extra="", bombe=0.0):
    return f'<path d="{P.chemin([q(*a) for a in points3d], r, bombe)}" fill="{fill}"{extra} />'


def sur_y(yc, pts):
    return [(x, yc, z) for x, z in pts]


def sur_x(xc, pts):
    return [(xc, y, z) for y, z in pts]


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


def degrade(stops, vertical=True):
    ident = f"ext-d{len(DEFS)}"
    x2, y2 = ("0", "1") if vertical else ("1", "0")
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}" />' for o, c, a in stops)
    DEFS.append(f'<linearGradient id="{ident}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>')
    return f"url(#{ident})"


def boite(x0, x1, y0, y1, z0, z1, t, r=2.5, bombe=0.0):
    """Un volume mimi, construit comme les meubles : sa silhouette arrondie dans le ton d'ombre, qui
    porte la rondeur et comble le creux des coins, puis ses trois faces aux angles doux.
    t : (dessus, face au soleil, face à l'ombre)."""
    rr = r * ROND
    silhouette = [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (x0, y1, z1)]
    return (forme(silhouette, t[2], rr, bombe=bombe)
            + forme([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], t[2], rr * 0.55)
            + forme([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], t[1], rr * 0.55)
            + forme([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], t[0], rr * 0.55))


def trait(a3, b3, couleur, largeur=3.0, opacite=1.0):
    a, b = q(*a3), q(*b3)
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{couleur}" stroke-width="{largeur}" '
            f'stroke-linecap="round" opacity="{opacite}" />')


def lueur(x, y, z, rayon, op=1.0):
    sx, sy = q(x, y, z)
    return f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{rayon:.1f}" ry="{rayon * 0.85:.1f}" fill="url(#ext-lueur)" opacity="{op}" />'


def arche(u0, u1, z0, z1, n=18, galbe=0.7):
    """Un contour au sommet en anse de panier, dans le plan d'une façade : (u, z)."""
    demi, um = (u1 - u0) / 2, (u0 + u1) / 2
    return ([(u0, z0), (u1, z0), (u1, z1)]
            + [(um + demi * math.cos(math.pi * k / n), z1 + demi * galbe * math.sin(math.pi * k / n)) for k in range(1, n)]
            + [(u0, z1)])


def definitions():
    DEFS.append('<radialGradient id="ext-lueur"><stop offset="0" stop-color="#FFD9A8" stop-opacity="0.65" />'
                '<stop offset="1" stop-color="#FFD9A8" stop-opacity="0" /></radialGradient>')
    DEFS.append('<radialGradient id="ext-lueur-froide"><stop offset="0" stop-color="#D6F0FF" stop-opacity="0.7" />'
                '<stop offset="1" stop-color="#D6F0FF" stop-opacity="0" /></radialGradient>')
    DEFS.append('<radialGradient id="ext-lueur-sol"><stop offset="0" stop-color="#FFE6C2" stop-opacity="0.8" />'
                '<stop offset="1" stop-color="#FFE6C2" stop-opacity="0" /></radialGradient>')


# ---------- Les fenêtres : un cadre épais, des croisillons francs, un appui dodu ----------


def fenetre(plan, u0, u1, z0, z1, verre=VERRE_CHAUD, arrondie=False, croisillon=True, appui=True, store=0.0):
    """Une fenêtre dans le pan de gauche (plan « y », u le long de x) ou de droite (plan « x », u le
    long de y). Le cadre est épais et plus sombre que le mur ; la vitre allumée ; le croisillon franc ;
    l'appui avance et prend la lumière sur le dessus."""
    sombre = plan == "y"
    poser = (lambda pts, e: sur_y(D + e, pts)) if sombre else (lambda pts, e: sur_x(W + e, pts))
    contour = arche if arrondie else rect
    cadre = CADRE_OMBRE if sombre else CADRE_SOLEIL
    k = 0.34   # l'épaisseur du cadre
    allumee = verre is not VERRE_ETEINT
    um, zm = (u0 + u1) / 2, (z0 + z1) / 2
    centre = (um, D + 0.01, zm) if sombre else (W + 0.01, um, zm)
    out = [lueur(*centre, 40 + 7 * (u1 - u0), 0.6) if allumee else ""]
    out.append(forme(poser(contour(u0 - k, u1 + k, z0 - k * 0.6, z1), 0.01), cadre, r=10))
    out.append(forme(poser(contour(u0, u1, z0, z1), 0.012), degrade([(0, verre[0], 1), (1, verre[1], 1)]), r=7))
    haut = z1 + ((u1 - u0) / 2 * 0.7 if arrondie else 0)
    if store:
        zs = haut - (haut - z0) * store
        out.append(forme(poser(arche(u0, u1, zs, z1) if arrondie else rect(u0, u1, zs, z1), 0.013), VOLUME[1] if sombre else VOLUME[0], r=7))
        for j in (1, 2):
            zz = zs + j * (min(z1, haut) - zs) / 3
            out.append(forme(poser(rect(u0, u1, zz - 0.06, zz + 0.06), 0.014), VOLUME[2], r=2))
    if croisillon:
        out.append(forme(poser(rect(um - 0.11, um + 0.11, z0, haut - 0.05), 0.015), cadre, r=3))
        zt = z0 + (z1 - z0) * 0.6
        out.append(forme(poser(rect(u0, u1, zt - 0.11, zt + 0.11), 0.015), cadre, r=3))
    if appui:
        if sombre:
            out.append(boite(u0 - k - 0.25, u1 + k + 0.25, D, D + 0.5, z0 - k * 0.6 - 0.35, z0 - k * 0.6, VOLUME, r=2))
        else:
            out.append(boite(W, W + 0.5, u0 - k - 0.25, u1 + k + 0.25, z0 - k * 0.6 - 0.35, z0 - k * 0.6, VOLUME, r=2))
    return "".join(out)


def buisson(sx, sy, k=1.0):
    """Une touffe de feuillage en boules, éclairée à droite."""
    out = []
    for (dx, dy, rr, c) in ((-7, 1, 9, VERTS[0]), (7, 0, 9, VERTS[0]), (0, -6, 10.5, VERTS[1]), (4, -10, 6, VERTS[2])):
        out.append(f'<circle cx="{sx + dx * k:.1f}" cy="{sy + dy * k:.1f}" r="{rr * k:.1f}" fill="{c}" />')
    return "".join(out)


def jardiniere(u0, u1, z):
    """Une jardinière sous une fenêtre du pan de gauche, avec trois grosses touffes fleuries."""
    out = [boite(u0, u1, D, D + 0.6, z - 0.7, z, SOMBRE, r=3)]
    for j in range(3):
        sx, sy = q(u0 + 0.5 + j * (u1 - u0 - 1.0) / 2, D + 0.3, z)
        out.append(buisson(sx, sy - 4, 0.85))
        out.append(f'<circle cx="{sx + 3:.1f}" cy="{sy - 12:.1f}" r="3.6" fill="#F7B2C6" /><circle cx="{sx + 3:.1f}" cy="{sy - 12:.1f}" r="1.4" fill="#FFF1C9" />')
    return "".join(out)


# ---------- Le sol ----------


def sol():
    """Le socle : une dalle épaisse, un trottoir plus clair le long des deux façades, et l'ombre de
    l'immeuble rejetée vers la gauche, du côté opposé à la lumière."""
    x1, y1 = 13.9, 13.9
    zt = ZP + 0.18
    out = [boite(-0.5, x1, -0.5, y1, ZP - 0.7, ZP, SOCLE, r=5),
           boite(W, W + 1.5, -0.5, D, ZP, zt, TROTTOIR, r=3),
           boite(-0.5, W + 1.5, D, D + 1.5, ZP, zt, TROTTOIR, r=3)]
    out.append(forme([(-0.5, D, zt), (W, D, zt), (W + 1.4, y1, ZP), (-0.5, y1, ZP)],
                     degrade([(0, OMBRE, 0.38), (1, OMBRE, 0.08)]), r=8))
    out.append(forme([(W, -0.5, zt), (W + 0.45, -0.5, zt), (W + 0.45, D, zt), (W, D, zt)], OMBRE, r=4, extra=' opacity="0.12"'))
    return "".join(out)


# ---------- Les murs ----------


def murs():
    silhouette = [(-0.5, D, ZP), (W, D, ZP), (W, -0.5, ZP), (W, -0.5, H2), (-0.5, -0.5, H2), (-0.5, D, H2)]
    out = [forme(silhouette, MUR_OMBRE[1], r=44),
           forme(sur_y(D, rect(-0.5, W, ZP, H2)), degrade([(0, MUR_OMBRE[0], 1), (1, MUR_OMBRE[1], 1)]), r=28),
           forme(sur_x(W, rect(-0.5, D, ZP, H2)), degrade([(0, MUR_SOLEIL[0], 1), (1, MUR_SOLEIL[1], 1)]), r=28)]
    # Le soubassement, l'ombre sous le toit et sous le plancher, l'arête de l'angle prise par la lumière
    out.append(forme(sur_y(D + 0.003, rect(-0.4, W - 0.1, ZP, ZP + 0.8)), SOMBRE[2], r=24, extra=' opacity="0.5"'))
    out.append(forme(sur_x(W + 0.003, rect(-0.4, D - 0.1, ZP, ZP + 0.8)), SOMBRE[0], r=24, extra=' opacity="0.45"'))
    out.append(forme(sur_y(D + 0.004, rect(-0.5, W, H2 - 1.0, H2)), degrade([(0, OMBRE, 0.3), (1, OMBRE, 0)]), r=22))
    out.append(forme(sur_x(W + 0.004, rect(-0.5, D, H2 - 0.8, H2)), degrade([(0, OMBRE, 0.16), (1, OMBRE, 0)]), r=22))
    out.append(forme(sur_y(D + 0.004, rect(-0.5, W, H1 - EP - 1.8, H1 - EP)), degrade([(0, OMBRE, 0.34), (1, OMBRE, 0)]), r=22))
    out.append(forme(sur_x(W + 0.004, rect(-0.5, D, H1 - EP - 1.4, H1 - EP)), degrade([(0, OMBRE, 0.2), (1, OMBRE, 0)]), r=22))
    out.append(trait((W, D, ZP + 0.3), (W, D, H2 - 0.3), "#FDE3DA", 3.2, 0.9))
    return "".join(out)


def rez_de_chaussee():
    """Le studio : la porte seule, au milieu du pan de gauche, dans un cadre épais, entre deux appliques
    (retour de Pauline, 21 octobre 2026 : plus de fenêtres de part et d'autre, plus d'imposte) ; sur le
    pan de droite, la fenêtre en arc à la lumière rose."""
    y = D + 0.01
    l, zh = 1.4, 6.0
    out = []
    # Le cadre épais, et l'entrée éclairée qu'on découvre en ouvrant
    out.append(forme(sur_y(y, rect(XC - l - 0.42, XC + l + 0.42, 0, zh + 0.42)), CADRE_OMBRE, r=9))
    out.append(forme(sur_y(y + 0.002, rect(XC - l, XC + l, 0, zh)), "#FFD9A0", r=5))
    out.append(forme(sur_y(y + 0.003, rect(XC - l + 0.5, XC + l - 0.3, 0, zh - 0.6)), "#FFF0D2", r=5, extra=' opacity="0.85"'))
    # Les deux appliques, rondes, et leur lumière sur le mur
    for xa in (XC - l - 1.05, XC + l + 1.05):
        sx, sy = q(xa, y, 5.3)
        out.append(lueur(xa, y, 5.2, 30, 0.95)
                   + f'<rect x="{sx - 6:.1f}" y="{sy - 10:.1f}" width="12" height="16" rx="6" fill="{SOMBRE[2]}" />'
                   + f'<rect x="{sx - 4:.1f}" y="{sy - 7:.1f}" width="8" height="11" rx="4" fill="#FFF1D6" />')
    out.append(fenetre("x", 6.6, 9.4, 2.5, 5.2, VERRE_ROSE, arrondie=True))  # échangée avec le distributeur, pour voir
    return "".join(out)


def plancher():
    """Le plancher de l'étage : une dalle droite qui fait le tour des deux façades. Pas de pente, pas
    de bombé : c'est un sol, il se prolonge en sol du balcon."""
    av = 0.75
    z0, z1 = H1 - EP, H1
    return (boite(W, W + av, -0.5, D, z0, z1, VOLUME, r=3)
            + boite(-0.5, W + av, D, D + av, z0, z1, VOLUME, r=3))


def balcon_sol(y0, y1, xb):
    """Le sol du balcon, dans le prolongement du plancher, à la même hauteur et de la même épaisseur."""
    return (forme(sur_x(W + 0.02, rect(y0, y1, H1, H1 + 0.7)), OMBRE, r=8, extra=' opacity="0.16"')
            + boite(W, xb, y0, y1, H1 - EP, H1, VOLUME, r=3))


def barriere(a, b, z0, hauteur, n, couleur_barreau, couleur_main):
    """Une barrière droite de a à b (au sol) : des barreaux épais régulièrement espacés et une main
    courante dodue."""
    out = []
    for j in range(n + 1):
        t = j / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        out.append(trait((x, y, z0), (x, y, z0 + hauteur), couleur_barreau, 3.4))
    out.append(trait((a[0], a[1], z0 + hauteur), (b[0], b[1], z0 + hauteur), couleur_main, 6.0))
    out.append(trait((a[0], a[1], z0 + hauteur + 0.04), (b[0], b[1], z0 + hauteur + 0.04), VOLUME[0], 2.0, 0.8))
    return "".join(out)


def guirlande(points, n_boules):
    """Une guirlande en festons, d'un point d'accroche au suivant, et des boules de lumière posées à
    distance régulière tout le long du fil."""
    chemin = []
    for (a, b) in zip(points, points[1:]):
        for i in range(0 if not chemin else 1, 41):
            t = i / 40
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            z = a[2] + (b[2] - a[2]) * t - 0.4 * math.sin(math.pi * t)
            chemin.append(q(x, y, z))
    longueurs = [0.0]
    for p0, p1 in zip(chemin, chemin[1:]):
        longueurs.append(longueurs[-1] + math.dist(p0, p1))
    total = longueurs[-1]
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(chemin))
    out = [f'<path d="{d}" fill="none" stroke="{OMBRE}" stroke-width="2.2" stroke-linecap="round" opacity="0.85" />']
    j = 0
    for k in range(n_boules):
        cible = total * (k + 0.5) / n_boules
        while longueurs[j + 1] < cible:
            j += 1
        t = (cible - longueurs[j]) / (longueurs[j + 1] - longueurs[j])
        sx = chemin[j][0] + (chemin[j + 1][0] - chemin[j][0]) * t
        sy = chemin[j][1] + (chemin[j + 1][1] - chemin[j][1]) * t
        out.append(f'<circle cx="{sx:.1f}" cy="{sy + 4:.1f}" r="11" fill="url(#ext-lueur)" />'
                   f'<circle cx="{sx:.1f}" cy="{sy + 4:.1f}" r="4.4" fill="#FFF4DC" />')
    return "".join(out)


def baie_angle(debut):
    """La baie vitrée de l'angle : elle passe sur les deux murs, de x = debut à l'angle sur le pan de
    gauche, puis de l'angle à y = debut sur le pan de droite. Des cadres épais, un poteau franc dans
    l'angle, un vantail au milieu de chaque pan."""
    z0, z1, k = H1 + 0.1, 13.5, 0.34
    vitre = [(0, VERRE_CHAUD[0], 1), (1, VERRE_CHAUD[1], 1)]
    out = [lueur((debut + W) / 2, D + 0.01, 11.8, 90, 0.7), lueur(W + 0.01, (debut + D) / 2, 11.8, 90, 0.6)]
    # Le pan de gauche, à l'ombre : le cadre, la vitre
    out.append(forme(sur_y(D + 0.01, rect(debut - k, W, z0, z1 + k)), CADRE_OMBRE, r=8))
    out.append(forme(sur_y(D + 0.012, rect(debut, W, z0, z1)), degrade(vitre), r=2))
    # Le pan de droite, au soleil
    out.append(forme(sur_x(W + 0.01, rect(debut - k, D, z0, z1 + k)), CADRE_SOLEIL, r=8))
    out.append(forme(sur_x(W + 0.012, rect(debut, D, z0, z1)), degrade(vitre), r=2))
    # Une seule vitre par pan (21 octobre 2026), une traverse haute qui fait le tour, un joint fin dans l'angle
    m = (debut + W) / 2
    zt = z1 - 1.0
    out.append(forme(sur_y(D + 0.014, rect(debut, W, zt - 0.11, zt + 0.11)), CADRE_OMBRE, r=1))
    out.append(forme(sur_x(W + 0.014, rect(debut, D, zt - 0.11, zt + 0.11)), CADRE_SOLEIL, r=1))
    out.append(trait((W + 0.015, D + 0.015, z0), (W + 0.015, D + 0.015, z1), "#FFFFFF", 1.6, 0.75))
    # Les reflets, en biais, sur chaque pan
    for (a3, b3) in (((W + 0.016, m + 1.1, z0 + 0.5), (W + 0.016, m + 0.4, z0 + 1.9)),
                     ((debut + 0.5, D + 0.016, z0 + 0.5), (debut + 1.2, D + 0.016, z0 + 1.9))):
        out.append(trait(a3, b3, "#FFFFFF", 4.0, 0.45))
    return "".join(out)


def etage():
    """L'étage du voisin (retours de Pauline, 21 octobre 2026) : à gauche, la fenêtre allumée, sans
    grille ; à droite, la fenêtre aux volets fermés ; dans l'angle, un balcon en enfilade sur les deux
    façades, devant une baie vitrée qui passe sur les deux murs, et la guirlande au-dessus."""
    out = [fenetre("y", 1.6, 3.8, 10.7, 13.3)]
    # La fenêtre aux volets fermés, sur le pan de droite : un cadre épais, quatre lames larges
    y0, y1 = 2.4, 4.8
    out.append(forme(sur_x(W + 0.01, rect(y0 - 0.34, y1 + 0.34, 10.4, 13.6)), CADRE_SOLEIL, r=10))
    out.append(forme(sur_x(W + 0.012, rect(y0, y1, 10.65, 13.35)), VOLUME[1], r=7))
    for j in range(1, 4):
        z = 10.65 + j * (13.35 - 10.65) / 4
        out.append(forme(sur_x(W + 0.014, rect(y0, y1, z - 0.08, z + 0.08)), VOLUME[2], r=2))
    out.append(boite(W, W + 0.5, y0 - 0.6, y1 + 0.6, 10.05, 10.4, VOLUME, r=2))
    # La baie de l'angle (la guirlande est retirée le 21 octobre 2026)
    # La baie commence plus loin de l'angle qu'avant (7,0), le balcon un peu avant elle (retour de
    # Pauline, 21 octobre 2026 : le début de la baie, contre le mur de gauche, faisait bizarre)
    out.append(baie_angle(9.0))
    debut = 9.0  # le balcon s'arrête au bord de la baie (raccourci le 21 octobre 2026, il partait de 8,0)
    # Le balcon d'angle : son sol en L, dans le prolongement du plancher, puis sa barrière, du fond
    # vers l'avant
    av, e = 1.8, 0.12
    out.append(forme(sur_y(D + 0.02, rect(debut - 0.4, W, H1, H1 + 0.7)), OMBRE, r=8, extra=' opacity="0.18"'))
    out.append(forme(sur_x(W + 0.02, rect(debut - 0.4, D, H1, H1 + 0.7)), OMBRE, r=8, extra=' opacity="0.14"'))
    out.append(boite(debut - 0.4, W, D, D + av, H1 - EP, H1, VOLUME, r=3))
    out.append(boite(W, W + av, debut - 0.4, D + av, H1 - EP, H1, VOLUME, r=3))
    x0b, y0b, xf, yf = debut - 0.4 + e, debut - 0.4 + e, W + av - e, D + av - e
    out.append(barriere((W + 0.1, y0b), (xf, y0b), H1, 1.3, 3, SOMBRE[1], SOMBRE[1]))
    out.append(barriere((x0b, D + 0.1), (x0b, yf), H1, 1.3, 3, SOMBRE[2], SOMBRE[2]))
    out.append(barriere((xf, y0b), (xf, yf), H1, 1.3, 7, SOMBRE[1], SOMBRE[1]))
    out.append(barriere((x0b, yf), (xf, yf), H1, 1.3, 7, SOMBRE[2], SOMBRE[2]))
    return "".join(out)


def battants():
    """La porte du studio, à deux battants, plus sombre que le mur, chacun avec une vitre haute allumée,
    un panneau bas et sa poignée ; chaque battant dans son groupe (battant-g, battant-d), pour que
    l'entrée le fasse pivoter sur ses gonds, vers l'intérieur (21 octobre 2026)."""
    y = D + 0.02
    l, zh = 1.4, 6.0
    out = []
    for (x0, x1, xp, classe) in ((XC - l, XC - 0.04, XC - 0.32, "battant-g"), (XC + 0.04, XC + l, XC + 0.32, "battant-d")):
        b = [forme(sur_y(y, rect(x0, x1, 0, zh)), degrade([(0, SOMBRE[0], 1), (1, SOMBRE[1], 1)]), r=6),
             forme(sur_y(y + 0.003, rect(x0 + 0.25, x1 - 0.25, 3.3, zh - 0.35)), degrade([(0, VERRE_CHAUD[0], 1), (1, VERRE_CHAUD[1], 1)]), r=6),
             forme(sur_y(y + 0.003, rect(x0 + 0.25, x1 - 0.25, 0.45, 2.8)), SOMBRE[2], r=6),
             forme(sur_y(y + 0.004, rect(x0 + 0.4, x1 - 0.25, 0.45, 2.65)), SOMBRE[1], r=5)]
        sx, sy = q(xp, y + 0.006, 3.0)
        b.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.4" fill="#F3D7A8" /><circle cx="{sx + 1:.1f}" cy="{sy - 1.2:.1f}" r="1.7" fill="#FFF6E2" />')
        out.append(f'<g class="{classe}">' + "".join(b) + "</g>")
    return "".join(out)


# ---------- Devant ----------


def distributeur(y0, y1):
    """Un distributeur de boissons contre le pan de droite, sur le trottoir, comme sur la photo : un
    gros volume arrondi, une vitrine allumée en bleu pâle avec trois rangées de bouteilles dodues, une
    colonne de boutons, la trappe en bas ; sa lumière froide sur le trottoir."""
    zt = ZP + 0.18
    x1, z1 = W + 1.15, zt + 4.6
    gx, gy = q(x1 + 0.2, (y0 + y1) / 2, zt)
    out = [f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="44" ry="20" fill="url(#ext-lueur-froide)" />',
           lueur(W + 0.01, (y0 + y1) / 2, zt + 3.0, 50, 0.0),
           boite(W, x1, y0, y1, zt, z1, (VOLUME[0], SOMBRE[0], SOMBRE[2]), r=5)]
    xf = x1 + 0.01
    vy0, vy1, vz0, vz1 = y0 + 0.75, y1 - 0.25, zt + 1.6, z1 - 0.35
    out.append(f'<ellipse cx="{q(xf, (vy0 + vy1) / 2, (vz0 + vz1) / 2)[0]:.1f}" cy="{q(xf, (vy0 + vy1) / 2, (vz0 + vz1) / 2)[1]:.1f}" rx="48" ry="44" fill="url(#ext-lueur-froide)" />')
    out.append(forme(sur_x(xf, rect(vy0, vy1, vz0, vz1)), degrade([(0, "#F4FBFF", 1), (1, "#BFE3F3", 1)]), r=7))
    # Trois rangées de bouteilles dodues, et l'étagère sous chacune
    couleurs = ("#F59AB6", "#FFFFFF", "#9ED3B4")
    for rang in range(3):
        zb = vz0 + 0.25 + rang * (vz1 - vz0 - 0.3) / 3
        out.append(forme(sur_x(xf + 0.002, rect(vy0 + 0.1, vy1 - 0.1, zb - 0.1, zb - 0.02)), "#8FC3DA", r=2))
        for j in range(3):
            yb = vy1 - 0.4 - j * (vy1 - vy0 - 0.8) / 2
            sx, sy = q(xf + 0.004, yb, zb)
            out.append(f'<rect x="{sx - 5:.1f}" y="{sy - 17:.1f}" width="10" height="17" rx="4" fill="{couleurs[(rang + j) % 3]}" />'
                       f'<rect x="{sx - 2.5:.1f}" y="{sy - 22:.1f}" width="5" height="6" rx="2" fill="{couleurs[(rang + j) % 3]}" />')
    # La colonne de boutons, la trappe
    out.append(forme(sur_x(xf, rect(y0 + 0.2, y0 + 0.6, zt + 1.9, z1 - 0.6)), SOMBRE[2], r=5))
    for j in range(3):
        sx, sy = q(xf + 0.003, y0 + 0.4, z1 - 1.2 - j * 0.65)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4" fill="#FFE7BE" />')
    out.append(forme(sur_x(xf, rect(vy0, vy1, zt + 0.55, zt + 1.15)), SOMBRE[2], r=6))
    return "".join(out)


def devant():
    """La marche de la porte, un gros pot de feuillage, et le lampadaire du trottoir, allumé."""
    zt = ZP + 0.18
    out = [distributeur(1.5, 4.3), boite(XC - 1.9, XC + 1.9, D, D + 0.85, zt, 0, VOLUME, r=3)]
    sx, sy = q(XC + 2.7, D + 0.7, zt)
    out.append(f'<ellipse cx="{sx - 4:.1f}" cy="{sy + 2:.1f}" rx="17" ry="6.5" fill="{OMBRE}" opacity="0.22" />')
    out.append(buisson(sx, sy - 30, 1.35))
    out.append(f'<path d="M{sx - 12:.1f} {sy - 20:.1f} L{sx + 12:.1f} {sy - 20:.1f} L{sx + 9:.1f} {sy:.1f} L{sx - 9:.1f} {sy:.1f} Z" fill="{SOMBRE[1]}" />'
               f'<path d="M{sx + 1:.1f} {sy - 20:.1f} L{sx + 12:.1f} {sy - 20:.1f} L{sx + 9:.1f} {sy:.1f} L{sx + 1:.1f} {sy:.1f} Z" fill="{VOLUME[1]}" />'
               f'<rect x="{sx - 14:.1f}" y="{sy - 24:.1f}" width="28" height="6" rx="3" fill="{VOLUME[0]}" />')
    # Le lampadaire, côté rue : un mât épais, une crosse, une boule de lumière
    lx, ly, zl = W + 1.15, 0.5, 12.0
    gx, gy = q(lx + 1.1, ly, zt)
    out.append(f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="50" ry="24" fill="url(#ext-lueur-sol)" />')
    fx, fy = q(lx, ly, zt)
    out.append(f'<ellipse cx="{fx - 3:.1f}" cy="{fy + 1:.1f}" rx="11" ry="4.5" fill="{OMBRE}" opacity="0.28" />')
    out.append(trait((lx, ly, zt), (lx, ly, zl), SOMBRE[2], 6.5))
    out.append(trait((lx + 0.04, ly, zt + 0.3), (lx + 0.04, ly, zl - 0.2), SOMBRE[0], 2.0, 0.8))
    a, b, c = q(lx, ly, zl), q(lx, ly, zl + 1.0), q(lx + 1.15, ly, zl + 1.0)
    out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f}" fill="none" stroke="{SOMBRE[2]}" stroke-width="6" stroke-linecap="round" />')
    hx, hy = q(lx + 1.15, ly, zl + 0.35)
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="42" fill="url(#ext-lueur)" />'
               f'<rect x="{hx - 6:.1f}" y="{hy - 19:.1f}" width="12" height="8" rx="4" fill="{SOMBRE[2]}" />'
               f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="12" fill="#FFE7BE" />'
               f'<circle cx="{hx + 3:.1f}" cy="{hy - 3.5:.1f}" r="5.5" fill="#FFF8EA" />')
    out.append(f'<ellipse cx="{fx:.1f}" cy="{fy - 3:.1f}" rx="10" ry="5.5" fill="{SOMBRE[2]}" />'
               f'<ellipse cx="{fx + 2:.1f}" cy="{fy - 5:.1f}" rx="5" ry="2.5" fill="{SOMBRE[0]}" />')
    return "".join(out)


# ---------- Le toit ----------


def toit():
    """Le toit : une dalle dodue qui déborde, un rebord tout autour et le creux de la terrasse ; une
    cheminée ronde ; une antenne franche, aux traits épais, terminée par des boules, sans câble."""
    zd, zt, zr = H2, H2 + 0.5, H2 + 1.0
    out = [boite(-0.7, W + 0.3, -0.7, D + 0.3, zd, zt, VOLUME, r=6, bombe=0.012)]
    out.append(boite(-0.7, W + 0.3, -0.7, -0.1, zt, zr, VOLUME, r=5))
    out.append(boite(-0.7, -0.1, -0.7, D + 0.3, zt, zr, VOLUME, r=5))
    out.append(forme([(-0.1, -0.1, zt), (W - 0.3, -0.1, zt), (W - 0.3, D - 0.3, zt), (-0.1, D - 0.3, zt)], "#EEBDAF", r=30))
    out.append(forme([(-0.1, -0.1, zt), (W - 0.3, -0.1, zt), (W - 0.3, 0.6, zt), (0.6, 0.6, zt), (0.6, D - 0.3, zt), (-0.1, D - 0.3, zt)],
                     OMBRE, r=14, extra=' opacity="0.16"'))
    # La cheminée, au fond à droite
    out.append(boite(8.4, 10.2, 1.2, 2.8, zt, zt + 1.8, VOLUME, r=5, bombe=0.02))
    out.append(boite(8.15, 10.45, 0.95, 3.05, zt + 1.8, zt + 2.15, SOMBRE, r=4))
    # L'antenne : un socle rond, un mât épais, deux barres arrondies, des boules au bout
    ax, ay = 3.4, 3.4
    sx, sy = q(ax, ay, zt)
    out.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="10" ry="5" fill="{SOMBRE[1]}" />')
    out.append(trait((ax, ay, zt), (ax, ay, zt + 3.0), SOMBRE[2], 5.0))
    for (z, l) in ((zt + 2.7, 1.1), (zt + 1.9, 0.8)):
        out.append(trait((ax - l, ay + l, z), (ax + l, ay - l, z), SOMBRE[2], 4.6))
        for s in (-1, 1):
            bx, by = q(ax + s * l, ay - s * l, z)
            out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="4.6" fill="{SOMBRE[2]}" />')
    bx, by = q(ax, ay, zt + 3.0)
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="6" fill="{SOMBRE[2]}" /><circle cx="{bx + 1.5:.1f}" cy="{by - 1.8:.1f}" r="2.2" fill="{SOMBRE[0]}" />')
    # Le rebord de devant, qui prend la lumière sur le dessus
    out.append(boite(-0.7, W + 0.3, D - 0.3, D + 0.3, zt, zr, VOLUME, r=5))
    out.append(boite(W - 0.3, W + 0.3, -0.7, D + 0.3, zt, zr, VOLUME, r=5))
    out.append(trait((-0.55, D + 0.3, zr), (W + 0.15, D + 0.3, zr), "#FFF0EA", 3.0, 0.9))
    out.append(trait((W + 0.3, -0.55, zr), (W + 0.3, D + 0.15, zr), "#FFF6F2", 3.0, 0.9))
    return "".join(out)


definitions()
calques = [("ext-sol", sol()),
           ("ext-murs", murs() + rez_de_chaussee() + plancher() + etage()),
           ("ext-battant", battants()),
           ("ext-marche", devant()),
           ("ext-toit", toit())]
corps = "".join(f'<g class="{c}">{s}</g>' for c, s in calques)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}"><g class="ext" data-viewbox="{VIEWBOX}">'
       f'<defs>{"".join(DEFS)}</defs>{corps}</g></svg>')

if __name__ == "__main__":
    page = open(sys.argv[1], encoding="utf-8").read()
    debut, fin = "<!-- IMMEUBLE -->", "<!-- /IMMEUBLE -->"
    i, j = page.index(debut) + len(debut), page.index(fin)
    page = page[:i] + '\n  <template id="immeuble">' + svg + "</template>\n  " + page[j:]
    open(sys.argv[1], "w", encoding="utf-8").write(page)
    print("immeuble inséré,", len(svg), "caractères")
