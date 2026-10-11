# images.txt: "name url-or-file:path" per line. For each: out/<name>.orig.jpg (source),
# out/<name>.rm.png (background removed, trimmed), out/<name>.rm.jpg (on white 1200x900).
import os, io, requests
from PIL import Image, ImageChops
from rembg import remove, new_session
os.makedirs("out", exist_ok=True)
sess = new_session("isnet-general-use")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept": "image/avif,image/webp,image/png,image/*;q=0.8"}
log = []
def place(cut, path):
    W, Hh = 1200, 900; s = min(W * .88 / cut.width, Hh * .84 / cut.height)
    c2 = cut.resize((max(1, int(cut.width * s)), max(1, int(cut.height * s))), Image.LANCZOS)
    bg = Image.new("RGBA", (W, Hh), (255, 255, 255, 255))
    bg.alpha_composite(c2, ((W - c2.width) // 2, (Hh - c2.height) // 2))
    bg.convert("RGB").save(path, quality=90)
for line in open("images.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    name, url = line.split()[:2]
    try:
        if url.startswith("file:"):
            data = open(url[5:], "rb").read()
        else:
            r = requests.get(url, headers=H, timeout=60); r.raise_for_status(); data = r.content
        im = Image.open(io.BytesIO(data)).convert("RGBA")
        im.thumbnail((1800, 1800), Image.LANCZOS)
        flat = Image.new("RGBA", im.size, (255, 255, 255, 255)); flat.alpha_composite(im)
        flat.convert("RGB").save(f"out/{name}.orig.jpg", quality=88)
        cut = remove(im, session=sess, post_process_mask=True)
        bb = cut.getbbox(); cut = cut.crop(bb) if bb else cut
        cut.save(f"out/{name}.rm.png"); place(cut, f"out/{name}.rm.jpg")
        log.append(f"OK {name} {im.size}")
    except Exception as e:
        log.append(f"FAIL {name} {url} {e}")
open("out/log.txt", "w").write("\n".join(log) + "\n")
print("\n".join(log))
