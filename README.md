# RENOVA MM — website

Handyman, maintenance and fit-out services in Bagnolet & Paris. French + English, 3D hero (Three.js).

**Live:** https://aelsaad.github.io/renova-mm/ (GitHub Pages, repo `aelsaad/renova-mm`)

To update the live site: save in the dashboard, or commit and `git push` — GitHub builds and publishes it in 1–2 minutes.
The site is unlisted for now (`"listed": false` in `content/settings.json` → `noindex` + `robots.txt` Disallow).

## Run locally

```bash
python3 -m http.server 5530 --directory "/Users/ahmad/Documents/Claude Projects/Websites/RENOVA-MM-Website"
```

Then open http://localhost:5530. (Opening `index.html` directly from Finder also works, but the 3D scene needs a server in some browsers.)

## Edit content — dashboard (for the site owner)

Photos, reviews and contact details are edited in **Pages CMS**: https://app.pagescms.org
(sign in with GitHub → repository `aelsaad/renova-mm`). Saving commits to GitHub; the workflow
`.github/workflows/deploy.yml` then rebuilds and publishes the site in 1–2 minutes.

- **Galerie photos** — upload a photo (phone photos are shrunk to WebP automatically), FR/EN caption, order.
- **Avis clients** — real reviews only, exact customer text; the 6 most recent visible ones are shown.
  "Exemple de test" entries are hidden automatically once the site is listed.
- **Contact & réseaux sociaux** — phone, email, Facebook/TikTok/… links (empty = hidden), WhatsApp button.

## Edit content — code (developer)

| What | Where |
|---|---|
| Photos, reviews, contact (same as the dashboard) | `content/gallery.json`, `content/reviews.json`, `content/contact.json` |
| Site address, listed on Google, analytics + form keys | `content/settings.json` |
| All texts, French + English | `js/i18n.js` |
| Page layout (all pages) | `src/index.html` |
| Colours, layout styles | `css/styles.css` |
| 3D scene | `js/scene.js` |

Preview locally: `python3 tools/build.py` (needs `pip install beautifulsoup4 pillow` and node), then
`python3 -m http.server 5530`. The generated files (`index.html`, `en/`, `services/`, `js/config.js`,
`sitemap.xml`, `robots.txt`) are not committed — GitHub Actions builds them on every push.

## Folders

- `brand/logo/` — logo files (SVG vector + PNG), favicon
- `brand/brand-guide.html` — brand identity (colours, fonts, logo versions)
- `brand/vectorize_logo.py` — rebuilds the vector logo from `logo/logo.jpeg`
- `photos/` — original photos (not uploaded; the site uses optimised WebP copies in `assets/photos/`)
- `tools/build.py` — builds all pages from `src/index.html` + `js/i18n.js` + `js/config.js`

## Before going live

- Set `"listed": true` in `content/settings.json` (and `siteUrl` once renovamm.fr is connected), push.
- Create a **Google Business Profile** and add the site to **Google Search Console** (submit `sitemap.xml`).

- Paste the real Facebook / TikTok links in the dashboard (Contact & réseaux sociaux), or leave them empty to hide.
- Add the **Mentions légales** and **Politique de confidentialité** pages (required in France); footer links are in `index.html`.
- Confirm the promises shown on the site (free quote, fast response, careful work).
