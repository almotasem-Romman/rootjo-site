# Root product cutout: photo (white/light studio bg, or an RGBA png) -> clean transparent device, ready for scene.py.
# Usage: python3 cutout.py SRC OUT.png [--model birefnet-general] [--max 2000] [--keep-alpha] [--no-floor-clean] [--sheet check.png]
#   or:  from cutout import cutout; rgba = cutout('photo.jpg')       (PIL RGBA, trimmed)
# Pipeline
#   1. mask      BiRefNet (rembg, onnx, CPU ~90s) on photos; an RGBA source keeps its own alpha (--keep-alpha forces it)
#   2. edges     guided filter snaps the 1024px model mask to the real image edges at full res (crisp, no stair steps)
#   3. floor     per column, everything under the lowest solid pixel of the device is cut: baked floor shadow,
#                grey studio sweep and the pale strip under the base all go (they made the "pasted on" look)
#   4. halo      soft alpha tail clipped and re-stretched, so no grey/white ring survives on dark backgrounds
#   5. colour    pymatting ML foreground estimation: edge pixels get the device's colour, not the old white bg
# The first run downloads the model (~1GB, github release) into ~/.u2net; later runs reuse it.
import sys, os, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def _box(x, r):
    return ndi.uniform_filter(x, 2 * r + 1, mode='reflect')

def guided(I, p, r, eps):
    """He et al. guided filter, colour guide I (h,w,3 in 0..1), input p (h,w)."""
    mI = np.stack([_box(I[..., c], r) for c in range(3)], -1)
    mp = _box(p, r)
    cov = np.stack([_box(I[..., c] * p, r) for c in range(3)], -1) - mI * mp[..., None]
    var = np.empty(I.shape[:2] + (3, 3))
    for i in range(3):
        for j in range(i, 3):
            var[..., i, j] = var[..., j, i] = _box(I[..., i] * I[..., j], r) - mI[..., i] * mI[..., j]
    var += eps * np.eye(3)
    a = np.linalg.solve(var, cov[..., None])[..., 0]
    b = mp - (a * mI).sum(-1)
    ma = np.stack([_box(a[..., c], r) for c in range(3)], -1)
    return (ma * I).sum(-1) + _box(b, r)

def model_mask(rgb_img, model):
    os.environ.setdefault('OMP_NUM_THREADS', str(os.cpu_count() or 4))
    from rembg import new_session
    m = new_session(model).predict(rgb_img)[0].convert('L')
    return np.asarray(m.resize(rgb_img.size, Image.BICUBIC)).astype(float) / 255

