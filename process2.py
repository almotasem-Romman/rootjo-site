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
        p = f"EDSR_x{scale}.pb"
        if not os.path.exists(p):
            urllib.request.urlretrieve(f"https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x{scale}.pb", p)
        m = cv2.dnn_superres.DnnSuperResImpl_create(); m.readModel(p); m.setModel("edsr", scale); models[scale] = m
    return models[scale]
sess = new_session("birefnet-general")
log = []
for line in open("images2.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    name, path = line.split()[:2]
    try:
        im = Image.open(path).convert("RGB")
        m = max(im.size)
        scale = 4 if m < 600 else 2 if m < 1300 else 1
        if scale > 1:
            bgr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
            up = sr(scale).upsample(bgr)
            im = Image.fromarray(cv2.cvtColor(up, cv2.COLOR_BGR2RGB))
        cut = remove(im, session=sess, post_process_mask=False)
        bb = cut.getbbox(); cut = cut.crop(bb) if bb else cut
        cut.thumbnail((1600, 1600), Image.LANCZOS)
        cut.save(f"out2/{name}.png", optimize=True)
        cut.save(f"out2/{name}.webp", quality=90, method=6)
        log.append(f"OK {name} x{scale} -> {cut.size}")
    except Exception as e:
        log.append(f"FAIL {name} {e}")
open("out2/log.txt", "w").write("\n".join(log) + "\n"); print("\n".join(log))
