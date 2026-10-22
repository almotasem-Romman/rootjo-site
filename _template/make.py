# Root ad v2 "Studio" design: 1080x1440 (3:4, Instagram grid shows it uncropped). Inputs: data.json, laptop.png (cutout), logo.png.
# Run: python3 scene.py laptop.png && python3 make.py && node shot.js '[["sq",1080,1440]]'
import json, os
from PIL import Image
B = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(B, 'data.json'), encoding='utf-8'))
FS = 'node_modules/@fontsource'
L = D.get('layout', {})

ICON = {
 'bolt': '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 10.5v3"/><path d="M11.5 8.5l-2.5 4h4l-2.5 4"/>',
 'ai': '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M18.5 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
 'cam': '<rect x="2" y="6" width="15" height="12" rx="2.5"/><path d="M17 10.5l5-3v9l-5-3"/><circle cx="9.5" cy="12" r="2.5"/>',
 'cpu': '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx=".5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
 'ram': '<rect x="2" y="6" width="20" height="10" rx="1.5"/><path d="M6 9.5v3M10 9.5v3M14 9.5v3M18 9.5v3M5 16v3M9 16v3M15 16v3M19 16v3"/>',
 'ssd': '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7 15h10"/><circle cx="17" cy="8" r="1"/>',
 'screen': '<rect x="2" y="3" width="20" height="13" rx="2"/><path d="M8 21h8M12 16v5"/>',
 'gpu': '<rect x="2" y="6" width="17" height="12" rx="2"/><circle cx="9" cy="12" r="3"/><path d="M15 9.5v5M19 9h3M19 15h3M5 18v3M9 18v3"/>',
 'wifi': '<path d="M2 9a15 15 0 0 1 20 0M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1"/>',
 'kb': '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h.01M18 14h.01M9 14h6"/>',
 'globe': '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.8 3.9 6 3.9 9.5s-1.3 6.7-3.9 9.5c-2.6-2.8-3.9-6-3.9-9.5s1.3-6.7 3.9-9.5z"/>',
 'mail': '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M3 6.5l9 6.5 9-6.5"/>',
 'shield': '<path d="M12 2l8 3.5v6c0 5-3.4 8.6-8 10.5-4.6-1.9-8-5.5-8-10.5v-6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
 'win': '<path d="M3 5.5l7.5-1v7H3zM12 4.3L21 3v8.5h-9zM3 13h7.5v7L3 19zM12 13h9v8l-9-1.3z" fill="currentColor" stroke="none"/>',
 'office': '<path d="M14 2.5L4 6v12l10 3.5 6-2V4.5z"/><path d="M14 2.5v19M4 18l10-2V8"/>',
 'gift': '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v9h14v-9M12 8v13"/><path d="M12 8c-1.5-3-5-4-6-2s2 2 6 2c4 0 7 0 6-2s-4.5-1-6 2"/>',
 'truck': '<path d="M2 6h12v10H2zM14 9h4l3 3.5V16h-7z"/><circle cx="6" cy="17.5" r="2"/><circle cx="17" cy="17.5" r="2"/>',
 'box': '<path d="M12 2l9 4.5v11L12 22l-9-4.5v-11z"/><path d="M3 6.5l9 4.5 9-4.5M12 11v11M7.5 4.2l9 4.6"/>',
 'wa': '<path d="M3.5 20.5l1.3-4.2A8.6 8.6 0 1 1 8 19.4z"/><path d="M9 8.2c.3-.6.9-.5 1.1 0l.6 1.5c.1.3 0 .6-.2.8l-.5.5c.6 1.2 1.6 2.2 2.8 2.8l.5-.5c.2-.2.5-.3.8-.2l1.5.6c.5.2.6.8 0 1.1-1 .7-2.4.8-4.6-1-2.2-1.9-2.8-3.6-2-5.6z" fill="currentColor" stroke="none"/>',
 'phone': '<path d="M5 3h3.5l1.8 4.6-2.3 1.6a11 11 0 0 0 6.8 6.8l1.6-2.3L21 15.5V19a2 2 0 0 1-2.2 2A17 17 0 0 1 3 5.2 2 2 0 0 1 5 3z"/>',
}
def ic(n, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICON[n]}</svg>'

