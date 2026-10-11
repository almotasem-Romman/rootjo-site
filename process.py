# Downloads each image in images.txt ("name url" per line), removes the background,
# trims, and writes out/<name>.png (transparent) and out/<name>.jpg (white, 1200x900).
import os, io, requests
from PIL import Image
from rembg import remove, new_session
os.makedirs("out", exist_ok=True)
sess = new_session("isnet-general-use")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
log = []
for line in open("images.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    name, url, *flags = line.split()
    try:
        r = requests.get(url, headers=H, timeout=60); r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGBA")
        im.save(f"out/{name}.orig.png")
        cut = im if "keepbg" in flags else remove(im, session=sess, post_process_mask=True)
        bb = cut.getbbox(); cut = cut.crop(bb) if bb else cut
        cut.save(f"out/{name}.png")
        W, Hh = 1200, 900; s = min(W * .88 / cut.width, Hh * .86 / cut.height)
        c2 = cut.resize((max(1, int(cut.width * s)), max(1, int(cut.height * s))), Image.LANCZOS)
        bg = Image.new("RGBA", (W, Hh), (255, 255, 255, 255))
        bg.alpha_composite(c2, ((W - c2.width) // 2, (Hh - c2.height) // 2))
        bg.convert("RGB").save(f"out/{name}.jpg", quality=90)
        log.append(f"OK {name} {im.size}")
    except Exception as e:
        log.append(f"FAIL {name} {url} {e}")
open("out/log.txt", "w").write("\n".join(log) + "\n")
print("\n".join(log))
