"""Reuse the existing extracted-production harness for only mobile/lean boundaries."""
from pathlib import Path
import ast, hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Scripts/CombatAI01/CAIT02'
SCRIPT=Path(__file__).resolve().parent
SRC=ROOT/'Source/MeridianSquad'
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
tree=ast.parse((BASE/'check.py').read_text())
reuse=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='extract' or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='methods' for t in n.targets)]
scope={}; exec(compile(ast.Module(body=reuse,type_ignores=[]),str(BASE/'check.py'),'exec'),scope)
extract=scope['extract']; methods=scope['methods']
methods['EnemyCombatComponent.cpp']+=['EnsureMoveAction','FinishMoveAction','ClearMovement','MuzzleCorridorBlocked','RefreshObstruction','StopCombat','ResetCombat']
methods['EnemyCombatMobile.cpp']=['AdvanceMobile']
methods['EnemyCombatLean.cpp']=['LeanSign','LeanProtected','LeanPoints','LeanSweep','LeanProposal','CaptureLeanPose','AchievedLeanClear','LeanReturned','AdvanceLeanCover']
methods['EnemyCombatNavigation.cpp']=['FollowPath','GroundPoint','WalkSegment']
tag=1
while (OUT/f'checks-{tag:02}.json').exists(): tag+=1
tag=f'{tag:02}'
def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)
adapters=(BASE/'adapters.cpp').read_text()
exec(compile((SCRIPT/'adapt.py').read_text(),str(SCRIPT/'adapt.py'),'exec'))
engine_math=Path('D:/UE_5.8/Engine/Source/Runtime/Core/Public/Math/UnrealMathUtility.h')
interp=extract(engine_math.read_text(encoding='utf-8-sig'),'\ttemplate<typename T1, typename T2 = T1, typename T3 = T2, typename T4 = T3>\n\t[[nodiscard]] static auto FInterpConstantTo(')
adapters=once(adapters,'struct FMath {','constexpr double UE_SMALL_NUMBER=1.e-8;\nstruct FMath {\n'+interp)
header=(SRC/'EnemyCombatComponent.h').read_text(encoding='utf-8-sig')
tuning=extract(header,'struct FEnemyCombatTuning')+';'
declaration=extract(header,'class MERIDIANSQUAD_API UEnemyCombatComponent')+';'
declaration=declaration.replace('class MERIDIANSQUAD_API UEnemyCombatComponent : public UActorComponent','struct UEnemyCombatComponent').replace('private:','public:')
declaration=once(declaration,'    UEnemyCombatComponent();','    UEnemyCombatComponent();\n    WorldAdapter TestWorld; AGASPEnemyFixture Pawn; FVector ActualFeet; bool FreshSight=false; FVector FreshGround{3000,0,0};\n    WorldAdapter* GetWorld() const { return const_cast<WorldAdapter*>(&TestWorld); }\n    const AGASPEnemyFixture* GetOwner()const{return &Pawn;}')
for name in ('tuning','declaration'):
    value=locals()[name]
    value=re.sub(r'UPROPERTY\([^\n]*?\)\s*','',value)
    value=re.sub(r'UFUNCTION\([^\n]*?\)\s*','',value)
    locals()[name]=value.replace('GENERATED_BODY()','')
boundaries=(BASE/'boundaries.cpp').read_text()
boundaries=once(boundaries,'Pawn.Combat=this;', 'Pawn.Combat=this;DecisionTrace=std::make_unique<CombatAI::TraceRing>();')
boundaries=re.sub(r'bool UEnemyCombatComponent::FollowPath[^\n]+\n','',boundaries)
boundaries+='\nbool UEnemyCombatComponent::PlanPath(FVector, float){return false;}\nvoid UEnemyCombatComponent::ContinuePath(){}\nvoid UEnemyCombatComponent::NavigationQuery(FCollisionQueryParams&)const{}\n'
parts=[adapters,tuning,declaration,boundaries];identities=[]
for file,names in methods.items():
    source=(SRC/file).read_text(encoding='utf-8-sig')
    for name in names:
        signature=re.search(r'^[\w :<>*&]+ UEnemyCombatComponent::'+name+r'\(',source,re.M).group(0)
        body=extract(source,signature);parts.append(body)
        identities.append(dict(file=file,method=name,sha256=hashlib.sha256(body.encode()).hexdigest()))
for file,names in {'GASPEnemyRifle.cpp':['GetFireMotion','SetRifleLean'], 'GASPEnemyFixture.cpp':['SetMovementCommand','StopMovementCommand']}.items():
    source=(SRC/file).read_text(encoding='utf-8-sig')
    for name in names:
        signature=re.search(r'^[\w :<>*&]+ AGASPEnemyFixture::'+name+r'\(',source,re.M).group(0)
        body=extract(source,signature);parts.append(body)
        identities.append(dict(file=file,method=name,sha256=hashlib.sha256(body.encode()).hexdigest()))
anim_source=(SRC/'GASPALSRifleAnimInstance.cpp').read_text(encoding='utf-8-sig')
owner=re.search(r'    const bool bRifleOwnsPose = .*;',anim_source).group(0)
start=anim_source.index('    const auto Motion = Enemy->GetFireMotion();')
end=anim_source.index('    const float Ready =',start)
blend=owner+'\n'+anim_source[start:end]
parts.append('float UpdateLean(float RifleLeanDegrees,const AGASPEnemyFixture* Enemy,float DeltaSeconds)\n{\n'+blend+'\nreturn RifleLeanDegrees;\n}')
identities.append(dict(file='GASPALSRifleAnimInstance.cpp',method='NativeUpdateAnimation lean owner and consumer fragment',sha256=hashlib.sha256(blend.encode()).hexdigest()))
identities.append(dict(file=str(engine_math),method='FInterpConstantTo installed engine template',sha256=hashlib.sha256(interp.encode()).hexdigest()))
parts.append((SCRIPT/'tests.cpp').read_text())
generated=OUT/f'generated-{tag}.cpp';generated.write_text('\n\n'.join(parts),encoding='utf-8')
vc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207');sdk=Path('C:/Program Files (x86)/Windows Kits/10')
exe=OUT/f'checks-{tag}.exe'
args=[str(vc/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX','/wd4244','/I'+str(SRC),'/I'+str(vc/'include'),'/I'+str(sdk/'Include/10.0.22621.0/ucrt'),str(generated),'/Fe:'+str(exe),'/Fo:'+str(OUT/f'checks-{tag}.obj'),'/link','/LIBPATH:'+str(vc/'lib/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
build=subprocess.run(args,cwd=OUT,text=True,capture_output=True)
(OUT/f'compile-{tag}.log').write_text(build.stdout+build.stderr,encoding='utf-8')
report=dict(compile_exit=build.returncode,methods=identities,generated_sha256=sha(generated),scope='Extracted real policy, route-following, motion producer, muzzle and lean lifecycle. Engine clock/collision/socket acknowledgement and projectile storage are explicit boundaries; no gameplay or pose simulation.',reused_driver_sha256=sha(BASE/'check.py'),reused_adapters_sha256=sha(BASE/'adapters.cpp'))
if build.returncode==0:
    run=subprocess.run([str(exe)],cwd=OUT,text=True,capture_output=True)
    (OUT/f'run-{tag}.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    report.update(run_exit=run.returncode,output=run.stdout,passed=run.returncode==0)
else: report.update(errors=build.stdout+build.stderr,passed=False)
with (OUT/f'checks-{tag}.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='methods'},indent=2))
raise SystemExit(0 if report['passed'] else 1)
