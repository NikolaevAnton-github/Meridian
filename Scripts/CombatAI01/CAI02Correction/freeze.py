"""Freeze Candidate03 once; previous manifests, archives and reports are immutable."""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import hashlib
import json
import re
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).resolve().parent
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate03'
PREVIOUS=OUT.parent/'Candidate02'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as stream:json.dump(data,stream,indent=2)

manifest=OUT/'candidate-manifest.json'
archive=OUT/'CAI02-Candidate03-frozen.zip'
assert not any(p.exists() for p in (manifest,archive,OUT/'freeze-result.json')), 'Never rebaseline a frozen candidate'
checks=read(OUT/'checks-03.json')
assert checks['passed'] and read(OUT/'execution-settings.json')['passed']
assert 'checks=59 failures=0' in checks['output'] and len(checks['checks'])==26
build=(OUT/'build01.log').read_text(encoding='utf-8-sig')
assert 'Result: Succeeded' in build
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
assert sha(dll)==checks['dll_sha256']=='c0c3b64f8ab48bd9c9eb6cbb4100a7a9a3a2c0ea42f240ba32fdf7c8ea66d488'
editor_output=subprocess.check_output(['powershell','-NoProfile','-Command',
    "@(Get-CimInstance Win32_Process -Filter \"Name = 'UnrealEditor.exe'\" | Select-Object ProcessId) | ConvertTo-Json"],text=True).strip()
assert not editor_output or json.loads(editor_output)==[], 'Unexpected live editor; revise the handoff without lifecycle mutations'
assets=subprocess.check_output(['git','status','--porcelain','--','Content','Plugins'],cwd=ROOT,text=True).strip()
assert not assets, 'Unexpected asset changes'
preservation={}
for group in ('previous','historical','owner'):
    rows=read(OUT/f'{group}-preservation-before.json')
    assert all(sha(ROOT/row['path'])==row['sha256'] for row in rows), group
    preservation[group]=dict(files=len(rows),matches=True)
write('preservation-final.json',dict(groups=preservation,assets_changed=False,controller_files_unchanged=True))
write('build-result.json',dict(result='PASS',exit_code=0,target='MeridianSquadEditor Win64 Development',
    actions=16,seconds=float(re.search(r'Total execution time: ([\d.]+) seconds',build)[1]),
    dll_sha256=sha(dll),editor_processes=[],editor_reload='PENDING controller ordinary lobby reload after finding closure',
    agent_gameplay=False))

with zipfile.ZipFile(PREVIOUS/'CAI02-Candidate02-frozen.zip') as prior:
    delta=[]
    for name in checks['changed_source']:
        before=prior.read(name).decode('utf-8-sig').replace('\r\n','\n').splitlines(keepends=True)
        after=(ROOT/name).read_text(encoding='utf-8-sig').splitlines(keepends=True)
        delta.extend(difflib.unified_diff(before,after,fromfile='Candidate02/'+name,tofile='Candidate03/'+name))
with (OUT/'source-delta-from-candidate02.patch').open('x',encoding='utf-8') as stream:stream.write(''.join(delta))

mapping={
    'CAI02-R1':dict(change='Coalesce protected-search evidence; retain deadline, progress, action and transfer history; revalidate winner/destination against latest evidence.',
        check='checks-03.json / run-03.log: 20 steps over eight world seconds at 120 and 5 Hz; latest-winner veto, safe/unsafe moving retarget, physical cancellation/recovery/reset and reload/sight precedence.',
        self_check='PASS',primary_finding_closure='PENDING same primary reviewer'),
    'CAI02-R2':dict(change='Explicit intended/achieved stance profiles for body/eye/weapon/exposure/facing; guard movement and arrival, immediate hold reassessment, visible-contact standing request before backoff.',
        check='checks-03.json / run-03.log: original high ledge, reverse low ledge, low body/exposure screens, unachieved crouch, actual arrival, mid-route/held stance changes and contact with/without backoff.',
        self_check='PASS',primary_finding_closure='PENDING same primary reviewer')}
reuse=[
    dict(candidate='Candidate02/build01',evidence='checks-check01.json: 202 navigation assertions and 16 supporting checks',scope='Unchanged navigator/domain/ceilings/pursuit tuning; no navigation rerun.'),
    dict(candidate='Candidate01/build04',evidence='checks-check04.json, audio/notify audit, saved-class ancestry and native build',scope='Unchanged hearing producers/delivery, grounded audio, immutable knowledge and weapon/physical seams. The coupled intent/scan/stance checks are superseded only by the new affected evidence.'),
    dict(candidate='Candidate02 primary review',evidence='Docs/CombatAI01-CAI02Review.md and retained reproducer archive',scope='Reuse unaffected passing criteria. Preserve the original changes-requested verdict and failed R1/R2 evidence unchanged.')]
write('scope-and-verification.json',dict(changed_source=checks['changed_source'],findings=mapping,reused_evidence=reuse,
    pure_assertions=59,extracted_methods=len(checks['methods']),supporting_checks=len(checks['checks']),
    pending_owner=['gameplay','motion','audibility','actual map-position usefulness','difficulty','performance'],
    controller_only=['primary finding-closure dispatch','ordinary editor reload','acceptance','status/profile administration','local closure commit']))

paths=sorted(p for p in (ROOT/'Source/MeridianSquad').glob('*') if p.suffix in ('.h','.cpp','.cs'))
paths += [dll,ROOT/'Binaries/Win64/UnrealEditor.modules']
paths += [ROOT/'Docs'/name for name in ('CombatAI01-CAI02.md','CombatAI01-CAI02Navigation01.md','CombatAI01-CAI02Review.md','CombatAI01-CAI02Correction01.md')]
paths += sorted(p for p in SCRIPT.iterdir() if p.suffix in ('.py','.cpp'))
paths += sorted(p for p in OUT.iterdir() if p.suffix in ('.json','.log','.cpp','.patch'))
for candidate,names in {
    'Candidate01':['candidate-manifest.json','freeze-result.json','checks-check04.json','editor-asset_wiring.json'],
    'Candidate02':['candidate-manifest.json','freeze-result.json','checks-check01.json'],
}.items():paths += [OUT.parent/candidate/name for name in names]
paths += [OUT.parents[1]/'Review'/name for name in ('gaps-02.json','gaps-run-02.log','gap_adapters.cpp','gap_tests.cpp','run_gaps.py')]
paths=sorted(set(paths))
rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]
data=dict(task='MSQ-104',candidate='Candidate03/build01',frozen_at_utc=datetime.now(timezone.utc).isoformat(),
    baseline=read(OUT/'baseline.json'),changed_source=checks['changed_source'],findings=mapping,reused_evidence=reuse,files=rows,
    verification='PASS native build; 59 affected assertions across 22 exact production methods; 26 compile/source/preservation checks.',
    primary_review='PENDING same primary reviewer finding closure',owner_gameplay='PENDING',
    final_editor_reload='PENDING controller ordinary retained-lobby reload',mutable_controller_logs_included=False)
with manifest.open('x',encoding='utf-8') as stream:json.dump(data,stream,indent=2)
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as package:
    for p in paths+[manifest]:package.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as package:
    for row in rows:assert hashlib.sha256(package.read(row['path'])).hexdigest()==row['sha256'],row['path']
result=dict(entries=len(rows),manifest_sha256=sha(manifest),dll_sha256=sha(dll),
    frozen_sha256=sha(archive),frozen_bytes=archive.stat().st_size,all_frozen_bytes_verified=True)
write('freeze-result.json',result)
print(json.dumps(dict(result=result,preservation=preservation),indent=2))
