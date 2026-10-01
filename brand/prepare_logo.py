"""Prepares the original RENOVA MM logo (logo/logo.jpeg) for web use — design unchanged.

Run:  python3 brand/prepare_logo.py   (needs: pip install Pillow)
Writes to brand/logo/:
  renova-mm-logo.png            original, transparent background (for light backgrounds)
  renova-mm-logo-dark.png       same, anthracite parts in ivory (for dark backgrounds)
  renova-mm-icon.png / -dark    monogram only (RMM + house + buildings)
  favicon.png, apple-touch-icon.png
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "logo" / "logo.jpeg"
OUT = ROOT / "logo"
OUT.mkdir(exist_ok=True)

IVORY = (246, 241, 231)
NIGHT = (20, 22, 24)


def unmatte(img):
    """Remove the white background, keeping soft anti-aliased edges."""
    src = img.convert("RGB")
    out = Image.new("RGBA", src.size)
    sp, op = src.load(), out.load()
    w, h = src.size
    for y in range(h):
        for x in range(w):
            r, g, b = sp[x, y]
            ink = 255 - min(r, g, b)
            if ink < 14:                      # paper / JPEG noise
                op[x, y] = (0, 0, 0, 0)
                continue
            a = min(1.0, ink / 170)
            # recover the un-blended colour: c = a*f + (1-a)*255
            f = [max(0, min(255, round((c - (1 - a) * 255) / a))) for c in (r, g, b)]
            op[x, y] = (*f, round(a * 255))
    return out


def for_dark_background(rgba):
    """Swap the neutral anthracite ink to ivory; gold stays untouched."""
    out = rgba.copy()
    p = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = p[x, y]
            if a and max(r, g, b) - min(r, g, b) < 40 and max(r, g, b) < 140:
                p[x, y] = (*IVORY, a)
    return out


def trim(rgba, pad):
    box = rgba.getbbox()
    cropped = rgba.crop(box)
    canvas = Image.new("RGBA", (cropped.width + pad * 2, cropped.height + pad * 2))
    canvas.paste(cropped, (pad, pad))
    return canvas


def monogram_box(rgba):
    """Bounding box of the artwork above the first gold rule."""
    a = rgba.getchannel("A")
    w, h = rgba.size
    # the first gold rule is a row that is inked across most of the width
    for y in range(h // 3, h):
        inked = sum(1 for x in range(0, w, 4) if a.getpixel((x, y)) > 128)
        if inked > (w // 4) * 0.6:
            rule_y = y
            break
    return rgba.crop((0, 0, w, rule_y - 12)).getbbox()


def square(rgba, size, bg=None, radius=0, inset=0.14):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if bg:
        from PIL import ImageDraw
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
        canvas.paste(Image.new("RGBA", (size, size), (*bg, 255)), (0, 0), m)
    inner = int(size * (1 - inset * 2))
    art = rgba.copy()
    art.thumbnail((inner, inner), Image.LANCZOS)
    canvas.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    return canvas


src = Image.open(SRC)
logo = unmatte(src)
logo_dark = for_dark_background(logo)

trim(logo, 24).save(OUT / "renova-mm-logo.png", optimize=True)
trim(logo_dark, 24).save(OUT / "renova-mm-logo-dark.png", optimize=True)

box = monogram_box(logo)
icon = logo.crop(box)
icon_dark = logo_dark.crop(box)
trim(icon, 8).save(OUT / "renova-mm-icon.png", optimize=True)
trim(icon_dark, 8).save(OUT / "renova-mm-icon-dark.png", optimize=True)

square(icon_dark, 512, bg=NIGHT, radius=112).save(OUT / "favicon.png", optimize=True)
square(icon_dark, 180, bg=NIGHT, radius=0).save(OUT / "apple-touch-icon.png", optimize=True)

for f in sorted(OUT.glob("*.png")):
    im = Image.open(f)
    print(f"{f.name:28s} {im.width}x{im.height}  {f.stat().st_size // 1024} KB")
