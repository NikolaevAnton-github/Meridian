"""Freeze the reviewed worker candidate and explicit asset/region replacement contract."""
import json
import shutil
import subprocess
from pathlib import Path
from preserve69 import ROOT, OUT, base

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path, value):
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
def fingerprint(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=base.sha(path))

if __name__ == '__main__':
    assert not read(OUT/'verification-summary01.json')['failed']
    editor=read(OUT/'handoff-final.json')
    assert not editor['state']['pie'] and not editor['state']['dirty_content'] and not editor['state']['dirty_maps']
    preservation=read(OUT/'preservation-after.json')
    assert not preservation['missing']
    owner=read(OUT.parent/'Controller/owner-config-before.json')['Hash'].lower()
    assert base.sha(ROOT/'Config/DefaultEngine.ini') == owner
    closure=read(OUT/'dependency-plan-final.json')
    assert all(r['loaded'] for r in closure['assets'])
    assets=[fingerprint(ROOT/'Content'/(p.removeprefix('/Game/')+'.uasset')) | dict(package=p) for p in closure['closure']]
    stages=read(OUT/'staged-sources.json')['files']+read(OUT/'staged-sources-template.json')['files']
    for asset in assets:
        original=next((r for r in stages if r['package']==asset['package'] and r.get('source')),None)
        if original:
            assert base.sha(Path(original['source'])) == original['sha256'] == asset['sha256']
            asset['immutable_source']=original['source']
    anims=read(OUT/'animation-adaptation-02.json')
    for a in anims:
        row=next(r for r in stages if r['package']==a['source'])
        a['immutable_source']=row['source']
        a['source_sha256']=row['sha256']
        a.pop('head',None)
        a['adaptation']={'additive':'None (raw full pose)', 'root_motion':False, 'force_root_lock':True, 'skeleton_unchanged':True}
    meshrow=next(r for r in read(OUT/'asset-audit-01.json')['assets'] if r['package']=='/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
    spheres=[dict(region='head',bone='head',end='head',radius_cm=12,count=1,component_offset_cm=[0,0,7]),
             dict(region='torso',bone='spine_04',end='spine_05',radius_cm=19,count=1),
             dict(region='torso',bone='spine_02',end='spine_03',radius_cm=17,count=1),
             dict(region='pelvis',bone='pelvis',end='spine_01',radius_cm=18,count=1)]
    for side in ['l','r']:
        for region,bone,end,radius,count in [('arm','upperarm','lowerarm',9,2),('arm','lowerarm','hand',8,2),('arm','hand','hand',8,1),
            ('leg','thigh','calf',12,3),('leg','calf','foot',10,3),('leg','foot','ball',10,1)]:
            spheres.append(dict(region=region+'_'+side,bone=bone+'_'+side,end=end+'_'+side,radius_cm=radius,count=count))
    contract=dict(record_id='EnemyPrototype01-Contract01',task='MSQ-69',revision=1,date_local='2026-09-19',
        status='Worker verified; independent review and controller acceptance pending',
        representation='Installed UE template Manny Simple technical placeholder; no final enemy art acceptance',
        engine='5.8.1-56057345+++UE5+Release-5.8',
        source_rights=dict(template='Installed Templates/TemplateResources/High/Characters; UE Examples reuse in this Unreal project',
            terms='https://www.unrealengine.com/eula/unreal',
            rifle='Existing owner-purchased Infima SK_TFA_AR visual core; owner purchase statement is preserved, receipt/tier unavailable locally',
            exclusions=['No purchases or downloads','No reuse of the paused original protagonist as enemy source','No external source-asset redistribution authorization']),
        assets=assets,
        retained_rifle=fingerprint(ROOT/'Content/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/SK_TFA_AR.uasset'),
        editable_source=fingerprint(ROOT/'Assets/Source/EnemyPrototype01/SKM_Manny_Simple_Export02.fbx'),
        unselected_export=fingerprint(ROOT/'Assets/Source/EnemyPrototype01/SKM_Manny_Simple_Export01.fbx'),
        skeleton=dict(package='/Game/Characters/Mannequins/Meshes/SK_Mannequin',mesh_bone_entries=len(meshrow['bones']),
            exported_bones=88,mesh_bones=meshrow['bones']),
        animation_copies=anims,
        verified_coverage=['Rifle idle/hold with the visual rifle core','Left/right in-place walk','Explicit fire-pose playback (no enemy shot)',
            'Front light hit and idle/walk recovery','Whole-body ragdoll death and active/settled reset'],
        missing_or_unverified=['Full modular rifle attachment/magazine assembly','Directional or limb-specific hit animation variants',
            'Integrated forward/back locomotion, crouch, turns, jumps, blend transitions','AI, enemy projectile firing, player health',
            'Corpse damage, detached limb rendering/physics, cap UVs/interior materials'],
        collision=dict(alive_capsule='34 cm radius / 92 cm half-height: world and pawn movement only; ignored by projectile world query',
            alive_mesh='No rigid/query collision; 28 sampled bone spheres own projectile and convergence queries',
            sphere_centers='Lerp(start bone, end bone, (index+0.5)/count), plus optional component-space offset',
            spheres=spheres,total_spheres=sum(s['count'] for s in spheres),
            temporal_policy='Linear interpolation between rendered-frame bone samples on the retained birth/substep clock; per-bullet birth snapshots',
            damage_path='Authoritative rifle -> finite-flight manager -> earliest world/player/enemy hit -> ApplyPointDamage -> TakeDamage',
            event_mapping='FPointDamageEvent.HitInfo.BoneName maps to head, torso, pelvis, arm_l, arm_r, leg_l, leg_r; unmapped generic damage is explicitly labelled',
            damage_multiplier=1,health=100,default_rifle_damage=25,
            unsupported_detail='Not per-poly. No independent fingers, toes, eyes, armor layers, neck segment, or internal damage. Sphere gaps and overlap follow the documented approximation.',
            dead='Movement capsule/query volumes off; unchanged PA_Mannequin ragdoll blocks WorldStatic only; ignores pawn/projectiles; forced sleep after six world seconds',
            reset='Manager clears bullets/feedback; enemy clears rigid velocities, disables physics, reattaches and refreshes idle pose; health restored, ammunition unchanged'),
        separation=dict(status='Editable source and bounded forearm capping feasibility established; no severed gameplay asset accepted',
            evidence='Saved/CombatSlice01/EnemyPrototype01/Worker/mesh-topology-audit02.json',
            measurement=read(OUT/'mesh-topology-audit02.json')['forearm_trial'],
            required_next=['Preserve UV/normal/weight seams while reconciling coincident vertices','Prepare matching retained stump and detached mesh',
                'Triangulate/inspect caps and assign interior material','Check deformed cut continuity, self-intersections and mass/collision',
                'Verify detached rigid-body behavior and reset in Unreal'],
            owner_source_selection_gate=False,
            scope_limit='Only a bounded technical source adaptation is feasible under this contract. Final enemy appearance and new model production keep separate concept/owner gates.'),
        replacement_boundary=dict(actor='/Script/MeridianSquad.EnemyPrototypeCharacter',
            body='Replace body, skeleton-compatible animations and physics asset on a subclass; preserve 1 cm world units and foot origin',
            region_mapping='Update SampleHitSpheres / RegionForBone for the replacement skeleton; retain FPointDamageEvent and health semantics',
            behavior='Future EnemyCombat01 replaces the explicit preview movement/fire hooks with its scoped AI/weapon behavior',
            projectiles='Reuse CombatProjectileWorld / CombatRifleComponent; no animation notify applies gameplay damage'),
        verification='Saved/CombatSlice01/EnemyPrototype01/Worker/verification-summary01.json')
    save(ROOT/'Docs/EnemyPrototype01-Contract01.json',contract)
    save(OUT/'EnemyPrototype01-Contract01.json',contract)
    paths=[ROOT/'.gitattributes',ROOT/'Docs/EnemyPrototype01.md',ROOT/'Docs/EnemyPrototype01-Contract01.json']
    paths += list((ROOT/'Scripts/EnemyPrototype01').glob('*.py'))
    paths += [ROOT/'Source/MeridianSquad'/n for n in ['CombatProjectileWorld.cpp','CombatProjectileWorld.h','CombatRifleComponent.cpp','CombatRifleComponent.h','CombatPrototypeHUD.cpp','EnemyPrototypeCharacter.cpp','EnemyPrototypeCharacter.h','EnemyPrototypeProbes.cpp']]
    paths += [ROOT/a['path'] for a in assets]
    paths += list((ROOT/'Assets/Source/EnemyPrototype01').glob('*.fbx'))
    manifest=[fingerprint(p) for p in sorted(paths)]
    save(OUT/'candidate-manifest.json',manifest)
    snapshot=OUT/'FinalCandidate/SourceSnapshot'
    for p in paths:
        if p.suffix in ['.cpp','.h','.py','.md','.json']:
            dst=snapshot/p.relative_to(ROOT)
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dst)
    evidence=[OUT/'verification-summary01.json',OUT/'collision-probe-02.json',OUT/'collision-probe-cover03.json',OUT/'mesh-topology-audit02.json',OUT/'handoff-final.json',OUT/'native-settings-verified.json',OUT/'preservation-after.json',OUT/'storage-after.json',OUT/'build07.log']
    for label in ['Candidate06-IdleHitDeathReset','Candidate06-MovingHits','Candidate06-HoldFirePresentation','Candidate07-ActiveRagdollReset']:
        evidence.append(OUT/(label+'.json'))
        evidence.extend(sorted((OUT/'Video').glob(label+'*')))
    save(OUT/'evidence-manifest.json',[fingerprint(p) for p in evidence])
    binary=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
    summary=read(OUT/'verification-summary01.json')
    handoff=dict(task='MSQ-69',status='ready_for_primary_independent_review',report='Docs/EnemyPrototype01.md',
        contract='Docs/EnemyPrototype01-Contract01.json',candidate_manifest='Saved/CombatSlice01/EnemyPrototype01/Worker/candidate-manifest.json',
        evidence_manifest='Saved/CombatSlice01/EnemyPrototype01/Worker/evidence-manifest.json',
        build=dict(result='Succeeded',log='Saved/CombatSlice01/EnemyPrototype01/Worker/build07.log',binary=fingerprint(binary)),
        checks_passed=summary['passed'],checks_failed=summary['failed'],sampled_rows=sum(m['rows'] for m in summary['metrics'].values()),
        metrics=summary['metrics'],owner_config_sha256=owner,preservation=preservation,storage=read(OUT/'storage-after.json'),
        editor=editor,actual_settings='gpt-6-astra / max / default; ChatGPT login; fast mode disabled',
        limits=['Technical placeholder, no final art acceptance','No AI/player damage/enemy firing','Immediate single-node animation transitions',
            'Approximate bone spheres; no precise finger/toe/neck damage','Rifle core only, no full modular dressing',
            'Forearm topology feasibility only; detached-piece runtime physics/cap materials not yet verified',
            'Retained MSQ-82 low-FPS procedural recoil limitation unchanged'],
        controller_actions=['Primary independent technical/visual evidence review','Close any bounded findings','Asset registry decision and task-scoped local commit','Issue/profile/acceptance administration'],
        task_files=[r['path'] for r in manifest],not_committed=True,issue_status_not_changed=True)
    save(OUT/'handoff.json',handoff)
    print(json.dumps(dict(candidate_files=len(manifest),asset_packages=len(assets),evidence_files=len(evidence),checks=summary['passed'],rows=handoff['sampled_rows'])))
