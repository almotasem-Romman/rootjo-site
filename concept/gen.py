#!/usr/bin/env python3
"""Root redesign concept (not live). Reads ../rootjo-src/products.json and writes out/:
index.html, laptops.html, desktops.html, monitors.html, licenses.html, repair.html, img/.
Arabic first (RTL) with an English toggle, Root navy/cyan, Readex Pro headings."""
import json, os, shutil, html
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/home/claude/rootjo-src"
OUT = os.path.join(HERE, "out")
WA = "962799167971"
E = html.escape
P = [p for p in json.load(open(f"{SRC}/products.json", encoding="utf-8")) if p.get("status") != "hidden"]
FEATURED = "macbook-pro-14-m5-pro"

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(f"{SRC}/img", f"{OUT}/img")
shutil.copytree(f"{SRC}/out/p", f"{OUT}/p")   # product pages stay in the current style for now


def bi(ar, en, tag="span", cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c}><span class="t-ar">{ar}</span><span class="t-en">{en}</span></{tag}>' if tag else f'<span class="t-ar">{ar}</span><span class="t-en">{en}</span>'


def T(ar, en):
    return f'<span class="t-ar">{ar}</span><span class="t-en">{en}</span>'


def wa(text):
    return f"https://wa.me/{WA}?text={quote(text)}"


COND = {"new": ("جديد بالكرتونة", "New in box", "ok"), "open-box": ("مفتوح الكرتونة", "Open box", "ok"),
        "used": ("مستعمل", "Used", "used"), "like-new": ("مستعمل بحالة الجديد", "Used, like new", "used"),
        "digital": ("ترخيص رقمي فوري", "Instant digital key", "ok")}
