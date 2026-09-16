"""Metal01 fingerprints and exact rollback, reusing the reviewed file walker."""
import json
import shutil
from pathlib import Path
from functionalbuild01_preflight import walk,digest
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/PainterMetal01/Worker'
CURRENT='L_OpeningLobby_PainterStone01'
FLOOR_MANIFEST=ROOT/'Saved/OpeningLobby/PainterFloor01/Worker/manifest.json'
TARGETS=dict(zip(['StaticMeshActor_'+str(n) for n in [3,4,13,14,16,24,28,34,39,41]],['FB01_EPos_Frame','FB01_EPos_Leaf','FB01_ENeg_Frame','FB01_ENeg_Leaf','FB01_IPos_Frame','FB01_IPos_Leaf','FB01_INeg_Frame','FB01_INeg_Leaf','FB01_Checkpoint','FB01_ElevatorLeaves']))
OLD='/Game/OpeningLobby/ArchitectureReworkA01/Materials/M_RA01_Metal.M_RA01_Metal'
NEW='/Game/OpeningLobby/PainterMetal01/Materials/M_PainterMetal01.M_PainterMetal01'
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p))
def write(name,data):
    p=OUT/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2));return data
def usage():return dict(project_bytes=sum(p.stat().st_size for p in walk(ROOT)),lobby_bytes=sum(p.stat().st_size for f in ['Saved/OpeningLobby','Assets/Concepts/OpeningLobby','Assets/Source/OpeningLobby','Content/OpeningLobby'] for p in walk(ROOT/f)))
def prepare():
    assert not (OUT/'protected-before.json').exists()
    assert digest(FLOOR_MANIFEST)=='0b7a2c9733eabc304c60c47ffa64beed93da1d6d0a0c96d8324969de709f9fc1'
    rows=json.loads(FLOOR_MANIFEST.read_text())['entries']
    for row in rows:assert entry(ROOT/row['path'])==row,row
    write('approved-manifest-verification',dict(manifest=entry(FLOOR_MANIFEST),verified=len(rows)))
    write('storage-before',usage())
    protected=[]
    for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source']:
        protected.extend(entry(p) for p in walk(ROOT/f) if '__pycache__' not in str(p) and 'paintermetal01_' not in p.name)
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected))
    p=ROOT/'Content/Maps'/(CURRENT+'.umap');target=OUT/'Before'/p.name
    assert digest(p)=='5cc84cac736d24cfe0dedf4c4d1dd0413b3d07f081c9e82e5dd4ab2ca0ae9270'
    target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();shutil.copy2(p,target)
    assert digest(p)==digest(target)
    write('archive',dict(entries=[dict(original=entry(p),archive=entry(target))],historical_resolution='Accepted Floor01 map resolves to this exact Before archive; prior stone and retired maps retain the Floor01 archive mapping. No historical manifest edited.'))
    mesh=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Exports/StoneSample_240cm.fbx'
    target=OUT/'Exports/StoneSample_240cm.fbx';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(mesh,target)
    write('authoring-mesh',dict(original=entry(mesh),task_copy=entry(target),physical_size_cm=240,projection_coverage_cm=120,reason='Read-only original; identical copy in authorized mesh root. Final texture projection intentionally covers 120 cm for fine satin structure.'))
    write('planned-bindings',dict(rows=[dict(actor=a,label=l,component='StaticMeshComponent0',slot=0,old=OLD,new=NEW) for a,l in TARGETS.items()]))
    (OUT/'assembly-contract.md').write_text('''# LobbyPainter-Metal01 / WorkerCandidate01\n\nOne new native Painter family: charcoal satin coating over architectural metal.\nThe opaque coating is dielectric: metallic 0, sRGB charcoal base around 0.20,\nroughness around 0.32, dielectric F0 0.04. Fine native roughness variation,\nno color clouds, seams, damage, or simulated geometry. 2048 DirectX packed export,\nworld projection 120 cm. Satin reflections describe the existing metal forms.\n\nThe ten actor/component/slot identities in planned-bindings.json are the only\nauthorized scene differences. Confirm live labels and inherited material paths\nbefore binding. Preserve accepted four stone and three floor bindings, every\nother reflected property and all old source/content/config bytes.\n\nBoth actual OwnerReferences01 images inspected: subdued dark service doors and\ncheckpoint silhouettes with thin highlights, subservient to stone and floor.\nNo broad material rollout, modeling, lighting, glass, gameplay or atmosphere.\n\nAcceptance: native editable source and exact final regeneration, clean reopened\nmap, ten overrides only, complete property and protected-byte checks, compiled\nnew-only graph, channel/settings verification, five genuine matched standing\n1920x1080 HFOV90 captures and possession check, restored capture settings, unique\nnonempty manifest and bounded measured storage. Fresh independent review and\nowner metal-direction decision remain pending. At most two author QA revisions.\n''')
    print(json.dumps(dict(approved_entries=len(rows),protected=len(protected),archived_map=entry(OUT/'Before'/(CURRENT+'.umap')))))
if __name__=='__main__':prepare()