FONTFACE = ''.join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};src:url({FS}/{f}/files/{f}-{sub}-{w}-normal.woff2) format('woff2');{ur}}}"
    for fam, f, subs, ws in [('Poppins', 'poppins', ['latin'], [400, 500, 600, 700, 800]),
                             ('Montserrat', 'montserrat', ['latin'], [600, 700, 800, 900]),
                             ('Cairo', 'cairo', ['arabic'], [500, 600, 700, 800, 900])]
    for sub in subs
    for ur in [("unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF;" if sub == 'arabic' else '')]
    for w in ws)

# laptop + its floor shadow/reflection (from scene.py) share one coordinate system
LAP_W, LAP_X, LAP_Y = L.get('lap_w', 668), L.get('lap_x', 10), L.get('lap_y', 392)
lw, lh = Image.open(os.path.join(B, 'laptop_lit.png')).size
# fit check: the device must never clip the canvas or slide under the spec card
MARGIN, CARD_X, FLOOR_Y, EDGE_Y = 24, L.get('card_x', 684), L.get('floor', 760), L.get('edge', 1000)
room = CARD_X - 14 - max(LAP_X, MARGIN)
if LAP_W > room:
    print(f'fit: lap_w {LAP_W} -> {room} (would hit the spec card)'); LAP_Y += (LAP_W - room) * lh / lw; LAP_W = room
LAP_X = max(LAP_X, MARGIN)
bottom = LAP_Y + lh * LAP_W / lw
if not FLOOR_Y + 30 <= bottom <= EDGE_Y - 60:  # the base must rest on the stage, not float or fall off it
    LAP_Y = min(max(LAP_Y, FLOOR_Y + 30 - lh * LAP_W / lw), EDGE_Y - 60 - lh * LAP_W / lw); print(f'fit: lap_y -> {LAP_Y:.0f}')
assert LAP_Y >= 260, 'device too tall for the stage: lower lap_w in data.json layout'
s = LAP_W / lw
PAD = 220
SH = dict(x=LAP_X - PAD * s, y=LAP_Y - PAD * s, w=(lw + 2 * PAD) * s)
LAP_BOTTOM = LAP_Y + lh * s

d = D
specs = ''.join(f'<div class="sp">{ic(x["icon"])}<div><i>{x["label"]}</i><b>{x["value"]}</b></div></div>' for x in d['specs'])
extras = ''.join(f'<div class="ex"><span class="exi">{ic(e["icon"])}</span><div><b class="{"en" if e["t"].isascii() else "ar"}">{e["t"]}</b><small>{e["s"]}</small></div></div>' for e in d['extras'])
BRANDBG = d.get('brand_bg', '#E2231A')
WM = d.get('wm', '')
H = 1440
FLOOR = L.get('floor', 760)       # where the back wall meets the stage top
EDGE = L.get('edge', 1000)         # front edge of the stage (navy face starts)

