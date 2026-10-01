# RENOVA MM — website

Handyman, maintenance and fit-out services across France. French + English, 3D hero (Three.js).

## Run locally

```bash
python3 -m http.server 5530 --directory "/Users/ahmad/Documents/Claude Projects/Websites/RENOVA-MM-Website"
```

Then open http://localhost:5530. (Opening `index.html` directly from Finder also works, but the 3D scene needs a server in some browsers.)

## Edit content

| What | Where |
|---|---|
| Phone number, email, social network links | `js/config.js` |
| Gallery photos + captions | `js/config.js` (files in `assets/photos/`) |
| All texts (FR / EN) | `js/i18n.js` |
| Colours, layout | `css/styles.css` (tokens at the top) |
| 3D scene (house, towers, tools) | `js/scene.js` |

After editing CSS/JS, bump the `?v=` number in `index.html` so browsers load the new files.

## Folders

- `brand/logo/` — logo files (SVG vector + PNG), favicon
- `brand/brand-guide.html` — brand identity (colours, fonts, logo versions)
- `brand/vectorize_logo.py` — rebuilds the vector logo from `logo/logo.jpeg`
- `photos/` — original photos (only the selected ones are used, optimised, in `assets/photos/`)

## Before going live

- Paste the real Facebook / Instagram / TikTok / LinkedIn links in `js/config.js` (or set them to "" to hide).
- Add the **Mentions légales** and **Politique de confidentialité** pages (required in France); footer links are in `index.html`.
- Confirm the promises shown on the site (free quote, fast response, careful work).
