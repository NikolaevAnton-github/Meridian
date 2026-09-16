// SVG drafting primitives and perspective adapted from ArchitectureRework01/generate.mjs.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(dir,'../../../..');
const worker=path.join(root,'Saved/OpeningLobby/FunctionalRevision01/Worker');
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
function start(id,title,sub){sheetName=id;out=[];rect(0,0,W,H,C.paper,'none');text(44,37,'MERIDIAN SQUAD   /   LOBBYFUNCTIONAL–REVISION01   /   CANDIDATE01',16,C.teal,'start',600);text(1556,37,id.slice(0,2),22,C.teal,'end',700);text(44,82,title,34,C.ink,'start',600);text(44,119,sub,18,C.muted);line(44,143,1556,143,C.line);line(44,1145,1556,1145,C.line);text(44,1176,'2D ARCHITECTURAL DRAWINGS  •  Metres  •  Functional proposals  •  Pending independent review',17,C.orange);text(1556,1176,'Owner approval required before 3D',17,C.muted,'end');}
function save(){const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Arial, sans-serif"><defs><pattern id="cut" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#c5d0c0"/><path d="M0 9L9 0" stroke="#83957f" stroke-width="1"/></pattern></defs>${out.join('\n')}</svg>`;fs.writeFileSync(path.join(dir,`${sheetName}.svg`),svg);sheets.push({name:sheetName,width:W,height:H});}
function retainedSolids(V,{full=true}={}) {
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
function tint(kind,face){const table={stone:['#75887a','#526d61','#354f47'],wall:['#b7c3b1','#93a590','#819782'],reveal:['#668078','#47665e','#2d4c47'],soffit:['#a0ad97','#7d927c','#61785f'],metal:['#394e46','#253d36','#1e312c'],checkpoint:['#465d52','#30483f','#213a32']};return (table[kind]||table.stone)[face==='x'?0:face==='z'?2:1];}
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
 const hp=inner?[28,3.3,0]:[-26.3,3.25,0],foot=P.screen(P.toCamera(hp)),head=P.screen(P.toCamera([hp[0],hp[1],1.8]));
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

// Common drawing geometry; only SVG faces are emitted, never DCC data.
function solids(V){
 const a=retainedSolids(V);const add=(id,x0,x1,y0,y1,z0,z1,kind='wall')=>a.push({id,b:[x0,x1,y0,y1,z0,z1],kind});
 const R=D.rooms,Q=D.checkpoint,E=D.elevator;
 for(const d of R.doors){
  const [x0,x1]=R[d.end+'_x'],[lo,hi]=R.abs_y.map(n=>n*d.sign).sort((a,b)=>a-b),c=R.door_centres_x[d.end];
  const w=R.door_width/2+R.frame_width,h=R.door_height+R.frame_width,t=R.wall_thickness;
  const side=d.normal_y>0?'high':'low';
  for(const edge of ['low','high']){
   const yl=edge==='low'?lo:hi-t,yh=edge==='low'?lo+t:hi;
   if(edge!==side)add(d.id+'-blind',x0,x1,yl,yh,0,R.z[1]);
   else{
    add(d.id+'-wall-left',x0,c-w,yl,yh,0,R.z[1]);add(d.id+'-wall-right',c+w,x1,yl,yh,0,R.z[1]);add(d.id+'-wall-over',c-w,c+w,yl,yh,h,R.z[1]);
    for(const sign of [-1,1])add(d.id+'-jamb'+sign,c+sign*w-(sign>0?R.frame_width:0),c+sign*w+(sign<0?R.frame_width:0),yl,yh,0,h,'metal');
    add(d.id+'-head',c-R.door_width/2,c+R.door_width/2,yl,yh,R.door_height,h,'metal');
    const face=edge==='low'?lo+R.door_recess:hi-R.door_recess;
    add(d.id+'-closed-leaf',c-R.door_width/2,c+R.door_width/2,face-(edge==='high'?R.door_leaf_thickness:0),face+(edge==='low'?R.door_leaf_thickness:0),0,R.door_height,'metal');
   }
  }
  // Cross-bay end caps and overhead closure meet existing terminal/free-pier faces.
  add(d.id+'-end0',x0,x0+t,lo+t,hi-t,0,R.z[1]);add(d.id+'-end1',x1-t,x1,lo+t,hi-t,0,R.z[1]);
  add(d.id+'-cap',x0+t,x1-t,lo+t,hi-t,R.z[1]-t,R.z[1]);
 }
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
const all=solids(V),R=D.rooms,Q=D.checkpoint,E=D.elevator;
function cutPlan(px,py,s,xlo=-30,xhi=30){
 for(const o of all.filter(o=>o.b[4]<1&&o.b[5]>1)){
  const [a,b,c,d]=o.b;if(b<=xlo||a>=xhi)continue;
  const newObj=/^[EI][+-]-/.test(o.id)||o.id.startsWith('elevator');
  rect(px(Math.max(a,xlo)),py(d),(Math.min(b,xhi)-Math.max(a,xlo))*s,(d-c)*s,o.kind==='checkpoint'?C.orange:newObj?'#c6b39a':o.kind==='metal'?C.deep:C.stone,C.ink,1,`data-element="${o.id}" data-scale="${s}"`);
 }
}
function path2(points,px,py,color=C.teal,width=2.5){for(let i=1;i<points.length;i++)arrow(px(points[i-1][0]),py(points[i-1][1]),px(points[i][0]),py(points[i][1]),color,width);}
function roomFace(x,y,s,d,showDoor){
 const [a,b]=R[d.end+'_x'],w=b-a,z=R.z[1],cx=R.door_centres_x[d.end]-a;
 rect(x,y-z*s,w*s,z*s,'#c6b39a');
 rect(x,y-(z+1)*s,w*s,1*s,C.stone); // lower part of retained beam, cropped above
 if(showDoor){rect(x+(cx-R.door_width/2-R.frame_width)*s,y-(R.door_height+R.frame_width)*s,(R.door_width+2*R.frame_width)*s,(R.door_height+R.frame_width)*s,C.deep);rect(x+(cx-R.door_width/2)*s,y-R.door_height*s,R.door_width*s,R.door_height*s,C.dark);}
 person(x+(w-.6)*s,y,s);eye(x,x+w*s,y,s);dh(x,x+w*s,y+35,`${f(w)} between existing faces`);
}
start('01-plan-circulation','Four terminal infills; the adjacent bays take the crossings','Retained: 60 x 24 x 18 hall, six free pier pairs, 11.2 central clear and two 4 m longitudinal aisles.');
{
 const s=22,px=x=>140+(x+30)*s,py=y=>530-y*s;
 rect(px(-30),py(12),60*s,24*s,C.white);
 for(const y of [5.6,-8])rect(px(-30),py(y+2.4),60*s,2.4*s,'none',C.line,1,'stroke-dasharray="7 5"');
 for(const d of R.doors){const [a,b]=R[d.end+'_x'];rect(px(a),py(d.sign>0?8:-5.6),(b-a)*s,2.4*s,'#eee4d6','none');}cutPlan(px,py,s);line(px(E.leaf_x),py(E.opening_width/2),px(E.leaf_x),py(-E.opening_width/2),C.deep,3);
 for(const d of R.doors){const c=R.door_centres_x[d.end],y=d.face==='aisle'?d.sign*8:d.sign*5.6;tag(px(c),py(d.sign*6.8),d.id);path2([[c,y+d.normal_y*1.2],[c,y]],px,py,C.orange,2);}
 for(const x of D.routes.closed_crossovers_x)for(const y of [-6.8,6.8]){line(px(x)-8,py(y)-8,px(x)+8,py(y)+8,C.orange,3);line(px(x)-8,py(y)+8,px(x)+8,py(y)-8,C.orange,3);}
 for(const y of D.routes.aisle_centres_y)path2([[-29,y],[-16.8,y],[16.8,y],[29,y]],px,py);
 for(const x of D.routes.crossing_centres_x)path2([[x,-10],[x,0],[x,10]],px,py);
 // Entrance forks before the joined line; reconverges on the hall axis after it.
 for(const y of Q.lane_centres_y)path2([[-29.3,0],[-26.6,y],[-23.3,y],[-21,0]],px,py);
 path2([[-21,0],[16.8,0],[28.8,0]],px,py);
 for(const d of R.doors){const c=R.door_centres_x[d.end];if(d.face==='aisle')path2([[c,d.sign*10],[c,d.sign*8.65]],px,py);else path2([[c,0],[c,d.sign*4.95]],px,py);}
 dh(px(-30),px(30),215,'60 m overall / +X toward elevator');dv(90,py(12),py(-12),'24 m overall');
 for(const x of S.piers.x){line(px(x),py(12)-9,px(x),py(12),C.teal);text(px(x),py(12)-20,String(x),16,C.teal,'middle');}
 text(140,181,'PLAN CUT Z 1.0 / +Y up / metres / tan = new infill / green = retained / orange = checkpoint',18,C.teal);
 text(px(-30),py(-12)+29,'ENTRANCE X -30',17,C.teal);text(px(30),py(-12)+29,'ELEVATOR X +30',17,C.teal,'end');
 for(const x of D.routes.crossing_centres_x)text(px(x),py(-12)+59,`Open 6 m bay at X ${x}`,17,C.teal,'middle');
 bar(140,895,s);person(1380,912,s);text(1420,908,'1.8 m',17,C.orange);
 notes(55,978,['CLOSED: old crossovers at X +/-27 (orange crosses). Terminal fills are deliberate route changes.','ALTERNATE: X -19.8..-13.8 and +13.8..+19.8; crossing centres +/-16.8 have 2.66 m capsule margin to pier faces.','Aisles remain |Y| 8..12, centre margin 1.66 m. Doors are closed endpoints, not traversable routes.','60 m nominal axial distance: 16.7 s at 3.6 m/s; two checkpoint approaches add lateral travel. Side aisles remain unblocked.'],18,32);
}
save();

start('02-entrance-checkpoint','One joined checkpoint, two opposite-side lanes','Proposed human-use exception: each net opening 1.50 W x 2.40 H. A entrance portal and glazing remain unchanged.');
{
 panelTitle(55,186,'P','Checkpoint plan / cut Z 1.0');
 const s=52,cx=380,top=240,px=y=>cx-y*s,py=x=>top+(x+28)*s;
 rect(px(5.96),py(-28),11.92*s,6*s,C.white);
 for(const sign of [-1,1])rect(px(sign>0?5.96:-5.6),py(-28),.36*s,5.8*s,'#c6b39a');
 for(const o of all.filter(o=>o.kind==='checkpoint'&&o.b[4]<1.1)){const [a,b,c,d,e,g]=o.b;rect(px(d),py(a),(d-c)*s,(b-a)*s,C.orange);}
 for(const y of Q.lane_centres_y){arrow(px(y),py(-27),px(y),py(-23));dot(px(y),py(Q.x),D.routes.capsule_radius*s,C.teal);dh(px(y+.75),px(y-.75),py(-28)-13,'1.50');}
 dh(px(3.7),px(-3.7),py(-28)-13,'7.40 joined desk + barrier');
 dh(px(5.6),px(-5.6),py(-22)+36,'11.20 control line / wall to wall');
 text(55,630,'X -24.60 centre; depth 0.90; end posts touch Y +/-5.60.',18);
 text(55,660,'No gap beside end posts; no desk undercut or raised threshold.',18);
 panelTitle(835,186,'E','Hall-facing checkpoint elevation / look -X');
 const sx=y=>1180-y*55,b=475,sz=z=>b-z*55;
 for(const o of all.filter(o=>o.kind==='checkpoint')){const [a,bb,c,d,e,g]=o.b;rect(sx(d),sz(g),(d-c)*55,(g-e)*55,C.orange);}
 for(const y of Q.lane_centres_y)person(sx(y),b,55);
 eye(sx(5.6),sx(-5.6),b,55);line(sx(5.6),b,sx(-5.6),b,C.ink,2);
 dv(1530,sz(2.4),b,'2.40 net');dh(sx(5.6),sx(-5.6),b+40,'11.20 overall');
 notes(835,570,['Posts 0.20; heads 0.18; overall lane height 2.58.','Desk/barrier top Z 1.02, slab 0.06; all faces join.','Each lane: 1.50 - 0.68 capsule = 0.82 total spare width.','Centred capsule margin 0.41 per side. Eye line Z 1.72.'],18,30);
 line(44,695,1556,695,C.line);panelTitle(55,735,'S','Longitudinal cut at Y +4.65 / look +Y');
 const ss=55,xx=x=>95+(x+30)*ss,zz=z=>1080-z*ss;
 rect(xx(-30),zz(5.4),.4*ss,5.4*ss,'url(#cut)');text(130,820,'Retained shoulder',16,C.teal);text(130,846,'cropped at Z 5.4',16,C.teal);
 rect(xx(Q.x-Q.depth/2),zz(Q.net_height+Q.header_height),Q.depth*ss,Q.header_height*ss,'url(#cut)');
 line(xx(-30),zz(0),xx(-22.2),zz(0),C.ink,2);person(xx(Q.x),zz(0),ss);eye(xx(-30),xx(-22.2),zz(0),ss);
 dh(xx(Q.x-Q.depth/2),xx(Q.x+Q.depth/2),790,'0.90');dv(580,zz(2.4),zz(0),'2.40');
 notes(690,782,['Retained A: glazing/entrance leaves X -30; portal main face -28.4.','Retained datum Z 5.28..5.40; upper glazing head 17.80.','Entry-to-checkpoint near face: 4.95 m from X -30.','Lane floor flush Z 0; no operational detector or security claim.','Old single lane Y -1.05 becomes Y +/-4.65; X remains -24.60.','Old station Y +0.95 becomes one centred 7.40 m composition.','Aisles |Y| 8..12 remain open. This is central-passage control only.','The wider checkpoint interpretation remains an owner decision.'],18,36);
}
save();

start('03-inner-elevator','A large elevator below an opaque upper wall','Proposed opening 3.60 x 4.20; remove the full old high window, all mullions and transoms. No cab, shaft or branding.');
{
 panelTitle(55,184,'E','Inner end elevation / look +X');
 const s=32,cx=450,b=845,px=y=>cx+y*s,pz=z=>b-z*s;
 rect(px(-12),pz(9.2),24*s,9.2*s,C.pale);rect(px(-8),pz(18),16*s,8.8*s,C.pale);
 for(const sign of [-1,1]){rect(px(sign<0?-8:5.6),pz(11.2),2.4*s,11.2*s,C.stone);rect(px(sign<0?-8:6.2),pz(18),1.8*s,6.8*s,C.pale);}
 rect(px(-E.outer_width/2),pz(E.outer_height),E.outer_width*s,E.outer_height*s,C.stone);
 rect(px(-E.opening_width/2),pz(E.opening_height),E.opening_width*s,E.opening_height*s,C.deep);line(cx,b,cx,pz(E.opening_height),C.line,1.4);
 const q=E.sign_zone;rect(px(-q.width/2),pz(q.z[1]),q.width*s,(q.z[1]-q.z[0])*s,'none',C.teal,1.6,'stroke-dasharray="8 6"');
 ['OPAQUE WALL','Future sign zone','6.0 x 6.0'].forEach((t,i)=>text(cx,pz(14.5)+i*25,t,17,C.teal,'middle')); // moved to centered labels below
 person(px(3.4),b,s);eye(px(-5.6),px(5.6),b,s);
 dh(px(-E.opening_width/2),px(E.opening_width/2),b+35,'3.60 opening');dv(860,pz(18),b,'18 retained');
 text(70,932,'1.8 m human / eye Z 1.72; elevator leaves closed.',18,C.orange);
 notes(55,980,['Upper zone is a drafting reservation on a flush opaque wall.','Dashed boundary is annotation only; no new frame or panel joint.','The 2.4 x 6.2 window at Z 11.4..17.6 is entirely infilled.','Nearby room doors face the hall; see sheet 04 for all four faces.'],18,32);
 panelTitle(950,184,'P','Elevator plan / cut Z 1.0');
 const ss=90,pp=y=>1225+y*ss,py=x=>355+(x-30)*ss;
 rect(pp(-2.8),py(30),5.6*ss,8,C.pale);for(const o of all.filter(o=>o.id.startsWith('elevator')&&o.b[4]===0)){const [a,bb,c,d]=o.b;rect(pp(c),py(a),(d-c)*ss,(bb-a)*ss,o.kind==='metal'?C.deep:C.stone);}
 dh(pp(-E.opening_width/2),pp(E.opening_width/2),405,`${E.opening_width.toFixed(2)} nominal opening`);dh(pp(-E.outer_width/2),pp(E.outer_width/2),445,`${E.outer_width.toFixed(2)} outer frame`);
 notes(950,495,['Front X 29.40; closed leaf plane X 30.00.','Reveal 0.60; no cab or shaft depth specified.','Frame 0.40; leaf 0.06 behind X 30 datum.'],18,30);
 panelTitle(950,640,'S','Vertical section at Y 0 / look -Y');
 const k=65,xx=x=>1100+(x-29.4)*k,zz=z=>1055-z*k;
 rect(xx(E.front_x),zz(E.outer_height),(E.leaf_x-E.front_x)*k,E.frame_width*k,'url(#cut)');rect(xx(E.leaf_x),zz(E.opening_height),E.leaf_thickness*k,E.opening_height*k,C.deep);
 line(960,zz(0),1220,zz(0),C.ink,2);person(995,zz(0),k);eye(960,1210,zz(0),k);
 dv(1260,zz(E.opening_height),zz(0),`${E.opening_height.toFixed(2)} opening`);dh(xx(E.front_x),xx(E.leaf_x),720,`${f(E.leaf_x-E.front_x).toFixed(2)} reveal`);
 notes(1330,815,['4.60 outer','head Z','Flush Z 0','threshold','Interior','deferred'],17,32);
}
save();

start('04-room-faces','Hall and aisle doors reverse at opposite ends','Four closed recessed doors, each 1.20 x 2.40; visible enclosures only. No usable interiors or stair circulation are asserted.');
{
 const s=31,b=600;
 const cols=[{x:60,d:R.doors[0],door:false,title:'ENTRANCE / HALL',sub:'E+ and E-: both blind'}, {x:425,d:R.doors[0],door:true,title:'ENTRANCE / AISLE',sub:'E+ faces +Y; E- faces -Y'}, {x:790,d:R.doors[2],door:true,title:'INNER / HALL',sub:'I+ faces -Y; I- faces +Y'}, {x:1190,d:R.doors[2],door:false,title:'INNER / AISLE',sub:'I+ and I-: both blind'}];
 for(const c of cols){text(c.x,190,c.title,20,C.teal,'start',600);text(c.x,225,c.sub,17);roomFace(c.x+20,b,s,c.d,c.door);text(c.x,682,c.d.end==='entrance'?'X -28.8 to -22.2':'X 22.2 to 29.97',17,C.teal);}
 text(60,276,'Elevation abscissa = increasing X in all diagrams; face normal is explicit above. Beam cropped at top.',18,C.muted);
 line(44,718,1556,718,C.line);panelTitle(55,759,'P','Door reveal / horizontal cut at Z 1.0');
 const sc=160,cx=295,yy=y=>835+y*sc,xx=x=>cx+x*sc;
 // Local coordinate U along wall, V into enclosure. All four mirror this detail.
 rect(xx(-1.3),yy(0),(.7-R.frame_width)*sc,.36*sc,'url(#cut)');rect(xx(.6+R.frame_width),yy(0),(.7-R.frame_width)*sc,.36*sc,'url(#cut)');
 for(const sign of [-1,1])rect(xx(sign<0?-.72:.6),yy(0),.12*sc,.36*sc,C.deep);
 rect(xx(-.6),yy(.24),1.2*sc,.06*sc,C.dark);
 dh(xx(-.6),xx(.6),805,'1.20 leaf / opening');dv(545,yy(0),yy(.24),'0.24 recess');
 text(100,946,'ACCESS SIDE / flush wall face V 0',17,C.teal);text(100,987,'Wall 0.36; frame 0.12; leaf 0.06; threshold Z 0.',17);
 notes(55,1040,['Entrance leaf |Y| 7.76; inner leaf |Y| 5.84.','Opposite wall is blind. Centre X: entrance -25.50; inner +26.085.'],18,32);
 panelTitle(720,759,'T','Transverse enclosure section / door centre');
 const t=24,tx=y=>745+(y-5.6)*t,tz=z=>1080-z*t;
 rect(tx(5.6),tz(8.4),2.4*t,.36*t,'url(#cut)');rect(tx(5.6),tz(8.04),.36*t,8.04*t,'url(#cut)');rect(tx(7.64),tz(8.04),.36*t,8.04*t,'url(#cut)');
 rect(tx(5.6),tz(11.2),2.4*t,2.8*t,C.stone); // section below depicts blind envelope; door opening called out
 rect(tx(5.6),tz(2.52),.36*t,2.52*t,C.paper,'none');rect(tx(5.6),tz(2.52),.36*t,.12*t,C.deep);rect(tx(5.84),tz(2.4),.06*t,2.4*t,C.dark);
 line(tx(5.6),tz(0),tx(12),tz(0),C.ink,1.6);person(tx(10),tz(0),t);eye(tx(5),tx(12),tz(0),t);
 dh(tx(8),tx(12),1112,'4.00 aisle');
 notes(1020,813,['Inner +Y door section shown; mirror for I-.','Entrance E+/E- place door on the aisle wall.','2.40 gross band |Y| 5.6..8.0.','Walls/cap 0.36; new top meets beam at Z 8.40.','Retained beam Z 8.40..11.20; side soffit Z 9.20.','End caps abut existing pier/end-wall faces.','No floor-level slots at these joints.','Band is not an engineered stair envelope.'],18,34);
}
save();

start('05-spatial-context','Retained monumental frame, bounded functional additions','Architectural perspective drawings from common dimensions. Neutral diagram colours; these are not in-engine evidence.');
panelTitle(44,184,'A','Entrance and filled terminal bay');panelTitle(824,184,'B','Elevator and hall-facing terminal doors');
perspective(V,D.drawing_cameras.entrance,{x:44,y:210,w:732,h:412},'entry');
perspective(V,D.drawing_cameras.inner,{x:824,y:210,w:732,h:412},'inner');
notes(44,658,['X -12.6 / Y +3.5 / eye 1.72 / yaw 180 / pitch +15 / HFOV 90.','Retained portal: main face -28.4 > reveal -29.0 > glazing -30.','Blind hall infill meets shaft and beam; aisle door is behind it.'],17,29);
notes(824,658,['X +16 / Y 0 / eye 1.72 / yaw 0 / pitch +20 / HFOV 90.','Large elevator anchors the opaque wall; no high-window grid.','Infill doors sit inside the hall wall with 0.24 m recess.'],17,29);
line(44,751,1556,751,C.line);
function crop(file,x,y,w,h,vb){const bytes=fs.readFileSync(path.join(root,file));out.push(`<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="${vb}" preserveAspectRatio="xMidYMid slice"><image width="1920" height="1080" href="data:image/png;base64,${bytes.toString('base64')}"/></svg>`);}
perspective(V,D.drawing_cameras.context,{x:44,y:795,w:360,h:203},'axial');
notes(44,1035,['Full-hall context / C1 drawing pose','X -19 / Y 0 / eye 1.72 / pitch 0 / HFOV 90'],16,27);
crop('Saved/OpeningLobby/ArchitectureReworkA01/Worker/C3-context-90.png',435,795,260,203,'500 140 900 700');
crop('Saved/OpeningLobby/ArchitectureReworkA01/Worker/C1-90.png',1015,795,240,203,'650 220 650 580');
tag(560,890,'1');tag(515,849,'2');tag(1138,820,'3');tag(1138,925,'4');
notes(710,802,['CURRENT / C3 crop','1. Projecting main jamb.','2. Beam meets shaft.','PROPOSED','Close below beam.','Retain depth hierarchy.'],16,29);
notes(1280,802,['CURRENT / C1 crop','3. Old high window.','4. Tiny isolated door.','OWNER DIRECTION','Replace both; opaque','wall and large elevator.'],16,29);
text(435,1035,'Visible evidence: numbered captures. Hidden returns: inferred, medium confidence.',16,C.muted);
text(435,1062,'New infill, checkpoint and elevator metres: design proposals, not measurements from art.',16,C.muted);
text(44,1110,'Art pair and A sheets inspected. Source crops preserve captured pixels; annotations are separate. See README evidence mapping.',17,C.muted);
save();

fs.writeFileSync(path.join(worker,'sheets.json'),JSON.stringify(sheets,null,2)+'\n');
fs.writeFileSync(path.join(worker,'text-records.json'),JSON.stringify(textRecords,null,2)+'\n');
fs.writeFileSync(path.join(worker,'drawing-bounds.json'),JSON.stringify({scope:'Derived 2D drawing bounds only; not a mesh/scene deliverable',objects:all},null,2)+'\n');
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
