// Adapted from ArchitectureRework01's bounded geometry/source checks.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(dir,'../../../..'),worker=path.join(root,'Saved/OpeningLobby/FunctionalRevision01/Worker');
const frozen=fs.existsSync(path.join(dir,'manifest.json'));
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const D=JSON.parse(fs.readFileSync(path.join(dir,'design.json'),'utf8')),objects=JSON.parse(fs.readFileSync(path.join(worker,'drawing-bounds.json'),'utf8')).objects;
const S=D.shared,Q=D.checkpoint,R=D.rooms,E=D.elevator,eq=(a,b)=>Math.abs(a-b)<1e-6,checks=[];
function check(name,pass,detail=''){checks.push({name,pass:!!pass,detail});}
const accepted=read('Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json').architecture.candidate;
for(const k of ['length','width','height'])check('Accepted hall '+k,eq(S.hall[k],accepted[k]));
check('Six free pier pairs retained',JSON.stringify(S.piers.x)===JSON.stringify(accepted.pier_x)&&eq(S.piers.size,accepted.pier_size)&&eq(S.piers.abs_y,accepted.pier_y)&&eq(S.piers.height,accepted.shaft_height));
check('Width partition',eq(S.circulation.central_clear+2*S.piers.size+2*S.circulation.aisle_clear,S.hall.width));
const A=read('Assets/Concepts/OpeningLobby/ArchitectureRework01/design.json').variants.A;
check('Selected A retained exactly',JSON.stringify(D.retained_A)===JSON.stringify(A));
check('Positive drawing bounds',objects.every(o=>o.b[1]>o.b[0]&&o.b[3]>o.b[2]&&o.b[5]>o.b[4]));
check('Bounds within hall except explicit elevator leaf backing',objects.every(o=>o.b[0]>=-30&&o.b[1]<=30+(o.id.startsWith('elevator-closed-leaf')?E.leaf_thickness:0)&&o.b[2]>=-12&&o.b[3]<=12&&o.b[4]>=0&&o.b[5]<=18));
check('Four doors; inverse face normals',R.doors.length===4&&new Set(R.doors.map(d=>d.id)).size===4&&R.doors.every(d=>d.normal_y===(d.end==='entrance'?d.sign:-d.sign)));
for(const d of R.doors){
 const rows=objects.filter(o=>o.id.startsWith(d.id+'-')),leaf=rows.find(o=>o.id.endsWith('closed-leaf')),blind=rows.find(o=>o.id.endsWith('blind'));
 const [x0,x1]=R[d.end+'_x'],faceY=d.face==='aisle'?d.sign*8:d.sign*5.6,visible=leaf.b[d.normal_y>0?3:2];
 check(d.id+' correctly recessed closed face',eq(Math.abs(visible-faceY),R.door_recess)&&eq(leaf.b[1]-leaf.b[0],R.door_width)&&eq(leaf.b[5],R.door_height));
 check(d.id+' blind opposite wall and beam joint',eq(blind.b[0],x0)&&eq(blind.b[1],x1)&&eq(blind.b[5],S.beam.z_min)&&eq(R.z[1],S.beam.z_min));
 check(d.id+' within colonnade band',rows.every(o=>o.b[2]>=Math.min(d.sign*5.6,d.sign*8)-1e-6&&o.b[3]<=Math.max(d.sign*5.6,d.sign*8)+1e-6));
}
check('Terminal X joints explicit',eq(R.entrance_x[0],A.end_pier.front_x)&&eq(R.entrance_x[1],S.piers.x[0]-S.piers.size/2)&&eq(R.inner_x[0],S.piers.x.at(-1)+S.piers.size/2)&&eq(R.inner_x[1],29.97));
check('Exactly two symmetric lane centres',Q.lane_centres_y.length===2&&eq(Q.lane_centres_y[0],-Q.lane_centres_y[1]));
check('Checkpoint wall contact, no end gap',eq(Math.abs(Q.lane_centres_y[0])+Q.net_width/2+Q.post_width,Q.half_width)&&eq(Q.half_width,R.abs_y[0]));
check('Checkpoint joins desk to lane posts',eq(Q.desk_y[1],Q.lane_centres_y[1]-Q.net_width/2-Q.post_width)&&eq(Q.desk_y[0],Q.lane_centres_y[0]+Q.net_width/2+Q.post_width));
check('Checkpoint width arithmetic',eq(2*Q.net_width+4*Q.post_width+Q.desk_y[1]-Q.desk_y[0],S.circulation.central_clear));
check('Checkpoint remains inside terminal enclosure run',Q.x-Q.depth/2>R.entrance_x[0]&&Q.x+Q.depth/2<R.entrance_x[1]);
check('Capsule and human retained',eq(D.routes.capsule_radius,.34)&&eq(S.circulation.capsule_half_height,.88)&&eq(S.human.height,1.8)&&eq(S.human.eye_height,1.72)&&eq(D.routes.speed,3.6));
check('Checkpoint nominal centred capsule width margin',eq(Q.net_width/2-D.routes.capsule_radius,.41));
check('Checkpoint vertical clearance',Q.net_height>2*S.circulation.capsule_half_height);
check('Elevator frame and opening close',eq(E.opening_width+2*E.frame_width,E.outer_width)&&eq(E.opening_height+E.frame_width,E.outer_height)&&eq(E.leaf_x-E.front_x,.6));
check('Large elevator exceeds replaced door in both dimensions',E.opening_width>S.inner.door_width*3&&E.opening_height>S.inner.door_height*1.8);
check('High window entirely superseded by opaque field',E.remove_window.all_glass_mullions_transoms&&E.sign_zone.z[0]>=0&&E.sign_zone.z[1]<=18&&!objects.some(o=>/inner.*(glass|mullion|window)/i.test(o.id)));
const floor=objects.filter(o=>o.b[4]<2*S.circulation.capsule_half_height&&o.b[5]>0);
const distance=(p,o)=>{const b=o.b,dx=Math.max(b[0]-p[0],p[0]-b[1],0),dy=Math.max(b[2]-p[1],p[1]-b[3],0);return Math.hypot(dx,dy);};
const routes=[];
for(const route of D.routes.polylines){let minimum=Infinity,samples=0,length=0,maxStep=0,nearest='';
 for(let i=1;i<route.points.length;i++){const a=route.points[i-1],b=route.points[i],len=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.ceil(len/.025);length+=len;maxStep=Math.max(maxStep,len/n);
  for(let j=0;j<=n;j++){const t=j/n,p=a.map((v,k)=>v+(b[k]-v)*t);samples++;for(const o of floor){const d=distance(p,o);if(d<minimum){minimum=d;nearest=o.id;}}}
 }
 const conservativeMargin=minimum-D.routes.capsule_radius-maxStep/2;
 routes.push({id:route.id,samples,length,seconds:length/D.routes.speed,min_centre_to_obstruction:minimum,nominal_capsule_margin:minimum-D.routes.capsule_radius,conservative_margin:conservativeMargin,nearest});
 check('Route clear: '+route.id,conservativeMargin>0,`Conservative margin ${conservativeMargin.toFixed(3)} m; distance ${length.toFixed(3)} m`);
}
for(const x of D.routes.closed_crossovers_x)check(`Old crossing X${x} intentionally blocked`,floor.some(o=>distance([x,5.7],o)===0)&&floor.some(o=>distance([x,-5.7],o)===0));
const manifests=['Saved/OpeningLobby/ArchitectureReworkA01/Worker/manifest.json','Assets/Concepts/OpeningLobby/ArchitectureRework01/manifest.json'];
for(const file of manifests){const m=read(file);for(const row of m.entries)check('Historical candidate preserved: '+row.path,hash(row.path)===row.sha256&&fs.statSync(path.join(root,row.path)).size===row.bytes);}
check('Baseline manifest exact identity',hash(manifests[0])===D.baseline.manifest_sha256);
check('Baseline map exact identity',hash('Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap')===D.baseline.map_sha256);
for(const r of read('Assets/Concepts/OpeningLobby/OwnerReferences01/references.json').files)check('Original owner art preserved: '+r.file,hash('Assets/Concepts/OpeningLobby/OwnerReferences01/'+r.file)===r.sha256);
const textAudit=JSON.parse(fs.readFileSync(path.join(worker,'text-audit.json'),'utf8'));
check('Five browser-measured sheets without text clipping/overlap',textAudit.sheets.length===5&&textAudit.sheets.every(s=>s.outside.length===0&&s.overlaps.length===0));
for(const sh of JSON.parse(fs.readFileSync(path.join(worker,'sheets.json'),'utf8'))){const png=fs.readFileSync(path.join(dir,sh.name+'.png'));check('PNG dimensions '+sh.name,png.readUInt32BE(16)===1600&&png.readUInt32BE(20)===1200);}
const sources=['Docs/Tasks/OpeningLobbyFunctionalRevision01.md','Docs/Design/GameBrief.md','Docs/VisualAcceptance.md','Docs/OpeningLobbyArchitectureReworkA01Review.md','Docs/Approvals/LobbyArchitectureReworkA01-Walkthrough01.json','.agents/skills/environment-reference-analysis/SKILL.md','Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png','Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png','Assets/Concepts/OpeningLobby/ArchitectureRework01/design.json','Assets/Concepts/OpeningLobby/ArchitectureRework01/generate.mjs','Assets/Concepts/OpeningLobby/ArchitectureRework01/audit-text.mjs','Assets/Concepts/OpeningLobby/ArchitectureRework01/freeze.mjs',...['03-A-plan-elevation','04-A-sections','05-A-spatial'].map(n=>'Assets/Concepts/OpeningLobby/ArchitectureRework01/'+n+'.png'),...['C1-90','C2-75','C3-context-90'].map(n=>'Saved/OpeningLobby/ArchitectureReworkA01/Worker/'+n+'.png')];
const report={candidate:D.package+'/'+D.revision,scope:'2D arithmetic, conservative sampled plan-route clearance and preserved source bytes. No engine collision, engineering, independent visual or owner acceptance.',checks,routes};
if(!frozen){fs.writeFileSync(path.join(worker,'verification.json'),JSON.stringify(report,null,2)+'\n');fs.writeFileSync(path.join(dir,'input-provenance.json'),JSON.stringify({inputs:sources.map(file=>({file,bytes:fs.statSync(path.join(root,file)).size,sha256:hash(file)}))},null,2)+'\n');}
console.log(JSON.stringify({checks:checks.length,passed:checks.filter(c=>c.pass).length,failed:checks.filter(c=>!c.pass),routes:routes.length,samples:routes.reduce((n,r)=>n+r.samples,0)},null,2));
if(checks.some(c=>!c.pass))process.exitCode=1;
