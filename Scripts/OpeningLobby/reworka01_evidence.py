"""Read-only provenance/storage audit and candidate-scoped evidence packaging."""
import hashlib
import json
import os
import subprocess
import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/OpeningLobby/ArchitectureReworkA01/Worker'
OUT.mkdir(parents=True, exist_ok=True)

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def walk(folder):
    for base, dirs, files in os.walk(folder, followlinks=False):
        dirs[:] = [n for n in dirs if not (getattr((Path(base)/n).lstat(), 'st_file_attributes', 0) & 0x400)]
        for n in files:
            p = Path(base)/n
            if not p.is_symlink():
                yield p

def storage():
    sizes = {}
    for p in walk(ROOT):
        key = p.relative_to(ROOT).parts[0]
        try:
            sizes[key] = sizes.get(key, 0)+p.stat().st_size
        except FileNotFoundError:
            pass
    return dict(bytes=sum(sizes.values()), by_root=sizes, method='No symlink or junction traversal', budget_bytes=250_000_000_000)

def protected():
    folders = ['Assets/Concepts', 'Assets/Source/OpeningLobby/Architecture01', 'Content/Maps',
               'Content/OpeningLobby', 'Config', 'Source', '.agents', 'Docs', 'Scripts']
    paths = set()
    for folder in folders:
        if (ROOT/folder).exists():
            paths.update(walk(ROOT/folder))
    paths.update(ROOT/p for p in ['AGENTS.md', '.gitattributes', '.codex/config.toml'])
    allowed = ['Content/OpeningLobby/ArchitectureReworkA01/', 'Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap',
               'Docs/OpeningLobbyArchitectureReworkA01.md', 'Scripts/OpeningLobby/reworka01_']
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(paths)
            if p.is_file() and not any(p.relative_to(ROOT).as_posix().startswith(a) for a in allowed)}

def preflight():
    assert not (OUT/'protected-before.json').exists(), 'Do not replace original preservation baseline.'
    package = ROOT/'Assets/Concepts/OpeningLobby/ArchitectureRework01'
    result = subprocess.run(['node', str(package/'freeze.mjs'), '--verify'], capture_output=True, text=True)
    (OUT/'freeze-verification.txt').write_text(result.stdout+result.stderr, encoding='utf-8')
    manifest = json.loads((package/'manifest.json').read_text())
    entries = [dict(path=e['path'], passed=digest(ROOT/e['path'])==e['sha256'] and (ROOT/e['path']).stat().st_size==e['bytes']) for e in manifest['entries']]
    changes = [dict(file=e['file'], frozen_sha256=e['sha256'], current_sha256=digest(ROOT/e['file']))
               for e in json.loads((package/'input-provenance.json').read_text())['inputs'] if digest(ROOT/e['file'])!=e['sha256']]
    identity = digest(package/'manifest.json')
    assert identity == 'fb0f306ff60011d01a1008345017d9029964301b2365d81d8ca5d5eba686a4df'
    assert all(e['passed'] for e in entries), entries
    report = dict(manifest_sha256=identity, entries=entries, changed_historical_inputs=changes, freeze_exit_code=result.returncode)
    (OUT/'design-provenance.json').write_text(json.dumps(report, indent=2))
    (OUT/'protected-before.json').write_text(json.dumps(protected(), indent=2))
    usage = storage()
    (OUT/'storage-before.json').write_text(json.dumps(usage, indent=2))
    assert usage['bytes'] <= usage['budget_bytes']
    print(json.dumps(dict(manifest_entries_passed=len(entries), changed_historical_inputs=changes, storage_bytes=usage['bytes'])))

