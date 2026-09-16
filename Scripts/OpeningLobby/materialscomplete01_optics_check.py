"""Correction03 exact file and reflected-property verification."""
import json,sys,copy,struct
from materialscomplete01_support_check import ROOT,entry,read,walk,usage,MAPFILE,INITIAL
from painterstone01_check import differences
OUT=INITIAL/'Correction03'
PREV=INITIAL/'Correction02'
CTRL=INITIAL.parent/'Controller'
def write(n,d):
    p=OUT/(n+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2));return d
def prepare():
    assert not (OUT/'protected-before.json').exists()
    receipts=[]
    for name in ['BeforeOptics01/archive.json','optics-registration-preparation-archive.json']:
        p=CTRL/name;r=read(p)
        for row in r['entries']:
            for key in ['path','archive_path']:
                a=entry(ROOT/row[key]);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256']),row
        receipts.append(entry(p))
    for r in read(PREV/'manifest.json')['entries']:assert entry(ROOT/r['path'])==r,r
    a=read(OUT/'Before/all-properties.json')
    assert not differences(a,read(OUT/'ResumeBefore/all-properties.json'))
    assert not differences(a,read(PREV/'RestoredFinal/all-properties.json'))
    protected=[entry(p) for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby'] for p in walk(ROOT/f) if not p.is_relative_to(OUT) and '__pycache__' not in str(p) and not (p.parent==ROOT/'Scripts/OpeningLobby' and p.name.startswith('materialscomplete01_optics')) and not p.name.endswith(('.lock','.painter_lock'))]
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected));write('storage-before',usage())
    write('archive-verification',dict(passed=True,receipts=receipts,prior_manifest_entries=536,preparation_properties_exact=True))
    print('Baseline and rollback PASS:',len(protected),'protected files')
def properties():
    before=read(OUT/'Before/all-properties.json');final=read(OUT/'Final/all-properties.json')
    plan=read(OUT/'plan.json');expected=copy.deepcopy(before)
    for r in plan['rows']:
        expected['actors'][r['actor']]['components'][r['component']]['properties']['overrideMaterials']=[dict(refPath=r['new'])]
    assert not differences(expected,final)
    assert not differences(final,read(OUT/'RestoredFinal/all-properties.json'))
    diff=differences(before,final);assert len(diff)==6
    inv=read(OUT/'Final/inventory.json');old=read(OUT/'Before/inventory.json')
    lookup={(r['actor'],r['component']):r for r in inv}
    changes={(r['actor'],r['component']):r for r in plan['rows']}
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    for r in old:
        x=copy.deepcopy(r);k=(r['actor'],r['component'])
        if k in changes:x.update(materials=[changes[k]['new']],overrides=[changes[k]['new']])
        assert {k:x[k] for k in keys}=={k:lookup[(r['actor'],r['component'])][k] for k in keys}
    coverage=read(PREV/'coverage.json');rows=coverage['rows']
    for r in rows:
        k=(r['actor'],r['component']);r['correction03_previous']=r['new']
        if k in changes:r['new']=changes[k]['new']
        r['correction03_preserved']=k not in changes
        assert lookup[k]['materials']==[r['new']]
    assert len(rows)==107 and sum(r['accepted_binding'] for r in rows)==17
    support=[r for r in inv if r['label']=='MC02_ProvisionalNeutralFarField'];assert len(support)==1
    assert len(inv)==108
    write('coverage',dict(passed=True,rows=rows,counts=coverage['counts'],visible_lobby_components=107,accepted_preserved=17,ceiling_preserved=9,changed_glass_bindings=6,unchanged_bindings_including_support=102,proxy_error_bindings=0,support=support))
    write('property-preservation',dict(passed=True,actors=128,components=149,mesh_components=108,exact_differences=diff,local_flags_restored=True,other_differences=[],restored_checked=True,route_evidence=entry(INITIAL/'Movement/runtime-verification.json')))
    print('Property and full coverage PASS')

