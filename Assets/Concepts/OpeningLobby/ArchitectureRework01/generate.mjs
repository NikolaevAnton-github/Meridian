// Reproducible local 2D architectural drawings. Emits SVG/PNG only, no scene or mesh.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../../..');
const worker=path.join(root,'Saved/OpeningLobby/ArchitectureRework01/Worker');
if(fs.existsSync(path.join(dir,'manifest.json')))throw Error('Frozen candidate: generation is disabled. Review this digest; put any authorized correction in a separately identified candidate.');
fs.mkdirSync(worker,{recursive:true});
const D=JSON.parse(fs.readFileSync(path.join(dir,'design.json'),'utf8'));
const S=D.shared;
const C={paper:'#f6f4ed',ink:'#243c38',muted:'#60736b',line:'#a6b2a7',stone:'#70877a',dark:'#415d53',deep:'#2b4943',pale:'#dce2d7',glass:'#c3dfd9',teal:'#187568',orange:'#ae542d',white:'#fffdf7'};
const sources=[
 'Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png',
 'Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png',
 'Assets/Concepts/OpeningLobby/ArchitectureRework01Inputs/OwnerEntranceDetail.png',
 'Assets/Concepts/OpeningLobby/Review02/03-SecurityOblique.png',
 'Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/C2-75.png',
 'Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/C3-90.png',
 'Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/Final/C3-context-90.png',
 'Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json',
 'Assets/Concepts/OpeningLobby/ScaleReview01/manifest.json',
 'Assets/Concepts/OpeningLobby/Approvals/LobbyScale-Review01.json',
 'Docs/Approvals/LobbyLayout03-Scale01.json',
 'Docs/Tasks/OpeningLobbyArchitectureRework01.md',
 'Docs/Design/GameBrief.md','Docs/VisualAcceptance.md',
 'Scripts/OpeningLobby/architecture01_unreal.py','Scripts/OpeningLobby/architecture01_kit.py',
 '.agents/skills/environment-reference-analysis/SKILL.md'
];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const inputRows=()=>sources.map(file=>({file,bytes:fs.statSync(path.join(root,file)).size,sha256:hash(path.join(root,file))}));
const before=path.join(worker,'inputs-before.json');
if(!fs.existsSync(before))fs.writeFileSync(before,JSON.stringify(inputRows(),null,2)+'\n');
const eq=(a,b)=>Math.abs(a-b)<1e-7;
const f=n=>Number(n.toFixed(3));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
let out=[],sheetName='',textRecords=[],sheets=[];
const W=1600,H=1200;
function line(x1,y1,x2,y2,color=C.ink,w=1.4,dash='') {out.push(`<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${color}" stroke-width="${w}" ${dash?`stroke-dasharray="${dash}"`:''}/>`);}
function rect(x,y,w,h,fill=C.pale,stroke=C.ink,sw=1.2,extra=''){if(w<0||h<0)throw Error('Negative rectangle');out.push(`<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${extra}/>`);}
function poly(points,fill=C.pale,stroke=C.ink,sw=1.3,extra=''){out.push(`<polygon points="${points.map(p=>p.map(f).join(',')).join(' ')}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round" ${extra}/>`);}
function text(x,y,t,size=19,color=C.ink,anchor='start',weight=400){out.push(`<text x="${f(x)}" y="${f(y)}" font-size="${size}" fill="${color}" text-anchor="${anchor}" font-weight="${weight}">${esc(t)}</text>`);textRecords.push({sheet:sheetName,x:f(x),y:f(y),text:t,size,anchor});}
function notes(x,y,rows,size=19,leading=28,color=C.ink){rows.forEach((t,i)=>text(x,y+i*leading,t,size,color));}
function dot(x,y,r=4,fill=C.orange){out.push(`<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" fill="${fill}"/>`);}
function tag(x,y,n){dot(x,y,14,C.white);out.push(`<circle cx="${x}" cy="${y}" r="14" fill="none" stroke="${C.teal}" stroke-width="1.7"/>`);text(x,y+6,n,17,C.teal,'middle',700);}
function arrow(x,y,xx,yy,color=C.teal,w=2){line(x,y,xx,yy,color,w);const a=Math.atan2(yy-y,xx-x);for(const da of [-.5,.5])line(xx,yy,xx-10*Math.cos(a+da),yy-10*Math.sin(a+da),color,w);}
function dh(x1,x2,y,label){line(x1,y,x2,y,C.teal);for(const x of [x1,x2])line(x-4,y+5,x+4,y-5,C.teal);text((x1+x2)/2,y-9,label,17,C.teal,'middle');}
function dv(x,y1,y2,label){line(x,y1,x,y2,C.teal);for(const y of [y1,y2])line(x-5,y+4,x+5,y-4,C.teal);out.push(`<text transform="translate(${f(x-9)} ${f((y1+y2)/2)}) rotate(-90)" font-size="17" fill="${C.teal}" text-anchor="middle">${esc(label)}</text>`);}
function leader(x,y,xx,yy,t,side='right'){dot(x,y,3,C.teal);line(x,y,xx,yy,C.teal);line(xx,yy,xx+(side==='right'?18:-18),yy,C.teal);text(xx+(side==='right'?24:-24),yy+6,t,18,C.teal,side==='right'?'start':'end');}
function person(x,b,s){const h=S.human.height;dot(x,b-(h-.12)*s,.12*s,C.orange);line(x,b-(h-.26)*s,x,b-.74*s,C.orange,.17*s);for(const a of [-1,1]){line(x,b-1.33*s,x+a*.24*s,b-.87*s,C.orange,.08*s);line(x,b-.75*s,x+a*.18*s,b,C.orange,.1*s);}}
function eye(x1,x2,b,s){line(x1,b-S.human.eye_height*s,x2,b-S.human.eye_height*s,C.orange,1.2,'7 5');}
function bar(x,y,s,length=5){for(let i=0;i<2;i++)rect(x+i*length*s/2,y,length*s/2,7,i?C.paper:C.ink);text(x,y+28,'0',16);text(x+length*s,y+28,`${length} m`,16,C.ink,'end');}
function panelTitle(x,y,n,title){text(x,y,n,17,C.teal,'start',700);text(x+43,y,title,23,C.ink,'start',600);}
function start(id,title,sub){sheetName=id;out=[];rect(0,0,W,H,C.paper,'none');text(44,37,'MERIDIAN SQUAD   /   LOBBYARCHITECTURE–REWORK01   /   CANDIDATE01',16,C.teal,'start',600);text(1556,37,id.slice(0,2),22,C.teal,'end',700);text(44,82,title,34,C.ink,'start',600);text(44,119,sub,18,C.muted);line(44,143,1556,143,C.line);line(44,1145,1556,1145,C.line);text(44,1176,'2D ARCHITECTURAL DRAWINGS  •  Metres  •  Proposed secondary forms  •  Pending independent review',17,C.orange);text(1556,1176,'Owner selection required before 3D',17,C.muted,'end');}
function save(){const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Arial, sans-serif"><defs><pattern id="cut" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#c5d0c0"/><path d="M0 9L9 0" stroke="#83957f" stroke-width="1"/></pattern></defs>${out.join('\n')}</svg>`;fs.writeFileSync(path.join(dir,`${sheetName}.svg`),svg);sheets.push({name:sheetName,width:W,height:H});}
function sourceImage(index,x,y,w,h){const file=sources[index];const b=fs.readFileSync(path.join(root,file));out.push(`<image x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,${b.toString('base64')}" data-source="${file}" data-sha256="${hash(path.join(root,file))}"/>`);}

// Common dimensional source -> planar drawing faces. Bounds are never exported as a mesh.
function solids(V,{full=true}={}) {
 const a=[];const add=(id,x0,x1,y0,y1,z0,z1,kind='stone')=>a.push({id,b:[x0,x1,y0,y1,z0,z1],kind});
 const mirror=(id,x0,x1,lo,hi,z0,z1,kind='stone')=>{add(id+'+',x0,x1,lo,hi,z0,z1,kind);add(id+'-',x0,x1,-hi,-lo,z0,z1,kind);};
 const p=V.portal,e=V.end_pier,u=V.upper,b=V.side_bay,t=V.transom,q=V.shoulder;
 for(const x of S.piers.x)if(full||x<=-19.8)mirror(`free-pier-${x}`,x-1.2,x+1.2,5.6,8,0,8.4);
 mirror('longitudinal-beam',-30,30,5.6,8,8.4,11.2);
 mirror('upper-wall',-30,30,u.inner_abs_y,u.outer_abs_y,u.bottom_z,u.top_z,'wall');
 mirror('terminal-engaged-pier',e.back_x,e.front_x,e.abs_y_min,e.abs_y_max,0,e.height);
 mirror('portal-main',p.back_x,p.front_x,p.abs_y_inner,p.abs_y_outer,p.z_min,p.z_max);
 mirror('portal-reveal-step',p.back_x,p.reveal_front_x,p.reveal_abs_y_inner,p.reveal_abs_y_outer,p.z_min,p.top_band_bottom,'reveal');
 add('portal-head-ceiling-joint',p.back_x,p.front_x,-p.abs_y_inner,p.abs_y_inner,p.top_band_bottom,18);
 mirror('recessed-shoulder',-30,q.front_x,q.abs_y_min,q.abs_y_max,q.z_min,q.z_max,'wall');
 add('entry-datum-or-bridge',t.back_x,t.front_x,-t.half_width,t.half_width,t.bottom_z,t.top_z);
 if(t.backing_return_to_x!==undefined)add('bridge-backing-return',t.backing_return_to_x,t.back_x,-t.half_width,t.half_width,t.bottom_z,t.top_z,'reveal');
 // A continuous raised sill is deliberately absent: the threshold remains flush.
 const dc=S.door_collar;
 mirror('human-door-jamb',dc.back_x,dc.front_x,dc.inner_half_width,dc.outer_half_width,0,dc.head_top,'metal');
 add('human-door-head',dc.back_x,dc.front_x,-dc.inner_half_width,dc.inner_half_width,dc.head_bottom,dc.head_top,'metal');
 for(const sign of [-1,1]){
  const yl=sign<0?-12:8,yh=sign<0?-8:12;
  add('coffer-end-'+sign,b.x_min,b.x_min+b.edge_width,yl,yh,b.edge_bottom_z,b.soffit_z,'soffit');
  add('coffer-pier-'+sign,b.x_max-b.edge_width,b.x_max,yl,yh,b.edge_bottom_z,b.soffit_z,'soffit');
  add('coffer-wall-'+sign,b.x_min+b.edge_width,b.x_max-b.edge_width,sign<0?-12:12-b.edge_width,sign<0?-12+b.edge_width:12,b.edge_bottom_z,b.soffit_z,'soffit');
  add('coffer-beam-'+sign,b.x_min+b.edge_width,b.x_max-b.edge_width,sign<0?-8-b.edge_width:8,sign<0?-8:8+b.edge_width,b.edge_bottom_z,b.soffit_z,'soffit');
  for(const x of b.cross_rib_centres_x)add('coffer-rib-'+sign,x-b.rib_width/2,x+b.rib_width/2,yl+b.edge_width,yh-b.edge_width,b.edge_bottom_z,b.soffit_z,'soffit');
 }
 const st=S.station,de=S.detector;
 add('station-body',st.x-st.depth/2,st.x+st.depth/2,st.y-st.width/2,st.y+st.width/2,0,st.height,'checkpoint');
 add('station-worktop',st.x-st.top_depth/2,st.x+st.top_depth/2,st.y-st.top_width/2,st.y+st.top_width/2,st.top_height-st.top_thickness,st.top_height,'checkpoint');
 for(const s of [-1,1]){const y=de.y+s*(de.clear_width/2+de.post_width/2);add('detector-post-'+s,de.x-de.depth/2,de.x+de.depth/2,y-de.post_width/2,y+de.post_width/2,0,de.clear_height,'checkpoint');}
 add('detector-head',de.x-de.depth/2,de.x+de.depth/2,de.y-de.clear_width/2-de.post_width,de.y+de.clear_width/2+de.post_width,de.clear_height,de.clear_height+de.header_height,'checkpoint');
 return a;
}

function plan(V,cx,top,s){
 const px=y=>cx-y*s,py=x=>top+(x+30)*s;
 rect(px(12),py(-30),24*s,12*s,C.white,C.ink,2);
 for(const sy of [-1,1])rect(px(sy*S.floor_strips.abs_y+S.floor_strips.width/2),py(-30),S.floor_strips.width*s,12*s,C.pale,'none');
 // Project all masses cut by Z=1.0; the actual station top is projected above.
 const cut=solids(V,{full:false}).filter(o=>o.b[4]<=1&&o.b[5]>1&&!o.id.startsWith('station-body'));
 for(const o of cut){const [x0,x1,y0,y1]=o.b;if(x0> -18)continue;rect(px(y1),py(x0),(y1-y0)*s,(Math.min(x1,-18)-x0)*s,o.kind==='checkpoint'?C.orange:(o.kind==='wall'?C.pale:C.stone),C.ink,1.5,`data-element="${o.id}" data-scale="${s}"`);}
 for(const sign of [-1,1]){
  // Dashed reflected soffit; no false floor obstruction.
  const b=V.side_bay,lo=sign<0?-12:8,hi=sign<0?-8:12;
  rect(px(hi),py(b.x_min),4*s,(b.x_max-b.x_min)*s,'none',C.muted,1.2,'stroke-dasharray="6 5"');
  rect(px(hi-b.edge_width),py(b.x_min+b.edge_width),(4-2*b.edge_width)*s,(b.x_max-b.x_min-2*b.edge_width)*s,'none',C.muted,1.2,'stroke-dasharray="6 5"');
  for(const x of b.cross_rib_centres_x)line(px(hi),py(x),px(lo),py(x),C.muted,3,'4 4');
  arrow(px(sign*10),py(-27),px(sign*10),py(-18.6));
 }
 arrow(px(10),py(-27),px(-10),py(-27));
 line(px(2.6),py(-30),px(-2.6),py(-30),C.glass,6);
 line(px(1.04),py(-30),px(-1.04),py(-30),C.orange,4);
 const t=V.transom;rect(px(t.half_width),py(t.back_x),t.half_width*2*s,(t.front_x-t.back_x)*s,'none',C.muted,1.4,'stroke-dasharray="6 5"');
 line(px(0),py(-30.4),px(0),py(-18),C.line,1.2,'8 5');
 text(px(0),py(-30.65),'PANE / DOOR X −30',17,C.teal,'middle');
 dh(px(12),px(-12),top-40,'24 overall');
 dh(px(5.6),px(-5.6),py(-18)+48,'11.2 central clear');
 dh(px(12),px(8),py(-18)+48,'4 aisle');
 dh(px(-8),px(-12),py(-18)+48,'4 aisle');
 dv(px(12)-20,py(V.end_pier.front_x),py(-22.2),`${V.terminal_clear_gap} terminal gap`);
 tag(px(3.7),py(V.portal.front_x)+14,'1');tag(px(-6.8),py(V.end_pier.front_x)-16,'2');tag(px(-10),py(-23.5),'3');tag(px(3.1),py(-24.6),'4');
 text(px(10),py(-18)+82,'+Y',17,C.teal,'middle');text(px(-10),py(-18)+82,'−Y',17,C.teal,'middle');
 arrow(px(0),py(-18)+75,px(0),py(-18)+106);text(px(0)+17,py(-18)+102,'+X into hall',17,C.teal);
 // Cut lines kept outside dimension chains.
 line(px(0)-7,py(-30.25),px(0)-7,py(-18.2),C.orange,1,'3 7');
 text(px(0)-20,py(-18.1),'L',17,C.orange,'end');
 line(px(12)+7,py(-21),px(-12)-7,py(-21),C.orange,1,'3 7');text(px(-12)+17,py(-21)+6,'T',17,C.orange);
}

function elevation(V,cx,base,s,{dimensions=true}={}){
 const px=y=>cx-y*s,pz=z=>base-z*s;
 rect(px(12),pz(9.2),24*s,9.2*s,C.pale,C.ink,1.8);
 rect(px(8),pz(18),16*s,8.8*s,C.pale,C.ink,1.8);
 for(const a of [-1,1]){
  const lo=a<0?-8:5.6,hi=a<0?-5.6:8;
  rect(px(hi),pz(11.2),2.4*s,11.2*s,C.dark);
  const q=V.shoulder;const ylo=a<0?-q.abs_y_max:q.abs_y_min,yhi=a<0?-q.abs_y_min:q.abs_y_max;
  rect(px(yhi),pz(q.z_max),(yhi-ylo)*s,(q.z_max-q.z_min)*s,C.pale);
  const p=V.portal;const l=a<0?-p.abs_y_outer:p.abs_y_inner,h=a<0?-p.abs_y_inner:p.abs_y_outer;
  rect(px(h),pz(p.z_max),(h-l)*s,(p.z_max-p.z_min)*s,C.stone);
  const rl=a<0?-p.reveal_abs_y_outer:p.reveal_abs_y_inner,rh=a<0?-p.reveal_abs_y_inner:p.reveal_abs_y_outer;
  rect(px(rh),pz(p.top_band_bottom),(rh-rl)*s,(p.top_band_bottom-p.z_min)*s,C.deep);
 }
 const gw=S.entrance.field_width,gs=V.upper_glazing_sill,gh=S.entrance.upper_head;
 rect(px(gw/2),pz(gh),gw*s,(gh-gs)*s,C.glass);
 rect(px(gw/2),pz(S.entrance.lower_height),gw*s,S.entrance.lower_height*s,C.glass);
 for(let i=1;i<4;i++)line(px(-gw/2+i*gw/4),pz(gh),px(-gw/2+i*gw/4),pz(gs),C.dark,1.7);
 for(let i=1;i<6;i++)line(px(gw/2),pz(gs+i*(gh-gs)/6),px(-gw/2),pz(gs+i*(gh-gs)/6),C.dark,1.6);
 const p=V.portal;rect(px(p.abs_y_inner),pz(18),2*p.abs_y_inner*s,.2*s,C.stone);
 const t=V.transom;rect(px(t.half_width),pz(t.top_z),2*t.half_width*s,(t.top_z-t.bottom_z)*s,C.dark);
 const dc=S.door_collar;
 rect(px(dc.outer_half_width),pz(dc.head_top),2*dc.outer_half_width*s,dc.head_top*s,C.dark);
 rect(px(dc.inner_half_width),pz(dc.head_bottom),2*dc.inner_half_width*s,dc.head_bottom*s,C.glass);
 line(cx,base,cx,pz(2.64),C.dark,1.4);
 line(px(2.6),pz(2.88),px(-2.6),pz(2.88),C.dark,1.2);
 const st=S.station,de=S.detector;
 rect(px(st.y+st.top_width/2),pz(st.top_height),st.top_width*s,st.top_thickness*s,C.orange,C.orange,1);
 rect(px(st.y+st.width/2),pz(st.height),st.width*s,st.height*s,'none',C.orange,1.3);
 for(const a of [-1,1]){const y=de.y+a*(de.clear_width/2+de.post_width/2);rect(px(y+de.post_width/2),pz(de.clear_height),de.post_width*s,de.clear_height*s,'none',C.orange,1.4);}
 rect(px(de.y+de.clear_width/2+de.post_width),pz(de.clear_height+de.header_height),(de.clear_width+de.post_width*2)*s,de.header_height*s,C.orange,C.orange,1);
 person(px(3.55),base,s);eye(px(12),px(-12),base,s);
 if(dimensions){dh(px(12),px(-12),base+48,'24 overall');dh(px(2.6),px(-2.6),pz(18)-26,'5.2 glazing');dv(px(-12)+35,pz(18),base,'18 central height');for(const z of [0,gs,11.2,17.8]){const edge=px(z<9.2?12:8);line(edge,pz(z),edge-12,pz(z),C.teal);text(edge-18,pz(z)+5,`Z ${z}`,16,C.teal,'end');}}
}

function sections(V){
 panelTitle(55,188,'L','Entrance section / Y = 0');
 text(55,217,'Looking +Y; pier, jamb and beam beyond shown pale.',17,C.muted);
 const s=29,b=799,px=x=>146+(x+30)*s,pz=z=>b-z*s;
 // Uncut elements beyond the centre line are deliberately light and dashed.
 for(const [x0,x1,z0,z1] of [[-22.2,-19.8,0,8.4],[-30,-18,8.4,11.2],[-30,-18,11.2,18],[-30,V.portal.front_x,V.portal.z_min,18]])rect(px(x0),pz(z1),(x1-x0)*s,(z1-z0)*s,'#e3e7dc',C.line,1,'stroke-dasharray="5 5"');
 line(px(-30),pz(18),px(-18),pz(18),C.ink,2);line(px(-30),b,px(-18),b,C.ink,2.4);
 rect(px(-30)-6,pz(17.8),6,(17.8-V.upper_glazing_sill)*s,C.glass,C.teal,1.4);
 rect(px(-30)-6,pz(5.28),6,5.28*s,C.glass,C.teal,1.4);
 const t=V.transom,p=V.portal,dc=S.door_collar;
 rect(px(t.back_x),pz(t.top_z),(t.front_x-t.back_x)*s,(t.top_z-t.bottom_z)*s,'url(#cut)',C.ink,2);
 if(t.backing_return_to_x!==undefined)rect(px(t.backing_return_to_x),pz(t.top_z),(t.back_x-t.backing_return_to_x)*s,(t.top_z-t.bottom_z)*s,'url(#cut)',C.ink,1.5);
 rect(px(-30),pz(18),(p.front_x+30)*s,.2*s,'url(#cut)',C.ink,2);
 rect(px(dc.back_x),pz(dc.head_top),(dc.front_x-dc.back_x)*s,(dc.head_top-dc.head_bottom)*s,C.dark,C.ink,1.7);
 // Door plane is retained; drawing does not invent leaf swing or external destination.
 line(px(-30),b,px(-30),pz(2.64),C.orange,3);
 const st=S.station,de=S.detector;
 rect(px(st.x-st.top_depth/2),pz(st.top_height),st.top_depth*s,st.top_thickness*s,'none',C.orange,1.2);
 rect(px(de.x-de.depth/2),pz(de.clear_height+de.header_height),de.depth*s,de.header_height*s,'none',C.orange,1.2);
 line(px(de.x-de.depth/2),b,px(de.x-de.depth/2),pz(de.clear_height),C.orange,1.2,'4 4');
 person(px(-26.6),b,s);eye(px(-30),px(-18),b,s);
 dv(103,pz(18),b,'18 hall height');dh(px(-30),px(-22.2),b+43,'7.8 datum to free pier');
 line(px(-27),b+3,px(-27),b-55,C.teal,1.2,'4 3');
 leader(px(-27),b-15,566,754,'Crossover X −27');
 leader(px(t.front_x),pz(t.top_z),566,618,`Band Z ${t.bottom_z}–${t.top_z}`);
 leader(px(-30),pz(V.upper_glazing_sill+2),566,533,'Glazing X −30');
 leader(px(-28.6),pz(11.2),566,454,'Beam beyond: Z 8.4–11.2');
 leader(px(p.front_x),pz(16.5),566,316,'Jamb beyond (dashed)');
 text(153,888,'Cut solids hatched. Exterior beyond X −30 unresolved.',17,C.muted);

 panelTitle(855,188,'T','Through first free pier / X = −21');
 text(855,217,'Looking −X; accepted shaft and beam section retained.',17,C.muted);
 text(855,246,'Shaft 2.4 × 2.4 × 8.4; beam 2.4 wide × 2.8 deep.',17,C.teal);
 const ts=24,tcx=1200,tb=799,tx=y=>tcx-y*ts,tz=z=>tb-z*ts;
 line(tx(12),tb,tx(-12),tb,C.ink,2.4);line(tx(8),tz(18),tx(-8),tz(18),C.ink,2);
 for(const sign of [-1,1]){
  const lo=sign<0?-8:5.6,hi=sign<0?-5.6:8;
  rect(tx(hi),tz(8.4),2.4*ts,8.4*ts,'url(#cut)',C.ink,2);
  rect(tx(hi),tz(11.2),2.4*ts,2.8*ts,'url(#cut)',C.ink,2);
  const ul=sign<0?-8:V.upper.inner_abs_y,uh=sign<0?-V.upper.inner_abs_y:8;
  rect(tx(uh),tz(18),(uh-ul)*ts,6.8*ts,'url(#cut)',C.ink,2);
  const al=sign<0?-12:8,ah=sign<0?-8:12;
  line(tx(ah),tz(9.2),tx(al),tz(9.2),C.ink,2.4);line(tx(sign*12),tb,tx(sign*12),tz(9.2),C.ink,2.4);
 }
 person(tcx,tb,ts);person(tx(10),tb,ts);eye(tx(12),tx(-12),tb,ts);
 dh(tx(5.6),tx(-5.6),tb+43,'11.2 central clear');dh(tx(12),tx(8),tb+43,'4 aisle');dh(tx(-8),tx(-12),tb+43,'4 aisle');
 dh(tx(V.upper.inner_abs_y),tx(-V.upper.inner_abs_y),tz(18)-28,`${f(2*V.upper.inner_abs_y)} upper clear`);
 leader(tx(V.upper.inner_abs_y),tz(11.2),1070,471,`${f(V.upper.inner_abs_y-5.6)} setback`,'left');
 leader(tx(-8),tz(9.2),1440,493,'Z 9.2');
 leader(tx(-5.6),tz(8.4),1440,552,'Z 8.4');
 text(855,888,'Human 1.8 / eye 1.72. Upper setback repeats along hall.',17,C.muted);

 line(44,914,1556,914,C.line);
 panelTitle(55,949,'P','Horizontal reveal / enlarged');
 const ds=64,cx=368,top=1000,rx=y=>cx-y*ds,ry=x=>top+(x+30)*ds;
 for(const [lo,hi,front,col] of [[p.abs_y_inner,p.abs_y_outer,p.front_x,C.stone],[p.reveal_abs_y_inner,p.reveal_abs_y_outer,p.reveal_front_x,C.deep]])rect(rx(hi),ry(-30),(hi-lo)*ds,(front+30)*ds,col,C.ink,1.6);
 line(rx(2.6),ry(-30),rx(1.3),ry(-30),C.glass,5);
 dh(rx(p.abs_y_outer),rx(p.abs_y_inner),ry(-30)-13,`${f(p.abs_y_outer-p.abs_y_inner)} main face`);
 notes(402,1001,[V.name.startsWith('Bridged')?`Upper jamb above Z 6; face X ${p.front_x}.`:`Main face X ${p.front_x}; pane X −30.`,`Pane to main / inner step: ${f(p.front_x+30)} / ${f(p.reveal_front_x+30)}.`,`Threshold Z 0; door collar depth 0.6.`,V.name.startsWith('Bridged')?'Bridge: 1.8 deep + 0.4 backing return.':'P cuts the full-height jamb.'],18,29);
 panelTitle(855,949,'S','Final side bay / X = −23.5');
 const ss=60,sx=y=>960+(y-8)*ss,sb=1092,sz=z=>sb-(z-8)*ss;
 rect(sx(8),sz(9.2),4*ss,.04*ss,C.pale,C.ink,2);
 for(const y of [8,12-V.side_bay.edge_width])rect(sx(y),sz(9.2),V.side_bay.edge_width*ss,.8*ss,'url(#cut)',C.ink,1.5);
 dh(sx(8),sx(12),1121,'4.0 floor aisle');
 notes(1260,990,['Z 9.2 recessed soffit','Z 8.4 perimeter edge','Edge width 0.35',V.side_bay.cross_rib_centres_x.length?'B rib: X −25 / width 0.4':'One quiet ceiling pocket'],17,28);
}

function projector(camera,frame){
 const {xyz,yaw,pitch,hfov}=camera,ya=yaw*Math.PI/180,pa=pitch*Math.PI/180;
 const F=[Math.cos(ya)*Math.cos(pa),Math.sin(ya)*Math.cos(pa),Math.sin(pa)];
 const R=[-Math.sin(ya),Math.cos(ya),0],U=[-Math.cos(ya)*Math.sin(pa),-Math.sin(ya)*Math.sin(pa),Math.cos(pa)];
 const dot3=(a,b)=>a.reduce((r,n,i)=>r+n*b[i],0),dist=p=>p.map((n,i)=>n-xyz[i]);
 const focal=frame.w/2/Math.tan(hfov*Math.PI/360);
 return {cam:xyz,toCamera:p=>{const d=dist(p);return [dot3(d,R),dot3(d,U),dot3(d,F)];},screen:q=>[frame.x+frame.w/2+focal*q[0]/q[2],frame.y+frame.h/2-focal*q[1]/q[2]]};
}
function nearClip(points,P){const q=points.map(P.toCamera),near=.25,r=[];for(let i=0;i<q.length;i++){const a=q[i],b=q[(i+1)%q.length],ain=a[2]>=near,bin=b[2]>=near;if(ain)r.push(a);if(ain!==bin){const t=(near-a[2])/(b[2]-a[2]);r.push(a.map((n,j)=>n+(b[j]-n)*t));}}return r;}
function tint(kind,face){const table={stone:['#75887a','#526d61','#354f47'],wall:['#b7c3b1','#93a590','#819782'],reveal:['#668078','#47665e','#2d4c47'],soffit:['#a0ad97','#7d927c','#61785f'],metal:['#394e46','#253d36','#1e312c'],checkpoint:['#465d52','#30483f','#213a32']};return (table[kind]||table.stone)[face==='x'?0:face==='z'?2:1];}
function perspective(V,camera,frame,id){
 out.push(`<defs><clipPath id="${id}"><rect x="${frame.x}" y="${frame.y}" width="${frame.w}" height="${frame.h}"/></clipPath></defs><g clip-path="url(#${id})">`);
 rect(frame.x,frame.y,frame.w,frame.h,'#e2e7da','none');
 const P=projector(camera,frame);
 const face=(pts,color,stroke=C.ink,w=.9)=>{const q=nearClip(pts,P);if(q.length>=3)poly(q.map(P.screen),color,stroke,w);};
 const drawLine=(a,b,col=C.line,w=1)=>{const q=[P.toCamera(a),P.toCamera(b)];if(q.every(p=>p[2]<.25))return;if(q.some(p=>p[2]<.25)){const i=q[0][2]<.25?0:1,j=1-i,t=(.25-q[i][2])/(q[j][2]-q[i][2]);q[i]=q[i].map((n,k)=>n+(q[j][k]-n)*t);}const [p0,p1]=q.map(P.screen);line(...p0,...p1,col,w);};
 face([[-30,-12,0],[30,-12,0],[30,12,0],[-30,12,0]],'#e0e4d5','none');
 for(const sign of [-1,1]){
  const y=sign*2.2;face([[-30,y-.32,.001],[30,y-.32,.001],[30,y+.32,.001],[-30,y+.32,.001]],'#829688','none');
  face([[-30,sign*12,0],[30,sign*12,0],[30,sign*12,9.2],[-30,sign*12,9.2]],'#b9c5b3');
  face([[-30,sign*8,9.2],[30,sign*8,9.2],[30,sign*12,9.2],[-30,sign*12,9.2]],'#899e84');
 }
 face([[-30,-8,18],[30,-8,18],[30,8,18],[-30,8,18]],'#adbca6');
 // End wall stays closed; glazing is a bright planar drawing field, not an exit claim.
 face([[-30,-12,0],[-30,12,0],[-30,12,9.2],[-30,-12,9.2]],'#b2c0ad');
 face([[-30,-8,9.2],[-30,8,9.2],[-30,8,18],[-30,-8,18]],'#b2c0ad');
 for(const [z0,z1] of [[0,5.28],[V.upper_glazing_sill,17.8]]){
  face([[-29.998,-2.6,z0],[-29.998,2.6,z0],[-29.998,2.6,z1],[-29.998,-2.6,z1]],'#d7ede6',C.deep,1.5);
  if(z0>0){for(let i=1;i<4;i++)drawLine([-29.99,-2.6+i*1.3,z0],[-29.99,-2.6+i*1.3,z1],C.dark,1.6);for(let i=1;i<6;i++)drawLine([-29.99,-2.6,z0+(z1-z0)*i/6],[-29.99,2.6,z0+(z1-z0)*i/6],C.dark,1.5);}
 }
 drawLine([-29.99,0,0],[-29.99,0,2.64],C.dark,1.5);drawLine([-29.99,-2.6,2.88],[-29.99,2.6,2.88],C.dark,1.5);
 for(let x=-30;x<=30;x+=3)drawLine([x,-12,.002],[x,12,.002],'#b5c3ad',.6);
 const faces=[];
 for(const o of solids(V)){
  const [x0,x1,y0,y1,z0,z1]=o.b;
  const fc=[{n:[1,0,0],p:[[x1,y0,z0],[x1,y1,z0],[x1,y1,z1],[x1,y0,z1]],a:'x'},{n:[-1,0,0],p:[[x0,y1,z0],[x0,y0,z0],[x0,y0,z1],[x0,y1,z1]],a:'x'},{n:[0,-1,0],p:[[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1]],a:'y'},{n:[0,1,0],p:[[x1,y1,z0],[x0,y1,z0],[x0,y1,z1],[x1,y1,z1]],a:'y'},{n:[0,0,1],p:[[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],a:'z'},{n:[0,0,-1],p:[[x0,y1,z0],[x1,y1,z0],[x1,y0,z0],[x0,y0,z0]],a:'z'}];
  for(const fp of fc){const ct=fp.p[0];if(fp.n.reduce((a,n,i)=>a+n*(P.cam[i]-ct[i]),0)<=0)continue;const q=nearClip(fp.p,P);if(q.length<3)continue;faces.push({q,col:tint(o.kind,fp.a),depth:q.reduce((a,p)=>a+p[2],0)/q.length,id:o.id});}
 }
 faces.sort((a,b)=>b.depth-a.depth);
 for(const fc of faces)poly(fc.q.map(P.screen),fc.col,'#395447',.85,`data-element="${fc.id}"`);
 // One standing silhouette, at a known clear central floor position.
 const hp=[-26.3,3.25,0],foot=P.screen(P.toCamera(hp)),head=P.screen(P.toCamera([hp[0],hp[1],1.8]));
 person(foot[0],foot[1],Math.abs(foot[1]-head[1])/1.8);
 out.push('</g>');rect(frame.x,frame.y,frame.w,frame.h,'none',C.line,1.2);
}

function axon(V,frame,id){
 // A parallel drawing of planar returns, selected near-side faces omitted.
 const all=solids(V,{full:false}).filter(o=>o.kind!=='checkpoint'&&o.b[3]>0&&o.b[0]<=-19.8).map(o=>({...o,b:o.b.map((n,i)=>i===2?Math.max(0,n):n)}));
 const sc=frame.w/25,pr=([x,y,z])=>[frame.x+frame.w*.47+(y-6)*sc*.87+(x+25)*sc*.58,frame.y+frame.h*.93-z*sc*.66+(x+25)*sc*.28-(y-6)*sc*.15];
 out.push(`<defs><clipPath id="${id}"><rect x="${frame.x}" y="${frame.y}" width="${frame.w}" height="${frame.h}"/></clipPath></defs><g clip-path="url(#${id})">`);
 poly([[-30,0,0],[-19.8,0,0],[-19.8,12,0],[-30,12,0]].map(pr),C.pale,C.line,1);
 for(const [z0,z1] of [[0,5.28],[V.upper_glazing_sill,17.8]])poly([[-30,0,z0],[-30,2.6,z0],[-30,2.6,z1],[-30,0,z1]].map(pr),C.glass,C.deep,.7);
 const faces=[];
 for(const o of all){let [x0,x1,y0,y1,z0,z1]=o.b;x1=Math.min(x1,-19.8);if(x1<=x0)continue;
  for(const [pts,axis] of [[[[x1,y0,z0],[x1,y1,z0],[x1,y1,z1],[x1,y0,z1]],'x'],[[[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1]],'y'],[[[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],'z']])faces.push({pts,col:tint(o.kind,axis),depth:pts.reduce((a,p)=>a+p[0]*.5742-p[1]*.3828+p[2]*.3306,0)/4});
 }
 faces.sort((a,b)=>a.depth-b.depth);for(const a of faces)poly(a.pts.map(pr),a.col,C.deep,.7);
 out.push('</g>');
}

start('01-reference-reading','Read the depth before designing the surface','Unchanged source images. Diagram and observations below are separate from the owner’s art.');
sourceImage(0,44,173,730,411);sourceImage(1,824,173,732,411);
text(44,614,'PRIMARY / EntranceSecurity — tall light field, heavy jambs, low checkpoint',18,C.teal);
text(824,614,'PRIMARY / InnerEnd — same beam rhythm, smaller human door',18,C.teal);
line(44,641,1556,641,C.line);
sourceImage(2,44,675,258,381);
notes(44,1082,['OWNER DETAIL / unchanged','Hidden depth is not measured.'],17,27,C.muted);
panelTitle(348,678,'R','Depth reading / qualitative');
poly([[345,1004],[695,1085],[982,989],[647,904]],'#e0e5d9',C.line,1);
rect(807,705,68,310,C.stone);rect(875,696,63,290,C.glass);rect(782,797,25,209,C.deep);
poly([[358,723],[782,782],[807,758],[383,699]],'#a5b4a2');
poly([[358,723],[782,782],[782,824],[358,766]],C.stone);
poly([[358,766],[782,824],[807,800],[383,742]],C.deep);
for(const [x,y,w,h] of [[358,766,72,238],[526,789,56,194],[661,807,42,160]]){rect(x,y,w,h,C.stone);poly([[x+w,y],[x+w+23,y-17],[x+w+23,y+h-17],[x+w,y+h]],C.dark);}
line(884,918,884,986,C.dark,2);line(926,918,926,986,C.dark,2);line(875,918,938,918,C.dark,2);
for(let i=1;i<4;i++)line(875+i*63/4,696,875+i*63/4,911,C.dark,1.2);
for(let i=1;i<5;i++)line(875,696+i*215/5,938,696+i*215/5,C.dark,1.2);
tag(432,847,'1');tag(754,917,'2');tag(587,763,'3');tag(847,861,'4');tag(909,944,'5');
text(348,1112,'Ordering and occlusion only; all proposed metres appear on later sheets.',17,C.muted);
panelTitle(1019,678,'V','Visible evidence');
notes(1019,717,['1  Front and return faces of free piers.','    A walkable aisle is visible behind.','2  Dark terminal shoulder is occluded','    by the pier and entrance surround.','3  Deep beam underside converges','    into the terminal wall zone.','4  Broad stone jamb beside thin glass.','5  Human entrance below a tall window.'],18,27);
text(1019,966,'I / Interpretation, medium confidence',19,C.orange,'start',600);
notes(1019,999,['The shoulder reads as a setback;','its exact depth and upper junction','are not revealed. Review02 clarifies','the checkpoint, not hidden structure.'],18,27);
save();

start('02-baseline-and-constraints','Keep the monumentality; redesign the junction','Current candidate is diagnostic evidence. It already has projecting piers and real side aisles.');
sourceImage(4,44,176,730,411);sourceImage(6,824,176,732,411);
text(44,617,'CURRENT / C2-75 — overall hall and entrance',18,C.teal);
text(824,617,'CURRENT / C3-context-90 — wall, beam and window meet',18,C.teal);
line(44,647,1556,647,C.line);
sourceImage(3,44,687,350,197);sourceImage(5,424,687,350,197);
notes(44,913,['SUBORDINATE / Review02 oblique','Original supplement, unchanged.'],17,26,C.muted);
notes(424,913,['CURRENT / C3-90 close view','Original capture, unchanged.'],17,26,C.muted);
notes(44,998,['Baseline diagnosis: a near-planar end field and applied bands.','The existing 2.4 m piers are substantial; they are not flush walls.','The redesign adds coherent returns, terminal piers and soffits.','Reference lenses are uncertain; these images are not matched cameras.'],18,29);
panelTitle(824,686,'P','Accepted footprint / +X to the right');
{
 const s=10.5,px=x=>1190+x*s,py=y=>880-y*s;
 rect(px(-30),py(12),60*s,24*s,C.white,C.ink,1.8);
 for(const x of S.piers.x)for(const y of [-6.8,6.8])rect(px(x-1.2),py(y+1.2),2.4*s,2.4*s,C.stone);
 for(const y of [-10,10])arrow(px(-27),py(y),px(27),py(y));
 arrow(px(-27),py(10),px(-27),py(-10));
 const st=S.station;rect(px(st.x-st.top_depth/2),py(st.y+st.top_width/2),st.top_depth*s,st.top_width*s,C.orange,C.orange);
 line(px(-30),py(2.6),px(-30),py(-2.6),C.glass,5);
 rect(px(-30),py(12),10.2*s,24*s,'none',C.orange,2);
 text(px(-30),py(12)-18,'Entrance study',17,C.orange);
 dh(px(-30),px(30),py(-12)+36,'60 m / six pier pairs / 8.4 pitch');
 dv(1537,py(12),py(-12),'24 m');
 text(824,1097,'18 m high • 11.2 m central clear • 4 m side aisles',19,C.teal);
}
save();

function orthographicSheet(key,id){
 const V=D.variants[key];
 start(id,`${key} / ${V.name}`,key==='A'?'A continuous vertical surround, separated from the end piers by a quiet recessed shoulder.':'A broad lower bridge ties engaged piers together; the upper window and jambs step back above it.');
 panelTitle(55,189,'P','Entry plan / cut at Z 1.0');
 text(55,220,'+Y left, +X down; dashed = overhead. L/T cuts on next sheet.',17,C.muted);
 plan(V,413,300,26);
 panelTitle(824,189,'E','Interior entrance elevation');
 text(824,220,'Free piers omitted; checkpoint projected in orange.',17,C.muted);
 elevation(V,1165,798,25);
 notes(55,761,[`1  Portal: main face X ${V.portal.front_x}.`,`2  Engaged end pier: X ${V.end_pier.front_x}.`,`3  Side-bay pocket: Z 9.2; perimeter Z 8.4.`,`4  Station at Y +0.95; detector at Y −1.05.`,`Crossover stays at X −27; checkpoint at X −24.6.`,`Free pier 2.4 × 2.4; shaft 8.4; bay pitch 8.4.`],18,30);
 bar(55,945,26,5);
 notes(824,884,[`Upper glass: 5.2 × ${f(17.8-V.upper_glazing_sill)}; sill ${V.upper_glazing_sill}; head 17.8.`,`Lower field: 5.2 × 5.28; two leaves 1.04 × 2.64.`,`Detector clear: 1.14 × 2.28; station top Z 1.02.`,`Standing human: 1.8; dashed eye datum: 1.72.`],18,30);
 line(44,1013,1556,1013,C.line);
 text(55,1048,'DEPTH SEQUENCE / from the hall toward the pane',19,C.teal,'start',600);
 notes(55,1080,key==='A'?['Main jamb −28.4  →  inner reveal −29.0  →  glazing / door −30.0.','Adjacent shoulder −29.6; terminal pier −28.8; first free pier face −22.2.']:['Engaged pier / bridge −27.8  →  upper jamb −28.6  →  glazing / door −30.0.','Lower side wall −29.6; first free pier face −22.2; bridge spans 11.2 m.'],18,28);
 text(1000,1048,key==='A'?'Accepted glazing dimensions retained.':'EXPLICIT ACCEPTED-SCHEDULE DELTA',18,key==='A'?C.teal:C.orange,'start',600);
 notes(1000,1080,key==='A'?['Proposed metres define visible form.','No hidden structure or route is asserted.']:['Upper sill +0.6; glass height −0.6.','Requires an explicit owner decision.'],18,28);
 save();
}
function sectionSheet(key,id){const V=D.variants[key];start(id,`${key} / Resolve the section before production`,'Primary shaft and beam dimensions remain fixed. Hatched cuts and enlarged details expose the secondary depth.');sections(V);save();}
function spatialSheet(key,id){
 const V=D.variants[key];start(id,`${key} / ${V.name} in space`,'Architectural perspective drawings from the same cameras in A and B. Neutral diagram tones; no engine evidence.');
 panelTitle(44,181,'O','Oblique approach / entrance and adjacent bay');
 perspective(V,D.drawing_cameras.approach,{x:44,y:208,w:1040,h:585},'oblique-'+key);
 notes(44,824,[`Eye 1.72 m / X −14, Y +3.5 / yaw ${D.drawing_cameras.approach.yaw}°, pitch +${D.drawing_cameras.approach.pitch}° / HFOV ${D.drawing_cameras.approach.hfov}°`,'Wide drawing lens includes head and adjacent pier; gameplay FOV remains 90°.'],18,28,C.muted);
 text(1110,181,'AXIAL HALL CONTEXT',18,C.teal,'start',600);
 perspective(V,D.drawing_cameras.context,{x:1110,y:208,w:446,h:251},'context-'+key);
 notes(1110,488,['X +19, Y 0, eye 1.72; pitch 0°','HFOV 75° / accepted provisional C2'],17,26,C.muted);
 text(1110,555,'OPEN PARALLEL DRAWING',18,C.teal,'start',600);
 axon(V,{x:1110,y:574,w:446,h:282},'axon-'+key);
 text(1110,884,'+Y half / selected enclosing faces omitted',16,C.muted);
 line(44,913,1556,913,C.line);
 if(key==='A'){
  panelTitle(55,951,'1','Vertical continuity');
  notes(55,986,['The tall jamb stays continuous to the head.','A 1.6 m return puts the thin glazing behind','a substantial stone edge; a 0.6 m inner step','makes the reveal legible on approach.'],18,28);
  panelTitle(565,951,'2','A separated terminal joint');
  notes(565,986,['The 1.0 m wide shoulder sits behind the','portal and engaged pier. The long beam','lands on the end pier; the upper wall','steps back 0.6 m above the beam.'],18,28);
  panelTitle(1070,951,'3','One quiet side-bay pocket');
  notes(1070,986,['A deep perimeter frames the side soffit.','The 4 m floor aisle and crossover stay.','The head zone remains thin at 0.2 m;','hidden construction is unresolved.'],18,28);
 }else{
  text(55,952,'A / recommended for the next owner selection',22,C.teal,'start',600);
  notes(55,989,['Stronger match to the art’s uninterrupted vertical surround.','Keeps the approved upper glass at 5.2 × 12.4 m.','Terminal gap 6.6 m; crossover capsule margin 1.06 m.','Tradeoff: the deep jamb masks more glass at an oblique angle.'],19,30);
  text(836,952,'B / a more enclosed entrance pause',22,C.teal,'start',600);
  notes(836,989,['The 11.2 m bridge ties the end piers and lower field together.','Upper glass becomes 5.2 × 11.8 m; sill increases to 6.0 m.','Terminal gap 5.6 m; crossover capsule margin 0.46 m.','Tradeoff: the horizontal bridge competes with the tall window.'],19,30);
 }
 save();
}
orthographicSheet('A','03-A-plan-elevation');
sectionSheet('A','04-A-sections');
spatialSheet('A','05-A-spatial');
orthographicSheet('B','06-B-plan-elevation');
sectionSheet('B','07-B-sections');
spatialSheet('B','08-B-spatial-comparison');

// Meaningful acceptance checks: source preservation, schedule agreement and path clearance.
const checks=[];function check(name,pass,detail=''){checks.push({name,pass:!!pass,detail});if(!pass)throw Error(name);}
const accepted=JSON.parse(fs.readFileSync(path.join(root,'Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json'),'utf8'));
const old=accepted.architecture.candidate;
for(const k of ['length','width','height'])check(`Accepted hall ${k}`,eq(S.hall[k],old[k]));
check('Accepted six pier pairs and exact coordinates',JSON.stringify(S.piers.x)===JSON.stringify(old.pier_x)&&S.piers.pair_count===6&&eq(S.piers.abs_y,old.pier_y)&&eq(S.piers.size,old.pier_size));
check('Width partition closes',eq(S.circulation.central_clear+2*S.piers.size+2*S.circulation.aisle_clear,S.hall.width));
for(let i=1;i<S.piers.x.length;i++)check(`Pier interval ${i}`,eq(S.piers.x[i]-S.piers.x[i-1],8.4));
check('Checkpoint and human-use exceptions retained',eq(S.station.x,accepted.human_elements.station.x)&&eq(S.station.y,accepted.human_elements.station.y)&&eq(S.station.top_depth,accepted.human_elements.station.worktop_depth_x)&&eq(S.station.top_width,accepted.human_elements.station.worktop_width_y)&&eq(S.station.top_height,accepted.human_elements.station.worktop_height)&&eq(S.detector.x,accepted.human_elements.detector.x)&&eq(S.detector.y,accepted.human_elements.detector.y)&&eq(S.detector.clear_width,accepted.human_elements.detector.clear_width)&&eq(S.detector.clear_height,accepted.human_elements.detector.clear_height)&&eq(S.entrance.leaf_width,accepted.human_elements.entrance_leaves.candidate_leaf_width)&&eq(S.entrance.leaf_height,accepted.human_elements.entrance_leaves.candidate_leaf_height));
check('Human and eye height retained',eq(S.human.height,accepted.human_reference.height)&&eq(S.human.eye_height,accepted.human_reference.eye_height));
check('Scale manifest matches external approval',hash(path.join(root,'Assets/Concepts/OpeningLobby/ScaleReview01/manifest.json'))===D.authority.scale_manifest_sha256);
for(const [key,V] of Object.entries(D.variants)){
 const list=solids(V);
 check(`${key}: positive drawing bounds`,list.every(o=>o.b[1]>o.b[0]&&o.b[3]>o.b[2]&&o.b[5]>o.b[4]));
 check(`${key}: all secondary masses inside accepted hall`,list.every(o=>o.b[0]>=-30&&o.b[1]<=30&&o.b[2]>=-12&&o.b[3]<=12&&o.b[4]>=0&&o.b[5]<=18));
 check(`${key}: terminal gap closes`,eq(-22.2-V.end_pier.front_x,V.terminal_clear_gap));
 check(`${key}: upper-wall setback leaves supported beam shelf`,V.upper.inner_abs_y>=5.6&&V.upper.inner_abs_y<8&&eq(V.upper.bottom_z,11.2));
 check(`${key}: upper glass joins bridge / datum without overlap`,eq(V.upper_glazing_sill,V.transom.top_z)&&eq(V.transom.bottom_z,5.28));
 check(`${key}: door collar keeps nominal leaves unobstructed`,eq(S.door_collar.inner_half_width,S.entrance.leaf_width)&&eq(S.door_collar.head_bottom,S.entrance.leaf_height));
 const floor=list.filter(o=>o.b[4]<1.76&&o.b[5]>0);
 const distanceToSegment=(o)=>{const [x0,x1,y0,y1]=o.b;const dx=Math.max(x0+27,-27-x1,0),dy=Math.max(y0-10,-10-y1,0);return Math.hypot(dx,dy);};
 const minimum=Math.min(...floor.map(distanceToSegment));
 check(`${key}: crossover minimum centre distance`,eq(minimum,V.crossover_min_centre_distance),`${f(minimum)} m`);
 check(`${key}: crossover capsule clears all drawn floor masses`,minimum>S.circulation.capsule_radius&&eq(minimum-S.circulation.capsule_radius,V.crossover_capsule_margin),`${f(minimum-S.circulation.capsule_radius)} m nominal margin`);
 for(const sign of [-1,1])check(`${key}: aisle centre ${sign*10} clear from X -27 to +27`,floor.every(o=>{const [x0,x1,y0,y1]=o.b;if(x1< -27||x0>27)return true;const dy=Math.max(y0-sign*10,sign*10-y1,0);return dy>.34;}));
 const svg=fs.readFileSync(path.join(dir,`${key==='A'?'03-A':'06-B'}-plan-elevation.svg`),'utf8');
 const match=svg.match(/<rect[^>]*data-element="terminal-engaged-pier\+"[^>]*\/>/);
 const attrs=Object.fromEntries([...match[0].matchAll(/([\w-]+)="([^"]*)"/g)].map(m=>[m[1],m[2]]));
 check(`${key}: serialized plan pier depth matches source`,eq(Number(attrs.height)/Number(attrs['data-scale']),V.end_pier.front_x+30));
 check(`${key}: section annotation contains correct band levels`,fs.readFileSync(path.join(dir,`${key==='A'?'04-A':'07-B'}-sections.svg`),'utf8').includes(`Band Z ${V.transom.bottom_z}–${V.transom.top_z}`));
}
for(const row of JSON.parse(fs.readFileSync(before,'utf8')))check(`Input preserved: ${row.file}`,hash(path.join(root,row.file))===row.sha256);
fs.writeFileSync(path.join(worker,'verification.json'),JSON.stringify({package:D.package,revision:D.revision,scope:'Drawing arithmetic, source preservation and nominal route clearance only. No collision, structural or visual acceptance.',checks},null,2)+'\n');
fs.writeFileSync(path.join(worker,'text-records.json'),JSON.stringify(textRecords,null,2)+'\n');
fs.writeFileSync(path.join(worker,'sheets.json'),JSON.stringify(sheets,null,2)+'\n');
fs.writeFileSync(path.join(dir,'input-provenance.json'),JSON.stringify({package:D.package,inputs:inputRows(),source_image_policy:'Original PNG bytes embedded unchanged with preserveAspectRatio=meet, no source edits or image cropping.'},null,2)+'\n');
console.log(`Generated ${sheets.length} SVG drawings; ${checks.length} checks passed.`);

if(process.argv.some(a=>a==='--render'||a.startsWith('--render='))){
 const requested=process.argv.find(a=>a.startsWith('--render='))?.slice(9);
 const chrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
 if(!fs.existsSync(chrome))throw Error('Installed Chrome required for local PNG previews; no installation attempted.');
 for(const sh of sheets){
  if(requested&&sh.name!==requested)continue;
  const html=path.join(worker,`${sh.name}.html`),svgurl=new URL('file:///'+path.join(dir,sh.name+'.svg').replaceAll('\\','/')).href;
  fs.writeFileSync(html,`<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;width:${W}px;height:${H}px;overflow:hidden}img{display:block;width:${W}px;height:${H}px}</style></head><body><img src="${svgurl}"></body></html>`);
  const args=['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-extensions','--disable-sync','--disable-component-update','--hide-scrollbars','--allow-file-access-from-files',`--user-data-dir=${path.join(worker,'BrowserProfile')}`,'--disk-cache-size=1048576','--media-cache-size=1048576','--force-device-scale-factor=1',`--window-size=${W},${H}`,'--run-all-compositor-stages-before-draw','--virtual-time-budget=1200',`--screenshot=${path.join(dir,sh.name+'.png')}`,new URL('file:///'+html.replaceAll('\\','/')).href];
  const r=spawnSync(chrome,args,{encoding:'utf8',timeout:45000,windowsHide:true});
  fs.writeFileSync(path.join(worker,`${sh.name}-render.log`),`${r.stdout||''}\n${r.stderr||''}\nExit: ${r.status}\nError: ${r.error||''}`);
  if(r.status!==0||!fs.existsSync(path.join(dir,sh.name+'.png')))throw Error(`Render failed: ${sh.name}`);
  console.log(`Rendered ${sh.name}`);
 }
}
