"""MSQ-68 preservation reuses the established source and storage inventory."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'
sys.path.insert(0, str(ROOT / 'Scripts/PurchasedArms01'))
import preserve as previous
previous.OUT = OUT

if __name__ == '__main__':
    operation = sys.argv[1]
    if operation == 'baseline':
        previous.baseline()
        packages = ['Common/Core/Characters/BP_TFA_BaseCharacter',
                    'Common/Core/Weapons/BP_TFA_BaseWeapon']
        for package in packages:
            relative = Path('Content/InfimaGames/TacticalFPSAnimations') / (package + '.uasset')
            target = OUT / 'Rollback' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            assert not target.exists()
            shutil.copy2(ROOT / relative, target)
    elif operation == 'verify':
        previous.verify()
        previous.write(OUT / 'storage-after.json', {'bytes': previous.storage(), 'limit_bytes': 250_000_000_000})
    elif operation == 'native':
        raw = subprocess.check_output(['multica', 'agent', 'get', 'd3ed0aae-f7e4-40d2-9568-9aa9b11fdf51', '--output', 'json'])
        profile = json.loads(raw)
        safe = {k: profile.get(k) for k in ['id', 'model', 'thinking_level', 'service_tier', 'custom_args', 'max_concurrent_tasks']}
        session_root = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-68-7e7eab995c07/codex-home/sessions'
        contexts = []
        for session in session_root.rglob('*.jsonl'):
            for line in session.open(encoding='utf-8'):
                row = json.loads(line)
                if row.get('type') == 'turn_context':
                    contexts.append({k: row['payload'].get(k) for k in ['cwd', 'model', 'effort', 'service_tier', 'approval_policy']})
        assert safe['model'] == 'gpt-6-astra' and safe['thinking_level'] == 'max' and safe['service_tier'] == 'default'
        assert contexts and all(c['model'] == 'gpt-6-astra' and c['effort'] == 'max' for c in contexts)
        previous.write(OUT / 'native-settings-verified.json', {'profile': safe, 'contexts': contexts})
        print(json.dumps({'model': safe['model'], 'effort': safe['thinking_level'], 'tier': safe['service_tier'], 'contexts': contexts}))
