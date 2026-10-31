#!/usr/bin/env python3
"""Build rootjo.com from site.html + products.json (v2 light design).

Usage:  python3 build.py [--out OUT_DIR]
Output: OUT/index.html (live page), OUT/index.preview.html (claude.ai preview body),
        OUT/p/<slug>.html, OUT/<section>.html, OUT/img/..., OUT/sitemap.xml, OUT/robots.txt, OUT/CNAME, OUT/.nojekyll
Config: config.json -> {"ga_id": "G-XXXX", "base_url": "https://rootjo.com"}
Shared CSS: the /*@base*/ and /*@card*/ blocks of site.html are reused by the product and section pages,
so the home page stays the single source of the design tokens and the product card.
"""
import json, os, re, shutil, sys, html, datetime
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "out")
cfg = {"ga_id": "", "base_url": "https://rootjo.com", "whatsapp": "962799167971"}
if os.path.exists(os.path.join(HERE, "config.json")):
    cfg.update(json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8")))
BASE = cfg["base_url"].rstrip("/")
WA = cfg["whatsapp"]
products = json.load(open(os.path.join(HERE, "products.json"), encoding="utf-8"))
visible = [p for p in products if p.get("status") != "hidden"]
TODAY = datetime.date.today()
today = TODAY.isoformat()
E = html.escape

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "p"))
shutil.copytree(os.path.join(HERE, "img"), os.path.join(OUT, "img"))

src = open(os.path.join(HERE, "site.html"), encoding="utf-8").read()
BASE_CSS = re.search(r"/\*@base\*/(.*?)/\*@end\*/", src, re.S).group(1)
CARD_CSS = re.search(r"/\*@card\*/(.*?)/\*@end\*/", src, re.S).group(1)
FONTS = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]+)"', src).group(1)

# ---------- shared vocab ----------
LBL = {
    "cpu": ("المعالج", "Processor"), "ram": ("الذاكرة", "Memory"), "storage": ("التخزين", "Storage"),
    "display": ("الشاشة", "Display"), "gpu": ("كرت الشاشة", "Graphics"), "wifi": ("الشبكة", "Wireless"),
    "ports": ("المنافذ", "Ports"), "keyboard": ("لوحة المفاتيح", "Keyboard"), "security": ("الحماية", "Security"),
    "weight": ("الوزن", "Weight"), "battery": ("البطارية", "Battery"), "os": ("نظام التشغيل", "Operating system"),
    "warranty": ("الكفالة", "Warranty"), "users": ("المستخدمين", "Users"), "duration": ("المدة", "Duration"),
    "devices": ("الأجهزة", "Devices"), "platforms": ("الأنظمة", "Platforms"), "cloud": ("التخزين السحابي", "Cloud storage"),
    "apps": ("التطبيقات", "Apps"), "monitor": ("الشاشة المرفقة", "Monitor"), "inbox": ("داخل العلبة", "In the box"), "type": ("النوع", "Type"), "license": ("الترخيص", "License"), "color": ("اللون", "Color"), "other": ("أخرى", "Other"),
    "panel": ("نوع اللوحة", "Panel"), "refresh": ("معدل التحديث", "Refresh rate"), "hdr": ("الألوان و HDR", "Color & HDR"),
    "eyecare": ("راحة العين", "Eye care"), "audio": ("الصوت", "Audio"), "mount": ("التثبيت والإمالة", "Mount & tilt"),
    "camera": ("الكاميرا", "Camera"), "npu": ("الذكاء الاصطناعي", "AI engine"), "charger": ("الشاحن", "Charger"),
    "cooling": ("التبريد", "Cooling"), "case": ("الكيس", "Case"), "psu": ("مزود الطاقة", "Power supply"),
    "colors": ("دقة الألوان", "Color accuracy"), "usbhub": ("منافذ USB", "USB hub"),
}
COND = {"new": ("جديد بالكرتونة", "New in box"), "open-box": ("جديد بدون كرتونة", "New, no box"),
        "used": ("مستعمل", "Used"), "like-new": ("مستعمل بحالة الجديد", "Used, like new"), "digital": ("ترخيص رقمي", "Digital license")}
