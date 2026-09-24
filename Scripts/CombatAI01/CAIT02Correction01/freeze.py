"""Freeze Candidate02 exactly once; old candidate/review bytes are never rewritten."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import stat
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate02'
OLD=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01'
SCRIPT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name,value):
    with (OUT/name).open('x',encoding='utf-8') as stream: json.dump(value,stream,indent=2)
manifest=OUT/'candidate-manifest.json'
assert not manifest.exists(),'Never rebaseline an immutable candidate'
checks=read(OUT/'checks-02.json'); build=read(OUT/'build-result01.json')
assert checks['passed'] and build['exit_code']==0 and read(OUT/'execution-settings.json')['passed']
assert 'Result: Succeeded' in (OUT/'build01.log').read_text(encoding='utf-8-sig')
dll=ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'
assert sha(dll)==build['dll_sha256']
for category in ('owner','historical'):
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in read(OUT/f'{category}-preservation-before.json'))
state=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
    "$editors = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'UnrealEditor*' } | Select-Object ProcessId,Name); [pscustomobject]@{ captured_utc=[DateTime]::UtcNow.ToString('o'); editors=$editors; lifecycle_operations_by_worker=$false; owner_gameplay_run=$false } | ConvertTo-Json -Depth 4"],text=True))
write('editor-final.json',state)
# Count logical file bytes once without following reparse points/junctions into
# duplicate workspaces or external trees. No file is removed for this budget check.
project_bytes=0; project_files=0; reparse_points=0
for directory,dirs,files in os.walk(ROOT,followlinks=False):
    kept=[]
    for name in dirs:
        path=Path(directory)/name
        if path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT: reparse_points+=1
        else: kept.append(name)
    dirs[:]=kept
    for name in files:
        path=Path(directory)/name
        try: info=path.lstat()
        except FileNotFoundError: continue # Unrelated service transient files.
        if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT: reparse_points+=1
        else: project_bytes+=info.st_size; project_files+=1
assert project_bytes+100_000_000 < 250_000_000_000,project_bytes
write('storage.json',dict(project_file_bytes_before_archives=project_bytes,project_files=project_files,
    reparse_points_not_double_counted=reparse_points,archive_reserve_bytes=100_000_000,cap_bytes=250_000_000_000))
paths=[p for p in (ROOT/'Source/MeridianSquad').iterdir() if p.is_file()]
paths += [dll,ROOT/'Binaries/Win64/UnrealEditor.modules',ROOT/'Docs/CombatAI01-CoverFire01Correction01.md',
          ROOT/'Docs/CombatAI01-CoverFire01.md',ROOT/'Docs/CombatAI01-CoverFire01Review.md']
paths += [p for p in SCRIPT.iterdir() if p.suffix in ('.py','.cpp')]
paths += [ROOT/'Scripts/CombatAI01/CAIT02'/name for name in ('check.py','adapters.cpp','boundaries.cpp','tests.cpp')]
paths += [OLD/name for name in ('candidate-manifest.json','checks-09.json','compile-09.log','run-09.log','build-result04.json')]
paths += [p for p in OUT.iterdir() if p.suffix in ('.json','.log','.cpp','.diff')]
paths=sorted(set(paths))
rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]
write(manifest.name,dict(task='MSQ-119',candidate='Candidate02/build01',frozen_utc=datetime.now(timezone.utc).isoformat(),
    baseline=read(OUT/'baseline.json'),findings=['CFT02-R1','CFT02-R2'],
    verification='PASS native Development Editor build and 44 affected assertions; Candidate01 and original review preserved',
    independent_review='PENDING same primary reviewer finding closure',owner_gameplay='PENDING',files=rows))
archive=OUT/'CAIT02-Candidate02-frozen.zip'; evidence=OUT/'CAIT02-Candidate02-evidence.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as stream:
    for p in paths+[manifest]: stream.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(evidence,'x',zipfile.ZIP_DEFLATED) as stream:
    for p in paths+[manifest]:
        if not p.is_relative_to(ROOT/'Binaries'):
            stream.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as stream:
    assert all(hashlib.sha256(stream.read(r['path'])).hexdigest()==r['sha256'] for r in rows)
assert all(sha(ROOT/r['path'])==r['sha256'] for r in rows)
result=dict(entries=len(rows),dll_sha256=sha(dll),manifest_sha256=sha(manifest),
    archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),
    evidence_bytes=evidence.stat().st_size,evidence_sha256=sha(evidence),all_current_and_archived_bytes_match=True,
    candidate_data_bytes=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()))
assert archive.stat().st_size+evidence.stat().st_size < 100_000_000
write('freeze-result.json',result)
print(json.dumps(result,indent=2))
