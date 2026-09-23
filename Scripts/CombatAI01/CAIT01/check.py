"""Focused MSQ-118 production-header tests, source wiring and preservation.

Never launches Unreal or gameplay. Uses the existing installed MSVC convention.
The pure fixtures verify decisions given geometry; they do not prove map behavior.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import argparse

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Saved/CombatAI01/CAI-T01/Worker/Candidate01'
BASE = '5ae0fbc48a2c2f2b3cd3da64d15ec1a70446712a'


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


def run(label):
    checks = {}
    combat = source('EnemyCombatComponent.cpp')
    policy = source('EnemyCombatPolicy.cpp')
    tactics = source('EnemyCombatTactics.cpp')
    nav = source('EnemyCombatNavigation.cpp')
    observation = source('EnemyCombatObservation.cpp')
    checks['stationary_launch_gates_unchanged'] = function(combat, 'bool UEnemyCombatComponent::CanShoot(') == function(original('EnemyCombatComponent.cpp'), 'bool UEnemyCombatComponent::CanShoot(')
    checks['sight_adapter_unchanged'] = function(combat, 'bool UEnemyCombatComponent::TryObservePlayer(') == function(original('EnemyCombatComponent.cpp'), 'bool UEnemyCombatComponent::TryObservePlayer(')
    checks['finite_fire_cadence_and_effects_unchanged'] = function(combat, 'bool UEnemyCombatComponent::Fire(') == function(original('EnemyCombatComponent.cpp'), 'bool UEnemyCombatComponent::Fire(')
    sight = function(combat, 'bool UEnemyCombatComponent::ObservePlayer(')
    checks['contact_classifies_pre_refresh_memory'] = sight.index('Prior = Memory') < sight.index('TryObservePlayer()') < sight.index('ClassifyContact(Prior.Alert, Prior.HasObservation, WasVisible')
    checks['proposal_and_hold_no_hidden_player_getters'] = not re.search(r'GetFirstPlayer|GetPlayerViewPoint|Target->|Target.Get|GetPawn|SetRifleFollowPlayer\(true', policy+tactics+nav)
    checks['geometry_uses_static_object_type'] = 'ECC_WorldStatic' in tactics and not re.search('ByChannel|BuildQuery|Target', function(tactics, 'bool UEnemyCombatComponent::TacticalTrace('))
    checks['support_footprint_and_standing_capsule'] = all(t in function(tactics, 'bool UEnemyCombatComponent::TacticalGround(') for t in ['I < 4', 'ImpactNormal.Z < Slope', 'MaxSlopeDegrees', 'MakeCapsule(Radius+3, HalfHeight)', 'OverlapAnyTestByObjectType'])
    checks['routes_validate_support_and_sweep'] = all(t in function(tactics, 'bool UEnemyCombatComponent::TacticalWalk(') for t in ['Distance > MaxCandidateTravel', '1, 26', 'TacticalGround(', 'SweepSingleByObjectType'])
    checks['surface_derived_proposals_not_offset_cover_labels'] = all(t in tactics for t in ['SurfaceIndex < 8', 'Hit.ImpactPoint + Normal', 'ImpactNormal.Z) < .35', 'LowDistance <= 160', 'HighDistance <= 160', 'F.ProtectionMask |=', 'AddTacticalCandidate(ScanOrigin)'])
    checks['no_per_candidate_a_star'] = 'PlanPath(' not in tactics and 'FollowPath(' in tactics
    checks['bounded_candidates_work_scan_time'] = all(t in tactics for t in ['TacticalCandidates.Num() >= CombatAI::MaxTacticalCandidates', 'NextTacticalWork = Now + .025', 'Now - ScanStartedAt >= 4'])
    checks['failed_destinations_and_transfers_bounded_live'] = all(t in tactics for t in ['RejectedPositions.Remember(Ground.X, Ground.Y, Now + 12)', 'Transfers.Refresh(Now)', '!Transfers.CanStart()', 'Transfers.Start()', 'Now - TacticalMoveStartedAt > 10'])
    checks['arrival_actual_feet_and_policy_guard'] = 'AssessTacticalPosition(Feet(), Feet(), false)' in tactics and 'CombatAI::AcceptTacticalArrival(SelectedPosition.Rating, Arrived.Rating)' in tactics
    checks['winning_candidate_freshly_revalidated_before_move'] = 'const auto Winner = AssessTacticalPosition(TacticalCandidates[Best].Ground, Feet(), true);' in tactics and 'SelectedPosition = Winner' in tactics
    checks['lost_held_geometry_invalidates_cached_assignment'] = 'Assignment.Assign(EncounterGeneration, Assignment.Objective, Assignment.EvidenceId, Now);' in function(tactics, 'void UEnemyCombatComponent::HoldTacticalPosition(')
    checks['held_geometry_periodically_revalidated'] = 'Now >= NextHoldValidation' in tactics and 'NextHoldValidation = Now + 1' in tactics
    checks['held_facing_turns_existing_foundation'] = 'E->SetRifleStance(LookSector >= 0 ? EGASPALSRifleStance::Aim' in tactics and 'CombatAI::ObservationSector(' in tactics and 'WantsToAim_' in source('GASPEnemyRifle.cpp') and 'Inputs->OrientationIntent = Aim.GetSafeNormal2D();' in source('GASPEnemyRifle.cpp')
    checks['tactical_final_path_strip_validated'] = 'if (bTactical) Path.Add(FinalGround);' in nav and '!WalkSegment(Current.Ground, FinalGround, Query)' in nav
    advance = function(policy, 'void UEnemyCombatComponent::AdvanceCombat(')
    checks['death_authority_readiness_before_perception'] = advance.index('E->IsDead()') < advance.index('E->Authority !=') < advance.index('!E->IsReady()') < advance.index('ObservePlayer();')
    checks['new_sight_before_search_and_reload_waits'] = advance.index('ObservePlayer();') < advance.index('Assignment.Objective != CombatAI::TacticalObjective::Engage') < advance.index('Now < Gates.ReloadUntil') < advance.index('AdvanceSearch(Now)')
    checks['reload_requests_not_canceled_by_contact_classification'] = 'ClearIntent' not in sight and 'State == EEnemyCombatState::Reload' not in sight
    checks['reload_commit_request_guard_retained'] = advance.index('FinishAction(ReloadRequest,') < advance.index('Magazine = FMath::Clamp')
    checks['distinct_deadlines_live_at_fire_decision'] = all(t in advance for t in ['Gates.ContactUntil', 'Gates.AimUntil =', 'Gates.PauseUntil =', 'Gates.ReloadUntil =', 'Now < Gates.ReadyAt(NextShot)']) and 'ReadyAt =' not in advance
    checks['recovery_replans_actual_feet'] = 'BeginSearch(TEXT("locomotion returned; replan from actual feet"))' in advance and 'ScanOrigin = Feet()' in tactics
    for signature in ['void UEnemyCombatComponent::SetEnabled(', 'void UEnemyCombatComponent::StopCombat(', 'void UEnemyCombatComponent::SuspendForPhysics(']:
        checks['reset_tactics_' + signature.split('::')[1].split('(')[0]] = 'ResetTactics()' in function(combat, signature)
    suspend = function(combat, 'void UEnemyCombatComponent::SuspendForPhysics(')
    checks['living_memory_retained_death_cleared'] = 'if (bDead) { Target.Reset(); Memory.Reset(); }' in suspend and suspend.count('Memory.Reset') == 1
    checks['scan_tokens_guard_stale_work'] = tactics.count('Assignment.Accepts(ScanRequest)') == 2
    checks['path_action_tokens_retained'] = nav.count('!Action.Accepts(PathRequest)') == 2 and 'Request.Generation != EncounterGeneration' in combat
    checks['trace_exposes_decision_execution_and_gates'] = all(t in observation for t in ['pending_gate', 'contact_world_time', 'contact_decision_world_time', 'tactical_move_started_world_time', 'action_started', 'position_rejections', 'evidence_age_world_seconds', 'next_reassessment', 'selected_facing_point'])
    for name in ['CombatRifleComponent.cpp', 'CombatProjectileWorld.cpp', 'PhysicsControlDummyWorld.cpp', 'GASPEnemyFixture.cpp', 'GASPEnemyRifle.cpp', 'GASPALSRifleAnimInstance.cpp', 'PlayerCombatReceiver.cpp', 'CombatAIAction.h']:
        checks['unchanged_' + name] = source(name) == original(name)
    preservation = []
    for entry in json.loads((ROOT / 'Saved/CombatAI01/CAI-T01/Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
        digest = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
        preservation.append(dict(path=entry['path'], sha256=digest, match=digest == entry['sha256']))
    checks['owner_config_project_map_preserved'] = all(x['match'] for x in preservation if x['path'] != 'AGENTS.md')
    # Multica injects its runtime block on task startup, after controller capture.
    # Preserve that block and the original manifest; never rebaseline its hash.
    before_instructions = (ROOT / 'Saved/CombatAI01/CAI-T01/Controller/AGENTS.md').read_bytes()
    after_instructions = (ROOT / 'AGENTS.md').read_bytes()
    durable = after_instructions.split(b'<!-- BEGIN MULTICA-RUNTIME', 1)[0].rstrip()
    checks['durable_instructions_preserved_runtime_append_identified'] = durable == before_instructions.rstrip()
    (OUT / f'instructions-preservation-{label}.json').write_text(json.dumps(dict(
        full_hash_matches=next(x['match'] for x in preservation if x['path']=='AGENTS.md'),
        durable_bytes_match=checks['durable_instructions_preserved_runtime_append_identified'],
        difference='Multica auto-managed runtime block appended at task startup; not edited by executor'), indent=2))
    (OUT / f'preservation-{label}.json').write_text(json.dumps(preservation, indent=2))
    vc = Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
    sdk = Path('C:/Program Files (x86)/Windows Kits/10')
    command = [str(vc / 'bin/Hostx64/x64/cl.exe'), '/nologo', '/std:c++20', '/EHsc', '/W4', '/WX',
        '/I' + str(vc / 'include'), '/I' + str(sdk / 'Include/10.0.22621.0/ucrt'),
        str(Path(__file__).with_name('tactics_test.cpp')), '/Fe:' + str(OUT / 'tactics_test.exe'),
        '/Fo:' + str(OUT / 'tactics_test.obj'), '/link', '/LIBPATH:' + str(vc / 'lib/x64'),
        '/LIBPATH:' + str(sdk / 'Lib/10.0.22621.0/ucrt/x64'), '/LIBPATH:' + str(sdk / 'Lib/10.0.22621.0/um/x64')]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (OUT / f'pure-test-build-{label}.log').write_text(result.stdout + result.stderr)
    checks['production_header_test_compile_W4_WX'] = result.returncode == 0
    if result.returncode == 0:
        result = subprocess.run([str(OUT / 'tactics_test.exe')], cwd=OUT, text=True, capture_output=True)
        (OUT / f'pure-test-{label}.log').write_text(result.stdout + result.stderr)
        checks['production_header_behavioral_invariants'] = result.returncode == 0
    else:
        checks['production_header_behavioral_invariants'] = False
    report = dict(task='MSQ-118', baseline=BASE, label=label, mode='source and pure contracts only; no gameplay',
        checks=checks, passed=all(checks.values()), pending_owner='All actual movement, map-position utility, firing, physical transitions, performance and feel')
    with (OUT / f'self-check-{label}.json').open('x') as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', required=True)
    raise SystemExit(run(parser.parse_args().label))