CAT_LAT = {"laptop": "Laptop", "desktop": "Desktop", "monitor": "Monitor", "license": "License"}
CSLUG = {"laptop": "laptops", "desktop": "desktops", "monitor": "monitors", "license": "licenses", "repair": "repair"}
PERKS = {
    "win11": ("ويندوز 11 برو أصلي", "Genuine Windows 11 Pro", '<rect x="3" y="3" width="8" height="8"/><rect x="13" y="3" width="8" height="8"/><rect x="3" y="13" width="8" height="8"/><rect x="13" y="13" width="8" height="8"/>'),
    "office": ("أوفيس برو بلس أصلي", "Genuine MS Office Pro Plus", '<path d="M4 6l9-3 7 3v12l-7 3-9-3z"/><path d="M13 3v18"/>'),
    "gift": ("هدية: شنطة وماوس لاسلكي", "Free gift: bag and wireless mouse", '<rect x="3" y="8" width="18" height="13" rx="1"/><path d="M12 8v13M3 12h18M12 8c-2-4-6-4-6-1s4 1 6 1c2 0 6 2 6-1s-4-3-6 1"/>'),
    "gift_mouse": ("هدية: ماوس لاسلكي", "Free gift: wireless mouse", '<rect x="3" y="8" width="18" height="13" rx="1"/><path d="M12 8v13M3 12h18"/>'),
    "macos": ("نظام macOS الأصلي", "Genuine macOS", '<path d="M12 3l1.8 4.7 4.7 1.8-4.7 1.8L12 16l-1.8-4.7-4.7-1.8 4.7-1.8z"/>'),
    "delivery": ("توصيل لكل المملكة، الدفع بعد الاستلام والمعاينة", "Delivery across Jordan, pay after you receive and check it", '<path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>'),
}
SECTIONS = [
    ("laptop", "لابتوبات", "Laptops", "جديد بالكرتونة ومستعمل بحالة ممتازة، وكل جهاز بكفالة واضحة.", "New in box and used in excellent condition, each with a clear warranty."),
    ("desktop", "كمبيوترات مكتبية", "Desktops", "كمبيوترات جاهزة أو تجميع حسب ميزانيتك.", "Ready-made desktops, or one built to your budget."),
    ("monitor", "شاشات", "Monitors", "شاشات جديدة بالكرتونة وبكفالة.", "New-in-box monitors with warranty."),
    ("license", "تراخيص البرامج", "Software licenses", "ويندوز وأوفيس ومايكروسوفت 365 أصلي، والمفتاح بيوصلك بعد الدفع مباشرة.", "Genuine Windows, Office and Microsoft 365, with the key sent right after payment."),
    ("repair", "الصيانة والتجهيز", "Repair & setup", "فحص وإصلاح وترقية وتهيئة لجهازك، ومنعطيك التكلفة قبل أي شغل.", "Diagnosis, repair, upgrades and setup for your device, with the cost quoted before any work."),
]
REPAIR = [
    ("$ diagnose --quote-first", "فحص وتشخيص", "Diagnosis", "نفحص الجهاز ونحدد المشكلة ونعطيك التكلفة قبل أي إصلاح.", "We check the device, find the fault and give you the cost before any repair.", "مرحباً Root، بدي أفحص جهازي. المشكلة: ", "Hi Root, I'd like my device checked. The problem: "),
    ("$ install --windows --office", "تثبيت ويندوز وأوفيس", "Windows & Office setup", "تثبيت نظام نظيف مع تفعيل أصلي وتعريفات كاملة.", "A clean install with genuine activation and all drivers.", "مرحباً Root، بدي تثبيت ويندوز وأوفيس على جهازي. ", "Hi Root, I'd like Windows and Office installed on my device. "),
    ("$ upgrade --ram --ssd", "ترقية الرام والتخزين", "RAM & SSD upgrades", "نرفع سرعة جهازك بإضافة رام أو تركيب SSD.", "Speed up your device with more RAM or an SSD.", "مرحباً Root، بدي أرقّي جهازي (رام / SSD). موديل الجهاز: ", "Hi Root, I'd like to upgrade my device (RAM / SSD). Model: "),
    ("$ clean --tune-up", "تنظيف وتحسين الأداء", "Cleaning & tune-up", "تنظيف داخلي وتحسين أداء الجهاز وحرارته.", "Internal cleaning and a tune-up for speed and temperature.", "مرحباً Root، بدي تنظيف وصيانة لجهازي. ", "Hi Root, I'd like my device cleaned and tuned up. "),
]


def bi(ar, en, tag="span"):
    return f'<{tag} class="t-ar">{ar}</{tag}><{tag} class="t-en">{en}</{tag}>'


def wa_link(text):
    return f"https://wa.me/{WA}?text={quote(text)}"


def is_new(p):
    if not p.get("added") or p.get("status") == "sold":
        return False
    try:
        d = (TODAY - datetime.date.fromisoformat(p["added"])).days
    except ValueError:
        return False
    return 0 <= d <= 10


def hud_label(x, cat):
    v = str(x).lower()
    if cat == "monitor":
        for pat, lab in [(r'"|inch', "SIZE"), (r"hz|ms\b", "REFRESH"), (r"\bips\b|\bva\b|oled|tn\b", "PANEL"), (r"hdr|srgb|dci", "COLOR"),
                         (r"usb|hdmi|dp\b", "PORTS"), (r"stand|pivot|height|vesa", "STAND"), (r"\d+:\d+", "RATIO")]:
            if re.search(pat, v):
                return lab
        return "SPEC"
    if cat == "license":
        for pat, lab in [(r"person|user", "USERS"), (r"month|year|lifetime|permanent", "TERM"), (r"device|pc\b", "DEVICES"), (r"cloud", "CLOUD")]:
            if re.search(pat, v):
                return lab
        return "TYPE"
    if re.search(r"gpu|rtx|gtx|radeon|geforce|quadro|t1000|t500|arc a|nvidia", v) and "cpu" not in v:
        return "GPU"
    for pat, lab in [(r"cpu|core|ryzen|xeon|celeron|pentium|snapdragon|apple|\bm[1-5]\b", "CPU"), (r"ddr|lpddr|ram|unified|^\d+ ?gb$", "RAM"),
                     (r"ssd|nvme|hdd|\btb\b", "SSD"), (r'"|inch|fhd|qhd|uhd|wuxga|oled|retina|touch', "DISPLAY"), (r"wi-?fi|bluetooth", "WIRELESS")]:
        if re.search(pat, v):
            return lab
    return "SPEC"


