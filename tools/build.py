#!/usr/bin/env python3
"""Builds the static, SEO-ready pages of the RENOVA MM site.

    python3 tools/build.py        (needs: pip install beautifulsoup4, and node)

Sources (edit these, then re-run the build):
  src/index.html        page template (layout of all pages)
  js/i18n.js            all texts, French and English
  content/contact.json  phone, email, social links          (editable in the Pages CMS dashboard)
  content/gallery.json  gallery photos + captions           (editable in the dashboard)
  content/reviews.json  customer reviews                    (editable in the dashboard)
  content/sections.json photo of the "Nos engagements" section (editable in the dashboard)
  content/settings.json siteUrl, listed, analytics + form keys (technical, not in the dashboard)

Generates:
  index.html, en/index.html                         home pages
  services/<slug>.html, en/services/<slug>.html     one page per service
  sitemap.xml, robots.txt, js/config.js
"""
import copy
import datetime
import hashlib
import json
import os
import posixpath
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["fr", "en"]
OG_LOCALE = {"fr": "fr_FR", "en": "en_GB"}

ICONS = [  # one per service, same order as I18N[lang]["services"]
    '<path d="M2 12h20"/><path d="M20 12v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8"/><path d="m4 8 16-4"/><path d="m8.86 6.78-.45-1.81a2 2 0 0 1 1.45-2.43l1.94-.48a2 2 0 0 1 2.43 1.46l.45 1.8"/>',  # kitchens: cooking pot
    '<path d="M10 4 8 6"/><path d="M17 19v2M7 19v2M2 12h20"/><path d="M9 5 7.6 3.6A2.1 2.1 0 0 0 4 5v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/>',  # bathroom: bath
    '<rect x="3" y="3" width="18" height="18" rx="1.5"/><path d="M3 9h18M3 15h18M10 3v6M6 9v6M15 9v6M12 15v6"/>',  # flooring: planks
    '<rect x="2" y="2" width="16" height="6" rx="2"/><path d="M10 16v-2a2 2 0 0 1 2-2h8a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="8" y="16" width="4" height="6" rx="1"/>',  # painting: roller
    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/>',  # electrical & lighting: bulb
    '<path d="m15 12-8.4 8.4a2.1 2.1 0 1 1-3-3L12 9"/><path d="m18 15 4-4"/><path d="m21.5 11.5-1.9-1.9a2 2 0 0 1-.6-1.4V7l-2.3-2.3a6 6 0 0 0-4.2-1.7H9l.9.8A6.2 6.2 0 0 1 12 8.4V10l2 2h1.2a2 2 0 0 1 1.4.6l1.9 1.9"/>',  # assembly & fixing: hammer
    '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M9 3v18M15 3v18M3 10h18"/>',  # fit-out: glass partition
]
ARROW = '<svg class="arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg>'
PHONE = ('<svg viewBox="0 0 24 24" class="arrow"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 '
         '2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>')


# ------------------------------------------------------------------ sources
def load_js(rel, var):
    code = f"global.window={{}}; require({json.dumps(str(ROOT / rel))}); process.stdout.write(JSON.stringify(window.{var}))"
    return json.loads(subprocess.run(["node", "-e", code], check=True, capture_output=True, text=True).stdout)


def load_json(name):
    return json.loads((ROOT / "content" / f"{name}.json").read_text(encoding="utf-8"))


MAX_REVIEWS = 6
PHOTO_BOX = (900, 1200)


def optimise_photo(path):
    """Phone photos uploaded through the dashboard -> 900x1200 WebP in assets/photos/opt/ (original kept)."""
    path = path.lstrip("/")
    src = ROOT / path
    if not src.exists():
        print(f"  ! missing photo: {path}")
        return path
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return path  # Pillow not installed locally: use the file as it is
    with Image.open(src) as im:
        if src.suffix.lower() == ".webp" and im.width <= PHOTO_BOX[0] and im.height <= PHOTO_BOX[1]:
            return path
        out = ROOT / "assets" / "photos" / "opt" / (src.stem + ".webp")
        if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            out.parent.mkdir(parents=True, exist_ok=True)
            img = ImageOps.exif_transpose(im).convert("RGB")
            img.thumbnail(PHOTO_BOX, Image.LANCZOS)
            img.save(out, "WEBP", quality=78, method=6)
            print(f"  optimised {path} -> {out.relative_to(ROOT)}")
        return str(out.relative_to(ROOT)).replace(os.sep, "/")


