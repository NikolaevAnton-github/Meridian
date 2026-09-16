"""Reuse proven validators with this correction's explicit deltas and references."""
import json,sys,gzip,re,struct,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'Scripts/OpeningLobby/uppervoid01_soft_check.py'
s=p.read_text().replace("UpperVoid01/HeightCorrection02/Worker","UpperVoid01/HeightCorrection03/Worker").replace("UpperVoid01/HeightCorrection01/Worker","UpperVoid01/HeightCorrection02/Worker").replace("uppervoid01_soft_","uppervoid01_volume_")
s=s.replace("read(PREV/'Handoff/all-properties.json')","json.loads(gzip.open(PREV/'Handoff/all-properties.json.gz','rt',encoding='utf-8').read())")
# Material edits do not touch controller-owned files, but controller may update its logs.
m=types.ModuleType('inherited_checks');exec(compile(s,str(p),'exec'),m.__dict__)
OUT=m.OUT;PREV=m.PREV;CTRL=m.CTRL
entry=m.entry;read=m.read;walk=m.walk;write=m.write;snapshot=m.snapshot;differences=m.differences
prepare=m.prepare
movement=m.movement

def properties():
    before=snapshot('Before');after=snapshot('Reopened')
    assert not differences(snapshot('Candidate'),after)
    ds=differences(before,after);expected={}
    for name,a in before['actors'].items():
        c=a.get('components',{}).get('LightComponent0',{}).get('properties',{})
        if c.get('intensity')==20000 and c.get('specularScale')==0.05000000074505806:
            expected['/actors/'+name+'/components/LightComponent0/properties/intensity']=(20000,100000)
            expected['/actors/'+name+'/components/LightComponent0/properties/specularScale']=(c['specularScale'],0.20000000298023224)
    assert len(ds)==len(expected)==12,(ds,expected)
    for d in ds:assert (d['before'],d['after'])==expected[d['path']],d
    a=read(OUT/'Reopened/inventory.json');b=read(PREV/'Handoff/inventory.json')
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    assert len(a)==108 and [{k:r[k] for k in keys} for r in a]==[{k:r[k] for k in keys} for r in b]
    write('property-preservation',dict(passed=True,actors=129,components=150,lobby_bindings=107,separate_support_components=1,unexpected=0,scheduled_deltas=ds,twelve_aisle_lights_exact=True,candidate_reopened_exact=True))
    print('Complete properties: only twelve authorized central-light restorations')

def preserved():
    rows=read(OUT/'protected-before.json')['entries'];changed=[];errors=[]
    for r in rows:
        a=entry(ROOT/r['path'])
        if a!=r:(changed if r['path'] in m.ALLOWED else errors).append(dict(before=r,after=a))
    write('protected-after',dict(passed=not errors,checked=len(rows),allowed_changes=changed,unexpected=errors));assert not errors,errors[:3]
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
        a=entry(ROOT/r['archive_path']);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
    write('history-verification',dict(passed=True,records=records,total_entry_checks=total,predecessor_all_bytes_preserved=True))
    print('Protected/history checks',len(rows),total)

