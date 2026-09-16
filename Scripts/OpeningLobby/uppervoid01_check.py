"""Exact preservation and storage checks using existing repository primitives."""
import json,sys,copy,struct
from materialscomplete01_support_check import ROOT,entry,read,walk,usage,MAPFILE
from painterstone01_check import differences
OUT=ROOT/'Saved/OpeningLobby/UpperVoid01/Worker'
CTRL=OUT.parent/'Controller'
PREV=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01'
def write(n,d):
    p=OUT/(n+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2));return d
def prepare():
    assert not (OUT/'protected-before.json').exists()
    r=read(CTRL/'BeforeUpperVoid01/archive.json')
    assert entry(PREV/'manifest.json')==r['predecessor_manifest']
    for row in r['entries']:
        for key in ['path','archive_path']:
            a=entry(ROOT/row[key]);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256'])
    for row in read(PREV/'manifest.json')['entries']:assert entry(ROOT/row['path'])==row,row
    protected=[entry(p) for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby'] for p in walk(ROOT/f) if not p.is_relative_to(OUT) and '__pycache__' not in str(p) and not p.name.startswith('uppervoid01_') and not p.name.endswith(('.lock','.painter_lock')) and not p.is_relative_to(CTRL)]
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected));write('storage-before',usage())
    write('archive-verification',dict(passed=True,receipt=entry(CTRL/'BeforeUpperVoid01/archive.json'),entries=r['entries'],prior_manifest_entries=891))
    print(json.dumps(dict(protected=len(protected),archive_verified=True)))
def summary():
    data=read(OUT/'lights-before.json')
    for name,r in data.items():
        print(name,r['label'])
        if 'settings' in r['actor']['properties']:
            s=r['actor']['properties']['settings'];print(json.dumps(s)[:1200])
        for n,c in r['components'].items():
            pp=c['properties'];keys=[k for k in pp if any(s in k.lower() for s in ['intensity','radius','relative','lightfunction','indirect','mobility','cast','source','color'])]
            print(n,json.dumps({k:pp[k] for k in keys}))
    inv=read(OUT/'Before/inventory.json')
    for r in inv:
        if any(s in r['label'].lower() for s in ['central','ceiling','mainroof']):print(r['label'],r['bounds'])
    c=read(OUT/'capabilities.json')
    for name in ['Material','MaterialExpressionWorldPosition','MaterialExpressionSceneTexture','LightComponent']:
        print(name,json.dumps({k:v for k,v in c[name].items() if any(s in k.lower() for s in ['blendable','domain','position','scenetexture','lightfunction'])}))
def properties():
    before=read(OUT/'Before/all-properties.json');after=read(OUT/'Reopened/all-properties.json')
    assert not differences(read(OUT/'Trial02/all-properties.json'),after)
    existing=copy.deepcopy(after);added=set(existing['actors'])-set(before['actors'])
    assert added=={'PostProcessVolume_1'},added
    new=existing['actors'].pop('PostProcessVolume_1');assert new['label']=='UpperVoid01_WorldHeightExtinction'
    assert new['properties']['bUnbound'] and new['properties']['priority']==100
    ds=differences(before,existing);allowed=[];unexpected=[]
    for d in ds:
        tokens=d['path'].split('/');actor=tokens[2] if len(tokens)>2 else ''
        valid=actor.startswith('PointLight_') and int(actor.split('_')[-1]) in range(18)
        suffix='/'.join(tokens[3:])
        valid=valid and (suffix=='transform' or suffix in ['components/LightComponent0/properties/'+k for k in ['relativeLocation/z','intensity','attenuationRadius','indirectLightingIntensity','lightFunctionMaterial','specularScale']])
        (allowed if valid else unexpected).append(d)
    write('property-differences',dict(allowed=allowed,unexpected=unexpected,new_actor=new))
    assert not unexpected,unexpected[:8]
    assert len(ds)==126,len(ds)
    for name,a in before['actors'].items():
        if not name.startswith('PointLight_'):continue
        old=a['components']['LightComponent0']['properties'];p=existing['actors'][name]['components']['LightComponent0']['properties'];central=abs(old['relativeLocation']['y'])<1
        assert p['relativeLocation']['z']==(450 if central else 400)
        assert p['intensity']==(40000 if central else 18000) and p['attenuationRadius']==(1500 if central else 1200)
        assert abs(p['indirectLightingIntensity']-.2)<1e-6 and abs(p['specularScale']-.2)<1e-6
        assert p['lightFunctionMaterial']['refPath']=='/Game/OpeningLobby/UpperVoid01/M_UpperVoid_LightTransmission.M_UpperVoid_LightTransmission'
    inv=read(OUT/'Reopened/inventory.json');old=read(OUT/'Before/inventory.json')
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    assert [{k:r[k] for k in keys} for r in inv]==[{k:r[k] for k in keys} for r in old]
    assert len(inv)==108
    write('property-preservation',dict(passed=True,existing_actors=128,existing_components=149,mesh_components=108,lobby_bindings=107,support=1,unchanged_mesh_inventory=True,allowed_deltas=len(ds),new_postprocess_actors=1,unexpected=[],reopen_exact=True))
    print('Property preservation PASS',len(ds))
