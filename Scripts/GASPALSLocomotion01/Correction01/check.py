"""Reuse the project's exact-source extractor and MSVC runner; only R1/R2 seams.

The C++ boundaries are plain data and prerecorded contact/query responses.
No Unreal world, actor tick, physics, firing or gameplay simulation is started.
"""
from pathlib import Path
import ast,hashlib,json,re,subprocess,sys
from prepare import ROOT,OUT,sha
BASE=ROOT/'Scripts/CombatAI01/CAIT02'
tree=ast.parse((BASE/'check.py').read_text())
scope={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='extract'],type_ignores=[]),str(BASE/'check.py'),'exec'),scope)
extract=scope['extract']
SCRIPT=Path(__file__).resolve().parent
SRC=ROOT/'Source/MeridianSquad'
kind=sys.argv[1]
identities=[]
def take(file,signature):
    path=SRC/file if not str(file).startswith('D:') else Path(file)
    body=extract(path.read_text(encoding='utf-8-sig'),signature)
    identities.append(dict(file=str(path),signature=signature,sha256=hashlib.sha256(body.encode()).hexdigest()))
    return body
def fragment(body,start,end,name):
    result=body[body.index(start):body.index(end,body.index(start))]
    identities.append(dict(fragment=name,sha256=hashlib.sha256(result.encode()).hexdigest()))
    return result

base=(BASE/'adapters.cpp').read_text()
if kind=='routing':
    common=base[:base.index('template<class A,class B>struct TMap')]
    common=common.replace('static double Abs','static double Sqrt(double V){return std::sqrt(V);}\n    template<class T>static T Square(T V){return V*V;}\n    static double Abs')
    common=common.replace('static double Dist2D','static double DistSquared(FVector A,FVector B){return (A-B).SizeSquared();}\n    static double Distance(FVector A,FVector B){return std::sqrt(DistSquared(A,B));}\n    static double Dist2D')
    common=common.replace('void Add(const T& V){this->push_back(V);}',
        'void Add(const T& V){this->push_back(V);}template<class F>void Sort(F Fn){std::sort(this->begin(),this->end(),Fn);}')
    parts=[common,(SCRIPT/'routing_boundaries.cpp').read_text()]
    for signature in ['const APhysicsControlDummy* PhysicalProjectileOwner(', 'bool UsesProjectileCapsule(',
        'bool SameProjectileBody(', 'double CapsuleDistanceSquared(', 'bool CapsuleContact(',
        'TMap<TWeakObjectPtr<ACharacter>, ACombatProjectileWorld::FCapsuleSample> ACombatProjectileWorld::SampleCapsules() const',
        'void ACombatProjectileWorld::RecordCapsules()']:
        parts.append(take('CombatProjectileWorld.cpp',signature))
    parts.append(take('PhysicsControlDummyWorld.cpp','TMap<TWeakObjectPtr<APhysicsControlDummy>, FDummyPose> ACombatProjectileWorld::SampleDummies() const'))
    advance=take('CombatProjectileWorld.cpp','void ACombatProjectileWorld::AdvanceSegment(')
    loops=fragment(advance,'        for (const auto& Entry : EndCapsules)','        if (bHit)','exact capsule and skeletal arbitration loops')
    parts.append('bool Arbitrate(ACombatProjectileWorld& W,BulletData& Bullet,const FVector& Start,const FVector& End,FHitResult& Hit,bool bHit=false) {\n'
        'using FCapsuleSample=ACombatProjectileWorld::FCapsuleSample;\n'
        'const auto& StartCapsules=W.PreviousCapsules;const auto EndCapsules=W.CachedCapsules;\n'
        'const auto& StartDummies=W.PreviousDummies;const auto EndDummies=W.CachedDummies;\n'
        'double Earliest=bHit ? Hit.Time : 2.0;\n'+loops+'\nreturn bHit;\n}')
    launch=take('CombatProjectileWorld.cpp','int64 ACombatProjectileWorld::LaunchTimed(')
    clearance=fragment(launch,'    const auto* PhysicalShooter =','    Bullets.Add(Bullet);','exact physical launch-clearance branch')
    parts.append('void LaunchClearance(AActor* Shooter,FVector Position,BulletData& Bullet) {\n'+clearance+'\n}')
    resolve=take('CombatProjectileWorld.cpp','void ACombatProjectileWorld::ResolveHit(')
    damage=fragment(resolve,'    const float Applied =','    if (Generation !=','exact single damage dispatch expression')
    parts.append('float Dispatch(const BulletData& Bullet,const FHitResult& Hit) {\n'
        'auto* Victim=Hit.GetActor();auto* PhysicalTarget=Cast<APhysicsControlDummy>(Victim);double LastContactTime=.2;uint64 FrameSerial=1;\n'+damage+'return Applied;\n}')
    ordered=fragment(advance,'    PendingHits.Sort','    const uint64 Generation','exact contact-time and shot-id ordering')
    parts.append('struct FPendingHit { BulletData Bullet; FHitResult Hit; double Time; };\n'
        'void Order(TArray<FPendingHit>& PendingHits) {\n'+ordered+'\n}')
    parts.append((SCRIPT/'routing_tests.cpp').read_text())
