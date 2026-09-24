"""Compile exact production producers, geometry and lifecycle against deterministic adapters.

No Unreal world, gameplay, simulation or firing probe is run. Extracted methods
are byte identified; adapters replace engine boundaries, not the tested policy.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).resolve().parent
OUT=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate01'
SRC=ROOT/'Source/MeridianSquad'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(text, signature):
    start=text.index(signature);end=text.index('{',start)+1;depth=1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return text[start:end]
tag=1
while (OUT/f'checks-{tag:02}.json').exists():tag+=1
tag=f'{tag:02}'
header=(SRC/'EnemyCombatComponent.h').read_text(encoding='utf-8-sig')
tuning=extract(header,'struct FEnemyCombatTuning')+';'
declaration=extract(header,'class MERIDIANSQUAD_API UEnemyCombatComponent')+';'
declaration=declaration.replace('class MERIDIANSQUAD_API UEnemyCombatComponent : public UActorComponent','struct UEnemyCombatComponent').replace('private:','public:')
declaration=declaration.replace('    UEnemyCombatComponent();','    UEnemyCombatComponent();\n    WorldAdapter TestWorld; AGASPEnemyFixture Pawn; FVector ActualFeet; bool FreshSight=false; FVector FreshGround{1000,0,0}; int FollowCalls=0; bool FollowSucceeds=true;\n    WorldAdapter* GetWorld() const { return const_cast<WorldAdapter*>(&TestWorld); }')
for textname in ('tuning','declaration'):
    text=locals()[textname]
    text=re.sub(r'UPROPERTY\([^\n]*?\)\s*','',text)
    text=re.sub(r'UFUNCTION\([^\n]*?\)\s*','',text)
    text=text.replace('GENERATED_BODY()','')
    locals()[textname]=text
parts=[(SCRIPT/'adapters.cpp').read_text(),tuning,declaration,(SCRIPT/'boundaries.cpp').read_text()]
methods={
    'EnemyCombatComponent.cpp':['EnsureAction','FinishAction','ClearIntent','ChangeState','SetEnabled','SuspendForPhysics','ObservePlayer','CanShoot','Fire'],
    'EnemyCombatPolicy.cpp':['BeginSearch','FailTactic','AdvanceWeapon','AdvanceCombat'],
    'EnemyCombatCover.cpp':['WeaponProfile','ReceiveTargetHealth','RefreshTacticalContext','PoseCapsuleSize','CoverCapsule','CoverWalk','RefreshCoverThreat','CoverProtected','CoverLane','AssessCoverOption','AssessCoverOptions','ResetCover','AdvanceCoverScan','ChooseCover','SetCoverPhase','StartCoverMove','ReturnToCover','FailCoverReturn','AdvanceCover'],
    'EnemyCombatTactics.cpp':['ResetTactics','TacticalDirection','TacticalTrace','TacticalGround','TacticalWalk','TacticalRoute','AssessTacticalPosition','AddTacticalCandidate','BeginTacticalScan','AdvanceTacticalScan','ChooseTacticalPosition','RejectTacticalPosition','SetObservationFacing','HoldTacticalPosition','AdvanceSearch'],
    'EnemyCombatSenses.cpp':['ReceiveStimulus','ApplyEvidenceIntent']}
identities=[]
for file,names in methods.items():
    source=(SRC/file).read_text(encoding='utf-8-sig')
    for name in names:
        signature=re.search(r'^[\w :<>*&]+ UEnemyCombatComponent::'+name+r'\(',source,re.M).group(0)
        body=extract(source,signature)
        parts.append(body);identities.append(dict(file=file,method=name,sha256=hashlib.sha256(body.encode()).hexdigest()))
parts.append((SCRIPT/'tests.cpp').read_text())
generated=OUT/f'generated-{tag}.cpp';generated.write_text('\n\n'.join(parts),encoding='utf-8')
vc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
sdk=Path('C:/Program Files (x86)/Windows Kits/10')
exe=OUT/f'checks-{tag}.exe'
args=[str(vc/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX','/wd4244',
    '/I'+str(SRC),'/I'+str(vc/'include'),'/I'+str(sdk/'Include/10.0.22621.0/ucrt'),str(generated),
    '/Fe:'+str(exe),'/Fo:'+str(OUT/f'checks-{tag}.obj'),'/link','/LIBPATH:'+str(vc/'lib/x64'),
    '/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
build=subprocess.run(args,cwd=OUT,text=True,capture_output=True)
(OUT/f'compile-{tag}.log').write_text(build.stdout+build.stderr,encoding='utf-8')
report=dict(compile_exit=build.returncode,methods=identities,generated_sha256=sha(generated),scope='Extracted production source; deterministic clock, collision, actor and launch boundaries. No game execution or performance evidence.')
checks={'compiled_production_methods':build.returncode==0}
if build.returncode==0:
    run=subprocess.run([str(exe)],cwd=OUT,text=True,capture_output=True)
    (OUT/f'run-{tag}.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    report.update(run_exit=run.returncode,output=run.stdout);checks['behavior']=run.returncode==0
else:report['errors']=build.stdout+build.stderr
for name in ('owner','historical'):
    rows=json.loads((OUT/f'{name}-preservation-before.json').read_text())
    # Controller-owned docs may evolve during the worker. Assets/config must not.
    required=[r for r in rows if name=='historical' or r['path'] in ('Config/DefaultEngine.ini','MeridianSquad.uproject','Content/Maps/L_OpeningLobby_PainterStone01.umap')]
    checks[name+'_preserved']=all(sha(ROOT/r['path'])==r['sha256'] for r in required)
unchanged=['GASPEnemyFixture.cpp','GASPEnemyFixture.h','GASPEnemyRifle.cpp','CombatProjectileWorld.cpp','CombatProjectileWorld.h','CombatRifleComponent.cpp','CombatAISenses.h','CombatStimulusWorld.cpp']
rows=json.loads((OUT/'source-before.json').read_text())
checks['retained_physics_player_projectile_senses']=all(sha(ROOT/r['path'])==r['sha256'] for r in rows if Path(r['path']).name in unchanged)
with zipfile.ZipFile(ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate03/CAI02-Candidate03-frozen.zip') as z:
    before=z.read('Source/MeridianSquad/EnemyCombatComponent.cpp').decode('utf-8-sig').replace('\r\n','\n')
    after=(SRC/'EnemyCombatComponent.cpp').read_text(encoding='utf-8-sig')
    checks['unchanged_success_only_sight_producer']=extract(before,'bool UEnemyCombatComponent::TryObservePlayer(')==extract(after,'bool UEnemyCombatComponent::TryObservePlayer(')
report.update(checks=checks,passed=all(checks.values()))
with (OUT/f'checks-{tag}.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='methods'},indent=2))
raise SystemExit(0 if report['passed'] else 1)
