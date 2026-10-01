# RENOVA MM — website

Handyman, maintenance and fit-out services across France. French + English, 3D hero (Three.js).

**Live:** https://aelsaad.github.io/renova-mm/ (GitHub Pages, repo `aelsaad/renova-mm`)

To update the live site: commit and `git push` — GitHub rebuilds it in about a minute.
The site is unlisted for now (`listed: false` in `js/config.js` → `noindex` + `robots.txt` Disallow).

## Run locally

```bash
python3 -m http.server 5530 --directory "/Users/ahmad/Documents/Claude Projects/Websites/RENOVA-MM-Website"
```

Then open http://localhost:5530. (Opening `index.html` directly from Finder also works, but the 3D scene needs a server in some browsers.)

## Edit content

The pages are **generated**: edit the sources, then run the build.

```bash
python3 tools/build.py
```

| What | Where |
|---|---|
| Phone number, email, social network links, gallery photos | `js/config.js` |
| All texts, French + English (incl. service pages, FAQ, page titles) | `js/i18n.js` |
| Page layout (all pages) | `src/index.html` |
| Colours, layout styles | `css/styles.css` (tokens at the top) |
| 3D scene (house, towers, tools) | `js/scene.js` |

The build writes `index.html`, `en/index.html`, the 14 service pages in `services/` and `en/services/`,
`sitemap.xml` and `robots.txt`, and adds the SEO tags (title, description, canonical, hreflang,
Open Graph, structured data). CSS/JS cache versions are set automatically.
Then commit and `git push` — GitHub Pages updates the live site in about a minute.

## Folders

- `brand/logo/` — logo files (SVG vector + PNG), favicon
- `brand/brand-guide.html` — brand identity (colours, fonts, logo versions)
- `brand/vectorize_logo.py` — rebuilds the vector logo from `logo/logo.jpeg`
- `photos/` — original photos (not uploaded; the site uses optimised WebP copies in `assets/photos/`)
- `tools/build.py` — builds all pages from `src/index.html` + `js/i18n.js` + `js/config.js`

## Before going live

- Set `listed: true` in `js/config.js` (and `siteUrl` if you connect renovamm.fr), run the build, push.
- Create a **Google Business Profile** and add the site to **Google Search Console** (submit `sitemap.xml`).

- Paste the real Facebook / Instagram / TikTok / LinkedIn links in `js/config.js` (or set them to "" to hide).
- Add the **Mentions légales** and **Politique de confidentialité** pages (required in France); footer links are in `index.html`.
- Confirm the promises shown on the site (free quote, fast response, careful work).