def cutout(src, model='birefnet-general', max_side=2000, keep_alpha=None, floor_clean=True, log=print):
    im = Image.open(src) if isinstance(src, str) else src
    im = im.convert('RGBA')
    if max(im.size) > max_side:
        k = max_side / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    rgb = np.asarray(im.convert('RGB')).astype(float) / 255
    a0 = np.asarray(im.split()[3]).astype(float) / 255
    has_alpha = (a0 < .04).mean() > .03
    if keep_alpha is None: keep_alpha = has_alpha
    if has_alpha:  # transparent png: flatten on white so the model and the guide see a normal studio shot
        rgb = rgb * a0[..., None] + (1 - a0[..., None])
    h, w = a0.shape
    if keep_alpha:
        m = a0; log('cutout: using source alpha')
    else:
        m = model_mask(Image.fromarray((rgb * 255).astype(np.uint8)), model); log(f'cutout: {model} mask')

    # 2. edge snap: guided filter only inside a thin band around the model's edge
    u = max(2, round(min(h, w) / 500))                       # ~2px at 1000px, scales with resolution
    hard = m > .5
    band = ndi.binary_dilation(hard, iterations=3 * u) & ~ndi.binary_erosion(hard, iterations=3 * u)
    g = np.clip(guided(rgb, m, 2 * u, 1e-4), 0, 1)
    a = np.where(band, g, m)
    a = np.minimum(a, ndi.binary_dilation(hard, iterations=2 * u))   # never grow into the floor
    a = np.where(ndi.binary_erosion(hard, iterations=3 * u), 1., a)  # solid interior (screens, glossy panels)

    # 3. floor clean: nothing below the device's own bottom contour
    if floor_clean:
        solid = a > .6
        has = solid.any(0)
        low = np.where(has, h - 1 - np.argmax(solid[::-1], 0), -1)
        low = ndi.minimum_filter1d(np.where(has, low, h), 3)     # stray 1px drips do not lower the contour
        low = np.where(low >= h, -1, low)
        rows = np.arange(h)[:, None]
        under = rows - low[None, :]                              # px below the contour
        fade = np.clip(1 - (under - 1) / (1.5 * u), 0, 1)        # keep 1px anti-aliasing, then zero
        a = np.where((under > 0) & (low[None, :] >= 0), a * fade, a)
        a = np.where(low[None, :] < 0, 0, a)

    # 4. halo: drop the faint tail, keep a tight 1-2px anti-aliased edge
    a = np.clip((a - .06) / .9, 0, 1)
    lab, n = ndi.label(a > .02)
    if n > 1:  # drop specks/islands smaller than 0.2% of the device (dust, logo bits of the studio)
        sizes = ndi.sum(np.ones_like(a), lab, range(1, n + 1))
        a[np.isin(lab, 1 + np.nonzero(sizes < .002 * sizes.max())[0])] = 0

    # 5. colour decontamination
    from pymatting import estimate_foreground_ml
    fg = estimate_foreground_ml(rgb, a, n_big_iterations=2)
    fg = np.where((a >= .98)[..., None], rgb, fg)                # interior pixels untouched
    out = Image.fromarray((np.dstack([np.clip(fg, 0, 1), a]) * 255).round().astype(np.uint8), 'RGBA')
    box = out.split()[3].point(lambda v: 255 if v > 3 else 0).getbbox()
    return out.crop(box)

def sheet(rgba, path):
    """QA sheet: device on navy / white / checker + 3x zoom of the bottom-left and bottom-right corners."""
    w, h = rgba.size; k = 520 / max(w, h); t = rgba.resize((round(w * k), round(h * k)), Image.LANCZOS)
    S = Image.new('RGB', (1600, 1100), (236, 240, 246))
    chk = Image.new('RGB', t.size, 'white')
    for y in range(0, t.height, 16):
        for x in range(0, t.width, 16):
            if (x // 16 + y // 16) % 2: chk.paste((205, 205, 205), (x, y, x + 16, y + 16))
    for i, bg in enumerate([(26, 44, 80), (255, 255, 255), chk]):
        c = Image.new('RGB', t.size, bg) if isinstance(bg, tuple) else bg.copy(); c.paste(t, mask=t)
        S.paste(c, (10 + i * 530, 10))
    zw, zh = min(w // 3, 300), min(h // 4, 100)
    al = np.asarray(rgba.split()[3]) > 128
    for i, fx in enumerate([.2, .8]):  # zoom on the bottom contour (where the base meets the floor)
        x0 = int(np.clip(fx * w - zw / 2, 0, w - zw)); cols = al[:, x0:x0 + zw]
        yb = int(np.nonzero(cols.any(1))[0].max()) if cols.any() else h - 1
        y0 = int(np.clip(yb - zh * .6, 0, max(0, h - zh)))
        z = rgba.crop((x0, y0, x0 + zw, y0 + zh)); z = z.resize((780, round(zh * 780 / zw)), Image.LANCZOS)
        for j, bg in enumerate([(26, 44, 80), (255, 255, 255)]):
            c = Image.new('RGB', (780, 270), bg); c.paste(z, (0, 0), z)
            S.paste(c, (10 + i * 800, 560 + j * 270))
    S.save(path)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--model', default='birefnet-general', help='rembg model: birefnet-general (best), isnet-general-use (fast)')
    ap.add_argument('--max', type=int, default=2000); ap.add_argument('--keep-alpha', action='store_true', default=None)
    ap.add_argument('--no-floor-clean', action='store_true'); ap.add_argument('--sheet')
    o = ap.parse_args()
    r = cutout(o.src, o.model, o.max, o.keep_alpha, not o.no_floor_clean)
    r.save(o.out); print('cutout ->', o.out, r.size)
    if o.sheet: sheet(r, o.sheet); print('sheet ->', o.sheet)
