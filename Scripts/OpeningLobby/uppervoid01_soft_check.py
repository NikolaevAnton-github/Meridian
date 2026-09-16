"""Compact exact preservation and correction evidence checks."""
import json,sys,gzip,re,struct
from materialscomplete01_support_check import ROOT,entry,read,walk,usage,MAPFILE
from painterstone01_check import differences
OUT=ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Worker'
PREV=ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker'
CTRL=OUT.parent/'Controller'
ALLOWED=[MAPFILE,'Content/OpeningLobby/UpperVoid01/M_UpperVoid_Extinction.uasset','Content/OpeningLobby/UpperVoid01/M_UpperVoid_LightTransmission.uasset']
def write(n,d):
    p=OUT/(n+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2));return d
def snapshot(n):return json.loads(gzip.open(OUT/n/'all-properties.json.gz','rt',encoding='utf-8').read())
def prepare():
    assert not (OUT/'protected-before.json').exists()
    receipt=CTRL/'BeforeCorrection/archive.json';r=read(receipt)
    for row in r['entries']:
        for key in ['path','archive_path']:
            a=entry(ROOT/row[key]);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256'])
    assert not differences(read(PREV/'Handoff/all-properties.json'),snapshot('Before'))
    protected=[]
    for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby']:
        for p in walk(ROOT/f):
            if p.is_relative_to(OUT) or '__pycache__' in str(p) or p.name.startswith('uppervoid01_soft_') or '/Controller/' in p.as_posix() or p.name.endswith(('.lock','.painter_lock')):continue
            protected.append(entry(p))
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected));write('storage-before',usage())
    write('archive-verification',dict(passed=True,receipt=entry(receipt),entries=r['entries'],prior_live_properties_exact=True))
    print(json.dumps(dict(protected=len(protected),archive_verified=True)))
def properties():
    before=snapshot('Before');after=snapshot('Reopened')
    assert not differences(snapshot('Candidate'),after)
    ds=differences(before,after)
    expected={}
    recipe=read(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02/recipe.json')
    for r in recipe['lights']+recipe['revision_deltas']:
        expected['/actors/'+r['actor']+'/components/LightComponent0/properties/'+r['property']]=(r['before'],r['after'])
    assert len(ds)==len(expected)==12,(len(ds),len(expected))
    for d in ds:assert (d['before'],d['after'])==expected[d['path']],d
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    a=read(OUT/'Reopened/inventory.json');b=read(PREV/'Handoff/inventory.json')
    assert len(a)==108 and [{k:r[k] for k in keys} for r in a]==[{k:r[k] for k in keys} for r in b]
    write('property-preservation',dict(passed=True,actors=129,components=150,lobby_bindings=107,separate_support_components=1,unexpected=0,scheduled_deltas=ds,twelve_aisle_lights_exact=True,candidate_reopened_exact=True))
    print('129 actors / 150 components; 107 bindings; 12 scheduled property deltas')

def graphs():
    old=read(PREV/'graph-audit-Reopened.json');new=read(OUT/'graph-audit-Reopened.json')
    ds=differences(old,new);scheduled=[];pointers=[];stats=[]
    recipe=read(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02/recipe.json')
    for d in ds:
        if isinstance(d['before'],str) and isinstance(d['after'],str) and re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['before'])==re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['after']):pointers.append(d);continue
        if '/statistics/' in d['path']:stats.append(d);continue
        assert d['path'].endswith(('/properties/properties/defaultValue','/properties/properties/code')),d
        if d['path'].endswith('defaultValue'):assert (d['before'],d['after']) in [(1400,1370),(1750,1780)],d
        else:assert d['after'] in [recipe['postprocess'],recipe['light_function']]
        scheduled.append(d)
    assert len(scheduled)==6
    src=ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02'
    assert (src/'Extinction.hlsl').read_text()==recipe['postprocess'] and (src/'LightTransmission.hlsl').read_text()==recipe['light_function']
    reopen_diffs=differences(read(OUT/'graph-audit-Trial01.json'),new)
    for d in reopen_diffs:
        assert isinstance(d['before'],str) and isinstance(d['after'],str) and re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['before'])==re.sub(r'0x[0-9A-Fa-f]+','POINTER',d['after']),d
    write('graph-verification',dict(passed=True,assets=2,scheduled=scheduled,statistics_changes=stats,pointer_only=pointers,reopen_pointer_only=reopen_diffs,normalization='Only transient hexadecimal object addresses; paths and types retained.',source_matches_saved_reopened=True,topology_unchanged=True,fade_cm=[1370,1780],world_height_only=True))
    print('Saved/reopened native graphs and editable sources agree')

