"""Execute only CAIT-R1/R2 and their arrival/hold boundaries; no Unreal gameplay."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'Saved/CombatAI01/CAI-T01/Worker/Candidate02'
SRC = ROOT/'Source/MeridianSquad'
SCRIPT = Path(__file__).resolve().parent


def extract(text, signature):
    start = text.index(signature)
    begin = text.index('{', start)
    depth, end = 1, begin+1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[start:end]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(label):
    report_path = OUT/f'correction-check-{label}.json'
    assert not report_path.exists(), 'Use a new attempt label; preserve prior evidence'
    methods = [
        (SRC/'EnemyCombatNavigation.cpp', 'bool UEnemyCombatComponent::PlanPath('),
        (SRC/'EnemyCombatNavigation.cpp', 'void UEnemyCombatComponent::ContinuePath('),
        (SRC/'EnemyCombatTactics.cpp', 'bool UEnemyCombatComponent::TacticalTrace('),
        (SRC/'EnemyCombatTactics.cpp', 'void UEnemyCombatComponent::RejectTacticalPosition('),
        (SRC/'EnemyCombatTactics.cpp', 'void UEnemyCombatComponent::SetObservationFacing('),
        (SRC/'EnemyCombatTactics.cpp', 'void UEnemyCombatComponent::HoldTacticalPosition('),
        (SRC/'EnemyCombatTactics.cpp', 'void UEnemyCombatComponent::AdvanceSearch('),
        (Path('D:/UE_5.8/Engine/Source/Runtime/Experimental/Chaos/Private/Chaos/CollisionFilterData.cpp'),
         'ENarrowFilterResult FQueryFilterData::ChannelTypeNarrowFilter('),
    ]
    parts = [(SCRIPT/'correction_prefix.cpp').read_text()]
    records = []
    for path, signature in methods:
        body = extract(path.read_text(encoding='utf-8-sig'), signature)
        parts.append(body)
        records.append(dict(path=str(path), method=signature, sha256=hashlib.sha256(body.encode()).hexdigest()))
    parts.append((SCRIPT/'correction_suffix.cpp').read_text())
    generated = OUT/f'correction-generated-{label}.cpp'
    generated.write_text('\n\n'.join(parts), encoding='utf-8')

    checks = {}
    with zipfile.ZipFile(OUT.parent/'Candidate01/CAIT01-Candidate01-frozen.zip') as archive:
        for name, signatures in {
            'EnemyCombatNavigation.cpp': ['bool UEnemyCombatComponent::GroundPoint(', 'bool UEnemyCombatComponent::WalkSegment(',
                'bool UEnemyCombatComponent::PlanPath(', 'bool UEnemyCombatComponent::FollowPath('],
            'EnemyCombatTactics.cpp': ['bool UEnemyCombatComponent::TacticalGround(', 'bool UEnemyCombatComponent::TacticalWalk(',
                'void UEnemyCombatComponent::AdvanceSearch(', 'void UEnemyCombatComponent::HoldTacticalPosition(',
                'void UEnemyCombatComponent::RejectTacticalPosition(', 'void UEnemyCombatComponent::SetObservationFacing('],
        }.items():
            previous = archive.read('Source/MeridianSquad/'+name).decode('utf-8-sig')
            current = (SRC/name).read_text(encoding='utf-8-sig')
            for signature in signatures:
                checks['unchanged_'+signature.split('::')[1]] = extract(previous,signature).replace('\r\n','\n') == extract(current,signature)
        original_source = {n:archive.read(n) for n in archive.namelist() if n.startswith('Source/')}
        changed = [n for n, data in original_source.items() if data != (ROOT/n).read_bytes()]
        checks['only_two_production_files_changed'] = sorted(changed)==[
            'Source/MeridianSquad/EnemyCombatNavigation.cpp','Source/MeridianSquad/EnemyCombatTactics.cpp']
    trace = extract((SRC/'EnemyCombatTactics.cpp').read_text(), 'bool UEnemyCombatComponent::TacticalTrace(')
    checks['native_channel_query_static_only_response_mask'] = all(s in trace for s in [
        'FCollisionResponseParams StaticOnly(ECR_Ignore)', 'SetResponse(ECC_WorldStatic, ECR_Block)',
        'LineTraceSingleByChannel(Hit, From, To, Response, Query, StaticOnly)'])
    checks['historical_evidence_unchanged'] = all(digest(ROOT/r['path'])==r['sha256']
        for r in json.loads((OUT/'historical-preservation-before.json').read_text()))
    owner = json.loads((OUT/'owner-preservation-baseline.json').read_text())
    checks['owner_config_project_map_unchanged'] = all(digest(ROOT/r['path'])==r['sha256'] for r in owner if r['path']!='AGENTS.md')
    checks['durable_AGENTS_unchanged'] = (ROOT/'AGENTS.md').read_bytes().split(b'<!-- BEGIN MULTICA-RUNTIME',1)[0].rstrip()==(
        OUT.parents[1]/'Controller/AGENTS.md').read_bytes().rstrip()

    vc = Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
    sdk = Path('C:/Program Files (x86)/Windows Kits/10')
    command = [str(vc/'bin/Hostx64/x64/cl.exe'), '/nologo', '/std:c++20', '/EHsc', '/W4', '/WX',
        '/I'+str(vc/'include'), '/I'+str(sdk/'Include/10.0.22621.0/ucrt'), '/I'+str(SRC), str(generated),
        '/Fe:'+str(OUT/f'correction-{label}.exe'), '/Fo:'+str(OUT/f'correction-{label}.obj'),
        '/link', '/LIBPATH:'+str(vc/'lib/x64'), '/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),
        '/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
    build = subprocess.run(command,cwd=OUT,text=True,capture_output=True)
    (OUT/f'correction-build-{label}.log').write_text(build.stdout+build.stderr,encoding='utf-8')
    checks['MSVC_W4_WX_compile'] = build.returncode==0
    report = dict(methods=records, checks=checks, changed_source=changed, compile_exit=build.returncode,
        scope='Extracted production methods and installed UE channel filter; deterministic collision/container/clock/action adapters. No editor world or gameplay.',
        reused='Candidate01 native/source evidence for unchanged timing, lifecycle and combat contracts; primary-review original failed gap probes preserved.')
    if build.returncode==0:
        result = subprocess.run([str(OUT/f'correction-{label}.exe')],cwd=OUT,text=True,capture_output=True)
        (OUT/f'correction-run-{label}.log').write_text(result.stdout+result.stderr,encoding='utf-8')
        checks['affected_behavioral_checks'] = result.returncode==0
        report.update(run_exit=result.returncode,output=result.stdout)
    else:
        report['compile_output'] = build.stdout+build.stderr
    report['passed'] = all(checks.values())
    with report_path.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--label',required=True)
    raise SystemExit(run(parser.parse_args().label))
