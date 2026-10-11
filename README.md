# rootjo.com source

This branch holds the source; `main` holds the built site that GitHub Pages serves.

- `site.html` - home page template (Arabic/English). `__PRODUCTS__` and `__GA_ID__` are filled by the build.
- `products.json` - the catalog. `status`: `available`, `sold` (stays listed at the bottom of its section as "غير متوفر / Out of stock"), or `hidden`.
- `img/products/<slug>.webp` - transparent product images (max 1200px).
- `config.json` (optional) - `{"ga_id": "G-XXXX"}`.
- `build.py` - `python3 build.py` writes `out/`: `index.html` (live), `index.preview.html` (claude.ai preview), `p/<slug>.html`, `img/og/<slug>.jpg`, `sitemap.xml`, `robots.txt`, `CNAME`.

Workflow: edit -> build -> preview on claude.ai -> owner approves -> copy `out/` (minus `index.preview.html`) to `main`.
Product images are cut out and upscaled by the workflow on the `asset-pipeline` branch.
