// SVG drafting primitives and perspective adapted from ArchitectureRework01/generate.mjs.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(dir,'../../../..');
const worker=path.join(root,'Saved/OpeningLobby/FunctionalRevision02/Worker');
if(fs.existsSync(path.join(dir,'manifest.json')))throw Error('Frozen candidate');
const D=JSON.parse(fs.readFileSync(path.join(dir,'design.json'),'utf8')),S=D.shared,V=D.retained_A;
const C={paper:'#f6f4ed',ink:'#243c38',muted:'#60736b',line:'#a6b2a7',stone:'#70877a',dark:'#415d53',deep:'#2b4943',pale:'#dce2d7',glass:'#c3dfd9',teal:'#187568',orange:'#ae542d',white:'#fffdf7'};
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
function start(id,title,sub){sheetName=id;out=[];rect(0,0,W,H,C.paper,'none');text(44,37,'MERIDIAN SQUAD   /   LOBBYFUNCTIONAL–REVISION02   /   CANDIDATE01',16,C.teal,'start',600);text(1556,37,id.slice(0,2),22,C.teal,'end',700);text(44,82,title,34,C.ink,'start',600);text(44,119,sub,18,C.muted);line(44,143,1556,143,C.line);line(44,1145,1556,1145,C.line);text(44,1176,'2D ARCHITECTURAL DRAWINGS  •  Metres  •  Functional proposals  •  Pending independent review',17,C.orange);text(1556,1176,'Owner approval required before 3D',17,C.muted,'end');}
function save(){const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Arial, sans-serif"><defs><pattern id="cut" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#c5d0c0"/><path d="M0 9L9 0" stroke="#83957f" stroke-width="1"/></pattern></defs>${out.join('\n')}</svg>`;fs.writeFileSync(path.join(dir,`${sheetName}.svg`),svg);sheets.push({name:sheetName,width:W,height:H});}
function retainedSolids(V,{full=true}={}) {
 const a=[];const add=(id,x0,x1,y0,y1,z0,z1,kind='stone')=>a.push({id,b:[x0,x1,y0,y1,z0,z1],kind});
 const mirror=(id,x0,x1,lo,hi,z0,z1,kind='stone')=>{add(id+'+',x0,x1,lo,hi,z0,z1,kind);add(id+'-',x0,x1,-hi,-lo,z0,z1,kind);};
 const p=V.portal,e=V.end_pier,u=V.upper,b=V.side_bay,t=V.transom,q=V.shoulder;
 for(const x of S.piers.x)if(full||x<=-19.8)mirror(`original-pier-${x}`,x-1.2,x+1.2,5.6,8,0,8.4);
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
 return a;
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
function tint(kind,face){const table={stone:['#75887a','#526d61','#354f47'],wall:['#b7c3b1','#93a590','#819782'],reveal:['#668078','#47665e','#2d4c47'],soffit:['#a0ad97','#7d927c','#61785f'],metal:['#394e46','#253d36','#1e312c'],checkpoint:['#465d52','#30483f','#213a32'],newcolumn:['#ba956c','#987852','#745c40'],infill:['#cfbba0','#b39e82','#99856b']};return (table[kind]||table.stone)[face==='x'?0:face==='z'?2:1];}
function perspective(V,camera,frame,id){
 out.push(`<defs><clipPath id="${id}"><rect x="${frame.x}" y="${frame.y}" width="${frame.w}" height="${frame.h}"/></clipPath></defs><g clip-path="url(#${id})">`);
 rect(frame.x,frame.y,frame.w,frame.h,'#e2e7da','none');
 const P=projector(camera,frame);
 const inner=camera.yaw===0;
 const face=(pts,color,stroke=C.ink,w=.9)=>{const q=nearClip(pts,P);if(q.length>=3)poly(q.map(P.screen),color,stroke,w);};
 const drawLine=(a,b,col=C.line,w=1)=>{const q=[P.toCamera(a),P.toCamera(b)];if(q.every(p=>p[2]<.25))return;if(q.some(p=>p[2]<.25)){const i=q[0][2]<.25?0:1,j=1-i,t=(.25-q[i][2])/(q[j][2]-q[i][2]);q[i]=q[i].map((n,k)=>n+(q[j][k]-n)*t);}const [p0,p1]=q.map(P.screen);line(...p0,...p1,col,w);};
 face([[-30,-12,0],[30,-12,0],[30,12,0],[-30,12,0]],'#e0e4d5','none');
 for(const sign of [-1,1]){
  const y=sign*2.2;face([[-30,y-.32,.001],[30,y-.32,.001],[30,y+.32,.001],[-30,y+.32,.001]],'#829688','none');
  face([[-30,sign*12,0],[30,sign*12,0],[30,sign*12,9.2],[-30,sign*12,9.2]],'#b9c5b3');
  face([[-30,sign*8,9.2],[30,sign*8,9.2],[30,sign*12,9.2],[-30,sign*12,9.2]],'#899e84');
 }
 face([[-30,-8,18],[30,-8,18],[30,8,18],[-30,8,18]],'#adbca6');
 if(!inner){
 // End wall stays closed; glazing is a bright planar drawing field, not an exit claim.
 face([[-30,-12,0],[-30,12,0],[-30,12,9.2],[-30,-12,9.2]],'#b2c0ad');
 face([[-30,-8,9.2],[-30,8,9.2],[-30,8,18],[-30,-8,18]],'#b2c0ad');
 for(const [z0,z1] of [[0,5.28],[V.upper_glazing_sill,17.8]]){
  face([[-29.998,-2.6,z0],[-29.998,2.6,z0],[-29.998,2.6,z1],[-29.998,-2.6,z1]],'#d7ede6',C.deep,1.5);
  if(z0>0){for(let i=1;i<4;i++)drawLine([-29.99,-2.6+i*1.3,z0],[-29.99,-2.6+i*1.3,z1],C.dark,1.6);for(let i=1;i<6;i++)drawLine([-29.99,-2.6,z0+(z1-z0)*i/6],[-29.99,2.6,z0+(z1-z0)*i/6],C.dark,1.5);}
 }
 drawLine([-29.99,0,0],[-29.99,0,2.64],C.dark,1.5);drawLine([-29.99,-2.6,2.88],[-29.99,2.6,2.88],C.dark,1.5);
 }else{
 face([[30,-12,0],[30,12,0],[30,12,18],[30,-12,18]],'#b2c0ad');
 const q=D.elevator.sign_zone;
 face([[29.99,-q.width/2,q.z[0]],[29.99,q.width/2,q.z[0]],[29.99,q.width/2,q.z[1]],[29.99,-q.width/2,q.z[1]]],'#b2c0ad','none');
 }
 for(let x=-30;x<=30;x+=3)drawLine([x,-12,.002],[x,12,.002],'#b5c3ad',.6);
 const faces=[];
 for(const o of solids(V)){
  const [x0,x1,y0,y1,z0,z1]=o.b;
  const fc=[{n:[1,0,0],p:[[x1,y0,z0],[x1,y1,z0],[x1,y1,z1],[x1,y0,z1]],a:'x'},{n:[-1,0,0],p:[[x0,y1,z0],[x0,y0,z0],[x0,y0,z1],[x0,y1,z1]],a:'x'},{n:[0,-1,0],p:[[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1]],a:'y'},{n:[0,1,0],p:[[x1,y1,z0],[x0,y1,z0],[x0,y1,z1],[x1,y1,z1]],a:'y'},{n:[0,0,1],p:[[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],a:'z'},{n:[0,0,-1],p:[[x0,y1,z0],[x1,y1,z0],[x1,y0,z0],[x0,y0,z0]],a:'z'}];
  for(const fp of fc){const ct=fp.p[0];if(fp.n.reduce((a,n,i)=>a+n*(P.cam[i]-ct[i]),0)<=0)continue;const q=nearClip(fp.p,P);if(q.length<3)continue;faces.push({p:fp.p,original:fp.p,col:tint(o.kind,fp.a),id:o.id});}
 }
 for(const fc of orderedFaces(faces,P.cam)){const q=nearClip(fc.p,P);if(q.length<3)continue;poly(q.map(P.screen),fc.col,'none',0);for(let i=0;i<fc.p.length;i++){const a=fc.p[i],b=fc.p[(i+1)%fc.p.length];if(originalEdge(a,b,fc.original))drawLine(a,b,'#395447',.7);}}
 // One standing silhouette, at a known clear central floor position.
 const hp=camera.human_xyz||(inner?[28,3.3,0]:[-26.3,3.25,0]),foot=P.screen(P.toCamera(hp)),head=P.screen(P.toCamera([hp[0],hp[1],1.8]));
 person(foot[0],foot[1],Math.abs(foot[1]-head[1])/1.8);
 out.push('</g>');rect(frame.x,frame.y,frame.w,frame.h,'none',C.line,1.2);
}

// Exact painter ordering for axis-aligned architectural drawing faces.
// Splits SVG source polygons at intervening planes; no mesh or scene is exported.
function orderedFaces(input,camera){
 const eps=1e-7;
 const side=(p,axis,k)=>p[axis]-k;
 function split(face,axis,k){
  const pos=[],neg=[],pts=face.p;
  for(let i=0;i<pts.length;i++){
   const a=pts[i],b=pts[(i+1)%pts.length],sa=side(a,axis,k),sb=side(b,axis,k);
   if(sa>=-eps)pos.push(a);if(sa<=eps)neg.push(a);
   if(sa*sb< -eps){const t=sa/(sa-sb),q=a.map((n,j)=>n+(b[j]-n)*t);pos.push(q);neg.push(q);}
  }
  return [pos.length>=3?{...face,p:pos}:null,neg.length>=3?{...face,p:neg}:null];
 }
 function build(list){
  if(!list.length)return null;
  const pivot=list[0],axis=[0,1,2].find(i=>pivot.p.every(p=>Math.abs(p[i]-pivot.p[0][i])<eps)),k=pivot.p[0][axis];
  const plane=[],pos=[],neg=[];
  for(const face of list){const v=face.p.map(p=>side(p,axis,k));if(v.every(n=>Math.abs(n)<eps))plane.push(face);else if(v.every(n=>n>=-eps))pos.push(face);else if(v.every(n=>n<=eps))neg.push(face);else{const [p,n]=split(face,axis,k);if(p)pos.push(p);if(n)neg.push(n);}}
  return {axis,k,plane,pos:build(pos),neg:build(neg)};
 }
 const result=[];
 function visit(n){if(!n)return;const near=camera[n.axis]>=n.k;visit(near?n.neg:n.pos);result.push(...n.plane);visit(near?n.pos:n.neg);}
 visit(build(input));return result;
}
function originalEdge(a,b,original){
 const eps=1e-6;
 for(let i=0;i<original.length;i++){
  const p=original[i],q=original[(i+1)%original.length],axis=[0,1,2].find(j=>Math.abs(p[j]-q[j])>eps);
  if(axis===undefined)continue;
  if([0,1,2].every(j=>j===axis||(Math.abs(a[j]-p[j])<eps&&Math.abs(b[j]-p[j])<eps)))return true;
 }return false;
}

// Derived planar bounds for orthographic cuts and SVG perspective projection only.
function solids(V){
 const a=retainedSolids(V),R=D.rooms,Q=D.checkpoint,E=D.elevator,N=D.columns;
 const add=(id,x0,x1,y0,y1,z0,z1,kind='infill')=>a.push({id,b:[x0,x1,y0,y1,z0,z1],kind});
 // Local U runs along the face, V runs inward from the face. Closed leaves recess in V.
 function doorWall(d,u0,u1,h){
  const c=d.face==='transverse'?d.centre[1]:d.centre[0],t=R.wall_thickness,w=R.door_width/2,F=R.frame_width;
  const box=(id,lo,hi,v0,v1,z0,z1,kind='infill')=>{
   if(d.face==='transverse')add(d.id+'-'+id,d.centre[0]-v1,d.centre[0]-v0,lo,hi,z0,z1,kind);
   else{const ys=[d.centre[1]+d.sign*v0,d.centre[1]+d.sign*v1].sort((a,b)=>a-b);add(d.id+'-'+id,lo,hi,...ys,z0,z1,kind);}
  };
  box('wall-left',u0,c-w-F,0,t,0,h);box('wall-right',c+w+F,u1,0,t,0,h);box('wall-over',c-w-F,c+w+F,0,t,R.door_height+F,h);
  box('jamb-left',c-w-F,c-w,0,t,0,R.door_height+F,'metal');box('jamb-right',c+w,c+w+F,0,t,0,R.door_height+F,'metal');
  box('head',c-w,c+w,0,t,R.door_height,R.door_height+F,'metal');box('closed-leaf',c-w,c+w,R.door_recess,R.door_recess+R.door_leaf_thickness,0,R.door_height,'metal');
 }
 for(const d of R.doors){
  const [x0,x1]=R[d.end+'_x'],sg=d.sign,t=R.wall_thickness;
  const range=(lo,hi)=>[sg*lo,sg*hi].sort((a,b)=>a-b);
  const band=(id,a,b,lo,hi,z0,z1)=>add(d.id+'-'+id,a,b,...range(lo,hi),z0,z1);
  // Terminal original piers form the last 2.4 m of each hall-facing enclosure wall.
  if(d.end==='entrance'){
   band('blind-hall',V.end_pier.front_x,S.piers.x[0]-S.piers.size/2,5.6,5.6+t,0,R.top.band_z);
   doorWall(d,...range(8,12),R.top.aisle_z);
  }else{
   doorWall(d,S.piers.x.at(-1)+S.piers.size/2,x1,R.top.band_z);
   band('blind-transverse',x0,x0+t,8,12,0,R.top.aisle_z);
  }
  band('outer-wall',x0,x1,12-t,12,0,R.top.aisle_z);
  const end=d.end==='entrance'?x0:x1-t;
  band('end-wall',end,end+t,8,12,0,R.top.aisle_z);
  band('roof-band',x0,x1,5.6,8,R.top.band_z-t,R.top.band_z);
  band('roof-aisle',x0,x1,8,12,R.top.aisle_z-t,R.top.aisle_z);
 }
 for(const x of N.x)for(const y of N.y)add(`new-column-${x}-${y}`,x-N.section[0]/2,x+N.section[0]/2,y-N.section[1]/2,y+N.section[1]/2,...N.z,'newcolumn');

 for(const sign of [-1,1])add('retained-inner-band'+sign,29.97,30,sign<0?-8:5.6,sign<0?-5.6:8,0,18,'stone');
 const x0=Q.x-Q.depth/2,x1=Q.x+Q.depth/2;
 add('joined-desk',x0,x1,...Q.desk_y,0,Q.desk_height-Q.top_thickness,'checkpoint');
 add('joined-top',x0,x1,...Q.desk_y,Q.desk_height-Q.top_thickness,Q.desk_height,'checkpoint');
 for(const y of Q.lane_centres_y){
  for(const sign of [-1,1]){const c=y+sign*(Q.net_width/2+Q.post_width/2);add('lane-post'+y+sign,x0,x1,c-Q.post_width/2,c+Q.post_width/2,0,Q.net_height,'checkpoint');}
  add('lane-head'+y,x0,x1,y-Q.net_width/2-Q.post_width,y+Q.net_width/2+Q.post_width,Q.net_height,Q.net_height+Q.header_height,'checkpoint');
 }
 for(const sign of [-1,1])add('elevator-jamb'+sign,E.front_x,E.leaf_x,sign<0?-E.outer_width/2:E.opening_width/2,sign<0?-E.opening_width/2:E.outer_width/2,0,E.outer_height,'stone');
 add('elevator-head',E.front_x,E.leaf_x,-E.opening_width/2,E.opening_width/2,E.opening_height,E.outer_height,'stone');
 for(const sign of [-1,1])add('elevator-closed-leaf'+sign,E.leaf_x,E.leaf_x+E.leaf_thickness,sign<0?-E.opening_width/2:0,sign<0?0:E.opening_width/2,0,E.opening_height,'metal');
 return a;
}

const all=solids(V),R=D.rooms,Q=D.checkpoint,E=D.elevator,N=D.columns;
function cutPlan(px,py,s,xlo=-30,xhi=30){
 for(const o of all.filter(o=>o.b[4]<1&&o.b[5]>1)){
  const [a,b,c,d]=o.b;if(b<=xlo||a>=xhi)continue;
  const fill=o.kind==='checkpoint'?C.orange:o.kind==='newcolumn'?'#ba956c':o.kind==='infill'?'#c6b39a':o.kind==='metal'?C.deep:C.stone;
  rect(px(Math.max(a,xlo)),py(d),(Math.min(b,xhi)-Math.max(a,xlo))*s,(d-c)*s,fill,C.ink,1,`data-element="${o.id}" data-scale="${s}"`);
 }
}
function path2(points,px,py,color=C.teal,width=2){for(let i=1;i<points.length;i++)arrow(px(points[i-1][0]),py(points[i-1][1]),px(points[i][0]),py(points[i][1]),color,width);}
function roomTint(px,py,s){for(const d of R.doors){const [a,b]=R[d.end+'_x'];rect(px(a),py(d.sign>0?12:-5.6),(b-a)*s,6.4*s,'#eee4d6','none');}}
function stripsPlan(px,py,s,x0=-30,x1=30){for(const sign of [-1,1])rect(px(x0),py(sign*S.floor_strips.abs_y+S.floor_strips.width/2),(x1-x0)*s,S.floor_strips.width*s,'#d5dace','none');}
function markerImage(x,y,w,h){out.push(`<image x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,${fs.readFileSync(path.join(dir,'OwnerMarkup01.png')).toString('base64')}"/>`);}
start('01-plan-markup','Four corner rooms close the terminal aisles','Owner yellow strokes control topology. Exact room and new-column metres below are proposals; hall remains 60 x 24 x 18.');
{
 const s=21,px=x=>170+(x+30)*s,py=y=>490-y*s;
 text(55,183,'PLAN Z 1.0 / +X right, +Y up / green: original piers / tan: new walls and four tall columns',18,C.teal);
 rect(px(-30),py(12),60*s,24*s,C.white);stripsPlan(px,py,s);roomTint(px,py,s);cutPlan(px,py,s);
 for(const r of D.routes.polylines)path2(r.points,px,py,C.teal,r.id.startsWith('column')?1.2:2);
 for(const d of R.doors){tag(px(d.end==='entrance'?-25.5:25.5),py(d.sign*9),d.id);path2([d.centre,[d.centre[0]+d.normal[0]*1.3,d.centre[1]+d.normal[1]*1.3]],px,py,C.orange,2.5);}
 for(const x of N.x)for(const y of N.y)text(px(x),py(y)+5,'N',16,C.deep,'middle',700);
 dh(px(-30),px(30),214,'60.00 overall');dv(114,py(12),py(-12),'24.00 overall');
 text(px(-30),775,'ENTRANCE -30',17,C.teal);text(px(30),775,'ELEVATOR +30',17,C.teal,'end');
 for(const x of [-19.8,-12.6,12.6,19.8]){line(px(x),py(12)-8,px(x),py(12),C.teal);text(px(x),py(12)-13,`${x}`,16,C.teal,'middle');}
 bar(170,797,s);person(1440,831,s);text(1490,818,'1.8 m',16,C.orange);
 markerImage(55,872,500,230);text(55,1126,'OwnerMarkup01 / entire unmodified source paired in package',16,C.muted);
 notes(590,867,['MARKUP MAPPING / high-confidence topology; regularized dimensions','Four large outlines -> 10.2 x 6.4 gross corner rooms, |Y|5.6..12.','Small entrance marks -> doors on X -19.8, normals +X (orange).','Inner door marks -> X26.1 / Y +/-5.6, normals toward hall.','Four central squares -> N columns, X +/-12.6 / Y +/-2.4, Z0..18.','Routes terminate before closed doors. Aisles run only X -19.8..19.8.','Cross between hall and aisles at X +/-16.8 in the open 6 m bays.','Exactly two entrance floor paths through checkpoint; no terminal bypass.'],18,32);
}
save();
start('02-rooms-closure','Transverse service doors; hall-facing inner doors','All four gross rooms: 10.20 x 6.40. No dividing wall at |Y|8. Four original terminal piers are integrated into the enclosures.');
{
 panelTitle(55,187,'P','Positive-Y rooms / mirror across Y0');
 const s=30,py=y=>445-(y-5.6)*s,p1=x=>70+(x+30)*s,p2=x=>500+(x-19.8)*s;
 for(const [px,a,b,id] of [[p1,-30,-19.8,'E+'],[p2,19.8,30,'I+']]){
  rect(px(a),py(12),(b-a)*s,6.4*s,'#eee4d6');
  out.push(`<defs><clipPath id="${id}cut"><rect x="${px(a)}" y="${py(12)}" width="${(b-a)*s}" height="${6.4*s}"/></clipPath></defs><g clip-path="url(#${id}cut)">`);cutPlan(px,py,s,a,b);out.push('</g>');
  dh(px(a),px(b),225,'10.20 gross');text(px(a),488,id+' / unknown interior',17,C.muted);
 }
 dv(840,py(12),py(5.6),'6.40 gross');
 path2([[-19.8,10],[-18.2,10]],p1,py,C.orange);path2([[26.1,5.6],[26.1,4.2]],p2,py,C.orange);
 notes(910,231,['DOOR NORMALS / closed endpoints','E+ / E- : X -19.8, Y +/-10; face +X.','Approach from remaining aisle on +X side.','I+ : X26.1, Y5.6; face -Y.','I- : X26.1, Y-5.6; face +Y.','Entrance hall faces and inner caps: blind.','No old X-25.5 / |Y|8 service doors.','Both door types: 1.20 W x 2.40 H.','Wall 0.36; recess 0.24; frame 0.12.'],18,31);
 line(44,540,1556,540,C.line);
 panelTitle(55,580,'T','Room roof step / X -25 / look +X');
 const k=36,yy=y=>85+(y-5.6)*k,zz=z=>1030-z*k;
 // Section outside the old pier: one enlarged enclosed volume under stepped closure.
 rect(yy(5.6),zz(8.4),.36*k,8.4*k,'#c6b39a');rect(yy(11.64),zz(9.2),.36*k,9.2*k,'#c6b39a');
 rect(yy(5.6),zz(8.4),2.4*k,.36*k,'#c6b39a');rect(yy(8),zz(9.2),4*k,.36*k,'#c6b39a');
 rect(yy(5.6),zz(11.2),2.4*k,2.8*k,'url(#cut)');line(yy(8),zz(9.2),yy(12),zz(9.2),C.stone,4);
 line(yy(5),zz(0),yy(12),zz(0),C.ink,2);person(yy(9.8),zz(0),k);eye(yy(5),yy(12),zz(0),k);
 dh(yy(5.6),yy(12),1070,'6.40 gross');leader(yy(8),zz(9.2),400,668,'Z9.20 soffit / closure top');
 notes(395,720,['Z8.40 band closure meets old beam.','Z8.84..9.20 aisle closure touches','beam side at |Y|8; no upper slot.','Wall and closure thickness 0.36.','No internal wall at |Y|8.','No new floor or accessible roof.','Retained coffer edges stay enclosed.'],17,32);
 text(55,1110,'Human 1.8 / eye 1.72; interior silhouette is scale only, not a usable-room claim.',16,C.muted);
 panelTitle(910,580,'L','Service door / Y +10 / look +Y');
 const q=42,xx=x=>940+(x+22)*q,z=z=>1030-z*q;
 rect(xx(-20.16),z(9.2),.36*q,(9.2-2.52)*q,'#c6b39a');rect(xx(-22),z(9.2),(22-19.8)*q,.36*q,'#c6b39a');
 rect(xx(-20.16),z(2.52),.36*q,.12*q,C.deep);rect(xx(-20.10),z(2.4),.06*q,2.4*q,C.deep);
 line(xx(-22),z(0),xx(-14),z(0),C.ink,2);person(xx(-18.4),z(0),q);eye(xx(-22),xx(-14),z(0),q);
 arrow(xx(-17),z(.25),xx(-19.15),z(.25),C.orange);
 dv(1380,z(9.2),z(0),'9.20 closure top');
 notes(1100,710,['Remaining corridor on +X.','Wall face X -19.80.','Closed leaf face X -20.04.','1.20 W / 2.40 H opening.','0.24 recess; threshold Z0.','Inner leaves |Y|5.84.'],17,32);
}
save();
start('03-retained-functions','Two checkpoint lanes and the large inner elevator','Carried forward from Revision01 without new approval. Enlarged rooms now close the old side-aisle bypass at floor level.');
{
 panelTitle(55,185,'C','Checkpoint / hall-facing elevation');
 const s=58,px=y=>395-y*s,pz=z=>480-z*s;
 for(const o of all.filter(o=>o.kind==='checkpoint')){const [a,b,c,d,e,g]=o.b;rect(px(d),pz(g),(d-c)*s,(g-e)*s,C.orange);}
 for(const y of Q.lane_centres_y){person(px(y),pz(0),s);dh(px(y+.75),px(y-.75),315,'1.50');}
 eye(px(5.6),px(-5.6),pz(0),s);dh(px(5.6),px(-5.6),524,'11.20 control line / wall to wall');
 notes(55,575,['X -24.60 / depth 0.90 / lane centres Y +/-4.65.','Lane height 2.40; overall frame height 2.58.','Joined desk 7.40 wide / top Z1.02 / posts 0.20.','End posts touch room hall faces at |Y|5.60.','Exactly two 1.50 m physical floor openings.','Capsule diameter 0.68 leaves 0.41 m on each side.','Entrance-to-near-checkpoint face: 4.95 m.'],19,33);
 panelTitle(850,185,'E','Inner elevation / look +X');
 const q=31,cx=1150,b=817,yy=y=>cx+y*q,zz=z=>b-z*q;
 rect(yy(-8),zz(18),16*q,18*q,C.pale);
 for(const sg of [-1,1]){rect(yy(sg<0?-8:5.6),zz(11.2),2.4*q,11.2*q,C.stone);rect(yy(sg<0?-8:6.2),zz(18),1.8*q,6.8*q,C.pale);}
 rect(yy(-E.outer_width/2),zz(E.outer_height),E.outer_width*q,E.outer_height*q,C.stone);rect(yy(-1.8),zz(4.2),3.6*q,4.2*q,C.deep);line(cx,zz(0),cx,zz(4.2),C.line);
 const v=E.sign_zone;rect(yy(-v.width/2),zz(v.z[1]),v.width*q,(v.z[1]-v.z[0])*q,'none',C.teal,1.5,'stroke-dasharray="8 6"');
 notes(cx-90,zz(14.8),['OPAQUE WALL','Blank future name/logo','6.0 x 6.0 reservation'],16,27,C.teal);
 person(yy(3.5),b,q);eye(yy(-5.6),yy(5.6),b,q);dv(1450,zz(18),b,'18.00 retained');dh(yy(-1.8),yy(1.8),857,'3.60 opening');
 line(44,893,1556,893,C.line);
 notes(55,940,['Retained A entrance: glazing X-30; main jamb face X-28.4; reveal X-29.0.','Datum Z5.28..5.40 and upper glazing head Z17.80 remain.','Rooms bound the checkpoint line; side aisles are reached after control.','Floor-level route study only: no detector, anti-jump or security gameplay claim.'],18,38);
 notes(900,940,['Elevator opening 3.60 W x 4.20 H; closed leaves X30.','Reveal 0.60 / front X29.40 / frame 0.40.','Remove full 2.4 x 6.2 high window and its grid.','Reservation is annotation only; no logo, cab or shaft.'],18,38);
}
save();
start('04-columns-passages','Four new columns meet the main ceiling at 18 m','Exact X +/-12.6, Y +/-2.4 and 2.40 square section are proposals. Twelve original piers retain their positions and sizes.');
{
 panelTitle(55,185,'T','Transverse section / X -12.6 / look +X');
 const s=31,py=y=>455+y*s,pz=z=>837-z*s;
 for(const o of all.filter(o=>o.b[0]<-12.6&&o.b[1]>-12.6)){const [a,b,c,d,e,g]=o.b;rect(py(c),pz(g),(d-c)*s,(g-e)*s,o.kind==='newcolumn'?'#ba956c':'url(#cut)');}
 line(py(-8),pz(18),py(8),pz(18),C.ink,3);for(const sg of [-1,1])line(py(sg*8),pz(9.2),py(sg*12),pz(9.2),C.stone,3);
 line(py(-12),pz(0),py(12),pz(0),C.ink,2);for(const y of [-4.6,0,4.6])person(py(y),pz(0),s);eye(py(-5.6),py(5.6),pz(0),s);
 dh(py(-1.2),py(1.2),886,'2.40');dh(py(-5.6),py(-3.6),886,'2.00');dh(py(3.6),py(5.6),886,'2.00');
 dv(865,pz(18),pz(0),'18.00 / ten 1.8 m humans');
 text(80,253,'Main ceiling Z18 / flush full-section contact; no capital or ceiling opening',17,C.teal);
 notes(55,944,['At both X stations: gaps measured between actual shaft faces.','Axis: Y -1.2..1.2; sides: |Y|3.6..5.6.','Centred capsule margins: axis 0.86; side passages 0.66 m.','New top Z18 exceeds beam top Z11.2 by 6.8 m.','Human 1.80 / eye 1.72 / capsule R0.34 / walk 3.6 m/s.'],18,33);
 panelTitle(940,185,'P','Pair plan / cut Z1.0');
 const k=33,xx=x=>1000+(x+15.6)*k,yy=y=>510-y*k;
 rect(xx(-15.6),yy(8),6*k,16*k,C.white);stripsPlan(xx,yy,k,-15.6,-9.6);cutPlan(xx,yy,k,-15.6,-9.6);
 for(const y of [-4.6,0,4.6])path2([[-15.5,y],[-9.7,y]],xx,yy);
 dh(xx(-13.8),xx(-11.4),813,'2.40 shaft');
 notes(1245,275,['New centres','X +/-12.6','Y +/-2.4','Original shafts','Y +/-6.8','2.40 square','height 8.40'],18,33);
 notes(940,868,['Strips stay at |Y|2.20, width 0.64; no relocation.','Four shaft-covered areas: 2.40 x 0.64 each.'],18,31);
 panelTitle(940,939,'L','Longitudinal section / Y +2.4');
 const ls=8,lx=x=>995+(x+30)*ls,lz=z=>1104-z*ls;
 line(lx(-30),lz(0),lx(30),lz(0),C.ink,2);line(lx(-30),lz(18),lx(30),lz(18),C.ink,2);
 for(const x of N.x)rect(lx(x-N.section[0]/2),lz(N.z[1]),N.section[0]*ls,(N.z[1]-N.z[0])*ls,'#ba956c');
 person(lx(0),lz(0),ls);eye(lx(-30),lx(30),lz(0),ls);
 dh(lx(N.x[0]),lx(N.x[1]),1131,'25.20 between pair centres');dv(1520,lz(18),lz(0),'18.00');
 text(950,1109,'-30',15,C.teal);text(1482,1109,'+30',15,C.teal);
}
save();
start('05-spatial-context','Entrance, inner end, full hall and the service-door approach','SVG perspective drawings from design.json; neutral diagram colours. Camera eye 1.72 m and HFOV 90 throughout.');
{
 const views=[['A','Entrance / retained portal','entrance',44,205],['B','Inner end / retained proposal','inner',824,205],['C','Whole hall / both new pairs','context',44,695],['D','Positive aisle / closed service door','aisle',824,695]];
 for(const [id,title,key,x,y] of views){panelTitle(x,y-23,id,title);perspective(V,D.drawing_cameras[key],{x,y,w:732,h:key==='context'||key==='aisle'?380:360},'view'+id);const c=D.drawing_cameras[key];text(x,y+(key==='context'||key==='aisle'?407:387),`X ${c.xyz[0]} / Y ${c.xyz[1]} / yaw ${c.yaw} / pitch +${c.pitch} / eye ${c.xyz[2]} / HFOV ${c.hfov}`,17);}
 text(44,623,'Portal main -28.4 > reveal -29.0 > glass -30; blind hall infill.',17,C.muted);
 text(824,623,'Elevator remains focal; both inner doors face the hall.',17,C.muted);
 text(44,1131,'Four tan shafts reach Z18; axial view narrows to 2.4 m at each pair.',17,C.muted);
 text(824,1131,'Door in X-19.8 cap faces this corridor; room continues to outer wall.',17,C.muted);
}
save();
fs.writeFileSync(path.join(worker,'sheets.json'),JSON.stringify(sheets,null,2)+'\n');
fs.writeFileSync(path.join(worker,'text-records.json'),JSON.stringify(textRecords,null,2)+'\n');
fs.writeFileSync(path.join(worker,'drawing-bounds.json'),JSON.stringify({scope:'Derived 2D drawing bounds only; no mesh or scene output',objects:all},null,2)+'\n');
console.log(`Generated ${sheets.length} SVG sheets`);

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
