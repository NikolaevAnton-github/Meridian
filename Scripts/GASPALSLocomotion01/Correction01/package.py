"""Freeze Candidate02 using the immutable Candidate01 archive plus a small delta.

No source intake, registry mutation, staging, commit or historical rewrite.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import json
import os
import shutil
import subprocess
import sys
import zipfile
from prepare import ROOT, OUT, sha

WORKER = OUT.parent
BASE = WORKER / 'Candidate01'
FINAL = WORKER / 'Candidate02'
BASE_MANIFEST = BASE / 'candidate-manifest.json'
SOURCE = ROOT / 'Assets/Source/GASPALSLocomotion01'
REVISION = SOURCE / 'revision-Candidate02.json'
REGISTRY = ROOT / 'Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate02.json'
OLD_REGISTRY = ROOT / 'Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate01.json'
REPORT = ROOT / 'Docs/GASPALSLocomotion01Correction01.md'
NATIVE = ['Source/MeridianSquad/CombatProjectileWorld.cpp', 'Source/MeridianSquad/EnemyCombatCover.cpp']
DLL = 'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
EXPECTED_BASE = '768c86198fed639105411d297a49729c6464c1c3408fec2616a58d95b248d3e4'
EXPECTED_DLL = '600731ab8e22aba32834ec33bd2b26798377b69879f1de0f70d3a0f28667f3b8'


def relative(path):
    return path.relative_to(ROOT).as_posix()


def row(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    return dict(path=relative(path), size_bytes=path.stat().st_size, sha256=sha(path))


def write_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def verify(entries):
    for entry in entries:
        actual = row(entry['path'])
        assert actual['sha256'] == entry['sha256'], entry['path']
        if 'size_bytes' in entry:
            assert actual['size_bytes'] == entry['size_bytes'], entry['path']


def base_manifest():
    assert sha(BASE_MANIFEST) == EXPECTED_BASE
    return json.loads(BASE_MANIFEST.read_text())


def project_files(root):
    # Do not follow directory junctions into another project or source tree.
    for folder, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if not
            (os.lstat(Path(folder) / name).st_file_attributes & 0x400)]
        for name in filenames:
            path = Path(folder) / name
            if not (path.lstat().st_file_attributes & 0x400):
                yield path


def prepare():
    assert not REVISION.exists() and not REGISTRY.exists()
    base = base_manifest()
    protected = json.loads((OUT / 'historical-before.json').read_text())
    verify(protected)
    verify(base['production'])
    verify(base['preserved_before'])
    initial = json.loads((OUT / 'inputs-before.json').read_text())
    verify([entry for entry in initial if entry['path'] not in NATIVE])
    assert sha(ROOT / DLL) == EXPECTED_DLL
    old_revision = SOURCE / 'revision-Candidate01.json'
    assets = json.loads(old_revision.read_text())['files']
    verify(assets)
    result = dict(
        historical_files_unchanged=len(protected),
        candidate01_production_files_unchanged=len(base['production']),
        candidate01_original_preservation_records_unchanged=len(base['preserved_before']),
        asset_revision_files_unchanged=len(assets),
        owner_inputs_unchanged=[entry['path'] for entry in initial if entry['path'] not in NATIVE],
        changed_production_sources=NATIVE,
        original_source_intake_reused=True, source_project_written=False,
        registry_mutated=False, staged_or_committed=False)
    write_new(OUT / 'preservation-check.json', result)
    revision = dict(
        task='MSQ-121', candidate='Candidate02', correction='Correction01',
        closes=['GL01-R1', 'GL01-R2'],
        status='executor correction; review closure, controller acceptance and owner Play remain separate',
        inherited_candidate=row(BASE_MANIFEST),
        intake_provenance=row(SOURCE / 'intake-manifest.json'),
        inherited_asset_revision=row(old_revision),
        all_inherited_asset_bytes_unchanged=True, assets_reimported=0,
        runtime_source_dependency=False,
        source_graph_nodes=dict(full_path_unique_non_comment_nodes=1172, added_nodes=4,
            evidence=row(ROOT / 'Saved/GASPALSLocomotion01/Review/technical-evidence.json'),
            note='Use the sole primary review count; the original Candidate01 report remains immutable.'),
        native_corrections=[row(path) for path in NATIVE], dll=row(DLL),
        report=relative(REPORT),
        final_identity_manifest=relative(FINAL / 'candidate-manifest.json'))
    write_new(REVISION, revision)
    previous = json.loads(OLD_REGISTRY.read_text())
    # Identical inherited artifact descriptors avoid silently replacing any
    # existing path identity, role or historical evidence. The new revision
    # artifact explicitly binds this candidate's native correction and evidence.
    artifacts = copy.deepcopy(previous['artifacts'])
    artifacts.append(row(REVISION) | dict(role='gaspals_locomotion_candidate02', evidence=[
        dict(source=relative(REPORT), note='Candidate02 correction of GL01-R1/GL01-R2. Unchanged intake and asset bytes; technical closure and owner Play remain separate.'),
        dict(source=relative(FINAL / 'candidate-manifest.json'), note='Complete final production and loaded native DLL identities; immutable Candidate02 evidence.')]))
    write_new(REGISTRY, dict(asset='GASPALSLocomotion01-Candidate02', artifacts=artifacts,
        dependencies=copy.deepcopy(previous['dependencies'])))
    print(json.dumps(result | dict(registry_artifacts=len(artifacts))))


def freeze():
    assert not FINAL.exists(), 'Candidate02 is immutable; use a new candidate for corrections.'
    base = base_manifest()
    assert REPORT.exists() and REVISION.exists() and REGISTRY.exists()
    assert json.loads((OUT / 'routing-02.json').read_text())['passed']
    assert json.loads((OUT / 'geometry-01.json').read_text())['passed']
    assert json.loads((WORKER / 'build-correction01-01.json').read_text())['exit_code'] == 0
    assert json.loads((OUT / 'loaded-module.json').read_text())['dll_sha256'] == EXPECTED_DLL
    assert sha(ROOT / DLL) == EXPECTED_DLL
    state = json.loads((WORKER / 'editor-state-correction01-delivery.json').read_text())
    assert not state['pie'] and not state['dirty']
    assert state['project'].replace('\\', '/').lower() == ROOT.as_posix().lower()
    assert state['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
    verify(json.loads((OUT / 'historical-before.json').read_text()))
    verify(base['production'])
    initial = json.loads((OUT / 'inputs-before.json').read_text())
    verify([entry for entry in initial if entry['path'] not in NATIVE])
    registry = json.loads(REGISTRY.read_text())
    verify(registry['artifacts'])
    scripts = [relative(p) for p in Path(__file__).parent.iterdir() if p.is_file()]
    changed = sorted(NATIVE + scripts + [relative(REPORT), relative(REVISION), relative(REGISTRY)])
    paths = sorted({entry['path'] for entry in base['production']} | set(changed))
    inventory = [row(path) for path in paths]
    native_inputs = [row(p) for p in project_files(ROOT / 'Source')]
    # Include otherwise unchanged native dependencies so the DLL identity is
    # reviewable without claiming those source files were edited by this task.
    support = [entry['path'] for entry in native_inputs if entry['path'] not in paths]
    support += ['Binaries/Win64/UnrealEditor.modules', 'Binaries/Win64/MeridianSquadEditor.target']
    FINAL.mkdir()
    archive = FINAL / 'production-delta.zip'
    delta = sorted(set(changed + support + [DLL]))
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for path in delta:
            z.write(ROOT / path, path)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(delta)
    (FINAL / 'changed-files.txt').write_text('\n'.join(changed) + '\n', encoding='utf-8')
    evidence = FINAL / 'Evidence'
    evidence.mkdir()
    selected = [p for p in OUT.iterdir() if p.is_file() and p.suffix not in ('.obj', '.exe')]
    selected += [WORKER / name for name in [
        'build-correction01-01.json', 'build-correction01-01.log',
        'editor-close-correction01-build01.json', 'editor-process-correction01-build01.json',
        'editor-state-correction01-before.json', 'editor-state-correction01-ready.json',
        'editor-state-correction01-delivery.json']]
    evidence_rows = []
    for path in selected:
        target = evidence / path.name
        assert not target.exists()
        shutil.copy2(path, target)
        evidence_rows.append(dict(path=target.relative_to(FINAL).as_posix(),
            size_bytes=target.stat().st_size, sha256=sha(target)))
    # The live editor log can continue to append. Freeze only a bounded snapshot.
    log = WORKER / 'editor-correction01-build01.log'
    log_copy = evidence / log.name
    shutil.copy2(log, log_copy)
    evidence_rows.append(dict(path=log_copy.relative_to(FINAL).as_posix(),
        size_bytes=log_copy.stat().st_size, sha256=sha(log_copy)))
    project_bytes = sum(p.stat().st_size for p in project_files(ROOT))
    assert project_bytes < 250_000_000_000
    manifest = dict(
        task='MSQ-121', candidate='Candidate02', correction='Correction01',
        frozen_utc=datetime.now(timezone.utc).isoformat(),
        baseline_head=base['baseline_head'],
        implementation_status='Both scoped corrections complete; primary finding closure/controller acceptance and owner Play remain separate.',
        no_agent_play=True, no_game_world_simulation=True, source_intake_unchanged=True,
        parent_candidate=row(BASE_MANIFEST),
        reused_base_archive=row(BASE / 'production.zip'),
        archive_composition='Immutable Candidate01 production.zip plus Candidate02 production-delta.zip. The new DLL supersedes only the archived old DLL; no asset bytes are replaced.',
        changed_files=changed, production=inventory, native_build_inputs=native_inputs,
        dll=row(DLL), build_outputs=[row(path) for path in support if path.startswith('Binaries/')],
        delta_archive=dict(path=archive.name, size_bytes=archive.stat().st_size, sha256=sha(archive)),
        delta_archive_members=delta, evidence=evidence_rows,
        reused_evidence=[row(BASE_MANIFEST), row(ROOT / 'Docs/GASPALSLocomotion01Review.md'),
            row(ROOT / 'Saved/GASPALSLocomotion01/Review/technical-evidence.json')],
        registry_input=row(REGISTRY), registry_mutated=False, staged_or_committed=False,
        editor_pid=json.loads((OUT / 'loaded-module.json').read_text())['pid'], editor_state=state,
        project_bytes_including_candidate=project_bytes, project_ceiling_bytes=250_000_000_000,
        disk_free_bytes=shutil.disk_usage(ROOT).free)
    write_new(FINAL / 'candidate-manifest.json', manifest)
    print(json.dumps(dict(candidate=relative(FINAL), manifest_sha256=sha(FINAL / 'candidate-manifest.json'),
        production_files=len(inventory), changed_files=len(changed), native_build_inputs=len(native_inputs),
        evidence_files=len(evidence_rows), archive_bytes=archive.stat().st_size, project_bytes=project_bytes)))


if __name__ == '__main__':
    {'prepare': prepare, 'freeze': freeze}[sys.argv[1]]()
