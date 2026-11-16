# Root ad tools

## cutout.py (device photo -> clean transparent cutout)
Setup once per container: `pip install rembg pymatting scipy opencv-python-headless`
(first run downloads the BiRefNet model, ~1GB, from GitHub into ~/.u2net; ~90s per photo on CPU).

    python3 cutout.py photo.jpg device.png --sheet check.png

Normally you don't call it directly: `_template/scene.py <photo>` runs it and then builds the
rim light, floor shadow and reflection. Flags on scene.py: `--seg` (re-cut a PNG that has a
baked glow/shadow), `--shadow 1.2` (denser shadow, 0.8 lighter), `--refl 0` (no floor reflection).

## studio_shadow.py (the floor shadow; approved by the owner 2026-11-16)
The owner rejected the old shadow: stacked tight contact layers made a hard black line hugging the
base. The approved look is a soft, diffused shadow as from a big softbox above and behind-left at
about 45 degrees: densest exactly where the base meets the floor, falling forward and slightly right,
dissolving smoothly, deep navy rather than black, never darker than CAP (0.50). Nothing shows behind
or to the left of the base's bottom edge. It still grounds the device (it must not look floating).

scene.py uses it by default (`--style soft`). Preview any cutout on the ad floor before building:

    python3 studio_shadow.py device.png preview.png [strength]

Tuning lives at the top of the file (LAYERS, AO, CAP, COLOR). qa/2026-11-16-soft-shadow-before-after.png
shows old vs new on a grey 3/4 laptop, a silver one and a black one. Rules: no stroke, no dark band,
no shadow above the bottom contour, keep it visible enough that the device sits on the floor.

## Build environment (make.py / shot.js)
- make.py finds node_modules/@fontsource in the build dir or any parent and stops if it is missing
  (fonts that silently fail render the title and price in a serif font).
- shot.js picks Chromium from $CHROME or the newest /opt/pw-browsers/chromium-* build, and refuses to
  save a PNG if Poppins or Cairo did not load.

Always open the QA sheet (scene_check.png) before rendering: the zoomed base corners must be
crisp on navy and on white with no pale strip, halo or stair steps.

qa/ holds the before/after proof from 2026-10-21 (Lenovo V15, Dell 5550, HP EliteBook 840,
ThinkPad E16, MSI MP341CQW white monitor).
