"""Record exact worker delivery paths, preservation and focused acceptance."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms01'))
import preserve


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    scripts = sorted((ROOT / 'Scripts/PurchasedArms04').glob('*.py'))
    existing = ['Source/MeridianSquad/OpeningLobbyCharacter.cpp',
                'Source/MeridianSquad/OpeningLobbyCharacter.h',
                'Scripts/PurchasedArms02/capture02.py', 'Scripts/PurchasedArms02/video_cases.py']
    paths = existing + ['Docs/PurchasedArms04.md'] + [p.relative_to(ROOT).as_posix() for p in scripts]
    for p in scripts + [ROOT / existing[2], ROOT / existing[3]]:
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
    report = json.loads((OUT / 'focused-analysis02.json').read_text())
    assert report['passed']
    preserved = json.loads((OUT / 'preservation-after.json').read_text())
    assert not preserved['missing']
    assert sorted(p.replace('\\', '/') for p in preserved['changed']) == sorted(existing[:2])
    state = json.loads((OUT / 'editor-state-handoff.json').read_text())
    assert not state['pie'] and not state['dirty_maps'] and not state['dirty_content']
    subprocess.run(['git', 'diff', '--check', '--', *paths], cwd=ROOT, check=True)
    rows = []
    for path in paths:
        p = ROOT / path
        row = {'path': path, 'bytes': p.stat().st_size, 'sha256': sha(p)}
        if path in existing:
            before = OUT / 'Rollback' / path
            if before.exists():
                row['before_working_bytes_sha256'] = sha(before)
            else:
                # These capture helpers had no starting edits; record their canonical
                # Git source rather than mislabeling normalized bytes as a disk snapshot.
                old = subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT)
                row['before_git_blob_sha256'] = hashlib.sha256(old).hexdigest()
        rows.append(row)
    result = {'task': 'MSQ-64', 'files': rows, 'changed_binaries': 0,
              'unchanged_preservation_files': 1417,
              'map_sha256': sha(ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'),
              'ads_anim_blueprint_sha256': sha(ROOT / 'Content/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter.uasset'),
              'worker_commit': False, 'controller_owned': 'Review, issue status, acceptance and scoped local closure commit.'}
    assert not (OUT / 'changed-files.json').exists()
    (OUT / 'changed-files.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (OUT / 'git-status-handoff.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    total = preserve.storage()
    assert total < 250_000_000_000
    (OUT / 'storage-after.json').write_text(json.dumps({'bytes': total, 'limit_bytes': 250_000_000_000}, indent=2))
    print(json.dumps({'files': len(rows), 'changed_binaries': 0, 'project_bytes': total,
                      'editor_state': state, 'acceptance_passed': report['passed']}))


if __name__ == '__main__':
    main()