def postflight():
    before=json.loads((OUT/'protected-before.json').read_text())
    changed=[name for name,old in before.items() if not (ROOT/name).is_file() or digest(ROOT/name)!=old]
    (OUT/'preservation.json').write_text(json.dumps(dict(passed=not changed,protected_files=len(before),changed=changed),indent=2))
    assert not changed,changed
    full=json.loads((OUT/'runtime-verification.json').read_text())
    partial=json.loads((OUT/'EntranceRecheck/runtime-verification.json').read_text())
    resumed=json.loads((OUT/'EntranceRecheckResume/runtime-verification.json').read_text())
    assert full['passed'] and resumed['passed']
    assert partial['step']=='mid_return_-1' and 'mid_return_-1' in partial['error']
    assert not any(r['cleanup_errors'] for r in [full,partial,resumed])
    events={e['step']:e for r in [partial,resumed] for e in r['events']}
    required=['west_terminal_crossover','east_terminal_crossover','west_adjacent_aisle','east_adjacent_aisle',
        'portal_front_-1','portal_front_1','mid_return_-1','mid_return_1','inner_reveal_-1','inner_reveal_1',
        'closed_entrance_plane','A_final_checkpoint_inbound','A_final_checkpoint_outbound','A_entrance_jump_land','A_final_entrance_return']
    assert all(n in events for n in required)
    full_events={e['step']:e for e in full['events']}
    measured_longitudinal=abs(full_events['longitudinal_end']['state']['location'][0]-full_events['longitudinal_start']['state']['location'][0])/100
    assert abs(measured_longitudinal-56)<.5
    samples=json.loads((OUT/'runtime-samples.json').read_text())
    speed=max(math.hypot(*s['velocity'][:2]) for s in samples)
    assert 359<speed<361
    runtime=dict(passed=True,full_hall=dict(report='runtime-verification.json',elapsed=full['elapsed'],samples=full['sample_count'],
        expected_longitudinal_m=56,measured_longitudinal_m=measured_longitudinal,max_horizontal_speed_cm_s=speed,
        note='Full route completed before swapping the two handed jamb meshes; hall/context remained byte-identical in scene properties.'),
        corrected_entrance=dict(initial_report='EntranceRecheck/runtime-verification.json',resume_report='EntranceRecheckResume/runtime-verification.json',
            retained_passed_events=len(partial['events']),resumed_events=len(resumed['events']),samples=partial['sample_count']+resumed['sample_count'],
            required_steps=required,contact_results={n:e['result'] for n,e in events.items() if isinstance(e['result'],dict) and 'surface_cm' in e['result']},
            resolved_setup_failure='Approach target -28.50m stopped at -28.399m due existing route tolerance, outside front corner; target moved to -28.60m with an explicit actual setup range. Continued with input only in the same PIE world.'),
        cleanup_passed=True,input_method=full['input_method'])
    (OUT/'runtime-summary.json').write_text(json.dumps(runtime,indent=2))
    current_map=ROOT/'Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap'
    map_hash=digest(current_map)
    inventory=json.loads((OUT/'capture-inventory.json').read_text())
    for record in inventory:
        path=OUT/(Path(record['filename']).stem+'-camera.json');camera=json.loads(path.read_text())
        camera['candidate_map_sha256_at_handoff']=map_hash
        camera['capture_revision']='Initial; retained unaffected inner-end context view' if record['filename']=='C1-90.png' else 'Corrected handed jamb assignment'
        path.write_text(json.dumps(camera,indent=2));record['camera']=camera
    (OUT/'capture-inventory.json').write_text(json.dumps(inventory,indent=2))
    usage=storage();initial=json.loads((OUT/'storage-before.json').read_text())
    usage['project_growth_bytes']=usage['bytes']-initial['bytes']
    dedicated=[ROOT/'Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap']
    for folder in ['Content/OpeningLobby/ArchitectureReworkA01','Assets/Source/OpeningLobby/ArchitectureReworkA01','Saved/OpeningLobby/ArchitectureReworkA01/Worker']:
        dedicated.extend(walk(ROOT/folder))
    dedicated.extend((ROOT/'Scripts/OpeningLobby').glob('reworka01_*.py'))
    usage['dedicated_output_bytes']=sum(p.stat().st_size for p in dedicated)
    (OUT/'storage-after.json').write_text(json.dumps(usage,indent=2))
    assert usage['bytes']<250_000_000_000 and usage['dedicated_output_bytes']<1_000_000_000
    print(json.dumps(dict(preservation_files=len(before),map_sha256=map_hash,storage=usage,runtime_passed=True)))

def manifest():
    from zipfile import ZipFile,ZIP_DEFLATED
    files=[ROOT/'Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap',ROOT/'Docs/OpeningLobbyArchitectureReworkA01.md']
    for folder in ['Content/OpeningLobby/ArchitectureReworkA01','Assets/Source/OpeningLobby/ArchitectureReworkA01']:
        files.extend(walk(ROOT/folder))
    files.extend((ROOT/'Scripts/OpeningLobby').glob('reworka01_*.py'))
    exclusions=['InitialBeforeProfileFix/','ScheduleAdapter/','blender-','error-','manifest','delivery-','handoff-comment']
    for p in walk(OUT):
        rel=p.relative_to(OUT).as_posix()
        if not any(rel.startswith(s) for s in exclusions) and p.suffix not in ['.zip','.log']:
            files.append(p)
    entries=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(set(files))]
    report=dict(candidate='LobbyArchitecture-ReworkA01 / WorkerCandidate01',owner_acceptance='pending',
        scope='Neutral representative entrance/terminal bays in accepted complete hall context',entries=entries,
        exclusions='Initial pre-profile-fix capture archive, temporary adapter files, process/error logs, manifest itself and delivery ZIP/receipt')
    path=OUT/'manifest.json';path.write_text(json.dumps(report,indent=2))
    identity=digest(path);(OUT/'manifest.sha256').write_text(identity+'  manifest.json\n')
    archive=OUT/'ReworkA01-WorkerCandidate01.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(set(files)):
            z.write(p,p.relative_to(ROOT).as_posix())
        z.write(path,path.relative_to(ROOT).as_posix())
        z.write(OUT/'manifest.sha256',(OUT/'manifest.sha256').relative_to(ROOT).as_posix())
    with ZipFile(archive) as z:assert z.testzip() is None
    delivery=dict(manifest_sha256=identity,entries=len(entries),artifact_bytes=sum(e['bytes'] for e in entries),zip_bytes=archive.stat().st_size,zip_sha256=digest(archive),
        zip='Saved/OpeningLobby/ArchitectureReworkA01/Worker/ReworkA01-WorkerCandidate01.zip',
        map='Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap',map_sha256=digest(ROOT/'Content/Maps/L_OpeningLobby_ArchitectureReworkA01.umap'),
        owner_acceptance='pending',technical_result='passed; independent visual review pending')
    (OUT/'delivery-package.json').write_text(json.dumps(delivery,indent=2))
    print(json.dumps(delivery))

if __name__ == '__main__':
    if '--postflight' in sys.argv:postflight()
    elif '--manifest' in sys.argv:manifest()
    else:preflight()
