# Root studio shadow: a soft, diffused floor shadow for a device cutout, as if lit by a large softbox
# above and behind-left at about 45 degrees, the way product studios light laptops. It replaces the old
# stack of tight contact layers, which piled up into a hard dark line under the base.
#
# How it is built (all on the padded canvas scene.py uses):
#   1. The floor footprint of the base (its bottom contour + hidden back corner) is swept toward the camera
#      and a little to the right, the way a 45 degree key light from behind-left throws it.
#   2. Several sweeps of growing length are blurred more and more and faded more and more (a big softbox):
#      densest where the base touches the floor, dissolving smoothly away from it. No stroke, no hard edge.
#   3. A soft ambient pool under the footprint keeps the device grounded.
#   4. The total is capped so no part of the floor ever goes darker than CAP.
#
# From scene.py:   mask = studio_shadow(a, PAD, u, foot, strength)   -> 'L' image, W x H padded canvas
# Standalone:      python3 studio_shadow.py cutout.png preview.png [strength]
#                  renders the cutout + shadow on the ad floor colour, to judge a device before building an ad.
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

# ---- tuning; every length is a multiple of u = device width / 1300 (about 0.5 px in the final ad) ----
# Each layer is the floor footprint swept from where it sits toward (dx, dy): right and toward the camera,
# then blurred. Near layers are short, fairly dense and slightly soft; far layers are long, faint and very soft.
LAYERS = (                 # (dx, dy, blur, opacity)
    (2, 5, 4, .42),        # contact: dark only where the base meets the floor, a gradient not a stroke
    (14, 16, 14, .30),     # near penumbra
    (34, 38, 34, .20),     # softbox spread
    (70, 70, 72, .10),     # wide haze toward the camera
)
AO = (1.04, 30, .16)       # ambient pool under the footprint: scale, blur, opacity
CAP = .50                  # darkest the floor may get anywhere
COLOR = (24, 32, 52)       # shadow tint: deep navy, not black


def _poly(W, H, pts):
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.asarray(m).astype(float) / 255


def _screen(total, layer, op):
    return 1 - (1 - total) * (1 - layer * op)


def _swept(W, H, foot, dx, dy, steps=12):
    m = np.zeros((H, W))
    for t in np.linspace(0, 1, steps):
        m = np.maximum(m, _poly(W, H, [(x + dx * t, y + dy * t) for x, y in foot]))
    return m


def studio_shadow(a, PAD, u, foot, strength=1.0):
    """a: device alpha (h x w, 0..1); foot: floor footprint polygon in padded coords. Returns PIL 'L'."""
    h, w = a.shape
    W, H = w + 2 * PAD, h + 2 * PAD
    total = np.zeros((H, W))
    k, r, op = AO
    cx = np.mean([p[0] for p in foot]); cy = np.mean([p[1] for p in foot])
    total = _screen(total, gaussian_filter(_poly(W, H, [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in foot]), r * u), op)
    for dx, dy, r, op in LAYERS:
        total = _screen(total, gaussian_filter(_swept(W, H, foot, dx * u, dy * u), r * u), op)
    # The light comes from behind-left, so no shadow may show above the base's visible bottom edge
    # (left of it or behind it): keep only the floor in front of the bottom contour, with a soft border.
    on = a > .5
    cols = np.nonzero(on.any(0))[0]
    low = np.array([np.nonzero(on[:, x])[0].max() for x in cols]) + PAD
    line = np.interp(np.arange(W), cols + PAD, low)              # flat beyond the device ends
    allowed = (np.arange(H)[:, None] >= line[None, :] - 4 * u).astype(float)
    allowed = np.maximum(allowed, np.pad(a, PAD))                # under the device it is hidden anyway
    total *= gaussian_filter(allowed, 3 * u)
    total = np.clip(total * strength, 0, CAP)
    return Image.fromarray((total * 255).astype(np.uint8), 'L')


def footprint(a, PAD, u):
    """Same floor footprint scene.py builds: the bottom contour plus the hidden back corner."""
    h, w = a.shape
    on = a > .5
    xs = np.nonzero(on.any(0))[0]
    ys = np.array([np.nonzero(on[:, x])[0].max() for x in xs])
    keep = ys >= np.percentile(ys, 30) - 40 * u
    xs, ys = xs[keep], ys[keep]
    bottom = [(int(x) + PAD, int(y) + PAD) for x, y in zip(xs, ys)]
    L, R = bottom[0], bottom[-1]; F = max(bottom, key=lambda p: p[1])
    if F[1] - max(L[1], R[1]) < h * .08:                          # front view: flat bottom edge
        d = int(h * .19)
        return bottom + [(R[0] - int(w * .07), R[1] - d), (L[0] + int(w * .07), L[1] - d)]
    return bottom + [(L[0] + R[0] - F[0], L[1] + R[1] - F[1])]


if __name__ == '__main__':
    import sys
    src = Image.open(sys.argv[1]).convert('RGBA')
    strength = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    a = np.asarray(src.split()[3]).astype(float) / 255
    h, w = a.shape; PAD = 220; u = w / 1300
    m = studio_shadow(a, PAD, u, footprint(a, PAD, u), strength)
    W, H = w + 2 * PAD, h + 2 * PAD
    bg = Image.new('RGB', (W, H), (234, 239, 246))
    out = Image.composite(Image.new('RGB', (W, H), COLOR), bg, m)
    out.paste(src, (PAD, PAD), src)
    out.save(sys.argv[2] if len(sys.argv) > 2 else 'shadow_preview.png')
    print('preview', out.size)
