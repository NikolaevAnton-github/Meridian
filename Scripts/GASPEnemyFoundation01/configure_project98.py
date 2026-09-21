"""Append only the sample's named CVar defaults and capsule profile, preserving owner bytes."""
from pathlib import Path
import hashlib, json, re

root = Path(__file__).resolve().parents[2]
target = root / 'Config/DefaultEngine.ini'
before = target.read_bytes()
source = Path('D:/devgames/GameAnimationSample/Config/DefaultEngine.ini').read_text(encoding='utf-8-sig')
text = before.decode('utf-8-sig')
lines = [line for line in source.splitlines() if line.startswith('+CVarsArray=')
         and re.search(r'Name="([^"]+)"', line).group(1) not in text]
profile = next(line for line in source.splitlines() if line.startswith('+Profiles=(Name="CharacterCapsule"'))
extra = '\n; MSQ-98: GASP enemy defaults. Player and global physics settings remain owner-authored.\n'
if lines:
    extra += '[/Script/Engine.DataDrivenConsoleVariableSettings]\n' + '\n'.join(lines) + '\n'
if 'Name="CharacterCapsule"' not in text:
    extra += '\n[/Script/Engine.CollisionProfile]\n' + profile + '\n'
assert lines or 'Name="CharacterCapsule"' not in text, 'Already configured; inspect instead of replaying.'
evidence = root / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
(evidence / 'DefaultEngine-before98.ini').write_bytes(before)
target.write_bytes(before + extra.replace('\n', '\r\n').encode('utf-8'))
after = target.read_bytes()
assert after.startswith(before)
with (evidence / 'config98.json').open('x', encoding='utf-8') as f:
    json.dump({'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': hashlib.sha256(after).hexdigest(),
               'owner_prefix_preserved': True, 'added_cvars': len(lines), 'added_capsule_profile': True}, f, indent=2)
print('Preserved owner config bytes; appended', len(lines), 'GASP defaults and capsule profile.')
