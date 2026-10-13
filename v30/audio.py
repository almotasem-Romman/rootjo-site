# Procedural music bed + SFX for the 30s Root promo (royalty-free, synthesized). Cue times match scene.html.
# Cue times match scene.html; if you shift scenes, shift the cue lists below.
import numpy as np, wave, sys
out = sys.argv[1] if len(sys.argv) > 1 else "audio.wav"
SR = 48000; T = 30.0; N = int(SR * T); t = np.arange(N) / SR
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)

def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR); j = min(N, i + len(sig)); s = sig[:j - i] * gain
    L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))

def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for k in range(len(x)):
        acc += a * (x[k] - acc); y[k] = acc
    return y

mid = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [(0, [45, 52, 57, 60, 64]), (6.6, [41, 48, 53, 57, 60]), (10.3, [48, 55, 60, 64, 67]), (14.1, [43, 50, 55, 59, 62]),
          (17.6, [45, 52, 57, 60, 64]), (21.3, [41, 48, 53, 57, 60]), (25.0, [48, 55, 60, 64, 67]), (27.4, [45, 52, 57, 60, 64])]
pl = np.zeros(N); pr = np.zeros(N)
for ci, (st, notes) in enumerate(chords):
    en = chords[ci + 1][0] if ci + 1 < len(chords) else T
    i = int(st * SR); j = int(en * SR); tt = np.arange(j - i) / SR
    xf = np.clip(np.minimum(1, tt / .35) * np.minimum(1, (en - st - tt) / .35), 0, 1)
    for n in notes:
        f = mid(n)
        for det, ch in ((0.998, pl), (1.002, pr)):
            ch[i:j] += (np.sin(2*np.pi*f*det*tt) + .35*np.sin(4*np.pi*f*det*tt) + .12*np.sin(6*np.pi*f*det*tt)) * xf
lfo = .75 + .25 * np.sin(2 * np.pi * .25 * t)
fade = np.minimum(1, t / 1.2) * np.clip((T - t) / 1.5, 0, 1)
L += pl * .028 * lfo * fade; R += pr * .028 * lfo * fade

def kick():
    n = int(.35 * SR); tt = np.arange(n) / SR; f = 45 + 70 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    n = int(.06 * SR); x = rng.standard_normal(n); x = x - lp(x, .35)
    return x * np.exp(-np.arange(n) / SR * 70)
def whoosh(d=.6):
    n = int(d * SR); x = rng.standard_normal(n); tt = np.arange(n) / SR
    e = (tt / d) ** 2.2 * np.exp(-np.maximum(0, tt - d * .85) * 40)
    return (lp(x, .08) + .4 * (x - lp(x, .5))) * e
def impact():
    n = int(1.6 * SR); tt = np.arange(n) / SR; f = 30 + 80 * np.exp(-tt * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.8)
    nz = lp(rng.standard_normal(n), .15) * np.exp(-tt * 10) * .5
    sh = (np.sin(2*np.pi*1760*tt) + .6*np.sin(2*np.pi*2637*tt)) * np.exp(-tt * 3.2) * .12
    return boom + nz + sh
def tick(f=3200, d=.035):
    n = int(d * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 120)
def click():
    n = int(.08 * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*1200*tt)*np.exp(-tt*60) + .5*np.sin(2*np.pi*240*tt)*np.exp(-tt*40)
def pop(f0=520, f1=980):
    n = int(.14 * SR); tt = np.arange(n) / SR; f = f0 + (f1 - f0) * np.minimum(1, tt / .05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 28)

k = kick(); h = hat(); b = 2.6
while b < 27.4:
    add(k, b, .55); add(h, b + .25, .10, pan=.3); b += .5
for s in (2.3, 6.3, 9.9, 13.8, 17.3, 21.1, 23.5, 24.85, 27.1): add(whoosh(), s, .30)   # scene transitions
add(impact(), 0.6, .75); add(impact(), 28.6, .85)                        # logo in / end card
for i in range(17): add(tick(4200), 1.5 + i * (.6 / 17), .05, pan=(-1) ** i * .2)   # tagline typing
for i in range(10): add(tick(3600), 2.7 + i * .06, .09, pan=(-1) ** i * .15)        # url typing
for r in range(5): add(click(), 6.75 + r * .13, .22, pan=(-1) ** r * .2)          # category rows
add(pop(), 8.45, .38)                                                     # NEW badge
for base in (10.5, 14.3):
    for k2 in range(4): add(click(), base + k2 * .16, .2, pan=(-1) ** k2 * .25) # cards in
for base in (11.85, 15.65):
    for k2 in range(4): add(tick(2600, .05), base + k2 * .45, .14)            # spotlight
for s in (18.75, 22.0, 22.55, 23.1): add(click(), s, .4)                   # taps
for s in (18.8, 20.35):
    add(whoosh(.45), s, .28)
    for j in range(8): add(tick(5200 - j * 300, .02), s + j * .05, .06)      # glitch sweep
add(pop(), 24.0, .35, pan=.2); add(pop(620, 1150), 24.65, .38, pan=-.2)
for j in range(3): add(tick(1800, .03), 24.42 + j * .08, .05)               # typing dots
for k2 in range(4): add(pop(500 + 60 * k2, 900 + 80 * k2), 25.75 + k2 * .22, .28, pan=(-1) ** k2 * .3)  # pills
add(pop(400, 700), 27.5, .25); add(click(), 28.25, .4)                   # CTA
mix = np.stack([L, R], 1) * np.clip((T - t) / .6, 0, 1)[:, None]
mix = np.tanh(mix * 1.2) / np.tanh(1.2); mix /= np.abs(mix).max() / .89
pcm = (mix * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio ok", out)
