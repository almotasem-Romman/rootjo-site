# images2.txt: "name path". Upscale small images (EDSR x2/x4), remove background (BiRefNet),
# trim, save out2/<name>.png (transparent, max 1600px) and out2/<name>.webp.
import os, sys, urllib.request
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
os.makedirs("out2", exist_ok=True)
models = {}
def sr(scale):
    if scale not in models:
        p = f"FSRCNN_x{scale}.pb"
        if not os.path.exists(p):
            urllib.request.urlretrieve(f"https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x{scale}.pb", p)
        m = cv2.dnn_superres.DnnSuperResImpl_create(); m.readModel(p); m.setModel("fsrcnn", scale); models[scale] = m
    return models[scale]
sess = new_session("birefnet-general-lite")
log = []
for line in open("images2.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    name, path, *flags = line.split()
    try:
        if path.startswith("http"):
            import urllib.request
            req = urllib.request.Request(path, headers={"User-Agent": "Mozilla/5.0"})
            os.makedirs("dl", exist_ok=True)
            lp = "dl/" + name + ".img"
            open(lp, "wb").write(urllib.request.urlopen(req, timeout=60).read())
            path = lp
        if "cutout" in flags:
            from cutout import cutout as _co
            rr = _co(path)
            rr.thumbnail((1600, 1600), Image.LANCZOS)
            rr.save(f"out2/{name}.png", optimize=True); rr.save(f"out2/{name}.webp", quality=90, method=6)
            log.append(f"OK {name} cutout.py -> {rr.size}"); continue
        if "rawalpha" in flags:
            ra = Image.open(path).convert("RGBA")
            am = (np.asarray(ra.getchannel("A")) > 127).astype(np.uint8) * 255
            n, lab, stats, _ = cv2.connectedComponentsWithStats(am)
            if n > 1:
                big = stats[1:, cv2.CC_STAT_AREA].max()
                keep = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > big * 0.2]
                am = np.isin(lab, keep).astype(np.uint8) * 255
            keepA = Image.fromarray(np.minimum(np.asarray(ra.getchannel("A")), am))
            ra.putalpha(keepA); bb = ra.getbbox(); ra = ra.crop(bb) if bb else ra
            ra.thumbnail((1600, 1600), Image.LANCZOS)
            ra.save(f"out2/{name}.png", optimize=True); ra.save(f"out2/{name}.webp", quality=90, method=6)
            log.append(f"OK {name} rawalpha -> {ra.size}"); continue
        im = Image.open(path).convert("RGB")
        m = max(im.size)
        scale = 3 if m < 600 else 2 if m < 1300 else 1
        if scale > 1:
            bgr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
            up = sr(scale).upsample(bgr)
            im = Image.fromarray(cv2.cvtColor(up, cv2.COLOR_BGR2RGB))
        im.thumbnail((2000, 2000), Image.LANCZOS)
        print("processing", name, im.size, flush=True)
        mask = remove(im, session=sess, only_mask=True, post_process_mask=False)
        m = (np.asarray(mask) > 127).astype(np.uint8) * 255
        if "close" in flags or "fill" in flags:
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        if "biggest" in flags:
            n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
            if n > 1:
                big = stats[1:, cv2.CC_STAT_AREA].max()
                keep = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > big * 0.05]
                m = np.isin(lab, keep).astype(np.uint8) * 255
        if "fill" in flags:
            cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            m = np.zeros_like(m); cv2.drawContours(m, cnts, -1, 255, -1)
        if "hull" in flags:
            pts = cv2.findNonZero(m); h = cv2.convexHull(pts)
            m = np.zeros_like(m); cv2.fillPoly(m, [h], 255)
        soft = Image.fromarray(m).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(1.0))
        cut = im.convert("RGBA"); cut.putalpha(soft)
        bb = cut.getbbox(); cut = cut.crop(bb) if bb else cut
        cut.thumbnail((1600, 1600), Image.LANCZOS)
        cut.save(f"out2/{name}.png", optimize=True)
        cut.save(f"out2/{name}.webp", quality=90, method=6)
        log.append(f"OK {name} x{scale} -> {cut.size}")
    except Exception as e:
        log.append(f"FAIL {name} {e}")
open("out2/log.txt", "w").write("\n".join(log) + "\n"); print("\n".join(log))