FR_SPACE_BEFORE = re.compile(r" +([?!:;»])")


def fr_typo(v):
    """French puts a space before ? ! : ; » — make it non-breaking so the sign never starts a new line."""
    if isinstance(v, str):
        return FR_SPACE_BEFORE.sub("\u00a0\\1", v).replace("« ", "«\u00a0")
    if isinstance(v, list):
        return [fr_typo(x) for x in v]
    if isinstance(v, dict):
        return {k: fr_typo(x) for k, x in v.items()}
    return v


def load_config():
    """Merge content/*.json (edited in the dashboard) into the structure the pages use."""
    contact, settings = load_json("contact"), load_json("settings")
    reviews = []
    for r in load_json("reviews"):
        if not r.get("visible", True):
            continue
        reviews.append({
            "name": r.get("name", "").strip(), "city": r.get("city", ""), "rating": r.get("rating", 5),
            "date": str(r.get("date") or ""), "lang": r.get("lang") or "fr", "placeholder": bool(r.get("placeholder")),
            "service": {"fr": fr_typo(r.get("service_fr", "")), "en": r.get("service_en", "")},
            "text": {"fr": fr_typo(r.get("text_fr", "")), "en": r.get("text_en", "")},
        })
    reviews.sort(key=lambda r: r["date"], reverse=True)  # newest first
    sections = load_json("sections")
    if sections.get("promise_photo"):
        sections["promise_photo"] = optimise_photo(sections["promise_photo"])
    gallery = [{"src": optimise_photo(g["image"]), "fr": fr_typo(g.get("caption_fr", "")), "en": g.get("caption_en") or g.get("caption_fr", "")}
               for g in load_json("gallery") if g.get("image")]
    return {
        **settings,
        "phone": contact.get("phone", ""), "email": contact.get("email", ""),
        "social": {k: contact.get(k, "") for k in ("facebook", "tiktok", "instagram", "linkedin")} | {"whatsapp": bool(contact.get("whatsapp"))},
        "gallery": gallery,
        "reviews": reviews,
        "sections": sections,
    }


I18N = load_js("js/i18n.js", "I18N")
I18N["fr"] = fr_typo(I18N["fr"])
CFG = load_config()
SITE = CFG["siteUrl"].rstrip("/") + "/"
LISTED = bool(CFG.get("listed"))
TEMPLATE = (ROOT / "src" / "index.html").read_text(encoding="utf-8")


def T(lang, key):
    return I18N[lang].get(key, I18N["fr"].get(key, ""))


def services(lang):
    return I18N[lang]["services"]


# ------------------------------------------------------------------ paths & urls
def home_path(lang):
    return "index.html" if lang == "fr" else "en/index.html"


def service_path(lang, slug):
    return f"services/{slug}.html" if lang == "fr" else f"en/services/{slug}.html"


def legal_path(lang):
    return "mentions-legales.html" if lang == "fr" else "en/mentions-legales.html"


def public_url(path):
    """Absolute URL; index.html pages are addressed by their folder."""
    return SITE + (path[: -len("index.html")] if path.endswith("index.html") else path)


def rel_link(from_path, to_path):
    rel = posixpath.relpath(to_path, posixpath.dirname(from_path) or ".")
    if rel == "index.html" or rel.endswith("/index.html"):
        rel = rel[: -len("index.html")] or "./"
    return rel


def asset_version(rel):
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]


def page_link(to_path, hash_=""):
    """Placeholder link, resolved per output page in finalize()."""
    return f'data-page="{to_path}" data-hash="{hash_}" href="#"'