def order_msgs(p):
    share = f"rootjo.com/p/{p['slug']}"
    n = p["name"]
    if p.get("status") == "sold":
        return (f"مرحباً Root، {n} غير متوفر حالياً. في إشي مشابه؟\n{share}", f"Hi Root, {n} is out of stock. Do you have something similar?\n{share}")
    return (f"مرحباً Root، بدي أطلب: {n} بسعر {p['price']} JD\n{share}", f"Hi Root, I'd like to order: {n} ({p['price']} JD)\n{share}")


WA_USE = '<svg viewBox="0 0 24 24"><use href="#wa-i"/></svg>'
WA_SYMBOL = re.search(r'(<svg width="0" height="0"[^>]*>.*?</svg>)', src, re.S).group(1)


def card(p, pre, bilingual=True, qv=False):
    """Product card, same markup as the home page's JS card()."""
    sold = p.get("status") == "sold"
    c = COND.get(p.get("condition"), ("", ""))
    na, ne = p.get("condition_note_ar") or "", p.get("condition_note_en") or ""
    ctext_ar = E(c[0]) + (f" · {E(na)}" if na else "")
    ctext_en = E(c[1]) + (f" · {E(ne)}" if ne else "")
    ctext = bi(ctext_ar, ctext_en) if bilingual else ctext_ar
    m_ar, m_en = order_msgs(p)
    hud = "".join(f"<li><em>{hud_label(x, p['category'])}</em>{E(x)}</li>" for x in (p.get("card_specs") or [])[:4])
    if sold:
        tag = '<span class="tag">Sold out</span>'
    elif is_new(p):
        tag = '<span class="tag new">New in</span>'
    else:
        tag = '<span class="tag">' + ("Used" if p.get("condition") in ("used", "like-new") else "Digital" if p.get("condition") == "digital" else "New") + "</span>"
    url = f"{pre}p/{p['slug']}.html"
    q = f' data-qv="{E(p["slug"])}"' if qv else ""
    lab_ar = "اطلب مشابه" if sold else "اطلبه"
    lab_en = "Ask for similar" if sold else "Order"
    label = bi(lab_ar, lab_en) if bilingual else lab_ar
    hen = f' data-href-en="{wa_link(m_en)}"' if bilingual else ""
    old = f"<s>{p['old_price']} JD</s>" if p.get("old_price") else ""
    return (f'<article class="card{" sold" if sold else ""}">'
            f'<div class="cmeta"><span>{CAT_LAT.get(p["category"], "")} · {E(p.get("brand") or "")}</span>{tag}</div>'
            f'<a class="cimg" href="{url}"{q} tabindex="-1" aria-hidden="true"><img loading="lazy" src="{pre}{E(p["image"])}" alt=""></a>'
            f'<div class="cbody"><h3 class="cname"><a href="{url}"{q}>{E(p["name"])}</a></h3>'
            f'<div class="ccond {E(p.get("condition", ""))}">{ctext}</div>'
            + (f'<ul class="hud">{hud}</ul>' if hud else "") + "</div>"
            f'<a class="buy" target="_blank" rel="noopener" data-product="{E(p["slug"])}" href="{wa_link(m_ar)}"{hen}><span class="l">{WA_USE}{label}</span>'
            f'<span class="p">{old}<b>{p["price"]}<small>JD</small></b></span></a></article>')


# ---------- home page ----------
def home_sort(p):
    return (p.get("status") == "sold", "".join(chr(0x10FFFF - ord(ch)) for ch in (p.get("added") or "")))

grid0 = "".join(card(p, "", bilingual=False, qv=True) for p in sorted(visible, key=home_sort))
data = json.dumps(visible, ensure_ascii=False).replace("</", "<\\/")
body = src.replace("__PRODUCTS__", data).replace("__GA_ID__", cfg["ga_id"]).replace("__GRID__", grid0)
open(os.path.join(OUT, "index.preview.html"), "w", encoding="utf-8").write(body)

_qs = dict(re.findall(r'data-i18n="(q\d+)">([^<]+)<', body)); _as = dict(re.findall(r'data-i18n="(a\d+)">([^<]+)<', body))
FAQ_LD = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "ar",
    "mainEntity": [{"@type": "Question", "name": _qs[k], "acceptedAnswer": {"@type": "Answer", "text": _as["a" + k[1:]]}} for k in sorted(_qs, key=lambda x: int(x[1:]))]}, ensure_ascii=False)
GA_SNIPPET = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={cfg["ga_id"]}"></script>\n'
    f'<script>window.__gaHead=1;window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{cfg["ga_id"]}");</script>\n') if cfg["ga_id"] else ""
