# Root ad tools

## cutout.py (device photo -> clean transparent cutout)
Setup once per container: `pip install rembg pymatting scipy opencv-python-headless`
(first run downloads the BiRefNet model, ~1GB, from GitHub into ~/.u2net; ~90s per photo on CPU).

    python3 cutout.py photo.jpg device.png --sheet check.png

Normally you don't call it directly: `_template/scene.py <photo>` runs it and then builds the
rim light, contact shadow and reflection. Flags on scene.py: `--seg` (re-cut a PNG that has a
baked glow/shadow), `--shadow 1.2` (heavier contact shadow), `--refl 0` (no floor reflection).

Always open the QA sheet (scene_check.png) before rendering: the zoomed base corners must be
crisp on navy and on white with no pale strip, halo or stair steps.

qa/ holds the before/after proof from 2026-10-21 (Lenovo V15, Dell 5550, HP EliteBook 840,
ThinkPad E16, MSI MP341CQW white monitor).
