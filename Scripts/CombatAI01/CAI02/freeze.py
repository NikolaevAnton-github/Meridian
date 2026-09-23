"""Freeze the review-ready MSQ-104 candidate once; never rebaseline prior evidence."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
assert read(OUT/'checks-check04.json')['passed']
assert read(OUT/'execution-settings.json')['passed']
assert 'Result: Succeeded' in (OUT/'build04.log').read_text(encoding='utf-8-sig')
assert read(OUT/'FinalReload/editor-closed.json')['closed']
state=read(OUT/'FinalReload/editor-after.json')['after']
assert not state['pie'] and not state['dirty']
assert state['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
assert all(r['uses_native_footstep_filter'] for r in read(OUT/'editor-asset_wiring.json')['blueprints'])
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
load=read(OUT/'FinalReload/editor-load-check.json')
assert load['matches_launch'] and load['sha256'].lower()==sha(dll)
assert not subprocess.check_output(['git','status','--porcelain','--','Content','Plugins'],cwd=ROOT,text=True).strip()
preserved=[]
for row in read(OUT/'owner-preservation-before.json'):
    actual=sha(ROOT/row['path'])
    preserved.append(dict(path=row['path'],sha256=actual,match=actual==row['sha256']))
    if row['path']!='AGENTS.md':assert actual==row['sha256'],row
assert (ROOT/'AGENTS.md').read_bytes().split(b'<!-- BEGIN MULTICA-RUNTIME',1)[0].rstrip()==(ROOT/'Saved/CombatAI01/CAI-02/Controller/AGENTS.md').read_bytes().rstrip()
assert all(sha(ROOT/r['path'])==r['sha256'] for r in read(OUT/'historical-preservation-before.json'))
with (OUT/'preservation-final.json').open('x') as f:json.dump(dict(owner=preserved,durable_instructions=True,
    history_files=146,history_matches=True,assets_changed=False,full_AGENTS_difference='Multica managed runtime append at startup'),f,indent=2)

paths=sorted((ROOT/'Source/MeridianSquad').glob('*.h'))+sorted((ROOT/'Source/MeridianSquad').glob('*.cpp'))
paths += [ROOT/'Source/MeridianSquad/MeridianSquad.Build.cs',ROOT/'Docs/CombatAI01-CAI02.md',dll,ROOT/'Binaries/Win64/UnrealEditor.modules']
paths += sorted(p for p in (ROOT/'Scripts/CombatAI01/CAI02').iterdir() if p.suffix in ('.py','.cpp'))
paths += [ROOT/'Scripts/CombatAI01/CAI00/editor_tools.py',ROOT/'Scripts/CombatAI01/CAI01/editor_tools.py',ROOT/'Scripts/OpeningLobby/functionalbuild01_client.py']
paths += sorted(p for p in OUT.rglob('*') if p.suffix in ('.json','.log','.cpp'))
manifest=OUT/'candidate-manifest.json'
archive=OUT/'CAI02-Candidate01-frozen.zip'
evidence=OUT/'CAI02-Candidate01-evidence.zip'
assert not any(p.exists() for p in [manifest,archive,evidence])
rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]
data=dict(task='MSQ-104',candidate='Candidate01/build04',baseline=read(OUT/'baseline.json')['head'],
    frozen_at_utc=datetime.now(timezone.utc).isoformat(),
    verification='PASS native build, 66 pure assertions, 22 extracted-method assertions, source/preservation and read-only editor wiring/load',
    review='PENDING primary independent controller dispatch',gameplay='PENDING OWNER',
    mutable_controller_logs_included=False,files=rows)
with manifest.open('x') as f:json.dump(data,f,indent=2)
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for p in paths+[manifest]:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for p in paths+[manifest]:
        if p.is_relative_to(OUT) or p.is_relative_to(ROOT/'Scripts/CombatAI01/CAI02') or p.name=='CombatAI01-CAI02.md':
            z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
result=dict(entries=len(rows),manifest_sha256=sha(manifest),frozen_sha256=sha(archive),frozen_bytes=archive.stat().st_size,
    evidence_sha256=sha(evidence),evidence_bytes=evidence.stat().st_size,dll_sha256=sha(dll),all_frozen_bytes_verified=True)
with (OUT/'freeze-result.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