# ------------------------------------------------------------------ fragments
def services_grid_html(lang):
    cards = []
    for i, s in enumerate(services(lang)):
        target = service_path(lang, s["slug"])
        items = "".join(f"<li>{it}</li>" for it in s["items"])
        cards.append(
            f'<article class="svc tilt reveal"><div class="svc-ico"><svg viewBox="0 0 24 24">{ICONS[i]}</svg></div>'
            f'<h3><a {page_link(target)}>{s["t"]}</a></h3><ul>{items}</ul>'
            f'<a class="svc-link" {page_link(target)}>{T(lang, "svc.learn")}{ARROW}</a></article>'
        )
    cards.append(
        f'<article class="svc more tilt reveal"><div><h3>{T(lang, "svc.more.t")}</h3><p>{T(lang, "svc.more.d")}</p></div>'
        f'<a href="#contact" class="btn btn-gold btn-sm">{T(lang, "svc.more.b")}{ARROW}</a></article>'
    )
    return "".join(cards)


def carousel_html(lang):
    out = []
    for i, p in enumerate(CFG.get("gallery", [])):
        cap = p.get(lang) or p["fr"]
        lazy = "" if i == 0 else ' loading="lazy"'
        out.append(f'<figure class="car-item"><img src="{p["src"]}" alt="{cap}" width="900" height="1200"{lazy} /><figcaption>{cap}</figcaption></figure>')
    return "".join(out)


STAR = '<svg viewBox="0 0 24 24"><path d="M12 2.8l2.8 5.8 6.4.9-4.6 4.5 1.1 6.3L12 17.3l-5.7 3 1.1-6.3L2.8 9.5l6.4-.9z"/></svg>'


QUOTE = '<svg class="rev-quote" viewBox="0 0 24 24"><path d="M9.5 6C6 7.4 4 10 4 13.6V18h5.6v-5.4H6.8c0-2.2 1.2-3.8 3.4-4.8zm10 0C16 7.4 14 10 14 13.6V18h5.6v-5.4h-2.8c0-2.2 1.2-3.8 3.4-4.8z"/></svg>'


def review_list(lang):
    items = [r for r in (CFG.get("reviews") or []) if not (r.get("placeholder") and LISTED)]
    return items[:MAX_REVIEWS]


def review_card(lang, r):
    rating = max(1, min(5, int(r.get("rating", 5))))
    texts = r.get("text") or {}
    text = texts.get(lang) or texts.get("fr", "")
    service = (r.get("service") or {}).get(lang) or (r.get("service") or {}).get("fr", "")
    meta = " · ".join(x for x in [service, r.get("city", "")] if x)
    original = r.get("lang", "fr")
    note = f'<em class="rev-tr">{T(lang, "rev.from." + original)}</em>' if original != lang and texts.get(lang) else ""
    initial = (r["name"].strip()[:1] or "?").upper()
    return (
        f'<figure class="rev-card"><div class="rev-top"><div class="stars" role="img" aria-label="{rating}/5">{STAR * rating}</div>{QUOTE}</div>'
        f'<blockquote>{text}</blockquote>{note}'
        f'<figcaption><span class="rev-avatar" aria-hidden="true">{initial}</span>'
        f'<span class="rev-who"><b>{r["name"]}</b><small>{meta}</small></span></figcaption></figure>'
    )


def reviews_html(lang):
    """Returns (cards_html, moving). With 3+ reviews the row is doubled for a seamless endless scroll."""
    items = review_list(lang)
    if not items:
        return "", False
    cards = "".join(review_card(lang, r) for r in items)
    if len(items) < 3:
        return f'<div class="rev-row">{cards}</div>', False
    return f'<div class="rev-row">{cards}</div><div class="rev-row" aria-hidden="true">{cards}</div>', True


def select_html(lang):
    opts = [f'<option value="">{T(lang, "f.choose")}</option>']
    opts += [f"<option>{s['t']}</option>" for s in services(lang)]
    opts.append(f'<option>{T(lang, "f.other")}</option>')
    return "".join(opts)


def frag(html):
    return BeautifulSoup(html, "html.parser")


# ------------------------------------------------------------------ structured data
AREA_SERVED = [{"@type": "City", "name": "Bagnolet"}, {"@type": "City", "name": "Paris"}]

