"""Snapshot protected project bytes without touching historical evidence."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/OpeningLobby/Layout03'

def snapshot():
    paths = []
    for folder in ['Assets/Concepts/OpeningLobby', 'Content', 'Source', 'Config',
                   'Saved/OpeningLobby/Stage1', 'Saved/OpeningLobby/Layout02',
                   'Saved/OpeningLobby/ScaleReview01']:
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and 'Layout03' not in p.relative_to(ROOT).as_posix())
    paths.extend(ROOT/p for p in ['AGENTS.md', '.codex/config.toml'])
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths))}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = OUT/'preservation-before.json'
    actual = snapshot()
    if not baseline.exists():
        baseline.write_text(json.dumps(actual, indent=2))
        print(f'Preservation baseline: {len(actual)} files')
    else:
        before = json.loads(baseline.read_text())
        changes = [p for p in before if actual.get(p) != before[p]]
        (OUT/'preservation-after.json').write_text(json.dumps(dict(files=actual, changed=changes), indent=2))
        print(dict(protected_files=len(before), changed=changes))
        assert not changes