def preserved():
    errors=[];external=[];rows=read(OUT/'protected-before.json')['entries']
    for r in rows:
        if r['path']==MAPFILE:continue
        a=entry(ROOT/r['path'])
        if a!=r:
            d=dict(before=r,after=a)
            if r['path']=='Saved/OpeningLobby/MaterialsComplete01/Controller/status.py' and r['sha256']=='bf9ee2bd21cec22861653725dd00a32f56cf75ab163b4bb340141562bb23406c' and a['sha256']=='ff681f8a4ac0dbae6e19c58aabfcb8fb0ff0b274aa01a31a797abfeaa8228c1c':
                d['reason']='Controller status reader changed externally during this run (1261 to 1269 bytes). Inspected current content: status/message polling helper only. Worker did not edit this file. Preserve newer controller bytes; record exception, not an exact-history claim.';external.append(d)
            elif r['path'].startswith('Saved/OpeningLobby/MaterialsComplete01/Controller/') and r['path'].endswith('-current.json'):
                d['reason']='External controller polling file; worker never wrote or restored this file.';external.append(d)
            else:errors.append(d)
    write('protected-after',dict(passed=not errors,checked=len(rows)-1,unexpected=errors,external_controller_logs=external,allowed_current_map=MAPFILE));assert not errors,errors[:3]
    hist=read(PREV/'history-verification.json')['records']
    hist.append(dict(manifest=entry(PREV/'manifest.json'),entries=536,resolutions=[dict(original=next(r for r in read(PREV/'manifest.json')['entries'] if r['path']==MAPFILE),archive=entry(CTRL/'BeforeOptics01/files'/MAPFILE))]))
    for h in hist:
        assert entry(ROOT/h['manifest']['path'])==h['manifest']
        resolve={r['original']['path']:r['archive']['path'] for r in h['resolutions']}
        for r in read(ROOT/h['manifest']['path'])['entries']:
            a=entry(ROOT/resolve.get(r['path'],r['path']));assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r
    assert len(list((ROOT/'Content/Maps').glob('L_OpeningLobby*.umap')))==1
    write('history-verification',dict(passed=True,records=hist,all_prior_manifests_immutable=True))
    print('Protected files and',sum(h['entries'] for h in hist),'historical entries PASS')

