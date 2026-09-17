"""Summarize recorded native playback; generate an offline evidence viewer."""
import html
import json
import math
from pathlib import Path

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/PlayerCharacter01/AnimationAudit01/Worker'
SOURCE=ROOT/'Assets/Source/PlayerCharacter01/AnimationAudit01'


def local_position(point,frame):
    v=[point[i]-frame['translation'][i] for i in range(3)]
    x,y,z,w=frame['rotation_xyzw']
    q=[-x,-y,-z]
    cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    t=[2*n for n in cross(q,v)]
    c=cross(q,t)
    return [v[i]+w*t[i]+c[i] for i in range(3)]


def main():
    metrics=[]
    gallery=[]
    for p in sorted((OUT/'Playback').glob('*.json')):
        if not (p.stem.startswith('Contact04-') or p.stem.startswith('Local-')):continue
        d=json.loads(p.read_text())
        ss=d['samples']
        assert ss and not d.get('error') and not d['active'],p
        row=dict(key=d['key'],samples=len(ss),duration=d['duration'],
                 first_time=ss[0]['components']['character']['time'],last_time=ss[-1]['components']['character']['time'],
                 complete=ss[-1]['components']['character']['time']>=d['duration']-.01)
        if p.stem.startswith('Contact04-'):
            relative=[local_position(s['components']['character']['bones']['hand_r']['translation'],s['components']['weapon']['bones']['Root']) for s in ss]
            row['max_character_weapon_time_delta_s']=max(abs(s['components']['character']['time']-s['components']['weapon']['time']) for s in ss)
            row['right_wrist_in_rifle_root_at_start_cm']=relative[0]
            row['right_wrist_max_displacement_from_start_in_rifle_root_cm']=max(math.dist(v,relative[0]) for v in relative)
            distances=[math.dist(s['components']['character']['bones']['index_03_r']['translation'],s['components']['weapon']['bones']['Trigger']['translation']) for s in ss]
            row['index03_joint_to_trigger_bone_distance_cm']=[min(distances),max(distances)]
            row['interpretation']='Bone origins, not glove/trigger surfaces; contact observations, not a zero-distance surface-contact acceptance test.'
            row['first_visibility_transitions']={}
            previous=None
            for s in ss:
                vis=s.get('visibility')
                if vis!=previous:
                    row['first_visibility_transitions'][str(round(s['components']['weapon']['time'],6))]=vis
                    previous=vis
        else:
            row['left_foot_motion_extent_cm']=max(math.dist(s['components']['character']['bones']['foot_l']['translation'],ss[0]['components']['character']['bones']['foot_l']['translation']) for s in ss)
        metrics.append(row)
        frames=json.loads((OUT/'Playback'/p.stem/'frames.json').read_text())
        images=[Path(f['file']).relative_to(OUT).as_posix() for f in frames]
        gallery.append(dict(key=p.stem,images=images,duration=d['duration'],samples=len(ss)))
    (OUT/'playback-summary.json').write_text(json.dumps(metrics,indent=2))
    (SOURCE/'contact-measurements.json').write_text(json.dumps(metrics,indent=2))
    page='''<!doctype html><meta charset="utf-8"><title>MSQ-52 native playback evidence</title>
<style>body{background:#17202a;color:#eee;font:16px system-ui;max-width:1200px;margin:auto;padding:24px}img{max-width:100%;max-height:72vh}button,select,input{font:inherit;margin:6px}article{border-top:1px solid #657;padding-top:20px;margin-top:32px}small{color:#bdc9d3}</style>
<h1>MSQ-52: native playback and contact evidence</h1>
<p>Technical mannequins in UE 5.8.1. Contact04 uses fixed manual exposure, actual FP/TP additive-base evaluation, the default handguard, rear sight, main/reserve magazines and measured source visibility intervals. Dropped-magazine physics and gameplay ammo events are not implemented.</p>
<p>The clips advanced in PIE; frame images are sampled captures, not full-rate video. Raw per-frame bone transforms and timestamps are in adjacent JSON files. Local locomotion captures predate the fixed exposure pass; assess motion coverage, not final character quality.</p>
<label>Recording <select id="clip"></select></label><button id="play">Play/Pause</button><input id="frame" type="range" min="0" value="0"><span id="label"></span><br><img id="image"><p id="meta"></p>
<article><h2>Fixed 170 cm camera versus source head height</h2><p>Both images use 90 degree FOV and the same source aimed start pose, with no mesh scale or offset correction. This exposes the fitting work required for the original character.</p><img src="Camera/Final-baseline170-aimed.png"><img src="Camera/Final-source162-aimed.png"></article>
<script>const data=DATA;const select=document.querySelector('#clip'),slider=document.querySelector('#frame'),img=document.querySelector('#image');let playing=false;
data.forEach((d,i)=>{let o=document.createElement('option');o.value=i;o.textContent=d.key;select.append(o)});
function draw(){let d=data[+select.value],i=+slider.value;slider.max=d.images.length-1;img.src=d.images[i];document.querySelector('#label').textContent=` ${i+1}/${d.images.length}`;document.querySelector('#meta').textContent=`Duration ${d.duration.toFixed(4)} s; ${d.samples} native telemetry samples. See Playback/${d.key}.json.`}
select.onchange=()=>{slider.value=0;draw()};slider.oninput=draw;document.querySelector('#play').onclick=()=>playing=!playing;
setInterval(()=>{if(playing){let d=data[+select.value];slider.value=(+slider.value+1)%d.images.length;draw()}},350);draw();</script>'''.replace('DATA',json.dumps(gallery))
    (OUT/'index.html').write_text(page,encoding='utf-8')
    assert all(r['complete'] for r in metrics)
    assert all(r.get('max_character_weapon_time_delta_s',0)<.001 for r in metrics)
    print(json.dumps(dict(recordings=len(metrics),reload_pairs=sum(x['key'].startswith('Contact04') for x in metrics),
                         complete=all(x['complete'] for x in metrics),gallery=str(OUT/'index.html'))))


if __name__=='__main__':main()
