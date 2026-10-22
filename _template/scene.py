# Root ad scene pass: product photo (or cutout) -> studio-grade layers that share one geometry.
# Usage: python3 scene.py photo.jpg|cutout.png [--seg] [--rim 0.45] [--refl 0.10] [--shadow 1.0] [--halo 0]
#   A photo with a white/light background is cut by ../_tools/cutout.py (BiRefNet + guided-filter edges +
#   floor clean + colour decontamination). An RGBA png keeps its own alpha but gets the same clean-up;
#   --seg forces the AI mask on it too (use it when the png carries a baked glow/shadow, e.g. PSREF/Dell renders).
# Outputs (in the cwd):
#   laptop.png      the clean cutout (kept so the ad folder has it)
#   laptop_lit.png  cutout + thin cyan rim light (what make.py shows)
#   shadow.png      contact shadow + AO + soft penumbra on the floor (laptop_lit canvas padded by PAD, multiply)
#   refl.png        faint glossy-floor reflection of the base       (same padded canvas, normal blend)
#   scene_check.png QA sheet: cutout on navy/white/checker + zoomed base corners
import sys, os, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, os.environ.get('ROOT_TOOLS', '/mnt/project-files/ads/_tools'))
from cutout import cutout, sheet

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('--seg', action='store_true')
ap.add_argument('--rim', type=float, default=.45); ap.add_argument('--refl', type=float, default=.10)
ap.add_argument('--shadow', type=float, default=1.); ap.add_argument('--halo', type=float, default=0)
o = ap.parse_args()
PAD = 220                                              # make.py uses the same padding

def blur(arr, r):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(arr.astype(float), r)

# ---------- 1. clean cutout ----------
src = cutout(o.src, keep_alpha=False if o.seg else None)
if os.path.abspath(o.src) != os.path.abspath('laptop.png'): src.save('laptop.png')
sheet(src, 'scene_check.png')
rgb = np.asarray(src.convert('RGB')).astype(float)
a = np.asarray(src.split()[3]).astype(float) / 255
if o.halo: a = np.clip((a - o.halo) / (1 - o.halo), 0, 1)
h, w = a.shape
u = w / 1300                                           # every size below is relative to the device width

# ---------- 2. rim light: thin cyan band on silhouette edges facing the upper-left glow ----------
A8 = Image.fromarray((a * 255).astype(np.uint8))
band = np.clip(a - np.asarray(A8.filter(ImageFilter.MinFilter(2 * max(1, round(3 * u)) + 1))) / 255, 0, 1)
gy, gx = np.gradient(np.asarray(A8.filter(ImageFilter.GaussianBlur(3 * u))).astype(float))
mag = np.hypot(gx, gy) + 1e-6
facing = np.clip(gx / mag * .55 + gy / mag * .83, 0, 1)  # inward normal pointing down/right = edge facing up/left
rim = blur(band * facing, 1.2 * u)
rgb = rgb + (np.array([150, 235, 245.]) - rgb) * (rim[..., None] * o.rim)
Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save('laptop_lit.png')

# ---------- 3. floor contact: bottom contour of the base ----------
on = a > .5
xs = np.nonzero(on.any(0))[0]
ys = np.array([np.nonzero(on[:, x])[0].max() for x in xs])
keep = ys >= np.percentile(ys, 30) - 40 * u            # drop lid-only columns that sit above the base
xs, ys = xs[keep], ys[keep]
bottom = [(int(x) + PAD, int(y) + PAD) for x, y in zip(xs, ys)]
L, R = bottom[0], bottom[-1]; F = max(bottom, key=lambda p: p[1])
depth = int(h * .19)
front = F[1] - max(L[1], R[1]) < h * .08               # front-facing shot: flat bottom edge, centred light
if front:
    foot = bottom + [(R[0] - int(w * .07), R[1] - depth), (L[0] + int(w * .07), L[1] - depth)]
else:  # base is a parallelogram: hidden back corner = L + R - F (works whichever way the laptop faces)
    foot = bottom + [(L[0] + R[0] - F[0], L[1] + R[1] - F[1])]
sx = 0 if front else 1                                  # 3/4 views: key light front-left pushes shadows right
W, H = w + 2 * PAD, h + 2 * PAD

def layer(poly=None, line=None, width=0, r=0, dx=0, dy=0, op=1.):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    if poly: d.polygon([(x + dx * u, y + dy * u) for x, y in poly], fill=255)
    if line: d.line([(x + dx * u, y + dy * u) for x, y in line], fill=255, width=max(1, round(width * u)), joint='curve')
    if r: m = m.filter(ImageFilter.GaussianBlur(r * u))
    return m.point(lambda v: int(v * min(1, op * o.shadow)))
def grow(p, k):
    cx = sum(q[0] for q in p) / len(p); cy = sum(q[1] for q in p) / len(p)
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in p]
# The base sits ON the floor: darkest right at the contact line, falling off fast in front of the base,
# a wider soft pool around it. No hard black stroke (it read as a sticker outline).
layers = [
    layer(poly=grow(foot, 1.08), r=55, dx=20 * sx, dy=22, op=.40),  # wide ambient occlusion pool
    layer(poly=foot, r=16, dx=6 * sx, dy=9, op=.58),               # soft body shadow
    layer(poly=foot, r=5, dx=2 * sx, dy=3, op=.85),                # tight under-body shadow
    layer(line=bottom, width=7, r=2.5, dy=4, op=.95),              # contact shadow hugging the edge
    layer(line=bottom, width=12, r=7, dx=2 * sx, dy=8, op=.45),    # occlusion just in front of the base
    layer(poly=foot, r=34, dx=10 * sx, dy=36, op=.20),             # long falloff toward the viewer
]
m = layers[0]
for l in layers[1:]: m = ImageChops.screen(m, l)
sh = Image.new('RGBA', (W, H), (22, 28, 42, 0)); sh.putalpha(m); sh.save('shadow.png')

# ---------- 4. glossy floor reflection of the base (subtle, starts below the contact shadow) ----------
RH = int(h * .10); gap = max(2, round(4 * u))
ref = np.zeros((H, W, 4))
for x, b in zip(xs, ys):
    k = np.arange(1, min(RH, b, h - b + PAD - gap))
    ref[b + PAD + gap + k, x + PAD, :3] = rgb[b - k, x]
    ref[b + PAD + gap + k, x + PAD, 3] = a[b - k, x] * o.refl * (1 - k / RH) ** 3 * 255
Image.fromarray(ref.clip(0, 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(2.2 * u)).save('refl.png')
print('scene', w, h, 'pad', PAD, 'front' if front else '3/4')