def business_ld(lang):
    same_as = [u for k, u in (CFG.get("social") or {}).items() if isinstance(u, str) and u.startswith("http")]
    return {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "@id": SITE + "#business",
        "name": "RENOVA MM",
        "url": public_url(home_path(lang)),
        "logo": SITE + "assets/img/renova-mm-logo.png",
        "image": SITE + f"assets/img/og-{lang}.jpg",
        "description": T(lang, "meta.desc"),
        "telephone": CFG.get("phone"),
        "email": CFG.get("email"),
        "address": {"@type": "PostalAddress", "addressLocality": "Bagnolet", "postalCode": "93170", "addressRegion": "Île-de-France", "addressCountry": "FR"},
        "areaServed": AREA_SERVED,
        "knowsLanguage": ["fr", "en"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": T(lang, "svc.eyebrow"),
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["t"], "url": public_url(service_path(lang, s["slug"]))}}
                for s in services(lang)
            ],
        },
        **({"sameAs": same_as} if same_as else {}),
    }


def service_ld(lang, s):
    url = public_url(service_path(lang, s["slug"]))
    return [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": s["h1"],
            "serviceType": s["t"],
            "description": s["intro"],
            "url": url,
            "provider": {"@id": SITE + "#business", "@type": "HomeAndConstructionBusiness", "name": "RENOVA MM", "telephone": CFG.get("phone")},
            "areaServed": AREA_SERVED,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": T(lang, "sp.home"), "item": public_url(home_path(lang))},
                {"@type": "ListItem", "position": 2, "name": T(lang, "sp.services"), "item": public_url(home_path(lang)) + "#services"},
                {"@type": "ListItem", "position": 3, "name": s["t"], "item": url},
            ],
        },
    ]


