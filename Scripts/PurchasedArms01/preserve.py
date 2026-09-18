"""MSQ-61 immutable baseline and reversible, dependency-reviewed content pruning."""
import hashlib
import json
import os
import stat
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms01/Worker'
ARCHIVE = ROOT / 'Assets/Archive/PurchasedArms01'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def storage():
    total = 0
    for base, directories, files in os.walk(ROOT, followlinks=False):
        directories[:] = [d for d in directories if not ((Path(base) / d).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)]
        for name in files:
            p = Path(base) / name
            if not p.is_symlink():
                total += p.stat().st_size
    return total


def baseline():
    dest = OUT / 'preservation-before.json'
    assert not dest.exists(), 'Never rebaseline existing evidence'
    files = [ROOT / 'MeridianSquad.uproject']
    for folder in ['Content', 'Config', 'Source', 'Assets/Source/PlayerCharacter01']:
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file())
    files.extend(p for p in Path('D:/devgames/Weapon').rglob('*') if p.is_file())
    rows = []
    for path in sorted(set(files)):
        rows.append(dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path)))
    write(dest, rows)
    (OUT / 'git-status-before.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    (OUT / 'git-diff-before.patch').write_bytes(subprocess.check_output(['git', 'diff', '--', 'Source', 'Config', 'MeridianSquad.uproject'], cwd=ROOT))
    # Only text files will be edited. The retained map and all asset bytes stay unchanged.
    for path in [ROOT / 'MeridianSquad.uproject', *(ROOT / 'Source').rglob('*'), *(ROOT / 'Config').glob('*.ini')]:
        if path.is_file():
            backup = OUT / 'Rollback' / path.relative_to(ROOT)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
    total = storage()
    write(OUT / 'storage-before.json', dict(bytes=total, limit_bytes=250_000_000_000))
    print(json.dumps(dict(baseline_files=len(rows), project_bytes=total)))


def prune():
    plan = json.loads((OUT / 'dependency-plan.json').read_text())
    assert not plan['external_referencers'], plan['external_referencers']
    assert not (ARCHIVE / 'manifest.json').exists(), 'Archive already exists'
    baseline_rows = {x['path']: x for x in json.loads((OUT / 'preservation-before.json').read_text())}
    rows = []
    for package in plan['archive']:
        relative = Path('Content') / (package.removeprefix('/Game/') + '.uasset')
        src, dst = (ROOT / relative).resolve(), (ARCHIVE / relative).resolve()
        assert src.is_relative_to((ROOT / 'Content').resolve())
        assert dst.is_relative_to(ARCHIVE.resolve()) and not dst.exists()
        row = baseline_rows[str(src)]
        assert sha(src) == row['sha256'], src
        rows.append(dict(original=relative.as_posix(), archived=dst.relative_to(ROOT).as_posix(), bytes=row['bytes'], sha256=row['sha256']))
    # Record the complete checked plan before the first move; no recursive shell operations.
    write(OUT / 'archive-plan.json', rows)
    for row in rows:
        src, dst = ROOT / row['original'], ROOT / row['archived']
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        assert sha(dst) == row['sha256']
    write(ARCHIVE / 'manifest.json', dict(task='MSQ-61', restore='With the editor closed, move each archived file to its original path after verifying SHA-256 and absence of a conflicting file.', files=rows))
    print(json.dumps(dict(archived=len(rows), bytes=sum(r['bytes'] for r in rows))))


def verify():
    archive = json.loads((ARCHIVE / 'manifest.json').read_text())['files']
    moved = {str(ROOT / r['original']): ROOT / r['archived'] for r in archive}
    changes, missing = [], []
    for row in json.loads((OUT / 'preservation-before.json').read_text()):
        p = moved.get(row['path'], Path(row['path']))
        if not p.exists():
            missing.append(str(p))
        elif sha(p) != row['sha256']:
            changes.append(str(p.relative_to(ROOT)))
    result = dict(missing=missing, changed=changes, archived=len(archive))
    write(OUT / 'preservation-after.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    {'baseline': baseline, 'prune': prune, 'verify': verify, 'storage': lambda: print(storage())}[sys.argv[1]]()
