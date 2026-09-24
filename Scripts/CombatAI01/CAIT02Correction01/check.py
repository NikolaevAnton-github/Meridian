"""Reuse CAIT02 extraction/adapters; run only R1/R2 and directly affected boundaries."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Scripts/CombatAI01/CAIT02'
SCRIPT=Path(__file__).resolve().parent
SRC=ROOT/'Source/MeridianSquad'
OUT=ROOT/'Saved/CombatAI01/CAI-T02/Worker/Candidate02'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
# Reuse the original extractor and its production method selection without
# executing its Candidate01 writer or its already passing 71-case entry point.
tree=ast.parse((BASE/'check.py').read_text())
reuse=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='extract' or
       isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='methods' for t in n.targets)]
scope={}
exec(compile(ast.Module(body=reuse,type_ignores=[]),str(BASE/'check.py'),'exec'),scope)
extract=scope['extract']; methods=scope['methods']
methods['EnemyCombatComponent.cpp'] += ['MuzzleCorridorBlocked','RefreshObstruction']
tag=1
while (OUT/f'checks-{tag:02}.json').exists(): tag+=1
tag=f'{tag:02}'
def replace_once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)

adapters=(BASE/'adapters.cpp').read_text()
adapters=replace_once(adapters,'struct UCharacterMoverComponent{UStanceSettings Settings;',
    '''struct UCharacterMoverComponent{UStanceSettings Settings;
    bool bWantsToCrouch=false; bool* Achieved=nullptr;
    bool CanCrouch(); void Crouch(); void UnCrouch();
    bool IsCrouching()const{return Achieved && *Achieved;}
    // Explicit engine boundary: acknowledge/refuse the real Mover request.
    // Collision/modifier application and animation are not executed here.
    void Acknowledge(bool CanExpand=true,bool CanEnter=true){
        if (!Achieved) return;
        if (*Achieved && !bWantsToCrouch && CanExpand) *Achieved=false;
        else if (!*Achieved && bWantsToCrouch && CanEnter) *Achieved=true;
    }
''')
adapters=replace_once(adapters,'APawn Data;APawn* Foundation=&Data;',
    'APawn Data;APawn* Foundation=&Data;UCharacterMoverComponent* Mover=&Data.Mover;void ConsumeRifleStance();')
adapters=replace_once(adapters,'bool IsMovementCrouched()const{return ActualCrouch;}',
    'bool IsMovementCrouched() const;')
boundaries=(BASE/'boundaries.cpp').read_text()
boundaries=replace_once(boundaries,'Pawn.Combat=this;', 'Pawn.Combat=this;Pawn.Data.Mover.Achieved=&Pawn.ActualCrouch;')
header=(SRC/'EnemyCombatComponent.h').read_text(encoding='utf-8-sig')
tuning=extract(header,'struct FEnemyCombatTuning')+';'
declaration=extract(header,'class MERIDIANSQUAD_API UEnemyCombatComponent')+';'
declaration=declaration.replace('class MERIDIANSQUAD_API UEnemyCombatComponent : public UActorComponent','struct UEnemyCombatComponent').replace('private:','public:')
declaration=replace_once(declaration,'    UEnemyCombatComponent();',
    '    UEnemyCombatComponent();\n    WorldAdapter TestWorld; AGASPEnemyFixture Pawn; FVector ActualFeet; bool FreshSight=false; FVector FreshGround{1000,0,0}; int FollowCalls=0; bool FollowSucceeds=true;\n    WorldAdapter* GetWorld() const { return const_cast<WorldAdapter*>(&TestWorld); }')
for name in ('tuning','declaration'):
    value=locals()[name]
    value=re.sub(r'UPROPERTY\([^\n]*?\)\s*','',value)
    value=re.sub(r'UFUNCTION\([^\n]*?\)\s*','',value)
    locals()[name]=value.replace('GENERATED_BODY()','')
parts=[adapters,tuning,declaration,boundaries]
identities=[]
def add_body(path,name,body,kind='production_method'):
    parts.append(body)
    identities.append(dict(file=str(path),method=name,sha256=hashlib.sha256(body.encode()).hexdigest(),kind=kind))
for file,names in methods.items():
    source=(SRC/file).read_text(encoding='utf-8-sig')
    for name in names:
        signature=re.search(r'^[\w :<>*&]+ UEnemyCombatComponent::'+name+r'\(',source,re.M).group(0)
        add_body('Source/MeridianSquad/'+file,name,extract(source,signature))
rifle=(SRC/'GASPEnemyRifle.cpp').read_text(encoding='utf-8-sig')
add_body('Source/MeridianSquad/GASPEnemyRifle.cpp','IsMovementCrouched',extract(rifle,'bool AGASPEnemyFixture::IsMovementCrouched() const'))
# Compile the exact engine-facing branch of UpdateRifleInput. Unrelated reflected
# aim/controller input remains outside this bounded stance-consumer check.
consumer=extract(rifle,'void AGASPEnemyFixture::UpdateRifleInput()')
locomotion=re.search(r'    const bool bLocomotion = .*;',consumer).group(0)
branch=extract(consumer,'    if (auto* CharacterMover = Cast<UCharacterMoverComponent>(Mover))')
parts.append('void AGASPEnemyFixture::ConsumeRifleStance()\n{\n'+locomotion+'\n'+branch+'\n}')
identities.append(dict(file='Source/MeridianSquad/GASPEnemyRifle.cpp',method='UpdateRifleInput stance consumer',
    kind='exact_consumer_fragment',sha256=hashlib.sha256((locomotion+'\n'+branch).encode()).hexdigest()))
engine=Path('D:/UE_5.8/Engine/Plugins/Experimental/Mover/Source/Mover/Private/DefaultMovementSet/CharacterMoverComponent.cpp')
native=engine.read_text(encoding='utf-8-sig')
for name,ret in [('CanCrouch','bool'),('Crouch','void'),('UnCrouch','void')]:
    add_body(engine.as_posix(),name,extract(native,ret+' UCharacterMoverComponent::'+name+'()'),'installed_engine_method')
old_tests=(BASE/'tests.cpp').read_text()
parts.append(replace_once(old_tests,'int main()', 'int Candidate01ChecksNotRun()'))
parts.append((SCRIPT/'tests.cpp').read_text())
generated=OUT/f'generated-{tag}.cpp'
generated.write_text('\n\n'.join(parts),encoding='utf-8')
vc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
sdk=Path('C:/Program Files (x86)/Windows Kits/10')
exe=OUT/f'checks-{tag}.exe'
args=[str(vc/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX','/wd4244',
    '/I'+str(SRC),'/I'+str(vc/'include'),'/I'+str(sdk/'Include/10.0.22621.0/ucrt'),str(generated),
    '/Fe:'+str(exe),'/Fo:'+str(OUT/f'checks-{tag}.obj'),'/link','/LIBPATH:'+str(vc/'lib/x64'),
    '/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
build=subprocess.run(args,cwd=OUT,text=True,capture_output=True)
(OUT/f'compile-{tag}.log').write_text(build.stdout+build.stderr,encoding='utf-8')
report=dict(compile_exit=build.returncode,methods=identities,generated_sha256=sha(generated),
    scope='Only CFT02-R1/R2 and affected consumers/transitions; exact production extraction, real stance-consumer fragment and installed Mover request methods. Achieved modifier/stance and motion remain explicit engine boundaries. No game execution.',
    reused_driver_sha256=sha(BASE/'check.py'), reused_adapters_sha256=sha(BASE/'adapters.cpp'), reused_boundaries_sha256=sha(BASE/'boundaries.cpp'))
if build.returncode==0:
    run=subprocess.run([str(exe)],cwd=OUT,text=True,capture_output=True)
    (OUT/f'run-{tag}.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    report.update(run_exit=run.returncode,output=run.stdout,passed=run.returncode==0)
else: report.update(errors=build.stdout+build.stderr,passed=False)
with (OUT/f'checks-{tag}.json').open('x',encoding='utf-8') as stream: json.dump(report,stream,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='methods'},indent=2))
raise SystemExit(0 if report['passed'] else 1)
