# Procedural music bed + SFX for the 20s Root promo (royalty-free, synthesized).
# Cue times match scene.html; if you shift scenes, shift the cue lists below.
import numpy as np, wave, sys
out = sys.argv[1] if len(sys.argv) > 1 else "audio.wav"
SR = 48000; T = 20.0; N = int(SR * T); t = np.arange(N) / SR
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
chords = [(0, [45, 52, 57, 60, 64]), (6.0, [41, 48, 53, 57, 60]), (10.7, [48, 55, 60, 64, 67]),
          (14.0, [43, 50, 55, 59, 62]), (17.0, [45, 52, 57, 60, 64])]
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
while b < 17.0:
    add(k, b, .55); add(h, b + .25, .10, pan=.3); b += .5
for s in (2.0, 5.45, 10.1, 13.45, 16.5): add(whoosh(), s, .30)          # scene transitions
add(impact(), 0.6, .75); add(impact(), 18.3, .85)                       # logo in / end card
for i in range(17): add(tick(4200), 1.5 + i * (.7 / 17), .05, pan=(-1) ** i * .2)   # tagline typing
for i in range(10): add(tick(3600), 3.0 + i * .08, .09, pan=(-1) ** i * .15)        # url typing
for s in (6.9, 7.9, 8.9, 9.7): add(click(), s, .32)                     # product highlights
for s in (14.15, 14.5, 14.85, 15.65, 16.05): add(k[:int(.2 * SR)], s, .35); add(click(), s, .18)  # kinetic words
add(pop(), 11.4, .35, pan=.2); add(pop(620, 1150), 12.5, .38, pan=-.2); add(tick(2600, .05), 13.1, .15)
for i in range(4): add(tick(1800, .03), 11.95 + i * .14, .05)            # typing dots
add(click(), 17.95, .4); add(pop(400, 700), 17.1, .25)                  # CTA

mix = np.stack([L, R], 1) * np.clip((T - t) / .6, 0, 1)[:, None]
mix = np.tanh(mix * 1.2) / np.tanh(1.2); mix /= np.abs(mix).max() / .89
pcm = (mix * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("audio ok", out)
