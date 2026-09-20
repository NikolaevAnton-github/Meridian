"""Validate the final immutable handoff and explicitly delimit evidence reuse."""
import difflib
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlLegPose01/Worker'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    p=OUT/name;assert not p.exists(),p;p.write_text(json.dumps(value,indent=2),encoding='utf-8')
def manifest(name):return {e['path']:e for e in json.loads((OUT/name/'manifest.json').read_text())}

old,current=manifest('Candidate05'),manifest('Candidate06')
native=[p for p in current if p.startswith(('Source/','Binaries/','Content/'))]
changed=[p for p in native if current[p]['sha256']!=old[p]['sha256']]
assert set(changed)=={'Source/MeridianSquad/PhysicsControlStepping.cpp','Source/MeridianSquad/PhysicsControlBalance.cpp','Binaries/Win64/UnrealEditor-MeridianSquad.dll'},changed
diffs={p:''.join(difflib.unified_diff((OUT/'Candidate05'/p).read_text().splitlines(True),
    (OUT/'Candidate06'/p).read_text().splitlines(True),fromfile='Candidate05/'+p,tofile='Candidate06/'+p)) for p in changed if p.startswith('Source/')}
cases=[]
for e in json.loads((OUT/'focused-results02.json').read_text())['cases']:
    name=e['name'];data=json.loads((OUT/(name+'.json')).read_text())
    if name.startswith('Candidate05'):
        assert not any(r['dummy']['step']['corrective'] or r['dummy']['step']['stance_correction_pending'] for r in data['rows'])
        applicability='No sample enters either corrected branch (pending correction or corrective step); normal geometry, driving, fall/get-up, reset and sampling are unchanged.'
    else:applicability='Recorded on Candidate06, with native/asset identity identical to final Candidate07.'
    cases.append(dict(record=name,runtime_sha256=sha(OUT/(name+'.json')),video_sha256=sha(OUT/'Video'/(name+'.mp4')),applicability=applicability))
write('evidence-applicability01.json',dict(native_changes_05_to_06=changed,exact_source_diff=diffs,cases=cases,
    before=dict(candidate='Baseline01',identity='baseline-identity01.json',records=['Before-Rear','Before-Side']),
    unchanged_msq89_scope=['static placement/path probes','six rendered fixtures','native rifle/ammunition and terminal death controls','relative slowdown clocks','input queue and two-step budget logic'],
    excluded_reuse='Old leg poses and precise physical trajectories are not new-pose evidence. No old assertion count is added to the 183 focused checks.'))

images=OUT/'ReviewImages';images.mkdir(exist_ok=False)
for source,dest in [('Before-Rear','Before-Rear'),('Before-Side','Before-Side'),('Candidate05-Rear','After-Rear'),('Candidate05-Side','After-Side')]:
    shutil.copyfile(OUT/'Video'/(source+'-Frames')/'007.20.png',images/(dest+'.png'))

files=['Source/MeridianSquad/'+p for p in ['PhysicsControlStepping.cpp','PhysicsControlDummy.h','PhysicsControlBalance.cpp','PhysicsControlBalanceProbes.cpp']]
files += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'Scripts/PhysicsControlLegPose01').glob('*')) if p.is_file()]
files += ['Docs/PhysicsControlLegPose01.md']
write('changed-files01.json',[dict(path=p,sha256=sha(ROOT/p),bytes=(ROOT/p).stat().st_size) for p in files])
print(json.dumps(dict(scoped_files=len(files),applicable_records=len(cases),source_diffs=list(diffs))))
