"""Build the MSQ-52 source contract and verify the bounded selected subset."""
import csv
import hashlib
import json
import math
import os
import shutil
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT/'Saved/PlayerCharacter01/AnimationAudit01/Worker'
SOURCE = ROOT/'Assets/Source/PlayerCharacter01/AnimationAudit01'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2),encoding='utf-8')


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def selection():
    if (OUT/'selection-initial.json').exists():
        manifest=read(OUT/'selection-initial.json')
    else:
        manifest=read(SOURCE/'selected-sources.json')
        write(OUT/'selection-initial.json',manifest)
    files={r['package']:r for r in manifest['files']}
    deps={r['package']:r for r in read(OUT/'dependencies.json')}
    excluded=['/Interactions/','Grip_Angled','Grip_Vertical','Canted','FireModeSwitch','TriggerDiscipline','FireModeStates']
    seeds=[k for k,r in files.items() if r['seed'] and not any(x in k for x in excluded)
           and ('/Weapons/AssaultRifle/' in k or '/Anims/Rifle/' in k or k.endswith(('/SKM_Manny_Simple','/SKM_FP_Manny_Simple')))]
    seeds.append('/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple')
    keep=set()
    queue=list(seeds)
    while queue:
        k=queue.pop()
        if k in keep:continue
        assert k in files,k
        keep.add(k)
        queue.extend(d for d in deps[k]['hard'] if d.startswith('/Game/'))
    # Preserve all worker-created excess art and temporary montage copies outside Content.
    before_paths={r['path'] for r in read(OUT/'preservation-before.json')[str(ROOT).replace('\\','/')+'/Content']}
    archive=OUT/'ExcludedAuditCopies'
    moves=[]
    candidates=[r for k,r in files.items() if k not in keep]
    candidates += [dict(destination=r['copy'].replace('\\','/'),sha256=r['sha256']) for r in read(OUT/'montage-audit-copies.json')]
    for row in candidates:
        src=(ROOT/row['destination']).resolve()
        assert src.is_relative_to((ROOT/'Content').resolve()),src
        rel=src.relative_to(ROOT/'Content').as_posix()
        assert rel not in before_paths,src
        dst=(archive/rel).resolve()
        assert dst.is_relative_to(archive.resolve()),dst
        if dst.exists():
            assert sha(dst)==row['sha256'],dst
            if not src.exists():
                moves.append(dict(source=str(src),archive=str(dst),sha256=row['sha256']))
                continue
            assert sha(src)==row['sha256'],src
            # A previous Windows move copied the archive but could not release a loaded file.
            src.unlink()
            moves.append(dict(source=str(src),archive=str(dst),sha256=row['sha256']))
            continue
        assert sha(src)==row['sha256'],src
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(src),str(dst))
        moves.append(dict(source=str(src),archive=str(dst),sha256=row['sha256']))
    write(OUT/'excluded-copies.json',moves)
    final=dict(schema=2,status='Technical audit candidate for controller review; not owner visual acceptance',
        source_root='D:/devgames/Weapon (untouched)', engine='5.8.1-56057345',
        extraction='Selected sequences, five inspected blend spaces, one default handguard/iron-sight rifle, opaque magazine, diagnostic mannequins, hard package closure. No vendor gameplay or montages.',
        files=[dict(files[k],seed=k in seeds) for k in sorted(keep)],
        bytes=sum(files[k]['bytes'] for k in keep),
        excluded_audit_archive='Saved/PlayerCharacter01/AnimationAudit01/Worker/ExcludedAuditCopies',
        soft_reference_policy='Keep original bytes, retain unresolved unused preview/editor references explicitly in final-dependencies.json. Never treat soft-reference completeness as verified.',
        provenance=[dict(provider='Infima Games',product='Tactical FPS Animation Pack - Assault Rifle',
                         identity='Exact installed package hashes; source package engine header 5.4, verified playback in 5.8.1',
                         license='Owner-supplied licensed pack per task. Receipt/acquisition tier not present in local source; no new entitlement or redistribution claim.',
                         url='https://www.fab.com/listings/1ae386ab-4a40-4a0f-ac17-621e2d9d1028'),
                    dict(provider='Epic Games',product='UE 5.8.1 installed High Characters rifle template',
                         identity='D:/UE_5.8/Templates/TemplateResources/High/Characters/Content; CL 56057345',
                         license='Unreal Engine EULA, Examples (Templates); reviewed 2026-09-17',
                         url='https://www.unrealengine.com/eula/unreal')],
        acquisition=dict(download_bytes=0,new_purchases=0,paid_api_calls=0))
    write(SOURCE/'selected-sources.json',final)
    print(json.dumps(dict(selected=len(keep),bytes=final['bytes'],archived=len(moves))))


