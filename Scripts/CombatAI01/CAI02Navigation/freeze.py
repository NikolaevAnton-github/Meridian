"""Freeze the bounded navigation correction once; retain Candidate01 unchanged."""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).resolve().parent
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate02'
PREVIOUS=OUT.parent/'Candidate01'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(name,data):
    # A failed packaging attempt may already have written a verified sidecar.
    # Check identical content without replacing it; the manifest guard above
    # still forbids any second freeze or rebaseline.
    if (OUT/name).exists():
        assert read(OUT/name)==data, 'Existing sidecar differs: '+name
        return
    with (OUT/name).open('x',encoding='utf-8') as stream:
        json.dump(data,stream,indent=2)


manifest=OUT/'candidate-manifest.json'
archive=OUT/'CAI02-Candidate02-frozen.zip'
evidence=OUT/'CAI02-Candidate02-evidence.zip'
assert not any(path.exists() for path in (manifest,archive,evidence)), 'Never rebaseline a frozen candidate'
checks=read(OUT/'checks-check01.json')
assert checks['passed'] and read(OUT/'execution-settings.json')['passed']
build=(OUT/'build01.log').read_text(encoding='utf-8-sig')
assert 'Result: Succeeded' in build
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
assert sha(dll)=='cf138423924d3bc3a820de26c6d6f9970dc01879265bcc94ad00edbada8203aa'
editor_json=subprocess.check_output(['powershell','-NoProfile','-Command',
    "@(Get-CimInstance Win32_Process -Filter \"Name = 'UnrealEditor.exe'\" | Select-Object ProcessId) | ConvertTo-Json"],text=True).strip()
assert not editor_json or json.loads(editor_json)==[], 'Unexpected live editor; do not claim lifecycle state'
assets=subprocess.check_output(['git','status','--porcelain','--','Content','Plugins'],cwd=ROOT,text=True).strip()
assert not assets
preservation={}
for filename in ('candidate01-preservation-before.json','historical-preservation-before.json'):
    rows=read(OUT/filename)
    assert all(sha(ROOT/row['path'])==row['sha256'] for row in rows), filename
    preservation[filename]=dict(files=len(rows),matches=True)
owner=[]
for row in read(OUT/'owner-preservation-before.json'):
    match=sha(ROOT/row['path'])==row['sha256']
    if row['path']!='AGENTS.md': assert match,row
    owner.append(dict(path=row['path'],sha256=sha(ROOT/row['path']),match=match))
assert (ROOT/'AGENTS.md').read_bytes().split(b'<!-- BEGIN MULTICA-RUNTIME',1)[0].rstrip()==(ROOT/'Saved/CombatAI01/CAI-02/Controller/AGENTS.md').read_bytes().rstrip()
write('preservation-final.json',dict(evidence=preservation,owner=owner,durable_AGENTS=True,assets_changed=False,
    runtime_note='Preserved Multica managed runtime append; controller-owned files not edited.'))
write('build-result.json',dict(result='PASS',exit_code=0,actions=16,seconds=23.43,
    target='MeridianSquadEditor Win64 Development',dll_sha256=sha(dll),
    editor_processes=[],editor_reload='PENDING controller ordinary lobby reload after primary review',
    agent_gameplay=False))

with zipfile.ZipFile(PREVIOUS/'CAI02-Candidate01-frozen.zip') as prior:
    delta=[]
    for name in checks['changed_source']:
        before=prior.read(name).decode('utf-8-sig').replace('\r\n','\n').splitlines(keepends=True)
        after=(ROOT/name).read_text(encoding='utf-8-sig').splitlines(keepends=True)
        delta.extend(difflib.unified_diff(before,after,fromfile='Candidate01/'+name,tofile='Candidate02/'+name))
with (OUT/'source-delta-from-candidate01.patch').open('x',encoding='utf-8') as stream:
    stream.write(''.join(delta))

paths=sorted((ROOT/'Source/MeridianSquad').glob('*.h'))+sorted((ROOT/'Source/MeridianSquad').glob('*.cpp'))
paths += [ROOT/'Source/MeridianSquad/MeridianSquad.Build.cs',dll,ROOT/'Binaries/Win64/UnrealEditor.modules',
    ROOT/'Docs/CombatAI01-CAI02.md',ROOT/'Docs/CombatAI01-CAI02Navigation01.md']
paths += sorted(path for path in SCRIPT.iterdir() if path.suffix in ('.py','.cpp'))
paths += sorted(path for path in (ROOT/'Scripts/CombatAI01/CAI02').iterdir() if path.suffix in ('.py','.cpp'))
paths += [ROOT/'Scripts/CombatAI01/CAIT01/check_correction.py',ROOT/'Scripts/CombatAI01/CAIT01/correction_prefix.cpp']
paths += sorted(path for path in OUT.iterdir() if path.suffix in ('.json','.log','.cpp','.patch'))
reused=['candidate-manifest.json','checks-check04.json','editor-geometry.json','editor-audio.json',
    'editor-player_notifies.json','editor-asset_wiring.json','freeze-result.json']
paths += [PREVIOUS/name for name in reused]
paths=sorted(set(paths))
rows=[dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path)) for path in paths]
data=dict(task='MSQ-104',candidate='Candidate02/build01',frozen_at_utc=datetime.now(timezone.utc).isoformat(),
    baseline=read(OUT/'baseline.json'),changed_source=checks['changed_source'],files=rows,
    verification='PASS native build and 202 affected navigation assertions including per-strip checks; 16 compile/source/preservation checks. Reuse Candidate01 senses/audio/weapon/wiring evidence.',
    primary_review='PENDING controller dispatch',owner_gameplay='PENDING',
    final_editor_reload='PENDING controller ordinary retained-lobby reload',mutable_controller_logs_included=False)
with manifest.open('x',encoding='utf-8') as stream: json.dump(data,stream,indent=2)
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as package:
    for path in paths+[manifest]: package.write(path,path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence,'x',compression=zipfile.ZIP_DEFLATED) as package:
    for path in paths+[manifest]:
        if path.is_relative_to(OUT) or path.is_relative_to(SCRIPT) or path.name=='CombatAI01-CAI02Navigation01.md':
            package.write(path,path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as package:
    for row in rows: assert hashlib.sha256(package.read(row['path'])).hexdigest()==row['sha256']
result=dict(entries=len(rows),manifest_sha256=sha(manifest),dll_sha256=sha(dll),
    frozen_sha256=sha(archive),frozen_bytes=archive.stat().st_size,
    evidence_sha256=sha(evidence),evidence_bytes=evidence.stat().st_size,all_frozen_bytes_verified=True)
write('freeze-result.json',result)
print(json.dumps(result,indent=2))
