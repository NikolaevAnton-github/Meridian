"""Bounded preservation and storage record for MSQ-84; no source deletion."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlDummy01/Worker'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'preservation-before.json'
    if dest.exists():
        raise RuntimeError('The initial preservation record is immutable')
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    rows = []
    for relative in paths:
        path = ROOT / relative
        if path.is_file() and (relative.startswith(('Config/', 'Content/', 'Assets/Source/EnemyPrototype01/', 'Source/')) or relative in ('MeridianSquad.uproject', '.codex/config.toml')):
            rows.append(dict(path=relative, bytes=path.stat().st_size, sha256=sha(path)))
    dest.write_text(json.dumps(rows, indent=2), encoding='utf-8')
    total = sum(p.stat().st_size for parent, dirs, files in os.walk(ROOT) for name in files if (p := Path(parent) / name).is_file())
    (OUT / 'storage-before.json').write_text(json.dumps(dict(bytes=total, limit_bytes=250000000000)), encoding='utf-8')
    (OUT / 'git-status-before.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    (OUT / 'MeridianSquad.uproject.before').write_bytes((ROOT / 'MeridianSquad.uproject').read_bytes())
    print(json.dumps(dict(files=len(rows), project_bytes=total)))

if __name__ == '__main__':
    run()