elif kind=='geometry':
    common=base.replace('template<class T,class U>T* Cast(U* P){return reinterpret_cast<T*>(P);}',
        'template<class T,class U>auto Cast(U* P){using R=std::conditional_t<std::is_const_v<U>,const T*,T*>;return dynamic_cast<R>(P);}')
    common=common.replace('static double Abs','template<class T>static T Max3(T A,T B,T C){return std::max({A,B,C});}\n    static double Abs')
    start=common.index('struct UCapsuleComponent{')
    end=common.index('struct UGASPALSRifleAnimInstance{')
    common=common[:start]+(SCRIPT/'geometry_boundaries.cpp').read_text()+common[end:]
    # Instrument the retained collision boundary, not the production consumers.
    common=common.replace('double Now=1;','int Overlaps=0,Sweeps=0;double LastRadius=0,LastHeight=0; bool Block=false;\n    double Now=1;')
    common=common.replace('return Trace(H,A,B,ECC_Pawn,{S.Radius,S.Radius,S.Height});','++Sweeps;LastRadius=S.Radius;LastHeight=S.Height;if(Block)return true;return Trace(H,A,B,ECC_Pawn,{S.Radius,S.Radius,S.Height});')
    common=common.replace('FHitResult H;return Trace(H,A,A,ECC_Pawn,{S.Radius,S.Radius,S.Height});','++Overlaps;LastRadius=S.Radius;LastHeight=S.Height;if(Block)return true;FHitResult H;return Trace(H,A,A,ECC_Pawn,{S.Radius,S.Radius,S.Height});')
    parts=[common,(SCRIPT/'geometry_consumer.cpp').read_text()]
    for file,names in {'EnemyCombatCover.cpp':['PoseCapsuleSize','CoverCapsule','CoverWalk'],
        'EnemyCombatTactics.cpp':['TacticalTrace','TacticalGround','TacticalWalk'],
        'EnemyCombatNavigation.cpp':['CapsuleSize']}.items():
        source=(SRC/file).read_text(encoding='utf-8-sig')
        for name in names:
            signature=re.search(r'^[\w :<>*&]+ UEnemyCombatComponent::'+name+r'\(',source,re.M).group(0)
            parts.append(take(file,signature))
    # Source-default values are reused from frozen asset evidence, not guessed.
    evidence=json.loads((ROOT/'Saved/GASPALSLocomotion01/Worker/Candidate01/Evidence/asset-checks-02.json').read_text())
    source=json.loads((ROOT/'Saved/GASPALSLocomotion01/Worker/Candidate01/Evidence/SourceGraph/CBP_SandboxCharacter.json').read_text())
    radius=float(source['capsule_defaults'].get('CapsuleRadius',source['capsule_defaults'].get('capsule_radius')))
    height=float(source['capsule_defaults'].get('CapsuleHalfHeight',source['capsule_defaults'].get('capsule_half_height')))
    crouch=float(evidence['child_movement_defaults']['CrouchedHalfHeight'])
    parts.append(f'constexpr float SourceRadius={radius}f,SourceStanding={height}f,SourceCrouch={crouch}f;')
    parts.append((SCRIPT/'geometry_tests.cpp').read_text())
else:raise ValueError(kind)

tag=1
while (OUT/f'{kind}-{tag:02}.json').exists():tag+=1
stem=f'{kind}-{tag:02}'
generated=OUT/(stem+'.cpp');generated.write_text('\n\n'.join(parts))
vc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
sdk=Path('C:/Program Files (x86)/Windows Kits/10')
exe=OUT/(stem+'.exe')
args=[str(vc/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX','/wd4244',
    '/I'+str(SRC),'/I'+str(vc/'include'),'/I'+str(sdk/'Include/10.0.22621.0/ucrt'),str(generated),
    '/Fe:'+str(exe),'/Fo:'+str(OUT/(stem+'.obj')),'/link','/LIBPATH:'+str(vc/'lib/x64'),
    '/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
build=subprocess.run(args,cwd=OUT,text=True,capture_output=True)
(OUT/(stem+'-compile.log')).write_text(build.stdout+build.stderr)
report=dict(kind=kind,compile_exit=build.returncode,source=identities,generated_sha256=sha(generated),
    extractor_sha256=sha(BASE/'check.py'),geometry_boundary_sha256=sha(BASE/'adapters.cpp'),
    scope='Pure extracted production routing/arbitration or proposed geometry consumers. Actors, traced contact data and geometry query responses are explicit test boundaries; no Unreal world, gameplay or firing.')
if build.returncode==0:
    run=subprocess.run([str(exe)],cwd=OUT,text=True,capture_output=True)
    report.update(run_exit=run.returncode,output=run.stdout+run.stderr,passed=run.returncode==0)
else:report.update(passed=False,errors=build.stdout+build.stderr)
with (OUT/(stem+'.json')).open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='source'}))
raise SystemExit(0 if report['passed'] else 1)
