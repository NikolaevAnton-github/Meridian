"""Freeze exact Metal01 source, regeneration and review package once."""
import json
from paintermetal01_evidence import ROOT,OUT,CURRENT,entry,write,walk,usage,FLOOR_MANIFEST

def regeneration():
    src=ROOT/'Assets/Source/OpeningLobby/PainterMetal01'
    rows=[]
    for exported,channel in [('BaseColor','BaseColor'),('OcclusionRoughnessMetallic','ORM'),('Normal','Normal')]:
        files=[OUT/'Exports'/folder/('StoneSample_240cm_PainterStone01_'+exported+'.png') for folder in ['Final','ReopenedFinal','ReopenedStableFinal']]
        files.append(src/'Channels'/('T_PainterMetal01_'+channel+'.png'))
        entries=[entry(p) for p in files]
        assert len({(r['bytes'],r['sha256']) for r in entries})==1
        rows.append(dict(channel=channel,exact_files=entries))
    opened=json.loads((OUT/'Native/openFinalStable.json').read_text())['structuredContent']
    assert opened['open'] and not opened['needs_saving']
    assert opened['path'].replace('\\','/')==str(src/'Metal.spp').replace('\\','/')
    readback=json.loads((OUT/'Native/finalNativeReadback.json').read_text())
    assert not readback['audit']['issues'] and readback['audit']['layer_count']==4
    write('exact-regeneration',dict(passed=True,source=entry(src/'Metal.spp'),channels=rows,open_evidence=entry(OUT/'Native/openFinalStable.json'),export_evidence=entry(OUT/'Native/regenerationStableExport.json'),native_readback=entry(OUT/'Native/finalNativeReadback.json'),note='First reopen changed only group UI state; Full save then second close/open was clean. Final exact source bytes were regenerated after the second reopen. No authored channel change between those reopens.'))
    print('Final saved/reopened .spp exactly regenerates all three canonical PNGs.')

def finalize():
    assert not (OUT/'manifest.json').exists(),'Freeze once.'
    for name in ['property-preservation','accepted-floor-bindings','protected-after','capture-verification','texture-channel-verification','exact-regeneration','approved-history-final-verification']:
        assert json.loads((OUT/(name+'.json')).read_text())['passed'],name
    restored=json.loads((OUT/'RestoredFinal/state.json').read_text())
    assert not restored['pie'] and not restored['dirty_content'] and not restored['dirty_maps']
    assert json.loads((OUT/'tick-restored.json').read_text())==dict(value=1,expected=1)
    src=ROOT/'Assets/Source/OpeningLobby/PainterMetal01'
    current=usage();before=json.loads((OUT/'storage-before.json').read_text())
    current.update(project_growth_bytes=current['project_bytes']-before['project_bytes'],lobby_growth_bytes=current['lobby_bytes']-before['lobby_bytes'],task_artifact_bytes=sum(p.stat().st_size for f in [OUT,src,ROOT/'Content/OpeningLobby/PainterMetal01'] for p in walk(f)),project_limit_bytes=250_000_000_000,lobby_limit_bytes=2_000_000_000,growth_aim_bytes=160_000_000)
    current['within_limits']=current['project_bytes']<current['project_limit_bytes'] and current['lobby_bytes']<current['lobby_limit_bytes']
    current['within_growth_aim']=current['lobby_growth_bytes']<=current['growth_aim_bytes']
    current['remaining_lobby_headroom_bytes']=current['lobby_limit_bytes']-current['lobby_bytes']
    assert current['within_limits'],current
    write('storage',current)
    key=[ROOT/'Content/Maps'/(CURRENT+'.umap'),src/'Metal.spp',OUT/'Before'/(CURRENT+'.umap'),src/'recipe.json']
    identity=dict(candidate='LobbyPainter-Metal01/WorkerCandidate01',author_revision='QARevision01',author_qa_revisions=1,review_status='Fresh independent review pending. Metal is not owner accepted.',current_map='/Game/Maps/'+CURRENT,files=[entry(p) for p in key],accepted_floor_manifest=entry(FLOOR_MANIFEST),allowed_bindings=10,protected_stone_bindings=4,protected_floor_bindings=3,final_state=restored)
    write('identity',identity)
    files=set(key)
    for f in [OUT,src,ROOT/'Content/OpeningLobby/PainterMetal01']:
        files.update(p for p in walk(f) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('paintermetal01_*.py'))
    for f in ['Assets/Source/OpeningLobby/PainterStone01','Content/OpeningLobby/PainterStone01','Assets/Source/OpeningLobby/PainterFloor01','Content/OpeningLobby/PainterFloor01']:
        files.update(p for p in walk(ROOT/f) if not p.name.endswith(('.lock','.painter_lock')))
    files.update(ROOT/p for p in ['Docs/OpeningLobbyPainterMetal01.md','Docs/Tasks/OpeningLobbyPainterMetal01.md','Docs/PainterWorkflow.md','Docs/Approvals/LobbyPainterFloor01-Acceptance01.json','Docs/Approvals/LobbyPainterStone01-Acceptance01.json','Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png','Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png','Saved/OpeningLobby/PainterFloor01/Worker/manifest.json','Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json','Saved/OpeningLobby/PainterFloor01/Worker/archive.json','Scripts/OpeningLobby/functionalbuild01_preflight.py','Scripts/OpeningLobby/functionalbuild01_client.py','Scripts/OpeningLobby/materialintegration01_unreal.py','Scripts/OpeningLobby/painterstone01_material.py','Scripts/OpeningLobby/painterstone01_check.py','Scripts/OpeningLobby/painterfloor01_check.py','Scripts/OpeningLobby/painterfloor01_evidence.py','Scripts/OpeningLobby/painterstone01_evidence.py','Scripts/OpeningLobby/reworka01_capture.py','Scripts/OpeningLobby/architecture01_lightstudy.py','Scripts/OpeningLobby/architecture01_reflection.py','Scripts/OpeningLobby/stage1_tools.py','Scripts/Benchmarks/OrchestrationAB/verify_maps.py','Config/DefaultEngine.ini'])
    entries=[entry(p) for p in sorted(files)]
    assert entries and len(entries)==len({r['path'] for r in entries}) and all(r['bytes']>0 for r in entries)
    write('manifest',dict(candidate=identity['candidate'],identity='Saved/OpeningLobby/PainterMetal01/Worker/identity.json',entries=entries,total_bytes=sum(r['bytes'] for r in entries)))
    for r in entries:assert entry(ROOT/r['path'])==r,r
    report=dict(passed=True,manifest=entry(OUT/'manifest.json'),identity=entry(OUT/'identity.json'),entries=len(entries),storage=current)
    write('manifest-verification',report)
    print(json.dumps(report))
if __name__=='__main__':
    import sys
    regeneration() if sys.argv[1]=='regeneration' else finalize()
