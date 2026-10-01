"""Builds the RENOVA MM logo set as clean, outlined SVG files.

Run:  python3 brand/build_logo.py   (needs: pip install fonttools)
Output goes to brand/logo/.
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
FONT_FILE = ROOT / "fonts" / "Montserrat.ttf"

# ---- Brand colours (sampled from the original logo, then cleaned up) ----
GOLD_LIGHT = "#E8C067"
GOLD = "#C99A3A"
GOLD_DEEP = "#9E7024"
CHARCOAL = "#2B2E31"
IVORY = "#F6F1E7"

NAME, NAME_ACCENT = "RENOVA", "MM"
TAGLINE = "CONSTRUCTION  •  RÉNOVATION  •  AMÉNAGEMENT"

# ---------------------------------------------------------------- text -> path
_fonts = {}


def font(weight):
    if weight not in _fonts:
        _fonts[weight] = instancer.instantiateVariableFont(TTFont(FONT_FILE), {"wght": weight})
    return _fonts[weight]


def text_path(text, weight, size, tracking, x, baseline):
    """Return (svg path d, advance width) for text set at (x, baseline)."""
    f = font(weight)
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    s = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx = x
    for i, ch in enumerate(text):
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, baseline)))
        cx += hmtx[g][0] * s
        if i < len(text) - 1:
            cx += tracking * size
    return pen.getCommands(), cx - x


def text_width(text, weight, size, tracking):
    return text_path(text, weight, size, tracking, 0, 0)[1]


def cap_height(weight, size):
    f = font(weight)
    return f["OS/2"].sCapHeight / f["head"].unitsPerEm * size


# ---------------------------------------------------------------- monogram
# Drawn on a 600-unit grid. Baseline y=480. Everything uses one roof pitch.
PITCH = 108 / 132          # roof slope (rise / run) ≈ 39°
APEX_X = 428


def M_polygon(x0, top=345, bottom=480, w=140, stem=32, v1=60, k=56):
    cx = x0 + w / 2
    pts = [(x0, bottom), (x0, top), (x0 + stem, top), (cx, top + v1),
           (x0 + w - stem, top), (x0 + w, top), (x0 + w, bottom),
           (x0 + w - stem, bottom), (x0 + w - stem, top + k), (cx, top + v1 + k),
           (x0 + stem, top + k), (x0 + stem, bottom)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def building(xl, xr, top_left, rising):
    """Parallelogram whose top and bottom follow the roof pitch."""
    sign = -1 if rising else 1
    top_r = top_left + sign * PITCH * (xr - xl)

    def base(x):  # 12 units above the roof's outer edge
        return 181.9 + PITCH * abs(x - APEX_X)

    pts = [(xl, top_left), (xr, top_r), (xr, base(xr)), (xl, base(xl))]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def monogram(gold="url(#rmmGold)", dark=CHARCOAL, uid="rmm"):
    gold = gold.replace("rmmGold", f"{uid}Gold")
    bars = [(296, 330, 132), (342, 376, 86), (388, 422, 40)]
    blocks = [(434, 468, 12.2), (480, 514, 58.2), (526, 560, 104.2)]
    win = "".join(
        f'<rect x="{x}" y="{y}" width="16" height="16" fill="{gold}"/>'
        for x in (409.5, 430.5) for y in (278, 299)
    )
    return f"""
  <defs>
    <linearGradient id="{uid}Gold" gradientUnits="userSpaceOnUse" x1="40" y1="12" x2="560" y2="480">
      <stop offset="0" stop-color="{GOLD_LIGHT}"/>
      <stop offset=".55" stop-color="{GOLD}"/>
      <stop offset="1" stop-color="{GOLD_DEEP}"/>
    </linearGradient>
    <clipPath id="{uid}Base"><rect x="0" y="-50" width="700" height="530"/></clipPath>
  </defs>
  <g clip-path="url(#{uid}Base)">
    <!-- skyline -->
    {''.join(f'<path d="{building(a, b, t, True)}" fill="{gold}"/>' for a, b, t in bars)}
    {''.join(f'<path d="{building(a, b, t, False)}" fill="{dark}"/>' for a, b, t in blocks)}
    <!-- R -->
    <path d="M66 480V226H150A59 59 0 0 1 150 344H66" fill="none" stroke="{gold}" stroke-width="52" stroke-linejoin="miter"/>
    <path d="M138 344L232 500" fill="none" stroke="{gold}" stroke-width="52"/>
    <!-- roof -->
    <path d="M296 320L428 212L560 320" fill="none" stroke="{dark}" stroke-width="28" stroke-linejoin="miter" stroke-miterlimit="8"/>
    <path d="M324.7 332L428 247.5L531.3 332" fill="none" stroke="{gold}" stroke-width="7" stroke-linejoin="miter" stroke-miterlimit="8"/>
    {win}
    <!-- MM -->
    <path d="{M_polygon(280)}" fill="{dark}"/>
    <path d="{M_polygon(436)}" fill="{dark}"/>
  </g>"""


ICON_BOX = (40, 12, 576, 480)  # x0, y0, x1, y1 of the monogram artwork


def svg(view_w, view_h, body, title="RENOVA MM"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w:.0f} {view_h:.0f}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}\n</svg>\n')


def place_icon(x, y, scale, gold, dark, uid):
    x0, y0, _, _ = ICON_BOX
    return (f'<g transform="translate({x - x0 * scale:.2f} {y - y0 * scale:.2f}) scale({scale})">'
            f'{monogram(gold, dark, uid)}</g>')


# ---------------------------------------------------------------- layouts
def stacked(dark_bg=False):
    ink = IVORY if dark_bg else CHARCOAL
    uid = "rmmD" if dark_bg else "rmmL"
    gold = f"url(#{uid}Gold)"
    W = 900
    iw = ICON_BOX[2] - ICON_BOX[0]
    body = place_icon((W - iw) / 2, 40, 1, gold, ink, uid)

    rule_x0, rule_x1 = 110, W - 110
    rule_w = rule_x1 - rule_x0
    y = 552
    body += f'<rect x="{rule_x0}" y="{y}" width="{rule_w}" height="3" fill="{GOLD}"/>'

    # wordmark sized to sit inside the rules
    wt, tr = 600, 0.16
    full = NAME + " " + NAME_ACCENT
    size = 96
    size = min(size, size * (rule_w - 40) / text_width(full, wt, size, tr))
    base = y + 30 + cap_height(wt, size)
    total = text_width(full, wt, size, tr)
    x = (W - total) / 2
    d1, w1 = text_path(NAME + " ", wt, size, tr, x, base)
    d2, _ = text_path(NAME_ACCENT, wt, size, tr, x + w1 + tr * size, base)
    body += f'<path d="{d1}" fill="{ink}"/><path d="{d2}" fill="{GOLD}"/>'

    y2 = base + 30
    body += f'<rect x="{rule_x0}" y="{y2:.1f}" width="{rule_w}" height="3" fill="{GOLD}"/>'

    tw, ttr = 500, 0.12
    tsize = 26
    tsize = min(tsize, tsize * rule_w / text_width(TAGLINE, tw, tsize, ttr))
    tbase = y2 + 3 + 26 + cap_height(tw, tsize)
    tt = text_width(TAGLINE, tw, tsize, ttr)
    d3, _ = text_path(TAGLINE, tw, tsize, ttr, (W - tt) / 2, tbase)
    body += f'<path d="{d3}" fill="{ink}"/>'
    return svg(W, tbase + 40, body)


def horizontal(dark_bg=False):
    ink = IVORY if dark_bg else CHARCOAL
    uid = "rmmHD" if dark_bg else "rmmHL"
    gold = f"url(#{uid}Gold)"
    icon_h = 240
    scale = icon_h / (ICON_BOX[3] - ICON_BOX[1])
    pad = 20
    body = place_icon(pad, pad, scale, gold, ink, uid)
    tx = pad + (ICON_BOX[2] - ICON_BOX[0]) * scale + 44

    wt, tr, size = 600, 0.14, 92
    base = pad + icon_h * 0.56
    d1, w1 = text_path(NAME + " ", wt, size, tr, tx, base)
    d2, w2 = text_path(NAME_ACCENT, wt, size, tr, tx + w1 + tr * size, base)
    word_w = w1 + tr * size + w2
    body += f'<path d="{d1}" fill="{ink}"/><path d="{d2}" fill="{GOLD}"/>'

    ry = base + 26
    body += f'<rect x="{tx}" y="{ry:.1f}" width="{word_w:.1f}" height="3" fill="{GOLD}"/>'
    tw, ttr = 500, 0.1
    tsize = 22
    tsize = min(tsize, tsize * word_w / text_width(TAGLINE, tw, tsize, ttr))
    tbase = ry + 3 + 18 + cap_height(tw, tsize)
    d3, _ = text_path(TAGLINE, tw, tsize, ttr, tx, tbase)
    body += f'<path d="{d3}" fill="{ink}"/>'
    return svg(tx + word_w + pad, icon_h + pad * 2, body)


def icon_only(dark_bg=False):
    ink = IVORY if dark_bg else CHARCOAL
    uid = "rmmID" if dark_bg else "rmmIL"
    x0, y0, x1, y1 = ICON_BOX
    pad = 24
    body = place_icon(pad, pad, 1, f"url(#{uid}Gold)", ink, uid)
    return svg(x1 - x0 + pad * 2, y1 - y0 + pad * 2, body)


def favicon():
    size = 512
    x0, y0, x1, y1 = ICON_BOX
    scale = 400 / (x1 - x0)
    ih = (y1 - y0) * scale
    body = f'<rect width="{size}" height="{size}" rx="112" fill="{CHARCOAL}"/>'
    body += place_icon((size - 400) / 2, (size - ih) / 2 + 6, scale, "url(#rmmFGold)", IVORY, "rmmF")
    return svg(size, size, body)


files = {
    "renova-mm-logo.svg": stacked(False),
    "renova-mm-logo-dark.svg": stacked(True),
    "renova-mm-logo-horizontal.svg": horizontal(False),
    "renova-mm-logo-horizontal-dark.svg": horizontal(True),
    "renova-mm-icon.svg": icon_only(False),
    "renova-mm-icon-dark.svg": icon_only(True),
    "favicon.svg": favicon(),
}
for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {name}  ({len(content) // 1024} KB)")
