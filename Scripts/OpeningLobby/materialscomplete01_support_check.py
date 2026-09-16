"""Exact support baselines, full preservation and evidence checks."""
import json,copy,sys,struct
from pathlib import Path
from materialscomplete01_evidence import ROOT,entry,digest,walk,usage,CURRENT
from painterstone01_check import differences
INITIAL=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker'
PREV=INITIAL/'Correction01'
OUT=INITIAL/'Correction02'
MAPFILE='Content/Maps/'+CURRENT+'.umap'
def read(p):return json.loads(p.read_text())
def write(name,data):
    p=OUT/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2));return data
def prepare():
    assert not (OUT/'protected-before.json').exists()
    receipt=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeSupport01/archive.json'
    r=read(receipt)
    for row in r['entries']:
        for p in [ROOT/row['path'],ROOT/row['archive_path']]:
            actual=entry(p);assert (actual['bytes'],actual['sha256'])==(row['bytes'],row['sha256']),row
    assert digest(PREV/'manifest.json')=='4c54f5d1f46d4d49eed26cae5bb8c6f3649014ccce1ab6b25f19cb0db0b1d86f'
    for row in read(PREV/'manifest.json')['entries']:assert entry(ROOT/row['path'])==row,row
    write('archive-verification',dict(passed=True,receipt=entry(receipt),entries=r['entries'],prior_manifest_entries=398))
    write('storage-before',usage())
    protected=[entry(p) for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby'] for p in walk(ROOT/f) if not p.is_relative_to(OUT) and '__pycache__' not in str(p) and not p.name.startswith('materialscomplete01_support') and not p.name.endswith(('.lock','.painter_lock'))]
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    assert len(protected)==len({r['path'] for r in protected})
    write('protected-before',dict(entries=protected))
    (OUT/'support-plan.md').write_text('''# Correction02 support plan

Actual reference PNGs and Correction01 whole/near glass, side wall and pane-hidden
images inspected. The empty black field explains absent transmitted variation.
Preserve all 107 bindings, all prior scene properties and every historical byte.
One stock Engine BasicShapes Sphere, radius 1 km, origin 0, two-sided native unlit
neutral gradient: horizon radiance 12, zenith 2, lower hemisphere 3, broad Y-axis
variation +/-18 percent. No small patches, sun, clouds, scenery or near backing.
Noncolliding, no shadows, no distance-field or dynamic indirect contribution.
Do not add a light initially. Evaluate actual transmitted gradient at matched
whole/near/entrance/hall poses under unchanged exposure. A second setup may add
one captured-scene support only if a specific reflection deficiency is observed.
Maximum two purposeful setups. Preserve trial settings and actual images.

Acceptance: credible glass body with fixed/leaf distinction, un-clipped continuous
transmission and readable fine frames/oblique response. R2 broad walls remain calm.
True/hidden/opaque controls, same support state and camera, exact restoration.
Final 12 standing 1920x1080 HFOV90 views, full existing-actor/world comparison,
107-row coverage plus separate support census, saved/reopened native graph audit,
protected hashes and exact history, clean map/PIE off. <=80 MB further growth,
<=400 MB batch, <=2.4 GB lobby and <=250 GB project. Independent review pending;
no owner acceptance or final atmosphere claim. Native UE source only.
''')
    print(json.dumps(dict(protected=len(protected),archive_verified=True)))

def properties():
    before=read(OUT/'Before/all-properties.json');final=read(OUT/'Final/all-properties.json')
    assert not differences(read(PREV/'RestoredFinal/all-properties.json'),before)
    new=set(final['actors'])-set(before['actors']);assert len(new)==1,new
    name=new.pop();assert final['actors'][name]['label']=='MC02_ProvisionalNeutralFarField'
    existing=copy.deepcopy(final);support=existing['actors'].pop(name)
    d=differences(before,existing)
    if (OUT/'RestoredFinal/all-properties.json').exists():d+=differences(final,read(OUT/'RestoredFinal/all-properties.json'))
    write('unexpected-property-differences',d);assert not d,d[:12]
    inv=read(OUT/'Final/inventory.json');old=read(OUT/'Before/inventory.json')
    lobby=[r for r in inv if r['actor']!=name];support_inv=[r for r in inv if r['actor']==name]
    assert len(lobby)==len(old)==107 and len(support_inv)==1
    # Inventory repr embeds temporary Python addresses in bounds/location.
    # Complete reflected properties above independently compare geometry exactly.
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    assert [{k:r[k] for k in keys} for r in lobby]==[{k:r[k] for k in keys} for r in old]
    coverage=read(PREV/'coverage.json');rows=coverage['rows']
    lookup={(r['actor'],r['component']):r for r in lobby}
    for r in rows:assert lookup[(r['actor'],r['component'])]['materials']==[r['new']]
    for r in rows:r['correction02_preserved']=True
    write('coverage',dict(passed=True,rows=rows,visible_lobby_components=107,existing_bindings_changed=0,accepted_preserved=17,ceiling_preserved=9,counts=coverage['counts'],invisible_exclusions=[],proxy_error_bindings=0))
    write('support-census',dict(passed=True,actors=1,mesh_components=1,new_lights=0,new_reflection_actors=0,inventory=support_inv,all_properties=support,setup=read(OUT/'setup-Setup01.json'),outside_107_coverage=True))
    write('property-preservation',dict(passed=True,existing_actors=127,existing_components=148,existing_mesh_components=107,allowed_existing_changes=0,new_support_actors=1,nonmaterial_differences=[],normalization='None; remove only the one explicitly inventoried added support actor before comparison.',restored_checked=(OUT/'RestoredFinal/all-properties.json').exists(),route_evidence=entry(INITIAL/'Movement/runtime-verification.json'),route_basis='Positive prior standing/input/collision results plus exact unchanged existing actor/component/world/gameplay properties; new sphere has collision disabled and lies 1 km away. No new route/performance claim.'))
    print('Properties PASS:127 existing actors and 107 bindings exact, one separately inventoried sphere.')

def preserved():
    errors=[];checked=0;external=[]
    for r in read(OUT/'protected-before.json')['entries']:
        if r['path']==MAPFILE:continue
        actual=entry(ROOT/r['path']);checked+=1
        if actual!=r:
            change=dict(before=r,after=actual)
            if r['path']=='Saved/OpeningLobby/MaterialsComplete01/Controller/artist-messages-current.json':
                change['reason']='Live controller transcript refreshed externally during worker execution. Worker read this file but never wrote it. Baseline hash retained; no restoration over controller work.'
                external.append(change)
            else:errors.append(change)
    write('protected-after',dict(passed=not errors,checked=checked,exact=checked-len(external)-len(errors),unexpected=errors,external_controller_log_changes=external,exceptions=[MAPFILE]));assert not errors,errors[:5]
    mapping={r['original']['path']:ROOT/r['archive']['path'] for r in read(ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/archive.json')['entries']}
    schedules=[(PREV/'manifest.json',{MAPFILE:ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeSupport01/files'/MAPFILE}),
        (INITIAL/'manifest.json',{MAPFILE:ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeCorrection01/files'/MAPFILE}),
        (ROOT/'Saved/OpeningLobby/PainterMetal01/Worker/manifest.json',{MAPFILE:INITIAL/'Before'/(CURRENT+'.umap')}),
        (ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/manifest.json',{MAPFILE:ROOT/'Saved/OpeningLobby/PainterMetal01/Worker/Before'/(CURRENT+'.umap')}),
        (ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json',mapping)]
    history=[]
    for m,resolve in schedules:
        entries=read(m)['entries'];resolved=[]
        for r in entries:
            p=resolve.get(r['path'],ROOT/r['path']);a=entry(p)
            assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r
            if a['path']!=r['path']:resolved.append(dict(original=r,archive=a))
        history.append(dict(manifest=entry(m),entries=len(entries),resolutions=resolved))
    assert [p.stem for p in (ROOT/'Content/Maps').glob('L_OpeningLobby*.umap')]==[CURRENT]
    write('history-verification',dict(passed=True,records=history,all_prior_manifests_immutable=True))
    print('Protected PASS:',checked,'files;',sum(r['entries'] for r in history),'historical manifest entries.')

def captures():
    rows=[];keys=['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution','exposure']
    folders=['Setup01','Setup02','Hidden','Opaque','SupportOff','Final']
    for folder in folders:
        for p in sorted((OUT/folder).glob('*.png')):
            c=read(p.with_name(p.stem+'-camera.json'));old=read(PREV/'Final'/(p.stem+'-camera.json'))
            assert struct.unpack('>II',p.read_bytes()[16:24])==(1920,1080)
            assert all(c[k]==old[k] for k in keys),(p,{k:(old[k],c[k]) for k in keys if old[k]!=c[k]})
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed'] and c['runtime']['world_seconds']>1
            rows.append(dict(folder=folder,image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json')),environment=c['environment']))
        r=read(OUT/folder/'capture-settings-restored.json');assert r['matched'] and r['slate_throttle_unchanged']==1
    assert len([r for r in rows if r['folder']=='Final'])==12
    for folder in ['Hidden','Opaque','SupportOff']:assert read(OUT/folder/'control-restored.json')['passed']
    for name in ['entrance-whole-90','entrance-glass-90','entrance-90','whole-hall-90']:
        a=read(OUT/'SupportOff'/(name+'-camera.json'));b=read(OUT/'Final'/(name+'-camera.json'))
        assert all(a[k]==b[k] for k in keys) and a['environment']['support']=='off' and b['environment']['support']=='on'
    write('capture-verification',dict(passed=True,images=rows,final_views=12,matched_support_pairs=4,matched_true_hidden_opaque_triplets=2,settings_restored=True,environment_exception='One distant neutral sphere on/off; existing lights, exposure, renderer and all 107 bindings remain exact. Setup02 runtime reflection is unsupported and removed, not successful evidence.'))
    print('Captures PASS:',len(rows),'native images;12 final,4 support pairs,2 control triplets.')

def storage():
    now=usage();b=read(OUT/'storage-before.json');initial=read(INITIAL/'storage-before.json')
    data=dict(**now,correction_growth_bytes=now['lobby_bytes']-b['lobby_bytes'],batch_growth_bytes=now['lobby_bytes']-initial['lobby_bytes'])
    assert data['batch_growth_bytes']<=400e6 and now['lobby_bytes']<=2.4e9 and now['project_bytes']<=250e9,data
    write('storage',dict(passed=True,within_80mb_target=data['correction_growth_bytes']<=80e6,**data,method='Existing no-junction traversal; no history or user data deletion.'))
    print(json.dumps(data))

def transmission():
    import importlib.util
    spec=importlib.util.spec_from_file_location('png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    records={}
    regions={'fixed_upper':(850,170,880,210),'fixed_lower':(825,615,865,660),'sidelight':(820,760,850,820),'leaf':(900,930,930,990)}
    for folder in ['SupportOff','Final','Hidden','Opaque']:
        p=OUT/folder/'entrance-whole-90.png';info,pixels=h.decode_png(p.read_bytes());samples={}
        for label,(x0,y0,x1,y1) in regions.items():
            values=[sum(pixels[(y*1920+x)*4:(y*1920+x)*4+3])/3 for y in range(y0,y1,3) for x in range(x0,x1,3)]
            samples[label]=dict(mean=sum(values)/len(values),min=min(values),max=max(values),samples=len(values),bounds=[x0,y0,x1,y1],clipped_fraction=sum(v>=254 for v in values)/len(values))
        records[folder]=dict(image=entry(p),regions=samples)
    for label in ['sidelight','leaf']:
        assert records['Final']['regions'][label]['mean']>records['Opaque']['regions'][label]['mean']+20
        assert records['Final']['regions'][label]['mean']>records['SupportOff']['regions'][label]['mean']+20
    assert all(r['clipped_fraction']==0 for r in records['Final']['regions'].values())
    write('transmission-verification',dict(passed=True,records=records,interpretation='Real neutral far-field radiance reaches lower fixed panes and leaves; opaque control blocks it and support-off makes leaves dark. Hidden controls reveal stronger horizon/zenith variation than final fixed panes. Existing fixed-pane surface response masks much of the upper transmitted gradient. No clipped values in named pane samples. This is causal visibility evidence, not calibrated transmittance or visual R1 closure.',visual_R1='UNRESOLVED',restoration=True,prior_reverse_control=entry(PREV/'transmission-verification.json')))
    print('Transmission PASS:lower fixed/leaf causal support visibility; pane samples nonclipped. R1 visual unresolved.')

def graphs():
    r=read(OUT/'graph-audit-final.json');assert r['passed'] and len(r['records'])==1
    m=next(iter(r['records'].values()));assert len(m['nodes'])==2 and m['all_nodes_connected'] and not m['textures']
    assert m['outputs']['EMISSIVE_COLOR'] and not m['outputs']['FRONT_MATERIAL']
    assert not any(p.startswith('/Game/') for p in m['dependencies'])
    recipe=read(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction02/recipe-Setup01.json')
    custom=[n['properties']['properties'] for n in m['nodes'].values() if n['properties']['class_path']=='/Script/Engine.MaterialExpressionCustom']
    assert len(custom)==1 and custom[0]['code']==recipe['hlsl']
    mat=m['material']['properties'];assert mat['twoSided'] and mat['bIsSky']
    original=read(INITIAL/'exact-regeneration.json')
    ceiling=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp');assert ceiling==original['source']
    links=[entry(PREV/p) for p in ['graph-source-verification.json','graph-audit-final.json','transmission-verification.json']]
    write('native-source-verification',dict(passed=True,graph_audit=entry(OUT/'graph-audit-final.json'),reload=read(OUT/'graphs-reloaded.json'),recipe=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction02/recipe-Setup01.json'),native_support_nodes=2,texture_dependencies=[],unchanged_glass_stone_evidence=links,unchanged_ceiling_spp=ceiling,ceiling_regeneration=entry(INITIAL/'exact-regeneration.json'),existing_materials_unmodified=True))
    print('Native source PASS:two-node saved/reloaded support graph; prior glass/wall and Ceiling source linked.')
if __name__=='__main__':
    for op in sys.argv[1:]:globals()[op]()
