"""Freeze MSQ-118 once, retaining exact source/DLL/evidence without overwrites."""
from pathlib import Path
import hashlib
import json
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-T01/Worker/Candidate01'
CONTROLLER = ROOT / 'Saved/CombatAI01/CAI-T01/Controller'
BASE = '5ae0fbc48a2c2f2b3cd3da64d15ec1a70446712a'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert json.loads((OUT/'self-check-check03.json').read_text())['passed']
assert json.loads((OUT/'execution-settings.json').read_text())['passed']
build = (OUT/'build02.log').read_bytes()
assert 'Result: Succeeded' in build.decode('utf-16' if build.startswith(b'\xff\xfe') else 'utf-8-sig')
editor = json.loads((OUT/'editor-after.json').read_text())
assert not editor['pie'] and not editor['dirty']
assert editor['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
dll = ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
loaded = json.loads((OUT/'editor-load-check.json').read_text(encoding='utf-8-sig'))
assert loaded['matches_launch'] and loaded['sha256'].lower() == digest(dll)
for entry in json.loads((CONTROLLER/'preservation-before.json').read_text(encoding='utf-8-sig')):
    if entry['path'] != 'AGENTS.md':
        assert digest(ROOT/entry['path']) == entry['sha256'], entry
assert (ROOT/'AGENTS.md').read_bytes().split(b'<!-- BEGIN MULTICA-RUNTIME',1)[0].rstrip() == (CONTROLLER/'AGENTS.md').read_bytes().rstrip()

manifest_path = OUT/'candidate-manifest.json'
frozen_path = OUT/'CAIT01-Candidate01-frozen.zip'
evidence_path = OUT/'CAIT01-Candidate01-evidence.zip'
assert not any(p.exists() for p in [manifest_path, frozen_path, evidence_path]), 'Never overwrite a frozen candidate'
paths = sorted((ROOT/'Source/MeridianSquad').glob('*.h'))
paths += sorted((ROOT/'Source/MeridianSquad').glob('*.cpp'))
paths += [ROOT/'Source/MeridianSquad/MeridianSquad.Build.cs', ROOT/'Docs/CombatAI01-Tactical01.md']
paths += sorted(p for p in (ROOT/'Scripts/CombatAI01/CAIT01').iterdir() if p.suffix in ('.py','.cpp'))
paths += [ROOT/'Scripts/CombatAI01/CAI00/editor_tools.py', ROOT/'Scripts/CombatAI01/CAI01/editor_tools.py']
paths += [dll, ROOT/'Binaries/Win64/UnrealEditor.modules']
paths += sorted(OUT.glob('*.json'))
paths += sorted(p for p in OUT.glob('*.log') if p.name != 'editor02.log')
paths += [CONTROLLER/name for name in ('agent-configured.json','native-process.json','native-turn-contexts.json','preservation-before.json')]
rows = [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p)) for p in paths]
manifest = dict(task='MSQ-118', candidate='Candidate01/build02', baseline=BASE,
    frozen_at_utc=datetime.now(timezone.utc).isoformat(),
    verification='Native Development Editor build, 45 pure test groups, 43 source/preservation/wrapper checks, read-only geometry inventory',
    independent_review='PENDING CONTROLLER DISPATCH',
    actual_movement_position_quality_firing_physics_performance_feel='PENDING OWNER',
    full_AGENTS_hash_exception='Multica startup appended the runtime block; original durable bytes unchanged; original preservation manifest retained',
    files=rows)
with manifest_path.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, indent=2)
with zipfile.ZipFile(frozen_path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in paths + [manifest_path]:
        archive.write(p, p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence_path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in paths + [manifest_path]:
        if p.is_relative_to(OUT) or p.name == 'CombatAI01-Tactical01.md' or p.is_relative_to(ROOT/'Scripts/CombatAI01/CAIT01'):
            archive.write(p, p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(frozen_path) as archive:
    for row in rows:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
summary = dict(entries=len(rows), manifest_sha256=digest(manifest_path), frozen_sha256=digest(frozen_path),
    frozen_bytes=frozen_path.stat().st_size, evidence_bytes=evidence_path.stat().st_size, all_frozen_bytes_verified=True)
with (OUT/'freeze-result.json').open('x') as stream:
    json.dump(summary, stream, indent=2)
print(json.dumps(summary, indent=2))
