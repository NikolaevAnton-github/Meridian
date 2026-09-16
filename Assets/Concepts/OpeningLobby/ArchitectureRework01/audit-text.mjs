// Measure rendered SVG text with the installed browser. Reports overlap candidates for human review.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../../..');
const worker=path.join(root,'Saved/OpeningLobby/ArchitectureRework01/Worker');
if(fs.existsSync(path.join(dir,'manifest.json')))throw Error('Frozen evidence: use freeze.mjs --verify; do not overwrite the submitted audit.');
const sheets=JSON.parse(fs.readFileSync(path.join(worker,'sheets.json'),'utf8'));
const refs=sheets.map(s=>({name:s.name,url:new URL('file:///'+path.join(dir,s.name+'.svg').replaceAll('\\','/')).href}));
const html=path.join(worker,'text-audit.html');
const js=`
 const jobs=${JSON.stringify(refs)};
 const reports=[];
 async function run(job){
  return await new Promise(resolve=>{
   const iframe=document.createElement('iframe');iframe.width=1600;iframe.height=1200;iframe.style.border='0';
   iframe.onload=()=>{
    const doc=iframe.contentDocument;
    const boxes=[...doc.querySelectorAll('text')].map(el=>{
     const b=el.getBBox(),m=el.getCTM();
     const pts=[[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
     return {text:el.textContent,x:Math.min(...pts.map(p=>p.x)),y:Math.min(...pts.map(p=>p.y)),right:Math.max(...pts.map(p=>p.x)),bottom:Math.max(...pts.map(p=>p.y))};
    });
    const outside=boxes.filter(b=>b.x<10||b.y<10||b.right>1590||b.bottom>1190);
    const overlaps=[];
    for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
     const a=boxes[i],b=boxes[j],w=Math.min(a.right,b.right)-Math.max(a.x,b.x),h=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);
     if(w>2&&h>2)overlaps.push({a:a.text,b:b.text,intersection:[w,h]});
    }
    reports.push({sheet:job.name,text_count:boxes.length,outside,overlaps});iframe.remove();resolve();
   };
   iframe.src=job.url;document.body.appendChild(iframe);
  });
 }
 (async()=>{for(const job of jobs)await run(job);const p=document.createElement('pre');p.id='audit-result';p.textContent=JSON.stringify(reports);document.body.appendChild(p);})();
`;
fs.writeFileSync(html,`<!doctype html><html><head><meta charset="utf-8"></head><body><script>${js}</script></body></html>`);
const chrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
const r=spawnSync(chrome,['--headless=new','--disable-gpu','--no-first-run','--disable-background-networking','--disable-extensions','--disable-sync','--disable-component-update','--allow-file-access-from-files',`--user-data-dir=${path.join(worker,'BrowserProfile')}`,'--virtual-time-budget=5000','--dump-dom',new URL('file:///'+html.replaceAll('\\','/')).href],{encoding:'utf8',timeout:45000,windowsHide:true,maxBuffer:5*1024*1024});
fs.writeFileSync(path.join(worker,'text-audit-render.log'),`${r.stderr}\nExit ${r.status}`);
const match=r.stdout?.match(/<pre id="audit-result">([\s\S]*?)<\/pre>/);
if(r.status!==0||!match)throw Error('Browser did not return text audit');
const report=JSON.parse(match[1].replaceAll('&amp;','&').replaceAll('&lt;','<').replaceAll('&gt;','>'));
fs.writeFileSync(path.join(worker,'text-audit.json'),JSON.stringify({scope:'Browser-measured text boxes only; diagrams/images require actual visual inspection.',sheets:report},null,2)+'\n');
for(const s of report)console.log(`${s.sheet}: ${s.text_count} text elements, ${s.outside.length} outside, ${s.overlaps.length} overlap candidates`);
