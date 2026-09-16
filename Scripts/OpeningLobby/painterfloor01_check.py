"""Scoped adapters of existing property, PNG and fingerprint checks."""
import copy
import importlib.util
import json
import re
import struct
from collections import Counter
from painterfloor01_evidence import ROOT,OUT,CURRENT,RETIRED,entry,write,walk,digest,usage
from painterstone01_check import differences

def properties():
    before=json.loads((OUT/'Before/all-properties.json').read_text())
    final=json.loads((OUT/'Final/all-properties.json').read_text())
    restored=json.loads((OUT/'Restored/all-properties.json').read_text())
    expected=copy.deepcopy(before)
    bindings=json.loads((OUT/'bindings.json').read_text())['rows'];assert len(bindings)==3
    for row in bindings:
        node=expected['actors'][row['actor']]['components'][row['component']]['properties']
        assert node['overrideMaterials']==[dict(refPath=p) for p in row['source_overrides']]
        node['overrideMaterials']=[dict(refPath=row['new'])]
    d=differences(expected,final)+differences(final,restored)
    write('unexpected-property-differences',d);assert not d,d[:8]
    def leaves(x):
        if isinstance(x,dict):return sum(leaves(v) for v in x.values())
        if isinstance(x,list):return sum(leaves(v) for v in x)
        return 1
    inv=json.loads((OUT/'Final/inventory.json').read_text())
    stones=[r for r in inv if any('/PainterStone01/' in p for p in r['materials'])]
    assert len(stones)==4
    checkpoint=[a for a in final['actors'].values() if 'Checkpoint' in a['label']]
    write('property-preservation',dict(passed=True,actors=len(before['actors']),components=sum(len(a['components']) for a in before['actors'].values()),compared_leaf_values=leaves(expected),allowed_changes=bindings,stone_bindings=stones,checkpoint=checkpoint,normalization='None. Exact same-map reflected properties; only three declared overrideMaterials substitutions.',unexpected=[]))
    print('Complete scene properties preserved; exactly three floor bindings; four stone bindings intact.')

def protected():
    old=json.loads((OUT/'protected-before.json').read_text())['entries']
    archive=json.loads((OUT/'archive.json').read_text())
    mapping={r['original']['path']:r['archive'] for r in archive['entries']}
    rows=[];errors=[]
    for row in old:
        path=row['path'];p=ROOT/path
        if path=='Content/Maps/'+CURRENT+'.umap' or path=='Config/DefaultEngine.ini':continue
        if path in mapping:
            assert not p.exists()
            actual=entry(ROOT/mapping[path]['path'])
            assert actual['sha256']==row['sha256'] and actual['bytes']==row['bytes']
            rows.append(dict(original=row,archived=actual));continue
        actual=entry(p) if p.exists() else dict(path=path,missing=True)
        if actual!=row:errors.append(dict(before=row,after=actual))
    write('protected-after',dict(passed=not errors,checked=len(old)-2,retired_resolutions=rows,unexpected=errors));assert not errors,errors
    baseline=(OUT/'Before/DefaultEngine.ini').read_bytes()
    expected=baseline.replace(b'GameDefaultMap=/Game/Maps/L_OpeningLobby\r\n',b'GameDefaultMap=/Game/Maps/L_OpeningLobby_PainterStone01\r\n').replace(b'EditorStartupMap=/Game/Maps/L_OpeningLobby\r\n',b'EditorStartupMap=/Game/Maps/L_OpeningLobby_PainterStone01\r\n')
    assert expected!=baseline
    actual=(ROOT/'Config/DefaultEngine.ini').read_bytes()
    assert actual==expected,'Unexpected config bytes outside two default keys'
    config=[]
    for folder in ['Config','Saved/Config']:
        for p in (ROOT/folder).rglob('*.ini'):
            for i,line in enumerate(p.read_text(errors='replace').splitlines(),1):
                if 'L_OpeningLobby' in line:config.append(dict(path=p.relative_to(ROOT).as_posix(),line=i,text=line))
    write('config-audit',dict(passed=True,exact_two_key_edit=True,references=config,classification='Config/DefaultEngine.ini startup defaults point to current map. Saved editor MRU, EditorViews and command-line caches retain historical strings only; LastLevel is current. No cook, server or transition map override references retired maps.'))
    print('Protected files and exact archived map bytes verified; only two startup config keys differ.')