SECT = [  # id, slug, ar, en, short ar, short en, desc ar, desc en, unit ar, unit en
    ("laptop", "laptops", "لابتوبات", "Laptops", "لابتوب", "Laptop",
     "لابتوبات ألعاب وأعمال ودراسة، جديدة بالكرتونة ومستعملة بحالة ممتازة، وكل جهاز بكفالة مكتوبة.",
     "Gaming, business and study laptops, new in box or used in excellent condition, each with a written warranty.", "جهاز", "models"),
    ("desktop", "desktops", "كمبيوترات مكتبية", "Desktops", "كمبيوتر", "Desktop",
     "كمبيوترات جاهزة للألعاب والشغل، أو تجميع حسب ميزانيتك واستخدامك.",
     "Ready-made gaming and work desktops, or one built to your budget and use.", "جهاز", "systems"),
    ("monitor", "monitors", "شاشات", "Monitors", "شاشة", "Monitor",
     "شاشات جديدة بالكرتونة للشغل والألعاب، من 24.5 لـ 34 إنش، وبكفالة.",
     "New-in-box monitors for work and play, from 24.5 to 34 inches, with warranty.", "شاشة", "displays"),
    ("license", "licenses", "تراخيص البرامج", "Software licenses", "ترخيص", "License",
     "ويندوز وأوفيس ومايكروسوفت 365 وويندوز سيرفر أصلي، والمفتاح بيوصلك بعد الدفع مباشرة.",
     "Genuine Windows, Office, Microsoft 365 and Windows Server, with the key sent right after payment.", "ترخيص", "keys"),
    ("repair", "repair", "الصيانة والتهيئة", "Repair & setup", "صيانة", "Repair",
     "فحص وتشخيص، تثبيت ويندوز وأوفيس، ترقية رام وSSD، وتنظيف وتحسين أداء.",
     "Diagnosis, Windows and Office setup, RAM and SSD upgrades, cleaning and tune-ups.", "خدمات", "services"),
]
ICONS = {
    "laptop": '<rect x="4" y="4" width="16" height="11" rx="1.5"/><path d="M2 19h20l-2-4H4z"/>',
    "desktop": '<rect x="7" y="2" width="10" height="20" rx="1.5"/><path d="M10 6h4M10 9h4"/><circle cx="12" cy="17" r="1.2"/>',
    "monitor": '<rect x="2" y="3" width="20" height="13" rx="2"/><path d="M8 21h8M12 16v5"/>',
    "license": '<circle cx="8" cy="15" r="4"/><path d="M10.8 12.2 20 3M17 6l3 3M15 8l2 2"/>',
    "repair": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "source": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5M11 8v6M8 11h6"/>',
}
REPAIR = [
    ("01 / DIAGNOSTICS", "فحص وتشخيص", "Diagnosis", "نفحص الجهاز ونحدد المشكلة، ومنعطيك التكلفة قبل ما نبلش بأي إصلاح.", "We check the device, find the fault and give you the cost before any repair starts.", "احجز فحص", "Book a check", "مرحباً Root، بدي أفحص جهازي. المشكلة: ", "Hi Root, I'd like my device checked. The problem: "),
    ("02 / OS SETUP", "تثبيت ويندوز وأوفيس", "Windows & Office setup", "تثبيت نظام نظيف مع تفعيل أصلي وكل التعريفات.", "A clean install with genuine activation and all drivers.", "احجز تثبيت", "Book setup", "مرحباً Root، بدي تثبيت ويندوز وأوفيس على جهازي. ", "Hi Root, I'd like Windows and Office installed on my device. "),
    ("03 / UPGRADES", "ترقية الرام والتخزين", "RAM & SSD upgrades", "نرفع سرعة جهازك بإضافة رام أو تركيب SSD، مع نقل ملفاتك.", "Speed up your device with more RAM or an SSD, with your files moved over.", "اطلب ترقية", "Request an upgrade", "مرحباً Root، بدي أرقّي جهازي (رام / SSD). موديل الجهاز: ", "Hi Root, I'd like to upgrade my device (RAM / SSD). Model: "),
    ("04 / THERMALS", "تنظيف وتحسين الأداء", "Cleaning & tune-up", "تنظيف داخلي ومعجون حراري جديد، لجهاز أبرد وأهدى.", "Internal cleaning and fresh thermal paste for a cooler, quieter device.", "احجز تنظيف", "Book a tune-up", "مرحباً Root، بدي تنظيف وصيانة لجهازي. ", "Hi Root, I'd like my device cleaned and tuned up. "),
]
WHY = [
    ("$ pay --on-delivery", "الدفع عند الاستلام", "Pay on delivery", "توصيل لكل المملكة: 3 دنانير داخل عمّان و5 خارجها، وما بتدفع إلا بعد ما تستلم الجهاز وتعاينه.", "Delivery across Jordan: 3 JD inside Amman and 5 JD outside. You only pay after you receive and check the device."),
    ("$ warranty --listed", "كفالة واضحة", "A clear warranty", "مدة الكفالة مكتوبة على كل جهاز: الجديد بكفالته، والمستعمل مفحوص وكفالته محددة.", "The warranty is written on every device: new ones carry their warranty, used ones are inspected with a set warranty."),
    ("$ setup --ready", "جاهز من أول يوم", "Ready from day one", "ويندوز وأوفيس أصليين على أجهزة ويندوز، وmacOS على أجهزة Apple.", "Genuine Windows and Office on Windows devices, and macOS on Apple devices."),
    ("$ license --genuine", "تراخيص أصلية", "Genuine licenses", "مفاتيح تفعيل أصلية لويندوز وأوفيس ومايكروسوفت 365 وويندوز سيرفر، بتوصلك بعد الدفع مباشرة.", "Genuine keys for Windows, Office, Microsoft 365 and Windows Server, sent right after payment."),
    ("$ source --any-device", "نوفّر أي جهاز", "Any device, sourced", "إذا ما لقيت جهازك، منوفره لك بالمواصفات اللي بدك ياها من موردينا.", "If your device isn't listed, we'll source it to your specs through our suppliers."),
]
FAQ = [
    ("كيف بطلب جهاز؟", "How do I order?", "اختار الجهاز واضغط «اطلبه»، أو عبّي نموذج «اطلب جهازك». بنأكدلك التوفر والسعر ومنرتب معك التوصيل.", "Pick a device and tap “Order”, or fill in the request form. We confirm availability and price and arrange delivery."),
    ("كيف التوصيل والدفع؟", "How do delivery and payment work?", "بنوصّل لكل المملكة: 3 دنانير داخل عمّان و5 دنانير خارجها. والدفع عند الاستلام بعد ما تعاين الجهاز.", "We deliver across Jordan: 3 JD inside Amman, 5 JD outside. You pay on delivery after you check the device."),
    ("شو الكفالة؟", "What warranty do I get?", "مدة الكفالة مكتوبة على كل جهاز. الجديد بكفالته، والمستعمل بكفالة أقصر مكتوبة على صفحته.", "The warranty is listed on every device. New devices carry their warranty; used ones carry a shorter one shown on their page."),
    ("شو الفرق بين «جديد بالكرتونة» و«مستعمل»؟", "What's the difference between “new in box” and “used”?", "الجديد بيوصلك بكرتونته الأصلية. المستعمل مفحوص وبحالة ممتازة وبسعر أقل، وحالته وكفالته مكتوبة.", "New devices come sealed in their box. Used ones are inspected, in excellent condition and cheaper, with condition and warranty listed."),
    ("كيف بيوصلني الترخيص؟", "How do I receive a license?", "التراخيص رقمية: بنبعتلك مفتاح التفعيل بعد الدفع مباشرة، وإذا واجهتك مشكلة راسلنا.", "Licenses are digital: we send the key right after payment, and help you if activation gives you trouble."),
]

WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'
ARR = '<i class="arr" aria-hidden="true"></i>'


def ico(k, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[k]}</svg>'


def warranty(p):
    for k, v in p.get("specs", []):
        if k == "warranty":
            return v
    return ""


def card(p):
    sold = p.get("status") == "sold"
    c = COND.get(p.get("condition"), ("", "", "ok"))
    dot = "sold" if sold else c[2]
    st_ar = (c[0] + " · غير متوفر") if sold else c[0]
    st_en = (c[1] + " · Out of stock") if sold else c[1]
    w_ar = p.get("condition_note_ar") or ""
    w_en = p.get("condition_note_en") or ""
    sec = next(s for s in SECT if s[0] == p["category"])
    share = f"rootjo.com/p/{p['slug']}"
    if sold:
        m_ar, m_en = f"مرحباً Root، {p['name']} غير متوفر حالياً. في إشي مشابه؟\n{share}", f"Hi Root, {p['name']} is out of stock. Do you have something similar?\n{share}"
    else:
        m_ar, m_en = f"مرحباً Root، بدي أطلب: {p['name']} بسعر {p['price']} JD\n{share}", f"Hi Root, I'd like to order: {p['name']} ({p['price']} JD)\n{share}"
    save = (p["old_price"] - p["price"]) if p.get("old_price") else 0
    specs = "".join(f"<li>{E(x)}</li>" for x in (p.get("card_specs") or [])[:4])
    brand = p.get("brand") or p["name"].split()[0]
    url = f"p/{p['slug']}.html"
    return f'''<article class="pc{' is-sold' if sold else ''}" data-cond="{E(p.get('condition',''))}" data-price="{p['price']}" data-sold="{1 if sold else 0}" data-added="{E(p.get('added',''))}" data-name="{E(p['name'].lower())}">
  <div class="pc-top"><span class="st"><i class="dot {dot}"></i>{T(E(st_ar), E(st_en))}</span><span class="w">{T(E(w_ar), E(w_en))}</span></div>
  <a class="pc-img" href="{url}" tabindex="-1" aria-hidden="true"><img loading="lazy" src="{E(p['image'])}" alt=""></a>
  <div class="pc-body">
    <div class="kick">{T(sec[4], sec[5])} · {E(brand)}</div>
    <h3><a href="{url}" dir="ltr">{E(p['name'])}</a></h3>
    <ul class="specs">{specs}</ul>
  </div>
  <div class="pc-foot">
    <div class="pr">{f'<s>{p["old_price"]} JD</s>' if save else ''}<b>{p['price']:,} <small>JD</small></b>{f'<em>{T(f"وفّر {save} JD", f"Save {save} JD")}</em>' if save and not sold else ''}</div>
    <div class="acts"><a class="b-ghost" href="{url}">{T("التفاصيل", "Details")}</a><a class="b-dark{' muted' if sold else ''}" target="_blank" rel="noopener" href="{wa(m_ar)}" data-href-en="{wa(m_en)}">{T("اطلب مشابه" if sold else "اطلبه", "Find similar" if sold else "Order")}{ARR}</a></div>
  </div>
</article>'''


CSS = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
JS = open(os.path.join(HERE, "app.js"), encoding="utf-8").read()


