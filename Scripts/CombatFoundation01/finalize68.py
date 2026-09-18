"""Direct preservation verification and task-only delivery manifest; no Git writes."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms01'))
from preserve import sha, storage

def write(name, value):
    path = OUT / (name + '.json')
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')

def main():
    baseline = json.loads((OUT / 'preservation-before.json').read_text())
    changed, missing = [], []
    for row in baseline:
        path = Path(row['path'])
        if not path.exists():
            missing.append(str(path))
            continue
        current = sha(path)
        if current != row['sha256']:
            changed.append({'path': str(path.relative_to(ROOT)), 'before': row['sha256'], 'after': current})
    write('preservation-direct-final', {'checked': len(baseline), 'changed': changed, 'missing': missing})
    allowed = {'Content/InfimaGames/TacticalFPSAnimations/Weapons/AssaultRifle/Meshes/ABP_TFA_AR_Magazine.uasset',
               'Source/MeridianSquad/MeridianSquad.Build.cs',
               *('Source/MeridianSquad/' + stem + suffix for stem in ['OpeningLobbyCharacter', 'OpeningLobbyGameMode',
                                                                    'PurchasedArmsAnimInstance'] for suffix in ['.h', '.cpp'])}
    assert not missing and all(r['path'].replace('\\', '/') in allowed for r in changed), (missing, changed)
    files = [ROOT / p for p in allowed]
    files.extend((ROOT / 'Source/MeridianSquad').glob('Combat*.h'))
    files.extend((ROOT / 'Source/MeridianSquad').glob('Combat*.cpp'))
    files.extend((ROOT / 'Scripts/CombatFoundation01').glob('*.py'))
    files.append(ROOT / 'Scripts/CombatFoundation01/cases.json')
    files.append(ROOT / 'Docs/CombatFoundation01.md')
    write('changed-files-final', [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                                  for p in sorted(set(files))])
    before = json.loads((OUT / 'storage-before.json').read_text())['bytes']
    current = storage()
    write('storage-final', {'before_bytes': before, 'after_bytes': current, 'growth_bytes': current - before,
                          'limit_bytes': 250_000_000_000})
    assert current < 250_000_000_000
    (OUT / 'git-status-final.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    print(json.dumps({'checked': len(baseline), 'changed_existing': len(changed), 'task_files': len(set(files)),
                      'project_bytes': current, 'growth_bytes': current - before}))

if __name__ == '__main__':
    main()