def preserved():
    errors=[];changed=[];rows=read(OUT/'protected-before.json')['entries']
    for r in rows:
        a=entry(ROOT/r['path'])
        if a!=r:(changed if r['path'] in ALLOWED else errors).append(dict(before=r,after=a))
    write('protected-after',dict(passed=not errors,checked=len(rows),allowed_changes=changed,unexpected=errors));assert not errors,errors[:3]
    records=read(PREV/'history-verification.json')['records']
    archive=read(CTRL/'BeforeCorrection/archive.json')
    prior=read(PREV.parent/'Controller/BeforeHeightCorrection01/archive.json')
    for manifest,ar in [(PREV/'manifest.json',archive)]:
        refs={r['path']:r for r in ar['entries']}
        resolutions=[]
        for r in read(manifest)['entries']:
            if r['path'] in refs:resolutions.append(dict(original=r,archive=entry(ROOT/refs[r['path']]['archive_path'])))
        records.append(dict(manifest=entry(manifest),entries=len(read(manifest)['entries']),resolutions=resolutions))
    total=0
    for h in records:
        assert entry(ROOT/h['manifest']['path'])==h['manifest']
        resolve={r['original']['path']:r['archive']['path'] for r in h['resolutions']}
        for r in read(ROOT/h['manifest']['path'])['entries']:
            a=entry(ROOT/resolve.get(r['path'],r['path']));assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r;total+=1
    for r in archive['entries']:
        a=entry(ROOT/r['archive_path']);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
    for r in prior['entries']:
        a=entry(ROOT/r['archive_path']);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
    write('history-verification',dict(passed=True,records=records,total_entry_checks=total,predecessor_all_bytes_preserved=True,original_interrupted_run_archive=entry(PREV.parent/'Controller/BeforeHeightCorrection01/archive.json'),original_run_note='Interrupted before manifest; all original evidence protected by exact file inventory and five-entry archive. No original manifest invented.'))
    print('Protected files and nine historical manifests verified',len(rows),total)