THEME = "#f4f5f7"
STORE_LD = json.dumps({"@context": "https://schema.org", "@type": "Store", "name": "Root Computers", "url": BASE + "/", "logo": BASE + "/img/logo.png",
                       "image": BASE + "/img/og-image.jpg", "telephone": "+" + WA, "email": "info@rootjo.com", "address": {"@type": "PostalAddress", "addressCountry": "JO"},
                       "sameAs": ["https://www.instagram.com/rootcomputers/"]}, ensure_ascii=False)
LIST_LD = json.dumps({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
    {"@type": "ListItem", "position": k + 1, "url": f"{BASE}/p/{p['slug']}", "name": p["name"]} for k, p in enumerate([q for q in visible if q.get("status") != "sold"])]}, ensure_ascii=False)
head = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
{GA_SNIPPET}<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Root - Your Tech Partner. متجر إلكتروني لأجهزة الحواسيب الجديدة والمستعملة، تراخيص البرامج، والصيانة في الأردن. New and used laptops, desktops, monitors, software licenses and repair in Jordan.">
<meta name="theme-color" content="{THEME}">
<link rel="canonical" href="{BASE}/">
<meta property="og:title" content="Root Computers">
<meta property="og:description" content="لابتوبات وكمبيوترات وشاشات جديدة ومستعملة، تراخيص برامج، وصيانة. New and used laptops, licenses and repair in Jordan.">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{BASE}/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="img/favicon.png">
<script>(function(){{var l="ar";try{{l=localStorage.getItem("root-lang")||l}}catch(e){{}}if(location.hash==="#en")l="en";if(location.hash==="#ar")l="ar";document.documentElement.lang=l;document.documentElement.dir=l==="en"?"ltr":"rtl"}})();</script>
<script type="application/ld+json">{STORE_LD}</script>
<script type="application/ld+json">{FAQ_LD}</script>
<script type="application/ld+json">{LIST_LD}</script>
'''
body_live = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", body)
assert body_live.count("</style>") == 1
live = head + body_live.replace("</style>", "\n</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n"
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(live)

# ---------- shared shell for product + section pages ----------
SUB_CSS = BASE_CSS + CARD_CSS + '''
html[lang="ar"] .t-en,html[lang="en"] .t-ar{display:none!important}
body{padding-bottom:30px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(258px,1fr));gap:16px}
.k{display:block;font-family:var(--f-lat);font-size:12.5px;letter-spacing:.3em;text-transform:uppercase;color:var(--cyan-ink)}
.crumbs{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:26px 0 6px;font-size:14px;color:var(--muted)}
.crumbs a{text-decoration:none;color:var(--muted);padding:4px 10px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.5)}
.crumbs a:hover{color:var(--ink);border-color:var(--line-2)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:52px;padding-inline:22px;border-radius:14px;text-decoration:none;font-weight:500;font-size:16px;border:1px solid transparent;cursor:pointer;transition:background .2s,border-color .2s,transform .2s}
.btn:hover{transform:translateY(-1px)}
.btn svg{width:19px;height:19px;flex:none;fill:currentColor}
.btn.pri{background:var(--navy);color:#fff}
.btn.pri:hover{background:var(--navy-hi)}
.btn.sec{border-color:var(--line-2);color:var(--ink);background:rgba(255,255,255,.5)}
.btn.sec:hover{border-color:var(--navy)}
.glass{background:rgba(255,255,255,.62);border:1px solid rgba(255,255,255,.95);box-shadow:0 1px 0 #fff inset,0 24px 50px -40px rgba(15,23,48,.5);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.foot{margin-top:60px;padding-block:28px 40px;border-top:1px solid var(--line)}
.foot .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:var(--muted);font-size:13.5px}
.foot .lat{letter-spacing:.14em;text-transform:uppercase;font-size:12px}
.foot a{color:var(--muted)}
@media (max-width:520px){.ibtn.solid .lbl{display:none}.grid{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
'''

FIELD_JS = '''
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var cv = document.getElementById("field"), ctx = cv.getContext("2d"), W, H, G = [], mx = -1e4, my = -1e4, t0 = performance.now();
  var CH = ">_{}[]/\\\\;:#$=+<>01RT".split("");
  function size() { var dpr = Math.min(window.devicePixelRatio || 1, 2); W = innerWidth; H = innerHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.min(80, Math.floor(W * H / 16000)); G = []; for (var k = 0; k < n; k++) G.push({ x: Math.random() * W, y: Math.random() * H, s: 13 + Math.random() * 15, a: .05 + Math.random() * .08, v: .05 + Math.random() * .14, c: CH[(Math.random() * CH.length) | 0], ph: Math.random() * 6.28 }); }
  function blob(x, y, r, rgb, a) { var g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, "rgba(" + rgb + "," + a + ")"); g.addColorStop(1, "rgba(" + rgb + ",0)"); ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); }
  function frame(now) { var t = (now - t0) / 1000, R = Math.max(W, H) * .5; ctx.clearRect(0, 0, W, H);
    blob(W * (.22 + .08 * Math.sin(t * .11)), H * (.25 + .1 * Math.cos(t * .09)), R, "40,205,228", .10);
    blob(W * (.8 + .07 * Math.cos(t * .08)), H * (.7 + .1 * Math.sin(t * .1)), R * .9, "27,42,82", .06);
    for (var k = 0; k < G.length; k++) { var g = G[k];
      if (!reduce) { g.y -= g.v; g.x += Math.sin(t * .3 + g.ph) * .08; if (g.y < -30) { g.y = H + 30; g.x = Math.random() * W; } }
      var dx = g.x - mx, dy = g.y - my, near = Math.max(0, 1 - Math.sqrt(dx * dx + dy * dy) / 170), a = g.a * (.75 + .25 * Math.sin(t * .8 + g.ph)) + near * .25;
      ctx.font = "300 " + g.s + "px 'Chakra Petch', monospace"; ctx.fillStyle = near > .05 ? "rgba(11,142,164," + a.toFixed(3) + ")" : "rgba(27,42,82," + a.toFixed(3) + ")"; ctx.fillText(g.c, g.x, g.y); } }
  function loop(now) { if (!document.hidden) frame(now); requestAnimationFrame(loop); }
  size(); frame(performance.now());
  addEventListener("resize", function () { size(); frame(performance.now()); });
  addEventListener("pointermove", function (e) { mx = e.clientX; my = e.clientY; }, { passive: true });
  if (!reduce) requestAnimationFrame(loop);
'''


def shell(*, pre, title, desc, canonical, og_image, og_type, ld, css, main, where):
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
{GA_SNIPPET}<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{THEME}">
<link rel="icon" type="image/png" href="{pre}img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<script>(function(){{var l="ar";try{{l=localStorage.getItem("root-lang")||l}}catch(e){{}}if(location.hash==="#en")l="en";if(location.hash==="#ar")l="ar";document.documentElement.lang=l;document.documentElement.dir=l==="en"?"ltr":"rtl"}})();</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{css}</style>
</head>
<body>
<canvas id="field" aria-hidden="true"></canvas>
<header class="top"><div class="wrap bar">
  <a class="logo" href="{pre}index.html" aria-label="Root"><img src="{pre}img/logo.png" alt=""><span class="lname">Root</span></a>
  <div class="tools">
    <button type="button" class="ibtn" id="langBtn"><span class="t-ar">EN</span><span class="t-en lang-ar">عربي</span></button>
    <a class="ibtn solid" target="_blank" rel="noopener" data-product="{E(where)}" href="{wa_link('مرحباً Root، بدي أستفسر عن ')}" data-href-en="{wa_link("Hi Root, I'd like to ask about ")}">{WA_USE}<span class="lbl">{bi("واتساب", "WhatsApp")}</span></a>
  </div>
</div></header>
<main class="wrap">
{main}
</main>
<footer class="foot"><div class="wrap"><span class="lat">Root · Your Tech Partner · <a href="{pre}index.html">rootjo.com</a></span><span><a href="https://www.instagram.com/rootcomputers/" target="_blank" rel="noopener">@rootcomputers</a> · info@rootjo.com · +962 7 9916 7971</span></div></footer>
{WA_SYMBOL}
<script>
(function(){{
  var h=document.documentElement;
  function apply(){{document.querySelectorAll("[data-href-en]").forEach(function(a){{if(!a.dataset.hrefAr)a.dataset.hrefAr=a.getAttribute("href");a.setAttribute("href",h.lang==="en"?a.dataset.hrefEn:a.dataset.hrefAr)}});}}
  apply();
  document.getElementById("langBtn").addEventListener("click",function(){{var l=h.lang==="en"?"ar":"en";h.lang=l;h.dir=l==="en"?"ltr":"rtl";try{{localStorage.setItem("root-lang",l)}}catch(e){{}}apply();}});
  var GA="{cfg['ga_id']}";window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}
  if(/^G-[A-Z0-9]+$/.test(GA)&&!window.__gaHead){{var s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+GA;document.head.appendChild(s);gtag("js",new Date());gtag("config",GA);}}
  document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest('a[href^="https://wa.me"]');if(a)gtag("event","whatsapp_click",{{link_location:"{where}",product:a.getAttribute("data-product")||""}});}});
{FIELD_JS}
}})();
</script>
</body>
</html>
'''


# ---------- product pages ----------
PCSS = SUB_CSS + '''
.prod{display:grid;grid-template-columns:1.1fr 1fr;gap:36px;padding-block:10px 50px;align-items:start}
.gal{position:sticky;top:calc(env(safe-area-inset-top,0px) + 96px);border-radius:28px;aspect-ratio:4/3;max-width:100%;overflow:hidden;
  background:radial-gradient(60% 55% at 50% 52%,#fff,rgba(255,255,255,.35) 75%)}
.gal img{width:100%;height:100%;object-fit:contain;padding:44px 30px 26px;filter:drop-shadow(0 26px 22px rgba(15,23,48,.22))}
.gal .cmeta{position:absolute;inset:18px 20px auto;padding:0}
.sold .gal img{filter:grayscale(1);opacity:.5}
.info{display:flex;flex-direction:column;gap:16px;min-width:0}
.pname{margin:0;font-family:var(--f-lat);font-weight:500;font-size:clamp(28px,3.6vw,42px);line-height:1.12;letter-spacing:.01em;text-transform:uppercase;direction:ltr;text-align:left;text-wrap:balance}
html[dir="rtl"] .pname{text-align:right}
.pprice{display:flex;align-items:baseline;gap:12px;direction:ltr;font-family:var(--f-lat);justify-content:flex-end}
html[dir="ltr"] .pprice{justify-content:flex-start}
.pprice b{font-weight:400;font-size:52px;line-height:1;color:var(--navy);font-variant-numeric:tabular-nums}
.pprice b small{font-size:17px;letter-spacing:.12em;color:var(--cyan-ink);margin-left:5px}
.pprice s{color:var(--faint);font-size:19px}
.about{margin:0;color:var(--muted);font-size:16px}
.soldnote{margin:0;padding:12px 16px;border-radius:14px;border:1px dashed var(--line-2);font-weight:500}
.acts{display:grid;grid-template-columns:1fr auto;gap:8px}
.perks{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.perk{display:flex;gap:10px;align-items:center;font-size:13.5px;line-height:1.4;padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.7);border:1px solid var(--line)}
.perk svg{width:24px;height:24px;flex:none;fill:none;stroke:var(--navy);stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.trust{list-style:none;margin:0;padding:0;display:grid;gap:6px;color:var(--muted);font-size:14.5px}
.trust li{display:flex;gap:10px;align-items:baseline}
.trust li::before{content:">_";font-family:var(--f-lat);color:var(--cyan-ink);direction:ltr;flex:none}
.sh{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:10px 0 16px}
.sh h2{margin:0;font-weight:600;font-size:clamp(24px,3vw,32px)}
html[lang="en"] .sh h2{font-family:var(--f-lat);font-weight:500;text-transform:uppercase}
.specs{margin:0 0 50px;border-radius:22px;overflow:hidden}
.specs div{display:grid;grid-template-columns:minmax(120px,30%) 1fr;gap:14px;padding:13px 22px;border-bottom:1px solid var(--line)}
.specs div:last-child{border:0}
.specs dt{color:var(--muted)}
.specs dd{margin:0;font-family:var(--f-lat);direction:ltr;text-align:left;overflow-wrap:anywhere}
html[dir="rtl"] .specs dd{text-align:right}
.more{grid-template-columns:repeat(3,1fr)}
@media (max-width:860px){.prod{grid-template-columns:1fr;gap:20px}.gal{position:relative;top:auto}.more{grid-template-columns:1fr 1fr}}
@media (max-width:520px){.acts,.perks,.more{grid-template-columns:1fr}.pprice b{font-size:44px}.specs div{grid-template-columns:1fr;gap:2px;padding:11px 18px}}
'''


def product_page(p, others):
    sold = p.get("status") == "sold"
    name = p["name"]
    share = f"rootjo.com/p/{p['slug']}"
    m_ar, m_en = order_msgs(p)
    q_ar, q_en = f"مرحباً Root، عندي سؤال عن {name}\n{share}", f"Hi Root, I have a question about {name}\n{share}"
    c = COND.get(p.get("condition"), ("", ""))
    na, ne = p.get("condition_note_ar") or "", p.get("condition_note_en") or ""
    cond_html = bi(E(c[0]) + (f" · {E(na)}" if na else ""), E(c[1]) + (f" · {E(ne)}" if ne else ""))
    tag = '<span class="tag">Sold out</span>' if sold else ('<span class="tag new">New in</span>' if is_new(p) else '<span class="tag">In stock</span>')
    specs = "".join(f'<div><dt>{bi(*map(E, LBL.get(k, (k, k))))}</dt><dd>{E(v)}</dd></div>' for k, v in p.get("specs", []))
    perks = "".join(f'<div class="perk"><svg viewBox="0 0 24 24" aria-hidden="true">{PERKS[k][2]}</svg>{bi(PERKS[k][0], PERKS[k][1])}</div>' for k in p.get("perks", []) if k in PERKS)
    more = "".join(card(o, "../") for o in others[:3])
    sec = next((s for s in SECTIONS if s[0] == p["category"]), None)
    crumb = (f'<nav class="crumbs" aria-label="breadcrumb"><a href="../index.html">{bi("الرئيسية", "Home")}</a>'
             + (f'<a href="../{CSLUG[p["category"]]}.html">{bi(E(sec[1]), E(sec[2]))}</a>' if sec else "") + "</nav>")
    img_abs = f"{BASE}/img/og/{p['slug']}.jpg"
    title = f"{name} - {p['price']} JD | Root"
    desc = ((p.get("about_ar") or "") + " " + (p.get("about_en") or "")).strip() or name
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name, "image": [img_abs],
          "description": p.get("about_en") or name, "brand": {"@type": "Brand", "name": p.get("brand") or name.split()[0]},
          "offers": {"@type": "Offer", "url": f"{BASE}/p/{p['slug']}", "priceCurrency": "JOD", "price": str(p["price"]),
                     "availability": "https://schema.org/SoldOut" if sold else "https://schema.org/InStock",
                     "itemCondition": "https://schema.org/UsedCondition" if p.get("condition") in ("used", "like-new") else "https://schema.org/NewCondition",
                     "seller": {"@type": "Organization", "name": "Root Computers"}}}
    main = f'''  {crumb}
  <div class="prod{' sold' if sold else ''}">
    <div class="gal glass"><div class="cmeta"><span>{CAT_LAT.get(p["category"], "")} · {E(p.get("brand") or "")}</span>{tag}</div><img src="../{E(p['image'])}" alt="{E(name)}"></div>
    <div class="info">
      <div class="ccond {E(p.get('condition', ''))}">{cond_html}</div>
      <h1 class="pname">{E(name)}</h1>
      <div class="pprice"><b>{p['price']}<small>JD</small></b>{f'<s>{p["old_price"]} JD</s>' if p.get("old_price") else ''}</div>
      <p class="about">{bi(E(p.get('about_ar', '')), E(p.get('about_en', '')))}</p>
      {f'<p class="soldnote">{bi("هذا الجهاز انباع. راسلنا ومنوفرلك بديل مشابه.", "This device is sold. Message us and we will find you a similar one.")}</p>' if sold else ''}
      <div class="acts">
        <a class="btn pri" target="_blank" rel="noopener" data-product="{E(p['slug'])}" href="{wa_link(m_ar)}" data-href-en="{wa_link(m_en)}">{WA_USE}{bi("اطلب مشابه على واتساب" if sold else "اطلبه على واتساب", "Ask for a similar one" if sold else "Order on WhatsApp")}</a>
        <a class="btn sec" target="_blank" rel="noopener" data-product="{E(p['slug'])}" href="{wa_link(q_ar)}" data-href-en="{wa_link(q_en)}">{bi("اسأل عنه", "Ask")}</a>
      </div>
      {f'<div class="perks">{perks}</div>' if perks else ''}
      <ul class="trust">
        <li>{bi("السعر نهائي بالدينار الأردني", "Final price in Jordanian dinars")}</li>
        <li>{bi("التوصيل 3 دنانير داخل عمّان و5 دنانير لباقي المحافظات، والدفع بعد المعاينة", "Delivery: 3 JD in Amman, 5 JD elsewhere, and you pay after checking it")}</li>
        <li>{bi("بدك مواصفات ثانية؟ منوفرلك أي جهاز بالطلب", "Need different specs? We source any device to order")}</li>
      </ul>
    </div>
  </div>
  {f'<div class="sh"><h2>{bi("المواصفات", "Specifications")}</h2><span class="k">Specs</span></div><dl class="specs glass">{specs}</dl>' if specs else ''}
  {f'<div class="sh"><h2>{bi("أجهزة ثانية متوفرة", "More in stock")}</h2><span class="k">More</span></div><div class="grid more">{more}</div>' if more else ''}'''
    return shell(pre="../", title=title, desc=desc, canonical=f"{BASE}/p/{p['slug']}", og_image=img_abs, og_type="product",
                 ld=ld, css=PCSS, main=main, where="product_page")


