"""MSQ-82 uses the existing preservation inventory; never overwrites MSQ-68 evidence."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatTiming01/Worker'
spec = importlib.util.spec_from_file_location('preservation61', ROOT / 'Scripts/PurchasedArms01/preserve.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
previous.OUT = OUT

if __name__ == '__main__':
    operation = sys.argv[1]
    if operation == 'baseline':
        previous.baseline()
        for folder in ['Scripts/CombatFoundation01']:
            for source in (ROOT / folder).glob('*.py'):
                target = OUT / 'Rollback' / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                assert not target.exists()
                shutil.copy2(source, target)
        for name in ['Content/Maps/L_OpeningLobby_PainterStone01.umap',
                     'Content/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter.uasset']:
            target = OUT / 'Rollback' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            assert not target.exists()
            shutil.copy2(ROOT / name, target)
    elif operation == 'native':
        profile = json.loads((OUT.parent / 'Controller/profile-before.json').read_text(encoding='utf-8-sig'))
        safe = {k: profile.get(k) for k in ['id', 'model', 'thinking_level', 'service_tier', 'custom_args', 'max_concurrent_tasks']}
        contexts = []
        session_root = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-82-8ed19fa960d1/codex-home/sessions'
        for path in session_root.rglob('*.jsonl'):
            for line in path.open(encoding='utf-8'):
                row = json.loads(line)
                if row.get('type') == 'turn_context':
                    contexts.append({k: row['payload'].get(k) for k in ['cwd', 'model', 'effort', 'service_tier', 'approval_policy']})
        raw = subprocess.check_output(['powershell', '-NoProfile', '-Command',
            "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'codex.exe' -and $_.CommandLine -match 'listen stdio' } | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json"], text=True)
        native = json.loads(raw)
        assert safe['model'] == 'gpt-6-astra' and safe['thinking_level'] == 'max' and safe['service_tier'] == 'default'
        assert contexts and all(c['model'] == 'gpt-6-astra' and c['effort'] == 'max' for c in contexts)
        command = native['CommandLine']
        assert all(s in command for s in ['gpt-6-astra', 'max', 'service_tier=', 'default', '--disable fast_mode', 'chatgpt'])
        previous.write(OUT / 'native-settings-verified.json', {'profile': safe, 'contexts': contexts, 'native': native})
        print(json.dumps({'model': safe['model'], 'effort': 'max', 'tier': 'default', 'contexts': contexts}))
    elif operation == 'verify':
        previous.verify()
        previous.write(OUT / 'storage-after.json', {'bytes': previous.storage(), 'limit_bytes': 250_000_000_000})
    elif operation == 'verify-final':
        # Reuse the retained verifier without overwriting earlier review evidence.
        original_write = previous.write
        def final_write(path, value):
            destination = path.with_name(path.name.replace('-after.', '-final.'))
            assert not destination.exists(), destination
            original_write(destination, value)
        previous.write = final_write
        previous.verify()
        previous.write(OUT / 'storage-after.json', {'bytes': previous.storage(), 'limit_bytes': 250_000_000_000})
    elif operation == 'snapshot':
        label = sys.argv[2]
        assert label.replace('-', '').isalnum()
        destination = OUT / label / 'SourceSnapshot'
        assert not destination.exists()
        paths = list((ROOT / 'Source/MeridianSquad').glob('Combat*')) + list((ROOT / 'Scripts/CombatFoundation01').glob('*.py'))
        rows = []
        for source in paths:
            target = destination / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            rows.append(dict(path=source.relative_to(ROOT).as_posix(), sha256=previous.sha(source)))
        previous.write(OUT / label / 'candidate-hashes.json', rows)
        print(json.dumps({'snapshot': label, 'files': len(rows)}))
