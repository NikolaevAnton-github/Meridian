"""Focused MSQ-103 source/preservation checks and production-header C++ invariants.
Reuses CAI-00's installed compiler/evidence conventions. Never starts gameplay.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-01/Worker/Candidate01'
BASE = 'b0e599d5f39023fa5c04d5e6b222b3415655621e'
checks = {}


def source(name):
    return (ROOT / 'Source/MeridianSquad' / name).read_text(encoding='utf-8-sig')


def original(name):
    return subprocess.check_output(['git', 'show', BASE + ':Source/MeridianSquad/' + name], cwd=ROOT, text=True)


def function(text, signature):
    start = text.index('{', text.index(signature))
    end, depth = start + 1, 1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[start:end]


combat = source('EnemyCombatComponent.cpp')
policy = source('EnemyCombatPolicy.cpp')
nav = source('EnemyCombatNavigation.cpp')
observation = source('EnemyCombatObservation.cpp')
checks['no_global_sight_suppression_or_amnesia_return'] = 'IgnoreSightUntil' not in combat + policy and 'StartReturn' not in combat + policy
checks['no_observation_age_disengagement'] = 'Memory.LastSeen' not in policy and 'Memory.Reset' not in policy
advance = function(policy, 'void UEnemyCombatComponent::AdvanceCombat(')
checks['perception_before_tactical_cooldown_selection'] = advance.index('ObservePlayer();') < advance.index('MoveBackoff.Blocks(')
checks['no_search_hidden_transform_reads'] = not re.search('GetFirstPlayer|GetPlayerViewPoint|Target->|Target.Get|GetPawn', policy + nav)
checks['stationary_launch_gates_unchanged'] = function(combat, 'bool UEnemyCombatComponent::CanShoot(') == function(original('EnemyCombatComponent.cpp'), 'bool UEnemyCombatComponent::CanShoot(')
sight = function(combat, 'bool UEnemyCombatComponent::TryObservePlayer(')
old_sight = function(original('EnemyCombatComponent.cpp'), 'bool UEnemyCombatComponent::TryObservePlayer(')
checks['same_sight_geometry_and_provenance'] = sight.replace('Memory.Observe(GetWorld()->GetTimeSeconds());', 'LastSeen = GetWorld()->GetTimeSeconds();\n    bHasMemory = true;') == old_sight
fire = function(combat, 'bool UEnemyCombatComponent::Fire(')
checks['fire_request_guard_before_perception_and_launch'] = fire.index('Action.Accepts(Request)') < fire.index('ObservePlayer()') < fire.index('World->Launch(')
checks['fire_generation_guard'] = 'Request.Generation != EncounterGeneration' in fire
checks['reload_commit_guard'] = advance.index('FinishAction(ReloadRequest,') < advance.index('Magazine = FMath::Clamp')
checks['death_physics_before_readiness_and_perception'] = advance.index('E->IsDead()') < advance.index('E->Authority !=') < advance.index('!E->IsReady()') < advance.index('ObservePlayer();')
suspend = function(combat, 'void UEnemyCombatComponent::SuspendForPhysics(')
checks['living_recovery_keeps_observation'] = 'if (bDead) { Target.Reset(); Memory.Reset(); }' in suspend and suspend.count('Memory.Reset()') == 1
checks['cancel_physics_clears_movement_path_and_burst'] = 'ClearIntent(bDead ?' in suspend and all(s in function(combat, 'void UEnemyCombatComponent::ClearIntent(') for s in ['ActionStatus::Canceled', 'Path.Reset()', 'Nodes.Reset()', 'BurstRemaining = 0', 'StopMovementCommand()'])
checks['resume_replans_actual_feet'] = 'BeginSearch(TEXT("locomotion returned; replan from actual feet"))' in advance and 'const FVector Start = Feet();' in nav
checks['stale_path_rejected_before_expansion'] = nav.index('!Action.Accepts(PathRequest)') < nav.index('const double BudgetStart')
follow = function(nav, 'bool UEnemyCombatComponent::FollowPath(')
checks['stale_path_rejected_before_submission'] = follow.index('!Action.Accepts(PathRequest)') < follow.index('E->SetMovementCommand(')
checks['failure_backoff_domains_separate'] = 'SearchBackoff.Set(SearchGoal.X' in policy and 'auto& Backoff = bWeapon ? WeaponBackoff : MoveBackoff;' in policy
checks['failed_closing_route_allows_in_range_aim'] = 'MoveSuppressed ? AttackRange : AttackRange * .82f' in policy
checks['explicit_gait_not_direction_magnitude'] = 'CombatAI::WantsWalk(Purpose,' in nav and 'E->SetMovementCommand(Direction, bRequestedWalk)' in nav
checks['bounded_local_planner_retained'] = all(s in nav for s in ['Work < 16', '> .0015', 'MaxPathExpansions, 64, 2000', 'PlanStarted > 5.f'])
checks['new_trace_distinguishes_alert_evidence_action_gait'] = all(s in observation for s in ['confirmed_alert', 'action_generation', 'action_failure', 'requested_gait', 'last_sight'])
checks['arrival_observes_outward_sector'] = 'SearchLook = Feet() + SearchForward.RotateAngleAxis(SectorAngle, FVector::UpVector) * 400.f' in policy
checks['reset_invalidates_action_requests'] = all(s in combat for s in ['Action.Reset(EncounterGeneration);', 'PathRequest = {}; ReloadRequest = {};'])
for name in ['CombatRifleComponent.cpp', 'CombatProjectileWorld.cpp', 'PhysicsControlDummyWorld.cpp', 'GASPEnemyFixture.cpp', 'GASPEnemyRifle.cpp', 'GASPALSRifleAnimInstance.cpp', 'PlayerCombatReceiver.cpp']:
    checks['unchanged_' + name] = source(name) == original(name)

preservation = []
for entry in json.loads((ROOT / 'Saved/CombatAI01/CAI-01/Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    digest = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
    preservation.append(dict(path=entry['path'], sha256=digest, match=digest == entry['sha256']))
checks['owner_config_project_map_preserved'] = all(x['match'] for x in preservation)
(OUT / 'preservation-after.json').write_text(json.dumps(preservation, indent=2))
asset_paths = ['Plugins/GASPEnemyFoundation01/Content/Blueprints/SandboxCharacter_Mover.uasset',
               'Plugins/GASPEnemyFoundation01/Content/Blueprints/MovementModes/BP_MovementMode_Walking.uasset',
               'Plugins/GASPEnemyFoundation01/Content/Blueprints/SandboxCharacter_Mover_ABP.uasset']
asset_rows = []
for path in asset_paths:
    pointer = subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT, text=True)
    expected = re.search(r'oid sha256:([0-9a-f]+)', pointer).group(1)
    actual = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    asset_rows.append(dict(path=path, sha256=actual, match=expected == actual))
checks['inspected_gasp_assets_unchanged_from_prerequisite_lfs'] = all(x['match'] for x in asset_rows)
(OUT / 'gait-asset-preservation.json').write_text(json.dumps(asset_rows, indent=2))

gait = json.loads((OUT / 'gait-mapping.json').read_text())['blueprints'][0]['graphs']
gait = {g['name']: g for g in gait}['Get_Gait']
nodes = {n['name']: n for n in gait['nodes']}
pin = lambda n, p: next(x for x in nodes[n]['pins'] if x['name'] == p)
branch = pin('K2Node_FunctionEntry_0', 'then')['links'][0].split(':')[0]
condition = pin(branch, 'Condition')['links'][0].split(':')[0]
walk_return = pin(branch, 'then')['links'][0].split(':')[0]
run_return = pin(branch, 'else')['links'][0].split(':')[0]
checks['gasp_commanded_walk_true0_false1'] = nodes[condition]['title'] == 'CommandedWalk' and pin(walk_return, 'ReturnValue')['value'] == 'NewEnumerator0' and pin(run_return, 'ReturnValue')['value'] == 'NewEnumerator1'
movement = json.loads((OUT / 'gait-movement-mode.json').read_text())
nodes = {n['name']: n for g in movement['graphs'] for n in g['nodes']}
checks['gasp_enum0_walk165_enum1_run375'] = pin('K2Node_Select_4', 'NewEnumerator0')['links'][0].endswith(':WalkSpeed') and pin('K2Node_Select_4', 'NewEnumerator1')['links'][0].endswith(':RunSpeed') and movement['defaults']['WalkSpeed'] == '165.0' and movement['defaults']['RunSpeed'] == '375.0'

vc = Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
sdk = Path('C:/Program Files (x86)/Windows Kits/10')
command = [str(vc / 'bin/Hostx64/x64/cl.exe'), '/nologo', '/std:c++20', '/EHsc', '/W4', '/WX',
           '/I' + str(vc / 'include'), '/I' + str(sdk / 'Include/10.0.22621.0/ucrt'),
           str(Path(__file__).with_name('action_test.cpp')),
           '/Fe:' + str(OUT / 'action_test.exe'), '/Fo:' + str(OUT / 'action_test.obj'), '/link',
           '/LIBPATH:' + str(vc / 'lib/x64'), '/LIBPATH:' + str(sdk / 'Lib/10.0.22621.0/ucrt/x64'),
           '/LIBPATH:' + str(sdk / 'Lib/10.0.22621.0/um/x64')]
result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
(OUT / 'pure-test-build.log').write_text(result.stdout + result.stderr)
checks['pure_cpp_compile'] = result.returncode == 0
if result.returncode == 0:
    result = subprocess.run([str(OUT / 'action_test.exe')], cwd=OUT, text=True, capture_output=True)
    (OUT / 'pure-test.log').write_text(result.stdout + result.stderr)
    checks['pure_cpp_invariants'] = result.returncode == 0
else:
    checks['pure_cpp_invariants'] = False
report = dict(mode='source and pure production-contract checks; no gameplay', checks=checks,
              runtime_S01_S06_S07_S10='PENDING OWNER', passed=all(checks.values()))
(OUT / 'self-check.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