from PIL import Image, ImageDraw
os.makedirs(os.path.join(OUT, "img", "og"), exist_ok=True)


def og_image(p):
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), (244, 245, 247)); d = ImageDraw.Draw(bg)
    for r in range(520, 0, -8):
        c = int(244 + (255 - 244) * (1 - r / 520)); d.ellipse((W / 2 - r * 1.4, H / 2 - r, W / 2 + r * 1.4, H / 2 + r), fill=(c, c, min(255, c + 2)))
    im = Image.open(os.path.join(HERE, p["image"])).convert("RGBA"); im.thumbnail((int(W * .78), int(H * .82)), Image.LANCZOS)
    bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2), im)
    lg = Image.open(os.path.join(HERE, "img", "logo.png")).convert("RGBA"); lg.thumbnail((150, 100))
    bg.paste(lg, (36, 30), lg)
    bg.save(os.path.join(OUT, "img", "og", p["slug"] + ".jpg"), quality=86)


for p in visible:
    og_image(p)
    others = [o for o in visible if o["slug"] != p["slug"] and o.get("status") == "available"]
    others.sort(key=lambda o: o["category"] != p["category"])
    open(os.path.join(OUT, "p", p["slug"] + ".html"), "w", encoding="utf-8").write(product_page(p, others))

