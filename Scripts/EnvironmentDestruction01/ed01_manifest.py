"""Immutable final identities for controller review; never stages or commits files."""
import hashlib
import json
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/EnvironmentDestruction01/ED-01/MSQ-141-Candidate01'

def fingerprint(path):
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return {'bytes': path.stat().st_size, 'sha256': digest}

def main():
    checks = json.loads((OUT / 'verification-summary.json').read_text())
    assert all(v['passed'] for v in checks['runtime'].values())
    audit = json.loads((OUT / 'scene-final-audit.json').read_text())
    assert audit['editor']['dirty'] == [] and not audit['editor']['pie']
    assert audit['editor']['background_cpu_throttle'] and audit['editor']['gpu_csv_enabled'] == 0
    restored = json.loads((OUT / 'editor-state-after-readable.json').read_text())
    assert restored['dirty'] == [] and not restored['pie'] and not restored['python_remote_execution']
    assert restored['background_cpu_throttle'] and restored['gpu_csv_enabled'] == 0
    assert json.loads((OUT / 'readable-verification.json').read_text())['passed']
    previous = json.loads((OUT / 'candidate-manifest.json').read_text())
    revised_handoff_files = {'Docs/EnvironmentDestruction01ED01.md',
                            'Scripts/EnvironmentDestruction01/ed01_runtime.py',
                            'Scripts/EnvironmentDestruction01/ed01_manifest.py'}
    assert all(fingerprint(ROOT / p) == value for p, value in previous['task_files'].items() if p not in revised_handoff_files)
    assert fingerprint(ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll') == previous['native_dll']
    preserved = json.loads((OUT / 'preservation-before.json').read_text())
    assert all(fingerprint(ROOT / p)['sha256'] == digest for p, digest in preserved.items())
    owned = [ROOT / 'Content/Maps/L_OpeningLobby_DestructionLab01.umap',
             ROOT / 'Source/MeridianSquad/DestructibleCladding.h',
             ROOT / 'Source/MeridianSquad/DestructibleCladding.cpp',
             ROOT / 'Docs/EnvironmentDestruction01ED01.md']
    owned += sorted((ROOT / 'Scripts/EnvironmentDestruction01').glob('ed01_*.py'))
    owned += sorted((ROOT / 'Assets/Source/EnvironmentDestruction01').rglob('*.json'))
    owned += sorted((ROOT / 'Content/Development/EnvironmentDestruction01').rglob('*.uasset'))
    files = {str(p.relative_to(ROOT)).replace('\\', '/'): fingerprint(p) for p in owned}
    active_assets = json.loads((OUT / 'assets-authored04.json').read_text())['assets']
    active_assets.append('/Game/Development/EnvironmentDestruction01/MSQ141Candidate01/M_ED01_Backing')
    evidence = {}
    for name in ['source-before.json', 'geometry-api.json', 'geometry-validation-04.json', 'build-06.log', 'build-06.json',
                 'normal05-complete.json', 'slow04-complete.json', 'cost01-complete.json',
                 'normal05.csv', 'slow04.csv', 'cost01.csv', 'verification-summary.json',
                 'scene-final-audit.json', 'preservation-before.json', 'preservation-after-final.json',
                 'worker-settings.json', 'hardware.json', 'runtime-final-editor.log', 'footprint.json',
                 'candidate-manifest.json', 'handoff-before-readable-capture.md',
                 'runtime-script-before-readable-capture.py', 'manifest-script-before-readable-capture.py',
                 'readable03-complete.json', 'readable03.csv', 'readable03-foreground.json',
                 'readable-verification.json', 'verify-readable.py', 'editor-state-after-readable.json',
                 'preservation-after-delivery.json', 'runtime-readable-editor.log']:
        evidence[name] = fingerprint(OUT / name)
    for prefix in ('normal05-', 'slow04-', 'readable03-'):
        for path in sorted(OUT.glob(prefix + '*.png')):
            value = fingerprint(path)
            with path.open('rb') as f:
                value['width'], value['height'] = struct.unpack('>II', f.read(24)[16:24])
            evidence[path.name] = value
    recipe = json.loads((ROOT / 'Assets/Source/EnvironmentDestruction01/MSQ-141-Candidate01/cladding-recipe.json').read_text())
    result = {'candidate': 'MSQ-141-Candidate01', 'created_utc': datetime.now(timezone.utc).isoformat(),
              'manifest_revision': 2,
              'supplement': 'Adds readable03 diagnostic-exposure captures and current handoff/tooling. Production map, assets, C++ and DLL are unchanged from immutable manifest 01.',
              'review_waiver': {'path': 'Docs/Approvals/EnvironmentDestruction01-ED01ReviewWaiver01.json',
                               **fingerprint(ROOT / 'Docs/Approvals/EnvironmentDestruction01-ED01ReviewWaiver01.json')},
              'base_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'worker_committed': False, 'active_asset_packages': active_assets,
              'note': 'Unused earlier derived asset iterations are retained. Only active_asset_packages are referenced by the final specimen.',
              'task_files': files, 'native_dll': fingerprint(ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll'),
              'evidence': evidence, 'protected_files_verified': len(preserved),
              'piece_mass_kg': {'minimum': min(p['mass_kg'] for p in recipe['pieces']), 'maximum': max(p['mass_kg'] for p in recipe['pieces']),
                                'total': sum(p['mass_kg'] for p in recipe['pieces'])},
              'native_actor_count': len(audit['actors'])}
    with (OUT / 'candidate-manifest02.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps({'map': files['Content/Maps/L_OpeningLobby_DestructionLab01.umap'],
                      'active_assets': len(active_assets), 'piece_mass_kg': result['piece_mass_kg'],
                      'task_files': len(files), 'manifest': fingerprint(OUT / 'candidate-manifest02.json')}))

if __name__ == '__main__':
    main()
