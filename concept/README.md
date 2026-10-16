# Root redesign concept (not live)

Structured, enterprise-clean look in Root navy + cyan, Arabic first, Readex Pro headings.
Approved direction on 2026-10-16; final edits pending from the owner before it replaces the live design.

- `gen.py` reads `products.json` from the `site-src` branch (path `SRC` at the top) and writes `out/`:
  index.html and the section pages laptops/desktops/monitors/licenses/repair.html.
- `style.css` and `app.js` are inlined into every page (search, filters/sort, request summary, language toggle).
- Product pages are still copied from the current build; they need the new style before go-live.
- Preview artifact: https://claude.ai/artifact/P4mBfJoz14go5S3ieftLgk
