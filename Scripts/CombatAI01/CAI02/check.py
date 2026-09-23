"""Focused production contracts/methods and source/preservation checks; no gameplay."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).resolve().parent
OUT=ROOT/'Saved/CombatAI01/CAI-02/Worker/Candidate01'
SRC=ROOT/'Source/MeridianSquad'
def source(name):return (SRC/name).read_text(encoding='utf-8-sig')
def method(text,signature):
    start=text.index(signature);begin=text.index('{',start);end=begin+1;depth=1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return text[start:end]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compile_run(path,name,label,checks):
    vc=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
    sdk=Path('C:/Program Files (x86)/Windows Kits/10')
    exe=OUT/f'{name}-{label}.exe'
    command=[str(vc/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX',
        '/I'+str(SRC),'/I'+str(vc/'include'),'/I'+str(sdk/'Include/10.0.22621.0/ucrt'),str(path),
        '/Fe:'+str(exe),'/Fo:'+str(OUT/f'{name}-{label}.obj'),'/link','/LIBPATH:'+str(vc/'lib/x64'),
        '/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/ucrt/x64'),'/LIBPATH:'+str(sdk/'Lib/10.0.22621.0/um/x64')]
    r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    (OUT/f'{name}-build-{label}.log').write_text(r.stdout+r.stderr)
    checks[name+'_compile']=r.returncode==0
    if r.returncode==0:
        r=subprocess.run([str(exe)],cwd=OUT,text=True,capture_output=True)
        (OUT/f'{name}-run-{label}.log').write_text(r.stdout+r.stderr)
        checks[name+'_assertions']=r.returncode==0
        print(r.stdout)
    else:print(r.stdout+r.stderr)

def run(label):
    assert not (OUT/f'checks-{label}.json').exists(),'Use a new attempt label'
    checks={};bodies=[];identities=[]
    for file,signature in [('EnemyCombatSenses.cpp','void UEnemyCombatComponent::ReceiveStimulus('),
        ('EnemyCombatSenses.cpp','void UEnemyCombatComponent::ApplyEvidenceIntent('),
        ('EnemyCombatPolicy.cpp','void UEnemyCombatComponent::BeginSearch('),
        ('EnemyCombatComponent.cpp','bool UEnemyCombatComponent::Fire(')]:
        body=method(source(file),signature);bodies.append(body)
        identities.append(dict(file=file,method=signature,sha256=hashlib.sha256(body.encode()).hexdigest()))
    generated=OUT/f'integration-{label}.cpp'
    generated.write_text((SCRIPT/'integration_prefix.cpp').read_text()+'\n\n'+'\n\n'.join(bodies)+'\n'+(SCRIPT/'integration_suffix.cpp').read_text())
    compile_run(SCRIPT/'senses_test.cpp','pure',label,checks)
    compile_run(generated,'integration',label,checks)
    projectile=source('CombatProjectileWorld.cpp');world=source('CombatStimulusWorld.cpp');combat=source('EnemyCombatComponent.cpp')
    policy=source('EnemyCombatPolicy.cpp');tactics=source('EnemyCombatTactics.cpp');senses=source('EnemyCombatSenses.cpp')
    launch=method(projectile,'int64 ACombatProjectileWorld::LaunchTimed(')
    hit=method(projectile,'void ACombatProjectileWorld::ResolveHit(')
    tick=method(projectile,'void ACombatProjectileWorld::Tick(')
    checks['accepted_birth_only']=launch.index('return 0;')<launch.index('Bullets.Add(Bullet)')<launch.index('QueueSound(')<launch.index('return Bullet.Id;')
    checks['contact_record_before_physics']=hit.index('CombatAI::Sense::Damage')<hit.index('PhysicalTarget->ReceiveBullet')
    checks['contact_keeps_world_and_simulation_clocks']='LastContactTime' in hit and 'S.OccurredWorld = GetWorld()->GetTimeSeconds(); S.SimulationTime = SimulationTime;' in world
    checks['delivery_outside_collision_frame']=tick.index('AdvanceFrame(')<tick.index('DeliverStimuli()') and 'check(!bAdvancing && !bProcessingFrame)' in world
    checks['reset_clears_delivery_and_motion']='Stimuli.Reset();' in method(projectile,'void ACombatProjectileWorld::ClearProjectiles(') and 'PlayerTravel.Reset(); EnemyTravel.Reset(); TravelPlayer.Reset();' in method(projectile,'void ACombatProjectileWorld::ResetTargets(')
    checks['ordered_contacts_preserved']='PendingHits.Sort(' in projectile and 'Generation != ResetGeneration' in projectile
    checks['bounded_queue_listener_fanout']='Stimuli.Num() >= 64' in world and 'if (++Listeners > 8) break' in world
    checks['mutable_actor_handles_do_not_enter_memory']='Q.Attribution.Get()' in world and 'Target->' not in senses and 'GetPlayer' not in senses
    checks['movement_audio_is_secondary_consumer']=world.index('QueueSound(Actor, Team')<world.index('if (!StepSound)') and 'PlaySoundAtLocation' in world
    checks['actual_ground_and_stance']='Move->IsMovingOnGround()' in world and 'Mover->IsOnGround(), E->IsMovementCrouched()' in world and 'Move->Velocity.Size2D() > 430' in world
    checks['foot_audio_old_route_intercept']='HandleNotify' in source('CombatLocomotionAnimInstance.cpp') and 'A_TFA_Foley_Footsteps_Cue' in source('CombatLocomotionAnimInstance.cpp') and 'BP_AnimNotify_FoleyEvent_Crouch_' in source('CombatLocomotionAnimInstance.cpp')
    checks['gasp_uses_notify_filter_base']='public UCombatLocomotionAnimInstance' in source('GASPALSRifleAnimInstance.h')
    checks['player_uses_notify_filter_base']='public UCombatLocomotionAnimInstance' in source('PurchasedArmsAnimInstance.h')
    checks['real_crouch_bridge']='E->SetCrouchCommand(true)' in tactics and 'CharacterMover->Crouch()' in source('GASPEnemyRifle.cpp')
    checks['sight_body_samples_and_range']='float SightRange = 7000.f' in source('EnemyCombatComponent.h') and 'FirstVisibleSample(3' in combat and 'LastKnownAim = Samples[VisibleSample]' in combat
    checks['failed_sight_cannot_refresh']=combat.index('if (VisibleSample < 0) return false')<combat.index('LastKnownAim = Samples[VisibleSample]')
    checks['contact_grace_stops_motion']='Knowledge.RetainsContact(Now)' in policy and 'E->StopMovementCommand(); E->SetRifleAimTarget(LastKnownAim)' in policy
    checks['evidence_reaches_active_decision']='ApplyEvidenceIntent(Now)' in policy and 'BeginSearch(TEXT("fresh sound redirects protected investigation"))' in senses
    checks['recovery_keeps_knowledge']='if (bDead) { Target.Reset(); Memory.Reset(); Knowledge.Reset(EncounterGeneration)' in combat
    checks['no_hidden_tactical_getters']=all(s not in policy+tactics+senses for s in ['GetPlayerViewPoint','Target->','GetPawn()','SetRifleFollowPlayer(true'])
    checks['static_protected_side_candidates']='const FBox Bounds=Hit.GetComponent()->Bounds.GetBox()' in tactics and 'CombatAI::AroundColumn(' in tactics
    checks['actual_checked_route_executed']='Path=Winner.Route' in tactics and 'TacticalWalk(FVector(A.X' in tactics
    checks['candidate_evidence_relative_facing']='P.FacingBasis=(SearchAnchor-P.Ground).GetSafeNormal2D()' in tactics
    checks['broad_exposure_and_safe_near_selection']='.35*BroadExposure/8.0' in tactics and 'CombatAI::PreferNearbySafe(' in tactics
    checks['arrival_uses_actual_feet']='AssessTacticalPosition(Feet(), Feet(), false)' in tactics and 'AcceptTacticalArrival(SelectedPosition.Rating, Arrived.Rating)' in tactics
    base=json.loads((OUT/'baseline.json').read_text())['head']
    old=subprocess.check_output(['git','show',base+':Source/MeridianSquad/EnemyCombatComponent.cpp'],cwd=ROOT,text=True)
    for signature in ['bool UEnemyCombatComponent::Fire(', 'bool UEnemyCombatComponent::CanShoot(']:
        checks['unchanged_'+signature.split('::')[1]]=method(old,signature)==method(combat,signature)
    for name in ['CombatRifleComponent.cpp','PhysicsControlDummyWorld.cpp','GASPEnemyFixture.cpp','GASPEnemyRifle.cpp','OpeningLobbyCharacter.cpp','PlayerCombatReceiver.cpp']:
        old=subprocess.check_output(['git','show',base+':Source/MeridianSquad/'+name],cwd=ROOT,text=True)
        checks['unchanged_'+name]=old==source(name)
    owner=json.loads((OUT/'owner-preservation-before.json').read_text())
    checks['owner_config_project_map_preserved']=all(sha(ROOT/r['path'])==r['sha256'] for r in owner if r['path']!='AGENTS.md')
    checks['history_preserved']=all(sha(ROOT/r['path'])==r['sha256'] for r in json.loads((OUT/'historical-preservation-before.json').read_text()))
    report=dict(task='MSQ-104',label=label,checks=checks,passed=all(checks.values()),extracted_methods=identities,
        mode='Production pure contracts and verbatim methods under deterministic adapters; supporting source checks; no gameplay',
        pending='Owner gameplay/motion/audibility/performance and independent review; native build and asset wiring have separate evidence')
    with (OUT/f'checks-{label}.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--label',required=True)
    raise SystemExit(run(parser.parse_args().label))
