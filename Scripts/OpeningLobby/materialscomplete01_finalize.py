"""Freeze exact complete-batch identity and verification manifest."""
import json,importlib.util
from materialscomplete01_evidence import ROOT,OUT,CURRENT,entry,write,walk,usage,digest
def transmission():
    spec=importlib.util.spec_from_file_location('existing_png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    records={};reference=None
    # Quantitative checks describe transmitted scene visibility, not a calibrated
    # photometric transmittance measurement of the glass.
    for name in ['transmission-90','without-panes-90','opaque-control-90']:
        p=OUT/'Transmission'/(name+'.png');cam=json.loads(p.with_name(name+'-camera.json').read_text())
        pose={k:cam[k] for k in ['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution']}
        if reference is None:reference=pose
        assert pose==reference and cam['runtime']['ready']
        info,pixels=h.decode_png(p.read_bytes());assert (info['width'],info['height'])==(1920,1080)
        regions={}
        for label,(x0,y0,x1,y1) in {'leaf':(610,350,870,700),'fixed_sidelight':(100,350,260,800)}.items():
            values=[sum(pixels[(y*1920+x)*4:(y*1920+x)*4+3])/3 for y in range(y0,y1,4) for x in range(x0,x1,4)]
            regions[label]=dict(mean_srgb_8bit=sum(values)/len(values),min=min(values),max=max(values),samples=len(values))
        records[name]=dict(image=entry(p),camera=entry(p.with_name(name+'-camera.json')),regions=regions,state=cam['diagnostic_state'])
    for r in ['leaf','fixed_sidelight']:
        assert records['transmission-90']['regions'][r]['mean_srgb_8bit']>records['opaque-control-90']['regions'][r]['mean_srgb_8bit']+5
    for name in ['restored','pose-restored','opaque-control-restored']:assert json.loads((OUT/'Transmission'/(name+'.json')).read_text())['passed']
    write('transmission-verification',dict(passed=True,records=records,interpretation='Existing hall columns, floor and checkpoint remain visible through final glass; the identical pane meshes with an opaque material occlude them. Near-unity reverse-side transmission is observed relative to absent panes. Interior fixed-pane reflection/scattering is softer and brighter than the less diffuse leaves. This is not a calibrated transmittance or distortion measurement; no exterior scenery exists.',restored=True))
    print('Real transmitted-scene visibility verified against absent-pane and opaque controls.')
def finalize():
    assert not (OUT/'manifest.json').exists()
    for name in ['coverage','property-preservation','protected-after','accepted-history','capture-verification','texture-channel-verification','exact-regeneration','transmission-verification','live-material-audit']:
        assert json.loads((OUT/(name+'.json')).read_text())['passed'],name
    state=json.loads((OUT/'RestoredFinal/state.json').read_text());assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    src=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01'
    regeneration=json.loads((OUT/'exact-regeneration.json').read_text());assert entry(src/'Ceiling.spp')==regeneration['source']
    current=usage();before=json.loads((OUT/'storage-before.json').read_text())
    current.update(project_growth_bytes=current['project_bytes']-before['project_bytes'],lobby_growth_bytes=current['lobby_bytes']-before['lobby_bytes'],task_artifact_bytes=sum(p.stat().st_size for f in [OUT,src,ROOT/'Content/OpeningLobby/MaterialsComplete01'] for p in walk(f)),project_limit_bytes=250_000_000_000,lobby_limit_bytes=2_400_000_000,growth_aim_bytes=300_000_000,correction_limit_bytes=400_000_000)
    current['within_limits']=current['project_bytes']<250_000_000_000 and current['lobby_bytes']<2_400_000_000 and current['lobby_growth_bytes']<400_000_000
    current['within_growth_aim']=current['lobby_growth_bytes']<300_000_000;assert current['within_limits'],current
    write('storage',current)
    identity=dict(candidate='LobbyMaterials-Complete01/WorkerCandidate01',status='Complete author candidate for fresh independent review; new batch and final atmosphere are not owner accepted.',current_map='/Game/Maps/'+CURRENT,files=[entry(p) for p in [ROOT/'Content/Maps'/(CURRENT+'.umap'),src/'Ceiling.spp',src/'recipe.json',OUT/'Before'/(CURRENT+'.umap')]],coverage=dict(visible=107,replaced=90,preserved=17,stone=44,floor_strip=3,metal=45,ceiling=9,glass=6,proxies=0),author_qa_revisions=dict(ceiling=0,glass=1),final_state=state)
    write('identity',identity)
    files={ROOT/'Content/Maps'/(CURRENT+'.umap')}
    for folder in [OUT,src,ROOT/'Content/OpeningLobby/MaterialsComplete01']:
        files.update(p for p in walk(folder) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('materialscomplete01_*.py'))
    for folder in ['PainterStone01','PainterFloor01','PainterMetal01']:
        for base in ['Assets/Source/OpeningLobby','Content/OpeningLobby']:
            files.update(p for p in walk(ROOT/base/folder) if not p.name.endswith(('.lock','.painter_lock')))
    files.update(ROOT/p for p in ['Docs/OpeningLobbyMaterialsComplete01.md','Docs/Tasks/OpeningLobbyMaterialsComplete01.md','Docs/PainterWorkflow.md','Docs/Approvals/LobbyPainterMetal01-Acceptance01.json','Docs/Approvals/LobbyPainterFloor01-Acceptance01.json','Docs/Approvals/LobbyPainterStone01-Acceptance01.json','Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png','Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png','Saved/OpeningLobby/PainterMetal01/Worker/manifest.json','Saved/OpeningLobby/PainterFloor01/Worker/manifest.json','Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json','Saved/OpeningLobby/PainterFloor01/Worker/archive.json','Scripts/OpeningLobby/functionalbuild01_preflight.py','Scripts/OpeningLobby/functionalbuild01_client.py','Scripts/OpeningLobby/materialintegration01_unreal.py','Scripts/OpeningLobby/painterstone01_material.py','Scripts/OpeningLobby/painterstone01_check.py','Scripts/OpeningLobby/paintermetal01_capture.py','Scripts/OpeningLobby/reworka01_capture.py','Scripts/OpeningLobby/reworka01_kit.py','Scripts/OpeningLobby/verify_lobby.py','Scripts/OpeningLobby/architecture01_lightstudy.py','Scripts/OpeningLobby/architecture01_reflection.py','Scripts/OpeningLobby/stage1_tools.py','Scripts/Benchmarks/OrchestrationAB/verify_maps.py','Config/DefaultEngine.ini'])
    entries=[entry(p) for p in sorted(files)]
    assert entries and all(r['bytes']>0 for r in entries) and len(entries)==len({r['path'] for r in entries})
    write('manifest',dict(candidate=identity['candidate'],identity=entry(OUT/'identity.json'),entries=entries,total_bytes=sum(r['bytes'] for r in entries)))
    for r in entries:assert entry(ROOT/r['path'])==r,r
    result=dict(passed=True,manifest=entry(OUT/'manifest.json'),identity=entry(OUT/'identity.json'),entries=len(entries),storage=current)
    write('manifest-verification',result);print(json.dumps(result))
if __name__=='__main__':
    import sys
    globals()[sys.argv[1]]()