def captures():
    views=['entrance-90','inner-90','floor-near-90','strip-boundary-90','long-floor-90'];rows=[]
    for view in views:
        before=json.loads((OUT/'Before'/(view+'-camera.json')).read_text())
        for folder in ['Before','Final']:
            p=OUT/folder/(view+'.png');raw=p.read_bytes()
            assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1920,1080)
            camera=json.loads(p.with_name(view+'-camera.json').read_text())
            assert all(camera[k]==before[k] for k in ['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution'])
            assert camera['runtime']['ready'] and camera['runtime']['world_seconds']>1 and camera['runtime']['standing'] and camera['runtime']['possessed']
            assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm']))<1
            assert max(abs((a-b+180)%360-180) for a,b in zip(camera['actual_rotation'],[camera['pitch'],camera['yaw'],0]))<.01
            rows.append(dict(image=entry(p),metadata=entry(p.with_name(view+'-camera.json'))))
    for folder in ['Before','Trial01','Final']:
        restored=json.loads((OUT/folder/'capture-settings-restored.json').read_text())
        assert restored['matched'] and restored['slate_throttle_unchanged']==1
    standing=json.loads((OUT/'Final/standing-possession.json').read_text())
    assert standing['standing'] and standing['possessed'] and standing['state']['walking'] and not standing['state']['falling']
    assert standing['state']['gravity_z']==-980 and standing['state']['walkable_floor'] and standing['state']['eye_above_capsule_bottom']==170
    write('capture-verification',dict(passed=True,matched_images=rows,standing_possession=standing,scope='Five matched 1920x1080 HFOV90 native standing-height views, 172.15 cm camera. Transient placement for still comparisons, not a route test. Three Trial01 stills retained separately; no origin frame saved.'))
    print('Ten matched genuine captures and standing possession verified; temporary settings restored.')

def textures():
    spec=importlib.util.spec_from_file_location('existing_png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    rows=[]
    for family in ['Floor','Strip']:
        for ch in ['BaseColor','ORM','Normal']:
            p=ROOT/'Assets/Source/OpeningLobby/PainterFloor01/Channels'/('T_PainterFloor01_'+family+'_'+ch+'.png')
            info,pixels=helper.decode_png(p.read_bytes());assert (info['width'],info['height'])==(2048,2048)
            counts=[Counter(pixels[c::4]) for c in range(3)]
            summary=[dict(min=min(c),max=max(c),mean=sum(v*n for v,n in c.items())/sum(c.values()),unique=len(c)) for c in counts]
            if ch=='ORM':assert set(counts[0])=={255} and set(counts[2])=={0} and 40<=min(counts[1])<=max(counts[1])<=75
            if ch=='Normal':assert min(counts[2])>=250 and min(counts[0])>=125 and max(counts[0])<=130 and min(counts[1])>=125 and max(counts[1])<=130
            rows.append(dict(family=family,channel=ch,file=entry(p),info=info,channels_rgb=summary))
    write('texture-channel-verification',dict(passed=True,rows=rows,meanings='BaseColor sRGB; DirectX tangent-space Normal; linear ORM R=neutral AO(1), G=roughness, B=dielectric metallic(0). Flat polished normals with export quantization; no sculpted surface relief.'))
    print('Six canonical 2048 PNG channels verified.')

if __name__=='__main__':
    import sys
    for op in sys.argv[1:] :globals()[op]()
