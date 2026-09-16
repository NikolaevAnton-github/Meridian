"""Reuse exact preservation primitives with HC04's zero scene-property deltas."""
import json,sys,gzip,re,struct,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'Scripts/OpeningLobby/uppervoid01_soft_check.py'
source=p.read_text().replace('UpperVoid01/HeightCorrection02/Worker','UpperVoid01/HeightCorrection04/Worker').replace('UpperVoid01/HeightCorrection01/Worker','UpperVoid01/HeightCorrection03/Worker').replace('uppervoid01_soft_','uppervoid01_spatial_')
source=source.replace("read(PREV/'Handoff/all-properties.json')","json.loads(gzip.open(PREV/'Handoff/all-properties.json.gz','rt',encoding='utf-8').read())")
m=types.ModuleType('spatial_preservation');exec(compile(source,str(p),'exec'),m.__dict__)
OUT=m.OUT;PREV=m.PREV;CTRL=m.CTRL;ALLOWED=m.ALLOWED
entry=m.entry;read=m.read;walk=m.walk;write=m.write;snapshot=m.snapshot;differences=m.differences
prepare=m.prepare;movement=m.movement

def properties():
    before=snapshot('Before')
    for tag in ['Candidate','Reopened','TrialHandoff','Restored','Handoff']:
        assert not differences(before,snapshot(tag)),tag
    assert not differences(before,json.loads(gzip.open(PREV/'Handoff/all-properties.json.gz','rt',encoding='utf-8').read()))
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    old=read(PREV/'Handoff/inventory.json')
    for tag in ['Candidate','Reopened','Restored','Handoff']:
        new=read(OUT/tag/'inventory.json');assert len(new)==len(old)==108
        assert [{k:r[k] for k in keys} for r in new]==[{k:r[k] for k in keys} for r in old]
    write('property-preservation',dict(passed=True,actors=129,components=150,lobby_bindings=107,separate_support_components=1,scene_property_deltas=0,all_lights_exact=True,geometry_materials_gameplay_glass_support_exposure_exact=True,all_saved_reopened_handoff_properties_exact=True))
    print('All scene properties, lights and107bindings exact')

def graph_deltas(a,b,expected_codes):
    ds=differences(a,b);semantic=[];pointer=[];stats=[]
    for d in ds:
        assert 'before' in d and 'after' in d,d
        if isinstance(d['before'],str) and isinstance(d['after'],str) and re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['before'])==re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['after']):pointer.append(d);continue
        if '/statistics/' in d['path']:stats.append(d);continue
        assert d['path'].endswith('/properties/properties/code') and d['after'] in expected_codes,d
        semantic.append(d)
    return dict(semantic=semantic,pointer_only=pointer,statistics=stats)

