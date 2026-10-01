"""Faithful vector redraw of the original RENOVA MM logo (logo/logo.jpeg).

The design is NOT changed:
  * the RMM monogram (R, house, roof, buildings) is traced from the original artwork,
  * the lettering is rebuilt with Montserrat SemiBold/Medium (measured to match the original),
  * rules and bullets are placed at their measured positions.

Run:  python3 brand/vectorize_logo.py      (needs: pip install Pillow numpy potracer fonttools)
Output: brand/logo/*.svg
"""
from pathlib import Path

import numpy as np
import potrace
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "logo" / "logo.jpeg"
OUT = ROOT / "logo"
FONT = ROOT / "fonts" / "Montserrat.ttf"
OUT.mkdir(exist_ok=True)

# colours sampled from the original
CHARCOAL = "#272A2D"
GOLD_TOP, GOLD_BOTTOM = "#D9AB4A", "#A67824"
GOLD_RULE = "#A27630"
IVORY = "#F6F1E7"
NIGHT = "#141618"

SCALE = 3            # trace at 3x for smooth curves
MONO_BOTTOM = 770    # monogram lives above the first rule (y=786)

# ------------------------------------------------------------------ tracing
img = Image.open(SRC).convert("RGB")
W, H = img.size
big = img.crop((0, 0, W, MONO_BOTTOM)).resize((W * SCALE, MONO_BOTTOM * SCALE), Image.LANCZOS)
a = np.asarray(big).astype(int)
ink = 255 - a.min(axis=2)
sat = a.max(axis=2) - a.min(axis=2)
gold_mask = (ink > 100) & (sat > 40)
dark_mask = (ink > 100) & (sat <= 40)


def xy(pt):
    return (pt.x, pt.y) if hasattr(pt, "x") else tuple(pt)


def trace(mask):
    bm = potrace.Bitmap(~mask)  # potracer inverts boolean input
    path = bm.trace(turdsize=40 * SCALE * SCALE, alphamax=0.75, opticurve=True, opttolerance=0.15)
    s = 1 / SCALE
    parts = []
    for curve in path:
        sx, sy = xy(curve.start_point)
        d = [f"M{sx * s:.2f} {sy * s:.2f}"]
        for seg in curve:
            ex, ey = xy(seg.end_point)
            if seg.is_corner:
                cx, cy = xy(seg.c)
                d.append(f"L{cx * s:.2f} {cy * s:.2f}L{ex * s:.2f} {ey * s:.2f}")
            else:
                (c1x, c1y), (c2x, c2y) = xy(seg.c1), xy(seg.c2)
                d.append(f"C{c1x * s:.2f} {c1y * s:.2f} {c2x * s:.2f} {c2y * s:.2f} {ex * s:.2f} {ey * s:.2f}")
        d.append("Z")
        xs = [sx * s] + [xy(seg.end_point)[0] * s for seg in curve]
        ys = [sy * s] + [xy(seg.end_point)[1] * s for seg in curve]
        parts.append(((min(xs), min(ys), max(xs), max(ys)), "".join(d)))
    return parts


def group_gold(parts):
    """Split gold shapes so each element gets its own light-to-dark sheen, like the original."""
    groups = {"r": [], "bars": [], "house": []}
    for (x0, y0, x1, y1), d in parts:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if cx < 480 and cy > 430:
            groups["r"].append(d)
        elif y1 < 520:
            groups["bars"].append(d)
        else:
            groups["house"].append(d)
    return {k: "".join(v) for k, v in groups.items()}


GOLD = group_gold(trace(gold_mask))
DARK_D = "".join(d for _, d in trace(dark_mask))

# ------------------------------------------------------------------ lettering
_fonts = {}


def font(w):
    if w not in _fonts:
        _fonts[w] = instancer.instantiateVariableFont(TTFont(FONT), {"wght": w})
    return _fonts[w]


def glyph(ch, w):
    f = font(w)
    name = f.getBestCmap()[ord(ch)]
    gs = f.getGlyphSet()
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    return f, gs, name, bp.bounds


def letters_at(chars, boxes, weight, cap_top, baseline):
    """Place each letter so its outline fills the measured box (left/right) on the baseline."""
    pen_d = []
    for ch, (x0, x1) in zip(chars, boxes):
        f, gs, name, (gx0, gy0, gx1, gy1) = glyph(ch, weight)
        cap = f["OS/2"].sCapHeight
        sy = (baseline - cap_top) / cap
        sx = (x1 - x0 + 1) / (gx1 - gx0)
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (sx, 0, 0, -sy, x0 - gx0 * sx, baseline)))
        pen_d.append(pen.getCommands())
    return "".join(pen_d)


