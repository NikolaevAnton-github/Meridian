"""Freeze the verified MSQ-103 candidate once. Refuses manifest/zip overwrite."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-01/Worker/Candidate01'
assert json.loads((OUT / 'self-check.json').read_text())['passed']
build_bytes = (OUT / 'build05.log').read_bytes()
build_text = build_bytes.decode('utf-16' if build_bytes.startswith(b'\xff\xfe') else 'utf-8-sig')
assert 'Result: Succeeded' in build_text
assert not json.loads((OUT / 'editor-after.json').read_text())['pie']
assert not json.loads((OUT / 'editor-after.json').read_text())['dirty']
paths = sorted((ROOT / 'Source/MeridianSquad').glob('*.h'))
paths += sorted((ROOT / 'Source/MeridianSquad').glob('*.cpp'))
paths += [ROOT / 'Source/MeridianSquad/MeridianSquad.Build.cs', ROOT / 'Docs/CombatAI01-CAI01.md']
paths += sorted((ROOT / 'Scripts/CombatAI01/CAI01').glob('*.py'))
paths += sorted((ROOT / 'Scripts/CombatAI01/CAI01').glob('*.cpp'))
paths += [ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll', ROOT / 'Binaries/Win64/UnrealEditor.modules']
paths += sorted(OUT.glob('*.json'))
paths += sorted(p for p in OUT.glob('*.log') if p.name not in ('editor.log', 'editor05.log'))
rows = [dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
             sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]
manifest = dict(task='MSQ-103', candidate='Candidate01/build05', baseline='b0e599d5f39023fa5c04d5e6b222b3415655621e',
    verification='native build, source and pure production-header checks; no gameplay',
    independent_review='PENDING CONTROLLER DISPATCH', runtime='PENDING OWNER', files=rows)
with (OUT / 'candidate-manifest.json').open('x') as stream:
    json.dump(manifest, stream, indent=2)
with zipfile.ZipFile(OUT / 'CAI01-Candidate01-evidence.zip', 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in paths + [OUT / 'candidate-manifest.json']:
        # Source is in the shared checkout; the handoff attachment carries diagnostics.
        if p.is_relative_to(OUT) or p.name == 'CombatAI01-CAI01.md':
            archive.write(p, p.relative_to(ROOT).as_posix())
print(json.dumps(dict(entries=len(rows), manifest_sha256=hashlib.sha256((OUT/'candidate-manifest.json').read_bytes()).hexdigest())))
