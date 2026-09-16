"""Freeze exact Correction02, preserving the unresolved visual requirement."""
import json
from materialscomplete01_support_check import ROOT,OUT,PREV,INITIAL,MAPFILE,entry,read,write,walk,storage

def freeze():
    assert not (OUT/'manifest.json').exists()
    for name in ['coverage','property-preservation','support-census','protected-after','history-verification','capture-verification','transmission-verification','native-source-verification']:
        assert read(OUT/(name+'.json'))['passed'],name
    assert read(OUT/'property-preservation.json')['restored_checked']
    state=read(OUT/'RestoredFinal/state.json');assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction02'
    recipe=read(source/'recipe-Setup01.json')
    recipe.update(chosen_setup='Setup01',purposeful_setups=2,rejected_setup=entry(OUT/'setup-Setup02.json'),rejection=entry(OUT/'Setup02/rejection.json'),existing_binding_changes=0,visual_R1='PARTIAL_UNRESOLVED',visual_R2='CORRECTION01_RETAINED_PENDING_INDEPENDENT_RECHECK')
    (source/'recipe.json').write_text(json.dumps(recipe,indent=2))
    write('visual-outcome',dict(candidate=recipe['candidate'],R1='PARTIAL_UNRESOLVED',R2='CORRECTION01_RETAINED_PENDING_INDEPENDENT_RECHECK',owner_review_ready=False,whole_entrance='Fixed panes remain overly uniform grey sheets. Entry leaves are now visible through real far-field radiance; brighter panes are not sufficient glass likeness.',reflection_trial='Runtime capture skipped by preserved renderer mode 0; no claim about efficacy of working baked captures or Skylight. Removed task-created actor.',support_exception=recipe['exception'],images_inspected=[p.relative_to(ROOT).as_posix() for p in sorted((OUT/'Final').glob('*.png'))],controls=['Hidden','Opaque','SupportOff'],reference_images=['Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png','Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png'],no_final_atmosphere_acceptance=True))
    storage()
    identity=dict(candidate=recipe['candidate'],status='Verified bounded support candidate, R1 unresolved; focused independent review/controller handoff, not completed visual finish.',owner_review_ready=False,technical_checks='PASS with documented externally refreshed controller transcript exception',R1='PARTIAL_UNRESOLVED',R2='CORRECTION01_RETAINED_PENDING_INDEPENDENT_RECHECK',map=entry(ROOT/MAPFILE),support_assets=[entry(p) for p in sorted((ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction02').glob('*.uasset'))],recipe=entry(source/'recipe.json'),unchanged_ceiling_spp=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp'),previous_identity=entry(PREV/'identity.json'),previous_manifest=entry(PREV/'manifest.json'),rollback=entry(ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeSupport01/archive.json'),coverage=dict(existing=107,existing_bindings_changed=0,accepted_preserved=17,ceiling_preserved=9,new_support_actors=1,new_light_or_reflection_actors=0),purposeful_setups=2,support_exception=recipe['exception'],final_state=state)
    write('identity',identity)
    files={ROOT/MAPFILE,OUT/'identity.json',PREV/'manifest.json',PREV/'identity.json',ROOT/'Docs/OpeningLobbyMaterialsComplete01Correction02.md',ROOT/'Docs/Tasks/OpeningLobbyMaterialsComplete01Correction02.md'}
    files.update(ROOT/r['path'] for r in read(PREV/'manifest.json')['entries'])
    for folder in [OUT,source,ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction02',ROOT/'Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeSupport01']:
        files.update(p for p in walk(folder) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('materialscomplete01_support*.py'))
    entries=[entry(p) for p in sorted(files)]
    assert len(entries)==len({r['path'] for r in entries}) and all(r['bytes']>0 for r in entries)
    write('manifest',dict(candidate=identity['candidate'],identity=entry(OUT/'identity.json'),entries=entries,total_bytes=sum(r['bytes'] for r in entries),history='Previous manifests unchanged; only their current-map entries resolve through exact archives in history-verification.json. This manifest identifies Correction02 current-map bytes.'))
    for r in entries:assert entry(ROOT/r['path'])==r,r
    write('manifest-verification',dict(passed=True,manifest=entry(OUT/'manifest.json'),identity=entry(OUT/'identity.json'),map=entry(ROOT/MAPFILE),entries=len(entries)))
    print(json.dumps(read(OUT/'manifest-verification.json')))
if __name__=='__main__':freeze()
