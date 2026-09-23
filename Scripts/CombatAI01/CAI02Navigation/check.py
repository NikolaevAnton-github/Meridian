"""Affected CAI-02 navigation checks; reuse CAIT01 adapters and frozen evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(__file__).resolve().parent
OUT = ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate02'
PREVIOUS = OUT.parent/'Candidate01'
SRC = ROOT/'Source/MeridianSquad'
sys.path.insert(0, str(ROOT/'Scripts/CombatAI01/CAIT01'))
from check_correction import extract


def read(path):
    return path.read_text(encoding='utf-8-sig')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text, old, new):
    assert text.count(old)==1, old
    return text.replace(old,new,1)


def run(label):
    report_path=OUT/f'checks-{label}.json'
    assert not report_path.exists(), 'Use a new attempt label'
    original_prefix=read(ROOT/'Scripts/CombatAI01/CAIT01/correction_prefix.cpp')
    prefix=original_prefix
    prefix=replace_once(prefix, 'bool operator==(const FVector&) const = default;', '''
    FVector operator-(FVector B) const { return {X-B.X,Y-B.Y,Z-B.Z}; }
    FVector GetSafeNormal2D() const { const float L=std::hypot(X,Y); return L>0 ? FVector(X/L,Y/L,0) : FVector{}; }
    static float DotProduct(FVector A,FVector B) { return A.X*B.X+A.Y*B.Y+A.Z*B.Z; }
    bool operator==(const FVector&) const = default;''')
    prefix=replace_once(prefix, 'int Num() const {', 'bool IsValidIndex(int I) const { return I>=0 && I<Num(); }\n    int Num() const {')
    prefix=replace_once(prefix, 'struct FPlatformTime { static double Seconds() { return 0; } };',
        'struct FPlatformTime { inline static double Now=0,Step=0; static double Seconds() { Now+=Step; return Now; } };')
    prefix=replace_once(prefix, 'enum class EGASPALSRifleStance', read(SCRIPT/'navigation_adapters.cpp')+'\nenum class EGASPALSRifleStance')
    prefix=replace_once(prefix, 'FVector Aim;', '''FVector Aim;
    bool Dead=false,bCrouchCommand=false,RequestedWalk=false;
    int MovementCalls=0;
    EGASPEnemyAuthority Authority=EGASPEnemyAuthority::Locomotion;
    bool IsDead() const { return Dead; }
    void SetMovementCommand(FVector,bool Walk) { Stopped=false; ++MovementCalls; RequestedWalk=Walk; }''')

    header=read(SRC/'EnemyCombatComponent.h')
    tuning=re.findall(r'UPROPERTY\(EditAnywhere, BlueprintReadWrite\) ((?:float|int32) \w+ = [^;]+;)', header)
    tuning_body=extract(prefix,'struct TuningValues')
    prefix=replace_once(prefix,tuning_body,'struct TuningValues {\n'+ '\n'.join(tuning)+'\n}')
    prefix=replace_once(prefix,'WorldAdapter World;', '''WorldAdapter World;
    NavigationCollision Collision;
    CombatAI::ResponseGates Gates;
    CombatAI::ActionToken ReloadRequest;
    CombatAI::PathOutcome LastPathOutcome=CombatAI::PathOutcome::None;
    int PathFailures=0,FailedAttempts=0,BurstRemaining=0;
    double NextRepath=0;
    bool bRequestedWalk=false;''')
    ground=extract(prefix,'bool GroundPoint(')
    prefix=replace_once(prefix,ground,'''bool GroundPoint(FVector Reference,FVector& Ground,const FCollisionQueryParams&) const {
        return !(UnsupportedGoal && Reference==PathGoal) && Collision.Ground(Reference,Ground);
    }''')
    walk=extract(prefix,'bool WalkSegment(')
    prefix=replace_once(prefix,walk,'''bool WalkSegment(FVector From,FVector To,const FCollisionQueryParams&) {
        if (To==PathGoal) {
            ++ConnectorChecks; MaxConnectorLength=std::max(MaxConnectorLength,FVector::Dist2D(From,To));
            if (BlockAllConnectors || (BlockFirstConnector && From==FixtureFeet)) { ++ConnectorRejected; return false; }
        }
        return Collision.Strip(From,To);
    }''')
    methods=[]
    for filename, signature in [
        ('EnemyCombatNavigation.cpp','bool UEnemyCombatComponent::PlanPath('),
        ('EnemyCombatNavigation.cpp','void UEnemyCombatComponent::ContinuePath('),
        ('EnemyCombatNavigation.cpp','bool UEnemyCombatComponent::FollowPath('),
        ('EnemyCombatComponent.cpp','CombatAI::ActionToken UEnemyCombatComponent::EnsureAction('),
        ('EnemyCombatComponent.cpp','bool UEnemyCombatComponent::FinishAction('),
        ('EnemyCombatComponent.cpp','void UEnemyCombatComponent::ClearIntent('),
    ]:
        body=extract(read(SRC/filename),signature)
        methods.append(dict(file=filename,method=signature,body=body,sha256=hashlib.sha256(body.encode()).hexdigest()))
    for signature,declaration in [
        ('bool FollowPath(', 'bool FollowPath(FVector,float,double,CombatAI::MovePurpose);'),
        ('CombatAI::ActionToken EnsureAction(', 'CombatAI::ActionToken EnsureAction(CombatAI::ActionKind,double);'),
        ('bool FinishAction(', 'bool FinishAction(CombatAI::ActionToken,CombatAI::ActionStatus,CombatAI::ActionFailure);'),
        ('void ClearIntent(', 'void ClearIntent(CombatAI::ActionFailure Why=CombatAI::ActionFailure::Replaced);'),
    ]:
        prefix=replace_once(prefix,extract(prefix,signature),declaration)
    policy=read(SRC/'EnemyCombatPolicy.cpp')
    condition=re.search(r'if \((Now - StateStarted > FMath::Clamp\(Tuning.PursuitSeconds, [^\n]+)\)',policy).group(1)
    prefix=replace_once(prefix,'bool PlanPath(FVector Goal,float Acceptance);',
        'bool PursuitExpired(double Now,double StateStarted) const { return '+condition+'; }\n    bool PlanPath(FVector Goal,float Acceptance);')

    geometry=json.loads(read(PREVIOUS/'editor-geometry.json'))
    floor=next(row for row in geometry['actors'] if row['label']=='Floor')
    selected=[row for row in geometry['actors'] if row['label'].startswith(('Pier_', 'FB01_newNcolumn'))]
    boxes=[]
    for row in selected:
        x,y,_=row['origin']; ex,ey,_=row['extent']; margin=37
        boxes.append('{'+','.join(f'{value:.5f}f' for value in (x-ex-margin,y-ey-margin,x+ex+margin,y+ey+margin))+'}')
    fixture='void LoadRetainedColumns(UEnemyCombatComponent& C) { C.Collision.Blockers={'+','.join(boxes)+'}; }'
    generated=OUT/f'navigation-{label}.cpp'
    generated.write_text(prefix+'\n\n'+'\n\n'.join(row['body'] for row in methods)+'\n'+fixture+'\n'+read(SCRIPT/'navigation_tests.cpp'),encoding='utf-8')

    checks={}
    with zipfile.ZipFile(PREVIOUS/'CAI02-Candidate01-frozen.zip') as archive:
        changed=[]
        for path in archive.namelist():
            if path.startswith('Source/') and archive.read(path)!=(ROOT/path).read_bytes(): changed.append(path)
        checks['only_three_native_files_changed']=sorted(changed)==[
            'Source/MeridianSquad/EnemyCombatComponent.h','Source/MeridianSquad/EnemyCombatNavigation.cpp','Source/MeridianSquad/EnemyCombatTactics.cpp']
        for filename in ('EnemyCombatNavigation.cpp','EnemyCombatTactics.cpp'):
            before=archive.read('Source/MeridianSquad/'+filename).decode('utf-8-sig').replace('\r\n','\n')
            checks[filename+'_only_home_radius_clamps_changed']=read(SRC/filename)==before.replace('Tuning.NavigationRadius, 400.f, 4000.f','Tuning.NavigationRadius, 400.f, 5000.f')
        old_header=archive.read('Source/MeridianSquad/EnemyCombatComponent.h').decode('utf-8-sig').replace('\r\n','\n')
        effective=lambda text: re.sub(r'//[^\n]*','',text).split()
        checks['header_only_radius_and_pursuit_defaults_changed']=effective(header)==effective(old_header.replace('PursuitSeconds = 12.f','PursuitSeconds = 24.f').replace('NavigationRadius = 2800.f','NavigationRadius = 4500.f'))
        checks['all_unchanged_evidence_methods_match_candidate01']=all(
            extract(archive.read('Source/MeridianSquad/'+row['file']).decode('utf-8-sig').replace('\r\n','\n'),row['method'])==row['body']
            for row in methods if 'PlanPath(' not in row['method'] and 'ContinuePath(' not in row['method'])
    checks['all_three_radius_clamps_match']=sum(read(SRC/name).count('Tuning.NavigationRadius, 400.f, 5000.f')
        for name in ('EnemyCombatNavigation.cpp','EnemyCombatTactics.cpp'))==3
    checks['actual_fixture_home_preserved']='FVector(-950, -320 + I * 320, 0)' in read(SRC/'PhysicsControlDummyWorld.cpp')
    max_home_distance=max(((x+950)**2+(y+320)**2)**.5 for x in (-3040,3040) for y in (-1240,1240))
    checks['retained_floor_extent_verified']=floor['extent']==[3040.,1240.,20.]
    checks['default_home_domain_contains_entire_floor']=max_home_distance<4500
    checks['pursuit_deadline_allows_nominal_crossing_plus_planning']=((6080**2+2480**2)**.5-820)/375+5<24
    for filename in ('candidate01-preservation-before.json','historical-preservation-before.json'):
        checks[filename+'_unchanged']=all(sha(ROOT/row['path'])==row['sha256'] for row in json.loads(read(OUT/filename)))
    checks['owner_config_project_map_unchanged']=all(sha(ROOT/row['path'])==row['sha256'] for row in json.loads(read(OUT/'owner-preservation-before.json')) if row['path']!='AGENTS.md')
    checks['durable_AGENTS_unchanged']=(ROOT/'AGENTS.md').read_bytes().split(b'<!-- BEGIN MULTICA-RUNTIME',1)[0].rstrip()==(ROOT/'Saved/CombatAI01/CAI-02/Controller/AGENTS.md').read_bytes().rstrip()

    vc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
    sdk=Path('C:/Program Files (x86)/Windows Kits/10')
    command=[str(vc/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX',
        '/I'+str(SRC),'/I'+str(vc/'include'),'/I'+str(sdk/'Include/10.0.22621.0/ucrt'),str(generated),
        '/Fe:'+str(OUT/f'navigation-{label}.exe'),'/Fo:'+str(OUT/f'navigation-{label}.obj'),'/link',
        '/LIBPATH:'+str(vc/'lib/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
    build=subprocess.run(command,cwd=OUT,text=True,capture_output=True)
    (OUT/f'compile-{label}.log').write_text(build.stdout+build.stderr,encoding='utf-8')
    checks['MSVC_W4_WX_compile']=build.returncode==0
    output=build.stdout+build.stderr
    if build.returncode==0:
        result=subprocess.run([str(OUT/f'navigation-{label}.exe')],cwd=OUT,text=True,capture_output=True)
        output=result.stdout+result.stderr
        (OUT/f'run-{label}.log').write_text(output,encoding='utf-8')
        checks['navigation_assertions']=result.returncode==0
    report=dict(passed=all(checks.values()),checks=checks,output=output,changed_source=changed,
        extracted_methods=[{key:value for key,value in row.items() if key!='body'} for row in methods],
        pursuit_timeout_expression=condition,max_home_corner_cm=max_home_distance,
        scope='Verbatim production navigation/action methods and timeout expression in reused CAIT01 container/action adapters. Deterministic support/strip callbacks with retained column bounds; no Unreal/gameplay/performance claims.',
        reuse='Candidate01 sensory, audio, sight, weapon, asset-wiring and remaining lifecycle evidence; unchanged native collision/physics/policy implementations verified by byte comparison.')
    with report_path.open('x',encoding='utf-8') as stream: json.dump(report,stream,indent=2)
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--label',required=True)
    raise SystemExit(run(parser.parse_args().label))
