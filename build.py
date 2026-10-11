#!/usr/bin/env python3
"""Build rootjo.com from site.html + products.json.

Usage:  python3 build.py [--out OUT_DIR]
Output: OUT/index.html (live page), OUT/index.preview.html (claude.ai preview body),
        OUT/p/<slug>.html, OUT/img/..., OUT/sitemap.xml, OUT/robots.txt, OUT/CNAME, OUT/.nojekyll
Config: config.json -> {"ga_id": "G-XXXX", "base_url": "https://rootjo.com"}
"""
import json, os, shutil, sys, html, datetime, base64

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "out")
cfg = {"ga_id": "", "base_url": "https://rootjo.com", "whatsapp": "962799167971"}
if os.path.exists(os.path.join(HERE, "config.json")):
    cfg.update(json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8")))
BASE = cfg["base_url"].rstrip("/")
WA = cfg["whatsapp"]
products = json.load(open(os.path.join(HERE, "products.json"), encoding="utf-8"))
visible = [p for p in products if p.get("status") != "hidden"]
today = datetime.date.today().isoformat()
E = html.escape

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "p"))
shutil.copytree(os.path.join(HERE, "img"), os.path.join(OUT, "img"))

# ---------- home page ----------
src = open(os.path.join(HERE, "site.html"), encoding="utf-8").read()
data = json.dumps(visible, ensure_ascii=False).replace("</", "<\\/")
body = src.replace("__PRODUCTS__", data).replace("__GA_ID__", cfg["ga_id"])
open(os.path.join(OUT, "index.preview.html"), "w", encoding="utf-8").write(body)

fav = "img/favicon.png"
head = f'''<!doctype html>
<html lang="ar">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Root - Your Tech Partner. لابتوبات وكمبيوترات جديدة ومستعملة، تراخيص برامج، وصيانة في الأردن. New and used laptops, desktops, software licenses and repair in Jordan.">
<meta name="theme-color" content="#0b1324">
<link rel="canonical" href="{BASE}/">
<meta property="og:title" content="Root Computers">
<meta property="og:description" content="لابتوبات وكمبيوترات جديدة ومستعملة، تراخيص برامج، وصيانة. New and used laptops, licenses and repair in Jordan.">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{BASE}/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{fav}">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"Store","name":"Root Computers","url":BASE+"/","logo":BASE+"/img/logo.png","image":BASE+"/img/og-image.jpg","telephone":"+"+WA,"address":{"@type":"PostalAddress","addressCountry":"JO"},"sameAs":["https://www.instagram.com/rootcomputers/"]},ensure_ascii=False)}</script>
'''
assert body.count("</style>") == 1
live = head + body.replace("</style>", "\nimg{max-width:100%}[hidden]{display:none!important}\n</style>\n</head>\n<body>") + "\n</body>\n</html>\n"
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(live)

# ---------- product pages ----------
LBL = {
    "cpu": ("المعالج", "Processor"), "ram": ("الذاكرة", "Memory"), "storage": ("التخزين", "Storage"),
    "display": ("الشاشة", "Display"), "gpu": ("كرت الشاشة", "Graphics"), "wifi": ("الشبكة", "Wireless"),
    "ports": ("المنافذ", "Ports"), "keyboard": ("لوحة المفاتيح", "Keyboard"), "security": ("الحماية", "Security"),
    "weight": ("الوزن", "Weight"), "battery": ("البطارية", "Battery"), "os": ("نظام التشغيل", "Operating system"),
    "warranty": ("الكفالة", "Warranty"), "users": ("المستخدمين", "Users"), "duration": ("المدة", "Duration"),
    "devices": ("الأجهزة", "Devices"), "platforms": ("الأنظمة", "Platforms"), "cloud": ("التخزين السحابي", "Cloud storage"),
    "apps": ("التطبيقات", "Apps"), "monitor": ("الشاشة المرفقة", "Monitor"), "inbox": ("داخل العلبة", "In the box"), "type": ("النوع", "Type"), "license": ("الترخيص", "License"), "color": ("اللون", "Color"), "other": ("أخرى", "Other"),
}
COND = {"new": ("جديد بالكرتونة", "New in box"), "open-box": ("مفتوح الكرتونة", "Open box"),
        "used": ("مستعمل", "Used"), "digital": ("ترخيص رقمي", "Digital license")}
