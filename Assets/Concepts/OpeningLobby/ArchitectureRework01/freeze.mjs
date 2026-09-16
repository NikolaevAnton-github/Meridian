// Local immutable-candidate manifest, or read-only verification of its exact bytes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../../..');
const worker=path.join(root,'Saved/OpeningLobby/ArchitectureRework01/Worker');
const manifest=path.join(dir,'manifest.json');
const sidecar=path.join(dir,'manifest.sha256');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel=p=>path.relative(root,p).replaceAll('\\','/');
function walk(p){return fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(p,e.name)):[path.join(p,e.name)]);}
function inRoot(p){const r=path.resolve(root,p);if(!r.startsWith(root+path.sep))throw Error('Manifest path escapes project');return r;}
if(process.argv.includes('--verify')){
 const m=JSON.parse(fs.readFileSync(manifest,'utf8'));
 const digest=hash(manifest);
 if(fs.readFileSync(sidecar,'utf8').split(/\s+/)[0]!==digest)throw Error('Manifest sidecar mismatch');
 for(const e of m.entries){const p=inRoot(e.path);if(fs.statSync(p).size!==e.bytes||hash(p)!==e.sha256)throw Error(`Candidate changed: ${e.path}`);}
 const input=JSON.parse(fs.readFileSync(path.join(dir,'input-provenance.json'),'utf8'));
 for(const e of input.inputs){const p=inRoot(e.file);if(hash(p)!==e.sha256)throw Error(`Source changed: ${e.file}`);}
 const bytes=[...walk(dir),...walk(worker)].reduce((s,p)=>s+fs.statSync(p).size,0);
 if(bytes>80*1000*1000)throw Error(`80 MB limit exceeded: ${bytes}`);
 console.log(JSON.stringify({verified:true,package:m.package,revision:m.revision,status:m.status,entries:m.entries.length,manifest_sha256:digest,total_package_and_worker_bytes:bytes},null,2));
}else{
 if(fs.existsSync(manifest)||fs.existsSync(sidecar))throw Error('Candidate already frozen; use --verify.');
 const D=JSON.parse(fs.readFileSync(path.join(dir,'design.json'),'utf8'));
 if(!['pending_independent_review','pending_owner_approval'].includes(D.status))throw Error('Unsupported candidate status');
 const verification=JSON.parse(fs.readFileSync(path.join(worker,'verification.json'),'utf8'));
 if(!verification.checks.every(c=>c.pass))throw Error('Drawing checks failed');
 const audit=JSON.parse(fs.readFileSync(path.join(worker,'text-audit.json'),'utf8'));
 if(audit.sheets.length!==8||audit.sheets.some(s=>s.outside.length||s.overlaps.length))throw Error('Text audit unresolved');
 for(const name of ['visual-inspection.md','handoff.md'])if(!fs.existsSync(path.join(worker,name)))throw Error(`Missing ${name}`);
 const evidence=['inputs-before.json','verification.json','sheets.json','text-audit.json','visual-inspection.md','handoff.md'];
 const packageFiles=walk(dir).filter(p=>!['manifest.json','manifest.sha256'].includes(path.basename(p)));
 const files=[...packageFiles,...evidence.map(n=>path.join(worker,n))].sort((a,b)=>rel(a).localeCompare(rel(b)));
 const entries=files.map(p=>({path:rel(p),bytes:fs.statSync(p).size,sha256:hash(p)}));
 const allBytes=[...walk(dir),...walk(worker)].reduce((s,p)=>s+fs.statSync(p).size,0);
 if(allBytes>79*1000*1000)throw Error('Insufficient room below the 80 MB package/evidence ceiling');
 const m={schema:1,package:D.package,revision:D.revision,candidate_id:D.package+'/'+D.revision,status:D.status,units:'metres',base:'project root',scope:'Immutable 2D candidate; pending fresh independent review and owner selection. No 3D authorization.',manifest_exclusions:['manifest.json','manifest.sha256','Worker browser cache, temporary HTML, logs and text-coordinate scratch data'],entries};
 fs.writeFileSync(manifest,JSON.stringify(m,null,2)+'\n');
 fs.writeFileSync(sidecar,`${hash(manifest)}  manifest.json\n`);
 console.log(JSON.stringify({package:D.package,entries:entries.length,manifest_sha256:hash(manifest),submission_bytes:entries.reduce((s,e)=>s+e.bytes,0),total_before_manifest_bytes:allBytes},null,2));
}
