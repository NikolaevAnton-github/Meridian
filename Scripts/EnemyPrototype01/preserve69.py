"""Task-scoped use of the established immutable preservation inventory."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/EnemyPrototype01/Worker'
spec = importlib.util.spec_from_file_location('preservation61', ROOT / 'Scripts/PurchasedArms01/preserve.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.OUT = OUT

if __name__ == '__main__':
    if sys.argv[1] == 'baseline':
        base.baseline()
        profile = json.loads((OUT.parent / 'Controller/profile-before.json').read_text(encoding='utf-8-sig'))
        safe = {k: profile.get(k) for k in ['model', 'thinking_level', 'service_tier', 'custom_args']}
        contexts = []
        session_root = ROOT / 'Saved/Multica/workspaces/meridiansqu-6f91832bf07d/msq-69-38609ab8038e/codex-home/sessions'
        for path in session_root.rglob('*.jsonl'):
            for line in path.open(encoding='utf-8'):
                row = json.loads(line)
                if row.get('type') == 'turn_context':
                    contexts.append({k: row['payload'].get(k) for k in ['cwd', 'model', 'effort', 'service_tier']})
        raw = subprocess.check_output(['powershell', '-NoProfile', '-Command',
            "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'codex.exe' -and $_.CommandLine -match 'listen stdio' } | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json"], text=True)
        native = json.loads(raw)
        commands = native if isinstance(native, list) else [native]
        matching = [r for r in commands if all(t in r['CommandLine'] for t in ['gpt-6-astra', 'max', 'default', '--disable fast_mode', 'chatgpt'])]
        assert safe['model'] == 'gpt-6-astra' and safe['thinking_level'] == 'max' and safe['service_tier'] == 'default'
        assert contexts and all(c['model'] == 'gpt-6-astra' and c['effort'] == 'max' for c in contexts)
        assert matching
        base.write(OUT / 'native-settings-verified.json', dict(profile=safe, contexts=contexts, native=matching))
        print(json.dumps(dict(settings='gpt-6-astra/max/default; fast disabled', contexts=contexts)))
    elif sys.argv[1] == 'verify':
        # Active files are compared directly; existing archives remain immutable.
        changed, missing = [], []
        for row in json.loads((OUT / 'preservation-before.json').read_text()):
            p = Path(row['path'])
            if not p.exists(): missing.append(str(p))
            elif base.sha(p) != row['sha256']: changed.append(str(p))
        base.write(OUT / 'preservation-after.json', dict(changed=changed, missing=missing))
        total = base.storage()
        before = json.loads((OUT / 'storage-before.json').read_text())['bytes']
        base.write(OUT / 'storage-after.json', dict(bytes=total, growth=total-before, limit_bytes=250_000_000_000))
        print(json.dumps(dict(changed=changed, missing=missing, project_bytes=total, growth=total-before)))
