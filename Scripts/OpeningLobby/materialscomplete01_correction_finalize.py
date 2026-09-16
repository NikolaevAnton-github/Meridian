"""Freeze Correction01 with explicit unresolved visual finding."""
import json
from materialscomplete01_correction_check import ROOT,OUT,INITIAL,entry,write,read,walk,MAPFILE,storage
def transmission():
    import materialscomplete01_finalize as existing
    existing.OUT=OUT
    def scoped_write(name,data):
        if name=='transmission-verification':
            data['interpretation']='Existing hall, columns, floor and checkpoint remain visible through corrected leaves and fixed sidelights; opaque control on identical meshes hides them. This verifies genuine scene transmission, not calibrated photometry or R1 visual closure. Interior controls reveal black background through absent panes. Final fixed panes still have uniform grey body under unchanged lighting; R1 remains partially unresolved.'
        return write(name,data)
    existing.write=scoped_write
    existing.transmission()
def freeze():
    assert not (OUT/'manifest.json').exists()
    for name in ['coverage','property-preservation','protected-after','history-verification','capture-verification','graph-source-verification','transmission-verification','storage']:
        assert read(OUT/(name+'.json'))['passed'],name
    state=read(OUT/'RestoredFinal/state.json');assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction01'
    recipe=dict(candidate='LobbyMaterials-Complete01/Correction01',stone_candidate='Candidate01',glass_candidate='Candidate02',stone=read(source/'recipe-Candidate01.json')['Stone'],glass=read(source/'recipe-Candidate02.json'),new_painter_pixels=False,source_reuse='Accepted Painter stone channels and initial Ceiling.spp remain unchanged, verified by history-verification.json; no ceremonial source project.',visual_R1='Partial improvement; unresolved uniform fixed-glass body. Fresh focused review required.',visual_R2='Broad fields corrected; author closure proposed within exact 19 target scope. Untouched structural/accepted highlights persist.')
    (source/'recipe.json').write_text(json.dumps(recipe,indent=2))
    identity=dict(candidate=recipe['candidate'],status='Bounded correction handoff for focused Review02; R1 not claimed closed.',owner_review_ready=False,technical_verification='PASS',required_correction_response=dict(R1='PARTIAL_UNRESOLVED',R2='ADDRESSED_PENDING_INDEPENDENT_RECHECK'),map=entry(ROOT/MAPFILE),graphs=[entry(p) for p in sorted((ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction01').glob('*.uasset'))],source=entry(source/'recipe.json'),unchanged_native_sources=[entry(ROOT/p) for p in ['Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp','Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json','Saved/OpeningLobby/PainterFloor01/Worker/manifest.json','Saved/OpeningLobby/PainterMetal01/Worker/manifest.json']],initial_manifest=entry(INITIAL/'manifest.json'),initial_archive_receipt=entry(ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeCorrection01/archive.json'),coverage=dict(visible=107,changed=25,glass_changed=6,stone_changed=19,preserved=82,accepted_preserved=17,ceiling_preserved=9),purposeful_candidates=dict(glass=2,stone=1),final_state=state)
    write('identity',identity)
    files={ROOT/MAPFILE,OUT/'identity.json',INITIAL/'manifest.json',INITIAL/'identity.json',ROOT/'Docs/OpeningLobbyMaterialsComplete01Correction01.md',ROOT/'Docs/Tasks/OpeningLobbyMaterialsComplete01Correction01.md'}
    # Initial entries are linked in place. The old map resolves via its archive;
    # the same current-map path below identifies only Correction01 bytes.
    files.update(ROOT/r['path'] for r in read(INITIAL/'manifest.json')['entries'])
    for folder in [OUT,source,ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction01',ROOT/'Saved/OpeningLobby/MaterialsComplete01/Review01',ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeCorrection01']:
        files.update(p for p in walk(folder) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('materialscomplete01_correction*.py'))
    entries=[entry(p) for p in sorted(files)]
    assert len(entries)==len({r['path'] for r in entries}) and all(r['bytes']>0 for r in entries)
    write('manifest',dict(candidate=identity['candidate'],identity=entry(OUT/'identity.json'),entries=entries,total_bytes=sum(r['bytes'] for r in entries),historical_map_resolution='See history-verification.json; original manifest is immutable and its map entry resolves only to controller BeforeCorrection01 archive.'))
    for r in entries:assert entry(ROOT/r['path'])==r,r
    write('manifest-verification',dict(passed=True,manifest=entry(OUT/'manifest.json'),identity=entry(OUT/'identity.json'),entries=len(entries)))
    print(json.dumps(read(OUT/'manifest-verification.json')))
if __name__=='__main__':
    import sys
    for op in sys.argv[1:]:globals()[op]()