def page(title, desc, body, active=""):
    nav = "".join(f'<a href="{s[1]}.html"{" aria-current=page" if s[0] == active else ""}>{T(s[2], s[3])}</a>' for s in SECT)
    search_data = json.dumps([{"n": p["name"], "u": f"p/{p['slug']}.html", "p": p["price"], "i": p["image"], "s": p.get("status")} for p in P], ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="noindex">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=JetBrains+Mono:wght@500;700&family=Readex+Pro:wght@300;500;600;700&display=swap">
<script>(function(){{var l="ar";try{{l=localStorage.getItem("root-lang")||l}}catch(e){{}}if(location.hash==="#en")l="en";document.documentElement.lang=l;document.documentElement.dir=l==="en"?"ltr":"rtl"}})();</script>
<style>{CSS}</style>
</head>
<body>
<div class="concept-tag" aria-hidden="true">CONCEPT · NOT LIVE</div>
<header class="hd"><div class="wrap">
  <button class="burger" type="button" aria-label="Menu" aria-expanded="false" id="burger"><i></i><i></i><i></i></button>
  <a class="logo" href="index.html" aria-label="Root"><img class="l" src="img/logo.png" alt="Root"><img class="d" src="img/logo-light-on-dark.png" alt=""></a>
  <nav class="mainnav" id="mainnav">{nav}</nav>
  <div class="search" role="search">
    <input id="q" type="search" autocomplete="off" data-ph-ar="ابحث: ThinkPad، RTX، MacBook…" data-ph-en="Search: ThinkPad, RTX, MacBook…" placeholder="ابحث: ThinkPad، RTX، MacBook…" aria-label="Search">
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <div class="sres" id="sres" hidden></div>
  </div>
  <button type="button" class="lang" id="langBtn"><span class="t-ar">EN</span><span class="t-en">عربي</span></button>
  <a class="wa-btn" target="_blank" rel="noopener" href="{wa('مرحباً Root، أريد الاستفسار عن ')}" data-href-en="{wa("Hi Root, I'd like to ask about ")}">{WA_SVG}<span>{T("واتساب", "WhatsApp")}</span></a>
</div></header>
{body}
<footer class="ft"><div class="wrap">
  <div class="fgrid">
    <div class="fbrand"><img src="img/logo-light-on-dark.png" alt="Root"><p>{T("Root متجر تقني مبني على الوضوح: مواصفات حقيقية، سعر معلن، وجهاز يناسب استخدامك.", "Root is a tech store built on clarity: real specs, upfront prices, and a device that fits how you use it.")}</p>
      <a class="flink" href="index.html#request">{T("اطلب جهاز بمواصفاتك", "Request a device")}{ARR}</a><a class="flink" target="_blank" rel="noopener" href="{wa('مرحباً Root، ')}" data-href-en="{wa('Hi Root, ')}">{T("راسلنا على واتساب", "Chat on WhatsApp")}{ARR}</a></div>
    <div><h4>{T("الأجهزة", "Hardware")}</h4>{"".join(f'<a href="{s[1]}.html">{T(s[2], s[3])}</a>' for s in SECT[:3])}<a href="index.html#request">{T("توفير بالطلب", "Made to order")}</a></div>
    <div><h4>{T("التراخيص والخدمات", "Licenses & services")}</h4><a href="licenses.html">Microsoft 365 · Office 2021</a><a href="licenses.html">Windows 11 Pro · Server 2019</a><a href="repair.html">{T("الصيانة والترقية", "Repair & upgrades")}</a></div>
    <div><h4>{T("تواصل", "Contact")}</h4><a href="tel:+962791851390"><bdi dir="ltr">+962 7 9185 1390</bdi></a><a target="_blank" rel="noopener" href="https://wa.me/{WA}"><bdi dir="ltr">WhatsApp +962 7 9916 7971</bdi></a><a href="mailto:info@rootjo.com">info@rootjo.com</a><a href="https://www.instagram.com/rootcomputers/" target="_blank" rel="noopener"><bdi dir="ltr">@rootcomputers</bdi></a></div>
  </div>
  <div class="fbot"><span>© 2026 Root · Your Tech Partner · rootjo.com</span><span>{T("الأسعار والتوفر قابلة للتغيير، ويؤكدها فريقنا عند الطلب.", "Prices and availability may change; our team confirms them when you order.")}</span></div>
</div></footer>
<script type="application/json" id="sdata">{search_data}</script>
<script>{JS}</script>
</body>
</html>
'''


def avail(cid):
    return [p for p in P if p["category"] == cid and p.get("status") != "sold"]


# ---------------- home ----------------
F = next(p for p in P if p["slug"] == FEATURED)
fs = dict(F.get("specs", []))
f_save = F["old_price"] - F["price"] if F.get("old_price") else 0
featured = f'''<div class="feat">
  <div class="feat-img"><img src="{F['image']}" alt="{E(F['name'])}"></div>
  <div class="feat-info">
    <div class="feat-head"><span class="eyebrow">{T("الجهاز المميّز · جديد بالكرتونة", "Featured · New in box")}</span><span class="feat-price" dir="ltr">{f'<s>{F["old_price"]:,} JD</s>' if f_save else ''}{F['price']:,} JD</span></div>
    <h2 dir="ltr">{E(F['name'])}</h2>
    <p>{T(E(F['about_ar']), E(F['about_en']))}</p>
    <div class="feat-specs">
      <div><small>{T("المعالج", "Processor")}</small><b dir="ltr">M5 Pro · 18-core</b></div>
      <div><small>{T("كرت الشاشة", "Graphics")}</small><b dir="ltr">20-core GPU</b></div>
      <div><small>{T("الذاكرة / التخزين", "Memory / SSD")}</small><b dir="ltr">24GB · 2TB</b></div>
    </div>
    <div class="feat-foot"><span>{T("الدفع بعد المعاينة عند الاستلام · كفالة سنة", "Pay after inspection on delivery · 1-year warranty")}</span><a class="tlink" href="p/{F['slug']}.html">{T("شوف التفاصيل", "View details")}{ARR}</a></div>
  </div>
</div>'''
tabs = "".join(f'<a class="htab" href="{h}"><code>{n}</code><b>{T(a, e)}</b></a>' for n, a, e, h in [
    ("01 / HARDWARE", "أجهزة جديدة ومستعملة", "New & used devices", "#portfolio"),
    ("02 / MADE-TO-ORDER", "توفير أي جهاز بالطلب", "Any device, to order", "#request"),
    ("03 / LICENSING", "تراخيص مايكروسوفت أصلية", "Genuine Microsoft keys", "licenses.html"),
    ("04 / LAB", "فحص وترقية وصيانة", "Diagnosis & upgrades", "repair.html")])
hero = f'''<section class="hero"><div class="wrap">
  <div class="prompt"><code dir="ltr">root@tech-partner:~$ ./start</code><span>{T("أجهزة للأفراد والشركات", "Computing for people and businesses")}</span></div>
  <h1>{T("شريكك التقني <b>لكل جهاز بتحتاجه</b>", "Your tech partner for <b>every computer you need</b>")}</h1>
  <p class="lead">{T("لابتوبات وكمبيوترات وشاشات جديدة ومستعملة، تراخيص برامج أصلية، وصيانة بأسعار واضحة. وإذا ما لقيت جهازك عندنا، منوفره لك بالطلب لأي مكان بالأردن.", "New and used laptops, desktops and monitors, genuine software licenses, and repairs with clear prices. Can't find your device? We'll source it for you anywhere in Jordan.")}</p>
  <div class="cta"><a class="b-cyan" href="#portfolio">{T("تصفّح الأجهزة المتوفرة", "Browse available devices")}{ARR}</a><a class="b-line" href="#request">{T("اطلب جهاز بمواصفاتك", "Request a custom device")}{ARR}</a></div>
  {featured}
</div><div class="wrap"><nav class="htabs" aria-label="Root">{tabs}</nav></div></section>'''

pcards = ""
for s in SECT:
    if s[0] == "repair":
        cnt = f'{len(REPAIR)} {T(s[8], s[9])}'
    else:
        a = avail(s[0]); cnt = f'{len(a)} {T(s[8], s[9])}'
    pcards += f'''<a class="port" href="{s[1]}.html"><span class="pi">{ico(s[0])}</span><div class="ph"><h3>{T(s[2], s[3])}</h3><span class="cnt">{cnt}</span></div><p>{T(s[6], s[7])}</p><span class="tlink">{T("تصفّح " + s[2], "Explore " + s[3].lower())}{ARR}</span></a>'''
pcards += f'''<a class="port" href="#request"><span class="pi">{ico("source")}</span><div class="ph"><h3>{T("توفير بالطلب", "On-demand sourcing")}</h3><span class="cnt">{T("حسب طلبك", "Custom")}</span></div><p>{T("بدك كرت شاشة معيّن أو مواصفات مش موجودة؟ قلنا استخدامك وميزانيتك ومنوفره لك.", "Need a specific GPU or a spec that isn't listed? Tell us your use and budget and we'll source it.")}</p><span class="tlink">{T("اطلب جهازك", "Request a device")}{ARR}</span></a>'''

fresh = sorted([(p, i) for i, p in enumerate(P) if p.get("status") == "available" and p["category"] != "license"], key=lambda x: (x[0].get("added", ""), -x[1]), reverse=True)[:4]
newgrid = "".join(card(p) for p, _ in fresh)

services = "".join(f'''<div class="svc"><code dir="ltr">{r[0]}</code><h3>{T(r[1], r[2])}</h3><p>{T(r[3], r[4])}</p><a class="tlink" target="_blank" rel="noopener" href="{wa(r[7])}" data-href-en="{wa(r[8])}">{T(r[5], r[6])}{ARR}</a></div>''' for r in REPAIR)
why = "".join(f'''<div class="why"><code dir="ltr">{w[0]}</code><h3>{T(w[1], w[2])}</h3><p>{T(w[3], w[4])}</p></div>''' for w in WHY)
faq = "".join(f'''<details class="qa"{" open" if i == 0 else ""}><summary>{T(q[0], q[1])}</summary><p>{T(q[2], q[3])}</p></details>''' for i, q in enumerate(FAQ))


def picks(name, opts, typ="radio", first=False):
    return "".join(f'<label class="pk"><input type="{typ}" name="{name}" value="{v}" data-ar="{a}" data-en="{e}"{" checked" if (first and k == 0) else ""}><span>{T(a, e)}</span></label>' for k, (v, a, e) in enumerate(opts))


request = f'''<section class="sec" id="request"><div class="wrap">
  <span class="eyebrow">&gt;_ {T("اطلب جهازك", "Request a device")}</span>
  <h2 class="h2">{T("قلنا شو بدك، <b>ومنوفره لك</b>", "Tell us what you need, <b>we'll source it</b>")}</h2>
  <p class="sub">{T("ما لقيت الجهاز اللي بدك ياه؟ اختار المواصفات وبتوصلنا رسالة واتساب مرتبة، ومنرد عليك بالخيارات والأسعار.", "Can't find your device? Pick what you need and we'll get a tidy WhatsApp message, then reply with options and prices.")}</p>
  <form class="rq" id="rq" novalidate>
    <div class="rq-fields">
      <fieldset><legend>1. {T("نوع الجهاز", "Device type")}</legend><div class="pks">{picks("t", [("laptop", "لابتوب", "Laptop"), ("desktop", "كمبيوتر مكتبي", "Desktop"), ("monitor", "شاشة", "Monitor")], first=True)}</div></fieldset>
      <fieldset><legend>2. {T("الاستخدام", "What it's for")}</legend><div class="pks">{picks("u", [("study", "دراسة", "Study"), ("office", "شغل مكتبي", "Office work"), ("dev", "برمجة", "Programming"), ("design", "تصميم ومونتاج", "Design & editing"), ("gaming", "ألعاب", "Gaming")], "checkbox")}</div></fieldset>
      <fieldset><legend>3. {T("الميزانية", "Budget")}</legend><div class="pks">{picks("b", [("lt300", "أقل من 300 دينار", "Under 300 JD"), ("300-600", "من 300 لـ 600", "300 – 600 JD"), ("600-900", "من 600 لـ 900", "600 – 900 JD"), ("900-1200", "من 900 لـ 1200", "900 – 1,200 JD"), ("gt1200", "أكثر من 1200", "Over 1,200 JD")])}</div></fieldset>
      <fieldset><legend>4. {T("الحالة", "Condition")}</legend><div class="pks">{picks("c", [("any", "الاثنين (أفضل قيمة)", "Either (best value)"), ("new", "جديد بالكرتونة", "New in box"), ("used", "مستعمل بحالة ممتازة", "Used, excellent")], first=True)}</div></fieldset>
      <div class="rq-two"><label class="fld"><span>{T("الاسم (اختياري)", "Name (optional)")}</span><input id="rq-name" type="text" autocomplete="name"></label>
      <label class="fld"><span>{T("موديل أو مواصفات (اختياري)", "Model or specs (optional)")}</span><input id="rq-notes" type="text" data-ph-ar="مثلاً: رام 32GB، كرت RTX" data-ph-en="e.g. 32GB RAM, RTX GPU" placeholder="مثلاً: رام 32GB، كرت RTX"></label></div>
    </div>
    <aside class="rq-sum" aria-live="polite">
      <span class="eyebrow">{T("ملخص طلبك", "Your request")}</span>
      <h3>{T("طلب عرض سعر", "Quote request")}</h3>
      <dl id="rqsum"></dl>
      <p>{T("بنرد عليك على واتساب بالخيارات المتوفرة وأسعارها.", "We'll reply on WhatsApp with matching options and prices.")}</p>
      <a class="b-cyan wide" id="rqsend" target="_blank" rel="noopener" href="#">{WA_SVG}{T("ابعت الطلب على واتساب", "Send on WhatsApp")}</a>
    </aside>
  </form>
</div></section>'''

home = f'''<main>
{hero}
<section class="sec gray" id="portfolio"><div class="wrap">
  <span class="eyebrow">{T("الأقسام", "Sections")}</span>
  <h2 class="h2">{T("شو بتدوّر عليه؟ <b>اختار القسم</b>", "What are you after? <b>Pick a section</b>")}</h2>
  <p class="sub">{T("مواصفات حقيقية، أسعار نهائية بالدينار، وكفالة مكتوبة على كل جهاز.", "Real specs, final prices in JD, and a written warranty on every device.")}</p>
  <div class="ports">{pcards}</div>
</div></section>
<section class="sec" id="new"><div class="wrap">
  <div class="sec-head"><div><span class="eyebrow">&gt;_ {T("وصل حديثاً", "Just arrived")}</span><h2 class="h2">{T("آخر الأجهزة <b>على الموقع</b>", "The latest <b>additions</b>")}</h2></div><a class="tlink" href="laptops.html">{T("كل اللابتوبات", "All laptops")}{ARR}</a></div>
  <div class="grid">{newgrid}</div>
</div></section>
<section class="sec dark" id="services"><div class="wrap">
  <span class="eyebrow">&gt;_ {T("الصيانة والتهيئة", "Repair & setup")}</span>
  <h2 class="h2">{T("صيانة <b>بسعر واضح من البداية</b>", "Repairs with <b>upfront pricing</b>")}</h2>
  <p class="sub">{T("كل شغلة بتبلش بفحص وتكلفة واضحة، وما منشتغل إلا بعد موافقتك.", "Every job starts with a check and a clear cost, and nothing starts without your approval.")}</p>
  <div class="svcs">{services}</div>
</div></section>
<section class="sec gray" id="why"><div class="wrap">
  <span class="eyebrow">&gt;_ {T("ليش Root؟", "Why Root?")}</span>
  <h2 class="h2">{T("مبني على الوضوح: <b>مواصفات حقيقية وسعر معلن</b>", "Built on clarity: <b>real specs, upfront prices</b>")}</h2>
  <div class="whys">{why}</div>
</div></section>
{request}
<section class="sec gray" id="faq"><div class="wrap narrow">
  <span class="eyebrow">&gt;_ {T("أسئلة شائعة", "FAQ")}</span>
  <h2 class="h2">{T("أجوبة واضحة <b>قبل ما تشتري</b>", "Clear answers <b>before you buy</b>")}</h2>
  <div class="faq">{faq}</div>
  <div class="contact" id="contact">
    <span class="eyebrow">&gt;_ {T("تواصل معنا", "Contact")}</span>
    <h3>{T("تواصل مع Root", "Get in touch with Root")}</h3>
    <div class="cgrid">
      <div><small>{T("واتساب", "WhatsApp")}</small><b dir="ltr">+962 7 9916 7971</b></div>
      <div><small>{T("اتصال", "Call")}</small><b dir="ltr">+962 7 9185 1390</b></div>
      <div><small>{T("البريد الإلكتروني", "Email")}</small><b>info@rootjo.com</b></div>
      <div><small>{T("انستغرام", "Instagram")}</small><b dir="ltr">@rootcomputers</b></div>
    </div>
    <a class="b-cyan wide" target="_blank" rel="noopener" href="{wa('مرحباً Root، ')}" data-href-en="{wa('Hi Root, ')}">{WA_SVG}{T("ابدأ المحادثة على واتساب", "Start a WhatsApp chat")}</a>
  </div>
</div></section>
</main>'''
open(f"{OUT}/index.html", "w", encoding="utf-8").write(page("Root Computers · Concept", "Root redesign concept", home))

# ---------------- section pages ----------------
for s in SECT:
    cid = s[0]
    chips = "".join(f'<a class="chip" href="{x[1]}.html"{" aria-current=page" if x[0] == cid else ""}>{ico(x[0], "ci")}{T(x[2], x[3])}</a>' for x in SECT)
    if cid == "repair":
        grid = f'<div class="svcs light">{services}</div>'
        tools = ""
        count = f"{len(REPAIR)} {T(s[8], s[9])}"
    else:
        items = [p for p in P if p["category"] == cid]
        items.sort(key=lambda p: p.get("status") == "sold")
        conds = sorted({p.get("condition") for p in items})
        opts = "".join(f'<option value="{c}">{COND[c][0]}</option>' for c in conds)
        opts_en = "".join(f'<option value="{c}">{COND[c][1]}</option>' for c in conds)
        tools = f'''<div class="tools">
  <label class="sel"><span>{T("الحالة", "Condition")}</span><select id="fCond" data-opts-ar='<option value="">كل الحالات</option>{opts}' data-opts-en='<option value="">All conditions</option>{opts_en}'><option value="">كل الحالات</option>{opts}</select></label>
  <label class="sel"><span>{T("الترتيب", "Sort")}</span><select id="fSort" data-opts-ar='<option value="feat">المميّز</option><option value="new">الأحدث</option><option value="lo">السعر: من الأقل</option><option value="hi">السعر: من الأعلى</option>' data-opts-en='<option value="feat">Featured</option><option value="new">Newest</option><option value="lo">Price: low to high</option><option value="hi">Price: high to low</option>'><option value="feat">المميّز</option><option value="new">الأحدث</option><option value="lo">السعر: من الأقل</option><option value="hi">السعر: من الأعلى</option></select></label>
  <span class="shown" id="shown"></span>
</div>'''
        grid = f'<div class="grid" id="grid">{"".join(card(p) for p in items)}</div>'
        if cid == "desktop":
            grid += f'''<div class="custom"><div><h3>{T("بدك مواصفات ثانية؟", "Need different specs?")}</h3><p>{T("قلنا ميزانيتك وشو استخدامك، ونجهزلك الكمبيوتر المناسب، جاهز أو تجميع.", "Tell us your budget and use, and we'll put together the right desktop, ready-made or custom built.")}</p></div><a class="b-cyan" href="index.html#request">{T("اطلب جهازك", "Request a device")}{ARR}</a></div>'''
        count = f"{len(avail(cid))} {T(s[8], s[9])} {T('متوفر', 'in stock')}"
    body = f'''<main>
<section class="phero"><div class="wrap">
  <nav class="crumb" aria-label="breadcrumb"><a href="index.html">{T("الرئيسية", "Home")}</a><i>/</i><span>{T(s[2], s[3])}</span></nav>
  <div class="ph-row"><span class="pi big">{ico(cid)}</span><div><h1>{T(s[2], s[3])}</h1><p>{T(s[6], s[7])}</p></div><span class="cnt big">{count}</span></div>
  <nav class="chips" aria-label="sections">{chips}</nav>
</div></section>
<section class="sec tight"><div class="wrap">
  {tools}
  {grid}
  <div class="ask"><p>{T("ما لقيت اللي بدك ياه؟ قلنا شو بدك ومنوفره لك.", "Can't find what you need? Tell us and we'll source it.")}</p><a class="tlink" href="index.html#request">{T("اطلب جهازك", "Request a device")}{ARR}</a></div>
</div></section>
</main>'''
    open(f"{OUT}/{s[1]}.html", "w", encoding="utf-8").write(page(f"{s[3]} · Root concept", s[7], body, cid))
print("concept built:", sorted(os.listdir(OUT)))
