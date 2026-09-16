"""Freeze SlabLayout01 using the established entry/walk/manifest primitives."""
import json
from pathlib import Path
from materialscomplete01_slabs_check import ROOT, OUT, CTRL, PREV, MAPFILE, entry, read, write, walk, usage
from materialscomplete01_slabs_client import work


def freeze():
    assert not (OUT/'manifest.json').exists()
    required = ['archive-verification','coverage','property-preservation','capture-verification',
                'native-source-verification','layout-numerics','history-verification','storage',
                'Resume01/scene-verification','Resume01/reused-verification',
                'Resume01/protected-after','Resume01/runtime-dispatch-verification']
    for name in required: assert read(OUT/(name+'.json'))['passed'], name
    for row in read(OUT/'Resume01/native-bytes-before.json')['entries']:
        assert entry(ROOT/row['path']) == row
    state = work('state')
    assert state == read(OUT/'Resume01/state.json')
    assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    write('Resume01/final-live-state', state)
    source = ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/SlabLayout01'
    recipe = read(source/'recipe.json')
    assert recipe['candidate'] == 'LobbyMaterials-Complete01/SlabLayout01'
    assets = [entry(p) for p in sorted((ROOT/'Content/OpeningLobby/MaterialsComplete01/SlabLayout01').glob('*.uasset'))]
    assert len(assets) == 45
    visual = dict(candidate=recipe['candidate'], opaque_author_verification='PASS',
        independent_review='PENDING_FRESH_REVIEW02', owner_accepted=False,
        glass='DEFERRED_BY_OWNER', R1='DEFERRED_BY_OWNER',
        old_R2='SUPERSEDED_BY_OWNER_COLUMN_GLOSS_DIRECTION',
        author_refinements_after_representative=0, resume_material_mutations=0,
        final_images_inspected=[entry(p) for p in sorted((OUT/'Final').glob('*.png'))],
        comparisons_inspected=['Before/broad-wall-90.png','Before/column-corner-90.png',
                               'Trial01/broad-wall-90.png','Trial01/column-corner-90.png'],
        references=[entry(ROOT/'Assets/Concepts/OpeningLobby/OwnerReferences01'/n)
                    for n in ['01-InnerEnd.png','02-EntranceSecurity.png']],
        findings='Readable large slabs and continuous corner courses; current wall gloss matches accepted column graph. Trim uses elongated cut pieces. Existing highlight pools and dark returns remain under unchanged lighting.',
        limitations=['Shader normal recess only; no silhouette displacement.',
                     'Accepted continuous mineral world sampling retained, without new per-slab pixels.',
                     'Still captures and filter numerics do not establish a new temporal/performance benchmark.',
                     'Fresh independent opaque review and owner viewing pending; final atmosphere not accepted.'])
    assert len(visual['final_images_inspected']) == 16
    write('visual-outcome', visual)
    protection = read(OUT/'Resume01/protected-after.json')
    identity = dict(candidate=recipe['candidate'],
        status='Opaque author candidate verified; ready for fresh independent combined Review02.',
        ready_for_independent_review=True, owner_review_ready=False, owner_accepted=False,
        technical_checks='PASS with explicitly verified administrative, runtime-dispatch and polling exceptions',
        opaque_author_verification='PASS', glass='DEFERRED_BY_OWNER', R1='DEFERRED_BY_OWNER',
        old_R2='SUPERSEDED_BY_OWNER_COLUMN_GLOSS_DIRECTION',
        map=entry(ROOT/MAPFILE), native_assets=assets,
        recipe=entry(source/'recipe.json'), native_source_files=[entry(p) for p in sorted(source.iterdir()) if p.is_file()],
        unchanged_ceiling_spp=entry(ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp'),
        accepted_native_source_evidence=entry(OUT/'native-source-verification.json'),
        previous_manifest=entry(PREV/'manifest.json'), previous_identity=entry(PREV/'identity.json'),
        rollback=entry(CTRL/'BeforeSlabs01/archive.json'),
        coverage=dict(lobby=107,opaque=101,glass_deferred=6,support=1,stone_changed=44,
                      nonstone_preserved=63,accepted_nonstone_preserved=13,ceiling_preserved=9,proxies=0),
        module_cm=[120,240], joint_width_mm=5, joint_normal_recess_mm=.75,
        module_authority='Controller working default; not exact owner dimension approval',
        face_response=dict(roughness='Accepted ORM.G outside filtered joint coverage',specular=.4,source_coverage_cm=240),
        roles=dict(regular=39,trim_aware=5), final_state=state,
        preservation=entry(OUT/'Resume01/protected-after.json'),
        administrative_exceptions=protection['administrative_exceptions'],
        runtime_dispatch_changes=protection['runtime_dispatch_changes'],
        polling_log_changes=protection['external_controller_logs'],
        history=entry(OUT/'history-verification.json'),
        final_capture_count=16, resume_scene_operations='Read-only snapshot, state and graph audit after existing helper registration')
    write('identity', identity)
    files = {ROOT/MAPFILE, PREV/'manifest.json', PREV/'identity.json',
             ROOT/'Docs/OpeningLobbyStoneSlabs01.md', ROOT/'Docs/Tasks/OpeningLobbyStoneSlabs01.md',
             ROOT/'Docs/Approvals/LobbyMaterialsComplete01-StoneSlabs01.json',
             ROOT/'Docs/Approvals/LobbyMaterialsComplete01-GlazingDeferred01.json',
             CTRL/'slabs-controller-admin-exceptions.json', CTRL/'artist-slabs-resume01-dispatch.md',
             CTRL/'artist-slabs-before-resume01.json', CTRL/'artist-slabs-resume01-configured.json'}
    files.update(ROOT/r['path'] for r in read(PREV/'manifest.json')['entries'])
    for folder in [OUT, source, ROOT/'Content/OpeningLobby/MaterialsComplete01/SlabLayout01', CTRL/'BeforeSlabs01']:
        files.update(p for p in walk(folder) if '__pycache__' not in str(p)
                     and not p.name.endswith(('.lock','.painter_lock')))
    files.update((ROOT/'Scripts/OpeningLobby').glob('materialscomplete01_slabs*.py'))
    files.update(CTRL/'SlabsInterrupted01'/name for name in
                 ['protected-after-failed.json','prepare_slabs_review.py','usage_snapshot.py'])
    # No mutable controller polling log, current AGENTS, registry or profile is
    # included. Their exact observed values/authorities are in immutable evidence.
    files.discard(OUT/'manifest.json'); files.discard(OUT/'manifest-verification.json')
    entries = [entry(p) for p in sorted(files)]
    assert len(entries) == len({r['path'] for r in entries})
    assert all(r['bytes'] > 0 for r in entries)
    manifest = dict(candidate=identity['candidate'], identity=entry(OUT/'identity.json'),
        entries=entries, total_bytes=sum(r['bytes'] for r in entries),
        history='Earlier manifests unchanged. Historical map entries resolve through exact archives in history-verification.json. Current manifest binds SlabLayout01 map bytes.',
        preservation='Use Resume01/protected-after.json; original protected-after.json is intentionally preserved failed evidence.')
    payload = json.dumps(manifest, indent=2)
    now = usage()
    initial = read(OUT.parent/'storage-before.json')
    before = read(OUT/'storage-before.json')
    # Include serialized manifest plus a generous 1 MB verification-receipt margin.
    overhead = len(payload.encode()) + 1000000
    assert now['project_bytes'] + overhead <= 250e9
    assert now['lobby_bytes'] + overhead <= 2.4e9
    assert now['lobby_bytes'] - initial['lobby_bytes'] + overhead <= 450e6
    (OUT/'manifest.json').write_text(payload)
    for row in entries: assert entry(ROOT/row['path']) == row, row
    result = dict(passed=True, candidate=identity['candidate'], manifest=entry(OUT/'manifest.json'),
        identity=entry(OUT/'identity.json'), map=entry(ROOT/MAPFILE), entries=len(entries),
        storage_before_manifest=now,
        slab_growth_bytes=now['lobby_bytes']-before['lobby_bytes'],
        batch_growth_bytes=now['lobby_bytes']-initial['lobby_bytes'],
        manifest_and_receipt_reserved_bytes=overhead, storage_caps_pass_including_reserve=True,
        within_80mb_advisory_target=now['lobby_bytes']-before['lobby_bytes']<=80e6)
    write('manifest-verification', result)
    print(json.dumps(result))


if __name__ == '__main__': freeze()
