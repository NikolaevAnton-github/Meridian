"""Summarize retained trial measurements and index evidence without rerunning tests."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/PlayerCharacter01/MetaHumanTrial01/Worker'
BASE=ROOT/'Assets/Source/PlayerCharacter01/MetaHumanTrial01'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def rotate(q,v):
    t=[2*x for x in cross(q[:3],v)];c=cross(q[:3],t)
    return [v[i]+q[3]*t[i]+c[i] for i in range(3)]
def wrist(sample):
    root=sample['components']['weapon']['bones']['Root']
    hand=sample['components']['character']['bones']['hand_r']
    q=root['rotation_xyzw'];inverse=[-q[0],-q[1],-q[2],q[3]]
    return rotate(inverse,[a-b for a,b in zip(hand['translation'],root['translation'])])
def distance(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def summaries():
    reloads=[]
    for p in sorted((OUT/'Compatibility/Playback').glob('Contact04-*.json')):
        recording=read(p);samples=recording['samples']
        reference=read(ROOT/'Saved/PlayerCharacter01/AnimationAudit01/Worker/Playback'/p.name)
        offsets=[];phase_errors=[]
        for s in samples:
            nearest=min(reference['samples'],key=lambda r:abs(r['components']['character']['time']-s['components']['character']['time']))
            offsets.append(distance(wrist(s),wrist(nearest)))
            phase_errors.append(abs(nearest['components']['character']['time']-s['components']['character']['time']))
        frames=read(p.with_suffix('')/'frames.json')
        reloads.append(dict(case=p.stem,duration_s=recording['duration'],samples=len(samples),
            final_character_time_s=samples[-1]['components']['character']['time'],
            final_weapon_time_s=samples[-1]['components']['weapon']['time'],
            maximum_character_weapon_time_difference_s=max(abs(s['components']['character']['time']-s['components']['weapon']['time']) for s in samples),
            mean_right_wrist_offset_from_source_cm=sum(offsets)/len(offsets),
            right_wrist_offset_from_source_cm=[min(offsets),max(offsets)],
            maximum_source_nearest_sample_time_error_s=max(phase_errors),
            pose_sample_intervals_s=[min(b['elapsed']-a['elapsed'] for a,b in zip(samples,samples[1:])),max(b['elapsed']-a['elapsed'] for a,b in zip(samples,samples[1:]))],
            images=[str(Path(f['file']).relative_to(OUT)).replace('\\','/') for f in frames if f['file']],
            source_paths=recording['paths'],visibility_probe=recording['visibility_probe'],
            caveat='Candidate surface evaluated in native PIE. Weapon and magazine use a hidden original contract carrier because candidate lacks ik_hand_gun. Sparse captures do not prove continuous surface contact.'))
    native=read(OUT/'apose-native-inspection.json')
    probes=read(OUT/'Deformation03/probes.json')
    # The unregistered native component returned identity socket transforms.
    # Use the inspected FBX bind coordinates (centimeters) for distances instead.
    fbx=read(OUT/'CompareAPose02/mesh-inspection.json')
    joints={b['name']:b['head'] for b in fbx['armatures'][0]['hierarchy']}
    result=dict(reloads=reloads,rig=dict(bones=native['bone_count'],missing_contract_bones=native['missing_contract_bones'],
        additional_bones_count=len(native['additional_bones']),parent_mismatches=native['parent_mismatches'],
        native_weights={k:v for k,v in native['weights'].items() if k not in ('bone_vertex_counts','copy_result')}),
        finger_probes=[{k:v for k,v in p.items() if k not in ('pose_basis','bounds_m')} for p in probes['probes'] if p['name'][:2] in ('l_','r_')],
        identities={p:sha(ROOT/p) for p in [
            'Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/tactical+jumpsuit+3d+model.fbx',
            'Assets/Source/PlayerCharacter01/AnimationAudit01/rig-contract.json']})
    result['rig']['chain_distances_cm']={
        'shoulder_separation':distance(joints['upperarm_l'],joints['upperarm_r']),
        'left_upperarm':distance(joints['upperarm_l'],joints['lowerarm_l']),
        'left_forearm':distance(joints['lowerarm_l'],joints['hand_l']),
        'left_wrist_to_middle_distal':distance(joints['hand_l'],joints['middle_03_l'])}
    result['rig']['bind_measurement_source']='CompareAPose02/mesh-inspection.json: FBX armature coordinates in cm. The unregistered-component socket transforms in apose-native-inspection.json are identity and are rejected as bind-pose evidence; native hierarchy and weight reads remain valid.'
    write(OUT/'measurements-summary.json',result)
    return result

def index(data):
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Datum16 MetaHuman Trial 01</title>
<style>body{font:16px system-ui;margin:24px;background:#202327;color:#eee;max-width:1500px}h1,h2{font-weight:600}p{max-width:1050px;line-height:1.5}select,button,input{font:inherit;margin:8px}img{max-width:100%;background:#777}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}figcaption{padding:8px}.gallery{max-width:900px}a{color:#9cd0ff}.note{color:#ffd992}</style>
<h1>Datum16 MetaHuman Trial 01</h1><p>Live conformation succeeded. The fitted surface retains broad garment volume, but loses construction detail and turns boots into anatomical feet. It is a diagnostic base, not an accepted visible coverall or production rig.</p>
<h2>Source and fitted T-pose</h2><p class="note">The fitted view is the source-pose DNA mesh with a documented +90° X mesh-only display correction. Its original import has a mesh/skeleton axis mismatch. The default head is an unapproved scaffold. Use the separate A-pose export for rig inspection.</p>
<select id="comparison"></select><div class="pair"><figure><img id="source"><figcaption>Original body derivative</figcaption></figure><figure><img id="fit"><figcaption>Fitted source-pose surface, diagnostic alignment</figcaption></figure></div>
<h2>Usable A-pose export</h2><p>Actual exported body geometry, 342 Unreal bones, existing UVs and normalized weights. The missing upper neck/chest region belongs to the separate MetaHuman head partition. No final character assembly or face design is accepted.</p><div class="pair"><img src="CompareAPose02/fit-front.png"><img src="CompareAPose02/fit-oblique.png"></div>
<h2>Static deformation</h2><p>Deformation03 uses the exported geometry and weights in Blender. It does not execute Unreal corrective post-processing, cloth or physics. Deformation02 images are rejected because animation reevaluation reset the rendered pose.</p><select id="probe"></select><div class="pair"><img id="probeFront"><img id="probeSide"></div>
<h2>All ten digits</h2><p>Each named digit is flexed separately. These exact evaluated surface crops exclude the rest of the body within a 25 cm wrist radius for visibility. Palm, dorsal and oblique views preserve the same pose. This tests correspondence and skin response, not weapon trigger contact.</p><select id="digit"></select><select id="handview"><option>palm</option><option>dorsal</option><option>oblique</option></select><div class="pair"><img id="restHand"><img id="curlHand"></div>
<h2>Native reload probes</h2><p class="note">The visible character is the fitted body. A hidden original rig drives the rifle attachment missing from the candidate. These four recordings are diagnostic direct-animation probes, not accepted retargeting. They use original additive bases, rate 1 and synchronized weapon/magazine motion. Captures are sparse.</p><select id="reload"></select><input id="frame" type="range" min="0" value="0"><span id="frameLabel"></span><p id="reloadStats"></p><div class="gallery"><img id="reloadImage"></div>
<p><a href="measurements-summary.json">Measurements</a> · <a href="apose-native-inspection.json">Native geometry / weights / hierarchy</a> · <a href="preservation-after.json">Preservation</a> · <a href="final-packages.json">Package dependencies</a> · <a href="Deformation03/probes.json">Exact static probe settings</a></p>
<script>const data=DATA;
function options(id,values){const e=document.getElementById(id);values.forEach(v=>e.add(new Option(v,v)));return e}
const comparison=options('comparison',['front','back','side','oblique','hips','ankles','shoulders','left_dorsal','left_palm','left_oblique','right_dorsal','right_palm','right_oblique']);
function compare(){source.src='ComparePosedDNA02_Aligned/source-'+comparison.value+'.png';fit.src='ComparePosedDNA02_Aligned/fit-'+comparison.value+'.png'}comparison.onchange=compare;compare();
const probe=options('probe',['rest','arm_raise','cross_body','elbow_twist','deep_crouch','ankle_flex']);function drawProbe(){probeFront.src='Deformation03/'+probe.value+'-front.png';probeSide.src='Deformation03/'+probe.value+'-side.png'}probe.onchange=drawProbe;drawProbe();
const digit=options('digit',data.finger_probes.map(d=>d.name));function drawHand(){restHand.src='Deformation03/Hands04/rest_'+digit.value[0]+'-'+handview.value+'.png';curlHand.src='Deformation03/Hands04/'+digit.value+'-'+handview.value+'.png'}digit.onchange=handview.onchange=drawHand;drawHand();
const reload=options('reload',data.reloads.map(d=>d.case));function drawReload(){let d=data.reloads.find(d=>d.case===reload.value);frame.max=Math.max(0,d.images.length-1);frame.value=Math.min(+frame.value,+frame.max);reloadImage.src=d.images[+frame.value];frameLabel.textContent=(+frame.value+1)+' / '+d.images.length;reloadStats.textContent=d.samples+' telemetry samples; end '+d.final_character_time_s.toFixed(4)+' s; maximum character/rifle time difference '+d.maximum_character_weapon_time_difference_s.toFixed(6)+' s; right-wrist displacement from source grip '+d.right_wrist_offset_from_source_cm.map(v=>v.toFixed(2)).join('–')+' cm.'}reload.onchange=()=>{frame.value=0;drawReload()};frame.oninput=drawReload;drawReload();</script></html>'''
    (OUT/'index.html').write_text(html.replace('DATA',json.dumps(data)),encoding='utf-8')

def manifest():
    dest=BASE/'manifest.json'
    assert not dest.exists(),'Never silently replace an immutable candidate manifest'
    files=[p for root in [BASE,ROOT/'Content/Development/PlayerCharacter01/MetaHumanTrial01'] for p in root.rglob('*') if p.is_file()]
    files+=list((ROOT/'Scripts/PlayerCharacter01').glob('metahuman_trial01_*.py'))
    files += [ROOT/'Docs/PlayerCharacter01MetaHumanTrial01.md',ROOT/'MeridianSquad.uproject']
    rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)]
    binaries=[r['path'] for r in rows if Path(r['path']).suffix in ('.blend','.fbx','.dna','.uasset')]
    result=subprocess.check_output(['git','check-attr','filter','--',*binaries],cwd=ROOT,text=True)
    (OUT/'lfs-policy.txt').write_text(result,encoding='utf-8')
    assert all(line.endswith(': lfs') for line in result.splitlines()),result
    write(dest,dict(manifest_id='MSQ54-Datum16MetaHumanTrial01-Worker01',date='2026-09-17',
        state='Experimental; no production or owner visual acceptance',files=rows,
        binary_files=len(binaries),external_evidence='Saved/PlayerCharacter01/MetaHumanTrial01/Worker/',
        exclusions='Generated logs, image evidence and caches remain under Saved; immutable manifest excludes itself.'))
    return dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),binary_files=len(binaries),manifest_sha256=sha(dest))

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='manifest':print(json.dumps(manifest()))
    else:
        data=summaries();index(data)
        print(json.dumps({k:v for k,v in data.items() if k in ('reloads','identities')}))
