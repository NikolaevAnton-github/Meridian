"""Protect dispatch bytes, earlier frozen evidence and the 250 GB physical-tree cap."""
import difflib
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def write(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)

checks=[]
for row in json.loads((OUT/'preservation-before01.json').read_text()):
    actual=digest(ROOT/row['path'])
    checks.append(dict(path=row['path'],expected=row['expected'],actual=actual,match=actual==row['expected']))
previous=ROOT/'Saved/CombatSlice01/PhysicsControlLegPose01/Worker/Candidate07'
for row in json.loads((previous/'manifest.json').read_text()):
    if row['path'].startswith(('Content/','Source/MeridianSquad/DummyRecovery')):
        actual=digest(ROOT/row['path'])
        checks.append(dict(path=row['path'],expected=row['sha256'],actual=actual,match=actual==row['sha256']))
manifests=[previous/'manifest.json',ROOT/'Saved/CombatSlice01/PhysicsControlStepping01/Worker/Candidate05/manifest.json',
           *OUT.glob('*/manifest.json')]
frozen=[]
for manifest in manifests:
    entries=json.loads(manifest.read_text())
    frozen.append(dict(path=manifest.relative_to(ROOT).as_posix(),sha256=digest(manifest),entries=len(entries),
                       all_match=all(digest(manifest.parent/row['path'])==row['sha256'] for row in entries)))
diff=subprocess.check_output(['git','diff','--name-only','--','Content','Assets'],cwd=ROOT,text=True).strip()
assert all(c['match'] for c in checks) and all(f['all_match'] for f in frozen) and not diff
write('preservation-after01.json',dict(checks=checks,frozen_manifests=frozen,content_source_diff=diff,all_match=True))

changed=[]
for row in json.loads((OUT/'Candidate06/manifest.json').read_text()):
    if not row['path'].startswith(('Source/','Content/','Binaries/')):continue
    path=ROOT/row['path'];actual=digest(path)
    if actual!=row['sha256']:
        change=dict(path=row['path'],candidate06_sha256=row['sha256'],candidate07_sha256=actual)
        if row['path'].startswith('Source/'):
            change['diff']=''.join(difflib.unified_diff((OUT/'Candidate06'/row['path']).read_text().splitlines(True),
                path.read_text().splitlines(True),fromfile='Candidate06/'+row['path'],tofile='Candidate07/'+row['path']))
        changed.append(change)
assert {c['path'] for c in changed}=={'Source/MeridianSquad/PhysicsControlDummy.cpp',
    'Source/MeridianSquad/PhysicsControlRecoverability.cpp','Source/MeridianSquad/CombatProjectileWorld.h',
    'Binaries/Win64/UnrealEditor-MeridianSquad.dll'}
write('evidence-applicability01.json',dict(changes=changed,
    rechecked=['finite disabled drive creation','startup and fresh-session defaults','F6 during swing','F10 cleanup/persistence',
               'single-leg rifle replant','three completed steps during continuous torso fire','three rendered identities'],
    reused='Candidate06 dynamics after initialization: paired speed comparison, both-leg disturbance, no-support release, direct contact/fall/get-up, terminal death, relative slowdown. No branch governing those behaviors changed. Demand-ratio correction is telemetry only; startup logs and a stale preset comment were removed.'))

total=count=aliases=0
for directory,dirs,files in os.walk(ROOT,followlinks=False):
    kept=[]
    for name in dirs:
        if (Path(directory)/name).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:aliases+=1
        else:kept.append(name)
    dirs[:]=kept
    for name in files:
        path=Path(directory)/name
        if not path.is_symlink():
            try:total+=path.stat().st_size;count+=1
            except FileNotFoundError:pass
assert total<250e9
write('storage-after01.json',dict(bytes=total,GB=total/1e9,files=count,excluded_reparse_directories=aliases,
    within_250GB=True,method='Physical tree excluding directory aliases; hardlinks conservatively counted separately.'))
print(json.dumps(dict(protected_files=len(checks),frozen_manifests=len(frozen),native_changed_from_candidate06=len(changed),GB=total/1e9)))
