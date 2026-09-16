// Adapted from ArchitectureRework01's bounded geometry/source checks.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(dir,'../../../..'),worker=path.join(root,'Saved/OpeningLobby/FunctionalRevision02/Worker');
const frozen=fs.existsSync(path.join(dir,'manifest.json'));
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const D=JSON.parse(fs.readFileSync(path.join(dir,'design.json'),'utf8')),objects=JSON.parse(fs.readFileSync(path.join(worker,'drawing-bounds.json'),'utf8')).objects;
const S=D.shared,Q=D.checkpoint,R=D.rooms,E=D.elevator,eq=(a,b)=>Math.abs(a-b)<1e-6,checks=[];
function check(name,pass,detail=''){checks.push({name,pass:!!pass,detail});}
const accepted=read('Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json').architecture.candidate;
for(const k of ['length','width','height'])check('Accepted hall '+k,eq(S.hall[k],accepted[k]));
check('Twelve original pier positions and dimensions retained',JSON.stringify(S.piers.x)===JSON.stringify(accepted.pier_x)&&eq(S.piers.size,accepted.pier_size)&&eq(S.piers.abs_y,accepted.pier_y)&&eq(S.piers.height,accepted.shaft_height));
check('Width partition',eq(S.circulation.central_clear+2*S.piers.size+2*S.circulation.aisle_clear,S.hall.width));
const A=read('Assets/Concepts/OpeningLobby/ArchitectureRework01/design.json').variants.A;
check('Selected A retained exactly',JSON.stringify(D.retained_A)===JSON.stringify(A));
check('Positive drawing bounds',objects.every(o=>o.b[1]>o.b[0]&&o.b[3]>o.b[2]&&o.b[5]>o.b[4]));
check('Bounds within hall except explicit elevator leaf backing',objects.every(o=>o.b[0]>=-30&&o.b[1]<=30+(o.id.startsWith('elevator-closed-leaf')?E.leaf_thickness:0)&&o.b[2]>=-12&&o.b[3]<=12&&o.b[4]>=0&&o.b[5]<=18));
check('Four corrected door normals',R.doors.length===4&&R.doors.every(d=>JSON.stringify(d.normal)===JSON.stringify(d.end==='entrance'?[1,0]:[0,-d.sign])));
for(const d of R.doors){
 const rows=objects.filter(o=>o.id.startsWith(d.id+'-')),leaf=rows.find(o=>o.id.endsWith('closed-leaf'));
 const face=d.end==='entrance'?leaf.b[1]:leaf.b[d.sign>0?2:3],expected=d.end==='entrance'?-20.04:d.sign*5.84;
 const width=d.end==='entrance'?leaf.b[3]-leaf.b[2]:leaf.b[1]-leaf.b[0];
 check(d.id+' closed door position / width / height / recess',eq(face,expected)&&eq(width,R.door_width)&&eq(leaf.b[5],R.door_height));
 check(d.id+' gross extent 10.2 by 6.4 to outer wall',eq(R[d.end+'_x'][1]-R[d.end+'_x'][0],10.2)&&eq(R.abs_y[0],5.6)&&eq(R.abs_y[1],12));
 const band=rows.find(o=>o.id.endsWith('roof-band')),aisle=rows.find(o=>o.id.endsWith('roof-aisle'));
 check(d.id+' stepped closure touches beam and soffit',eq(band.b[5],S.beam.z_min)&&eq(aisle.b[5],S.aisle_ceiling_z)&&eq(aisle.b[4],8.84)&&eq(Math.min(Math.abs(aisle.b[2]),Math.abs(aisle.b[3])),S.beam.abs_y_max));
 check(d.id+' no obsolete internal wall at Y8',!rows.some(o=>o.b[4]===0&&eq(Math.min(Math.abs(o.b[2]),Math.abs(o.b[3])),7.64)));
 check(d.id+' opposite access face blind',rows.some(o=>o.id===d.id+(d.end==='entrance'?'-blind-hall':'-blind-transverse')));
}
check('Caps align original terminal pier hallward faces',eq(R.entrance_x[1],S.piers.x[0]+S.piers.size/2)&&eq(R.inner_x[0],S.piers.x.at(-1)-S.piers.size/2)&&eq(R.entrance_x[0],-30)&&eq(R.inner_x[1],30));
const columns=objects.filter(o=>o.kind==='newcolumn');
check('Exactly four new full-height square columns',columns.length===4&&columns.every(o=>eq(o.b[1]-o.b[0],2.4)&&eq(o.b[3]-o.b[2],2.4)&&eq(o.b[4],0)&&eq(o.b[5],18)&&D.columns.x.includes((o.b[0]+o.b[1])/2)&&D.columns.y.includes((o.b[2]+o.b[3])/2)));
for(const x of D.columns.x){
 const row=columns.filter(o=>eq((o.b[0]+o.b[1])/2,x)).sort((a,b)=>a.b[2]-b.b[2]);
 const original=objects.filter(o=>o.id.startsWith('original-pier')&&o.b[0]<x&&o.b[1]>x).sort((a,b)=>a.b[2]-b.b[2]);
 check('Actual shaft-face three passages at X'+x,eq(row[1].b[2]-row[0].b[3],2.4)&&eq(row[0].b[2]-original[0].b[3],2)&&eq(original[1].b[2]-row[1].b[3],2));
}
check('Strips retained and fully covered at four shafts',eq(S.floor_strips.abs_y,2.2)&&eq(S.floor_strips.width,.64)&&columns.every(o=>{const y=Math.sign(o.b[2])*S.floor_strips.abs_y;return y-.32>=o.b[2]&&y+.32<=o.b[3];}));
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
for(const d of R.doors){const ys=R.abs_y.map(y=>y*d.sign).sort((a,b)=>a-b);floor.push({id:d.id+'-unavailable-interior',b:[...R[d.end+'_x'],...ys,0,8.4]});}
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
// Exact union of obstacles across the full hall at checkpoint X proves floor openings.
const intervals=floor.filter(o=>o.b[0]<=Q.x&&o.b[1]>=Q.x).map(o=>[o.b[2],o.b[3]]).sort((a,b)=>a[0]-b[0]),merged=[];
for(const i of intervals){if(merged.length&&i[0]<=merged.at(-1)[1]+1e-7)merged.at(-1)[1]=Math.max(merged.at(-1)[1],i[1]);else merged.push([...i]);}
const openings=[];let end=-12;for(const [a,b] of merged){if(a>end+1e-7)openings.push([end,a]);end=Math.max(end,b);}if(end<12)openings.push([end,12]);
check('Exactly two accessible floor openings across all 24 metres',openings.length===2&&openings.every((o,i)=>eq(o[1]-o[0],Q.net_width)&&eq((o[0]+o[1])/2,Q.lane_centres_y[i])));
for(const x of [-27,27])for(const y of [-10,10])check('Former terminal aisle unavailable '+x+','+y,floor.some(o=>distance([x,y],o)===0));
// Eye-height slab-ray intersections expose occlusion; endpoints at walls are excluded.
const sightline=(a,b)=>objects.filter(o=>{let lo=0,hi=1;for(let k=0;k<3;k++){const d=b[k]-a[k];if(Math.abs(d)<1e-8){if(a[k]<o.b[k*2]||a[k]>o.b[k*2+1])return false;}else{let t0=(o.b[k*2]-a[k])/d,t1=(o.b[k*2+1]-a[k])/d;if(t0>t1)[t0,t1]=[t1,t0];lo=Math.max(lo,t0);hi=Math.min(hi,t1);if(lo>hi)return false;}}return lo<.9999&&hi>.0001;}).map(o=>o.id);
const sightlines=[{id:'axis-to-elevator',a:[-19,0,1.72],b:[29.39,0,1.72],expected_clear:true},{id:'off-axis-to-elevator',a:[-19,2.4,1.72],b:[29.39,0,1.72],expected_clear:false},{id:'aisle-to-service',a:[-14.5,10,1.72],b:[-19.79,10,1.72],expected_clear:true}].map(s=>({...s,blockers:sightline(s.a,s.b)}));
for(const s of sightlines)check('Sightline '+s.id,(s.blockers.length===0)===s.expected_clear,JSON.stringify(s.blockers));
const manifests=['Assets/Concepts/OpeningLobby/FunctionalRevision01/manifest.json','Saved/OpeningLobby/ArchitectureReworkA01/Worker/manifest.json','Assets/Concepts/OpeningLobby/ArchitectureRework01/manifest.json'];
for(const file of manifests){const m=read(file);for(const row of m.entries)check('Historical candidate preserved: '+row.path,hash(row.path)===row.sha256&&fs.statSync(path.join(root,row.path)).size===row.bytes);}
check('Baseline manifest exact identity',hash(manifests[1])===D.baseline.manifest_sha256);
check('Baseline map exact identity',hash('Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap')===D.baseline.map_sha256);
for(const r of read('Assets/Concepts/OpeningLobby/OwnerReferences01/references.json').files)check('Original owner art preserved: '+r.file,hash('Assets/Concepts/OpeningLobby/OwnerReferences01/'+r.file)===r.sha256);
const textAudit=JSON.parse(fs.readFileSync(path.join(worker,'text-audit.json'),'utf8'));
check('Five browser-measured sheets without text clipping/overlap',textAudit.sheets.length===5&&textAudit.sheets.every(s=>s.outside.length===0&&s.overlaps.length===0));
for(const sh of JSON.parse(fs.readFileSync(path.join(worker,'sheets.json'),'utf8'))){const png=fs.readFileSync(path.join(dir,sh.name+'.png'));check('PNG dimensions '+sh.name,png.readUInt32BE(16)===1600&&png.readUInt32BE(20)===1200);}
check('Historical Revision01 exact identity',hash(manifests[0])===D.prior_package.manifest_sha256);
check('Owner markup unchanged and paired exactly',hash('Assets/Concepts/OpeningLobby/FunctionalRevision02Inputs/OwnerMarkup01.png')==='fedce738e8218f3a80c5f811b4d2cbab947b96c02d965f45e5355fab02880541'&&hash('Assets/Concepts/OpeningLobby/FunctionalRevision02/OwnerMarkup01.png')===hash('Assets/Concepts/OpeningLobby/FunctionalRevision02Inputs/OwnerMarkup01.png'));
const sources=['Docs/Tasks/OpeningLobbyFunctionalRevision02.md','Docs/Approvals/LobbyFunctionalRevision02-OwnerMarkup01.json','Docs/Design/GameBrief.md','Docs/VisualAcceptance.md','.agents/skills/environment-reference-analysis/SKILL.md','Assets/Concepts/OpeningLobby/FunctionalRevision02Inputs/OwnerMarkup01.png','Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png','Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png','Assets/Concepts/OpeningLobby/ArchitectureRework01/04-A-sections.png',...fs.readdirSync(path.join(root,'Assets/Concepts/OpeningLobby/FunctionalRevision01')).map(n=>'Assets/Concepts/OpeningLobby/FunctionalRevision01/'+n)];
const report={candidate:D.package+'/'+D.revision,scope:'2D arithmetic, conservative sampled plan-route clearance and preserved source bytes. No engine collision, engineering, independent visual or owner acceptance.',checks,routes,openings,sightlines};
if(!frozen){fs.writeFileSync(path.join(worker,'verification.json'),JSON.stringify(report,null,2)+'\n');fs.writeFileSync(path.join(dir,'input-provenance.json'),JSON.stringify({inputs:sources.map(file=>({file,bytes:fs.statSync(path.join(root,file)).size,sha256:hash(file)}))},null,2)+'\n');}
console.log(JSON.stringify({checks:checks.length,passed:checks.filter(c=>c.pass).length,failed:checks.filter(c=>!c.pass),routes:routes.length,samples:routes.reduce((n,r)=>n+r.samples,0)},null,2));
if(checks.some(c=>!c.pass))process.exitCode=1;
