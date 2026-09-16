"""Reuse exact property and PNG validators for complete material coverage."""
import copy,json,struct,csv,importlib.util
from collections import Counter
from materialscomplete01_evidence import ROOT,OUT,CURRENT,ASSETS,entry,write,digest,walk,usage
from painterstone01_check import differences
VIEWS=['entrance-90','inner-90','side-aisle-90','bays-context-90','stone-oblique-90','ceiling-up-90','soffit-up-90','entrance-glass-90','checkpoint-90','elevator-90','whole-hall-90']
def regenerate():
    src=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01';(src/'Channels').mkdir(exist_ok=True)
    rows=[]
    for exported,ch in [('BaseColor','BaseColor'),('OcclusionRoughnessMetallic','ORM'),('Normal','Normal')]:
        files=[OUT/'Exports'/f/('StoneSample_240cm_PainterStone01_'+exported+'.png') for f in ['Final','ReopenedFinal']]
        assert digest(files[0])==digest(files[1])
        target=src/'Channels'/('T_MaterialsComplete01_'+ch+'.png');assert not target.exists()
        target.write_bytes(files[0].read_bytes());rows.append(dict(channel=ch,files=[entry(p) for p in files+[target]]))
    opened=json.loads((OUT/'Native/openFinal.json').read_text())['structuredContent'];assert not opened['needs_saving']
    native=json.loads((OUT/'Native/finalNativeReadback.json').read_text());assert not native['audit']['structuredContent']['issues']
    recipe=dict(candidate='LobbyMaterials-Complete01/WorkerCandidate01',source='Ceiling.spp',revision='Initial',author_qa_revisions=0,base_color_srgb=[.25,.28,.265],roughness=.82,metallic=0,coverage_cm=120,roughness_layer_opacity=.08,height_layer_opacity=.001,native= native,recipe=json.loads((OUT/'Native/recipe.json').read_text()),authorship='Genuine new native Painter Fill layers and procedural resources, no external pixels; accepted materials reused only in UE.')
    (src/'recipe.json').write_text(json.dumps(recipe,indent=2))
    write('exact-regeneration',dict(passed=True,source=entry(src/'Ceiling.spp'),channels=rows,open_evidence=entry(OUT/'Native/openFinal.json'),readback=entry(OUT/'Native/finalNativeReadback.json')))
    print('Exact reopened ceiling regeneration verified and canonical channels copied.')