CAT = {"laptop": ("لابتوبات", "Laptops"), "desktop": ("كمبيوترات", "Desktops"),
       "license": ("تراخيص", "Licenses"), "accessory": ("إكسسوارات", "Accessories")}
from urllib.parse import quote
PERKS = {
    "win11": ("ويندوز 11 برو أصلي", "Genuine Windows 11 Pro", '<rect x="3" y="3" width="8" height="8"/><rect x="13" y="3" width="8" height="8"/><rect x="3" y="13" width="8" height="8"/><rect x="13" y="13" width="8" height="8"/>'),
    "office": ("أوفيس برو بلس أصلي", "Genuine MS Office Pro Plus", '<path d="M4 6l9-3 7 3v12l-7 3-9-3z"/><path d="M13 3v18"/>'),
    "gift": ("هدية: شنطة وماوس لاسلكي", "Free gift: bag and wireless mouse", '<rect x="3" y="8" width="18" height="13" rx="1"/><path d="M12 8v13M3 12h18M12 8c-2-4-6-4-6-1s4 1 6 1c2 0 6 2 6-1s-4-3-6 1"/>'),
    "gift_mouse": ("هدية: ماوس لاسلكي", "Free gift: wireless mouse", '<rect x="3" y="8" width="18" height="13" rx="1"/><path d="M12 8v13M3 12h18M12 8c-2-4-6-4-6-1s4 1 6 1c2 0 6 2 6-1s-4-3-6 1"/>'),
    "delivery": ("توصيل لكل المملكة، الدفع بعد الاستلام والمعاينة", "Delivery across Jordan, pay after you receive and check it", '<path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>'),
}


def bi(ar, en, tag="span"):
    return f'<{tag} class="t-ar">{ar}</{tag}><{tag} class="t-en">{en}</{tag}>'


def wa_link(text):
    return f"https://wa.me/{WA}?text={quote(text)}"


WA_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'

