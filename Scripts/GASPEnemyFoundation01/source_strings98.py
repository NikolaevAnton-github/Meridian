"""Conservative serialized-reference preflight, pending Unreal registry verification."""
import collections
import hashlib
import json
from pathlib import Path
import re

SOURCE = Path('D:/devgames/GameAnimationSample')
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
SEED = '/Game/Blueprints/SandboxCharacter_Mover_Ragdoll'
PATTERN = re.compile(rb'/(?:Game|Script|Engine|[A-Z][A-Za-z]+)/(?:[A-Za-z0-9_./]+)')


def main():
    queue = collections.deque([SEED])
    seen = set()
    records = []
    scripts = set()
    missing = set()
    strings = {}
    while queue:
        package = queue.popleft().split('.')[0]
        if package in seen:
            continue
        seen.add(package)
        path = SOURCE / 'Content' / (package.removeprefix('/Game/') + '.uasset')
        if not path.is_file():
            missing.add(package)
            continue
        data = path.read_bytes()
        refs = sorted({r.decode().rstrip('.') for r in PATTERN.findall(data)})
        scripts.update(r for r in refs if r.startswith('/Script/'))
        queue.extend(r.split('.')[0] for r in refs if r.startswith('/Game/'))
        records.append(dict(package=package, path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), refs=refs))
        if package.startswith('/Game/Blueprints/') and ('SandboxCharacter_Mover' in package or 'Ragdoll' in package):
            strings[package] = [r.decode(errors='replace') for r in re.findall(rb'[ -~]{4,}', data)]
    result = dict(method='Serialized path strings: conservative planning estimate, NOT verified migration closure',
        seed=SEED, count=len(records), bytes=sum(r['bytes'] for r in records), missing=sorted(missing), scripts=sorted(scripts), assets=records)
    with (OUT / 'source-serialized-refs01.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    with (OUT / 'source-blueprint-strings01.json').open('x', encoding='utf-8') as stream:
        json.dump(strings, stream, indent=2)
    print(json.dumps({k: result[k] for k in ['method','count','bytes','missing','scripts']}))


if __name__ == '__main__':
    main()
