# Root promo video kit

Source for the 20-second Root (@rootcomputers) motion-graphics ad: 1080x1920, 30fps, Arabic, dark navy + cyan glow.
This branch is not part of the website (GitHub Pages serves `main` only).

- `scene.html` – the animation. Every frame is a pure function `render(t)`; edit the sections marked `EDIT`.
- `render.mjs` – Playwright: renders 600 JPEG frames (or preview frames).
- `audio.py` – synthesized music bed + SFX, timed to the scenes.
- `build.sh` – frames + audio -> MP4. `PREVIEW="..." ./build.sh` renders check frames only.
- `assets/` – logo pieces, product images, fonts (Cairo, JetBrains Mono).

Scenes: logo 0–2.8s · phone with rootjo.com 2.6–6.2 · 4 product rows 6–10.8 · WhatsApp chat 10.7–14.1 · kinetic text 14–17 · CTA + end card 17–20.