PCSS = '''
:root{--bg:#f5f8fc;--surface:#ffffff;--fg:#14213d;--muted:#586783;--line:#d9e2ef;--navy:#1b2a52;--cyan:#0e9db9;--cyan-soft:#e0f4f9;--wa:#1a8f4d;--hero:#0b1730;--panel-hi:#ffffff;--panel-lo:#e7edf5;
--font-ar:'Cairo','Segoe UI',Tahoma,sans-serif;--font-mono:'JetBrains Mono',ui-monospace,Consolas,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0b1324;--surface:#121d36;--fg:#e8eefb;--muted:#9aa9c7;--line:#24335a;--navy:#e8eefb;--cyan:#2cc4e3;--cyan-soft:#12304a;--wa:#2fb868;--panel-hi:#2a3d66;--panel-lo:#131e37;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0b1324;--surface:#121d36;--fg:#e8eefb;--muted:#9aa9c7;--line:#24335a;--navy:#e8eefb;--cyan:#2cc4e3;--cyan-soft:#12304a;--wa:#2fb868;--panel-hi:#2a3d66;--panel-lo:#131e37;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;font-family:var(--font-ar);font-size:17px;line-height:1.75;color:var(--fg);background:var(--bg);
 background-image:radial-gradient(900px 500px at 85% -10%,color-mix(in srgb,var(--cyan) 18%,transparent),transparent 70%),radial-gradient(700px 500px at 0% 30%,color-mix(in srgb,#4664eb 10%,transparent),transparent 70%),linear-gradient(color-mix(in srgb,var(--cyan) 7%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--cyan) 7%,transparent) 1px,transparent 1px);
 background-size:auto,auto,72px 72px,72px 72px;background-attachment:fixed}
img{max-width:100%}
a{color:inherit}
:focus-visible{outline:3px solid var(--cyan);outline-offset:3px;border-radius:6px}
html[lang="ar"] .t-en,html[lang="en"] .t-ar{display:none!important}
.wrap{max-width:1080px;margin-inline:auto;padding-inline:20px}
header{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:color-mix(in srgb,var(--bg) 82%,transparent);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;height:64px}
.logo img{height:38px;display:block}
.logo .d{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .logo .l{display:none}:root:not([data-theme="light"]) .logo .d{display:block}}
:root[data-theme="dark"] .logo .l{display:none}:root[data-theme="dark"] .logo .d{display:block}
.hbtns{display:flex;align-items:center;gap:10px}
.lang{font:700 14px/1 var(--font-mono);color:var(--fg);background:transparent;border:1.5px solid var(--line);border-radius:999px;padding:8px 14px;cursor:pointer}
html[lang="en"] .lang{font-family:var(--font-ar);font-size:15px;padding:5px 14px}
.lang:hover{border-color:var(--cyan);color:var(--cyan)}
.navcta{background:var(--wa);color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:7px 16px;border-radius:999px}
.crumb{display:inline-block;margin-top:22px;color:var(--muted);text-decoration:none;font-weight:600}
.crumb:hover{color:var(--cyan)}
.prod{display:grid;grid-template-columns:1.1fr 1fr;gap:40px;padding-block:20px 50px;align-items:start}
.gal{position:relative;background:radial-gradient(circle at 50% 45%,var(--panel-hi),var(--panel-lo) 75%);border:1px solid var(--line);border-radius:22px;overflow:hidden;aspect-ratio:4/3}
.gal img{width:100%;height:100%;object-fit:contain;padding:28px;filter:drop-shadow(0 18px 22px rgba(0,0,0,.28))}
.gal.cover img{object-fit:cover;padding:0}
.sold .gal img{filter:grayscale(1);opacity:.55}
.pbadge{position:absolute;top:14px;inset-inline-start:14px;font-size:14px;font-weight:800;padding:4px 14px;border-radius:999px;background:var(--cyan);color:#04121f}
.sold .pbadge{background:#6b7280;color:#fff}
.info{display:flex;flex-direction:column;gap:14px;min-width:0}
.cond{align-self:flex-start;font-size:14px;font-weight:700;padding:3px 14px;border-radius:999px;background:var(--cyan-soft);color:var(--navy)}
.cond.used{background:color-mix(in srgb,#f0b429 22%,transparent)}
h1{margin:0;font-size:clamp(28px,4.2vw,40px);line-height:1.25;color:var(--navy);text-wrap:balance;direction:ltr;text-align:left}
html[lang="ar"] h1{text-align:right}
.price{display:flex;align-items:baseline;gap:12px;direction:ltr;justify-content:flex-end}
html[lang="en"] .price{justify-content:flex-start}
.price b{font-size:44px;font-weight:800;color:var(--navy);font-variant-numeric:tabular-nums;line-height:1}
.price b small{font-size:20px;color:var(--cyan);margin-left:6px}
.price s{color:var(--muted);font-size:20px}
.about{margin:0;color:var(--muted)}
.soldnote{margin:0;padding:12px 16px;border-radius:12px;border:1.5px dashed var(--line);font-weight:600}
.acts{display:grid;gap:10px}
.btn{display:flex;align-items:center;justify-content:center;gap:10px;padding:14px 20px;border-radius:12px;font-weight:700;font-size:17px;text-decoration:none;transition:transform .2s,filter .2s}
.btn:hover{transform:translateY(-2px)}
.btn svg{width:22px;height:22px;flex:none}
.btn.wa{background:var(--wa);color:#fff}
.btn.ghost{border:1.5px solid var(--line);color:var(--fg)}
.btn.ghost:hover{border-color:var(--cyan)}
.perks{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:4px 0}
.perk{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;background:var(--surface);border:1px solid var(--line);font-size:14px;font-weight:600;line-height:1.4}
.perk svg{width:26px;height:26px;flex:none;stroke:var(--cyan);fill:none;stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round}
@media (max-width:420px){.perks{grid-template-columns:1fr}}
.trust{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:6px;color:var(--muted);font-size:15px}
.trust li{display:flex;gap:8px;align-items:baseline}
.trust li::before{content:">_";font-family:var(--font-mono);color:var(--cyan);font-weight:700;direction:ltr;flex:none}
h2{font-size:26px;color:var(--navy);margin:0 0 14px;display:flex;gap:10px;align-items:center}
h2::before{content:">_";font-family:var(--font-mono);color:var(--cyan);font-size:.7em;direction:ltr}
.specs{background:var(--surface);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin-bottom:50px}
.specs div{display:grid;grid-template-columns:minmax(120px,32%) 1fr;gap:12px;padding:12px 20px;border-bottom:1px solid var(--line)}
.specs div:last-child{border:0}
.specs dt{color:var(--muted)}
.specs dd{margin:0;font-weight:600;direction:ltr;text-align:start;overflow-wrap:anywhere}
html[lang="ar"] .specs dd{text-align:right}
.more{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-bottom:60px}
.mcard{display:flex;gap:12px;align-items:center;padding:12px;background:var(--surface);border:1px solid var(--line);border-radius:14px;text-decoration:none;min-width:0}
.mcard:hover{border-color:var(--cyan)}
.mcard img{width:72px;height:54px;object-fit:contain;background:radial-gradient(circle,var(--panel-hi),var(--panel-lo));border-radius:8px;flex:none}
.mcard span{display:block;font-weight:700;font-size:15px;line-height:1.3;direction:ltr;text-align:start}
.mcard small{color:var(--cyan);font-weight:700;direction:ltr;display:block}
footer{border-top:1px solid var(--line);padding-block:24px 40px;color:var(--muted);font-size:14px}
@media (max-width:760px){.prod{grid-template-columns:1fr;gap:22px}.navcta{display:none}.price b{font-size:38px}}
@media (prefers-reduced-motion:reduce){.btn{transition:none}}
'''


