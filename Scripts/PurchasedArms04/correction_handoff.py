"""Preserve the initial handoff and record the new animation-package revision."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'Saved/PurchasedArms04/Worker'
OUT = WORK / 'Correction01'
ASSET = 'Content/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter.uasset'
MANIFEST = 'Assets/Source/PurchasedArms04/source-manifest.json'
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms01'))
import preserve


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    previous_path = ROOT / 'Assets/Source/PurchasedArms03/source-manifest.json'
    previous = json.loads(previous_path.read_text())['files'][0]
    backup = OUT / 'Rollback' / ASSET
    assert sha(backup) == previous['active_sha256']
    assert sha(Path(previous['source'])) == previous['source_sha256']
    write(ROOT / MANIFEST, {'task': 'MSQ-64', 'revision': 'PurchasedArms04-CompatibleJumpBase01',
        'base_manifest': previous_path.relative_to(ROOT).as_posix(), 'base_manifest_sha256': sha(previous_path),
        'scope': 'One AnimBP revision over PurchasedArms03. The existing ADS basis conversion remains intact; all other Content packages and source animation clips are unchanged.',
        'files': [{'package': previous['package'], 'destination': ASSET,
            'source': previous['source'], 'source_sha256': previous['source_sha256'],
            'previous_active_sha256': previous['active_sha256'], 'active_sha256': sha(ROOT / ASSET),
            'active_bytes': (ROOT / ASSET).stat().st_size,
            'rollback': backup.relative_to(ROOT).as_posix(),
            'change': 'Seven existing locomotion/run-end transition conditions consume the native animation-only jump-base guard through flight and landing blend-out.'}],
        'acceptance': 'Worker technical/visual correction handoff only; controller review, registry and owner acceptance remain separate.'})
    native = ['Source/MeridianSquad/OpeningLobbyCharacter.cpp', 'Source/MeridianSquad/OpeningLobbyCharacter.h',
              'Source/MeridianSquad/PurchasedArmsAnimInstance.cpp', 'Source/MeridianSquad/PurchasedArmsAnimInstance.h']
    changes, missing = [], []
    baseline = json.loads((WORK / 'preservation-before.json').read_text())
    for row in baseline:
        path = Path(row['path'])
        if not path.exists():
            missing.append(row['path'])
        elif sha(path) != row['sha256']:
            changes.append(path.relative_to(ROOT).as_posix())
    assert not missing and sorted(changes) == sorted(native + [ASSET]), (missing, changes)
    write(OUT / 'preservation-after.json', {'baseline': 'Saved/PurchasedArms04/Worker/preservation-before.json',
          'baseline_files': len(baseline), 'missing': missing, 'changed': changes})
    analysis = json.loads((OUT / 'analysis.json').read_text())
    assert analysis['passed']
    current = json.loads((WORK / 'editor-state-correction01-handoff.json').read_text())
    assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content']
    helpers = ['Scripts/PurchasedArms02/capture02.py', 'Scripts/PurchasedArms02/video_cases.py']
    scripts = sorted((ROOT / 'Scripts/PurchasedArms04').glob('*.py'))
    files = native + [ASSET, MANIFEST, 'Docs/PurchasedArms04.md'] + helpers + [p.relative_to(ROOT).as_posix() for p in scripts]
    for path in scripts + [ROOT / p for p in helpers]:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    subprocess.run(['git', 'diff', '--check', '--', *files], cwd=ROOT, check=True)
    lfs = subprocess.check_output(['git', 'check-attr', 'filter', '--', ASSET], cwd=ROOT).decode()
    assert lfs.strip().endswith(': lfs'), lfs
    (OUT / 'lfs-policy.txt').write_text(lfs)
    rows = [{'path': p, 'bytes': (ROOT / p).stat().st_size, 'sha256': sha(ROOT / p)} for p in files]
    write(OUT / 'changed-files.json', {'task': 'MSQ-64', 'revision': 'Correction01', 'files': rows,
        'changed_binaries': 1, 'map_sha256': sha(ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'),
        'initial_handoff_preserved': 'Saved/PurchasedArms04/Worker/changed-files.json',
        'worker_commit': False, 'controller_owned': 'Review, registry, issue status, acceptance and task-scoped local commit.'})
    (OUT / 'git-status-handoff.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    total = preserve.storage()
    assert total < 250_000_000_000
    write(OUT / 'storage-after.json', {'bytes': total, 'limit_bytes': 250_000_000_000})
    print(json.dumps({'files': len(rows), 'changed_binaries': 1, 'project_bytes': total,
                      'preserved_files': len(baseline) - len(changes), 'focused_correction_passed': True}))


if __name__ == '__main__':
    main()
