"""One final identity/preservation and real asset-wiring audit, without gameplay."""
from pathlib import Path
import difflib, hashlib, json, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,v):
    with (OUT/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
def payload(result):
    assert not result.get('isError'),result
    return json.loads(next(c['text'] for c in result['content'] if c['type']=='text'))['returnValue']
before=payload(read(OUT/'graph-before.json'));after=payload(read(OUT/'graph-after.json'))
assert before==after,'The retained graph changed'
def node(name): return next(n for n in after if n['node']['refPath'].endswith('.'+name))
def linked(n,pin,direction,other):
    return any(c['node']['refPath'].endswith('.'+other) for p in n[direction+'_pins'] if p['name']==pin for c in p['connected_pins'])
correction=node('AnimGraphNode_ModifyBone_1')
checks=dict(native_correction_to_spine=linked(correction,'Rotation','input','K2Node_CallFunction_0') and 'spine_01' in correction['type_id'],
    spine_to_hand_ik=linked(correction,'Pose','output','AnimGraphNode_TwoBoneIK_2'),
    hand_ik_to_local=linked(node('AnimGraphNode_TwoBoneIK_2'),'Pose','output','AnimGraphNode_ComponentToLocalSpace_2'),
    local_to_preragdoll=linked(node('AnimGraphNode_ComponentToLocalSpace_2'),'Pose','output','AnimGraphNode_SaveCachedPose_0'))
ik=json.loads(payload(read(OUT/'ik-after.json')))['Node']
checks['left_hand_follows_right_hand']=ik['iKBone']['boneName']=='hand_l' and ik['effectorTarget']['boneReference']['boneName']=='hand_r' and ik['effectorLocationSpace']=='BCS_BoneSpace'
parents={r['value']['bone']:payload(r['value']['result']) for r in read(OUT/'bone-parents.json') if r['status']=='fulfilled'}
def below(bone,root):
    for _ in range(24):
        if bone==root:return True
        bone=parents.get(bone,'')
        if not bone:return False
    raise AssertionError('cyclic hierarchy')
checks['head_and_hands_inherit_lean']=all(below(n,'spine_01') for n in ('head','hand_l','hand_r'))
checks['pelvis_and_legs_outside_lean']=all(not below(n,'spine_01') for n in ('pelvis','thigh_l','thigh_r','foot_l','foot_r'))
editor=read(OUT/'editor-after.json')
checks['native_pose_cases']=editor['native_pose_checks']['passed'] and len(editor['native_pose_checks']['cases'])==18
checks['component_additive_control']=editor['modify_bones'][0]['bone']=='spine_01' and 'BMM_ADDITIVE' in editor['modify_bones'][0]['mode'] and 'BCS_COMPONENT_SPACE' in editor['modify_bones'][0]['space']
write('pose-wiring.json',dict(checks=checks,passed=all(checks.values()),source_graph_unchanged=True,asset='/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP',native_cases=18))
assert all(checks.values()),checks
preserved={}
for category in ('owner','historical','assets'):
    rows=read(OUT/('assets-before.json' if category=='assets' else f'{category}-preservation-before.json'))
    changed=[r['path'] for r in rows if sha(ROOT/r['path'])!=r['sha256']]
    assert not changed,changed
    preserved[category]=dict(files=len(rows),all_match=True)
old=read(OUT/'source-before.json');old_names={r['path'] for r in old}
current=[p for p in (ROOT/'Source/MeridianSquad').iterdir() if p.is_file()]
changed=[r['path'] for r in old if sha(ROOT/r['path'])!=r['sha256']]
added=[p.relative_to(ROOT).as_posix() for p in current if p.relative_to(ROOT).as_posix() not in old_names]
diff=[]
with zipfile.ZipFile(OUT/'preserved-inputs.zip') as z:
    for path in changed+added:
        previous=z.read(path).decode('utf-8-sig').replace('\r\n','\n') if path in old_names else ''
        updated=(ROOT/path).read_text(encoding='utf-8-sig')
        diff.extend(difflib.unified_diff(previous.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='MSQ-119/'+path,tofile='MSQ-120/'+path))
with (OUT/'source.diff').open('x',encoding='utf-8') as f:f.writelines(diff)
status=subprocess.check_output(['git','status','--porcelain','--','Content','Assets','Plugins'],cwd=ROOT,text=True)
assert not status.strip(),status
check=subprocess.run(['git','-c','core.safecrlf=false','diff','--check','--','Source/MeridianSquad','Scripts/CombatAI01/CAIT03','Docs/CombatAI01-MobileLean01.md'],cwd=ROOT,text=True,capture_output=True)
assert check.returncode==0,check.stdout+check.stderr
for name in ('CombatProjectileWorld.cpp','CombatProjectileWorld.h','CombatRifleComponent.cpp','GASPEnemyFixture.cpp','EnemyCombatSenses.cpp'):
    row=next(r for r in old if r['path'].endswith('/'+name));assert sha(ROOT/row['path'])==row['sha256']
preserved.update(changed_source=changed,new_source=added,unchanged_other_source=len(old)-len(changed),asset_status_clean=True,diff_check_passed=True,
    projectile_player_physics_senses_implementation_unchanged=True,source_diff_sha256=sha(OUT/'source.diff'),agent_gameplay=False,independent_review='PENDING controller dispatch',owner_gameplay='PENDING')
write('preservation-final.json',preserved)
with (OUT/'editor-readiness.log').open('x',encoding='utf-8') as f:f.write((OUT/'editor.log').read_text(encoding='utf-8-sig')[-16000:])
print(json.dumps(dict(pose_checks=checks,preservation=preserved),indent=2))
