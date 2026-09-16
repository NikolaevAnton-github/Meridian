"""Freeze Correction03 with explicit unresolved visual findings."""
import json,hashlib
from materialscomplete01_optics_check import *

def freeze():
    assert not (OUT/'manifest.json').exists()
    for name in ['archive-verification','coverage','property-preservation','capture-verification','native-source-verification','transmission-verification','protected-after','history-verification','storage']:
        assert read(OUT/(name+'.json'))['passed'],name
    state=read(OUT/'RestoredFinal/state.json');assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    sources=[]
    for rel,ranges in [('Renderer/Private/FrontLayerTranslucency.cpp',[(70,75)]),('Engine/Private/Materials/MaterialShared.cpp',[(2189,2196)]),('Renderer/Private/Lumen/LumenReflections.cpp',[(108,119),(422,432)])]:
        p=Path('D:/UE_5.8/Engine/Source/Runtime')/rel;b=p.read_bytes();lines=b.decode('utf-8-sig').splitlines()
        sources.append(dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),excerpts=[dict(start=a,end=z,text='\n'.join(lines[a-1:z])) for a,z in ranges]))
    write('renderer-source-evidence',dict(installed_engine=state['engine'],sources=sources,interpretation='Eligibility and cutoff inputs only; actual GPU execution not observed. Local on/off comparisons show no recognizable reflected scene contribution. Roughness-only causality not isolated.'))
    result=dict(candidate='LobbyMaterials-Complete01/Correction03',R1='UNRESOLVED',R2='CORRECTION01_RETAINED_PENDING_INDEPENDENT_RECHECK',owner_review_ready=False,scene_reflection_structure='NOT_DEMONSTRATED',transmission='PASS',comparisons=3,fine_adjustments=1,final_local_flags=dict(override=False,value=False),images_inspected=[p.relative_to(ROOT).as_posix() for p in sorted(OUT.rglob('*.png'))],references=[entry(ROOT/'Assets/Concepts/OpeningLobby/OwnerReferences01'/n) for n in ['01-InnerEnd.png','02-EntranceSecurity.png']],reason='New neutral preset and reduced micro-slope retained. Fixed-pane broad highlight and insufficient reflected scene structure prevent R1 closure. Both local flags restored because comparisons showed no useful benefit.')
    write('visual-outcome',result)
    recipe=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Correction03/recipe.json'
    identity=dict(candidate=result['candidate'],status='Bounded calibration complete; visual R1 unresolved; combined fresh Review02 required.',R1=result['R1'],R2=result['R2'],owner_review_ready=False,map=entry(ROOT/MAPFILE),native_assets=[entry(p) for p in sorted((ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction03').glob('*.uasset'))],recipe=entry(recipe),unchanged_ceiling_spp=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp'),previous_manifest=entry(PREV/'manifest.json'),previous_identity=entry(PREV/'identity.json'),rollback=entry(CTRL/'BeforeOptics01/archive.json'),preparation_archive=entry(CTRL/'optics-registration-preparation-archive.json'),coverage=dict(lobby=107,support=1,changed=6,accepted_preserved=17,ceiling_preserved=9),final_local_flags=result['final_local_flags'],final_state=state,technical='PASS with explicit external controller file exceptions',external_changes=read(OUT/'protected-after.json')['external_controller_logs'])
    write('identity',identity)
    files={ROOT/MAPFILE,OUT/'identity.json',PREV/'manifest.json',PREV/'identity.json',ROOT/'Docs/OpeningLobbyMaterialsComplete01Correction03.md',ROOT/'Docs/Tasks/OpeningLobbyMaterialsComplete01Correction03.md',CTRL/'optics-registration-preparation-archive.json'}
    files.update(ROOT/r['path'] for r in read(PREV/'manifest.json')['entries'])
    for folder in [OUT,recipe.parent,ROOT/'Content/OpeningLobby/MaterialsComplete01/Correction03',CTRL/'BeforeOptics01',CTRL/'OpticsRegistrationPreparation']:
        files.update(p for p in walk(folder) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('materialscomplete01_optics*.py'))
    entries=[entry(p) for p in sorted(files)];assert len(entries)==len({r['path'] for r in entries}) and all(r['bytes']>0 for r in entries)
    write('manifest',dict(candidate=result['candidate'],identity=entry(OUT/'identity.json'),entries=entries,total_bytes=sum(r['bytes'] for r in entries),history='Earlier manifests remain unchanged. Earlier current-map identities resolve only via the exact archived bytes in history-verification.json. This manifest identifies current Correction03 bytes.'))
    for r in entries:assert entry(ROOT/r['path'])==r,r
    result=dict(passed=True,manifest=entry(OUT/'manifest.json'),identity=entry(OUT/'identity.json'),map=entry(ROOT/MAPFILE),entries=len(entries))
    write('manifest-verification',result);print(json.dumps(result))

if __name__=='__main__':
    from pathlib import Path
    freeze()