def contract():
    assets=read(OUT/'assets.json')
    rigs=read(OUT/'rigs.json')
    skins=read(OUT/'skin-weights.json')
    binds=rigs['SKEL_TFA_Mannequin']['bones']
    mesh=next(x for x in assets if x['package'].endswith('/SKM_Manny') and '/InfimaGames/' in x['package'])
    parents={x['name']:x['parent'] for x in mesh['bones']}
    simple=next(x for x in assets if x['package'].endswith('/SKM_Manny_Simple') and '/InfimaGames/' in x['package'])
    simple_names={x['name'] for x in simple['bones']}
    weighted=skins[simple['package']]['weighted_bone_vertex_counts']
    body=[dict(b,parent=parents[b['name']],in_simple_mesh=b['name'] in simple_names,
               weighted_vertices_in_simple_lod0=weighted.get(b['name'],0)) for b in binds]
    positions={b['name']:b['component_bind']['translation'] for b in body}
    fingers={side:{digit:([f'{digit}_metacarpal_{side}'] if digit!='thumb' else [])+
                          [f'{digit}_{i:02d}_{side}' for i in range(1,4)]
                   for digit in ['thumb','index','middle','ring','pinky']} for side in ['l','r']}
    obj=dict(contract_id='MSQ52-RigContract01',date='2026-09-17',status='Measured source contract; original geometry and retarget quality remain later gates',
        skeleton_package=rigs['SKEL_TFA_Mannequin']['package'],bone_count=len(body),bones=body,
        fingers=fingers,twist_bones=[b['name'] for b in body if 'twist' in b['name']],
        ik_bones=[dict(name=b['name'],parent=b['parent']) for b in body if b['name'].startswith('ik_')],
        simple_mesh_bones=sorted(simple_names),skin_measurements=skins,
        units=dict(engine_distance='cm',engine_actor_forward='+X',engine_up='+Z',source_mesh_forward='+Y',
                   source_mesh_left='+X',actor_mesh_yaw_degrees=-90,mesh_origin='Ground/root; actor placement at capsule bottom',
                   root_local=body[0]['local_bind']),
        bind_pose='Exact source A-pose local transforms in bones; original model must preserve names, parents, axes and lengths until an explicit proportional/retarget revision is validated.',
        retarget_pose='Start with the exact source A-pose. Template SK_Mannequin and pack SKEL_TFA_Mannequin bind component translations match exactly; skeleton asset identities differ and compatible_skeletons is empty. No new retarget asset is approved by this audit.',
        baseline=dict(capsule_radius_cm=34,capsule_half_height_cm=88,standing_camera_from_floor_cm=170,fov_degrees=90,walk_speed_cm_s=360,max_step_cm=35),
        measured_source_dimensions=dict(standing_mesh_bounds_height_cm=180.543902,head_bone_height_cm=positions['head'][2],
            shoulder_joint_separation_cm=math.dist(positions['upperarm_l'],positions['upperarm_r']),
            upperarm_length_cm=math.dist(positions['upperarm_l'],positions['lowerarm_l']),
            forearm_length_cm=math.dist(positions['lowerarm_l'],positions['hand_l']),
            wrist_to_middle03_joint_cm=math.dist(positions['hand_l'],positions['middle_03_l']),
            note='Joint distances and diagnostic mannequin bounds, not owner-approved protagonist dimensions or fingertip surface length.'),
        interfaces=dict(local_body='Original torso/pelvis/legs, world scale, camera-intersecting head and duplicate arms excluded by sections; same master proportions as full body.',
                        local_arms='Original arm geometry on compatible rig; evaluate FP additive clips on their listed authored base. Mesh forward +Y -> actor +X via -90 yaw. Fit to fixed 170 cm gameplay camera; do not drive aim from head sockets.',
                        world_body='Complete original head/body silhouette, TP upper-body actions over separate locomotion; explicit shadow/reflection ownership; evaluate while owner-hidden.',
                        rifle='Rifle component attached to character ik_hand_gun at identity; independent SKEL_TFA_AR animation synchronized to character sequence time.',
                        magazines='Main and reserve representations attach to SOCKET_Magazine and SOCKET_Magazine_Reserve. Translate source visibility/drop intervals into project events; reconcile FP/TP event disagreement before gameplay integration.'),
        fitting_constraints=dict(grip='Preserve measured source wrist/finger target transforms before changing hand scale. Validate thumb opposition, index trigger independence and all five chains through full reload.',
            reload='Maintain shoulder/elbow reach to both animated magazine paths; test armor/cuffs and cross-body reach in the four reload cases.',
            camera='Source head reference is 162.5751 cm; fixed gameplay camera remains 170 cm. Resolve the 7.4249 cm difference with original FP fit/offset tests, not a camera-height or body-scale change.',
            tolerances='Proposed prototype checks: <=0.001 cm bind round-trip position error; quaternion |dot| >=0.999999; no negative/non-unit bone scale; original glove contact within 0.5 cm of agreed source contact targets. These are technical review proposals, not owner-approved dimensions.'),
        export_contract=dict(state='Proposed settings; Blender-to-UE round trip must be validated in MSQ-54',
            blender='Metric, unit scale 0.01 for cm-authored coordinates; object transforms applied; no added Armature parent root; no automatic bone orientation. Preserve exact local matrices.',
            fbx='Global scale 1; units conversion explicit; Forward -Y / Up Z as initial Blender export profile; add leaf bones off; export non-deform IK/helper bones; no animation bake for bind mesh.',
            unreal='Import scale 1, translation/rotation zero, Convert Scene true, Convert Scene Unit false, Force Front X false, Use T0 As Ref Pose false, Update Skeleton Reference Pose false; match recorded source settings and verify matrices rather than assuming axes from labels.'),
        weapon_rigs={k:rigs[k] for k in ['SKEL_TFA_AR','SKEL_TFA_AR_Magazine']},
        import_and_socket_evidence='socket-contract.json and import-settings.json in this directory; recorded directly from the source assets',
        locomotion_root_motion_policy='All 22 selected local-template clips have enable_root_motion=true. MSQ-56 must explicitly choose CharacterMovement-compatible in-place derived copies or a reviewed root-motion movement policy; never double-apply displacement.',
        source_pose_probes=['A_TFA_FP_AR_Idle_Pose_Standing','A_TFA_FP_AR_Aim_Pose','A_TFA_FP_AR_Reload','A_TFA_FP_AR_Reload_Aimed','A_TFA_FP_AR_Reload_Empty','A_TFA_FP_AR_Reload_Empty_Aimed','A_TFA_TP_AR_Reload','MF_Rifle_Walk_Fwd','MF_Rifle_Jog_Right','MM_Rifle_Jump_Fall_Land'])
    for key in obj['weapon_rigs']:
        m=next(x for x in assets if x['type']=='SkeletalMesh' and x.get('skeleton','').split('.')[0]==rigs[key]['package'])
        parent_map={b['name']:b['parent'] for b in m['bones']}
        for b in obj['weapon_rigs'][key]['bones']:b['parent']=parent_map[b['name']]
    write(SOURCE/'rig-contract.json',obj)
    write(SOURCE/'socket-contract.json',read(OUT/'socket-contract.json'))
    details=read(OUT/'details.json')
    write(SOURCE/'blendspace-contract.json',details['blends'])
    write(SOURCE/'import-settings.json',{k:v['import_data'] for k,v in details['meshes'].items()})
    selected={r['package']:r for r in read(SOURCE/'selected-sources.json')['files']}
    matrix=[]
    playback_files=list((OUT/'Playback').glob('*.json'))
    played={p for f in playback_files if not f.stem.startswith('Contact02') for p in read(f).get('paths',{}).values() if read(f).get('samples') and not read(f).get('error')}
    for row in assets:
        if row['type']!='AnimSequence' or row['package'] not in selected:continue
        record={k:row[k] for k in ['package','skeleton','sequence_length','rate_scale','enable_root_motion','force_root_lock','root_motion_root_lock','additive_anim_type','ref_pose_type','ref_pose_seq','ref_frame_index','tracks','notify_tracks','notifies','sampled_component_positions']}
        record.update(sha256=selected[row['package']]['sha256'],playback='PIE end-to-end' if row['package'] in played else 'Native pose evaluation at 4 phases; no end-to-end playback claim')
        matrix.append(record)
    write(SOURCE/'clip-matrix.json',matrix)
    with (SOURCE/'clip-matrix.csv').open('w',newline='',encoding='utf-8') as f:
        columns=['package','sequence_length','additive_anim_type','ref_pose_seq','enable_root_motion','playback','sha256']
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(matrix)
    write(SOURCE/'reload-timing.json',read(OUT/'montage-timing.json'))
    print(json.dumps(dict(bones=len(body),clips=len(matrix))))


