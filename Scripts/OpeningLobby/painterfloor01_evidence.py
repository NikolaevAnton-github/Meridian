"""Bounded floor task fingerprints and exact archive; reuse existing walker."""
import json
import shutil
from pathlib import Path
from functionalbuild01_preflight import walk,digest
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/PainterFloor01/Worker'
CURRENT='L_OpeningLobby_PainterStone01'
RETIRED=['L_OpeningLobby','L_OpeningLobby_Layout02','L_OpeningLobby_Layout03','L_OpeningLobby_Architecture01','L_OpeningLobby_Architecture01_GlassReview01','L_OpeningLobby_Architecture01_LightStudy01','L_OpeningLobby_ArchitectureReworkA01','L_OpeningLobby_FunctionalBuild01','L_OpeningLobby_MaterialIntegration01']
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p))
def write(name,data):
    p=OUT/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2));return data
def usage():return dict(project_bytes=sum(p.stat().st_size for p in walk(ROOT)),lobby_bytes=sum(p.stat().st_size for f in ['Saved/OpeningLobby','Assets/Concepts/OpeningLobby','Assets/Source/OpeningLobby','Content/OpeningLobby'] for p in walk(ROOT/f)))
def prepare():
    assert not (OUT/'protected-before.json').exists()
    manifest=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json'
    assert digest(manifest)=='69aadd32025c61a93210c4caf4b02fb1bf10c88882b5006300f52aeece66eec1'
    data=json.loads(manifest.read_text());rows=data['entries']
    for row in rows:assert entry(ROOT/row['path'])==row,row
    write('approved-manifest-verification',dict(manifest=entry(manifest),verified=len(rows)))
    write('storage-before',usage())
    protected=[]
    for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source']:
        protected.extend(entry(p) for p in walk(ROOT/f) if '__pycache__' not in str(p) and 'painterfloor01_' not in p.name)
    protected.extend(entry(ROOT/f) for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes'])
    write('protected-before',dict(entries=protected))
    archive=[]
    for name in [CURRENT]+RETIRED:
        p=ROOT/'Content/Maps'/(name+'.umap');target=OUT/('Before' if name==CURRENT else 'RetiredMaps')/p.name
        target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();shutil.copy2(p,target)
        assert digest(p)==digest(target)
        archive.append(dict(original=entry(p),archive=entry(target)))
    cfg=ROOT/'Config/DefaultEngine.ini';target=OUT/'Before/DefaultEngine.ini';shutil.copy2(cfg,target)
    write('archive',dict(entries=archive,config=dict(original=entry(cfg),archive=entry(target)),historical_resolution='Resolve historical Content/Maps entries using exact archived bytes; all original manifests remain unchanged.'))
    mesh=ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Exports/StoneSample_240cm.fbx'
    target=OUT/'Exports/StoneSample_240cm.fbx';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(mesh,target)
    write('authoring-mesh',dict(original=entry(mesh),task_copy=entry(target),physical_size_cm=240,reason='Identical mesh copied into task-authorized Painter mesh root.'))
    print(json.dumps(dict(approved_entries=len(rows),protected=len(protected),archived_maps=len(archive))))
def finalize():
    assert not (OUT/'manifest.json').exists(),'Freeze once; do not silently rebaseline.'
    required=['property-preservation','protected-after','capture-verification','texture-channel-verification','exact-regeneration','approved-history-final-verification']
    for name in required:assert json.loads((OUT/(name+'.json')).read_text())['passed'],name
    restored=json.loads((OUT/'Restored/state.json').read_text())
    assert not restored['pie'] and not restored['dirty_maps'] and not restored['dirty_content']
    src=ROOT/'Assets/Source/OpeningLobby/PainterFloor01'
    key=[ROOT/'Content/Maps'/(CURRENT+'.umap'),src/'Floor.spp',src/'Strip.spp',OUT/'archive.json',OUT/'bindings.json',ROOT/'Config/DefaultEngine.ini']
    identity=dict(candidate='LobbyPainter-Floor01/WorkerCandidate01',author_revision='QARevision01',review_status='Fresh independent review pending; new floor pair is not owner accepted.',current_map='/Game/Maps/'+CURRENT,files=[entry(p) for p in key],approved_stone_manifest=entry(ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json'),allowed_bindings=3,protected_stone_bindings=4,final_state=restored)
    write('identity',identity)
    files=set()
    for f in [OUT,src,ROOT/'Content/OpeningLobby/PainterFloor01']:
        files.update(p for p in walk(f) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('painterfloor01_*.py'))
    files.update(key)
    files.update(ROOT/p for p in ['Docs/OpeningLobbyPainterFloor01.md','Docs/Tasks/OpeningLobbyPainterFloor01.md','Docs/PainterWorkflow.md','Docs/Approvals/LobbyPainterStone01-Acceptance01.json','Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png','Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png','Scripts/OpeningLobby/functionalbuild01_preflight.py','Scripts/OpeningLobby/functionalbuild01_client.py','Scripts/OpeningLobby/materialintegration01_unreal.py','Scripts/OpeningLobby/painterstone01_material.py','Scripts/OpeningLobby/painterstone01_check.py','Scripts/OpeningLobby/painterstone01_evidence.py','Scripts/OpeningLobby/reworka01_capture.py','Scripts/OpeningLobby/architecture01_lightstudy.py','Scripts/OpeningLobby/architecture01_reflection.py','Scripts/OpeningLobby/stage1_tools.py','Scripts/Benchmarks/OrchestrationAB/verify_maps.py'])
    # Bind every exact approved stone file in addition to its untouched manifest.
    for folder in ['Assets/Source/OpeningLobby/PainterStone01','Content/OpeningLobby/PainterStone01']:
        files.update(p for p in walk(ROOT/folder) if not p.name.endswith(('.lock','.painter_lock')))
    files.add(ROOT/'Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json')
    current=usage();before=json.loads((OUT/'storage-before.json').read_text())
    current.update(project_growth_bytes=current['project_bytes']-before['project_bytes'],lobby_growth_bytes=current['lobby_bytes']-before['lobby_bytes'],task_artifact_bytes=sum(p.stat().st_size for f in [OUT,src,ROOT/'Content/OpeningLobby/PainterFloor01'] for p in walk(f)),project_limit_bytes=250_000_000_000,lobby_limit_bytes=2_000_000_000,growth_aim_bytes=250_000_000)
    current['within_limits']=current['project_bytes']<current['project_limit_bytes'] and current['lobby_bytes']<current['lobby_limit_bytes']
    current['within_growth_aim']=current['lobby_growth_bytes']<current['growth_aim_bytes']
    assert current['within_limits'] and current['within_growth_aim'],current
    current['measurement_note']='Apparent file bytes via existing no-junction walker; measured immediately before writing final manifest. Manifest overhead is reported separately in manifest-verification.json.'
    write('storage',current)
    entries=[entry(p) for p in sorted(files)]
    assert entries and len(entries)==len({e['path'] for e in entries}) and all(e['bytes']>0 for e in entries)
    write('manifest',dict(candidate=identity['candidate'],identity='Saved/OpeningLobby/PainterFloor01/Worker/identity.json',entries=entries,total_bytes=sum(e['bytes'] for e in entries)))
    for e in entries:assert entry(ROOT/e['path'])==e,e
    verification=dict(passed=True,entries=len(entries),manifest=entry(OUT/'manifest.json'),identity=entry(OUT/'identity.json'),manifest_overhead_bytes=(OUT/'manifest.json').stat().st_size,storage=current)
    write('manifest-verification',verification)
    print(json.dumps(verification))

if __name__=='__main__':
    import sys
    finalize() if len(sys.argv)>1 and sys.argv[1]=='finalize' else prepare()