def product_page(p, others):
    sold = p.get("status") == "sold"
    share = f"rootjo.com/p/{p['slug']}"
    name = p["name"]
    if sold:
        m_ar = f"مرحباً Root، {name} غير متوفر حالياً. في إشي مشابه؟\n{share}"
        m_en = f"Hi Root, {name} is out of stock. Do you have something similar?\n{share}"
    else:
        m_ar = f"مرحباً Root، بدي أطلب: {name} بسعر {p['price']} JD\n{share}"
        m_en = f"Hi Root, I'd like to order: {name} ({p['price']} JD)\n{share}"
    q_ar = f"مرحباً Root، عندي سؤال عن {name}\n{share}"
    q_en = f"Hi Root, I have a question about {name}\n{share}"
    cond = COND.get(p.get("condition"), ("", ""))
    note_ar, note_en = p.get("condition_note_ar") or "", p.get("condition_note_en") or ""
    cond_html = bi(E(cond[0]) + (f" · {E(note_ar)}" if note_ar else ""), E(cond[1]) + (f" · {E(note_en)}" if note_en else ""))
    badge = bi("غير متوفر", "Out of stock") if sold else (bi(E(p.get("badge_ar", "")), E(p.get("badge_en", ""))) if p.get("badge_ar") else "")
    specs = "".join(f'<div><dt>{bi(*map(E, LBL.get(k, (k, k))))}</dt><dd>{E(v)}</dd></div>' for k, v in p.get("specs", []))
    more = "".join(
        f'<a class="mcard" href="{E(o["slug"])}.html"><img src="../{E(o["image"])}" alt="" loading="lazy"><div><span>{E(o["name"])}</span><small>{o["price"]} JD</small></div></a>'
        for o in others[:3])
    perks = "".join(f'<div class="perk"><svg viewBox="0 0 24 24" aria-hidden="true">{PERKS[k][2]}</svg>{bi(PERKS[k][0], PERKS[k][1])}</div>' for k in p.get("perks", []) if k in PERKS)
    img_abs = f"{BASE}/img/og/{p['slug']}.jpg"
    title = f"{name} - {p['price']} JD | Root"
    desc = (p.get("about_ar") or "") + " " + (p.get("about_en") or "")
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name, "image": [img_abs],
          "description": p.get("about_en") or name, "brand": {"@type": "Brand", "name": name.split()[0]},
          "offers": {"@type": "Offer", "url": f"{BASE}/p/{p['slug']}", "priceCurrency": "JOD", "price": str(p["price"]),
                     "availability": "https://schema.org/SoldOut" if sold else "https://schema.org/InStock",
                     "itemCondition": "https://schema.org/UsedCondition" if p.get("condition") == "used" else "https://schema.org/NewCondition",
                     "seller": {"@type": "Organization", "name": "Root Computers"}}}
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc.strip())}">
<link rel="canonical" href="{BASE}/p/{p['slug']}">
<meta property="og:type" content="product">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc.strip())}">
<meta property="og:image" content="{img_abs}">
<meta property="og:url" content="{BASE}/p/{p['slug']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b1324">
<link rel="icon" type="image/png" href="../img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=JetBrains+Mono:wght@700&display=swap">
<script>(function(){{var l="ar";try{{l=localStorage.getItem("root-lang")||l}}catch(e){{}}if(location.hash==="#en")l="en";if(location.hash==="#ar")l="ar";document.documentElement.lang=l;document.documentElement.dir=l==="en"?"ltr":"rtl"}})();</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{PCSS}</style>
</head>
<body>
<header><div class="wrap">
  <a class="logo" href="../" aria-label="Root"><img class="l" src="../img/logo.png" alt="Root"><img class="d" src="../img/logo-light-on-dark.png" alt=""></a>
  <div class="hbtns">
    <button type="button" class="lang" id="langBtn"><span class="t-ar">EN</span><span class="t-en">عربي</span></button>
    <a class="navcta" target="_blank" rel="noopener" href="{wa_link('مرحباً Root، أريد الاستفسار عن ')}" data-product="{E(p['slug'])}">{bi("واتساب", "WhatsApp")}</a>
  </div>