def verify(measure_storage=True):
    before=read(OUT/'preservation-before.json')
    changes=[]
    checked=0
    for root,rows in before.items():
        for row in rows:
            p=Path(root)/row['path']
            checked+=1
            if not p.exists() or sha(p)!=row['sha256']:changes.append(str(p))
    manifest=read(SOURCE/'selected-sources.json')
    selected_changes=[r['destination'] for r in manifest['files'] if sha(ROOT/r['destination'])!=r['sha256'] or sha(Path(r['source']))!=r['sha256']]
    if (OUT/'preservation-final.json').exists() and not read(OUT/'preservation-final.json')['passed'] and not (OUT/'preservation-before-auto-config-restoration.json').exists():
        shutil.copy2(OUT/'preservation-final.json',OUT/'preservation-before-auto-config-restoration.json')
    added_weapon=sorted(set(p.relative_to('D:/devgames/Weapon').as_posix() for p in Path('D:/devgames/Weapon').rglob('*') if p.is_file())-
                        {r['path'] for r in before['D:/devgames/Weapon']})
    write(OUT/'preservation-final.json',dict(passed=not changes and not selected_changes and not added_weapon,
        baseline_files_checked=checked,changed_originals=changes,selected_files_checked=len(manifest['files']),selected_mismatches=selected_changes))
    if not measure_storage:
        assert not changes and not selected_changes and not added_weapon
        print(json.dumps(dict(passed=True,original_files=checked,selected_files=len(manifest['files']))))
        return
    total=sum(os.path.getsize(os.path.join(d,f)) for d,ds,fs in os.walk(ROOT) for f in fs)
    baseline=read(OUT/'storage-before.json')['project_bytes']
    result=dict(project_bytes=total,baseline_bytes=baseline,growth_bytes=total-baseline,cap_bytes=250000000000,passed=total<250000000000)
    write(OUT/'storage-final.json',result)
    print(json.dumps(result))
    assert not changes and not selected_changes and result['passed']


if __name__=='__main__':
    import sys
    {'selection':selection,'contract':contract,'verify':verify,'verify_hashes':lambda:verify(False)}[sys.argv[1]]()
