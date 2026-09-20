"""Verify unchanged owner bytes, predecessor evidence and physical disk usage."""
import difflib
import hashlib
import json
import os
import stat
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

checks = []
for row in json.loads((OUT / 'preservation-before01.json').read_text()):
    actual = digest(ROOT / row['path'])
    checks.append(dict(**row, actual=actual, match=actual == row['expected']))
previous = ROOT / 'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker/Candidate07'
changes = []
for row in json.loads((previous / 'manifest.json').read_text()):
    if not row['path'].startswith(('Source/', 'Binaries/', 'Content/')):
        continue
    path = ROOT / row['path']; actual = digest(path)
    if actual != row['sha256']:
        change = dict(path=row['path'], baseline_sha256=row['sha256'], current_sha256=actual)
        if row['path'].startswith('Source/'):
            change['diff'] = ''.join(difflib.unified_diff((previous/row['path']).read_text().splitlines(True),
                path.read_text().splitlines(True), fromfile='MSQ97-Candidate07/'+row['path'], tofile='MSQ92/'+row['path']))
        changes.append(change)
    elif row['path'].startswith('Content/') or 'DummyRecovery' in row['path']:
        checks.append(dict(path=row['path'], expected=row['sha256'], actual=actual, match=True))
manifests = [previous/'manifest.json', ROOT/'Saved/CombatSlice01/PhysicsControlLegPose01/Worker/Candidate07/manifest.json',
    ROOT/'Saved/CombatSlice01/PhysicsControlStepping01/Worker/Candidate05/manifest.json', *OUT.glob('Candidate*/manifest.json')]
frozen = [dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p),
    all_match=all(digest(p.parent/r.get('frozen_path',r['path'])) == r['sha256'] for r in json.loads(p.read_text()))) for p in manifests]
assert all(c['match'] for c in checks) and all(m['all_match'] for m in frozen)
expected = {'Source/MeridianSquad/PhysicsControlDummy.h', 'Source/MeridianSquad/PhysicsControlStepping.cpp',
    'Source/MeridianSquad/PhysicsControlBalance.cpp', 'Source/MeridianSquad/PhysicsControlBalanceProbes.cpp',
    'Binaries/Win64/UnrealEditor-MeridianSquad.dll'}
assert {c['path'] for c in changes} == expected
with (OUT/'preservation-after01.json').open('x',encoding='utf-8') as stream:
    json.dump(dict(checks=checks, frozen=frozen, changes_from_MSQ97=changes, all_match=True),stream,indent=2)
total = count = aliases = 0
for directory, dirs, files in os.walk(ROOT, followlinks=False):
    kept = []
    for name in dirs:
        if (Path(directory)/name).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            aliases += 1
        else:
            kept.append(name)
    dirs[:] = kept
    for name in files:
        path = Path(directory)/name
        if not path.is_symlink():
            try:
                total += path.stat().st_size; count += 1
            except FileNotFoundError:
                pass
assert total < 250e9
with (OUT/'storage-after01.json').open('x',encoding='utf-8') as stream:
    json.dump(dict(bytes=total,GB=total/1e9,files=count,excluded_directory_aliases=aliases,within_250GB=True),stream,indent=2)
print(json.dumps(dict(protected=len(checks), frozen=len(frozen), changed=len(changes), GB=total/1e9)))