</div></header>
<main class="wrap">
  <a class="crumb" href="../#products">{bi("&rarr; كل المنتجات", "&larr; All products")}</a>
  <div class="prod{' sold' if sold else ''}">
    <div class="gal">{f'<span class="pbadge">{badge}</span>' if badge else ''}<img src="../{E(p['image'])}" alt="{E(name)}"></div>
    <div class="info">
      <span class="cond {E(p.get('condition',''))}">{cond_html}</span>
      <h1>{E(name)}</h1>
      <div class="price">{f'<s>{p["old_price"]} JD</s>' if p.get("old_price") else ''}<b>{p['price']}<small>JD</small></b></div>
      <p class="about">{bi(E(p.get('about_ar','')), E(p.get('about_en','')))}</p>
      {f'<p class="soldnote">{bi("هذا المنتج غير متوفر حالياً. راسلنا ونوفرلك بديل مشابه.", "This item is out of stock. Message us and we will find you a similar one.")}</p>' if sold else ''}
      <div class="acts">
        <a class="btn wa" target="_blank" rel="noopener" data-product="{E(p['slug'])}" href="{wa_link(m_ar)}" data-href-en="{wa_link(m_en)}">{WA_ICON}{bi("اطلب مشابه على واتساب" if sold else "اطلبه على واتساب", "Ask for a similar one" if sold else "Order on WhatsApp")}</a>
        <a class="btn ghost" target="_blank" rel="noopener" data-product="{E(p['slug'])}" href="{wa_link(q_ar)}" data-href-en="{wa_link(q_en)}">{bi("اسأل عن الجهاز", "Ask a question")}</a>
      </div>
      {f'<div class="perks">{perks}</div>' if perks else ''}
      <ul class="trust">
        <li>{bi("السعر نهائي بالدينار الأردني", "Final price in Jordanian dinars")}</li>
        <li>{bi("الطلب والاستفسار عبر واتساب", "Order and ask on WhatsApp")}</li>
        <li>{bi("بدك مواصفات ثانية؟ نوفرلك أي جهاز بالطلب", "Need different specs? We source any device to order")}</li>
      </ul>
    </div>
  </div>
  {f'<h2>{bi("المواصفات", "Specifications")}</h2><dl class="specs">{specs}</dl>' if specs else ''}
  {f'<h2>{bi("منتجات ثانية متوفرة", "More available now")}</h2><div class="more">{more}</div>' if more else ''}
