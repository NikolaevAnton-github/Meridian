"""Identify the correction delta and preserve existing owner/candidate/review inputs."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate02'
OLD=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name,value):
    with (OUT/name).open('x',encoding='utf-8') as stream: json.dump(value,stream,indent=2)
source=read(OUT/'source-before.json')
changed=[r['path'] for r in source if sha(ROOT/r['path'])!=r['sha256']]
expected=['Source/MeridianSquad/'+n for n in ('EnemyCombatComponent.cpp','EnemyCombatComponent.h','EnemyCombatPolicy.cpp','EnemyCombatTactics.cpp')]
assert set(changed)==set(expected),changed
assert {p.relative_to(ROOT).as_posix() for p in (ROOT/'Source/MeridianSquad').iterdir() if p.is_file()}=={r['path'] for r in source}
checks=read(OUT/'checks-02.json')
assert checks['passed']
before={r['method']:r for r in read(OLD/'checks-09.json')['methods']}
method_delta=[r['method'] for r in checks['methods'] if r['kind']=='production_method' and
              (r['method'] not in before or r['sha256']!=before[r['method']]['sha256'])]
diff=[]
with zipfile.ZipFile(OLD/'CAIT02-Candidate01-frozen.zip') as archive:
    for path in changed:
        old=archive.read(path).decode('utf-8-sig').replace('\r\n','\n')
        new=(ROOT/path).read_text(encoding='utf-8-sig')
        diff.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),
                                       fromfile='Candidate01/'+path,tofile='Candidate02/'+path))
with (OUT/'correction-source.diff').open('x',encoding='utf-8') as stream: stream.writelines(diff)
preservation={}
for kind in ('owner','historical'):
    entries=read(OUT/f'{kind}-preservation-before.json')
    mismatches=[r['path'] for r in entries if not (ROOT/r['path']).is_file() or sha(ROOT/r['path'])!=r['sha256']]
    assert not mismatches,mismatches
    preservation[kind]=dict(files=len(entries),all_match=True,mismatches=mismatches)
asset_status=subprocess.check_output(['git','status','--porcelain','--','Content','Assets','Plugins'],cwd=ROOT,text=True)
assert not asset_status.strip(),asset_status
diff_check=subprocess.run(['git','-c','core.safecrlf=false','diff','--check','--',*expected,'Scripts/CombatAI01/CAIT02Correction01'],cwd=ROOT,text=True,capture_output=True)
assert diff_check.returncode==0,diff_check.stdout+diff_check.stderr
preservation.update(changed_source=changed,changed_or_new_extracted_methods=method_delta,
    unchanged_other_source_files=len(source)-len(changed),asset_status_clean=True,diff_check_passed=True,
    independent_review='PENDING same primary reviewer closure',owner_gameplay='PENDING',agent_gameplay=False,
    source_diff_sha256=sha(OUT/'correction-source.diff'))
write('preservation-final.json',preservation)
print(json.dumps(preservation,indent=2))