def graphs():
    import copy
    old=read(PREV/'graph-audit-Reopened.json');new=read(OUT/'graph-audit-Reopened.json')
    reduced=copy.deepcopy(new)
    pp=next(k for k in new if 'Extinction.' in k)
    camera=reduced[pp]['nodes'].pop('MaterialExpressionCameraPositionWS_0')
    assert camera['properties']['class_path']=='/Script/Engine.MaterialExpressionCameraPositionWS' and not camera['inputs']
    custom=reduced[pp]['nodes']['MaterialExpressionCustom_0']
    extra=custom['properties']['properties']['inputs'].pop()
    assert extra['inputName']=='CameraCm' and extra['input']['expression']['refPath']==pp+':MaterialExpressionCameraPositionWS_0'
    connection=custom['inputs'].pop();assert ':MaterialExpressionCameraPositionWS_0' in connection
    ds=differences(old,reduced)
    recipe=read(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03/recipe.json')
    write('graph-differences',ds)
    semantic=[];pointer=[];stats=[];topology=[]
    for d in ds:
        if 'before' not in d or 'after' not in d:
            topology.append(d);continue
        if isinstance(d['before'],str) and isinstance(d['after'],str) and re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['before'])==re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['after']):pointer.append(d);continue
        if '/statistics/' in d['path']:stats.append(d);continue
        if not d['path'].endswith('/properties/properties/code'):
            topology.append(d);continue
        assert d['after'] in [recipe['postprocess'],recipe['light_function']],d
        semantic.append(d)
    assert len(semantic)==2
    for d in differences(read(OUT/'graph-audit-Candidate.json'),new):
        assert isinstance(d['before'],str) and isinstance(d['after'],str) and re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['before'])==re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['after']),d
    for name,k in [('Extinction.hlsl','postprocess'),('LightTransmission.hlsl','light_function')]:assert (ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03'/name).read_text()==recipe[k]
    assert not topology,topology
    write('graph-verification',dict(passed=True,scheduled=semantic,statistics_changes=stats,pointer_only=pointer,topology_changes=dict(added_camera_node=camera,added_input=extra,added_connection=connection),source_matches_saved_reopened=True,fade_cm=[1370,1780],normalization='Only transient object addresses; added CameraPositionWS node and fourth custom input separately verified then removed for exhaustive predecessor comparison.'))
    print('Saved/reopened graphs and source verified')

def captures():
    rows=[]
    for folder in ['IsolatePP','IsolateLF','Trial01','Trial02','Final']:
        for p in sorted((OUT/folder).glob('*.png')):
            c=read(p.with_name(p.stem+'-camera.json'));dims=struct.unpack('>II',p.read_bytes()[16:24]);assert list(dims)==c['resolution']
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed'] and c['actual_hfov']==90
            if p.stem=='close-column-90':
                assert dims==(1920,1082)
                ref=PREV/'Trial02/close-column-90-camera.json'
            else:ref=ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker/Final'/(p.stem+'-camera.json')
            o=read(ref)
            assert max(abs(a-b) for a,b in zip(c['actual_xyz_cm'],o['actual_xyz_cm']))<.01
            assert max(abs(a-b) for a,b in zip(c['actual_rotation'],o['actual_rotation']))<.001
            rows.append(dict(image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json')),reference=entry(ref),same_pixel_dimensions=p.stem=='close-column-90'))
    write('capture-verification',dict(passed=True,images=rows,method='Native exact 1920x1082 close diagnostic; 960x540 pose-matched regression views. No pixel edits.'))
    print('Native capture metadata checked',len(rows))

def performance():
    a=read(PREV/'Performance/Final.json');b=read(OUT/'Performance/Final.json')
    for k in ['renderer','cvars','viewport']:assert a['config'][k]==b['config'][k],k
    pose_match=all(a['config']['state'][k]==b['config']['state'][k] for k in ['location','rotation','fov'])
    assert all(y['world_seconds']>x['world_seconds'] for x,y in zip(b['rows'],b['rows'][1:]))
    write('performance-verification',dict(passed=True,scope='Bounded frame sample valid; matched-pose comparison NOT VERIFIED',predecessor=entry(PREV/'Performance/Final.json'),frames=b['frames'],seconds=b['sample_seconds'],fps=b['fps'],mean_ms=b['mean_frame_ms'],p95_ms=b['p95_frame_ms'],matching_renderer_cvars_viewport=True,matching_pose=pose_match,recorded_start_pose={k:b['config']['state'][k] for k in ['location','rotation','fov']},requested_pose_receipt=entry(OUT/'Performance/Final-pose-request.json'),comparative_ratio=None,limitations='One 20-second sample after 5-second warmup. Recorded start pose differs from requested axis after settling; cause not established. No continuous pose telemetry, stationary or predecessor performance comparison claim. 120Hz plateau; no standalone/GPU-stage/worst-route claim. No extra sample beyond task bound.'))

def handoff():
    assert not differences(snapshot('Reopened'),snapshot('Handoff'))
    s=read(OUT/'Handoff/state.json');assert not s['pie'] and not s['dirty_content'] and not s['dirty_maps']
    controls={p.parent.name:read(p) for p in OUT.glob('*/capture-settings-restored.json')}
    assert all(x['matched'] and x['slate_throttle_unchanged']==1 for x in controls.values())
    r=read(OUT/'Movement/runtime-verification.json');assert r['done'] and not r['cleanup_errors']
    write('handoff-verification',dict(passed=True,state=s,controls=controls,reopened_properties_exact=True,inputs_released=True,callbacks_completed=True,map=entry(ROOT/m.MAPFILE)))

def storage():
    now=m.usage();files=[]
    for n,suffix in [('HeightCorrection01','height'),('HeightCorrection02','soft'),('HeightCorrection03','volume')]:
        files.extend(walk(ROOT/'Saved/OpeningLobby/UpperVoid01'/n));files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01'/n));files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_'+suffix+'_*.py'))
        report=ROOT/('Docs/OpeningLobbyUpperVoid01'+n+'.md')
        if report.exists():files.append(report)
    total=sum(p.stat().st_size for p in set(files));added=sum(p.stat().st_size for p in set(files) if 'HeightCorrection03' in p.as_posix() or p.name.startswith('uppervoid01_volume_'))
    r=dict(**now,combined_correction_bytes=total,new_correction_bytes=added,combined_under100mb=total<=100e6,new_under15mb_aim=added<=15e6,project_under250gb=now['project_bytes']<=250e9,lobby_planning_under2_4gb=now['lobby_bytes']<=2.4e9,lobby_overage_bytes=max(0,now['lobby_bytes']-2400000000),combined_planning_overage_bytes=max(0,total-100000000),scope='All three correction folders/controller/review/source/helpers/reports. No history deletion. Before this receipt.')
    write('storage',r);assert r['project_under250gb'];print(json.dumps(r))

if __name__=='__main__':globals()[sys.argv[1]]()