</main>
<footer><div class="wrap">Root &middot; Your Tech Partner &middot; <a href="../">rootjo.com</a> &middot; <a href="https://www.instagram.com/rootcomputers/" target="_blank" rel="noopener">@rootcomputers</a></div></footer>
<script>
(function(){{
  var h=document.documentElement;
  function apply(){{document.querySelectorAll("[data-href-en]").forEach(function(a){{if(!a.dataset.hrefAr)a.dataset.hrefAr=a.getAttribute("href");a.setAttribute("href",h.lang==="en"?a.dataset.hrefEn:a.dataset.hrefAr)}});}}
  apply();
  document.getElementById("langBtn").addEventListener("click",function(){{var l=h.lang==="en"?"ar":"en";h.lang=l;h.dir=l==="en"?"ltr":"rtl";try{{localStorage.setItem("root-lang",l)}}catch(e){{}}apply();}});
  var GA="{cfg['ga_id']}";window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}
  if(/^G-[A-Z0-9]+$/.test(GA)){{var s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+GA;document.head.appendChild(s);gtag("js",new Date());gtag("config",GA);}}
  document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest('a[href^="https://wa.me"]');if(a)gtag("event","whatsapp_click",{{link_location:"product_page",product:a.getAttribute("data-product")||""}});}});
}})();
</script>
</body>
</html>
'''


from PIL import Image, ImageDraw
os.makedirs(os.path.join(OUT, "img", "og"), exist_ok=True)
def og_image(p):
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), (244, 247, 251)); d = ImageDraw.Draw(bg)
    for r in range(520, 0, -8):
        c = int(244 + (255 - 244) * (1 - r / 520)); d.ellipse((W/2 - r*1.4, H/2 - r, W/2 + r*1.4, H/2 + r), fill=(c, c, min(255, c + 3)))
    im = Image.open(os.path.join(HERE, p["image"])).convert("RGBA"); im.thumbnail((int(W * .78), int(H * .82)), Image.LANCZOS)
    bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2), im)
    lg = Image.open(os.path.join(HERE, "img", "logo.png")).convert("RGBA"); lg.thumbnail((150, 100))
    bg.paste(lg, (36, 30), lg)
    out = os.path.join(OUT, "img", "og", p["slug"] + ".jpg"); bg.save(out, quality=86)
for p in visible:
    og_image(p)
    others = [o for o in visible if o["slug"] != p["slug"] and o.get("status") == "available"]
    open(os.path.join(OUT, "p", p["slug"] + ".html"), "w", encoding="utf-8").write(product_page(p, others))

# ---------- sitemap / robots / pages files ----------
urls = [(BASE + "/", today)] + [(f"{BASE}/p/{p['slug']}", p.get("added", today)) for p in visible]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
open(os.path.join(OUT, "CNAME"), "w").write("rootjo.com\n")
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print(f"built {len(visible)} products -> {OUT}")
