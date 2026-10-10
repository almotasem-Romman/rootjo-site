const { chromium } = await import(process.env.PW_PATH || '/opt/npm-tools/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, mode, outDir, ...times] = process.argv;
const browser = await chromium.launch({ args:['--allow-file-access-from-files','--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
const errs=[]; page.on('pageerror',e=>errs.push(String(e))); page.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await page.goto('file://'+process.cwd()+'/scene.html');
await page.evaluate(()=>window.ready);
fs.mkdirSync(outDir,{recursive:true});
const list = mode==='preview' ? times.map(Number) : Array.from({length:600},(_,i)=>i/30);
let k=0;
for(const t of list){
  await page.evaluate(t=>window.render(t), t);
  await page.screenshot({ path:`${outDir}/f${String(k).padStart(4,'0')}.jpg`, type:'jpeg', quality:94 });
  k++;
}
if(errs.length) console.log('ERRORS', errs.slice(0,5));
await browser.close(); console.log('done',k);
