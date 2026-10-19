"""Dessine la pièce de Tiny Studio en vue isométrique, en SVG, et l'insère dans la page.

Repère : x va vers la droite le long du mur de droite, y vers la gauche le long du mur de gauche,
z vers le haut. Le mur de gauche est le plan x = 0, le mur de droite le plan y = 0.

Ce fichier pose le socle, le sol et l'épaisseur des murs, les badges et les boutons des meubles ;
la pièce elle-même (murs, mobilier, déco) est dessinée dans piece_par_defaut.py.

Usage : python3 atelier/genere_piece.py index.html
"""
import math
import sys

import piece_par_defaut

S = 30             # pixels par unité
OX, OY = 390, 318  # position à l'écran de l'angle du fond, au sol
C30, S30 = math.cos(math.radians(30)), 0.5
W, D, H = 12, 12, 9  # largeur, profondeur et hauteur de la pièce


def p(x, y, z):
    return (OX + (x - y) * C30 * S, OY + (x + y) * S30 * S - z * S)


def pts(points):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in points)


def poly(points3d, classe="", style="", extra=""):
    c = f' class="{classe}"' if classe else ""
    st = f' style="{style}"' if style else ""
    return f'<polygon points="{pts([p(*q) for q in points3d])}"{c}{st}{extra} />'


