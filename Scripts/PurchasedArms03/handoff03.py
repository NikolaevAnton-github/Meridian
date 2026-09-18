"""Record the new binary revision without changing historical source manifests."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms03/Worker'
ASSET = 'Content/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter.uasset'
MANIFEST = 'Assets/Source/PurchasedArms03/source-manifest.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def manifest():
    previous_path = ROOT / 'Assets/Source/PurchasedArms02/source-manifest.json'
    previous = json.loads(previous_path.read_text())
    row = next(r for r in previous['files'] if r['destination'] == ASSET)
    backup = OUT / 'Rollback' / ASSET
    assert sha(backup) == row['active_sha256']
    assert sha(Path(row['source'])) == row['sha256']
    target = ROOT / MANIFEST
    assert not target.exists(), 'Never replace a revision manifest.'
    target.parent.mkdir(parents=True, exist_ok=True)
    value = {'task': 'MSQ-63', 'revision': 'PurchasedArms03-ADSComponentSpace01',
        'base_manifest': previous_path.relative_to(ROOT).as_posix(), 'base_manifest_sha256': sha(previous_path),
        'scope': 'One active-package override of the 400-package PurchasedArms02 baseline; all other package hashes remain unchanged.',
        'files': [{'package': row['package'], 'destination': ASSET,
                   'source': row['source'], 'source_sha256': row['sha256'],
                   'previous_active_sha256': row['active_sha256'],
                   'active_sha256': sha(ROOT / ASSET), 'active_bytes': (ROOT / ASSET).stat().st_size,
                   'rollback': backup.relative_to(ROOT).as_posix(),
                   'change': 'ADS translation uses component space after a +90-degree yaw basis conversion; source rotation, spring, recoil and IK are unchanged.'}],
        'acceptance': 'Technical worker handoff only; controller registration/review and owner acceptance remain separate.'}
    for old in previous['files']:
        if old['destination'] != ASSET:
            assert sha(ROOT / old['destination']) == old['active_sha256'], old['destination']
    target.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(value))


def inventory():
    scripts = sorted((ROOT / 'Scripts/PurchasedArms03').glob('*.py'))
    for path in scripts:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    files = [ASSET, MANIFEST, 'Docs/PurchasedArms03.md',
             *[p.relative_to(ROOT).as_posix() for p in scripts]]
    rows = [{'path': p, 'bytes': (ROOT / p).stat().st_size, 'sha256': sha(ROOT / p)} for p in files]
    preservation = json.loads((OUT / 'preservation-after.json').read_text())
    assert not preservation['missing']
    assert [p.replace('\\', '/') for p in preservation['changed']] == [ASSET], preservation
    lfs = subprocess.check_output(['git', 'check-attr', 'filter', '--', ASSET], cwd=ROOT).decode()
    assert lfs.strip().endswith(': lfs'), lfs
    (OUT / 'lfs-policy.txt').write_text(lfs)
    subprocess.run(['git', 'diff', '--check', '--', 'Scripts/PurchasedArms03', 'Docs/PurchasedArms03.md', MANIFEST],
                   cwd=ROOT, check=True)
    value = {'task': 'MSQ-63', 'files': rows, 'changed_binaries': 1,
             'unchanged_baseline_files': len(json.loads((OUT / 'preservation-before.json').read_text())) - 1,
             'map_sha256': sha(ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'),
             'worker_commit': False, 'controller_owned': 'Registry, review, task status and scoped closure commit.'}
    (OUT / 'changed-files.json').write_text(json.dumps(value, indent=2))
    (OUT / 'git-status-handoff.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    import sys
    {'manifest': manifest, 'inventory': inventory}[sys.argv[1]]()
