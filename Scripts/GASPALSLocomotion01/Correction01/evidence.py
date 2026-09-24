"""Record only changed integration call sites and unchanged lifecycle evidence."""
from pathlib import Path
import ast,difflib,json,zipfile
from prepare import ROOT,OUT,sha
base=ROOT/'Scripts/CombatAI01/CAIT02/check.py'
tree=ast.parse(base.read_text());scope={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='extract'],type_ignores=[]),str(base),'exec'),scope)
extract=scope['extract']
src=ROOT/'Source/MeridianSquad'
changed=['CombatProjectileWorld.cpp','EnemyCombatCover.cpp']
with zipfile.ZipFile(OUT/'before.zip') as z:
    previous={p:z.read('Source/MeridianSquad/'+p).decode('utf-8-sig').replace('\r\n','\n') for p in changed}
current={p:(src/p).read_text(encoding='utf-8-sig') for p in changed}
diff=''.join(''.join(difflib.unified_diff(previous[p].splitlines(True),current[p].splitlines(True),fromfile='Candidate01/'+p,tofile='Candidate02/'+p)) for p in changed)
(OUT/'production-correction.diff').write_text(diff)
unchanged={}
for signature in ['void ACombatProjectileWorld::BuildQuery(', 'TMap<TWeakObjectPtr<ACharacter>, ACombatProjectileWorld::FCapsuleSample> ACombatProjectileWorld::CapsulesAt(',
    'void ACombatProjectileWorld::ClearProjectiles()', 'void ACombatProjectileWorld::ResetTargets()', 'void ACombatProjectileWorld::AdvanceFrame(']:
    unchanged[signature]=extract(previous['CombatProjectileWorld.cpp'],signature)==extract(current['CombatProjectileWorld.cpp'],signature)
assert all(unchanged.values()),unchanged
snippets=[]
for file,words in {
    'CombatProjectileWorld.cpp':['PhysicalProjectileOwner','UsesProjectileCapsule','SameProjectileBody','void ACombatProjectileWorld::ResolveHit','void ACombatProjectileWorld::ResetTargets'],
    'PhysicsControlDummy.cpp':['FDummyPose APhysicsControlDummy::SamplePhysicalPose','bool APhysicsControlDummy::TracePhysicalPose'],
    'PhysicsControlDummyWorld.cpp':['SampleDummies() const','DummiesAt(double Time) const'],
    'EnemyCombatCover.cpp':['PoseCapsuleSize','CoverCapsule'],
    'EnemyCombatMobile.cpp':['TacticalGround(Proposed','TacticalWalk(Start'],
    'EnemyCombatTactics.cpp':['PoseCapsuleSize','OverlapAnyTestByObjectType','SweepSingleByObjectType']}.items():
    path=src/file;lines=path.read_text().splitlines()
    snippets.append(f'FILE {file} SHA256 {sha(path)}\n')
    chosen=set()
    for i,line in enumerate(lines):
        if any(word in line for word in words):chosen.update(range(max(0,i-2),min(len(lines),i+20)))
    snippets.extend(f'{i+1}: {lines[i]}\n' for i in sorted(chosen))
engine=[]
for file,start,end in [
    ('D:/UE_5.8/Engine/Source/Runtime/Engine/Private/Components/CharacterMovementComponent.cpp',3293,3301),
    ('D:/UE_5.8/Engine/Source/Runtime/Engine/Private/Components/CharacterMovementComponent.cpp',3480,3482),
    ('D:/UE_5.8/Engine/Source/Runtime/Engine/Classes/Components/CapsuleComponent.h',202,210)]:
    p=Path(file);lines=p.read_text(encoding='utf-8-sig').splitlines()
    engine.append(dict(path=file,sha256=sha(p),lines=[f'{i+1}: {lines[i]}' for i in range(start-1,end)]))
(OUT/'affected-source-excerpts.txt').write_text(''.join(snippets))
(OUT/'source-contract-check.json').write_text(json.dumps(dict(unchanged_lifecycle=unchanged,installed_engine=engine,
    reused_graph_count=1172,graph_count_evidence='Saved/GASPALSLocomotion01/Review/technical-evidence.json',
    notes=['Exact production methods/fragments are compiled by check.py; excerpts connect the active consumers.',
        'Physical tracer, reset/epoch and frame scheduling are retained; no broad replay or game simulation performed.']),indent=2))
print(json.dumps(dict(unchanged_lifecycle=len(unchanged),source_diff=str(OUT/'production-correction.diff'),passed=True)))