def line_of_text(text, weight, cap_top, baseline, x_left, x_right):
    """Set a line of text with even tracking so it spans exactly x_left..x_right."""
    f = font(weight)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    s = (baseline - cap_top) / f["OS/2"].sCapHeight
    names = [cmap[ord(c)] for c in text]

    def ink_bounds(name):
        bp = BoundsPen(gs)
        gs[name].draw(bp)
        return bp.bounds

    first_l = ink_bounds(names[0])[0] * s
    last = ink_bounds(names[-1])
    natural = sum(hmtx[n][0] for n in names[:-1]) * s + last[2] * s - first_l
    track = ((x_right - x_left) - natural) / (len(names) - 1)
    pen = SVGPathPen(gs)
    x = x_left - first_l
    for n in names:
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, x, baseline)))
        x += hmtx[n][0] * s + track
    return pen.getCommands()


# Measured from the original (pixels in the 1254x1254 artwork)
WORD_D = letters_at("RENOVA", [(138, 230), (265, 346), (384, 481), (515, 630), (645, 757), (766, 878)],
                    600, cap_top=821, baseline=928)
# the O overshoots (818–929); refit it so its overshoot matches
MM_D = letters_at("MM", [(934, 1014), (1037, 1116)], 600, cap_top=839, baseline=920)
BULLETS = [(487.5, 1000.5), (782, 1000.5)]
RULES = [(137, 786, 1116, 791), (137, 956, 1116, 961)]


def measure_tagline():
    """Find the left/right ink edge of each tagline word in the original."""
    arr = np.asarray(img).astype(int)
    band = arr[986:1013]
    inked = ((255 - band.min(axis=2)) > 100) & ((band.max(axis=2) - band.min(axis=2)) < 40)
    cols = np.where(inked.any(axis=0))[0]
    words, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > 20:
            words.append((int(start), int(prev)))
            start = c
        prev = c
    words.append((int(start), int(prev)))
    return words


words = measure_tagline()
TAG_D = "".join(
    line_of_text(t, 500, cap_top=989, baseline=1012, x_left=x0, x_right=x1)
    for t, (x0, x1) in zip(["CONSTRUCTION", "RÉNOVATION", "AMÉNAGEMENT"], words)
)

# ------------------------------------------------------------------ assemble
SHEEN = {  # top -> bottom colours per element, sampled from the original
    "r": ("#E0B253", "#A47622"),
    "bars": ("#D7A947", "#B4852B"),
    "house": ("#E2B65A", "#C99A3E"),
    "text": (GOLD_TOP, GOLD_BOTTOM),
}


def gradient(uid, kind="text"):
    top, bottom = SHEEN[kind]
    return (f'<linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>'
            f'</linearGradient>')


def gold_defs(uid):
    return "".join(gradient(f"{uid}-{k}", k) for k in ("r", "bars", "house"))


def svg(viewbox, body, defs):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img" aria-label="RENOVA MM">'
            f'<title>RENOVA MM</title><defs>{defs}</defs>{body}</svg>\n')


def monogram(ink, uid):
    gold = "".join(f'<path d="{GOLD[k]}" fill="url(#{uid}-{k})" fill-rule="evenodd"/>'
                   for k in ("r", "bars", "house"))
    return gold + f'<path d="{DARK_D}" fill="{ink}" fill-rule="evenodd"/>'


def full_logo(dark=False):
    ink = IVORY if dark else CHARCOAL
    uid = "rmmGoldD" if dark else "rmmGold"
    body = monogram(ink, uid)
    body += "".join(f'<rect x="{x0}" y="{y0}" width="{x1 - x0 + 1}" height="{y1 - y0}" fill="{GOLD_RULE}"/>'
                    for x0, y0, x1, y1 in RULES)
    body += f'<path d="{WORD_D}" fill="{ink}"/>'
    body += f'<path d="{MM_D}" fill="url(#{uid}T)"/>'
    body += f'<path d="{TAG_D}" fill="{ink}"/>'
    body += "".join(f'<circle cx="{x}" cy="{y}" r="4.3" fill="{GOLD_RULE}"/>' for x, y in BULLETS)
    defs = gold_defs(uid) + gradient(uid + "T")
    return svg("110 140 1034 900", body, defs)


def icon(dark=False):
    ink = IVORY if dark else CHARCOAL
    uid = "rmmIconD" if dark else "rmmIcon"
    return svg("215 150 815 610", monogram(ink, uid), gold_defs(uid))


def favicon():
    uid = "rmmFav"
    body = f'<rect x="150" y="40" width="944" height="944" rx="206" fill="{NIGHT}"/>'
    body += f'<g transform="translate(622 512) scale(1.12) translate(-622 -455)">{monogram(IVORY, uid)}</g>'
    return svg("150 40 944 944", body, gold_defs(uid))


files = {
    "renova-mm-logo.svg": full_logo(False),
    "renova-mm-logo-dark.svg": full_logo(True),
    "renova-mm-icon.svg": icon(False),
    "renova-mm-icon-dark.svg": icon(True),
    "favicon.svg": favicon(),
}
for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {name}  ({len(content) // 1024} KB)")
print("tagline words measured:", words)