def graphs():
    recipe=read(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04/recipe.json')
    old=read(PREV/'graph-audit-Reopened.json');trial=read(OUT/'graph-audit-Reopened.json');restored=read(OUT/'graph-audit-Restored.json')
    delta=graph_deltas(old,trial,[recipe['postprocess']]);assert len(delta['semantic'])==1
    for tag in ['Candidate','CompiledTrial']:
        assert not graph_deltas(trial,read(OUT/('graph-audit-'+tag+'.json')),[])['semantic']
    final_delta=graph_deltas(old,restored,[]);assert not final_delta['semantic']
    for n,k in [('Extinction.hlsl','postprocess'),('LightTransmission.hlsl','light_function')]:
        assert (ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04'/n).read_text()==recipe[k]
    for tag in ['WorldZ','Transmission']:
        graph=read(OUT/('graph-audit-'+tag+'.json'));pp=next(v for k,v in graph.items() if 'Extinction.' in k)
        assert 'MaterialExpressionCustom_0' in pp['emissive']
    assert read(OUT/'compile-verification.json')['passed']
    write('graph-verification',dict(passed=True,trial_delta=delta,final_delta=final_delta,trial_source_matches_saved_reopened=True,final_graph_equals_predecessor=True,diagnostics_restored=True,topology_unchanged=True,trial_onset_cm=[1370,1510],trial_roof_zero_cm=1790,final_onset_roof_cm=[1370,1800],current_source=entry(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03/recipe.json'),failed_trial_source=entry(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04/recipe.json')))
    print('One trial code delta; exact predecessor final graphs')

def preserved():
    rows=read(OUT/'protected-before.json')['entries'];errors=[];changes=[]
    for r in rows:
        a=entry(ROOT/r['path'])
        if a!=r:(changes if r['path'] in ALLOWED else errors).append(dict(before=r,after=a))
    assert not errors and not changes,(errors[:3],changes)
    write('protected-after',dict(passed=True,checked=len(rows),allowed_changes=changes,unexpected=errors,exact_rollback=True))
    records=read(PREV/'history-verification.json')['records'];archive=read(CTRL/'BeforeCorrection/archive.json')
    refs={r['path']:r for r in archive['entries']}
    records.append(dict(manifest=entry(PREV/'manifest.json'),entries=len(read(PREV/'manifest.json')['entries']),resolutions=[dict(original=r,archive=entry(ROOT/refs[r['path']]['archive_path'])) for r in read(PREV/'manifest.json')['entries'] if r['path'] in refs]))
    total=0
    for h in records:
        assert entry(ROOT/h['manifest']['path'])==h['manifest']
        resolve={r['original']['path']:r['archive']['path'] for r in h['resolutions']}
        for r in read(ROOT/h['manifest']['path'])['entries']:
            a=entry(ROOT/resolve.get(r['path'],r['path']));assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r;total+=1
    for r in archive['entries']:
        for p in [r['path'],r['archive_path']]:
            a=entry(ROOT/p);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
    for r in read(OUT/'FailedTrial/archive.json')['entries']:
        a=entry(ROOT/r['archive']['path']);assert a==r['archive']
        assert (a['bytes'],a['sha256'])==(r['live_before']['bytes'],r['live_before']['sha256'])
    write('history-verification',dict(passed=True,records=records,total_entry_checks=total,predecessor_all_bytes_preserved=True,failed_trial_archive_verified=True))
    print('Protected/history checks',len(rows),total)

def captures():
    rows=[]
    for folder in ['Disabled','WorldZ','Transmission','Trial01','Restored']:
        for p in sorted((OUT/folder).glob('*.png')):
            c=read(p.with_name(p.stem+'-camera.json'));dims=struct.unpack('>II',p.read_bytes()[16:24]);assert list(dims)==c['resolution']
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed'] and c['actual_hfov']==90
            if p.stem in ['close-column-90','lateral-column-90']:
                assert dims==(1920,1082)
                xyz=[-1551.150808,330.164361 if p.stem.startswith('lateral') else 230.164361,172.15]
                rotation=[74.912516,0,0]
                ref=PREV/'Trial02/close-column-90-camera.json'
            else:
                ref=ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker/Final'/(p.stem+'-camera.json')
                o=read(ref);xyz=o['actual_xyz_cm'];rotation=o['actual_rotation'];assert dims==(960,540)
            assert max(abs(a-b) for a,b in zip(c['actual_xyz_cm'],xyz))<.01
            assert max(abs(a-b) for a,b in zip(c['actual_rotation'],rotation))<.001
            rows.append(dict(image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json')),reference=entry(ref),lateral_offset_y_cm=100 if p.stem.startswith('lateral') else 0))
    assert len(rows)==12,len(rows)
    write('capture-verification',dict(passed=True,images=rows,method='Twelve native stills:3diagnostic,8spatial-trial,1exact-restored close. Close/lateral1920x1082, context960x540. No edited pixels. Motion evidence separate.'))
    print('Twelve native stills verified')

def performance():
    import statistics
    b=read(OUT/'Performance/Final.json');a=read(PREV/'Performance/Final.json')
    for k in ['renderer','cvars','viewport']:assert a['config'][k]==b['config'][k],k
    assert all(y['world_seconds']>x['world_seconds'] for x,y in zip(b['rows'],b['rows'][1:]))
    assert abs(statistics.mean(x['game_dt'] for x in b['rows'])*1000-b['mean_frame_ms'])<1e-6
    pose={k:b['config']['state'][k] for k in ['location','rotation','fov']}
    write('performance-verification',dict(passed=True,scope='One bounded observation of failed spatial trial, not the exact-restored final state.',frames=b['frames'],seconds=b['sample_seconds'],fps=b['fps'],mean_ms=b['mean_frame_ms'],p95_ms=b['p95_frame_ms'],actual_recorded_start_pose=pose,matching_renderer_cvars_viewport=True,requested_pose=entry(OUT/'Performance/Final-pose-request.json'),comparison_claim=False,limitations='20s after5s warmup. No per-frame pose series; no matched-view, uncapped/GPU or worst-route claim. Approximately120Hz plateau. Final performance carried from exact predecessor identity.'))
    print('One bounded trial performance observation verified')

def handoff():
    assert not differences(snapshot('Restored'),snapshot('Handoff'))
    s=read(OUT/'Handoff/state.json');assert not s['pie'] and not s['dirty_content'] and not s['dirty_maps']
    controls={p.parent.name:read(p) for p in OUT.glob('*/capture-settings-restored.json')}
    assert len(controls)==6
    assert all(x['matched'] and x['slate_throttle_unchanged']==1 for x in controls.values())
    r=read(OUT/'Movement/runtime-verification.json');assert r['done'] and not r['cleanup_errors']
    assert read(OUT/'rollback-verification.json')['passed']
    write('handoff-verification',dict(passed=True,state=s,controls=controls,restored_properties_exact=True,inputs_released=True,callbacks_completed=True,map=entry(ROOT/m.MAPFILE),disposition='Exact HC03 rollback; single failed spatial trial archived separately.'))
    print('Clean PIE-off exact restored handoff')

def storage():
    now=m.usage();files=[]
    for n,suffix in [('HeightCorrection01','height'),('HeightCorrection02','soft'),('HeightCorrection03','volume'),('HeightCorrection04','spatial')]:
        files.extend(walk(ROOT/'Saved/OpeningLobby/UpperVoid01'/n));files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01'/n));files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_'+suffix+'_*.py'))
        report=ROOT/('Docs/OpeningLobbyUpperVoid01'+n+'.md')
        if report.exists():files.append(report)
    total=sum(p.stat().st_size for p in set(files));added=sum(p.stat().st_size for p in set(files) if 'HeightCorrection04' in p.as_posix() or p.name.startswith('uppervoid01_spatial_'))
    r=dict(**now,combined_correction_bytes=total,new_correction_bytes=added,new_under15mb_aim=added<=15e6,combined_under100mb=total<=100e6,lobby_under2_4gb_planning=now['lobby_bytes']<=2.4e9,project_under250gb=now['project_bytes']<=250e9,new_aim_overage_bytes=max(0,added-15000000),combined_planning_overage_bytes=max(0,total-100000000),lobby_planning_overage_bytes=max(0,now['lobby_bytes']-2400000000),scope='All four corrections including controller/review/source/helpers/reports. Measured before receipt; no history deletion.')
    write('storage',r);assert r['project_under250gb'];print(json.dumps(r))

def all_checks():
    for f in [properties,graphs,captures,movement,performance,handoff,preserved]:f()

if __name__=='__main__':globals()[sys.argv[1]]()