# ---------- section pages (laptops.html, desktops.html, ...) ----------
CCSS = SUB_CSS + '''
.catnav{display:flex;gap:4px;padding:4px;border-radius:14px;background:var(--bg-2);overflow-x:auto;scrollbar-width:none;margin:22px 0 4px;max-width:100%;width:max-content}
.catnav::-webkit-scrollbar{display:none}
.catnav a{flex:none;text-decoration:none;border-radius:10px;padding:7px 14px;font-size:14px;color:var(--muted);white-space:nowrap}
.catnav a[aria-current="page"]{background:var(--paper);color:var(--ink);box-shadow:0 1px 3px rgba(15,23,48,.12)}
.catnav a:hover{color:var(--ink)}
.chead{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:30px 0 22px}
.chead h1{margin:4px 0 0;font-weight:600;font-size:clamp(32px,5vw,52px);line-height:1.15;text-wrap:balance}
html[lang="en"] .chead h1{font-family:var(--f-lat);font-weight:500;text-transform:uppercase}
.chead p{margin:6px 0 0;color:var(--muted);max-width:60ch}
.count{font-family:var(--f-lat);font-size:14px;letter-spacing:.08em;color:var(--muted);white-space:nowrap}
.count b{font-weight:500;font-size:28px;color:var(--navy);margin-inline-end:6px}
.svcs{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.svc{display:flex;flex-direction:column;gap:8px;padding:24px 22px 22px;border-radius:var(--r);min-width:0}
.svc code{font-family:var(--f-lat);font-size:12.5px;color:var(--cyan-ink);direction:ltr;text-align:start}
.svc h2{margin:0;font-size:21px;font-weight:600}
.svc p{margin:0;color:var(--muted);flex:1}
.svc .btn{align-self:flex-start;min-height:46px;font-size:15px;margin-top:6px}
.askbox{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:26px 0 0;padding:22px 24px;border-radius:20px;border:1px dashed var(--line-2);background:rgba(255,255,255,.4)}
.askbox p{margin:0;font-weight:500}
.askbox a{color:var(--navy);font-weight:600}
@media (max-width:520px){.svcs{grid-template-columns:1fr}.catnav{width:auto}}
'''


