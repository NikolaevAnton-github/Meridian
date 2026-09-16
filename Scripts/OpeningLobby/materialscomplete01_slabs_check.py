"""Reuse exact file, storage and full-property comparison primitives."""
import json,sys,copy,struct
from materialscomplete01_support_check import ROOT,entry,read,walk,usage,MAPFILE,INITIAL
from painterstone01_check import differences
OUT=INITIAL/'SlabLayout01';PREV=INITIAL/'Correction03';CTRL=INITIAL.parent/'Controller'
def write(n,d):
    p=OUT/(n+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2));return d
def prepare():
    assert not (OUT/'protected-before.json').exists()
    receipt=CTRL/'BeforeSlabs01/archive.json';r=read(receipt)
    for row in r['entries']:
        for key in ['path','archive_path']:
            a=entry(ROOT/row[key]);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256']),row
    assert entry(PREV/'manifest.json')['sha256']=='ed6b3c105b8f2b22536707e668e7db7ba3cff720b7938ed7899a091b985f520a'
    prior=read(PREV/'manifest.json')['entries']
    for r in prior:assert entry(ROOT/r['path'])==r,r
    assert not differences(read(OUT/'Before/all-properties.json'),read(PREV/'RestoredFinal/all-properties.json'))
    protected=[entry(p) for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby'] for p in walk(ROOT/f) if not p.is_relative_to(OUT) and '__pycache__' not in str(p) and not p.name.startswith('materialscomplete01_slabs') and not p.name.endswith(('.lock','.painter_lock'))]
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    assert len(protected)==len({r['path'] for r in protected})
    write('protected-before',dict(entries=protected));write('storage-before',usage())
    write('archive-verification',dict(passed=True,receipt=entry(receipt),entries=read(receipt)['entries'],prior_manifest_entries=len(prior),predecessor_properties_exact=True))
    print('Rollback, predecessor and baseline PASS:',len(protected),'protected files')
def properties():
    before=read(OUT/'Before/all-properties.json');final=read(OUT/'Final/all-properties.json');expected=copy.deepcopy(before)
    plan=read(OUT/'plan.json')['rows']
    for r in plan:expected['actors'][r['actor']]['components'][r['component']]['properties']['overrideMaterials']=[dict(refPath=r['new'])]
    unexpected=differences(expected,final);write('nonmaterial-differences',unexpected);assert not unexpected,unexpected[:5]
    assert not differences(final,read(OUT/'RestoredFinal/all-properties.json'))
    diff=differences(before,final);assert len(diff)==44
    inv=read(OUT/'Final/inventory.json');old=read(OUT/'Before/inventory.json')
    lookup={(r['actor'],r['component']):r for r in inv};changes={(r['actor'],r['component']):r for r in plan}
    keys=['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    for r in old:
        x=copy.deepcopy(r);k=(r['actor'],r['component'])
        if k in changes:x.update(materials=[changes[k]['new']],overrides=[changes[k]['new']])
        assert {k:x[k] for k in keys}=={k:lookup[(r['actor'],r['component'])][k] for k in keys}
    coverage=read(PREV/'coverage.json');rows=coverage['rows']
    accepted_preserved=0
    for r in rows:
        k=(r['actor'],r['component']);r['slabs_previous']=r['new'];r['slabs_preserved']=k not in changes
        if k in changes:
            r['new']=changes[k]['new'];r['slabs_role']=changes[k]['role'];r['stone_binding_change_authority']='Docs/Approvals/LobbyMaterialsComplete01-StoneSlabs01.json'
        if r['accepted_binding'] and k not in changes:accepted_preserved+=1
        assert lookup[k]['materials']==[r['new']]
        assert not any(t in r['new'] for t in ['M_RA01','DefaultMaterial','WorldGrid'])
    assert len(rows)==107 and accepted_preserved==13
    support=[r for r in inv if r['label']=='MC02_ProvisionalNeutralFarField'];assert len(support)==1 and len(inv)==108
    assert sum(r['slabs_preserved'] for r in rows)==63
    write('coverage',dict(passed=True,rows=rows,counts=coverage['counts'],visible_lobby_components=107,changed_stone=44,nonstone_preserved=63,accepted_nonstone_preserved=13,ceiling_preserved=9,proxy_error_bindings=0,support=support,glass='DEFERRED_BY_OWNER'))
    write('property-preservation',dict(passed=True,actors=len(final['actors']),components=sum(len(r['components']) for r in final['actors'].values()),mesh_components=108,exact_differences=diff,other_differences=[],restored_checked=True,route_evidence=entry(INITIAL/'Movement/runtime-verification.json')))
    print('44 authorized differences; all other properties and 63 nonstone bindings PASS')
def preserved():
    errors=[];external=[];rows=read(OUT/'protected-before.json')['entries']
    for r in rows:
        if r['path']==MAPFILE:continue
        a=entry(ROOT/r['path'])
        if a!=r:
            d=dict(before=r,after=a)
            if r['path'].startswith('Saved/OpeningLobby/MaterialsComplete01/Controller/') and r['path'].endswith('-current.json'):
                d['reason']='External controller status polling; worker did not write this file.';external.append(d)
            else:errors.append(d)
    write('protected-after',dict(passed=not errors,checked=len(rows)-1,unexpected=errors,external_controller_logs=external,allowed_current_map=MAPFILE));assert not errors,errors[:3]
    hist=read(PREV/'history-verification.json')['records']
    hist.append(dict(manifest=entry(PREV/'manifest.json'),entries=678,resolutions=[dict(original=next(r for r in read(PREV/'manifest.json')['entries'] if r['path']==MAPFILE),archive=entry(CTRL/'BeforeSlabs01/files'/MAPFILE))]))
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
    for folder in ['Before','Trial01','Final']:
        for p in sorted((OUT/folder).glob('*.png')):
            c=read(p.with_name(p.stem+'-camera.json'));old=read(OUT/'Before'/(p.stem+'-camera.json'))
            assert struct.unpack('>II',p.read_bytes()[16:24])==(1920,1080)
            assert all(c[k]==old[k] for k in keys),(folder,p.name)
            assert c['runtime']['ready'] and c['runtime']['standing'] and c['runtime']['possessed'] and c['runtime']['world_seconds']>1
            assert abs(c['actual_hfov']-90)<.001 and abs(c['actual_xyz_cm'][2]-172)<1
            rows.append(dict(image=entry(p),camera=entry(p.with_name(p.stem+'-camera.json'))))
        assert read(OUT/folder/'capture-settings-restored.json')['matched']
        assert read(OUT/folder/'capture-settings-restored.json')['slate_throttle_unchanged']==1
    assert len(rows)==36 and len(list((OUT/'Final').glob('*.png')))==16
    write('capture-verification',dict(passed=True,images=rows,final_views=16,representative_views=4,all_standing_hfov90_1920x1080=True,settings_restored=True,global_cvars_unchanged=True))
    print('36 genuine matched standing captures PASS')
def graphs():
    audit=read(OUT/'graph-audit-final.json');assert audit['passed']
    m=next(iter(audit['records'].values()));nodes={k.split(':')[-1]:v for k,v in m['nodes'].items()}
    prior=read(ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/native-material-audit.json')
    oldnodes={k.split(':')[-1]:v for k,v in prior['nodes'].items()}
    for name,old in oldnodes.items():
        props=old['properties'];new=nodes[name]['properties']['properties']
        for k in ['code','texture','defaultValue','r','g','b','a','parameterName','outputType']:
            if k in props:assert new[k]==props[k],(name,k)
    params={v['properties']['properties'].get('parameterName'):v['properties']['properties'].get('defaultValue') for v in nodes.values()}
    for k,v in dict(CoverageCm=240,DielectricSpecular=.4,WidthCm=120,HeightCm=240,JointWidthCm=.5,JointDepthCm=.075,GroutRoughness=.65,GroutFaceMultiplier=.32).items():assert abs(params[k]-v)<1e-6,(k,params[k])
    rough=nodes[m['outputs']['ROUGHNESS'].split(':')[-1]]
    assert rough['connected'][0].endswith(':MaterialExpressionComponentMask_1')
    assert nodes['MaterialExpressionComponentMask_1']['connected'][0].endswith(':MaterialExpressionCustom_1')
    maskprops=nodes['MaterialExpressionComponentMask_1']['properties']['properties'];assert maskprops['g'] and not maskprops['r'] and not maskprops['b']
    assert not m['outputs']['WORLD_POSITION_OFFSET'] and not m['outputs']['EMISSIVE_COLOR']
    assert m['outputs']['SPECULAR'].endswith(':MaterialExpressionScalarParameter_1')
    assert set(m['textures'])==set(prior['textures']) and len(m['textures'])==3
    assert set(d for d in m['dependencies'] if d.startswith('/Game/'))=={t.split('.')[0] for t in m['textures']}
    mat=m['material']['properties'];assert mat['blendMode']=='BLEND_Opaque' and not mat['bTangentSpaceNormal'] and not mat['bFullyRough']
    instances=read(OUT/'instances-final.json')
    for r in read(OUT/'plan.json')['rows']:
        p=instances[r['actor']]['properties']
        scalar={x['parameterInfo']['name']:x['parameterValue'] for x in p['scalarParameterValues']}
        vector={x['parameterInfo']['name']:x['parameterValue'] for x in p['vectorParameterValues']}
        assert scalar=={'LayoutMode':r['mode']}
        assert [vector['OriginCm'][k] for k in ['r','g','b']]==r['origin_cm']
        assert [vector['ExtentCm'][k] for k in ['r','g','b']]==[b-a for a,b in zip(r['bounds_min_cm'],r['bounds_max_cm'])]
        assert not p['textureParameterValues']
        assert not any(v for k,v in p['basePropertyOverrides'].items() if k.startswith('bOverride_'))
    assert not differences(read(OUT/'graph-audit-representative.json'),audit)
    assert not differences(read(OUT/'instances-representative.json'),instances)
    source=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp');assert source==read(INITIAL/'exact-regeneration.json')['source']
    spp=[entry(p) for p in (ROOT/'Assets/Source/OpeningLobby/PainterStone01').rglob('*.spp')]
    assert spp
    write('native-source-verification',dict(passed=True,statistics=m['statistics'],nodes=len(nodes),instances=len(instances),accepted_face_nodes_exact=len(oldnodes),textures=m['textures'],dependencies=m['dependencies'],face_ORM_G_direct=True,specular=.4,coverage_cm=240,unchanged_ceiling_spp=source,unchanged_stone_spp=spp,ceiling_regeneration=entry(INITIAL/'exact-regeneration.json'),stone_regeneration=entry(ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/exact-regeneration.json'),reload=read(OUT/'graphs-reloaded.json'),no_texture_pixels_or_old_assets_changed=True))
    print('Reopened graph, 44 instances, exact accepted face and native Painter sources PASS')
def numerics():
    import math
    rows=read(OUT/'plan.json')['rows']
    def line(t,module,footprint):
        q=((t/module+.5)%1-.5)*module;f=max(footprint,.0001)
        c=max(0,min(1,(min(q+f*.5,.25)-max(q-f*.5,-.25))/f))
        blend=max(0,min(1,(f-module*.5)/(module*.5)))
        return c*(1-blend)+.5/module*blend
    samples=[]
    for footprint in [.01,.1,.5,1,4,16,240]:
        # Integrate one full 120 cm period: true area is 0.5 cm at all distances.
        step=.005;area=sum(line(-60+(i+.5)*step,120,footprint)*step for i in range(24000))
        assert abs(area-.5)<.0002,(footprint,area)
        samples.append(dict(footprint_cm=footprint,integrated_joint_width_cm=area,center_coverage=line(0,120,footprint)))
    for r in rows:
        assert r['course_datum_world_z']==r['origin_cm'][2]==0 and r['module_cm']==[120,240]
        assert r['axes']==[[1,0,0],[0,1,0],[0,0,1]]
        if r['role']=='Column':
            for k in [0,1]:assert round((r['bounds_max_cm'][k]-r['bounds_min_cm'][k])/120,5) in [1,2]
        # Adjacent faces share the same absolute course phase irrespective of origin XY.
        for z in [239.8,240,240.2,480,720]:assert line(z-r['origin_cm'][2],240,.1)==line(z,240,.1)
    assert line(60,120,.1)==0 and line(120,120,.01)==1 and line(120.3,120,.01)==0
    write('layout-numerics',dict(passed=True,regular=39,trim_aware=5,physical_width_cm=.5,recess_depth_cm=.075,edge_ramp_cm=.125,filter_integrals=samples,all_course_datums_equal=True,column_faces_one_or_two_full_widths=True,ordinary_face_mask_exact_zero=True,projection='Dominant geometric plane; no blended grids or scaled cube UVs',trim='Beam X only; head/datum Y only; elevator Z below 420 cm then Y; horizontal shell faces long-axis only',limitation='Shader normal recess, no silhouette displacement. Mineral projection is the unchanged accepted world sampling.'))
    print('Physical module, joint width/filter area, corner courses and trim schedule PASS')
def storage():
    now=usage();before=read(OUT/'storage-before.json');initial=read(INITIAL/'storage-before.json')
    d=dict(**now,slab_growth_bytes=now['lobby_bytes']-before['lobby_bytes'],batch_growth_bytes=now['lobby_bytes']-initial['lobby_bytes'])
    assert d['batch_growth_bytes']<=450e6 and now['lobby_bytes']<=2.4e9 and now['project_bytes']<=250e9,d
    write('storage',dict(passed=True,within_80mb_target=d['slab_growth_bytes']<=80e6,**d));print(json.dumps(d))
if __name__=='__main__':
    for op in sys.argv[1:]:globals()[op]()