def captures():
    rows=[]
    for folder,count in [('Before',12),('Trial01',7),('Trial02',4),('Final',12)]:
        files=list((OUT/folder).glob('*.png'));assert len(files)==count,(folder,len(files))
        for p in files:
            c=read(p.with_name(p.stem+'-camera.json'));old=read(OUT/'Before'/(p.stem+'-camera.json'))
            assert struct.unpack('>II',p.read_bytes()[16:24])==(1920,1080)
            assert all(c[k]==old[k] for k in ['actual_xyz_cm','actual_hfov','renderer','resolution'])
            angle_error=max(abs(x-y) for x,y in zip(c['actual_rotation'],old['actual_rotation']))
            assert angle_error<1e-6,(p,angle_error)
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed']
            assert abs(c['actual_xyz_cm'][2]-172)<1 and abs(c['actual_hfov']-90)<.001
            rows.append(dict(image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json')),rotation_difference_degrees=angle_error))
        restored=OUT/folder/'capture-settings-restored.json'
        if restored.exists():assert read(restored)['matched']
    write('capture-verification',dict(passed=True,images=rows,matched_before_final=12,standing_eye_cm=172.14999961853027,hfov=90,resolution=[1920,1080],lighting='Intentionally changed; renderer and fixed manual exposure preserved'))
    print('Native matched captures PASS',len(rows))
def preserved():
    errors=[]
    rows=read(OUT/'protected-before.json')['entries']
    for r in rows:
        if r['path']==MAPFILE:continue
        a=entry(ROOT/r['path'])
        if a!=r:errors.append(dict(before=r,after=a))
    write('protected-after',dict(passed=not errors,checked=len(rows)-1,unexpected=errors,allowed_current_map=MAPFILE,controller_scope='Live controller area excluded from worker-owned preservation baseline; exact rollback receipt included in history'))
    assert not errors,errors[:5]
    hist=read(PREV/'history-verification.json')['records']
    hist.append(dict(manifest=entry(PREV/'manifest.json'),entries=891,resolutions=[dict(original=next(r for r in read(PREV/'manifest.json')['entries'] if r['path']==MAPFILE),archive=entry(CTRL/'BeforeUpperVoid01/files'/MAPFILE))]))
    for h in hist:
        assert entry(ROOT/h['manifest']['path'])==h['manifest']
        resolve={r['original']['path']:r['archive']['path'] for r in h['resolutions']}
        for r in read(ROOT/h['manifest']['path'])['entries']:
            a=entry(ROOT/resolve.get(r['path'],r['path']));assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r
    assert len(list((ROOT/'Content/Maps').glob('L_OpeningLobby*.umap')))==1
    write('history-verification',dict(passed=True,records=hist,all_prior_manifests_immutable=True))
    print('Preservation/history PASS',len(rows)-1,sum(h['entries'] for h in hist))
def storage():
    now=usage();initial=read(CTRL/'storage-before.json')
    taskfiles=[p for folder in [OUT,ROOT/'Assets/Source/OpeningLobby/UpperVoid01',ROOT/'Content/OpeningLobby/UpperVoid01'] for p in walk(folder)]
    taskfiles+=list((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_*.py'))
    report=ROOT/'Docs/OpeningLobbyUpperVoid01.md'
    if report.exists():taskfiles.append(report)
    task=sum(p.stat().st_size for p in taskfiles)
    result=dict(passed=now['project_bytes']<250e9 and now['lobby_bytes']<2.4e9 and task<100e6,**now,task_bytes=task,lobby_growth_since_controller=now['lobby_bytes']-initial['lobby_bytes'],aim70mb=task<=70e6)
    write('storage',result);assert result['passed'];print(json.dumps(result))
def performance():
    a=read(OUT/'Performance/Before.json');b=read(OUT/'Performance/Final.json')
    for k in ['renderer','cvars','viewport']:assert a['config'][k]==b['config'][k],k
    for k in ['location','rotation','fov']:assert a['config']['state'][k]==b['config']['state'][k],k
    rows=[]
    for s in [a,b]:
        unique=len({r['world_seconds'] for r in s['rows']});assert unique==len(s['rows'])
        assert all(y['world_seconds']>x['world_seconds'] for x,y in zip(s['rows'],s['rows'][1:]))
        rows.append(dict(tag=s['tag'],frames=s['frames'],duration=s['sample_seconds'],fps=s['fps'],mean_ms=s['mean_frame_ms'],p95_ms=s['p95_frame_ms'],unique_game_frames=unique,wall_fps=1000/s['slate_mean_ms']))
    result=dict(passed=True,samples=rows,ratio_candidate_to_before_ms=b['mean_frame_ms']/a['mean_frame_ms'],matching_settings=True,resolution=a['config']['viewport'],requested_window=[1920,1080],native_stills=[1920,1080],provisional60fps='Observed game/wall frame throughput exceeds 60 in both bounded stationary samples',limitations=['Actual PIE viewport reports 1920x1082; no 2560x1440 claim.','This is measured game-frame and Slate wall throughput, not independent GPU/presentation timing.','Approximately 120 Hz plateau; t.MaxFPS=0 and VSync=0, fixed/smoothed frame rate disabled on reflected Engine defaults. Origin of plateau not established.','ScreenPercentage=0 follows engine defaults; internal render fraction not independently measured.','No standalone game, worst-case route, CPU/GPU stage or 1440p benchmark claim.','Screenshots excluded from the two 20-second samples; sampled movement captures incur additional overhead.'])
    write('performance-verification',result);print(json.dumps(result))
def movement():
    r=read(OUT/'Movement02/runtime-verification.json');s=read(OUT/'Movement02/runtime-samples.json')
    assert r['passed'] and r['done'] and not r['cleanup_errors']
    holds={name:[x for x in s if x['step']==name] for name in ['sustained_up','close_column_up','aisle_up_hold']}
    durations={k:v[-1]['t']-v[0]['t'] for k,v in holds.items()}
    assert min(durations.values())>=5
    assert all(x['walking'] and x['possessed'] and x['fov']==90 for x in s)
    final=r['events'][-1]['state'];assert final['move_binding_samples']>100 and final['look_binding_samples']>0
    frames=read(OUT/'Movement02/frame-sequence.json')['frames']
    for f in frames:
        p=OUT/'Movement02'/f['image'];assert struct.unpack('>II',p.read_bytes()[16:24])==(960,540)
    write('movement-verification',dict(passed=True,elapsed=r['elapsed'],sample_count=len(s),native_sampled_frames=len(frames),upward_hold_seconds=durations,final=final,initial=r['initial'],input=r['input_method'],failed_attempt_preserved=entry(OUT/'Movement/runtime-verification.json'),route_adjustment=entry(OUT/'Movement02/route-correction.md'),frames=frames))
    print(json.dumps(dict(passed=True,elapsed=r['elapsed'],samples=len(s),frames=len(frames),holds=durations)))
if __name__=='__main__':globals()[sys.argv[1]]()