def cat_page(cid, ar, en, dar, den):
    slug = CSLUG[cid]
    nav = "".join(f'<a href="{CSLUG[c]}.html"{" aria-current=page" if c == cid else ""}>{bi(E(a), E(e))}</a>' for c, a, e, _, _ in SECTIONS)
    if cid == "repair":
        grid = '<div class="svcs">' + "".join(
            f'<article class="svc glass"><code>{E(r[0])}</code><h2>{bi(E(r[1]), E(r[2]))}</h2><p>{bi(E(r[3]), E(r[4]))}</p>'
            f'<a class="btn pri" target="_blank" rel="noopener" data-product="repair" href="{wa_link(r[5])}" data-href-en="{wa_link(r[6])}">{WA_USE}{bi("احجز على واتساب", "Book on WhatsApp")}</a></article>'
            for r in REPAIR) + "</div>"
        count = f'<span class="count"><b>{len(REPAIR)}</b>{bi("خدمات", "services")}</span>'
    else:
        items = sorted([p for p in visible if p["category"] == cid], key=home_sort)
        n = sum(p.get("status") != "sold" for p in items)
        grid = '<div class="grid">' + "".join(card(p, "") for p in items) + "</div>"
        count = f'<span class="count"><b>{n}</b>{bi("متوفر", "in stock")}</span>' if n else f'<span class="count">{bi("حسب الطلب", "Made to order")}</span>'
    main = f'''  <nav class="crumbs" aria-label="breadcrumb"><a href="index.html">{bi("الرئيسية", "Home")}</a></nav>
  <nav class="catnav" aria-label="Sections">{nav}</nav>
  <div class="chead"><div><span class="k">{E(en)}</span><h1>{bi(E(ar), E(en))}</h1><p>{bi(E(dar), E(den))}</p></div>{count}</div>
  {grid}
  <div class="askbox"><p>{bi("ما لقيت اللي بدك ياه؟ قلنا شو بدك ومنوفره لك.", "Can't find what you need? Tell us and we'll source it.")}</p><a href="index.html#request">{bi("اطلب جهازك ←", "Request a device →")}</a></div>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{ar} - Root", "url": f"{BASE}/{slug}",
          "isPartOf": {"@type": "WebSite", "name": "Root Computers", "url": BASE + "/"}}
    if cid != "repair":
        ld["mainEntity"] = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": k + 1, "url": f"{BASE}/p/{p['slug']}", "name": p["name"]} for k, p in enumerate([q for q in visible if q["category"] == cid])]}
    return shell(pre="", title=f"{en} | {ar} - Root Computers", desc=f"{dar} {den}", canonical=f"{BASE}/{slug}",
                 og_image=f"{BASE}/img/og-image.jpg", og_type="website", ld=ld, css=CCSS, main=main, where=f"category_{slug}")


for sec in SECTIONS:
    open(os.path.join(OUT, CSLUG[sec[0]] + ".html"), "w", encoding="utf-8").write(cat_page(*sec))

# ---------- sitemap / robots / pages files ----------
urls = [(BASE + "/", today)] + [(f"{BASE}/{CSLUG[c[0]]}", today) for c in SECTIONS] + [(f"{BASE}/p/{p['slug']}", p.get("added", today)) for p in visible]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
open(os.path.join(OUT, "CNAME"), "w").write("rootjo.com\n")
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print(f"built {len(visible)} products -> {OUT}")
