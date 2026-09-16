"""Complete-batch exact baseline, role schedule and evidence utilities."""
import json, shutil
from pathlib import Path
from functionalbuild01_preflight import walk,digest
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker'
CURRENT='L_OpeningLobby_PainterStone01'
ASSETS='/Game/OpeningLobby/MaterialsComplete01'
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p))
def write(name,data):
    p=OUT/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2));return data
def usage():return dict(project_bytes=sum(p.stat().st_size for p in walk(ROOT)),lobby_bytes=sum(p.stat().st_size for f in ['Saved/OpeningLobby','Assets/Concepts/OpeningLobby','Assets/Source/OpeningLobby','Content/OpeningLobby'] for p in walk(ROOT/f)))
def prepare():
    assert not (OUT/'protected-before.json').exists()
    manifest=ROOT/'Saved/OpeningLobby/PainterMetal01/Worker/manifest.json'
    assert digest(manifest)=='d056461ecf7bdaed92cb8ee463d6514c5b76218ef91fee3bdbf50c2c54b36035'
    rows=json.loads(manifest.read_text())['entries']
    for r in rows:assert entry(ROOT/r['path'])==r,r
    write('accepted-manifest-verification',dict(passed=True,manifest=entry(manifest),entries=len(rows)))
    write('storage-before',usage())
    protected=[entry(p) for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source'] for p in walk(ROOT/f) if '__pycache__' not in str(p) and 'materialscomplete01_' not in p.name and not p.name.endswith(('.lock','.painter_lock'))]
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected))
    p=ROOT/'Content/Maps'/(CURRENT+'.umap');target=OUT/'Before'/p.name
    assert digest(p)=='abc72118717b8333a109fdeeaf1583485a3e7b35badced84204e9fcc130ebc92'
    target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();shutil.copy2(p,target)
    assert digest(target)==digest(p)
    write('archive',dict(entries=[dict(original=entry(p),archive=entry(target))]))
    mesh=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Exports/StoneSample_240cm.fbx'
    target=OUT/'Exports'/mesh.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(mesh,target)
    write('authoring-mesh',dict(original=entry(mesh),task_copy=entry(target),coverage_cm=120))
    (OUT/'assembly-contract.md').write_text('''# LobbyMaterials-Complete01 / WorkerCandidate01

Complete all 90 remaining visible material slots in place. Preserve all 17 accepted
bindings and every other reflected actor/component/world property, all existing
source/content/config bytes and exact historical evidence. Exact rollback is in Before.
Both actual OwnerReferences01 PNGs inspected: dark green mineral architecture,
quieter recess/ceiling surfaces, charcoal hardware, cool diffusing fixed glass and
clearer entry leaves. Accepted stone keeps its 240 cm stochastic projection; metal
keeps its 120 cm satin coating projection. Native new ceiling: dark green-grey plaster,
120 cm coverage, calm uniform base with subtle native roughness and microheight.
New glass: native Substrate simple-volume transmission, F0 .04, fixed roughness .32,
leaf .09, neutral transmission. No emission. Existing geometry and lighting only.

Acceptance: 107 effective bindings, zero proxies/errors, 90 scheduled substitutions,
all properties and accepted bytes preserved, final Painter save/reopen regeneration,
saved/reopened native graphs, matched standing captures, actual transmission diagnostic,
real short walking forward/return, restored clean editor, exact manifest, measured
storage <=2.4 GB lobby and <=250 GB project, growth aim <=300 MB with <=400 MB headroom.
At most two author QA revisions per new family. Fresh independent review follows;
new batch/final atmosphere owner acceptance is not claimed.
''')
    print(json.dumps(dict(protected=len(protected),accepted=len(rows))))
def plan():
    inv=json.loads((OUT/'Before/inventory.json').read_text());assert len(inv)==107
    rows=[]
    for r in inv:
        assert r['visible'] and not r['hidden_in_game'] and not r['actor_hidden'] and len(r['materials'])==1
        old=r['materials'][0];family=old.split('M_RA01_')[-1].split('.')[0]
        accepted=any('/'+n+'/' in old for n in ['PainterStone01','PainterFloor01','PainterMetal01'])
        if accepted:new=old;family='Stone' if 'PainterStone01' in old else 'Metal' if 'PainterMetal01' in old else 'FloorStrip';reason='Preserve owner-accepted binding exactly.'
        elif family in ['Stone','Wall']:new='/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01.M_PainterStone01';family='Stone';reason='Architectural mineral cladding; accepted stone and physical projection, blank opaque logo field included.'
        elif family=='Metal':new='/Game/OpeningLobby/PainterMetal01/Materials/M_PainterMetal01.M_PainterMetal01';reason='Existing entrance collar, mullion, transom or meeting stile; accepted charcoal hardware.'
        elif family=='Ceiling':new=ASSETS+'/Materials/M_MaterialsComplete01.M_MaterialsComplete01';reason='Existing overhead or roof/soffit; new native Painter mineral plaster.'
        elif family=='Glazing':
            role='Leaf' if 'DoorLeaf' in r['label'] else 'Fixed';family='Glass';new=ASSETS+'/Materials/M_MC01_Glass'+role+'.M_MC01_Glass'+role;reason='Native optical '+role.lower()+' pane; real transmission and reflection.'
        else:raise AssertionError(r)
        rows.append(dict(actor=r['actor'],label=r['label'],component=r['component'],slot=0,old=old,new=new,family=family,preserved=accepted,reason=reason,source_overrides=r['overrides']))
    from collections import Counter
    counts=Counter(r['family'] for r in rows);assert counts==dict(Stone=44,Metal=45,FloorStrip=3,Ceiling=9,Glass=6),counts
    assert sum(r['preserved'] for r in rows)==17
    write('coverage-plan',dict(rows=rows,counts=counts,invisible_exclusions=[]))
    print(json.dumps(dict(counts=counts,changed=90,preserved=17)))
if __name__=='__main__':
    import sys
    globals()[sys.argv[1]]()
