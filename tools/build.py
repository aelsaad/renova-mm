#!/usr/bin/env python3
"""Builds the static, SEO-ready pages of the RENOVA MM site.

    python3 tools/build.py        (needs: pip install beautifulsoup4, and node)

Sources (edit these, then re-run the build):
  src/index.html page template (layout of all pages)
  js/i18n.js     all texts, French and English
  js/config.js   phone, email, social links, gallery, siteUrl, listed

Generates:
  index.html, en/index.html                         home pages
  services/<slug>.html, en/services/<slug>.html     one page per service
  sitemap.xml, robots.txt
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

ICONS = [
    '<path d="m15 12-8.4 8.4a2.1 2.1 0 1 1-3-3L12 9"/><path d="m18 15 4-4"/><path d="m21.5 11.5-1.9-1.9a2 2 0 0 1-.6-1.4V7l-2.3-2.3a6 6 0 0 0-4.2-1.7H9l.9.8A6.2 6.2 0 0 1 12 8.4V10l2 2h1.2a2 2 0 0 1 1.4.6l1.9 1.9"/>',
    '<path d="M11 21.7a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7z"/><path d="M12 22V12"/><path d="m3.3 7 7.7 4.7a2 2 0 0 0 2 0L20.7 7"/><path d="m7.5 4.3 9 5.1"/>',
    '<rect x="4" y="3" width="16" height="16" rx="1.5"/><path d="M12 3v16M10 10v2M14 10v2M6 19v2M18 19v2"/>',
    '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0z"/><path d="m14.5 12.5 2-2M11.5 9.5l2-2M8.5 6.5l2-2M17.5 15.5l2-2"/>',
    '<path d="M12 2.7s6 6.2 6 11.3a6 6 0 0 1-12 0c0-5.1 6-11.3 6-11.3z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
    '<path d="M12 22v-5M9 8V2M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z"/>',
    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/>',
]
ARROW = '<svg class="arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg>'
PHONE = ('<svg viewBox="0 0 24 24" class="arrow"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 '
         '2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>')


# ------------------------------------------------------------------ sources
def load_js(rel, var):
    code = f"global.window={{}}; require({json.dumps(str(ROOT / rel))}); process.stdout.write(JSON.stringify(window.{var}))"
    return json.loads(subprocess.run(["node", "-e", code], check=True, capture_output=True, text=True).stdout)


I18N = load_js("js/i18n.js", "I18N")
CFG = load_js("js/config.js", "RENOVA")
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


def select_html(lang):
    opts = [f'<option value="">{T(lang, "f.choose")}</option>']
    opts += [f"<option>{s['t']}</option>" for s in services(lang)]
    opts.append(f'<option>{T(lang, "f.other")}</option>')
    return "".join(opts)


def frag(html):
    return BeautifulSoup(html, "html.parser")


# ------------------------------------------------------------------ structured data
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
        "address": {"@type": "PostalAddress", "addressLocality": "Paris", "addressRegion": "Île-de-France", "addressCountry": "FR"},
        "areaServed": [{"@type": "City", "name": "Paris"}, {"@type": "AdministrativeArea", "name": "Île-de-France"}],
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


def faq_ld(lang):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": T(lang, f"faq.{i}.q"), "acceptedAnswer": {"@type": "Answer", "text": T(lang, f"faq.{i}.a")}}
            for i in range(1, 6)
        ],
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
            "areaServed": [{"@type": "City", "name": "Paris"}, {"@type": "AdministrativeArea", "name": "Île-de-France"}],
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
        beacon = soup.new_tag("script", src="https://static.cloudflareinsights.com/beacon.min.js")
        beacon["defer"] = ""
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
      </div>
    </section>
  </main>"""
    main = frag(html).find("main")
    # reuse the home page's "how it works", "promise" and CTA sections
    how = copy.copy(home_soup.find(id="how"))
    promise = copy.copy(home_soup.find(id="promise"))
    for cube in promise.select(".cube-scene"):
        cube.decompose()
    promise.find("h2").string = T(lang, "sp.why")
    cta = copy.copy(home_soup.select_one("section.cta-band"))
    sections = main.find_all("section", recursive=False)
    sections[1].insert_after(how)
    how.insert_after(promise)
    sections[2].insert_after(cta)
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
    written, pairs = [], []
    for lang in LANGS:
        home = base_soup(lang)
        set_head(home, lang, T(lang, "meta.title"), T(lang, "meta.desc"), home_path(lang),
                 {l: home_path(l) for l in LANGS}, [business_ld(lang), faq_ld(lang)])
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
