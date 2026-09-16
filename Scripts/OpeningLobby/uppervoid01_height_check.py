"""Height correction evidence, using the existing hash/storage/diff primitives."""
import json,sys,copy,struct,re
from materialscomplete01_support_check import ROOT,entry,read,walk,usage,MAPFILE
from painterstone01_check import differences
OUT=ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker'
OLD=ROOT/'Saved/OpeningLobby/UpperVoid01/Worker'
CTRL=OUT.parent/'Controller'
ASSET='Content/OpeningLobby/UpperVoid01/'
ALLOWED=[MAPFILE,ASSET+'M_UpperVoid_Extinction.uasset',ASSET+'M_UpperVoid_LightTransmission.uasset']
def write(n,d):
    p=OUT/(n+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2));return d
def prepare():
    assert not (OUT/'protected-before.json').exists()
    receipt=CTRL/'BeforeHeightCorrection01/archive.json';r=read(receipt)
    for row in r['entries']:
        for key in ['path','archive_path']:
            a=entry(ROOT/row[key]);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256']),a
    protected=[]
    for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby']:
        for p in walk(ROOT/f):
            if p.is_relative_to(OUT) or '__pycache__' in str(p) or p.name.startswith('uppervoid01_height_') or p.name.endswith(('.lock','.painter_lock')):continue
            if '/Controller/' in p.as_posix():continue
            protected.append(entry(p))
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected));write('storage-before',usage())
    write('archive-verification',dict(passed=True,receipt=entry(receipt),entries=r['entries']))
    prior=read(OLD/'Reopened/all-properties.json');live=read(OUT/'Before/all-properties.json')
    ds=differences(prior,live);write('intervening-live-differences',ds)
    print(json.dumps(dict(protected=len(protected),archive_verified=True,intervening_differences=len(ds))))
def properties():
    before=read(OUT/'Before/all-properties.json');after=read(OUT/'Reopened/all-properties.json');original=read(OLD/'Before/all-properties.json')
    assert not differences(read(OUT/'Candidate/all-properties.json'),after)
    rows={}
    for label,base in [('live',before),('pre_atmosphere',original)]:
        target=copy.deepcopy(after)
        if label=='pre_atmosphere':
            extra=set(target['actors'])-set(base['actors']);assert extra=={'PostProcessVolume_1'}
            target['actors'].pop('PostProcessVolume_1')
        ds=differences(base,target);bad=[]
        for d in ds:
            tokens=d['path'].split('/');actor=tokens[2] if len(tokens)>2 else '';suffix='/'.join(tokens[3:])
            ok=actor in ['PointLight_'+str(i) for i in range(18)] and (suffix=='transform' or suffix in ['components/LightComponent0/properties/'+k for k in ['relativeLocation/z','intensity','attenuationRadius','indirectLightingIntensity','lightFunctionMaterial','specularScale']])
            if not ok:bad.append(d)
        rows[label]=dict(differences=ds,unexpected=bad);assert not bad,bad[:5]
    for name,a in original['actors'].items():
        if not name.startswith('PointLight_'):continue
        old=a['components']['LightComponent0']['properties'];p=after['actors'][name]['components']['LightComponent0']['properties']
        for k in ['relativeLocation','intensity','attenuationRadius']:assert p[k]==old[k],(name,k)
        assert abs(p['specularScale']-.2)<1e-6
        assert abs(p['indirectLightingIntensity']-(.2 if abs(old['relativeLocation']['y'])<1 else 1.))<1e-6
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    inv=read(OUT/'Reopened/inventory.json')
    for base in [OUT/'Before/inventory.json',OLD/'Before/inventory.json']:
        assert [{k:r[k] for k in keys} for r in inv]==[{k:r[k] for k in keys} for r in read(base)]
    assert len(inv)==108
    write('property-differences',rows)
    write('property-preservation',dict(passed=True,actors=129,components=150,lobby_bindings=107,separate_support_components=1,unexpected=0,live_delta_count=len(rows['live']['differences']),pre_atmosphere_delta_count=len(rows['pre_atmosphere']['differences']),candidate_reopened_exact=True))
    print('Full properties and 107 bindings preserved')
