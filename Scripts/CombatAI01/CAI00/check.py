"""Focused MSQ-102 source/preservation checks plus the actual pure C++ contract test.

Run with the installed UE Python from the project root. Does not start a game/editor.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-00/Worker/Candidate01'
OUT.mkdir(parents=True, exist_ok=True)
checks = {}


def source(name):
    return (ROOT / 'Source/MeridianSquad' / name).read_text(encoding='utf-8-sig')


def original(name):
    return subprocess.check_output(['git', 'show', '288f44d3a313a9d6801c858ac74076d2cd6c7fd9:Source/MeridianSquad/' + name], cwd=ROOT, text=True)


def function(text, signature):
    start = text.index('{', text.index(signature))
    depth = 1
    end = start + 1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[start:end]


combat = source('EnemyCombatComponent.cpp')
legacy = original('EnemyCombatComponent.cpp')
observation = source('EnemyCombatObservation.cpp')
checks['legacy_sight_query_body_unchanged'] = function(combat, 'bool UEnemyCombatComponent::TryObservePlayer()') == function(legacy, 'bool UEnemyCombatComponent::ObservePlayer()')
advance = function(combat, 'void UEnemyCombatComponent::AdvanceCombat(')
advance = advance.replace('    CaptureDeltaSeconds = DeltaSeconds;\n', '').replace('        RecordTrace(CombatAI::Event::DecisionInput, TEXT("post-perception legacy policy input"));\n', '')
checks['legacy_decision_body_only_instrumented'] = advance == function(legacy, 'void UEnemyCombatComponent::AdvanceCombat(')
checks['launch_gates_unchanged'] = function(combat, 'bool UEnemyCombatComponent::CanShoot(') == function(legacy, 'bool UEnemyCombatComponent::CanShoot(')
checks['finite_search_return_unchanged'] = function(combat, 'void UEnemyCombatComponent::StartReturn(') == function(legacy, 'void UEnemyCombatComponent::StartReturn(')
capture = function(observation, 'CombatAI::InputSnapshot UEnemyCombatComponent::CaptureDecisionInput()')
capture = re.sub(r'//[^\n]*', '', capture)
checks['capture_no_player_or_target_dereference'] = not re.search(r'Target\s*(?:->|\.)|GetPlayer|GetFirstPlayer|GetPlayerViewPoint|GetActorLocation', capture)
checks['capture_known_positions_memory_gated'] = 'if (bHasMemory)\n    {\n        S.KnownGround' in capture
checks['capture_no_fairness_channel'] = 'PrivilegedFairnessTrace' not in observation + combat
checks['same_seed_reset_not_generation_mixed'] = 'Seed = CombatAI::AgentSeed(EncounterSeed, StableSpawnIndex);' in combat and 'Spread.Initialize(70)' not in combat
checks['slot_before_finish_spawning'] = source('PhysicsControlDummyWorld.cpp').index('SetStableSpawnIndex') < source('PhysicsControlDummyWorld.cpp').index('FinishSpawning')
reset = function(source('CombatProjectileWorld.cpp'), 'void ACombatProjectileWorld::ResetTargets()')
checks['generation_before_fixture_reset'] = reset.index('++EncounterGeneration') < reset.index('Dummy->ResetDummy()')
checks['reset_only_adds_encounter_generation'] = reset.replace('    ++EncounterGeneration;\n', '') == function(original('CombatProjectileWorld.cpp'), 'void ACombatProjectileWorld::ResetTargets()')
checks['new_ring_after_intent_clear'] = combat.index('DecisionTrace.Reset(EncounterGeneration)') > combat.index('SetEnabled(bEnabled);')
checks['no_automatic_trace_disk_write'] = combat.index('else if (Op == TEXT("trace"))') < combat.index('FFileHelper::SaveStringToFile') and 'SaveStringToFile' not in observation
checks['walking_unchanged'] = 'SetMovementCommand(Path[PathIndex] - Position, true)' in source('EnemyCombatNavigation.cpp')
for name in ['CombatRifleComponent.cpp', 'GASPEnemyFixture.cpp', 'GASPEnemyRifle.cpp', 'PlayerCombatReceiver.cpp', 'GASPALSRifleAnimInstance.cpp']:
    checks['unchanged_' + name] = source(name) == original(name)
for name in ['ApplyPreviewTime', 'RestorePreviewTime']:
    checks['unchanged_time_' + name] = function(source('PhysicsControlDummyWorld.cpp'), 'void ACombatProjectileWorld::' + name + '(') == function(original('PhysicsControlDummyWorld.cpp'), 'void ACombatProjectileWorld::' + name + '(')
preservation = []
for entry in json.loads((ROOT / 'Saved/CombatAI01/CAI-00/Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    digest = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
    preservation.append(dict(path=entry['path'], sha256=digest, match=digest == entry['sha256']))
checks['owner_config_project_map_preserved'] = all(x['match'] for x in preservation)
(OUT / 'preservation-after.json').write_text(json.dumps(preservation, indent=2))

# Compile/run the same header used by the native module, with warnings as errors.
vc = Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
sdk = Path('C:/Program Files (x86)/Windows Kits/10')
command = [str(vc / 'bin/Hostx64/x64/cl.exe'), '/nologo', '/std:c++20', '/EHsc', '/W4', '/WX',
           '/I' + str(vc / 'include'), '/I' + str(sdk / 'Include/10.0.22621.0/ucrt'),
           str(Path(__file__).with_name('observation_test.cpp')),
           '/Fe:' + str(OUT / 'observation_test.exe'), '/Fo:' + str(OUT / 'observation_test.obj'), '/link',
           '/LIBPATH:' + str(vc / 'lib/x64'), '/LIBPATH:' + str(sdk / 'Lib/10.0.22621.0/ucrt/x64'),
           '/LIBPATH:' + str(sdk / 'Lib/10.0.22621.0/um/x64')]
result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
(OUT / 'pure-test-build.log').write_text(result.stdout + result.stderr)
checks['pure_cpp_compile'] = result.returncode == 0
if result.returncode == 0:
    result = subprocess.run([str(OUT / 'observation_test.exe')], cwd=OUT, text=True, capture_output=True)
    (OUT / 'pure-test.log').write_text(result.stdout + result.stderr)
    checks['pure_cpp_invariants'] = result.returncode == 0
else:
    checks['pure_cpp_invariants'] = False
report = dict(mode='source and pure production-contract invariants only; no gameplay', checks=checks,
              runtime_reset_replay_behavior_performance='PENDING OWNER', passed=all(checks.values()))
(OUT / 'self-check.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
