"""Record why earlier runtime evidence applies to the final diagnostic revision."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'
old=json.loads((OUT/'Candidate03/manifest.json').read_text())
same=[];changed=[]
for row in old:
    name=row['path']
    if not name.startswith(('Source/','Content/')):continue
    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==row['sha256']:
        same.append(name)
    else:changed.append(name)
assert changed==['Source/MeridianSquad/PhysicsControlDummy.cpp'],changed
name=changed[0]
a=(OUT/'Candidate03'/name).read_text()
b=(ROOT/name).read_text()
prefix='FString APhysicsControlDummy::GetDummyState(bool IncludeContacts) const'
suffix='void APhysicsControlDummy::EndPlay('
assert a.split(prefix)[0]==b.split(prefix)[0]
assert a.split(suffix)[1]==b.split(suffix)[1]
result=dict(task='MSQ-87',from_candidate='Candidate03',to_candidate='Candidate05',
    unchanged_native_and_assets=same,changed_native=changed,
    change_scope='Only the read-only GetDummyState diagnostic body changed. The two animation assets, all balance/probe behavior and every other candidate native file have identical SHA-256.',
    visual_supplements='Candidate04 adds a visible wireframe ceiling, falling camera follow and clear six-fixture overview; these are PIE-only capture configurations. Candidate05-JointAnchors validates the final native diagnostic.',
    applicable=['Candidate03-Core','Candidate03-LegInterruptedDeath','Candidate03-FrontSlow','Candidate03-Unsupported','Candidate04-BlockedAndAnchors','Candidate04-UnsupportedView','Candidate04-SixRendered'],
    passed=True)
path=OUT/'evidence-reuse01.json';assert not path.exists()
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
diff=OUT/'Candidate03-to-Candidate05-diagnostics.patch';assert not diff.exists()
diff.write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='Candidate03/'+name,tofile='Candidate05/'+name)),encoding='utf-8')
print(json.dumps(dict(passed=True,unchanged_files=len(same),changed=changed)))