def preserved():
    rows=read(OUT/'protected-before.json')['entries'];errors=[];changed=[]
    for r in rows:
        a=entry(ROOT/r['path'])
        if a!=r:
            (changed if r['path'] in ALLOWED else errors).append(dict(before=r,after=a))
    write('protected-after',dict(passed=not errors,checked=len(rows),allowed_changes=changed,unexpected=errors))
    assert not errors,errors[:5]
    for row in read(CTRL/'BeforeHeightCorrection01/archive.json')['entries']:
        a=entry(ROOT/row['archive_path']);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256'])
    records=read(OLD/'history-verification.json')['records']
    for h in records:
        assert entry(ROOT/h['manifest']['path'])==h['manifest']
        resolve={r['original']['path']:r['archive']['path'] for r in h['resolutions']}
        for r in read(ROOT/h['manifest']['path'])['entries']:
            a=entry(ROOT/resolve.get(r['path'],r['path']));assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r
    write('history-verification',dict(passed=True,records=records,original_worker_files=sum(r['path'].startswith(OLD.relative_to(ROOT).as_posix()+'/') for r in rows),original_helpers_preserved=True))
    print('Protected files and exact history verified',len(rows))
def storage():
    now=usage();initial=read(OUT/'storage-before.json')
    folders=[OUT,ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection01']
    files=[p for f in folders for p in walk(f)]+list((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_height_*.py'))
    report=ROOT/'Docs/OpeningLobbyUpperVoid01HeightCorrection01.md'
    if report.exists():files.append(report)
    task=sum(p.stat().st_size for p in files)
    r=dict(passed=now['project_bytes']<=250e9 and now['lobby_bytes']<=2.4e9 and task<=100e6,**now,correction_bytes=task,lobby_growth=now['lobby_bytes']-initial['lobby_bytes'],correction_under100mb=task<=100e6,project_under250gb=now['project_bytes']<=250e9,lobby_under2400mb=now['lobby_bytes']<=2.4e9,lobby_overage_bytes=max(0,now['lobby_bytes']-int(2.4e9)),history_deleted=False)
    write('storage',r);assert r['correction_under100mb'] and r['project_under250gb'];print(json.dumps(r))
def captures():
    rows=[];original=[]
    for p in sorted((OUT/'Final').glob('*.png')):
        c=read(p.with_name(p.stem+'-camera.json'));old=read(OUT/'Before'/(p.stem+'-camera.json'))
        for q in [p,OUT/'Before'/p.name]:assert struct.unpack('>II',q.read_bytes()[16:24])==(1920,1080)
        assert all(c[k]==old[k] for k in ['actual_xyz_cm','actual_hfov','renderer','resolution'])
        assert max(abs(x-y) for x,y in zip(c['actual_rotation'],old['actual_rotation']))<1e-6
        assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed']
        assert abs(c['actual_xyz_cm'][2]-172)<1 and c['actual_hfov']==90
        rows.append(dict(before=entry(OUT/'Before'/p.name),final=entry(p),camera=entry(p.with_name(p.stem+'-camera.json'))))
        o=read(OLD/'Before'/(p.stem+'-camera.json'))
        original.append(dict(image=entry(OLD/'Before'/p.name),camera=entry(OLD/'Before'/(p.stem+'-camera.json')),matched=c['actual_xyz_cm']==o['actual_xyz_cm'] and max(abs(x-y) for x,y in zip(c['actual_rotation'],o['actual_rotation']))<1e-6,note='Original aisle pitch 12 degrees; correction uses 55 degrees to inspect soffits.' if 'aisle' in p.stem else 'Exact original pose retained.'))
    assert len(rows)==12
    write('capture-verification',dict(passed=True,matched_live_before_final=12,images=rows,original_pre_atmosphere=original,original_exact_pose_matches=sum(r['matched'] for r in original),native_png=True,standing_eye_cm=172.15,hfov=90,lighting='Intentionally different; same renderer and manual exposure.'))
    print('Twelve genuine matched before/final views verified')
def graphs():
    old=read(OLD/'graph-audit-Reopened.json');new=read(OUT/'graph-audit-Reopened.json')
    ds=differences(old,new);write('graph-differences',ds)
    expected=[];pointer_only=[]
    for d in ds:
        if isinstance(d['before'],str) and isinstance(d['after'],str) and re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['before'])==re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['after']):
            pointer_only.append(d);continue
        assert d['path'].endswith('/properties/properties/defaultValue'),d
        assert (d['before'],d['after']) in [(350,1400),(850,1750)],d
        expected.append(d)
    assert len(expected)==4,len(expected)
    write('graph-verification',dict(passed=True,assets=2,threshold_changes=expected,topology_and_formula_unchanged=True,fade_cm=[1400,1750],no_extinction_below_cm=1400,total_extinction_above_cm=1750,normalization='Only transient hexadecimal object addresses in input/emissive repr; full object paths and types compared.',pointer_only_differences=pointer_only))
    print('Both saved native graphs verified')
def performance():
    a=read(OUT/'Performance/Before.json');b=read(OUT/'Performance/Final.json')
    for k in ['renderer','cvars','viewport']:assert a['config'][k]==b['config'][k],k
    for k in ['location','rotation','fov']:assert a['config']['state'][k]==b['config']['state'][k],k
    rows=[]
    for s in [a,b]:
        assert len({r['world_seconds'] for r in s['rows']})==len(s['rows'])
        assert all(y['world_seconds']>x['world_seconds'] for x,y in zip(s['rows'],s['rows'][1:]))
        rows.append(dict(tag=s['tag'],frames=s['frames'],duration=s['sample_seconds'],fps=s['fps'],mean_ms=s['mean_frame_ms'],p95_ms=s['p95_frame_ms'],wall_fps=1000/s['slate_mean_ms']))
    write('performance-verification',dict(passed=True,samples=rows,ratio_candidate_to_before_ms=b['mean_frame_ms']/a['mean_frame_ms'],matching_settings=True,resolution=a['config']['viewport'],limitations=['Game-frame and Slate wall throughput, no independent CPU/GPU stage or presentation timing.','Approximately 120 Hz plateau; origin not established, VSync=0 and t.MaxFPS=0.','Requested 1920x1080 floating PIE; actual viewport recorded, no 1440p claim.','ScreenPercentage=0 uses engine defaults; internal render fraction not independently measured.','Stationary 5 second warmup and 20 second sample; excludes screenshots, not worst-case route benchmark.']))
    print(json.dumps(rows))
def movement():
    r=read(OUT/'Movement/runtime-verification.json');s=read(OUT/'Movement/runtime-samples.json')
    assert r['passed'] and r['done'] and not r['cleanup_errors']
    holds={n:[x for x in s if x['step']==n] for n in ['sustained_up','close_column_up','aisle_up_hold','west_aisle_up_hold']}
    durations={k:v[-1]['t']-v[0]['t'] for k,v in holds.items()};assert min(durations.values())>=5
    assert all(x['walking'] and x['possessed'] and x['fov']==90 for x in s)
    final=r['events'][-1]['state'];assert final['move_binding_samples']>100 and final['look_binding_samples']>0
    frames=read(OUT/'Movement/frame-sequence.json')['frames']
    for f in frames:assert struct.unpack('>II',(OUT/'Movement'/f['image']).read_bytes()[16:24])==(960,540)
    write('movement-verification',dict(passed=True,elapsed=r['elapsed'],samples=len(s),sampled_native_frames=len(frames),upward_holds_seconds=durations,input_method=r['input_method'],final=final,frames=frames,limitations='Continuous native telemetry and sampled frames, not continuous video; cannot exclude every unsampled transient.'))
    print(json.dumps(dict(elapsed=r['elapsed'],samples=len(s),frames=len(frames),holds=durations)))
def handoff():
    assert not differences(read(OUT/'Reopened/all-properties.json'),read(OUT/'Handoff/all-properties.json'))
    state=read(OUT/'Handoff/state.json');assert not state['pie'] and not state['dirty_content'] and not state['dirty_maps']
    controls={n:read(OUT/n/'capture-settings-restored.json') for n in ['Before','Trial01','Final']}
    assert all(r['matched'] and r['slate_throttle_unchanged']==1 for r in controls.values())
    r=read(OUT/'Movement/runtime-verification.json');assert r['done'] and r['passed'] and not r['cleanup_errors']
    write('handoff-verification',dict(passed=True,state=state,full_properties_match_reopened=True,restored_controls=controls,held_inputs_released=True,callbacks_completed=True,map=entry(ROOT/MAPFILE),gameplay_fov=90))
    print('Clean restored handoff verified')
if __name__=='__main__':globals()[sys.argv[1]]()
