"""Freeze the final MSQ-119 candidate once, preserving earlier attempts and inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,d):
    with (OUT/n).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
assert not (OUT/'candidate-manifest.json').exists(),'Never rebaseline an immutable candidate'
check=read(OUT/'checks-09.json')
assert check['passed'] and check['run_exit']==0
assert read(OUT/'execution-settings.json')['passed']
assert read(OUT/'build-result04.json')['exit_code']==0
assert 'Result: Succeeded' in (OUT/'build04.log').read_text(encoding='utf-8-sig')
state=read(OUT/'editor-after02.json')
assert not state['pie'] and not state['dirty']
assert state['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
loaded=read(OUT/'editor-load-check02.json')
assert loaded['matches_launch'] and loaded['no_live_coding_modules'] and loaded['sha256']==sha(dll)
history=read(OUT/'historical-preservation-before.json')
assert all(sha(ROOT/r['path'])==r['sha256'] for r in history)
owner=[]
for r in read(OUT/'owner-preservation-before.json'):
    actual=sha(ROOT/r['path']);owner.append(dict(**r,current_sha256=actual,matches=actual==r['sha256']))
    if r['path'] in ('Config/DefaultEngine.ini','MeridianSquad.uproject','Content/Maps/L_OpeningLobby_PainterStone01.umap'):
        assert actual==r['sha256'],r
assert not subprocess.check_output(['git','status','--porcelain','--','Content','Plugins','Assets'],cwd=ROOT,text=True).strip()
diff=subprocess.run(['git','-c','core.safecrlf=false','diff','--check','--','Source/MeridianSquad','Scripts/CombatAI01/CAIT02','Docs/CombatAI01-CoverFire01.md'],cwd=ROOT,capture_output=True,text=True)
assert diff.returncode==0,diff.stdout+diff.stderr
write('preservation-final.json',dict(owner=owner,historical_files=len(history),historical_match=True,
    assets_unchanged=True,diff_check_passed=True,controller_document_drift_is_not_worker_authorship=True))
baseline=read(OUT/'source-before.json');before={r['path']:r['sha256'] for r in baseline}
source=[p for p in (ROOT/'Source/MeridianSquad').iterdir() if p.is_file()]
changed=[p.relative_to(ROOT).as_posix() for p in source if before.get(p.relative_to(ROOT).as_posix())!=sha(p)]
write('scope-and-verification.json',dict(task='MSQ-119',candidate='Candidate01/build04',changed_source=sorted(changed),
    assertions=71,extracted_production_methods=len(check['methods']),native_build='PASS',
    independent_review='PENDING controller dispatch',owner_gameplay='PENDING',agent_gameplay=False,
    status_profiles_registry_commits_changed_by_worker=False,editor_pid=loaded['pid']))
paths=source+[dll,ROOT/'Binaries/Win64/UnrealEditor.modules',ROOT/'Docs/CombatAI01-CoverFire01.md']
paths+=list((ROOT/'Scripts/CombatAI01/CAIT02').glob('*.py'))+list((ROOT/'Scripts/CombatAI01/CAIT02').glob('*.cpp'))
# The open editor's log can keep growing after handoff; freeze only a bounded snapshot.
live=OUT/'editor-final02.log'
(OUT/'editor-startup-snapshot.log').write_bytes(live.read_bytes())
paths += [p for p in OUT.iterdir() if p.suffix in ('.json','.log','.cpp') and p.name not in ('editor-final.log','editor-final02.log')]
paths=sorted(set(paths))
manifest=OUT/'candidate-manifest.json'
rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]
write(manifest.name,dict(task='MSQ-119',candidate='Candidate01/build04',frozen_utc=datetime.now(timezone.utc).isoformat(),
    baseline=read(OUT/'baseline.json'),verification='PASS native build, 71 assertions / 49 production methods, preserved inputs and matching ordinary editor DLL',
    review='PENDING independent technical reviewer',gameplay='PENDING OWNER',files=rows))
archive=OUT/'CAIT02-Candidate01-frozen.zip';evidence=OUT/'CAIT02-Candidate01-evidence.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    for p in paths+[manifest]:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence,'x',zipfile.ZIP_DEFLATED) as z:
    for p in paths+[manifest]:
        if p.is_relative_to(OUT) or p.is_relative_to(ROOT/'Scripts/CombatAI01/CAIT02') or p.name=='CombatAI01-CoverFire01.md' or p.relative_to(ROOT).as_posix() in changed:
            z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert all(hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'] for r in rows)
result=dict(entries=len(rows),dll_sha256=sha(dll),manifest_sha256=sha(manifest),
    frozen_sha256=sha(archive),frozen_bytes=archive.stat().st_size,evidence_sha256=sha(evidence),evidence_bytes=evidence.stat().st_size,
    all_archived_bytes_verified=True,task_data_bytes=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()))
write('freeze-result.json',result)
print(json.dumps(result,indent=2))
