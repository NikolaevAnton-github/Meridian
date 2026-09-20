"""Bind reused observations to the unchanged branches of the final source."""
import difflib
import hashlib
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

prior = OUT / 'Candidate03'
changes = []
for e in json.loads((prior/'manifest.json').read_text()):
    if not e['path'].startswith(('Source/', 'Binaries/', 'Content/')):
        continue
    actual = digest(ROOT/e['path'])
    if actual != e['sha256']:
        row = dict(path=e['path'],candidate03_sha256=e['sha256'],current_sha256=actual)
        if e['path'].startswith('Source/'):
            row['diff'] = ''.join(difflib.unified_diff((prior/e['path']).read_text().splitlines(True),
                (ROOT/e['path']).read_text().splitlines(True),fromfile='Candidate03/'+e['path'],tofile='Candidate05/'+e['path']))
        changes.append(row)
assert {e['path'] for e in changes} == {'Source/MeridianSquad/PhysicsControlStepping.cpp','Binaries/Win64/UnrealEditor-MeridianSquad.dll'}
reused = []
for name in ['Slow','Controls','Rifle','ReferenceSpeed','ThreeRendered','Blocked02']:
    record = 'Candidate03-'+name
    data = json.loads((OUT/(record+'.json')).read_text())
    rows = [r for r in data['rows'] if r.get('dummy')]
    first = rows[0]['leg_bones']
    neutral = [a-b for a,b in zip(first['foot_l']['p'],first['foot_r']['p'])]
    spans = []
    steps = {}
    for r in rows:
        s = r['dummy']['step']
        if s['phase'] == 'IDLE':
            continue
        sign = 1 if s['swing_foot'] == 'foot_l' else -1
        span = [sign*(a-b) for a,b in zip(s['destination'],s['plant_target'])]
        error = math.dist(span[:2],neutral[:2]); spans.append(error)
        key = (r['dummy']['epoch'],s['started'])
        if key not in steps:
            actual = r['leg_bones']
            entry_span = [a-b for a,b in zip(actual['foot_l']['p'],actual['foot_r']['p'])]
            entry_error = math.dist(entry_span[:2],neutral[:2])
            # The strike can displace a physical foot slightly before planning.
            # Even actual entry positions stay far below the 8 cm selector;
            # that selector uses the still-neutral committed StandingPose.
            assert s['corrective'] or entry_error < 2, (record,entry_error)
            assert s['geometry_trials'] == 1, (record,s['geometry_trials'])
            assert s['selected_length_cm'] < 39, (record,s['selected_length_cm'])
            steps[key] = dict(corrective=s['corrective'],entry_stance_error_cm=entry_error,length=s['selected_length_cm'])
        assert s['corrective'] or error < 38, (record,error)
    reused.append(dict(record=record,sha256=digest(OUT/(record+'.json')),max_target_stance_error_cm=max(spans,default=0),
                       branches=list(steps.values())))
baseline = ROOT/'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker/Candidate07'
unchanged = []
for e in json.loads((baseline/'manifest.json').read_text()):
    if e['path'].startswith(('Source/', 'Content/')) and digest(ROOT/e['path']) == e['sha256']:
        unchanged.append(dict(path=e['path'],sha256=e['sha256']))
result = dict(candidate03_to_final_changes=changes,reused=reused,unchanged_from_msq97=unchanged,
    rechecked=['torso burst through consecutive adaptive steps', 'mid-step replan and following foot selection', 'closer phase-aligned small/large views'],
    rationale='Only stance-aware subsequent foot choice, a future stance reservation and bounded partial corrective placement changed after Candidate03. Reused episodes start within 2 cm of neutral in actual observations (the committed stance is neutral) or use the explicit corrective branch, finish geometry validation on trial 1 and remain well inside the new reservation. Their first valid target, timing, lift and physics drives are unchanged. Replan/Torso and the closer paired view use final native records.',
    predecessor_reuse=[
        dict(record='MSQ97 Candidate07-OneLeg/TorsoBurstResume',scope='Legacy rifle damage/contact routing, sustained-hit request/progress clock and finite support/effort controller. New geometry/tempo demonstrated by MSQ92; old motion is not proof of adaptive scaling.'),
        dict(record='MSQ97 Candidate06-NoSupportAssist',scope='Unchanged contact feasibility, zero powered drives without support and assistance capacity clamps.'),
        dict(record='MSQ97 Candidate06-LegContactWeak',scope='Unchanged Physics Asset inter-leg contacts, physical fall and living get-up; current blocked-landing record also releases drives.'),
        dict(record='MSQ97 Candidate06-DeathDuring',scope='Unchanged damage/death/get-up assets and terminal drive-release branch; CancelStep additionally clears the new adaptive state, exercised by reset/fall here.')])
name = sys.argv[1] if len(sys.argv) > 1 else 'evidence-applicability01.json'
with (OUT/name).open('x',encoding='utf-8') as stream:
    json.dump(result,stream,indent=2)
print(json.dumps(dict(reused=len(reused),source_diff=[c['path'] for c in changes],unchanged_from_msq97=len(unchanged))))