# ------------------------------------------------------------------ head
def set_head(soup, lang, title, desc, path, alternates, ld):
    head = soup.head
    for sel in ["title", 'meta[name="description"]', 'meta[name="robots"]', 'link[rel="canonical"]', 'link[rel="alternate"]',
                'meta[property^="og:"]', 'meta[name^="twitter:"]', 'script[type="application/ld+json"]']:
        for el in head.select(sel):
            el.decompose()
    url = public_url(path)
    og_img = SITE + f"assets/img/og-{lang}.jpg"
    tags = [
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}" />',
        f'<meta name="robots" content="{"index, follow, max-image-preview:large" if LISTED else "noindex, nofollow"}" />',
        f'<link rel="canonical" href="{url}" />',
    ]
    tags += [f'<link rel="alternate" hreflang="{l}" href="{public_url(p)}" />' for l, p in alternates.items()]
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{public_url(alternates["fr"])}" />')
    tags += [
        '<meta property="og:type" content="website" />',
        '<meta property="og:site_name" content="RENOVA MM" />',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}" />',
        *[f'<meta property="og:locale:alternate" content="{OG_LOCALE[l]}" />' for l in LANGS if l != lang],
        f'<meta property="og:title" content="{title}" />',
        f'<meta property="og:description" content="{desc}" />',
        f'<meta property="og:url" content="{url}" />',
        f'<meta property="og:image" content="{og_img}" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{T(lang, "meta.ogalt")}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{title}" />',
        f'<meta name="twitter:description" content="{desc}" />',
        f'<meta name="twitter:image" content="{og_img}" />',
    ]
    anchor = head.find("meta", attrs={"name": "viewport"})
    for tag in reversed(tags):
        anchor.insert_after(frag(tag))
        anchor.insert_after("\n  ")
    for block in ld:
        head.append(frag(f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>'))
    # tidy whitespace: one tag per line
    for child in list(head.children):
        if isinstance(child, NavigableString) and not isinstance(child, Comment) and not child.strip():
            child.extract()
    for child in list(head.children):
        child.insert_before("\n  ")
    head.append("\n")


# ------------------------------------------------------------------ page builders
def base_soup(lang):
    """The template with this language's texts, contact details and generated parts (paths relative to the site root)."""
    soup = BeautifulSoup(TEMPLATE, "html.parser")
    soup.html["lang"] = lang
    for el in soup.select("[data-i18n]"):
        el.string = T(lang, el["data-i18n"])
    for el in soup.select("[data-i18n-ph]"):
        el["placeholder"] = T(lang, el["data-i18n-ph"])
    for el in soup.select("[data-i18n-alt]"):
        el["alt"] = T(lang, el["data-i18n-alt"])
    # photo of the "Nos engagements" section (chosen in the dashboard)
    sec = CFG.get("sections") or {}
    promise_img = soup.select_one(".promise-photo img")
    if promise_img is not None and sec.get("promise_photo"):
        promise_img["src"] = sec["promise_photo"]
        alt = sec.get(f"promise_alt_{lang}") or sec.get("promise_alt_fr")
        if alt:
            promise_img["alt"] = alt
    phone_digits = re.sub(r"[^\d+]", "", str(CFG.get("phone", "")))
    for el in soup.select("[data-phone]"):
        el.string = CFG.get("phone", "")
    for el in soup.select("[data-phone-link]"):
        el["href"] = "tel:" + phone_digits
    for el in soup.select("[data-email]"):
        el.string = CFG.get("email", "")
    for el in soup.select("[data-email-link]"):
        el["href"] = "mailto:" + CFG.get("email", "")
    grid = soup.find(id="svcGrid")
    grid.clear()
    grid.append(frag(services_grid_html(lang)))
    ring = soup.find(id="carousel")
    ring.clear()
    ring.append(frag(carousel_html(lang)))
    reviews = soup.find(id="reviews")
    if reviews:
        cards, moving = reviews_html(lang)
        if cards:
            track = soup.find(id="reviewsTrack")
            track.clear()
            track.append(frag(cards))
            view = soup.find(id="reviewsViewport")
            view["class"] = view.get("class", []) + ["rev-marquee" if moving else "rev-static"]
            if moving:  # ~8 s per card keeps the speed constant whatever the number of reviews
                view["style"] = f"--rev-dur: {len(review_list(lang)) * 8}s"
        else:
            reviews.decompose()  # no reviews yet -> no section
    sel = soup.find(id="serviceSelect")
    sel.clear()
    sel.append(frag(select_html(lang)))
    for a in soup.select(".lang a[data-lang]"):
        a["class"] = ["active"] if a["data-lang"] == lang else []
        if a["data-lang"] == lang:
            a["aria-current"] = "true"
        elif a.has_attr("aria-current"):
            del a["aria-current"]
    # visitor statistics (Cloudflare Web Analytics, cookie-free) — only when a token is set
    token = (CFG.get("cloudflareAnalyticsToken") or "").strip()
    if token:
        beacon = soup.new_tag("script", type="module", src="https://static.cloudflareinsights.com/beacon.min.js")
        beacon["data-cf-beacon"] = json.dumps({"token": token})
        soup.body.append(beacon)
        soup.body.append("\n")
    # cache-busting versions for our own CSS/JS
    for el in soup.select('link[rel="stylesheet"][href^="css/"], script[src^="js/"]'):
        attr = "href" if el.name == "link" else "src"
        file = el[attr].split("?")[0]
        el[attr] = f"{file}?v={asset_version(file)}"
    return soup


def service_main(lang, idx, home_soup):
    s = services(lang)[idx]
    home = home_path(lang)
    tel = re.sub(r"[^\d+]", "", str(CFG.get("phone", "")))
    chips = "".join(f"<li>{CHECK}<span>{T(lang, f'hero.chip{i}')}</span></li>" for i in range(1, 4))
    items = "".join(f'<li class="sp-item reveal"><span class="p-ico">{CHECK}</span><span>{it}</span></li>' for it in s["items"])
    others = "".join(
        f'<a {page_link(service_path(lang, o["slug"]))}><svg viewBox="0 0 24 24">{ICONS[j]}</svg>{o["t"]}</a>'
        for j, o in enumerate(services(lang)) if j != idx
    )
    html = f"""
  <main id="top">
    <section class="sp-hero">
      <div class="hero-bg" aria-hidden="true"></div>
      <div class="container sp-hero-grid">
        <div>
          <nav class="crumbs reveal" aria-label="Breadcrumb">
            <a {page_link(home)}>{T(lang, "sp.home")}</a><span>›</span>
            <a {page_link(home, "services")}>{T(lang, "sp.services")}</a><span>›</span>
            <span aria-current="page">{s["t"]}</span>
          </nav>
          <span class="eyebrow reveal">{T(lang, "hero.eyebrow")}</span>
          <h1 class="sp-title reveal">{s["h1"]}</h1>
          <p class="hero-sub reveal">{s["intro"]}</p>
          <div class="hero-btns reveal">
            <a {page_link(home, "contact")} class="btn btn-gold"><span>{T(lang, "hero.cta1")}</span>{ARROW}</a>
            <a class="btn btn-line" data-phone-link href="tel:{tel}">{PHONE}<span data-phone>{CFG.get("phone", "")}</span></a>
          </div>
          <ul class="chips reveal">{chips}</ul>
        </div>
        <div class="sp-visual reveal" aria-hidden="true"><div class="sp-icon tilt"><svg viewBox="0 0 24 24">{ICONS[idx]}</svg></div></div>
      </div>
    </section>

    <section class="section light">
      <div class="container">
        <div class="section-head reveal">
          <span class="eyebrow">{s["t"]}</span>
          <h2>{T(lang, "sp.what")}</h2>
        </div>
        <ul class="sp-items">{items}</ul>
      </div>
    </section>

    <section class="section sp-others">
      <div class="container">
        <div class="section-head reveal"><h2>{T(lang, "sp.others")}</h2></div>
        <div class="others reveal">{others}</div>
        <div class="sp-cta reveal">
          <a {page_link(home, "contact")} class="btn btn-gold"><span>{T(lang, "cta.btn")}</span>{ARROW}</a>
          <a class="btn btn-line" data-phone-link href="tel:{tel}">{PHONE}<span data-phone>{CFG.get("phone", "")}</span></a>
        </div>
      </div>
    </section>
  </main>"""
    main = frag(html).find("main")
    # reuse the home page's "how it works" and "promise" sections
    how = copy.copy(home_soup.find(id="how"))
    promise = copy.copy(home_soup.find(id="promise"))
    for cube in promise.select(".cube-scene"):
        cube.decompose()
    promise.find("h2").string = T(lang, "sp.why")
    sections = main.find_all("section", recursive=False)
    sections[1].insert_after(how)
    how.insert_after(promise)
    return main


def link_legal(soup, lang):
    """Footer and form links to the legal notice / privacy policy page."""
    for el, hash_ in [(a, "") for a in soup.select('a[data-i18n="ft.legal"]')] + \
                     [(a, "confidentialite") for a in soup.select('a[data-i18n="ft.privacy"]')]:
        el["data-page"], el["data-hash"], el["href"] = legal_path(lang), hash_, "#"


def legal_main(lang):
    """Legal notice + privacy policy (src/legal-<lang>.html, company details from content/company.json)."""
    company = load_json("company")
    html = (ROOT / "src" / f"legal-{lang}.html").read_text(encoding="utf-8")
    html = html.format(home_link=page_link(home_path(lang)), **company)
    if lang == "fr":
        html = fr_typo(html)
    html = re.sub(r"(?<=[\dA-Z]) (?=\d)|(?<=\d) (?=€)", "\u00a0", html)  # keep numbers (SIREN, VAT, capital) on one line
    main = frag(html).find("main")
    tel = re.sub(r"[^\d+]", "", str(CFG.get("phone", "")))
    for a in main.select("[data-phone-link]"):
        a["href"] = f"tel:{tel}"
    for a in main.select("[data-email-link]"):
        a["href"] = f"mailto:{CFG.get('email', '')}"
    for el in main.select("[data-phone]"):
        el.string = CFG.get("phone", "")
    for el in main.select("[data-email]"):
        el.string = CFG.get("email", "")
    return main


def finalize(soup, out_path):
    """Resolve page links, rewrite asset paths for the page's folder depth, write the file."""
    is_home = out_path.endswith("index.html")
    lang = soup.html["lang"]
    for el in soup.select("[data-page]"):
        h = el["data-hash"]
        el["href"] = rel_link(out_path, el["data-page"]) + (f"#{h}" if h else "")
        del el["data-page"], el["data-hash"]
    if not is_home:  # in-page anchors point back to the home page
        for a in soup.select('a[href^="#"]'):
            h = a["href"][1:]
            a["href"] = rel_link(out_path, home_path(lang)) + (f"#{h}" if h and h != "top" else "")
    for a in soup.select(".lang a[data-lang]"):
        target = out_path if a["data-lang"] == lang else counterpart(out_path, a["data-lang"])
        a["href"] = rel_link(out_path, target)
    depth = out_path.count("/")
    if depth:
        prefix = "../" * depth
        for el in soup.find_all(src=True):
            if is_relative_asset(el["src"]):
                el["src"] = prefix + el["src"]
        for el in soup.find_all("link", href=True):
            if is_relative_asset(el["href"]):
                el["href"] = prefix + el["href"]
    out = ROOT / out_path
    out.parent.mkdir(parents=True, exist_ok=True)
    html = str(soup)
    out.write_text(html if html.startswith("<!DOCTYPE") else "<!DOCTYPE html>\n" + html, encoding="utf-8")
    return out_path


def counterpart(path, lang):
    bare = path[3:] if path.startswith("en/") else path
    return bare if lang == "fr" else "en/" + bare


def is_relative_asset(v):
    return not re.match(r"^(https?:|//|#|mailto:|tel:|data:|javascript:|\.\./)", v)


# ------------------------------------------------------------------ build
def build():
    written = []
    # 1) settings the browser needs — written first so the pages get its cache version (generated — edit content/*.json instead)
    browser_cfg = {k: CFG.get(k) for k in ("phone", "email", "social", "gallery", "web3formsKey")}
    (ROOT / "js" / "config.js").write_text(
        "/* GENERATED by tools/build.py from content/*.json — do not edit by hand. */\n"
        f"window.RENOVA = {json.dumps(browser_cfg, ensure_ascii=False, indent=2)};\n", encoding="utf-8")

    for lang in LANGS:
        home = base_soup(lang)
        link_legal(home, lang)
        set_head(home, lang, T(lang, "meta.title"), T(lang, "meta.desc"), home_path(lang),
                 {l: home_path(l) for l in LANGS}, [business_ld(lang)])
        home_copy = copy.copy(home)  # pristine sections to reuse on service pages
        written.append(finalize(home, home_path(lang)))

        for idx, s in enumerate(services(lang)):
            page = copy.copy(home_copy)
            page.find("main").replace_with(service_main(lang, idx, home_copy))
            for el in page.select('script[type="importmap"], script[src*="scene.js"]'):
                el.decompose()  # no 3D hero on service pages
            path = service_path(lang, s["slug"])
            set_head(page, lang, s["title"], s["intro"][:155].rsplit(" ", 1)[0] + "…" if len(s["intro"]) > 158 else s["intro"],
                     path, {l: service_path(l, s["slug"]) for l in LANGS}, service_ld(lang, s))
            written.append(finalize(page, path))

        legal = copy.copy(home_copy)
        legal.find("main").replace_with(legal_main(lang))
        for el in legal.select('script[type="importmap"], script[src*="scene.js"]'):
            el.decompose()
        set_head(legal, lang, T(lang, "legal.title"), T(lang, "legal.desc"), legal_path(lang),
                 {l: legal_path(l) for l in LANGS}, [])
        legal.head.find("meta", attrs={"name": "robots"})["content"] = "noindex, follow"  # not useful in search results
        written.append(finalize(legal, legal_path(lang)))

    # sitemap with hreflang alternates
    today = datetime.date.today().isoformat()
    groups = [{l: home_path(l) for l in LANGS}] + [{l: service_path(l, s["slug"]) for l in LANGS} for s in services("fr")]
    urls = []
    for g in groups:
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{public_url(p)}"/>' for l, p in g.items())
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{public_url(g["fr"])}"/>'
        for l in LANGS:
            urls.append(f"  <url>\n    <loc>{public_url(g[l])}</loc>\n    <lastmod>{today}</lastmod>{alts}\n  </url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n" if LISTED else "User-agent: *\nDisallow: /\n", encoding="utf-8")

    print(f"Built {len(written)} pages ({'LISTED' if LISTED else 'unlisted / noindex'}) for {SITE}")
    for w in written:
        print("  " + w)
    print("  sitemap.xml, robots.txt")


if __name__ == "__main__":
    build()