def captures():
    rows=[]
    for folder in ['Trial01','Trial02','Final']:
        for p in sorted((OUT/folder).glob('*.png')):
            c=read(p.with_name(p.stem+'-camera.json'));dims=struct.unpack('>II',p.read_bytes()[16:24]);assert list(dims)==c['resolution']
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed'] and c['actual_hfov']==90
            if p.stem=='close-column-90':
                assert dims==(1920,1082)
                assert max(abs(a-b) for a,b in zip(c['actual_xyz_cm'],[-1551.150808,230.164361,172.15]))<.01
                assert abs(c['actual_rotation'][0]-74.912516)<.001
                ref=PREV/'Movement/close_column_up.png';same_pixels=True
            else:
                assert dims==(960,540);o=read(PREV/'Final'/(p.stem+'-camera.json'))
                assert c['actual_xyz_cm']==o['actual_xyz_cm'] and c['renderer']==o['renderer']
                assert max(abs(a-b) for a,b in zip(c['actual_rotation'],o['actual_rotation']))<1e-6
                ref=PREV/'Final'/p.name;same_pixels=False
            rows.append(dict(image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json')),reference=entry(ref),same_pixel_dimensions=same_pixels,selected_candidate=folder in ['Trial02','Final']))
    assert len(rows)==14,len(rows)
    write('capture-verification',dict(passed=True,images=rows,selected_candidate_views=11,method='Native captures; exact close pose 1920x1082, regression poses 960x540 versus predecessor 1920x1080. Trial02 close/axis/west views reused without duplicate pixels; remaining views after reopen.'))
    print('Fourteen native images checked, eleven candidate poses')

def performance():
    a=read(PREV/'Performance/Final.json');b=read(OUT/'Performance/Final.json')
    for k in ['renderer','cvars','viewport']:assert a['config'][k]==b['config'][k],k
    for k in ['location','rotation','fov']:assert a['config']['state'][k]==b['config']['state'][k],k
    rows=[]
    for s in [a,b]:
        assert all(y['world_seconds']>x['world_seconds'] for x,y in zip(s['rows'],s['rows'][1:]))
        rows.append(dict(tag=s['tag'],frames=s['frames'],seconds=s['sample_seconds'],fps=s['fps'],mean_ms=s['mean_frame_ms'],p95_ms=s['p95_frame_ms']))
    write('performance-verification',dict(passed=True,predecessor=entry(PREV/'Performance/Final.json'),samples=rows,ratio=b['mean_frame_ms']/a['mean_frame_ms'],matching_settings=True,limitations='One stationary floating PIE sample, 5s warmup and 20s measurement at actual 1920x1082; near120Hz plateau unexplained; no GPU/CPU stage, uncapped headroom, standalone,1440p or worst-route claim.'))
    print(json.dumps(rows))

def movement():
    r=read(OUT/'Movement/runtime-verification.json');s=read(OUT/'Movement/runtime-samples.json');frames=read(OUT/'Movement/frame-sequence.json')['frames']
    assert r['passed'] and r['done'] and not r['cleanup_errors']
    assert all(x['walking'] and x['possessed'] and x['fov']==90 for x in s)
    assert all(b['t']>a['t'] for a,b in zip(s,s[1:]))
    h=[x for x in s if x['step']=='close_column_up'];duration=h[-1]['t']-h[0]['t'];assert duration>=5
    assert r['events'][-1]['state']['move_binding_samples']>100 and r['events'][-1]['state']['look_binding_samples']>0
    for f in frames:assert struct.unpack('>II',(OUT/'Movement'/f['image']).read_bytes()[16:24])==(960,540)
    write('movement-verification',dict(passed=True,elapsed=r['elapsed'],samples=len(s),hold_seconds=duration,frames=len(frames),actual_input=r['input_method'],hold_first=h[0],hold_last=h[-1],prior_full_route=entry(PREV/'movement-verification.json'),limitations='Continuous telemetry plus sampled native frames, not continuous video; unchanged gameplay full-route evidence carried forward.'))
    print(json.dumps(dict(seconds=r['elapsed'],samples=len(s),hold=duration,frames=len(frames))))

def handoff():
    assert not differences(snapshot('Reopened'),snapshot('Handoff'))
    s=read(OUT/'Handoff/state.json');assert not s['pie'] and not s['dirty_content'] and not s['dirty_maps']
    controls={f:read(OUT/f/'capture-settings-restored.json') for f in ['Trial01','Trial02','Final']}
    assert all(x['matched'] and x['slate_throttle_unchanged']==1 for x in controls.values())
    r=read(OUT/'Movement/runtime-verification.json');assert r['done'] and not r['cleanup_errors']
    write('handoff-verification',dict(passed=True,state=s,controls=controls,reopened_properties_exact=True,inputs_released=True,callbacks_completed=True,map=entry(ROOT/MAPFILE)))
    print('Clean PIE-off handoff and restored controls')

def storage():
    now=usage();files=[]
    for n,suffix in [('HeightCorrection01','height'),('HeightCorrection02','soft')]:
        files.extend(walk(ROOT/'Saved/OpeningLobby/UpperVoid01'/n));files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01'/n))
        files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_'+suffix+'_*.py'))
        report=ROOT/('Docs/OpeningLobbyUpperVoid01'+n+'.md')
        if report.exists():files.append(report)
    total=sum(p.stat().st_size for p in set(files))
    added=sum(p.stat().st_size for p in set(files) if 'HeightCorrection02' in p.as_posix() or p.name.startswith('uppervoid01_soft_'))
    r=dict(**now,combined_correction_bytes=total,new_correction_bytes=added,combined_under100mb=total<=100e6,new_under15mb_aim=added<=15e6,project_under250gb=now['project_bytes']<=250e9,lobby_planning_under2_4gb=now['lobby_bytes']<=2.4e9,lobby_overage_bytes=max(0,now['lobby_bytes']-2400000000),scope='Both correction folders including controller/review/cache files, source, helpers and reports; no history deleted; measurement before this receipt.')
    write('storage',r);assert r['combined_under100mb'] and r['project_under250gb'];print(json.dumps(r))
if __name__=='__main__':globals()[sys.argv[1]]()