HTML = f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONTFACE}
:root{{--navy:#1A2C50;--navy2:#0F1C38;--cyan:#1ABDCC;--ink:#1A2C50;--mute:#5B6B85}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:{H}px;overflow:hidden}}
body{{font-family:Poppins,Cairo,sans-serif;color:var(--ink);position:relative;background:#EDF1F6}}
.abs{{position:absolute}}
/* ---------- studio set ---------- */
.wall{{left:0;top:0;width:1080px;height:{FLOOR+40}px;
 background:radial-gradient(70% 85% at 38% 55%,#FFFFFF 0%,#F2F5F9 45%,#DFE6EF 100%)}}
.stage{{left:0;top:{FLOOR}px;width:1080px;height:{EDGE-FLOOR}px;
 background:linear-gradient(180deg,#E3E9F1 0%,#F1F4F8 38%,#F7F9FB 100%)}}
.horizon{{left:0;top:{FLOOR-60}px;width:1080px;height:120px;
 background:linear-gradient(180deg,rgba(223,230,239,0) 0%,rgba(214,222,233,.85) 50%,rgba(227,233,241,0) 100%)}}
.lip{{left:0;top:{EDGE-3}px;width:1080px;height:3px;background:linear-gradient(90deg,rgba(255,255,255,.4),#fff 30%,#fff 70%,rgba(255,255,255,.4))}}
.lip2{{left:0;top:{EDGE}px;width:1080px;height:2px;background:linear-gradient(90deg,transparent,var(--cyan) 20%,var(--cyan) 80%,transparent);box-shadow:0 0 18px 2px rgba(26,189,204,.55)}}
.face{{left:0;top:{EDGE}px;width:1080px;height:{H-EDGE}px;
 background:radial-gradient(90% 140% at 30% 0%,#22396A 0%,#1A2C50 45%,#0F1C38 100%)}}
.face:before{{content:"";position:absolute;inset:0;opacity:.07;
 background:repeating-linear-gradient(115deg,#fff 0 1px,transparent 1px 26px)}}
.wm{{left:-6px;top:150px;font:900 300px/1 Montserrat;letter-spacing:-.04em;color:transparent;
 -webkit-text-stroke:2px rgba(26,44,80,.09);white-space:nowrap}}
.glow{{border-radius:50%;filter:blur(60px)}}
.ring{{border-radius:50%;-webkit-mask-image:linear-gradient(180deg,#000 55%,transparent 88%)}}
.r1{{left:150px;top:118px;width:580px;height:580px;border:2px solid rgba(26,189,204,.40)}}
.r2{{left:205px;top:173px;width:470px;height:470px;border:1px dashed rgba(26,44,80,.16)}}
.r3{{left:95px;top:63px;width:690px;height:690px;border:1px solid rgba(26,44,80,.07)}}
.g1{{left:170px;top:230px;width:460px;height:340px;background:radial-gradient(closest-side,rgba(26,189,204,.42),rgba(26,189,204,0))}}
.g2{{left:330px;top:270px;width:360px;height:300px;background:radial-gradient(closest-side,rgba(124,92,255,.22),rgba(124,92,255,0))}}
.spill{{left:40px;top:{FLOOR+20}px;width:420px;height:110px;border-radius:50%;filter:blur(28px);
 background:radial-gradient(closest-side,rgba(130,110,255,.16),rgba(130,110,255,0))}}
.shadow{{left:{SH["x"]:.1f}px;top:{SH["y"]:.1f}px;width:{SH["w"]:.1f}px;mix-blend-mode:multiply;
 -webkit-mask-image:linear-gradient(180deg,transparent {FLOOR-40-SH["y"]:.0f}px,#000 {FLOOR+10-SH["y"]:.0f}px)}}
.refl{{left:{SH["x"]:.1f}px;top:{SH["y"]:.1f}px;width:{SH["w"]:.1f}px}}
.lap{{left:{LAP_X}px;top:{LAP_Y}px;width:{LAP_W}px}}
/* ---------- header ---------- */
.logo{{left:48px;top:40px}}.logo img{{height:78px;display:block}}
.logo .tag{{font:600 11px Poppins;letter-spacing:.34em;color:var(--navy);margin-top:6px}}
.title{{right:44px;top:44px;text-align:right}}
.brand{{display:inline-flex;align-items:center;background:{BRANDBG};color:#fff;font:700 26px Poppins;padding:8px 14px;border-radius:6px;box-shadow:0 6px 14px rgba(26,44,80,.18)}}
.model{{font:900 {L.get("model_fs",60)}px/0.98 Montserrat;letter-spacing:-.025em;color:var(--navy);margin-top:14px;white-space:nowrap}}
.model em{{font-style:normal;background:linear-gradient(90deg,#1ABDCC,#1C8FD0);-webkit-background-clip:text;color:transparent}}
.sub{{font:600 15px Poppins;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin-top:12px;display:flex;justify-content:flex-end;align-items:center;gap:10px}}
.sub:before{{content:"";width:38px;height:3px;border-radius:2px;background:var(--cyan)}}
/* ---------- spec card ---------- */
.card{{left:{L.get("card_x",684)}px;top:{L.get("card_y",300)}px;width:{1080-44-L.get("card_x",684)}px;padding:18px 18px 16px;border-radius:24px;
 background:linear-gradient(160deg,rgba(255,255,255,.88),rgba(255,255,255,.62));backdrop-filter:blur(14px);
 border:1px solid rgba(255,255,255,.9);box-shadow:0 30px 50px -22px rgba(15,28,56,.35),0 2px 0 rgba(255,255,255,.8) inset}}
.sp{{display:flex;align-items:center;gap:10px;padding:{L.get("sp_pad",11)}px 0;border-bottom:1px solid rgba(26,44,80,.08)}}
.sp:last-child{{border-bottom:0}}
.sp .ic{{flex:none;width:38px;height:38px;padding:8px;border-radius:10px;color:#fff;background:linear-gradient(145deg,#24406F,#1A2C50);stroke-width:1.7;box-shadow:0 4px 10px rgba(26,44,80,.25)}}
.sp i{{display:block;font:700 11px Poppins;letter-spacing:.16em;text-transform:uppercase;color:#13A3B0;font-style:normal;line-height:1.2}}
.sp b{{display:block;font:600 {L.get("spv",13.6)}px/1.25 Poppins;color:var(--navy);white-space:nowrap;letter-spacing:-.005em}}
/* ---------- price ---------- */
.price{{right:44px;top:{L.get("price_y",812)}px;display:flex;align-items:center;gap:16px;direction:ltr}}
.old{{font:700 27px Montserrat;color:#8A96AB;position:relative}}
.old:after{{content:"";position:absolute;left:-5%;right:-5%;top:52%;height:3px;background:#E2231A;border-radius:2px;transform:rotate(-8deg)}}
.new{{position:relative;display:flex;align-items:flex-start;gap:6px;padding:10px 26px 12px 28px;border-radius:18px;color:#fff;
 background:linear-gradient(135deg,#24406F,#1A2C50 55%,#0F1C38);box-shadow:0 22px 34px -14px rgba(15,28,56,.6),inset 0 1px 0 rgba(255,255,255,.18)}}
.new b{{font:900 74px/1 Montserrat;letter-spacing:-.03em}}
.new small{{font:800 24px/1 Montserrat;color:var(--cyan);margin-top:10px}}
.new:after{{content:"";position:absolute;left:28px;right:28px;bottom:-3px;height:4px;border-radius:3px;background:var(--cyan);box-shadow:0 0 14px rgba(26,189,204,.8)}}
/* ---------- navy face: extras + footer ---------- */
.extras{{left:40px;right:40px;top:{EDGE+40}px;display:grid;grid-template-columns:repeat(4,1fr);direction:rtl;font-family:Cairo,Poppins}}
.ex{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:12px;padding:0 10px;border-left:1px solid rgba(255,255,255,.12)}}
.ex:last-child{{border-left:0}}
.exi{{flex:none;width:66px;height:66px;border-radius:50%;display:grid;place-items:center;color:var(--cyan);
 background:radial-gradient(circle at 30% 30%,rgba(26,189,204,.28),rgba(26,189,204,.08));border:1px solid rgba(26,189,204,.45)}}
.exi svg{{width:32px;height:32px}}
.ex b{{display:block;color:#fff;white-space:nowrap;line-height:1.2}}
.ex b.en{{font:700 20px Poppins;direction:ltr;text-align:center}}
.ex b.ar{{font:800 21px Cairo}}
.ex small{{display:block;font:600 15px Cairo;color:#AFC0DA;white-space:nowrap;line-height:1.4;margin-top:2px}}
.foot{{left:40px;right:40px;top:{EDGE+228}px;height:{H-EDGE-228-52}px;display:flex;gap:16px;direction:rtl;font-family:Cairo,Poppins}}
.rib{{flex:none;display:flex;align-items:center;gap:16px;padding:0 30px;border-radius:18px;color:var(--navy);
 background:linear-gradient(135deg,#3FD6E3,#1ABDCC 60%,#139FAD);box-shadow:0 12px 24px -10px rgba(26,189,204,.7)}}
.rib svg{{width:56px;height:56px}}
.rib b{{display:block;font:900 32px/1.15 Cairo}}.rib small{{display:block;font:700 20px/1.35 Cairo}}
.contact{{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;align-items:center;padding:0 22px;column-gap:14px;border-radius:16px;
 background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.16)}}
.ci{{display:flex;align-items:center;gap:12px;color:#fff}}
.ci svg{{flex:none;width:34px;height:34px;color:var(--cyan)}}
.ci small{{display:block;font:700 14px/1 Cairo;color:#AFC0DA;margin-bottom:4px}}
.ci b{{display:block;font:700 26px/1 Poppins;letter-spacing:.02em;direction:ltr}}
.contact .ci:nth-child(-n+2){{border-bottom:1px solid rgba(255,255,255,.12);height:100%}}
.contact .ci:nth-child(n+3){{height:100%}}
.ci b.sm{{font-size:22px;letter-spacing:0}}
</style></head><body>
<div class="abs wall"></div><div class="abs stage"></div><div class="abs horizon"></div>
<div class="abs wm">{WM}</div><div class="abs halo" style="left:{LAP_X-14}px;top:{LAP_Y-284}px"><div class="abs ring r3"></div><div class="abs ring r1"></div><div class="abs ring r2"></div><div class="abs glow g1"></div><div class="abs glow g2"></div></div>
<div class="abs spill"></div>
<img class="abs refl" src="refl.png"><img class="abs shadow" src="shadow.png"><img class="abs lap" src="laptop_lit.png">
<div class="abs lip"></div><div class="abs face"></div><div class="abs lip2"></div>
<div class="abs logo"><img src="logo.png"><div class="tag">YOUR TECH PARTNER</div></div>
<div class="abs title"><div class="brand">{d["brand"]}</div><div class="model">{d["model"]}</div><div class="sub">{d["sub"]}</div></div>
<div class="abs card">{specs}</div>
<div class="abs price"><span class="old">{d["old"]} JD</span><div class="new"><b>{d["price"]}</b><small>JD</small></div></div>
<div class="abs extras">{extras}</div>
<div class="abs foot"><div class="rib">{ic("box")}<div><b>{d["rib_t"]}</b><small>{d["rib_s"]}</small></div></div>
<div class="contact"><div class="ci">{ic("wa")}<div><small>واتساب فقط</small><b>{d["wa"]}</b></div></div>
<div class="ci">{ic("phone")}<div><small>للاتصال</small><b>{d["tel"]}</b></div></div>
<div class="ci">{ic("globe")}<div><small>الموقع الإلكتروني</small><b class="sm">{d.get("web","www.rootjo.com")}</b></div></div>
<div class="ci">{ic("mail")}<div><small>البريد الإلكتروني</small><b class="sm">{d.get("mail","info@rootjo.com")}</b></div></div></div></div>
</body></html>'''
open(os.path.join(B, 'sq.html'), 'w', encoding='utf-8').write(HTML)
print('laptop bottom y =', round(LAP_BOTTOM))
