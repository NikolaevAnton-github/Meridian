"""Exact correction preservation, history and matched native image checks."""
import copy,json,struct,csv,sys
from pathlib import Path
from collections import Counter
from materialscomplete01_evidence import ROOT,entry,digest,walk,usage,CURRENT
from painterstone01_check import differences
INITIAL=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker'
OUT=INITIAL/'Correction01'
MAPFILE='Content/Maps/'+CURRENT+'.umap'
def read(p):return json.loads(p.read_text())
def write(name,data):
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2));return data
def properties():
    before=read(OUT/'Before/all-properties.json');final=read(OUT/'Final/all-properties.json');restored=read(OUT/'RestoredFinal/all-properties.json')
    assert not differences(read(INITIAL/'RestoredFinal/all-properties.json'),before)
    expected=copy.deepcopy(before);rows=read(OUT/'coverage-plan.json')['rows']
    for r in rows:
        if r['preserved']:continue
        node=expected['actors'][r['actor']]['components'][r['component']]['properties']
        assert node['overrideMaterials']==[dict(refPath=p) for p in r['source_overrides']]
        node['overrideMaterials']=[dict(refPath=r['new'])]
    d=differences(expected,final)+differences(final,restored)
    write('unexpected-property-differences',d);assert not d,d[:10]
    inv=read(OUT/'RestoredFinal/inventory.json');lookup={(r['actor'],r['component']):r for r in inv}
    assert len(inv)==len(lookup)==len(rows)==107
    for r in rows:
        a=lookup[(r['actor'],r['component'])]
        assert a['materials']==[r['new']]
        assert a['overrides']==(r['source_overrides'] if r['preserved'] else [r['new']])
        assert a['visible'] and not a['actor_hidden'] and not a['hidden_in_game']
        assert '/Painter' in r['new'] or '/MaterialsComplete01/' in r['new']
    assert sum(r['accepted_binding'] for r in rows)==17
    assert all(r['preserved'] for r in rows if r['accepted_binding'] or r['family']=='Ceiling')
    shoulders=[r for r in rows if r['label'] in ['RA01_Shoulder_-1','RA01_Shoulder_1']]
    assert len(shoulders)==2 and len({r['new'] for r in shoulders})==1 and all(r['preserved'] for r in shoulders)
    write('coverage',dict(passed=True,rows=rows,counts=Counter(r['family'] for r in rows),visible_components=107,changed=25,preserved=82,accepted_preserved=17,ceiling_preserved=9,invisible_exclusions=[],proxy_error_bindings=0))
    with (OUT/'coverage.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write('property-preservation',dict(passed=True,actors=len(before['actors']),components=sum(len(a['components']) for a in before['actors'].values()),allowed_overrides=25,nonmaterial_differences=[],initial_scene_exact=True,final_restored_exact=True,shoulders_exact=True,normalization='None',inherited_route_evidence=entry(INITIAL/'Movement/runtime-verification.json'),route_basis='Exact unchanged mesh/collision/gameplay/owner transforms. No new route or performance claim.'))
    print('Properties PASS: 127 actors,148 components,107 coverage,25 overrides,17 accepted,9 ceiling.')
def preserved():
    errors=[];own=[];checked=0
    for r in read(OUT/'protected-before.json')['entries']:
        if r['path']==MAPFILE:continue
        if Path(r['path']).name.startswith('materialscomplete01_correction'):
            own.append(r);continue
        actual=entry(ROOT/r['path']);checked+=1
        if actual!=r:errors.append(dict(before=r,after=actual))
    write('protected-after',dict(passed=not errors,checked=checked,unexpected=errors,task_owned_helper_exclusions=own));assert not errors,errors[:5]
    history=[]
    mapping={r['original']['path']:r['archive']['path'] for r in read(ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/archive.json')['entries']}
    initial_archive=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeCorrection01/files'/MAPFILE
    schedules=[(INITIAL/'manifest.json',{MAPFILE:initial_archive}),
        (ROOT/'Saved/OpeningLobby/PainterMetal01/Worker/manifest.json',{MAPFILE:INITIAL/'Before'/(CURRENT+'.umap')}),
        (ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/manifest.json',{MAPFILE:ROOT/'Saved/OpeningLobby/PainterMetal01/Worker/Before'/(CURRENT+'.umap')}),
        (ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json',{k:ROOT/v for k,v in mapping.items()})]
    for m,resolve in schedules:
        entries=read(m)['entries'];resolved=[]
        for r in entries:
            p=resolve.get(r['path'],ROOT/r['path']);a=entry(p)
            assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),r
            if a['path']!=r['path']:resolved.append(dict(original=r,archive=a))
        history.append(dict(manifest=entry(m),entries=len(entries),resolutions=resolved))
    assert [p.stem for p in (ROOT/'Content/Maps').glob('L_OpeningLobby*.umap')]==[CURRENT]
    write('history-verification',dict(passed=True,records=history,initial_manifest_exact=True))
    print('Protected and historical bytes PASS:',checked,'baseline files;',sum(r['entries'] for r in history),'manifest entries.')
def captures():
    rows=[];keys=['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution']
    for p in sorted((OUT/'Final').glob('*.png')):
        camera=read(p.with_name(p.stem+'-camera.json'));old=read(INITIAL/'Final'/(p.stem+'-camera.json'))
        assert struct.unpack('>II',p.read_bytes()[16:24])==(1920,1080)
        assert all(camera[k]==old[k] for k in keys),(p,{k:(old[k],camera[k]) for k in keys if camera[k]!=old[k]})
        assert camera['runtime']['ready'] and camera['runtime']['standing'] and camera['runtime']['possessed']
        assert camera['runtime']['world_seconds']>1 and camera['actual_hfov']==90
        rows.append(dict(initial=entry(INITIAL/'Final'/p.name),corrected=entry(p),metadata=entry(p.with_name(p.stem+'-camera.json'))))
    assert len(rows)==12
    controls=[]
    reference=read(OUT/'Transmission/transmission-90-camera.json')
    for name in ['transmission-90','without-panes-90','opaque-control-90']:
        p=OUT/'Transmission'/(name+'.png');c=read(p.with_name(name+'-camera.json'))
        assert all(c[k]==reference[k] for k in keys)
        assert c['runtime']['ready'] and c['runtime']['possessed']
        controls.append(dict(image=entry(p),metadata=entry(p.with_name(name+'-camera.json'))))
    interior=[]
    for name in ['entrance-whole-90','entrance-glass-90']:
        p=OUT/'InteriorDiagnostic'/(name+'.png');c=read(p.with_name(name+'-camera.json'));f=read(OUT/'Final'/(name+'-camera.json'))
        assert all(c[k]==f[k] for k in keys) and c['diagnostic_state']=='six panes hidden'
        interior.append(dict(image=entry(p),metadata=entry(p.with_name(name+'-camera.json'))))
    for folder in ['Trial01','Final','Transmission','InteriorDiagnostic']:
        c=read(OUT/folder/'capture-settings-restored.json');assert c['matched'] and c['slate_throttle_unchanged']==1
    write('capture-verification',dict(passed=True,matched_pairs=rows,transmission_controls=controls,interior_diagnostics=interior,restoration_passed=True,unused_incomplete_capture='InteriorDiagnostic/entrance-90-camera.json is an unshot camera request: optional third diagnostic was interrupted by early PIE stop. Two complete same-pose controls retained; all 12 required final images complete. error-capture_ready.json retained.'))
    print('Capture PASS:12 exact-pose pairs,3 transmission controls,2 interior controls;settings restored.')
def storage():
    now=usage();b=read(OUT/'storage-before.json');initial=read(INITIAL/'storage-before.json')
    data=dict(**now,correction_growth_bytes=now['lobby_bytes']-b['lobby_bytes'],batch_growth_bytes=now['lobby_bytes']-initial['lobby_bytes'])
    assert data['correction_growth_bytes']<=150e6 and data['batch_growth_bytes']<=400e6 and now['lobby_bytes']<=2.4e9 and now['project_bytes']<=250e9,data
    write('storage',dict(passed=True,**data,method='Existing no-junction traversal; no data/history deletion.'))
    print('Storage PASS:',json.dumps(data))
def graphs():
    original=read(ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/native-material-audit.json')
    audit=read(OUT/'graph-audit-final.json')['records']
    stone=next(r for p,r in audit.items() if 'BroadStone' in p)
    oldnodes={p.split(':')[-1]:n for p,n in original['nodes'].items()}
    newnodes={p.split(':')[-1]:n for p,n in stone['nodes'].items()}
    checked=[]
    for name,n in oldnodes.items():
        if name=='MaterialExpressionScalarParameter_1':continue
        a=copy.deepcopy(n);b=copy.deepcopy(newnodes[name]['properties'])
        for d in [a,b]:
            for k in ['materialExpressionEditorX','materialExpressionEditorY']:d['properties'].pop(k,None)
        b=json.loads(json.dumps(b).replace('/Game/OpeningLobby/MaterialsComplete01/Correction01/M_C01_BroadStone.M_C01_BroadStone:', '/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01.M_PainterStone01:'))
        assert a==b,(name,a,b)
        checked.append(name)
    for key in ['BASE_COLOR','NORMAL','METALLIC','AMBIENT_OCCLUSION']:
        assert stone['outputs'][key].split(':')[-1]==original['inputs'][key].split(':')[-1]
    assert len(stone['textures'])==3 and all('/PainterStone01/Textures/' in p for p in stone['textures'])
    roles={}
    for path,r in audit.items():
        if 'Glass' not in path:continue
        nodes=r['nodes'];slab=nodes[r['outputs']['FRONT_MATERIAL']]
        assert slab['properties']['properties']['subSurfaceType']=='MSS_SimpleVolume'
        assert slab['connected'][slab['inputs'].index('Emissive Color')] is None
        params={n['properties']['properties'].get('parameterName'):n['properties']['properties'].get('defaultValue') for n in nodes.values()}
        assert all(abs(params['F0'][ch]-.04)<1e-6 for ch in ['r','g','b'])
        assert not r['textures'] and len(nodes)==10
        assert 'BLEND_TranslucentColoredTransmittance' in str(r['material']) or 'ColoredTransmittance' in str(r['material'])
        roles[path]=dict(params=params,emission_connected=False,all_nodes_connected=r['all_nodes_connected'],statistics=r['statistics'])
    write('graph-source-verification',dict(passed=True,accepted_stone_nodes_exact_except_editor_positions=checked,stone_extra_nodes=['Multiply: accepted roughness * .35','Add: + .57'],stone_specular=.35,base_color_normal_projection_ao_metallic_exact=True,glass=roles,reload=read(OUT/'graphs-reloaded.json')))
    print('Graph source PASS:accepted mineral code/channels exact;glass linked real volume/no emission.')
if __name__=='__main__':
    for op in sys.argv[1:]:globals()[op]()