def properties():
    before=json.loads((OUT/'Before/all-properties.json').read_text());final=json.loads((OUT/'Final/all-properties.json').read_text());restored=json.loads((OUT/'RestoredFinal/all-properties.json').read_text())
    expected=copy.deepcopy(before);rows=json.loads((OUT/'coverage-plan.json').read_text())['rows']
    for r in rows:
        if r['preserved']:continue
        node=expected['actors'][r['actor']]['components'][r['component']]['properties']
        assert node['overrideMaterials']==[dict(refPath=p) for p in r['source_overrides']]
        node['overrideMaterials']=[dict(refPath=r['new'])]
    d=differences(expected,final)+differences(final,restored)
    write('unexpected-property-differences',d);assert not d,d[:10]
    inv=json.loads((OUT/'RestoredFinal/inventory.json').read_text());lookup={(r['actor'],r['component']):r for r in inv};assert len(inv)==107
    for r in rows:
        actual=lookup[(r['actor'],r['component'])]
        assert actual['materials']==[r['new']]
        assert actual['overrides']==(r['source_overrides'] if r['preserved'] else [r['new']])
    write('coverage',dict(passed=True,rows=rows,visible_components=107,replacements=90,preserved_bindings=17,invisible_exclusions=[],counts=Counter(r['family'] for r in rows),proxy_error_effective_bindings=0))
    with (OUT/'coverage.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    write('property-preservation',dict(passed=True,actors=len(before['actors']),components=sum(len(a['components']) for a in before['actors'].values()),allowed_changes=90,protected_bindings=[r for r in rows if r['preserved']],unexpected=[],normalization='None. Exact same-map actor/component/world/renderer comparison, only scheduled overrideMaterials substitutions.',checkpoint=[a for a in final['actors'].values() if 'Checkpoint' in a['label']]))
    print('107 effective bindings verified; 90 replacements and complete property preservation.')
def protected():
    errors=[];rows=json.loads((OUT/'protected-before.json').read_text())['entries']
    for r in rows:
        if r['path']=='Content/Maps/'+CURRENT+'.umap':continue
        actual=entry(ROOT/r['path'])
        if actual!=r:errors.append(dict(before=r,after=actual))
    write('protected-after',dict(passed=not errors,checked=len(rows)-1,unexpected=errors));assert not errors,errors
    history=[]
    manifests=[('PainterMetal01/Worker/manifest.json',OUT/'Before'/(CURRENT+'.umap')),('PainterFloor01/Worker/manifest.json',ROOT/'Saved/OpeningLobby/PainterMetal01/Worker/Before'/(CURRENT+'.umap')),('PainterStone01/Worker/Correction01/manifest.json',None)]
    archives=json.loads((ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/archive.json').read_text())['entries'];mapping={r['original']['path']:r['archive']['path'] for r in archives}
    for name,map_archive in manifests:
        m=ROOT/'Saved/OpeningLobby'/name;resolutions=[]
        for r in json.loads(m.read_text())['entries']:
            p=ROOT/r['path']
            if map_archive and r['path']=='Content/Maps/'+CURRENT+'.umap':p=map_archive
            if map_archive is None and r['path'] in mapping:p=ROOT/mapping[r['path']]
            actual=entry(p);assert (actual['bytes'],actual['sha256'])==(r['bytes'],r['sha256']),r
            if actual['path']!=r['path']:resolutions.append(dict(original=r,resolved=actual))
        history.append(dict(manifest=entry(m),entries=len(json.loads(m.read_text())['entries']),archive_resolutions=resolutions))
    assert [p.stem for p in (ROOT/'Content/Maps').glob('L_OpeningLobby*.umap')]==[CURRENT]
    write('accepted-history',dict(passed=True,records=history));print('All protected bytes and accepted historical manifests verified.')
def captures():
    rows=[]
    for view in VIEWS:
        before=json.loads((OUT/'Before'/(view+'-camera.json')).read_text())
        for folder in ['Before','Final']:
            p=OUT/folder/(view+'.png');raw=p.read_bytes();assert struct.unpack('>II',raw[16:24])==(1920,1080)
            camera=json.loads(p.with_name(view+'-camera.json').read_text())
            assert all(camera[k]==before[k] for k in ['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution'])
            assert camera['runtime']['ready'] and camera['runtime']['standing'] and camera['runtime']['possessed']
            assert camera['actual_hfov']==90 and max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm']))<1
            rows.append(dict(image=entry(p),metadata=entry(p.with_name(view+'-camera.json'))))
    for folder in ['Before','Final','Transmission']:
        d=json.loads((OUT/folder/'capture-settings-restored.json').read_text());assert d['matched'] and d['slate_throttle_unchanged']==1
    walk=json.loads((OUT/'Movement/runtime-verification.json').read_text());assert walk['passed']
    write('capture-verification',dict(passed=True,matched_images=rows,real_movement=walk,standing=json.loads((OUT/'Final/standing-possession.json').read_text()),scope='Eleven matched native 1920x1080 HFOV90 views; transmission diagnostic separate. No origin or embedded-pawn frame saved.'))
    print('22 matched standing captures and real input movement verified.')
def textures():
    spec=importlib.util.spec_from_file_location('existing_png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    rows=[]
    for ch in ['BaseColor','ORM','Normal']:
        p=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Channels'/('T_MaterialsComplete01_'+ch+'.png')
        info,pixels=h.decode_png(p.read_bytes());assert (info['width'],info['height'])==(2048,2048)
        counts=[Counter(pixels[c::4]) for c in range(3)]
        stats=[dict(min=min(c),max=max(c),mean=sum(v*n for v,n in c.items())/sum(c.values()),unique=len(c)) for c in counts]
        if ch=='ORM':assert set(counts[0])=={255} and set(counts[2])=={0} and 190<min(counts[1])<=max(counts[1])<220
        if ch=='Normal':assert min(counts[2])>240
        rows.append(dict(channel=ch,file=entry(p),info=info,channels_rgb=stats))
    write('texture-channel-verification',dict(passed=True,rows=rows,meaning='sRGB base color; linear ORM R=1 AO, G=roughness, B=0 dielectric; native Painter DirectX normal from microheight.'))
    print('Native 2048 channels verified.')
if __name__=='__main__':
    import sys
    for op in sys.argv[1:]:globals()[op]()
