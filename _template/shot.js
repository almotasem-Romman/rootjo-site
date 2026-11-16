const {chromium}=require('playwright-core');
const fs=require('fs'),path=require('path');
// Chromium: $CHROME, else the newest pre-installed /opt/pw-browsers build, else Playwright's own.
function chrome(){ if(process.env.CHROME) return process.env.CHROME;
  const root='/opt/pw-browsers'; if(!fs.existsSync(root)) return undefined;
  for (const d of fs.readdirSync(root).filter(n=>n.startsWith('chromium-')).sort().reverse())
    for (const sub of ['chrome-linux64','chrome-linux']){const p=path.join(root,d,sub,'chrome'); if(fs.existsSync(p)) return p;}
  return undefined; }
(async()=>{const b=await chromium.launch({executablePath:chrome()});
for (const [f,w,h] of JSON.parse(process.argv[2])){const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('file://'+__dirname+'/'+f+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
const ok=await p.evaluate(()=>document.fonts.check('700 40px Poppins')&&document.fonts.check('700 40px Cairo'));
if(!ok){console.error('fonts did not load (Poppins/Cairo): not saving '+f);process.exitCode=1;await p.close();continue;}
await p.screenshot({path:__dirname+'/out/'+f+'.png'});await p.close();}
await b.close();})();
