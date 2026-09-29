"""MSQ-171 immutable preservation and bounded rollback evidence."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyRollback01'
BASE = 'fd84f4a'
MAP = 'Content/Maps/L_OpeningLobby_PainterStone01.umap'
CUSTOM = ['Content/Experiments/DemoTiledColumn01', 'Content/ReinforcedColumn01',
          'Content/OpeningLobby/LobbyColumns01', 'Content/OpeningLobby/DestructionScaling01']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(name, data):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def snapshot():
    before = OUT / 'Before'
    assert not (before / 'manifest.json').exists()
    before.mkdir(parents=True, exist_ok=True)
    status = git('status', '--porcelain=v1', '-z')
    (before / 'git-status.z').write_bytes(status)
    (before / 'git-diff.patch').write_bytes(git('diff', '--binary'))
    (before / 'git-index.patch').write_bytes(git('diff', '--cached', '--binary'))
    (before / 'baseline-code.patch').write_bytes(git('diff', BASE, '--', 'Source/MeridianSquad'))
    (before / 'baseline-files.txt').write_bytes(git('diff', '--name-status', BASE))
    paths = {MAP, 'MeridianSquad.uproject', 'AGENTS.md', 'Docs/ProjectState.md'}
    for entry in status.decode('utf-8').split('\0'):
        if entry and not entry[3:].startswith('.multica/'):
            p = ROOT / entry[3:]
            if p.is_file():
                paths.add(entry[3:])
    for folder in ['Source/MeridianSquad', 'Config', *CUSTOM]:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob('*') if p.is_file())
    manifest = {}
    total = sum((ROOT / p).stat().st_size for p in paths)
    assert total < 5 * 1024 ** 3, 'Bound snapshot size before copying.'
    for relative in sorted(paths):
        source = ROOT / relative
        target = before / 'Files' / relative
        assert not target.exists(), target
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        digest = sha(source)
        assert sha(target) == digest
        manifest[relative] = {'sha256': digest, 'bytes': source.stat().st_size}
    write('Before/manifest.json', {'head': git('rev-parse', 'HEAD').decode().strip(),
          'base': BASE, 'files': manifest, 'total_bytes': total})
    vendor = {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / 'Content/NextGenDestruction').rglob('*') if p.is_file()}
    write('Before/vendor-hashes.json', vendor)
    print(json.dumps({'snapshot_files': len(manifest), 'bytes': total, 'vendor_files': len(vendor)}))


def native():
    config_path = ROOT / 'Saved/ContextBudget02/runs/01a0ecec-0f59-74d7-9281-d665c4703936/native-config.json'
    config = json.loads(config_path.read_text())
    sessions = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-171-d665c4703936/codex-home/sessions'
    contexts = []
    for path in sessions.rglob('*.jsonl'):
        for line in path.open(encoding='utf-8'):
            if '"turn_context"' not in line[:150]:
                continue
            row = json.loads(line)
            if row.get('type') == 'turn_context':
                contexts.append({k: row['payload'].get(k) for k in ['model', 'effort', 'service_tier', 'cwd']})
    raw = subprocess.check_output(['powershell', '-NoProfile', '-Command',
        "Get-CimInstance Win32_Process -Filter \"Name = 'codex.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json"], text=True)
    processes = json.loads(raw)
    if isinstance(processes, dict):
        processes = [processes]
    launch = []
    for row in processes:
        command = (row['CommandLine'] or '').replace('\\', '').replace('"', '')
        if 'model_reasoning_effort' not in command:
            continue
        fields = {k: (re.search(k + r'=([^ ]+)', command).group(1) if re.search(k + r'=([^ ]+)', command) else None)
                  for k in ['model', 'model_reasoning_effort', 'service_tier']}
        launch.append(dict(pid=row['ProcessId'], **fields, fast_disabled='--disable fast_mode' in command))
    assert config['model_reasoning_effort'] == 'max' and config['service_tier'] == 'default'
    assert contexts and all(c['model'] == 'gpt-6-astra' and c['effort'] == 'max' for c in contexts)
    assert any(p['model'] == 'gpt-6-astra' and p['model_reasoning_effort'] == 'max'
               and p['service_tier'] == 'default' and p['fast_disabled'] for p in launch)
    write('native-settings.json', {'config_sha256': sha(config_path),
          'configured': {k: config.get(k) for k in ['role', 'model_reasoning_effort', 'service_tier']},
          'actual_contexts': contexts, 'native_arguments': launch})
    print(json.dumps({'configured': 'Astra/max/default', 'actual_contexts': contexts, 'native_arguments': launch}))


def baseline():
    pointer = git('show', BASE + ':' + MAP)
    if pointer.startswith(b'version https://git-lfs'):
        digest = re.search(rb'oid sha256:([a-f0-9]+)', pointer).group(1).decode()
        path = ROOT / '.git/lfs/objects' / digest[:2] / digest[2:4] / digest
        assert path.is_file(), 'Historical LFS map must be available locally.'
        data = path.read_bytes()
    else:
        data = pointer
    assert hashlib.sha256(data).hexdigest() == '94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57'
    path = OUT / 'Baseline/L_OpeningLobby_PainterStone01.umap'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(data)
    print(json.dumps({'baseline_map_sha256': sha(path), 'bytes': len(data)}))


def compare_scene():
    base = json.loads((ROOT / 'Saved/LobbyPlaytestFix01/Candidate01/editor-reopened.json').read_text())
    current = json.loads((OUT / 'Before/editor-live.json').read_text())
    before = {a['name']: a for a in base['actors']}
    now = {a['name']: a for a in current['actors']}
    missing = [before[k] for k in before.keys() - now.keys()]
    added = [now[k] for k in now.keys() - before.keys()]
    changed = [dict(name=k, label=before[k]['label'], differences={f: [before[k][f], now[k].get(f)]
                   for f in before[k] if before[k][f] != now[k].get(f)})
               for k in before.keys() & now.keys() if before[k] != now[k]]
    write('actor-scope-audit.json', dict(baseline=str(ROOT / 'Saved/LobbyPlaytestFix01/Candidate01/editor-reopened.json'),
          baseline_sha256=sha(ROOT / 'Saved/LobbyPlaytestFix01/Candidate01/editor-reopened.json'),
          before_count=len(before), current_count=len(now), missing=missing, added=added, changed=changed))
    print(json.dumps(dict(before_count=len(before), current_count=len(now),
          missing=[r['label'] for r in missing], added=[r['label'] for r in added],
          changed=[dict(label=r['label'], fields=list(r['differences'])) for r in changed])))


def config_scope():
    changed = git('diff', BASE, '--', 'Config/DefaultEngine.ini').decode()
    rows = []
    for line in changed.splitlines():
        if not line.startswith(('+', '-')) or line.startswith(('+++', '---')):
            continue
        key, sep, val = line[1:].partition('=')
        rows.append(line[0] + key + ('=' + (val if re.fullmatch(r'[\d.\-]+|True|False', val) else '<redacted>') if sep else ''))
    print('\n'.join(rows))
    print(git('log', '--oneline', BASE + '..HEAD', '--', 'Source/MeridianSquad').decode())


def compare_t3d(canonical=False):
    import difflib
    def parse(path):
        data = path.read_text(encoding='utf-8-sig')
        data = re.sub(r'/Game/Maps/(L_OpeningLobby_PainterStone01|L_RollbackBaseline01)\.[^:\'"\s]+', '__LOBBY__', data)
        rows = {}
        for text in re.findall(r'^      Begin Actor .*?^      End Actor\s*$', data, re.M | re.S):
            name = re.search(r' Name=([^ ]+)', text).group(1)
            if canonical:
                stack = []
                properties = []
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith('Begin Object'):
                        match = re.search(r'Name=("[^"]+"|[^ ]+)', line)
                        stack.append(match.group(1))
                        properties.append('/'.join(stack) + ':' + line)
                    elif line == 'End Object':
                        stack.pop()
                    else:
                        properties.append('/'.join(stack) + ':' + line)
                rows[name] = '\n'.join(sorted(properties))
            else:
                rows[name] = text.rstrip()
        return rows
    before = parse(OUT / 'Baseline/editor-loaded.t3d')
    now = parse(OUT / 'Before/editor-full.t3d')
    data = json.loads((OUT / 'Baseline/editor-loaded.json').read_text())
    labels = {a['name']: a['label'] for a in data['actors']}
    current = json.loads((OUT / 'Before/editor-full.json').read_text())
    nowlabels = {a['name']: a['label'] for a in current['actors']}
    changed = sorted(k for k in before.keys() & now.keys() if before[k] != now[k])
    missing = sorted(before.keys() - now.keys())
    added = sorted(now.keys() - before.keys())
    exact = sorted(k for k in before.keys() & now.keys() if before[k] == now[k])
    lines = []
    for k in changed:
        lines.extend(difflib.unified_diff(before[k].splitlines(True), now[k].splitlines(True),
                     fromfile=labels.get(k, k) + ':baseline', tofile=nowlabels.get(k, k) + ':current'))
    suffix = '-canonical' if canonical else ''
    with (OUT / ('scene-properties' + suffix + '.diff')).open('x', encoding='utf-8') as f:
        f.writelines(lines)
    report = dict(method='Full actor T3D property comparison; map package identity normalized. Canonical mode sorts declarations/properties by object path without removing properties.',
                  canonical=canonical,
                  exact_count=len(exact), exact=exact, changed={k: labels.get(k, k) for k in changed},
                  removed={k: labels.get(k, k) for k in missing}, added={k: nowlabels.get(k, k) for k in added})
    write('scene-property-audit' + suffix + '.json', report)
    print(json.dumps({k:v for k,v in report.items() if k != 'exact'}))


def storage():
    import os
    pending = [str(ROOT)]
    size = count = 0
    skipped = []
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                if entry.is_symlink() or entry.is_junction():
                    skipped.append(entry.path)
                elif entry.is_dir(follow_symlinks=False):
                    pending.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    try:
                        size += entry.stat(follow_symlinks=False).st_size
                        count += 1
                    except FileNotFoundError:
                        pass
    write('storage.json', {'bytes': size, 'files': count, 'skipped_links': skipped,
                          'method': 'scandir without following junctions/symlinks'})
    assert size < 250 * 1000 ** 3
    print(json.dumps({'project_gb': round(size / 1e9, 2), 'files': count, 'skipped_links': len(skipped)}))


def restore():
    manifest = json.loads((OUT / 'Before/manifest.json').read_text())['files']
    scope = json.loads((OUT / 'scene-property-audit-canonical.json').read_text())
    assert scope['exact_count'] == 133
    assert set(scope['changed'].values()) == {'Floor', 'FloorStrip_-1', 'FloorStrip_1',
        'FB01_newNcolumnNN12p6NN2p4', 'FB01_newNcolumnNN12p6N2p4',
        'FB01_newNcolumnN12p6NN2p4', 'FB01_newNcolumnN12p6N2p4'}
    assert len(scope['removed']) == 12 and len(scope['added']) == 18
    # The extra non-column actor is engine-created and declared Transient.
    header = Path('D:/UE_5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayDebug/Public/MassDebugVisualizer.h')
    assert 'UCLASS(MinimalAPI, NotPlaceable, Transient)' in header.read_text()
    references = json.loads((OUT / 'Before/custom-referencers.json').read_text())
    assert {x for values in references['external_referencers'].values() for x in values} == {'/Game/Maps/L_OpeningLobby_PainterStone01'}
    added = git('diff', '--diff-filter=A', '--name-only', BASE, '--', 'Source/MeridianSquad').decode().splitlines()
    modified = git('diff', '--diff-filter=M', '--name-only', BASE, '--', 'Source/MeridianSquad').decode().splitlines()
    assert len(added) == 14
    assert set(modified) == {'Source/MeridianSquad/CombatProjectileWorld.cpp',
        'Source/MeridianSquad/CombatProjectileWorld.h', 'Source/MeridianSquad/NGDPropComponent.cpp',
        'Source/MeridianSquad/MeridianSquad.Build.cs'}
    assets = [p.relative_to(ROOT).as_posix() for folder in CUSTOM for p in (ROOT / folder).rglob('*') if p.is_file()]
    assert len(assets) == 801
    mutations = [*added, *modified, *assets, MAP, 'Config/DefaultEngine.ini']
    for relative in mutations:
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT.resolve()), path
        assert sha(path) == manifest[relative]['sha256'], 'Concurrent edit: ' + relative
        assert sha(OUT / 'Before/Files' / relative) == manifest[relative]['sha256']
    changes = {}
    for relative in modified:
        data = git('show', BASE + ':' + relative)
        (ROOT / relative).write_bytes(data)
        changes[relative] = {'action': 'restore audited custom-only diff to baseline', 'sha256': sha(ROOT / relative)}
    for relative in added + assets:
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT.resolve())
        path.unlink()
        changes[relative] = {'action': 'archive outside active source/content', 'archive': 'Before/Files/' + relative,
                             'sha256': manifest[relative]['sha256']}
    shutil.copy2(OUT / 'Baseline/L_OpeningLobby_PainterStone01.umap', ROOT / MAP)
    changes[MAP] = {'action': 'restore exact baseline map after full property audit', 'sha256': sha(ROOT / MAP)}
    config = ROOT / 'Config/DefaultEngine.ini'
    data = config.read_bytes()
    lines = data.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.startswith(b'+Profiles=(Name="MSQDestructionDebris"')]
    assert len(matches) == 1
    index = matches[0]
    assert lines[index - 1].strip() == b'[/Script/Engine.CollisionProfile]'
    assert not lines[index - 2].strip()
    del lines[index - 2:index + 1]
    config.write_bytes(b''.join(lines))
    changes['Config/DefaultEngine.ini'] = {'action': 'remove only appended MSQDestructionDebris profile section', 'sha256': sha(config)}
    temporary = (ROOT / 'Content/Maps/L_RollbackBaseline01.umap').resolve()
    assert temporary.parent == (ROOT / 'Content/Maps').resolve()
    assert sha(temporary) == sha(ROOT / MAP)
    temporary.unlink()
    write('rollback-manifest.json', {'baseline': BASE, 'changes': changes,
          'transient_exception_source': str(header), 'transient_exception_source_sha256': sha(header),
          'superseded_evidence': {'Baseline/editor.json': 'Captured original map after Epic load precheck failed; valid historical export is Baseline/editor-loaded.json.',
                                  'actor-scope-audit.json': 'Initial raw strings include process addresses; full canonical property audit is authoritative.'}})
    assert not git('diff', BASE, '--', 'Source/MeridianSquad')
    print(json.dumps({'restored_code': len(modified), 'archived_code': len(added), 'archived_assets': len(assets),
          'map_sha256': sha(ROOT / MAP), 'remaining_code_diff_from_baseline': False}))


if __name__ == '__main__':
    import sys
    {'snapshot': snapshot, 'native': native, 'baseline': baseline,
     'compare_scene': compare_scene, 'config_scope': config_scope,
     'compare_t3d': compare_t3d, 'compare_canonical': lambda: compare_t3d(True),
     'storage': storage, 'restore': restore}[sys.argv[1]]()
