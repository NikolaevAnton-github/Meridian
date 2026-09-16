"""Scoped reuse of property, capture, PNG and historical fingerprint checks."""
import json
import types
import importlib.util
from collections import Counter
from paintermetal01_evidence import ROOT,OUT,CURRENT,TARGETS,entry,write,digest,FLOOR_MANIFEST

def adapter():
    p=ROOT/'Scripts/OpeningLobby/painterfloor01_check.py'
    s=p.read_text().replace('from painterfloor01_evidence import ROOT,OUT,CURRENT,RETIRED,entry,write,walk,digest,usage','from paintermetal01_evidence import ROOT,OUT,CURRENT,entry,write,walk,digest,usage')
    s=s.replace("len(bindings)==3","len(bindings)==10").replace('three floor bindings','ten metal bindings').replace('three declared','ten declared')
    s=s.replace("OUT/'Restored/all-properties.json'","OUT/'RestoredFinal/all-properties.json'")
    s=s.replace("'floor-near-90','strip-boundary-90','long-floor-90'","'checkpoint-metal-90','service-door-90','elevator-metal-90'")
    s=s.replace("['Before','Trial01','Final']","['Before','Final']").replace('Three Trial01 stills retained separately; no origin frame saved.','No origin frame saved.')
    module=types.ModuleType('metal_checks');module.__file__=str(p)
    exec(compile(s,str(p),'exec'),module.__dict__)
    return module
def properties():
    adapter().properties()
    before=json.loads((OUT/'Before/inventory.json').read_text());final=json.loads((OUT/'Final/inventory.json').read_text())
    floor=[r for r in before if any('/PainterFloor01/' in p for p in r['materials'])]
    assert len(floor)==3
    after={r['actor']:r for r in final}
    for r in floor:
        assert after[r['actor']]['materials']==r['materials'] and after[r['actor']]['overrides']==r['overrides']
    write('accepted-floor-bindings',dict(passed=True,rows=floor))
def captures():adapter().captures()
def protected():
    old=json.loads((OUT/'protected-before.json').read_text())['entries'];errors=[]
    ignored_locks=[r['path'] for r in old if r['path'].endswith(('.painter_lock','.lock'))]
    for row in old:
        if row['path'].endswith(('.painter_lock','.lock')):continue
        if row['path']=='Content/Maps/'+CURRENT+'.umap':continue
        actual=entry(ROOT/row['path'])
        if row!=actual:errors.append(dict(before=row,after=actual))
    assert sorted(p.stem for p in (ROOT/'Content/Maps').glob('L_OpeningLobby*.umap'))==[CURRENT]
    write('protected-after',dict(passed=not errors,checked=len(old)-1-len(ignored_locks),unexpected=errors,config_changes=[],ignored_transient_locks=ignored_locks));assert not errors,errors
    assert digest(FLOOR_MANIFEST)=='0b7a2c9733eabc304c60c47ffa64beed93da1d6d0a0c96d8324969de709f9fc1'
    history=[]
    for row in json.loads(FLOOR_MANIFEST.read_text())['entries']:
        p=ROOT/row['path']
        if row['path']=='Content/Maps/'+CURRENT+'.umap':p=OUT/'Before'/(CURRENT+'.umap')
        actual=entry(p)
        assert actual['sha256']==row['sha256'] and actual['bytes']==row['bytes'],row
        history.append(dict(original=row,resolved=actual))
    # Resolve accepted stone's earlier map through its exact Floor01 archive.
    stone=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json'
    assert digest(stone)=='69aadd32025c61a93210c4caf4b02fb1bf10c88882b5006300f52aeece66eec1'
    archives=json.loads((ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/archive.json').read_text())['entries']
    mappings={r['original']['path']:r['archive'] for r in archives}
    stone_rows=[]
    for row in json.loads(stone.read_text())['entries']:
        p=ROOT/(mappings[row['path']]['path'] if row['path'] in mappings else row['path'])
        actual=entry(p)
        assert actual['sha256']==row['sha256'] and actual['bytes']==row['bytes'],row
        stone_rows.append(dict(original=row,resolved=actual))
    write('approved-history-final-verification',dict(passed=True,floor_manifest=entry(FLOOR_MANIFEST),floor_entries=history,stone_manifest=entry(stone),stone_entries=stone_rows))
    print('Protected assets/config and exact accepted Floor01/Stone01 history verified.')
def textures():
    spec=importlib.util.spec_from_file_location('existing_png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    rows=[]
    for ch in ['BaseColor','ORM','Normal']:
        p=ROOT/'Assets/Source/OpeningLobby/PainterMetal01/Channels'/('T_PainterMetal01_'+ch+'.png')
        info,pixels=helper.decode_png(p.read_bytes());assert (info['width'],info['height'])==(2048,2048)
        counts=[Counter(pixels[c::4]) for c in range(3)]
        summary=[dict(min=min(c),max=max(c),mean=sum(v*n for v,n in c.items())/sum(c.values()),unique=len(c)) for c in counts]
        if ch=='ORM':assert set(counts[0])=={255} and set(counts[2])=={0} and 68<=min(counts[1])<max(counts[1])<=78
        if ch=='Normal':assert min(counts[2])>=250 and min(counts[0])>=120 and max(counts[0])<=135 and min(counts[1])>=120 and max(counts[1])<=135
        if ch=='BaseColor':assert all(48<=min(c)<=max(c)<=60 and len(c)<=2 for c in counts)
        rows.append(dict(channel=ch,file=entry(p),info=info,channels_rgb=summary))
    write('texture-channel-verification',dict(passed=True,rows=rows,meanings='sRGB charcoal coating. DirectX tangent-space normal. Linear ORM: R neutral AO 1, G satin roughness, B dielectric coating metallic 0. Native roughness and microheight structure only; no pixel generation.'))
    print(json.dumps(rows))
if __name__=='__main__':
    import sys
    for op in sys.argv[1:]:globals()[op]()
