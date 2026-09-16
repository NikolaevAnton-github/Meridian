// Local vector drawing generator. No DCC, network, or external packages.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../../..');
const evidence=path.join(root,'Saved/OpeningLobby/ScaleReview01');
fs.mkdirSync(evidence,{recursive:true});
const D=JSON.parse(fs.readFileSync(path.join(dir,'schedule.json'),'utf8'));
const N=D.architecture.candidate,O=D.architecture.old,H=D.human_elements;
const end=N.length/2,half=N.width/2,pier=N.pier_size;
const firstFace=N.pier_x[0]-pier/2,aisleY=half-N.aisle_clear/2;
const checkpointCrossoverX=-27;
const C={paper:'#f7f5ef',ink:'#233637',stone:'#536969',pale:'#d9e2dc',glass:'#b5d9df',teal:'#18776d',orange:'#b85a27',line:'#8a9a93'};
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const num=n=>Number(n.toFixed(3));
let v=[];
function line(x1,y1,x2,y2,color=C.ink,w=1.5,dash=''){v.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${w}" ${dash?`stroke-dasharray="${dash}"`:''}/>`);}
function rect(x,y,w,h,fill=C.pale,stroke=C.ink,sw=1.5){v.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);}
function text(x,y,s,size=20,color=C.ink,anchor='start'){v.push(`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" text-anchor="${anchor}">${esc(s)}</text>`);}
function notes(x,y,arr,size=20){arr.forEach((s,i)=>text(x,y+i*30,s,size));}
function dot(x,y,r=5,color=C.orange){v.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${color}"/>`);}
function arrow(x,y,xx,yy,color=C.teal){line(x,y,xx,yy,color,2);const a=Math.atan2(yy-y,xx-x);line(xx,yy,xx-10*Math.cos(a-.45),yy-10*Math.sin(a-.45),color,2);line(xx,yy,xx-10*Math.cos(a+.45),yy-10*Math.sin(a+.45),color,2);}
function dh(x1,x2,y,label){line(x1,y,x2,y,C.teal);for(const x of [x1,x2])line(x-4,y+6,x+4,y-6,C.teal);text((x1+x2)/2,y-9,label,19,C.teal,'middle');}
function dv(x,y1,y2,label){line(x,y1,x,y2,C.teal);for(const y of [y1,y2])line(x-5,y+4,x+5,y-4,C.teal);v.push(`<text transform="translate(${x-9},${(y1+y2)/2}) rotate(-90)" text-anchor="middle" font-size="19" fill="${C.teal}">${esc(label)}</text>`);}
function person(x,b,s){const h=D.human_reference.height*s;dot(x,b-h+.13*s,.13*s,C.orange);line(x,b-h+.29*s,x,b-.72*s,C.orange,.16*s);line(x,b-1.3*s,x-.27*s,b-.84*s,C.orange,.09*s);line(x,b-1.3*s,x+.27*s,b-.84*s,C.orange,.09*s);line(x,b-.72*s,x-.22*s,b,C.orange,.11*s);line(x,b-.72*s,x+.22*s,b,C.orange,.11*s);}
function eye(x1,x2,b,s){line(x1,b-D.human_reference.eye_height*s,x2,b-D.human_reference.eye_height*s,C.orange,1.5,'7 5');}
function bar(x,y,s,metres=10){for(let i=0;i<2;i++)rect(x+i*metres*s/2,y,metres*s/2,8,i?C.paper:C.ink);text(x,y+32,'0',17);text(x+metres*s,y+32,`${metres} m`,17,C.ink,'end');}
function start(id,title,sub,h=1000){v=[];rect(0,0,1600,h,C.paper,'none');text(50,48,`LOBBYSCALE–REVIEW01  /  ${id}`,18,C.teal);text(50,91,title,32);text(50,127,sub,19);line(50,149,1550,149,C.line);line(50,h-64,1550,h-64,C.line);text(50,h-30,'PENDING OWNER APPROVAL  •  Dimensioned proposal / metres  •  Schematic, not a gameplay prediction',18,C.orange);}
const sheets=[];
function save(name,h=1000){const svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="${h}" viewBox="0 0 1600 ${h}" font-family="Arial, sans-serif">${v.join('\n')}</svg>`;fs.writeFileSync(path.join(dir,`${name}.svg`),svg);sheets.push({name,height:h});}
function section(a,cx,b,s,{people=true,detail=true}={}){
 const px=y=>cx+y*s,pz=z=>b-z*s;
 line(px(-a.width/2),b,px(a.width/2),b,C.ink,3);
 for(const sign of [-1,1]){
  const lo=sign<0?-a.width/2:a.pier_y+a.pier_size/2;
  line(px(lo),pz(a.aisle_height),px(lo+a.aisle_clear),pz(a.aisle_height),C.ink,3);
  line(px(sign*a.width/2),b,px(sign*a.width/2),pz(a.aisle_height),C.ink,3);
  rect(px(sign*a.pier_y-a.pier_size/2),pz(a.shaft_height),a.pier_size*s,a.shaft_height*s,C.stone);
  rect(px(sign*a.pier_y-a.lintel_width/2),pz(a.lintel_underside+a.lintel_depth),a.lintel_width*s,a.lintel_depth*s,C.stone);
  rect(px(sign*a.pier_y-a.lintel_width/2),pz(a.height),a.lintel_width*s,(a.height-a.lintel_underside-a.lintel_depth)*s,C.pale);
 }
 line(px(-a.pier_y-a.pier_size/2),pz(a.height),px(a.pier_y+a.pier_size/2),pz(a.height),C.ink,3);
 if(people){person(cx,b,s);person(px(a.width/2-a.aisle_clear/2),b,s);eye(px(-a.width/2),px(a.width/2),b,s);}
 if(detail){dh(px(-a.width/2),px(a.width/2),b+60,`${a.width} overall`);dh(px(-a.central_clear/2),px(a.central_clear/2),pz(a.height)-28,`${a.central_clear} central clear`);dv(px(-a.width/2)-45,pz(a.height),b,`${a.height} central height`);}
}
function elevation(kind,cx,b,s,compact=false){
 const a=N,f=D.end_fields.candidate,px=y=>cx+y*s,pz=z=>b-z*s;
 // Interior end wall only; foreground piers are omitted so the end face stays readable.
 rect(px(-a.width/2),pz(a.aisle_height),a.width*s,a.aisle_height*s,C.pale);
 rect(px(-a.pier_y-a.pier_size/2),pz(a.height),(2*a.pier_y+a.pier_size)*s,(a.height-a.aisle_height)*s,C.pale);
 for(const sign of [-1,1]){rect(px(sign*a.pier_y-a.pier_size/2),pz(a.height),a.pier_size*s,a.height*s,C.stone);line(px(sign*a.width/2),pz(a.aisle_height),px(sign*(a.pier_y+a.pier_size/2)),pz(a.aisle_height));}
 const gw=kind==='inner'?f.inner_window_width:f.entrance_field_width;
 const sill=kind==='inner'?f.inner_window_sill:f.upper_sill;
 const gh=kind==='inner'?f.inner_window_height:f.upper_height;
 rect(px(-gw/2),pz(sill+gh),gw*s,gh*s,C.glass);
 for(let i=1;i<4;i++)line(px(-gw/2+gw*i/4),pz(sill),px(-gw/2+gw*i/4),pz(sill+gh),C.ink,1);
 for(let i=1;i<(kind==='inner'?2:5);i++)line(px(-gw/2),pz(sill+gh*i/(kind==='inner'?2:5)),px(gw/2),pz(sill+gh*i/(kind==='inner'?2:5)),C.ink,1);
 if(kind==='inner'){
  rect(px(-H.inner_door.candidate_frame_width/2),pz(H.inner_door.candidate_frame_height),H.inner_door.candidate_frame_width*s,H.inner_door.candidate_frame_height*s,C.stone);
  rect(px(-H.inner_door.candidate_width/2),pz(H.inner_door.candidate_height),H.inner_door.candidate_width*s,H.inner_door.candidate_height*s,C.ink);
 }
 else{
  rect(px(-gw/2),pz(f.entry_field_height),gw*s,f.entry_field_height*s,C.glass);
  const w=H.entrance_leaves.candidate_leaf_width,h=H.entrance_leaves.candidate_leaf_height;
  rect(px(-w),pz(h),w*s*2,h*s,'none');line(cx,b,cx,pz(h));
  // Looking -X reverses screen Y: station at +Y is on screen left.
  const st=H.station,de=H.detector;
  rect(px(-st.y-st.width_y/2),pz(st.body_height),st.width_y*s,st.body_height*s,C.stone);
  rect(px(-st.y-st.worktop_width_y/2),pz(st.worktop_height),st.worktop_width_y*s,st.worktop_thickness*s,C.ink);
  const ex=-de.y,ew=de.clear_width+2*de.post_width;
  rect(px(ex-ew/2),pz(de.clear_height),de.post_width*s,de.clear_height*s,C.stone);
  rect(px(ex+ew/2-de.post_width),pz(de.clear_height),de.post_width*s,de.clear_height*s,C.stone);
  rect(px(ex-ew/2),pz(de.clear_height+de.header_depth),ew*s,de.header_depth*s,C.stone);
 }
 person(px(-3.6),b,s);eye(px(-a.width/2),px(a.width/2),b,s);
 if(!compact){dh(px(-a.width/2),px(a.width/2),b+60,`${a.width} overall`);dh(px(-gw/2),px(gw/2),pz(sill+gh)-22,`${gw} glazing width`);dv(px(-a.width/2)-45,pz(a.height),b,`${a.height} central height`);}
}

start('01','Plan / six paired piers and continuous circulation','Horizontal cut below lintels. +X runs from entrance (left) to the inner end (right).');
{
 const s=20,px=x=>800+x*s,py=y=>490-y*s;
 rect(px(-N.length/2),py(N.width/2),N.length*s,N.width*s,'none',C.ink,3);
 for(const y of [-N.floor_strip_y,N.floor_strip_y])rect(px(-30),py(y+N.floor_strip_width/2),N.length*s,N.floor_strip_width*s,C.pale,'none');
 for(const y of [-N.pier_y,N.pier_y])for(const x of N.pier_x)rect(px(x-N.pier_size/2),py(y+N.pier_size/2),N.pier_size*s,N.pier_size*s,C.stone);
 for(const y of [-aisleY,aisleY]){arrow(px(-27),py(y),px(27),py(y));text(px(0),py(y)-10,`${N.aisle_clear} m continuous ${y>0?'+Y':'-Y'} aisle`,18,C.teal,'middle');}
 arrow(px(-27),py(10),px(-27),py(-10));arrow(px(27),py(-10),px(27),py(10));
 const st=H.station,de=H.detector;
 rect(px(st.x-st.worktop_depth_x/2),py(st.y+st.worktop_width_y/2),st.worktop_depth_x*s,st.worktop_width_y*s,C.orange);
 for(const sign of [-1,1])rect(px(de.x-de.depth/2),py(de.y+sign*(de.clear_width/2+de.post_width/2)+de.post_width/2),de.depth*s,de.post_width*s,C.orange);
 const gw=D.end_fields.candidate.entrance_field_width,ew=H.entrance_leaves.candidate_leaf_width*H.entrance_leaves.candidate_leaf_count;
 line(px(-end),py(-gw/2),px(-end),py(gw/2),C.glass,8);line(px(-end),py(-ew/2),px(-end),py(ew/2),C.orange,5);
 line(px(end),py(-H.inner_door.candidate_width/2),px(end),py(H.inner_door.candidate_width/2),C.orange,7);
 for(const c of D.cameras){const [x,y]=c.xyz,a=c.yaw*Math.PI/180;dot(px(x),py(y));arrow(px(x),py(y),px(x)+42*Math.cos(a),py(y)-42*Math.sin(a),C.orange);text(px(x)+7,py(y)+28,c.id,19,C.orange);}
 line(px(-30),py(0),px(30),py(0),C.line,1,'8 8');arrow(1420,490,1420,447,C.ink);text(1420,429,'A',20,C.ink,'middle');
 line(px(4.2),py(12)+5,px(4.2),py(-12)-5,C.line,1,'8 8');text(px(4.2),py(-12)+30,'B → +X',18,C.ink,'middle');
 dh(px(-30),px(30),190,'60 m overall');
 for(let i=0;i<N.pier_x.length;i++){const x=N.pier_x[i];text(px(x),py(N.pier_y)-35,`${i+1} / X ${x}`,17,C.ink,'middle');}
 dh(px(-21),px(-12.6),226,'8.4 pitch');dh(px(-19.8),px(-13.8),760,'6 clear gap');
 dv(130,py(12),py(-12),'24 overall');dv(1470,py(5.6),py(-5.6),'11.2 central clear');
 text(185,795,'ENTRANCE  X −30',20);text(1170,795,'INNER END  X +30',20);
 notes(50,840,['Piers: 2.4 × 2.4 m at Y ±6.8; end-wall to nearest pier face: 7.8 m.', 'Orange: proposed human-size elements and cameras. Checkpoint detail: sheet 06.', 'Aisle centres Y ±10; end crossover routes X ±27. Route lines are spatial proposals.'],19);
 bar(1270,855,s,5);
}
save('01-plan');

start('02','Longitudinal section A / central aisle','Y=0 looking +Y. Six piers and the continuous +Y lintel are projected beyond the section plane.');
{
 const s=20,b=680,px=x=>800+x*s,pz=z=>b-z*s;
 rect(px(-end),pz(N.height),N.length*s,N.height*s,'none',C.ink,3);
 rect(px(-end),pz(N.height),N.length*s,(N.height-N.lintel_underside-N.lintel_depth)*s,C.pale);
 rect(px(-end),pz(N.lintel_underside+N.lintel_depth),N.length*s,N.lintel_depth*s,C.stone);
 for(const x of N.pier_x){rect(px(x-pier/2),pz(N.shaft_height),pier*s,N.shaft_height*s,C.pale);text(px(x),b+28,`X ${x}`,17,C.ink,'middle');}
 line(px(-30),pz(N.aisle_height),px(30),pz(N.aisle_height),C.teal,1,'7 5');
 eye(px(-30),px(30),b,s);person(px(-5),b,s);
 for(const c of D.cameras){dot(px(c.xyz[0]),pz(c.xyz[2]),4);text(px(c.xyz[0]),pz(c.xyz[2])-18,c.id,18,C.orange);}
 const f=D.end_fields.candidate;
 line(px(-30),pz(f.upper_sill),px(-30),pz(f.upper_sill+f.upper_height),C.glass,8);
 line(px(30),pz(f.inner_window_sill),px(30),pz(f.inner_window_sill+f.inner_window_height),C.glass,8);
 line(px(-30),b,px(-30),pz(H.entrance_leaves.candidate_leaf_height),C.orange,6);line(px(30),b,px(30),pz(H.inner_door.candidate_height),C.orange,6);
 // Checkpoint is off the Y=0 cut and intentionally not superimposed on this projection.
 dh(px(-30),px(30),270,'60 overall');dv(140,pz(18),b,'18 central height');dv(1460,pz(8.4),b,'8.4 underside / shaft');
 dv(1515,pz(11.2),pz(8.4),'2.8 lintel');dh(px(-30),px(-22.2),735,'7.8 end clear');dh(px(-19.8),px(-13.8),735,'6 clear');dh(px(-21),px(-12.6),780,'8.4 bay pitch');
 notes(60,835,['Projected piers are pale; continuous lintel is dark. Dashed teal: side-aisle ceiling Z 9.2.', 'Human: 1.8 m. Orange dashed eye line: Z 1.72 m; C3 is projected from Y +3.5.', 'Upper infill and ceiling construction are estimates; roof build-up and external connections are unresolved.'],19);bar(1250,845,s,10);
}
save('02-longitudinal');

start('03','Transverse section B / architectural hierarchy','X=+4.2 through a pier pair, looking +X. All human references share the geometry scale.');
section(N,620,775,30);
{
 const s=30,px=y=>620+y*s,pz=z=>775-z*s;
 dh(px(-12),px(-8),875,'4 aisle');dh(px(-8),px(-5.6),875,'2.4 pier');dh(px(8),px(12),875,'4 aisle');
 dv(1070,pz(9.2),775,'9.2 aisle ceiling');dv(1115,pz(8.4),775,'8.4 underside');
 notes(1190,240,['CENTRAL VOLUME','18 m ceiling','11.2 m clear span','','MASSIVE STONE','2.4 m square pier','8.4 m shaft','2.4 × 2.8 m lintel','','HUMAN REFERENCE','1.8 m standing','1.72 m eye line'],20);
 text(260,918,'4 + 2.4 + 11.2 + 2.4 + 4 = 24 m',20,C.teal);bar(1210,835,s,5);
}
save('03-transverse');

for(const [kind,id,title] of [['inner','04','Inner end elevation E1'],['entrance','05','Entrance elevation E2']]){
 start(id,title,kind==='inner'?'At X=+30 looking +X. Destination beyond the single door remains unspecified.':'At X=−30 looking −X. Checkpoint projected from X=−24.6; +Y is screen left.');
 elevation(kind,595,780,30);
 const f=D.end_fields.candidate;
 if(kind==='inner')notes(1110,220,['ARCHITECTURAL FIELD',`Window: ${f.inner_window_width} × ${f.inner_window_height} m`,`Sill Z ${f.inner_window_sill}; head Z ${num(f.inner_window_sill+f.inner_window_height)}`,'Old: 1.2 × 3.1; sill 5.7','','PROPOSED EXCEPTION','Door leaf: 1.04 × 2.18 m','Old → candidate: unchanged','Frame: 1.22 × 2.32 m','Destination: unspecified','','HUMAN / SAME SCALE','1.8 m person; eye Z 1.72','','Both side aisles terminate','at the end wall; connections','beyond it remain unresolved.'],19);
 else notes(1110,220,['ARCHITECTURAL FIELDS',`Upper: ${f.entrance_field_width} × ${f.upper_height} m`,`Sill Z ${f.upper_sill}; head Z ${num(f.upper_sill+f.upper_height)}`,`Lower: ${f.entrance_field_width} × ${f.entry_field_height} m`,'Old: 2.6 × 6.2 / 2.6 × 2.64','','PROPOSED EXCEPTIONS','2 entrance leaves:','1.04 × 2.64 m each','Fixed sidelights + overlight','Old operable sizes: unknown','','Checkpoint remains small:','detector clear 1.14 × 2.28 m','worktop Z 1.02 m','See sheet 06 for dimensions.'],19);
 text(240,897,'Stone end bands align with Y ±6.8 pier rows. Foreground piers omitted.',19);
 save(kind==='inner'?'04-inner-elevation':'05-entrance-elevation');
}

start('06','Checkpoint / human-size exceptions','Local checkpoint sizes and Y spacing retained as a proposal. Entrance glazing is doubled independently.');
{
 const s=25,px=x=>150+(x+30)*s,py=y=>530-y*s;
 rect(px(-end),py(half),(end+N.pier_x[0]+pier/2+1)*s,N.width*s,'none');
 for(const y of [-N.pier_y,N.pier_y])rect(px(firstFace),py(y+pier/2),pier*s,pier*s,C.stone);
 for(const y of [-aisleY,aisleY])arrow(px(-28),py(y),px(-20.5),py(y));arrow(px(checkpointCrossoverX),py(aisleY),px(checkpointCrossoverX),py(-aisleY));
 const st=H.station,de=H.detector;
 rect(px(st.x-st.worktop_depth_x/2),py(st.y+st.worktop_width_y/2),st.worktop_depth_x*s,st.worktop_width_y*s,C.orange);
 for(const sign of [-1,1])rect(px(de.x-de.depth/2),py(de.y+sign*(de.clear_width/2+de.post_width/2)+de.post_width/2),de.depth*s,de.post_width*s,C.orange);
 line(px(-30),py(-2.6),px(-30),py(2.6),C.glass,8);line(px(-30),py(-1.04),px(-30),py(1.04),C.orange,5);
 arrow(px(-29),py(de.y),px(-23),py(de.y),C.orange);
 dh(px(-30),px(-24.6),195,'5.4 to checkpoint centre');dv(95,py(12),py(-12),'24 hall width');
 text(155,870,'End plan / 25 px per metre',18);text(440,290,'+Y aisle',19,C.teal);text(440,790,'−Y aisle',19,C.teal);
 notes(440,370,['Pier front X −22.2','Checkpoint X −24.6','Worktop back X −24.125','Clear to pier front: 1.925 m','',`Crossover X ${checkpointCrossoverX.toString().replace('-', '−')}:`,`${num(st.x-st.worktop_depth_x/2-checkpointCrossoverX)} m to worktop front`,'Both side aisles: 4 m','','Detector centre Y −1.05','Station centre Y +0.95','Local spacing unchanged'],18);
 // Detail looking -X: +Y to left. A single common scale for human and equipment.
 const ds=110,b=550,cx=1180,q=y=>cx-y*ds,z=h=>b-h*ds;
 rect(q(st.y+st.width_y/2),z(st.body_height),st.width_y*ds,st.body_height*ds,C.stone);
 rect(q(st.y+st.worktop_width_y/2),z(st.worktop_height),st.worktop_width_y*ds,st.worktop_thickness*ds,C.ink);
 const ew=de.clear_width+2*de.post_width;
 for(const sign of [-1,1])rect(q(de.y+sign*(de.clear_width/2+de.post_width/2)+de.post_width/2),z(de.clear_height),de.post_width*ds,de.clear_height*ds,C.stone);
 rect(q(de.y+ew/2),z(de.clear_height+de.header_depth),ew*ds,de.header_depth*ds,C.stone);
 person(q(de.y),b,ds);eye(900,1500,b,ds);
 dh(q(st.y+st.width_y/2),q(st.y-st.width_y/2),600,'2.2 body width');dh(q(de.y+de.clear_width/2),q(de.y-de.clear_width/2),245,'1.14 clear');dv(1490,z(2.28),b,'2.28 clear');
 notes(880,660,['Equipment elevation / 110 px per metre','Detector: outer 1.46 W × 2.42 H × 0.55 D','Station body: 0.85 X × 2.2 Y × 0.96 Z','Worktop: 0.95 X × 2.3 Y; top Z 1.02','Old → candidate: all these sizes unchanged','1.8 m person / eye Z 1.72, same detail scale','Nominal capsule clearance: 1.14 − 0.68 = 0.46 m','No operational screening or external access implied.'],19);
}
save('06-checkpoint');

start('07','Old / candidate at one common drawing scale','Both sections: 30 pixels per metre, same floor datum and identical 1.8 m people. No rescaling between panels.');
section(O,320,790,30,{detail:false});section(N,1060,790,30,{detail:false});
text(140,190,'REJECTED LAYOUT02',24,C.orange);text(730,190,'EXACT 2× ARCHITECTURAL CANDIDATE',24,C.teal);
notes(140,260,['30 × 12 × 9 m envelope','4.2 m shaft / 2 m aisles','9 / 1.8 = 5 human heights'],21);
text(1060,220,'60 × 24 × 18 m envelope',21,C.ink,'middle');
dh(140,500,840,'12 m');dh(700,1420,840,'24 m');dv(95,520,790,'9 m');dv(1490,250,790,'18 m');
text(170,890,'Eye Z 1.72',20,C.orange);text(735,890,'18 / 1.8 = 10 human heights; eye remains Z 1.72',20,C.orange);save('07-common-scale');

// One review board embeds the original PNG bytes, without cropping, repainting or annotations on the art.
const approval=JSON.parse(fs.readFileSync(path.join(root,'Assets/Concepts/OpeningLobby/Review02/approval.json')));
start('08','Approved art / proposed dimensioned interpretation','Original LobbyArt-Review02 images at left. Schematics at right explain relationships; no perspective match is claimed.',1740);
for(let i=0;i<3;i++){
 const a=approval.approved_files[i],bytes=fs.readFileSync(path.join(root,a.file));
 if(crypto.createHash('sha256').update(bytes).digest('hex')!==a.sha256)throw Error(`Approved image mismatch: ${a.file}`);
 const top=180+i*485;
 v.push(`<image x="50" y="${top}" width="800" height="450" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,${bytes.toString('base64')}"/>`);
 text(50,top+474,`${i+1}. ${path.basename(a.file)}  /  approved image, unchanged`,18,C.teal);
 if(i<2){elevation(i===0?'inner':'entrance',1195,top+325,15,true);notes(880,top+368,i===0?['E1 / sheet 04: massive stone around a small door.','High inner glazing; both 4 m side aisles retained.','Door 1.04 × 2.18 m is a proposed exception.']:['E2 / sheet 05: upper glazing above small entry leaves.','Station left of detector when looking toward entrance.','18 m envelope; glazing head Z 17.8 m.'],18);}
 else{
  const bs=12,pxx=x=>1040+(x+N.length/2)*bs,pyy=y=>top+175-y*bs;
  rect(pxx(-N.length/2),pyy(N.width/2),20*bs,N.width*bs,'none');
  for(const y of [-N.pier_y,N.pier_y])for(const x of N.pier_x.slice(0,2))rect(pxx(x-N.pier_size/2),pyy(y+N.pier_size/2),N.pier_size*bs,N.pier_size*bs,C.stone);
  const ay=N.width/2-N.aisle_clear/2;
  for(const y of [-ay,ay])arrow(pxx(-28),pyy(y),pxx(-13),pyy(y));arrow(pxx(-27),pyy(ay),pxx(-27),pyy(-ay));
  const st=H.station,de=H.detector,cam=D.cameras[2];
  rect(pxx(st.x-st.worktop_depth_x/2),pyy(st.y+st.worktop_width_y/2),st.worktop_depth_x*bs,st.worktop_width_y*bs,C.orange);
  rect(pxx(de.x-de.depth/2),pyy(de.y+de.clear_width/2+de.post_width),de.depth*bs,(de.clear_width+2*de.post_width)*bs,'none',C.orange);
  arrow(pxx(cam.xyz[0]),pyy(cam.xyz[1]),pxx(cam.target_xy[0]),pyy(cam.target_xy[1]),C.orange);text(1300,top+140,'C3 direction',18,C.orange);
  notes(880,top+355,['Sheet 06 / schematic end plan, 12 pixels per metre.','Checkpoint stays compact; full pier and aisle matter.','Continuous ±Y routes join behind the checkpoint.','C3 pose and lens are estimates; later 16:9 proof required.'],18);
 }
}
save('08-art-board',1740);

const checks=[];function check(name,ok){checks.push({name,pass:!!ok});if(!ok)throw Error(name);}
const eq=(a,b)=>Math.abs(a-b)<1e-6;
for(const key of Object.keys(O)){if(typeof O[key]==='number')check(`2x architecture: ${key}`,eq(N[key],2*O[key]));}
for(const key of Object.keys(D.end_fields.old))check(`2x end field: ${key}`,eq(D.end_fields.candidate[key],D.end_fields.old[key]*2));
check('12 piers in six symmetric pairs',N.pier_x.length===D.architecture.pair_count&&N.pier_x.length*2===12);
check('width partition closes',eq(2*N.aisle_clear+2*N.pier_size+N.central_clear,N.width));
check('pier inner face = half central clear',eq(N.pier_y-N.pier_size/2,N.central_clear/2));
check('pier outer face + aisle = half hall',eq(N.pier_y+N.pier_size/2+N.aisle_clear,N.width/2));
for(let i=1;i<N.pier_x.length;i++)check(`bay ${i} pitch and clear`,eq(N.pier_x[i]-N.pier_x[i-1],N.bay_pitch)&&eq(N.bay_pitch-N.pier_size,N.bay_clear));
check('lintel underside equals shaft height',eq(N.lintel_underside,N.shaft_height));
check('entrance upper head below ceiling',D.end_fields.candidate.upper_sill+D.end_fields.candidate.upper_height<N.height);
check('inner window head below ceiling',D.end_fields.candidate.inner_window_sill+D.end_fields.candidate.inner_window_height<N.height);
check('detector capsule nominal width clearance',H.detector.clear_width>2*D.human_reference.capsule_radius);
check('checkpoint stops before first pier',H.station.x+H.station.worktop_depth_x/2<N.pier_x[0]-N.pier_size/2);
// B1: verify the printed clearance against the schedule and serialized drawing geometry.
const checkpointSvg=fs.readFileSync(path.join(dir,'06-checkpoint.svg'),'utf8');
const attrs=tag=>Object.fromEntries([...tag.matchAll(/([\w-]+)="([^"]*)"/g)].map(m=>[m[1],m[2]]));
const crossover=[...checkpointSvg.matchAll(/<line\b[^>]*\/>/g)].map(m=>attrs(m[0])).find(a=>a.stroke===C.teal&&eq(+a.x1,+a.x2)&&Math.abs(+a.y2-a.y1)>400);
const worktop=[...checkpointSvg.matchAll(/<rect\b[^>]*\/>/g)].map(m=>attrs(m[0])).find(a=>a.fill===C.orange);
const planScale=Number(checkpointSvg.match(/End plan \/ ([\d.]+) px per metre/)[1]);
const printedClearance=Number(checkpointSvg.match(/>([\d.]+) m to worktop front<\/text>/)[1]);
const scheduledClearance=H.station.x-H.station.worktop_depth_x/2-checkpointCrossoverX;
check('checkpoint crossover label agrees with schedule',eq(printedClearance,num(scheduledClearance)));
check('checkpoint crossover label agrees with drawn coordinates',eq(printedClearance,num((+worktop.x-+crossover.x1)/planScale)));
const c3=D.cameras[2];check('C3 yaw faces target',Math.abs(Math.atan2(c3.target_xy[1]-c3.xyz[1],c3.target_xy[0]-c3.xyz[0])*180/Math.PI-c3.yaw)<.00001);
fs.writeFileSync(path.join(evidence,'arithmetic.json'),JSON.stringify({package:D.package,checks,walking_seconds:{old:O.length/D.human_reference.walk_speed,candidate:N.length/D.human_reference.walk_speed},scope:'Arithmetic only; no visual acceptance or collision test.'},null,2));
fs.writeFileSync(path.join(evidence,'source-hashes.json'),JSON.stringify({approved:approval.approved_files,layout02:['view-entrance-to-inner.png','view-inner-to-entrance.png','view-security-oblique.png'].map(file=>({file:`Saved/OpeningLobby/Layout02/${file}`,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'Saved/OpeningLobby/Layout02',file))).digest('hex')}))},null,2));
fs.writeFileSync(path.join(evidence,'sheets.json'),JSON.stringify(sheets,null,2));
console.log(`Generated ${sheets.length} SVG sheets; ${checks.length} arithmetic checks passed.`);
if(process.argv.includes('--render')){
 const chrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
 const profile=path.join(evidence,'BrowserProfile');
 const renderSheet=process.argv.find(a=>a.startsWith('--render-sheet='))?.split('=')[1];
 if(renderSheet&&!sheets.some(sh=>sh.name===renderSheet))throw Error(`Unknown render sheet: ${renderSheet}`);
 for(const sh of sheets){
  if(renderSheet&&sh.name!==renderSheet)continue;
  const html=path.join(evidence,`${sh.name}.html`);
  fs.writeFileSync(html,`<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;width:1600px;height:${sh.height}px;overflow:hidden}</style></head><body>${fs.readFileSync(path.join(dir,`${sh.name}.svg`),'utf8')}</body></html>`);
  const args=['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-extensions','--disable-sync','--hide-scrollbars','--allow-file-access-from-files',`--user-data-dir=${profile}`,'--force-device-scale-factor=1',`--window-size=1600,${sh.height}`,'--run-all-compositor-stages-before-draw','--virtual-time-budget=1500',`--screenshot=${path.join(dir,`${sh.name}.png`)}`,new URL(`file:///${html.replaceAll('\\','/')}`).href];
  const r=spawnSync(chrome,args,{encoding:'utf8',timeout:45000,windowsHide:true});
  fs.writeFileSync(path.join(evidence,`${sh.name}-render.log`),`${r.stdout||''}\n${r.stderr||''}\nExit: ${r.status}\nError: ${r.error||''}`);
  if(r.status!==0||!fs.existsSync(path.join(dir,`${sh.name}.png`)))throw Error(`Render failed: ${sh.name}`);
  console.log(`Rendered ${sh.name}`);
 }
}
