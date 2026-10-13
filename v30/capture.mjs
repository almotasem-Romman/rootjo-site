// Capture real rootjo.com screens (mobile, dark) for the 30s promo.
const { chromium } = await import('/opt/npm-tools/node_modules/playwright/index.mjs');
import fs from 'fs';
const SITE = 'file:///home/claude/rootjo-src/out/index.html';
const OUT = '/home/claude/promo30/assets/site/';
fs.mkdirSync(OUT, { recursive: true });
const fontCss = fs.readFileSync('/home/claude/promo30/fonts.css', 'utf8');
const b = await chromium.launch();
const W = 390, H = 741;

async function page(lang) {
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2, colorScheme: 'dark', reducedMotion: 'reduce' });
  await ctx.route('https://fonts.googleapis.com/**', r => r.fulfill({ status: 200, contentType: 'text/css', body: fontCss }));
  await ctx.route('https://fonts.gstatic.com/**', r => r.abort());
  await ctx.route('https://www.googletagmanager.com/**', r => r.abort());
  const p = await ctx.newPage();
  await p.goto(SITE + (lang === 'en' ? '#en' : '#ar'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.addStyleTag({ content: 'html{scroll-behavior:auto!important}.rv{transform:none!important;transition:none!important}.scrollhint{display:none!important}' });
  await p.waitForTimeout(700);
  return p;
}
async function el(p, sel, name) {
  const h = await p.$(sel);
  await h.screenshot({ path: OUT + name + '.png' });
}

// AR
let p = await page('ar');
await p.screenshot({ path: OUT + 'hero_ar.png' });
await el(p, 'header.top', 'header_ar');
// header must not be sticky in element shots
await p.addStyleTag({ content: 'header.top{position:relative!important}' });
await p.evaluate(() => { const s = document.getElementById('products'); s.style.paddingBottom = '0'; });
// products top = heading + sub + category tiles
await p.evaluate(() => {
  const s = document.getElementById('products').querySelector('.wrap');
  const w = document.createElement('div'); w.id = 'ptop';
  const kids = [...s.children].slice(0, 3); s.insertBefore(w, kids[0]); kids.forEach(k => w.appendChild(k));
  w.style.paddingTop = '40px'; w.style.paddingBottom = '10px';
});
await el(p, '#ptop', 'cats_ar');
await el(p, '#cat-monitor', 'monitors_ar');
await el(p, '#about', 'why_ar');
await p.click('#faq .qa summary');
await el(p, '#faq', 'faq_ar');
// request form states
await el(p, '#request', 'req0');
await p.click('label.pick:has(input[value="code"])'); await el(p, '#request', 'req1');
await p.click('label.pick:has(input[value="500-800"])'); await el(p, '#request', 'req2');
await p.click('label.pick:has(input[value="new"])'); await el(p, '#request', 'req3');
// tap targets (centres, in element css px) for the scene
const taps = await p.evaluate(() => {
  const r = document.getElementById('request').getBoundingClientRect();
  return ['code', '500-800', 'new'].map(v => {
    const e = document.querySelector(`label.pick:has(input[value="${v}"]) span`).getBoundingClientRect();
    return [Math.round(e.left - r.left + e.width / 2), Math.round(e.top - r.top + e.height / 2)];
  });
});
const msg = await p.$eval('#rqSend', a => decodeURIComponent(a.href.split('text=')[1]));
// EN
const pe = await page('en');
await pe.screenshot({ path: OUT + 'hero_en.png' });
const langBtn = await p.evaluate(() => { window.scrollTo(0, 0); const r = document.getElementById('langBtn').getBoundingClientRect(); return [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)]; });
fs.writeFileSync(OUT + 'meta.json', JSON.stringify({ taps, msg, langBtn }, null, 1));
console.log({ taps, msg, langBtn });
await b.close();
