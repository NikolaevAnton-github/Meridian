// Adapted from ArchitectureRework01/freeze.mjs; never overwrite a frozen identity.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(dir,'../../../..');
const worker=path.join(root,'Saved/OpeningLobby/FunctionalRevision02/Worker');
const manifest=path.join(dir,'manifest.json'),sidecar=path.join(dir,'manifest.sha256');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const walk=p=>fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(p,e.name)):[path.join(p,e.name)]);
const resolve=p=>{const q=path.resolve(root,p);if(!q.startsWith(root+path.sep))throw Error('Path outside project');return q;};
const excluded=p=>['manifest.json','manifest.sha256','freeze-verification.json'].includes(path.basename(p))||p.includes(path.sep+'BrowserProfile'+path.sep)||p.endsWith('.html')||p.endsWith('.log');
if(process.argv.includes('--verify')){
 const m=JSON.parse(fs.readFileSync(manifest,'utf8'));
 if(fs.readFileSync(sidecar,'utf8').split(/\s+/)[0]!==hash(manifest))throw Error('Manifest digest mismatch');
 for(const e of m.entries){const p=resolve(e.path);if(hash(p)!==e.sha256||fs.statSync(p).size!==e.bytes)throw Error('Changed candidate: '+e.path);}
 const actual=[...walk(dir),...walk(worker)].filter(p=>!excluded(p)).map(rel).sort();
 if(JSON.stringify(actual)!==JSON.stringify(m.entries.map(e=>e.path).sort()))throw Error('Unlisted or missing candidate file');
 const input=JSON.parse(fs.readFileSync(path.join(dir,'input-provenance.json'),'utf8'));
 for(const e of input.inputs)if(hash(resolve(e.file))!==e.sha256)throw Error('Source changed: '+e.file);
 const bytes=[...walk(dir),...walk(worker)].reduce((n,p)=>n+fs.statSync(p).size,0);
 if(bytes>=40_000_000)throw Error('40 MB output ceiling exceeded');
 console.log(JSON.stringify({verified:true,candidate:m.candidate_id,status:m.status,entries:m.entries.length,manifest_sha256:hash(manifest),total_output_bytes:bytes},null,2));
}else{
 if(fs.existsSync(manifest)||fs.existsSync(sidecar))throw Error('Candidate already frozen');
 const D=JSON.parse(fs.readFileSync(path.join(dir,'design.json'),'utf8'));
 const verification=JSON.parse(fs.readFileSync(path.join(worker,'verification.json'),'utf8'));
 const audit=JSON.parse(fs.readFileSync(path.join(worker,'text-audit.json'),'utf8'));
 if(D.status!=='pending_independent_review'||verification.checks.some(c=>!c.pass)||audit.sheets.length!==5||audit.sheets.some(s=>s.outside.length||s.overlaps.length))throw Error('Incomplete author verification');
 for(const n of ['handoff.md','visual-inspection.md'])if(!fs.existsSync(path.join(worker,n)))throw Error('Missing '+n);
 const files=[...walk(dir),...walk(worker)].filter(p=>!excluded(p)).sort((a,b)=>rel(a).localeCompare(rel(b)));
 const entries=files.map(p=>({path:rel(p),bytes:fs.statSync(p).size,sha256:hash(p)}));
 if([...walk(dir),...walk(worker)].reduce((n,p)=>n+fs.statSync(p).size,0)>39_900_000)throw Error('Output too large');
 const m={schema:1,candidate_id:D.package+'/'+D.revision,status:D.status,base:'project root',scope:'Immutable 2D proposal only. Pending independent review and named-package owner approval; no 3D authorization.',manifest_exclusions:['manifest.json and manifest.sha256 (self-reference)','Worker transient browser profile, HTML wrappers and render logs','Worker freeze-verification.json (post-freeze read-only verification receipt)'],entries};
 fs.writeFileSync(manifest,JSON.stringify(m,null,2)+'\n');fs.writeFileSync(sidecar,hash(manifest)+'  manifest.json\n');
 console.log(JSON.stringify({candidate:m.candidate_id,entries:entries.length,manifest_sha256:hash(manifest),submission_bytes:entries.reduce((n,e)=>n+e.bytes,0)},null,2));
}
