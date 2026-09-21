"""Freeze MSQ-98 identities without registering assets, staging files or committing."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
PLUGIN = ROOT / 'Plugins/GASPEnemyFoundation01'


def digest(path):
    before = path.stat()
    with path.open('rb') as stream:
        result = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), path
    return result


def record(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=digest(path))


def write(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)


def prepare():
    source = Path('D:/devgames/GameAnimationSample')
    before = json.loads((OUT / 'source-preservation-before01.json').read_text())
    actual_paths = [p for base in [source / 'Content', source / 'Config'] for p in base.rglob('*') if p.is_file()]
    actual_paths += list(source.glob('*.uproject'))
    after = {p.relative_to(source).as_posix(): digest(p) for p in actual_paths}
    changed = [p for p, sha in before.items() if after.get(p) != sha]
    added = sorted(set(after) - set(before))
    result = dict(source_root=source.as_posix(), original_files=len(before), final_files=len(after),
                  changed_or_missing=changed, added=added, sha256=after)
    write(OUT / 'source-preservation-after01.json', result)
    assert not changed and not added
    original = (OUT / 'DefaultEngine-before98.ini').read_bytes()
    current = (ROOT / 'Config/DefaultEngine.ini').read_bytes()
    old_project = json.loads((OUT.parent / 'Controller/MeridianSquad.owner-before.uproject').read_text(encoding='utf-8-sig'))
    new_project = json.loads((ROOT / 'MeridianSquad.uproject').read_text(encoding='utf-8-sig'))
    added_plugins = [p for p in new_project['Plugins'] if p not in old_project['Plugins']]
    new_project['Plugins'] = [p for p in new_project['Plugins'] if p not in added_plugins]
    owner = dict(engine_original_prefix_preserved=current.startswith(original),
        project_owner_semantics_preserved=new_project == old_project, added_project_plugins=added_plugins,
        retained_map=record(ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'))
    assert owner['engine_original_prefix_preserved'] and owner['project_owner_semantics_preserved']
    assert added_plugins == [{'Name': 'Mover', 'Enabled': True}]
    assert owner['retained_map']['sha256'] == 'b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f'
    write(OUT / 'owner-preservation-after01.json', owner)
    migrated = {p['derived']: p for p in json.loads((OUT / 'migration-result01.json').read_text())['assets']}
    inventory = []
    for path in sorted((PLUGIN / 'Content').rglob('*')):
        if not path.is_file():
            continue
        row = record(path)
        initial = migrated.get(row['path'])
        row['package'] = '/GASPEnemyFoundation01/' + path.relative_to(PLUGIN / 'Content').with_suffix('').as_posix()
        row['migration_provenance'] = initial
        row['changed_since_migration'] = initial is None or initial['derived_sha256'] != row['sha256']
        inventory.append(row)
    write(OUT / 'asset-inventory01.json', dict(files=inventory,
        package_count=sum(Path(p['path']).suffix == '.uasset' for p in inventory),
        bytes=sum(p['bytes'] for p in inventory), changed=[p['path'] for p in inventory if p['changed_since_migration']]))
    total = count = 0
    aliases = []
    for folder, directories, names in os.walk(ROOT, followlinks=False):
        kept = []
        for name in directories:
            path = Path(folder) / name
            if path.stat(follow_symlinks=False).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                aliases.append(path.relative_to(ROOT).as_posix())
            else:
                kept.append(name)
        directories[:] = kept
        for name in names:
            path = Path(folder) / name
            info = path.stat(follow_symlinks=False)
            if not info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                total += info.st_size
                count += 1
    capacity = dict(project_bytes=total, project_files=count, cap_bytes=250_000_000_000,
        scope='Project root including Git, generated data and local project services; junction aliases excluded from double counting.',
        excluded_reparse_points=aliases, free_bytes_on_project_drive=shutil.disk_usage(ROOT).free)
    assert total < capacity['cap_bytes']
    write(OUT / 'capacity-after01.json', capacity)
    print(json.dumps(dict(source_files=len(before), source_changes=len(changed), assets=len(inventory),
        asset_bytes=sum(p['bytes'] for p in inventory), changed_assets=[p['path'] for p in inventory if p['changed_since_migration']],
        project_bytes=total, owner_preserved=True)))


def freeze():
    candidate = OUT / 'Candidate01'
    candidate.mkdir(exist_ok=False)
    files = [p for p in (ROOT / 'Source').rglob('*') if p.is_file()]
    files += [p for p in (ROOT / 'Scripts/GASPEnemyFoundation01').rglob('*')
              if p.is_file() and '__pycache__' not in p.parts]
    files += [ROOT / p for p in ['.gitattributes', 'MeridianSquad.uproject', 'Config/DefaultEngine.ini',
        'Config/DefaultGameplayTags.ini', 'Docs/GASPEnemyFoundation01.md', 'Docs/GASPEnemyFoundation01Handoff.md',
        'Plugins/GASPEnemyFoundation01/GASPEnemyFoundation01.uplugin', 'Binaries/Win64/UnrealEditor-MeridianSquad.dll']]
    inventory = json.loads((OUT / 'asset-inventory01.json').read_text())
    files += [ROOT / row['path'] for row in inventory['files']]
    records = [record(path) for path in sorted(set(files))]
    by_path = {r['path']: r for r in records}
    assert all(by_path[r['path']]['sha256'] == r['sha256'] for r in inventory['files'])
    native = ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
    assert all(p.stat().st_mtime <= native.stat().st_mtime for p in (ROOT / 'Source').rglob('*') if p.is_file())
    # Keep the executable, source, scripts and authored assets recoverable without
    # duplicating the entire migrated animation library. Immutable hashes still
    # cover every package; the controller owns Git/LFS closure of those packages.
    snapshots = [p for p in files if not p.is_relative_to(PLUGIN / 'Content')]
    snapshots += [ROOT / r['path'] for r in inventory['files'] if r['changed_since_migration']]
    with zipfile.ZipFile(candidate / 'implementation.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(snapshots)):
            archive.write(path, path.relative_to(ROOT).as_posix())
    evidence_names = ['final-analysis02.json', 'controls-analysis02.json', 'asset-inventory01.json',
        'source-preservation-before01.json', 'source-preservation-after01.json', 'owner-preservation-after01.json',
        'capacity-after01.json', 'migration-result01.json', 'migration-plan01.json', 'source-registry-full01.json',
        'gasp-physics-before01.json', 'gasp-physics-derived01.json', 'gasp-neutral-skin01.json',
        'native-execution01.json', 'native-baseline01.json', 'build10.log', 'final-editor-state01.json', 'visual-check01.json']
    evidence = [OUT / name for name in evidence_names]
    cases = [r['name'] for r in json.loads((OUT / 'final-analysis02.json').read_text())]
    for name in cases:
        evidence += list(OUT.glob(name + '*.json'))
        evidence += list((OUT / 'Video').glob(name + '.*'))
        frame_dir = OUT / 'Video' / (name + '-Frames')
        if frame_dir.exists():
            evidence += list(frame_dir.glob('*.png'))
    manifest = dict(candidate='MSQ-98 Candidate01', frozen_utc=datetime.now(timezone.utc).isoformat(),
        engine='5.8.1-56057345+++UE5+Release-5.8', native_build='build10.log',
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        ownership='Executor freeze only; controller scope/evidence acceptance, registry and closure commit remain separate.',
        files=records, evidence=[record(p) for p in sorted(set(evidence))],
        snapshot=record(candidate / 'implementation.zip'),
        limitations=['Final01 and Final02/03 evidence use build10; Pilot evidence reuse is scoped in Docs/GASPEnemyFoundation01.md.',
            'Manifest includes exact owner-containing configuration fingerprints; snapshot stays under ignored Saved.',
            'Unchanged migrated packages are fingerprinted in place, not duplicated in implementation.zip.'])
    write(candidate / 'manifest.json', manifest)
    print(json.dumps(dict(candidate=manifest['candidate'], files=len(records), evidence=len(manifest['evidence']),
        manifest_sha256=digest(candidate / 'manifest.json'), snapshot_bytes=(candidate / 'implementation.zip').stat().st_size)))


if __name__ == '__main__':
    {'prepare': prepare, 'freeze': freeze}[sys.argv[1]]()
