"""Resume-only checks; preserve original checker and failed evidence unchanged."""
import inspect
import hashlib
import json
import shutil
import sys
from pathlib import Path
import materialscomplete01_slabs_check as base
from materialscomplete01_slabs_check import ROOT, OUT, CTRL, PREV, MAPFILE, entry, read, write, differences


def baseline():
    target = OUT/'Resume01/PreResume'
    assert not target.exists()
    target.mkdir(parents=True)
    paths = [Path(base.__file__), OUT/'protected-after.json']
    receipt = []
    for p in paths:
        dest = target/p.name
        shutil.copyfile(p, dest)
        old, new = entry(p), entry(dest)
        assert (old['bytes'], old['sha256']) == (new['bytes'], new['sha256'])
        receipt.append(dict(original=old, archive=new))
    write('Resume01/pre-resume-archive', dict(entries=receipt))
    files = [ROOT/MAPFILE]
    for folder in [ROOT/'Content/OpeningLobby/MaterialsComplete01/SlabLayout01',
                   ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/SlabLayout01']:
        files.extend(base.walk(folder))
    write('Resume01/native-bytes-before', dict(entries=[entry(p) for p in files]))
    validate_scene()


def validate_scene():
    old, new = OUT/'RestoredFinal', OUT/'Resume01'
    delta = differences(read(old/'all-properties.json'), read(new/'all-properties.json'))
    write('Resume01/property-differences', delta)
    assert not delta, delta[:10]
    assert read(old/'state.json') == read(new/'state.json')
    state = read(new/'state.json')
    assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    assert entry(ROOT/MAPFILE)['sha256'] == 'c94331250d378e950ac7780c20bfee0e10145990fb28ac300b38c42477b0b62a'
    keys = ['actor','label','component','mesh','materials','overrides','visible','hidden_in_game','actor_hidden','collision']
    for folder in [old, new]:
        inventory = read(folder/'inventory.json')
        normalized = sorted([{k:r[k] for k in keys} for r in inventory], key=lambda r:(r['actor'],r['component']))
        if folder == old: expected = normalized
        else: assert normalized == expected
    write('Resume01/scene-verification', dict(passed=True, full_properties_exact=True,
          mesh_components=108, state=state, map=entry(ROOT/MAPFILE),
          bridge='Editor restarted externally; Epic discovery proved slab helper absent. One authorized Rider call registered existing helper only; all scene reads used Epic.'))
    print('Resume scene matches RestoredFinal exactly; map clean, PIE off.')


def preserved():
    archive = read(OUT/'Resume01/pre-resume-archive.json')['entries']
    for r in archive:
        assert entry(ROOT/r['archive']['path']) == r['archive']
    assert read(OUT/'Resume01/PreResume/protected-after.json') == read(CTRL/'SlabsInterrupted01/protected-after-failed.json')
    authority = CTRL/'slabs-controller-admin-exceptions.json'
    approved = read(authority)['changes']
    assert len(approved) == 2
    original = {r['path']:r for r in read(OUT/'protected-before.json')['entries']}
    for change in approved:
        assert original[change['before']['path']] == change['before']
        assert entry(ROOT/change['after']['path']) == change['after']
    # Multica injects the task's current Agent Identity into its auto-managed
    # AGENTS block at dispatch. Prove the only additional bytes are the exact
    # resume suffix explicitly configured by the controller, not a project edit.
    before_profile = read(CTRL/'artist-slabs-before-resume01.json')
    after_profile = read(CTRL/'artist-slabs-resume01-configured.json')
    old_instruction = before_profile['instructions']
    new_instruction = after_profile['instructions']
    assert new_instruction.startswith(old_instruction)
    suffix = new_instruction[len(old_instruction):]
    assert suffix == ' Resume interrupted finalization per Controller/artist-slabs-resume01-dispatch.md; do not rerun completed authoring. Exact two controller administrative file exceptions are authorized by Controller/slabs-controller-admin-exceptions.json.'
    actual_agents = (ROOT/'AGENTS.md').read_bytes()
    assert actual_agents.count(new_instruction.encode()) == 1
    reconstructed = actual_agents.replace(new_instruction.encode(), old_instruction.encode(), 1)
    assert len(reconstructed) == original['AGENTS.md']['bytes']
    assert hashlib.sha256(reconstructed).hexdigest() == original['AGENTS.md']['sha256']
    runtime_change = dict(before=original['AGENTS.md'], after=entry(ROOT/'AGENTS.md'))
    write('Resume01/runtime-dispatch-verification', dict(passed=True,
        change=runtime_change, added_instruction=suffix,
        before_profile=entry(CTRL/'artist-slabs-before-resume01.json'),
        after_profile=entry(CTRL/'artist-slabs-resume01-configured.json'),
        exact_original_reconstructed=True,
        basis='Exact controller-authorized resume instructions injected into Multica auto-managed Agent Identity. All other AGENTS bytes equal the original hash. No worker write or baseline replacement.'))
    # Reuse the existing history checker verbatim, extending only its exact
    # before/after exception branch and writing resumed preservation separately.
    source = inspect.getsource(base.preserved)
    old = '            else:errors.append(d)'
    new = """            elif d in approved:
                d['reason']='Exact before/after controller administrative exception; original baseline retained.'
                administrative.append(d)
            elif d == runtime_change:
                d['reason']='Exact authorized resume instruction suffix injected by Multica dispatch; all other AGENTS bytes verified against original hash.'
                runtime.append(d)
            else:errors.append(d)"""
    assert source.count(old) == 1
    source = source.replace(old, new)
    old = "write('protected-after',dict(passed=not errors,"
    new = "write('Resume01/protected-after',dict(runtime_dispatch_changes=runtime,administrative_exceptions=administrative,authority=entry(authority),passed=not errors,"
    assert source.count(old) == 1
    source = source.replace(old, new)
    namespace = dict(vars(base), approved=approved, administrative=[], authority=authority,
                     runtime_change=runtime_change, runtime=[])
    exec(compile(source, __file__, 'exec'), namespace)
    namespace['preserved']()
    result = read(OUT/'Resume01/protected-after.json')
    assert len(result['administrative_exceptions']) == 2


def reuse():
    for name in ['graph-audit', 'instances']:
        delta = differences(read(OUT/(name+'-final.json')), read(OUT/(name+'-Resume01.json')))
        write('Resume01/'+name+'-differences', delta)
        assert not delta, delta[:8]
    for row in read(OUT/'Resume01/native-bytes-before.json')['entries']:
        assert entry(ROOT/row['path']) == row
    captures = read(OUT/'capture-verification.json')
    assert captures['passed']
    for row in captures['images']:
        for key in ['image', 'camera']: assert entry(ROOT/row[key]['path']) == row[key]
    source = read(OUT/'native-source-verification.json')
    for row in [source['unchanged_ceiling_spp'], *source['unchanged_stone_spp'],
                source['ceiling_regeneration'], source['stone_regeneration']]:
        assert entry(ROOT/row['path']) == row
    checks = ['archive-verification', 'coverage', 'property-preservation', 'capture-verification',
              'native-source-verification', 'layout-numerics', 'graph-audit-final']
    for name in checks: assert read(OUT/(name+'.json'))['passed']
    write('Resume01/reused-verification', dict(passed=True,
        checks=[entry(OUT/(name+'.json')) for name in checks],
        current_graph_and_instances_exact=True, capture_files_exact=36,
        native_assets_and_recipe_unchanged_during_resume=True,
        basis='Current full scene equals RestoredFinal, current graph and 44 instances equal final audit after editor restart; accepted source and capture hashes verified. No production, capture, movement, Painter or glass work repeated.'))
    print('Reopened current graph/instances and existing capture/source evidence validated for reuse.')


if __name__ == '__main__':
    for operation in sys.argv[1:]: globals()[operation]()