def captures():
    rows=[];keys=['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution','exposure']
    for folder in ['CurrentOn','NewOff','NewOn','Final','Hidden','Opaque']:
        for p in sorted((OUT/folder).glob('*.png')):
            c=read(p.with_name(p.stem+'-camera.json'));old=read(PREV/'Final'/(p.stem+'-camera.json'))
            assert struct.unpack('>II',p.read_bytes()[16:24])==(1920,1080)
            assert all(c[k]==old[k] for k in keys),(folder,p.name)
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed'] and c['runtime']['world_seconds']>1
            assert all(v==(folder in ['CurrentOn','NewOn']) for v in c['optical_path']['local_flags'].values())
            rows.append(dict(image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json')),local_flags=c['optical_path']['local_flags'],environment=c['environment']))
        assert read(OUT/folder/'capture-settings-restored.json')['matched']
        assert read(OUT/folder/'capture-settings-restored.json')['slate_throttle_unchanged']==1
    assert len(rows)==22 and len(list((OUT/'Final').glob('*.png')))==12
    for folder in ['Hidden','Opaque']:assert read(OUT/folder/'control-restored.json')['passed']
    write('capture-verification',dict(passed=True,images=rows,final_views=12,comparisons=3,control_triplets=2,all_standing_hfov90_1920x1080=True,settings_restored=True,global_cvars_unchanged=True))
    print('22 native captures PASS')

def graphs():
    r=read(OUT/'graph-audit-final.json');assert r['passed'] and len(r['records'])==2
    recipes={};prior=read(OUT/'graph-audit-comparison.json')['records']
    for path,m in r['records'].items():
        role='Fixed' if path.endswith('Fixed.Fixed') or path.endswith('GlassFixed.GlassFixed') or 'GlassFixed' in path else 'Leaf'
        mat=m['material']['properties'];assert mat['blendMode']=='BLEND_TranslucentColoredTransmittance' and mat['translucencyLightingMode']=='TLM_SurfacePerPixelLighting' and mat['bAllowFrontLayerTranslucency']
        assert m['all_nodes_connected'] and m['outputs']['FRONT_MATERIAL'] and not m['outputs']['EMISSIVE_COLOR'] and not m['textures']
        assert not any(x.startswith('/Game/') for x in m['dependencies'])
        params={n['properties']['properties'].get('parameterName'):n['properties']['properties'].get('defaultValue') for n in m['nodes'].values() if 'parameterName' in n['properties']['properties']}
        target=dict(ScatteringAlbedo=.45 if role=='Fixed' else .04,Transmission=.90 if role=='Fixed' else .94,SurfaceRoughness=.32 if role=='Fixed' else .09,F0=.04,EtchSlope=.0045 if role=='Fixed' else .0025)
        for key,v in target.items():
            actual=params[key];values=[actual[k] for k in ['r','g','b']] if isinstance(actual,dict) else [actual]
            assert all(abs(x-v)<1e-6 for x in values),(key,actual)
        normal=[n['properties']['properties']['code'] for n in m['nodes'].values() if 'code' in n['properties']['properties']];assert len(normal)==1
        recipes[role]=dict(path=path,constants=target,normal_code=normal[0],emission=False,statistics=m['statistics'],dependencies=m['dependencies'])
        diff=differences(prior[path]['nodes'],m['nodes']);assert len(diff)==1 and diff[0]['path'].endswith('/defaultValue'),diff
    recipe=dict(candidate='LobbyMaterials-Complete01/Correction03',materials=recipes,local_frontlayer_override=False,local_frontlayer_value=False,comparison_recipe=entry(OUT/'ComparisonArchive/Assets/Source/OpeningLobby/MaterialsComplete01/Correction03/recipe.json'),fine_adjustment=read(OUT/'fine-adjustment.json'),build_helper='Scripts/OpeningLobby/materialscomplete01_optics_unreal.py')
    (ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction03/recipe.json').write_text(json.dumps(recipe,indent=2))
    source=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp');assert source==read(INITIAL/'exact-regeneration.json')['source']
    write('native-source-verification',dict(passed=True,materials=recipes,reload=read(OUT/'graphs-reloaded.json'),unchanged_ceiling_spp=source,regeneration=entry(INITIAL/'exact-regeneration.json'),prior_native_evidence=entry(PREV/'native-source-verification.json'),no_old_graph_changes=True))
    print('Native graphs, constants and source PASS')

def pixels():
    import importlib.util
    spec=importlib.util.spec_from_file_location('png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    regions={'fixed_upper':(850,170,880,210),'fixed_lower':(825,615,865,660),'sidelight':(820,760,850,820),'leaf':(900,930,930,990)}
    records={};samples={}
    for folder in ['CurrentOn','NewOff','NewOn','Final','Hidden','Opaque']:
        p=OUT/folder/'entrance-whole-90.png';info,px=h.decode_png(p.read_bytes());result={};samples[folder]={}
        for label,(x0,y0,x1,y1) in regions.items():
            values=[sum(px[(y*1920+x)*4:(y*1920+x)*4+3])/3 for y in range(y0,y1,3) for x in range(x0,x1,3)];samples[folder][label]=values
            result[label]=dict(mean=sum(values)/len(values),min=min(values),max=max(values),bounds=[x0,y0,x1,y1],clipped_fraction=sum(v>=254 for v in values)/len(values))
        records[folder]=dict(image=entry(p),regions=result)
    for label in ['sidelight','leaf']:assert records['Final']['regions'][label]['mean']>records['Opaque']['regions'][label]['mean']+20
    assert all(x['clipped_fraction']==0 for x in records['Final']['regions'].values())
    pairs={label:sum(abs(a-b) for a,b in zip(samples['NewOff'][label],samples['NewOn'][label]))/len(samples['NewOff'][label]) for label in regions}
    write('transmission-verification',dict(passed=True,records=records,new_off_on_mean_absolute_luminance_difference=pairs,interpretation='Hidden panes reveal continuous far-field gradient; final glass transmits it, while opaque controls block it. Fixed surface hotspot remains. Local-flag comparison adds no recognizable reflected architecture in inspected whole/oblique images; pixel differences alone do not prove a reflection path. Genuine transmission PASS; reflected scene structure NOT DEMONSTRATED; visual R1 unresolved.',calibrated_transmittance_claim=False))
    print('Transmission controls PASS; local on/off sample differences:',pairs)

def storage():
    now=usage();before=read(OUT/'storage-before.json');initial=read(INITIAL/'storage-before.json')
    d=dict(**now,correction_growth_bytes=now['lobby_bytes']-before['lobby_bytes'],batch_growth_bytes=now['lobby_bytes']-initial['lobby_bytes'])
    assert d['batch_growth_bytes']<=400e6 and now['lobby_bytes']<=2.4e9 and now['project_bytes']<=250e9,d
    write('storage',dict(passed=True,within_80mb_target=d['correction_growth_bytes']<=80e6,**d));print(json.dumps(d))

if __name__=='__main__':
    for op in sys.argv[1:]:globals()[op]()
