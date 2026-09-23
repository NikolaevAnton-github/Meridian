"""Compile exact affected production methods against bounded deterministic fixtures."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).resolve().parent
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate03'
SRC=ROOT/'Source/MeridianSquad'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def extract(text, signature):
    start=text.index(signature); end=text.index('{',start)+1; depth=1
    while depth:
        if text[end]=='{': depth+=1
        if text[end]=='}': depth-=1
        end+=1
    return text[start:end]

attempt=1
while (OUT/f'checks-{attempt:02}.json').exists(): attempt+=1
tag=f'{attempt:02}'
methods={
    'EnemyCombatComponent.cpp':['CombatAI::ActionToken UEnemyCombatComponent::EnsureAction(',
        'bool UEnemyCombatComponent::FinishAction(', 'void UEnemyCombatComponent::ClearIntent(',
        'void UEnemyCombatComponent::ChangeState(', 'void UEnemyCombatComponent::SuspendForPhysics(',
        'void UEnemyCombatComponent::SetEnabled('],
    'EnemyCombatSenses.cpp':['void UEnemyCombatComponent::ReceiveStimulus(', 'void UEnemyCombatComponent::ApplyEvidenceIntent('],
    'EnemyCombatPolicy.cpp':['void UEnemyCombatComponent::BeginSearch(', 'void UEnemyCombatComponent::FailTactic(', 'void UEnemyCombatComponent::AdvanceCombat('],
    'EnemyCombatTactics.cpp':['void UEnemyCombatComponent::ResetTactics(', 'FVector UEnemyCombatComponent::TacticalDirection(',
        'UEnemyCombatComponent::FTacticalPosition UEnemyCombatComponent::AssessTacticalPosition(',
        'void UEnemyCombatComponent::AddTacticalCandidate(', 'void UEnemyCombatComponent::BeginTacticalScan(',
        'void UEnemyCombatComponent::AdvanceTacticalScan(', 'void UEnemyCombatComponent::ChooseTacticalPosition(',
        'void UEnemyCombatComponent::RejectTacticalPosition(', 'void UEnemyCombatComponent::SetObservationFacing(',
        'void UEnemyCombatComponent::HoldTacticalPosition(', 'void UEnemyCombatComponent::AdvanceSearch(']}
header=(SRC/'EnemyCombatComponent.h').read_text(encoding='utf-8-sig')
tuning=extract(header,'struct FEnemyCombatTuning')
fields=re.findall(r'UPROPERTY\(EditAnywhere, BlueprintReadWrite\) ([^;]+;)',tuning)
prefix=(SCRIPT/'adapters.cpp').read_text().replace('// @PRODUCTION_TUNING@','\n'.join(fields))
parts=[prefix];identities=[]
for file,signatures in methods.items():
    text=(SRC/file).read_text(encoding='utf-8-sig')
    for signature in signatures:
        body=extract(text,signature);parts.append(body)
        identities.append(dict(file=file,signature=signature,sha256=hashlib.sha256(body.encode()).hexdigest()))
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
report=dict(compile_exit=build.returncode,methods=identities,
    generated_sha256=sha(generated),dll_sha256=sha(ROOT/'Binaries/Win64/UnrealEditor-MeridianSquad.dll'),
    scope='Exact sensing, policy, scan/selection/hold/arrival, action and physical-cancellation methods; production pure headers and tuning. Deterministic geometry/clock/actor boundaries; no engine gameplay or performance evidence.')
checks={'compiled_affected_methods':build.returncode==0}
if build.returncode==0:
    run=subprocess.run([str(exe)],cwd=OUT,text=True,capture_output=True)
    (OUT/f'run-{tag}.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    report.update(run_exit=run.returncode,output=run.stdout)
    checks['affected_regressions_pass']=run.returncode==0
else: report['build_output']=build.stdout+build.stderr
allowed={'CombatAITactics.h','EnemyCombatComponent.h','EnemyCombatSenses.cpp','EnemyCombatTactics.cpp','EnemyCombatPolicy.cpp'}
changed=[row['path'] for row in read(OUT/'source-before.json') if sha(ROOT/row['path'])!=row['sha256']]
checks['bounded_native_delta']=set(Path(n).name for n in changed)==allowed
for name in ('previous','historical','owner'):
    rows=read(OUT/f'{name}-preservation-before.json')
    checks[name+'_preserved']=all(sha(ROOT/row['path'])==row['sha256'] for row in rows)
with zipfile.ZipFile(OUT.parent/'Candidate02/CAI02-Candidate02-frozen.zip') as previous:
    for file,signatures in {
        'EnemyCombatComponent.cpp':['bool UEnemyCombatComponent::TryObservePlayer(', 'bool UEnemyCombatComponent::CanShoot(', 'bool UEnemyCombatComponent::Fire(', 'void UEnemyCombatComponent::SuspendForPhysics('],
        'EnemyCombatTactics.cpp':['bool UEnemyCombatComponent::TacticalGround(', 'bool UEnemyCombatComponent::TacticalWalk(', 'bool UEnemyCombatComponent::TacticalRoute(', 'void UEnemyCombatComponent::ResetTactics('],
    }.items():
        before=previous.read('Source/MeridianSquad/'+file).decode('utf-8-sig').replace('\r\n','\n')
        after=(SRC/file).read_text(encoding='utf-8-sig')
        for signature in signatures:
            checks['retained_'+signature.split('::')[-1].rstrip('(')]=extract(before,signature)==extract(after,signature)
    for file in ('EnemyCombatNavigation.cpp','CombatAISenses.h','CombatStimulusWorld.cpp','CombatProjectileWorld.cpp','CombatProjectileWorld.h',
        'CombatLocomotionAnimInstance.cpp','CombatLocomotionAnimInstance.h','CombatAIAction.h','CombatAIObservation.h','GASPEnemyRifle.cpp'):
        checks['retained_'+file]=previous.read('Source/MeridianSquad/'+file)==(SRC/file).read_bytes()
    old_header=previous.read('Source/MeridianSquad/EnemyCombatComponent.h').decode('utf-8-sig').replace('\r\n','\n')
    checks['all_tuning_unchanged']=tuning==extract(old_header,'struct FEnemyCombatTuning')
    old_policy=previous.read('Source/MeridianSquad/EnemyCombatPolicy.cpp').decode('utf-8-sig').replace('\r\n','\n')
    new_policy=(SRC/'EnemyCombatPolicy.cpp').read_text(encoding='utf-8-sig')
    checks['policy_only_moves_standing_request']=new_policy.replace(
        '    // Contact requests standing even when backoff postpones engagement. Mover\n'
        '    // may refuse it under geometry; actual head/muzzle probes remain authoritative.\n'
        '    E->SetCrouchCommand(false);\n','').replace('    E->SetRifleAimTarget(LastKnownAim);\n    if (!E->IsRifleHeld()',
        '    E->SetRifleAimTarget(LastKnownAim); E->SetCrouchCommand(false);\n    if (!E->IsRifleHeld()')==old_policy
report.update(checks=checks,changed_source=changed,passed=all(checks.values()))
with (OUT/f'checks-{tag}.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='methods'},indent=2))
raise SystemExit(0 if report['passed'] else 1)