def ligne(a, b, classe, extra=""):
    (x1, y1), (x2, y2) = p(*a), p(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{classe}"{extra} />'


# ---------- Les volumes ----------


def chemin_arrondi(points, r):
    """Le tracé d'un polygone à l'écran, chaque coin remplacé par une courbe de rayon r pixels.
    Le rayon se réduit tout seul sur les côtés courts, pour qu'une planche fine reste une planche."""
    def vers(u, v, dist):
        longueur = math.hypot(v[0] - u[0], v[1] - u[1]) or 1
        t = min(dist, longueur / 2.2) / longueur
        return (u[0] + (v[0] - u[0]) * t, u[1] + (v[1] - u[1]) * t)
    n, d = len(points), []
    for i in range(n):
        a, b, c = points[i - 1], points[i], points[(i + 1) % n]
        p1, p2 = vers(b, a, r), vers(b, c, r)
        d.append(f"{'M' if i == 0 else 'L'}{p1[0]:.1f} {p1[1]:.1f} Q{b[0]:.1f} {b[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d) + " Z"


def poly_arrondi(points3d, classe="", style="", r=5):
    c = f' class="{classe}"' if classe else ""
    st = f' style="{style}"' if style else ""
    return f'<path d="{chemin_arrondi([p(*q) for q in points3d], r)}"{c}{st} />'


def boite(x, y, z, dx, dy, dz, reflet=True, bois=None, rond=5):
    """Un volume aux coins arrondis : d'abord sa silhouette, dans la teinte de l'ombre, qui
    comble le petit creux là où les trois faces se rejoignent ; puis la face tournée vers +y
    (éclairée), la face tournée vers +x (à l'ombre) et le dessus, chacune aux coins ronds,
    avec un léger dégradé, et un reflet sur les arêtes du dessus. rond, en pixels : 5 pour un
    meuble, davantage pour ce qui est moelleux (coussin, matelas, oreiller).
    Avec bois=« h » ou « v », les faces reçoivent le veinage du bois."""
    x1, y1, z1 = x + dx, y + dy, z + dz
    face_y = [(x, y1, z), (x1, y1, z), (x1, y1, z1), (x, y1, z1)]
    face_x = [(x1, y, z), (x1, y1, z), (x1, y1, z1), (x1, y, z1)]
    dessus = [(x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1)]
    silhouette = [(x, y1, z), (x1, y1, z), (x1, y, z), (x1, y, z1), (x, y, z1), (x, y1, z1)]
    r = rond * 0.7
    o = [
        poly_arrondi(silhouette, "v ombre", r=rond),
        poly_arrondi(face_y, "v clair", r=r), poly_arrondi(face_y, "voile-lumiere", r=r),
        poly_arrondi(face_x, "v ombre", r=r), poly_arrondi(face_x, "voile-ombre", r=r),
        poly_arrondi(dessus, "v haut", r=r),
    ]
    if bois:
        o += [poly_arrondi(face, "grain", f"fill: url(#{motif})", r=r) for face, motif in
              ((face_y, f"grain-y-{bois}"), (face_x, f"grain-x-{bois}"), (dessus, "grain-z"))]
    if reflet and dz > 0.05:
        o.append(ligne((x + dx * 0.06, y1, z1), (x1 - dx * 0.06, y1, z1), "arete"))
        o.append(ligne((x1, y + dy * 0.06, z1), (x1, y1 - dy * 0.06, z1), "arete arete-ombre"))
    return "".join(o)


def face_x(xc, points_yz, classe, style=""):
    return poly([(xc, y, z) for y, z in points_yz], classe, style)


def face_y(yc, points_xz, classe, style=""):
    return poly([(x, yc, z) for x, z in points_xz], classe, style)


def teinte(var):
    return f"--c: var(--{var})"


def badge(cle, x, y, z):
    sx, sy = p(x, y, z)
    return (f'<g class="badge"><path d="M{sx - 6:.1f} {sy + 10:.1f} L{sx:.1f} {sy + 17:.1f} L{sx + 6:.1f} {sy + 10:.1f} Z" class="badge-pointe" />'
            f'<rect x="{sx - 17:.1f}" y="{sy - 13:.1f}" width="34" height="25" rx="12.5" class="badge-fond" />'
            f'<text x="{sx:.1f}" y="{sy + 5:.1f}" data-compte="{cle}"></text>'
            # La pièce dorée « % », visible quand le meuble contient une envie en promotion (19 octobre 2026)
            f'<g class="badge-promo"><circle cx="{sx + 16:.1f}" cy="{sy - 12:.1f}" r="8.5" class="piece-fond" />'
            f'<text x="{sx + 16:.1f}" y="{sy - 8.6:.1f}">%</text></g></g>')


def meuble(cle, contenu):
    return f'<g class="meuble" data-meuble="{cle}" tabindex="0" role="button">{contenu}</g>'


# ---------- La pièce par défaut ----------
# Une seule pièce, sans style au sens d'un thème : la version de départ, dessinée dans piece_par_defaut.py.


def piece():
    """Le socle, le sol et les murs de fond, l'épaisseur des murs, puis la pièce dessinée dans
    piece_par_defaut.py, qui recouvre le sol et les murs."""
    o = [f'<g style="{teinte("socle")}">' + boite(-0.5, -0.5, -0.7, W + 0.5, D + 0.5, 0.7, reflet=False) + "</g>"]
    o.append(poly([(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0)], "sol"))
    o.append(poly([(0, 0, 0), (0, D, 0), (0, D, H), (0, 0, H)], "mur-g"))
    o.append(poly([(0, 0, 0), (W, 0, 0), (W, 0, H), (0, 0, H)], "mur-d"))
    o.append(piece_par_defaut.parquet())
    o.append(poly([(-0.5, -0.5, H), (W, -0.5, H), (W, 0, H), (0, 0, H), (0, D, H), (-0.5, D, H)], "tranche-haut"))
    o.append(poly([(-0.5, D, 0), (0, D, 0), (0, D, H), (-0.5, D, H)], "tranche-g"))
    o.append(poly([(W, -0.5, 0), (W, 0, 0), (W, 0, H), (W, -0.5, H)], "tranche-d"))
    o.append(piece_par_defaut.dessine(meuble, badge))
    return "".join(o)


def dessine_svg():
    """La pièce entière, avec ses définitions."""
    return f'''<svg class="studio" viewBox="0 0 780 690" role="group" aria-label="Le studio en vue isométrique, avec ses cinq meubles">
        <defs>
          <linearGradient id="g-lumiere" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.22" /><stop offset="1" stop-color="#FFFFFF" stop-opacity="0" /></linearGradient>
          <linearGradient id="g-ombre" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B2414" stop-opacity="0" /><stop offset="1" stop-color="#3B2414" stop-opacity="0.18" /></linearGradient>
          <linearGradient id="g-ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="ciel-haut" /><stop offset="1" class="ciel-bas" /></linearGradient>
          <radialGradient id="g-papier" cx="0.5" cy="0.45" r="0.7"><stop offset="0" stop-color="#FFF1D2" stop-opacity="0.75" /><stop offset="1" stop-color="#FFFFFF" stop-opacity="0" /></radialGradient>
        </defs>
        {piece()}
      </svg>'''


SVG = dessine_svg()

if __name__ == "__main__":
    page = open(sys.argv[1], encoding="utf-8").read()
    debut, fin = "<!-- PIECE -->", "<!-- /PIECE -->"
    i, j = page.index(debut) + len(debut), page.index(fin)
    page = page[:i] + "\n      " + SVG + "\n      " + page[j:]
    open(sys.argv[1], "w", encoding="utf-8").write(page)
    print("pièce insérée,", len(SVG), "caractères")
