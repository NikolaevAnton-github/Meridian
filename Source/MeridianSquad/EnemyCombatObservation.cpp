#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "GASPALSRifleAnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "UObject/UnrealType.h"

namespace
{
CombatAI::Position ValuePosition(const FVector& V) { return {V.X, V.Y, V.Z}; }
TSharedPtr<FJsonValue> JsonPosition(const CombatAI::Position& P)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(P.X), MakeShared<FJsonValueNumber>(P.Y), MakeShared<FJsonValueNumber>(P.Z)});
}
const TCHAR* PathName(CombatAI::PathOutcome P)
{
    switch (P)
    {
    case CombatAI::PathOutcome::Planning: return TEXT("planning");
    case CombatAI::PathOutcome::Ready: return TEXT("ready");
    case CombatAI::PathOutcome::Following: return TEXT("following");
    case CombatAI::PathOutcome::Arrived: return TEXT("arrived");
    case CombatAI::PathOutcome::Failed: return TEXT("failed");
    case CombatAI::PathOutcome::Canceled: return TEXT("canceled");
    default: return TEXT("none");
    }
}
const TCHAR* EventName(CombatAI::Event E)
{
    switch (E)
    {
    case CombatAI::Event::Reset: return TEXT("reset");
    case CombatAI::Event::DecisionInput: return TEXT("decision_input");
    case CombatAI::Event::Sight: return TEXT("sight");
    case CombatAI::Event::SightLost: return TEXT("sight_query_failed");
    case CombatAI::Event::State: return TEXT("state");
    case CombatAI::Event::Path: return TEXT("path");
    case CombatAI::Event::Shot: return TEXT("shot");
    case CombatAI::Event::Authority: return TEXT("authority");
    case CombatAI::Event::Action: return TEXT("action");
    case CombatAI::Event::Tactical: return TEXT("tactical");
    case CombatAI::Event::Stimulus: return TEXT("stimulus");
    default: return TEXT("stop");
    }
}
TSharedRef<FJsonObject> SnapshotJson(const CombatAI::InputSnapshot& S)
{
    auto J = MakeShared<FJsonObject>();
    // Full-width IDs use decimal strings to avoid JSON double precision loss.
    J->SetStringField(TEXT("generation"), LexToString(S.Generation));
    J->SetNumberField(TEXT("encounter_seed"), S.EncounterSeed);
    J->SetNumberField(TEXT("spawn_index"), S.SpawnIndex);
    J->SetNumberField(TEXT("agent_seed"), S.Seed);
    J->SetNumberField(TEXT("world_time"), S.WorldTime);
    J->SetNumberField(TEXT("delta_world_seconds"), S.DeltaSeconds);
    J->SetField(TEXT("self_feet"), JsonPosition(S.SelfFeet));
    J->SetField(TEXT("home"), JsonPosition(S.Home));
    J->SetField(TEXT("known_ground"), JsonPosition(S.KnownGround));
    J->SetField(TEXT("known_aim"), JsonPosition(S.KnownAim));
    J->SetField(TEXT("action_goal"), JsonPosition(S.ActionGoal));
    J->SetField(TEXT("search_anchor"), JsonPosition(S.SearchAnchor));
    J->SetField(TEXT("search_look"), JsonPosition(S.SearchLook));
    J->SetNumberField(TEXT("last_seen_world_time"), S.LastSeenWorldTime);
    J->SetStringField(TEXT("sight_event_id"), LexToString(S.SightEventId));
    J->SetNumberField(TEXT("state_started"), S.StateStarted);
    J->SetNumberField(TEXT("ready_at"), S.ReadyAt);
    J->SetNumberField(TEXT("next_shot"), S.NextShot);
    J->SetNumberField(TEXT("move_retry_at"), S.MoveRetryAt);
    J->SetNumberField(TEXT("weapon_retry_at"), S.WeaponRetryAt);
    J->SetNumberField(TEXT("search_retry_at"), S.SearchRetryAt);
    J->SetStringField(TEXT("action_generation"), LexToString(S.ActionId.Generation));
    J->SetStringField(TEXT("action_id"), LexToString(S.ActionId.Id));
    static const TCHAR* Kinds[] = {TEXT("none"), TEXT("move"), TEXT("aim"), TEXT("burst"), TEXT("reload"), TEXT("observe")};
    static const TCHAR* Outcomes[] = {TEXT("none"), TEXT("running"), TEXT("succeeded"), TEXT("canceled"), TEXT("failed")};
    static const TCHAR* Failures[] = {TEXT("none"), TEXT("replaced"), TEXT("authority"), TEXT("death"), TEXT("reset"), TEXT("stopped"), TEXT("route"), TEXT("timeout"), TEXT("weapon"), TEXT("sight"), TEXT("obstruction")};
    J->SetStringField(TEXT("action"), Kinds[static_cast<uint8>(S.Action)]);
    J->SetStringField(TEXT("action_status"), Outcomes[static_cast<uint8>(S.ActionState)]);
    J->SetStringField(TEXT("action_failure"), Failures[static_cast<uint8>(S.Failure)]);
    J->SetNumberField(TEXT("action_started"), S.ActionStarted);
    J->SetNumberField(TEXT("action_updated"), S.ActionUpdated);
    static const TCHAR* Objectives[] = {TEXT("none"), TEXT("engage_observed_threat"), TEXT("protected_observation"), TEXT("cover_engagement")};
    static const TCHAR* Phases[] = {TEXT("none"), TEXT("scanning"), TEXT("moving"), TEXT("holding"), TEXT("fallback")};
    static const TCHAR* Contacts[] = {TEXT("none"), TEXT("initial"), TEXT("continuous"), TEXT("brief_reacquisition"), TEXT("known_reacquisition"), TEXT("new_direction")};
    static const TCHAR* Gates[] = {TEXT("none"), TEXT("disabled"), TEXT("physical_authority"), TEXT("readiness"), TEXT("reload"), TEXT("contact_response"), TEXT("aim_settle"), TEXT("burst_pause"), TEXT("cadence"), TEXT("path_planning"), TEXT("travel"), TEXT("geometry_scan"), TEXT("active_observation"), TEXT("weapon_backoff"), TEXT("route_backoff"), TEXT("alignment_and_launch_safety")};
    J->SetStringField(TEXT("objective"), Objectives[static_cast<uint8>(S.Objective)]);
    J->SetStringField(TEXT("position_phase"), Phases[static_cast<uint8>(S.PositionPhase)]);
    J->SetStringField(TEXT("contact_class"), Contacts[static_cast<uint8>(S.Contact)]);
    J->SetStringField(TEXT("pending_gate"), Gates[static_cast<uint8>(S.Gate)]);
    J->SetStringField(TEXT("tactical_reason"), UTF8_TO_TCHAR(S.TacticalReason.data()));
    static const TCHAR* CoverPhases[]={TEXT("none"),TEXT("to_anchor"),TEXT("protected"),TEXT("exposing"),TEXT("aiming"),TEXT("firing"),TEXT("returning")};
    static const TCHAR* CoverSides[]={TEXT("none"),TEXT("left"),TEXT("right"),TEXT("up")};
    static const TCHAR* CoverGates[]={TEXT("none"),TEXT("geometry"),TEXT("travel"),TEXT("achieved_crouch"),TEXT("achieved_stand"),TEXT("fresh_contact"),TEXT("actual_weapon_safety"),TEXT("burst_rest"),TEXT("protected_reload"),TEXT("stale_evidence"),TEXT("return_failed"),TEXT("deadline"),TEXT("no_option")};
    static const TCHAR* Ranges[]={TEXT("no_weapon"),TEXT("hold_effective_range"),TEXT("seek_firing_lane"),TEXT("bounded_cautious_advance"),TEXT("favor_protection")};
    J->SetStringField(TEXT("cover_phase"),CoverPhases[static_cast<uint8>(S.Cover)]);
    J->SetStringField(TEXT("cover_side"),CoverSides[static_cast<uint8>(S.Side)]);
    J->SetStringField(TEXT("cover_gate"),CoverGates[static_cast<uint8>(S.CoverWait)]);
    J->SetStringField(TEXT("range_intent"),Ranges[static_cast<uint8>(S.Range)]);
    J->SetField(TEXT("cover_anchor"),JsonPosition(S.CoverAnchor));
    J->SetField(TEXT("cover_firing_pose"),JsonPosition(S.CoverPose));
    J->SetField(TEXT("cover_evidence_region"),JsonPosition(S.CoverThreat));
    J->SetStringField(TEXT("cover_owner_id"),LexToString(S.CoverOwner.Id));
    J->SetNumberField(TEXT("cover_started"),S.CoverStarted);
    J->SetNumberField(TEXT("cover_phase_started"),S.CoverPhaseAt);
    J->SetNumberField(TEXT("cover_completed_bursts"),S.CoverBursts);
    J->SetNumberField(TEXT("next_cover_scan"),S.NextCoverScan);
    J->SetBoolField(TEXT("cover_scanning"),S.CoverScanning);
    static const TCHAR* MobileNames[]={TEXT("none"),TEXT("strafe"),TEXT("cautious_approach"),TEXT("cooldown")};
    static const TCHAR* MotionNames[]={TEXT("ready"),TEXT("physical_authority"),TEXT("airborne"),TEXT("running_gait"),TEXT("speed_over_fire_limit"),TEXT("vertical_speed_over_45")};
    static const TCHAR* FireNames[]={TEXT("ready"),TEXT("authority_or_weapon"),TEXT("current_contact"),TEXT("achieved_stance"),TEXT("achieved_motion"),TEXT("rifle_pose"),TEXT("achieved_lean_geometry"),TEXT("barrel_alignment"),TEXT("muzzle_corridor")};
    J->SetStringField(TEXT("movement_action_id"),LexToString(S.MovementId.Id));
    J->SetStringField(TEXT("movement_action_status"),Outcomes[static_cast<uint8>(S.MovementState)]);
    J->SetStringField(TEXT("movement_action_failure"),Failures[static_cast<uint8>(S.MovementFailure)]);
    J->SetStringField(TEXT("mobile_phase"),MobileNames[static_cast<uint8>(S.Mobile)]);
    J->SetField(TEXT("mobile_goal"),JsonPosition(S.MobileGoal));
    J->SetNumberField(TEXT("mobile_started"),S.MobileStarted);
    J->SetNumberField(TEXT("next_mobile_at"),S.NextMobileAt);
    J->SetNumberField(TEXT("actual_ground_speed"),S.Motion.Speed);
    J->SetNumberField(TEXT("actual_vertical_speed"),S.Motion.VerticalSpeed);
    J->SetBoolField(TEXT("grounded"),S.Motion.Grounded);
    J->SetStringField(TEXT("motion_fire_gate"),MotionNames[static_cast<uint8>(S.Motion.Gate())]);
    J->SetStringField(TEXT("last_launch_gate"),FireNames[static_cast<uint8>(S.LaunchGate)]);
    J->SetNumberField(TEXT("motion_spread_degrees"),S.MovingSpread);
    J->SetNumberField(TEXT("lean_requested_degrees"),S.LeanRequested);
    J->SetNumberField(TEXT("lean_animated_degrees"),S.LeanAnimated);
    J->SetBoolField(TEXT("lean_neutral_pose_captured"),S.LeanCaptured);
    const auto Risk=CombatAI::EvaluateRisk(S.Context);
    auto Context=MakeShared<FJsonObject>();
    Context->SetBoolField(TEXT("weapon_usable"),S.Context.WeaponUsable);
    Context->SetNumberField(TEXT("weapon_capabilities"),S.Context.Weapon.Capabilities);
    Context->SetNumberField(TEXT("effective_range_cm"),S.Context.Weapon.EffectiveRange);
    Context->SetNumberField(TEXT("preferred_range_cm"),S.Context.Weapon.PreferredRange);
    Context->SetNumberField(TEXT("max_advance_step_cm"),S.Context.Weapon.AdvanceStep);
    Context->SetBoolField(TEXT("self_health_known"),S.Context.SelfHealthKnown);
    Context->SetNumberField(TEXT("self_health_fraction"),S.Context.SelfHealth);
    Context->SetBoolField(TEXT("target_health_known"),S.Context.TargetHealth.Known);
    if (S.Context.TargetHealth.Known) Context->SetNumberField(TEXT("target_health_fraction"),S.Context.TargetHealth.Fraction);
    Context->SetStringField(TEXT("target_health_evidence_id"),LexToString(S.Context.TargetHealth.EvidenceId));
    Context->SetBoolField(TEXT("allies_known"),S.Context.Allies.Known);
    if (S.Context.Allies.Known)
    {
        Context->SetNumberField(TEXT("available_allies"),S.Context.Allies.Available);
        Context->SetNumberField(TEXT("direct_fire_allies"),S.Context.Allies.Capable[0]);
        Context->SetNumberField(TEXT("cover_fire_allies"),S.Context.Allies.Capable[1]);
        Context->SetNumberField(TEXT("mobile_allies"),S.Context.Allies.Capable[2]);
    }
    Context->SetNumberField(TEXT("protection_preference"),Risk.Protection);
    Context->SetNumberField(TEXT("cautious_attack_preference"),Risk.CautiousAttack);
    J->SetObjectField(TEXT("tactical_context"),Context);
    J->SetStringField(TEXT("assignment_generation"), LexToString(S.AssignmentId.Generation));
    J->SetStringField(TEXT("assignment_id"), LexToString(S.AssignmentId.Id));
    J->SetField(TEXT("selected_position"), JsonPosition(S.SelectedPosition));
    J->SetField(TEXT("selected_facing_point"), JsonPosition(S.SelectedFacing));
    J->SetNumberField(TEXT("contact_world_time"), S.ContactAt);
    J->SetNumberField(TEXT("contact_decision_world_time"), S.ContactDecisionAt);
    J->SetNumberField(TEXT("objective_decision_world_time"), S.ObjectiveDecidedAt);
    J->SetNumberField(TEXT("scan_started_world_time"), S.ScanStartedAt);
    J->SetNumberField(TEXT("contact_not_before"), S.ContactUntil);
    J->SetNumberField(TEXT("aim_not_before"), S.AimUntil);
    J->SetNumberField(TEXT("burst_pause_not_before"), S.PauseUntil);
    J->SetNumberField(TEXT("reload_not_before"), S.ReloadUntil);
    J->SetNumberField(TEXT("hold_started_world_time"), S.HoldStartedAt);
    J->SetNumberField(TEXT("tactical_move_started_world_time"), S.MoveStartedAt);
    J->SetNumberField(TEXT("next_reassessment"), S.NextReassess);
    J->SetNumberField(TEXT("next_observation_sector"), S.NextSector);
    J->SetNumberField(TEXT("evidence_age_world_seconds"), S.EvidenceAge);
    J->SetNumberField(TEXT("position_score"), S.PositionScore);
    J->SetNumberField(TEXT("rear_side_protection"), S.Protection);
    J->SetNumberField(TEXT("threat_region_exposure"), S.Exposure);
    J->SetNumberField(TEXT("candidate_count"), S.CandidateCount);
    J->SetNumberField(TEXT("evaluated_count"), S.EvaluatedCount);
    J->SetNumberField(TEXT("rejected_count"), S.RejectedCount);
    J->SetNumberField(TEXT("tactical_transfer_attempts"), S.TransferAttempts);
    J->SetNumberField(TEXT("look_sector"), S.LookSector);
    J->SetNumberField(TEXT("geometry_queries_since_assignment"), S.GeometryQueries);
    J->SetNumberField(TEXT("peak_assessment_queries"), S.PeakAssessmentQueries);
    J->SetBoolField(TEXT("scanning"), S.Scanning); J->SetBoolField(TEXT("has_validated_position"), S.HasPosition);
    static const TCHAR* Rejections[] = {TEXT("none"), TEXT("support"), TEXT("capsule"), TEXT("route"), TEXT("facing"), TEXT("recent_failure"), TEXT("arrival")};
    auto Rejected = MakeShared<FJsonObject>();
    for (size_t I = 0; I < S.Rejections.size(); ++I) Rejected->SetNumberField(Rejections[I], S.Rejections[I]);
    J->SetObjectField(TEXT("position_rejections"), Rejected);
    J->SetNumberField(TEXT("search_candidate"), S.SearchIndex);
    J->SetStringField(TEXT("requested_gait"), S.RequestedWalk ? TEXT("walk") : TEXT("run"));
    J->SetNumberField(TEXT("movement_purpose"), static_cast<uint8>(S.Purpose));
    J->SetStringField(TEXT("intent"), StaticEnum<EEnemyCombatState>()->GetNameStringByValue(S.Intent));
    J->SetStringField(TEXT("physical_authority"), StaticEnum<EGASPEnemyAuthority>()->GetNameStringByValue(S.Authority));
    J->SetStringField(TEXT("alert"), S.Alert ? TEXT("confirmed_alert") : TEXT("unaware"));
    J->SetStringField(TEXT("evidence"), S.TargetEvidence == CombatAI::Evidence::Sight ? TEXT("direct_sight") :
        S.TargetEvidence == CombatAI::Evidence::LastSight ? TEXT("last_sight") :
        S.TargetEvidence == CombatAI::Evidence::Sound ? TEXT("uncertain_sound") :
        S.TargetEvidence == CombatAI::Evidence::Bearing ? TEXT("incoming_bearing") : TEXT("none"));
    J->SetStringField(TEXT("path_outcome"), PathName(S.Path));
    J->SetBoolField(TEXT("enabled"), S.Enabled); J->SetBoolField(TEXT("ready"), S.Ready);
    J->SetBoolField(TEXT("requested_crouch"),S.RequestedCrouch);
    J->SetBoolField(TEXT("actual_crouch"),S.ActualCrouch);
    J->SetBoolField(TEXT("retained_contact"),S.RetainedContact);
    J->SetStringField(TEXT("knowledge_revision"),LexToString(S.KnowledgeRevision));
    J->SetStringField(TEXT("sensory_event_id"),LexToString(S.DominantEvidence.Id));
    J->SetNumberField(TEXT("sensory_kind"),static_cast<uint8>(S.DominantEvidence.Kind));
    J->SetNumberField(TEXT("sensory_occurred_world"),S.DominantEvidence.OccurredWorld);
    J->SetNumberField(TEXT("sensory_received_world"),S.DominantEvidence.ReceivedWorld);
    J->SetNumberField(TEXT("sensory_simulation_time"),S.DominantEvidence.SimulationTime);
    J->SetNumberField(TEXT("uncertainty_cm"),S.DominantEvidence.Uncertainty);
    J->SetField(TEXT("sensory_region"),JsonPosition(S.DominantEvidence.Region));
    J->SetBoolField(TEXT("has_memory"), S.HasMemory); J->SetBoolField(TEXT("visible"), S.Visible);
    J->SetBoolField(TEXT("dead"), S.Dead); J->SetBoolField(TEXT("rifle_held"), S.RifleHeld);
    J->SetBoolField(TEXT("right_hand_occupied"), S.RightHandOccupied);
    J->SetNumberField(TEXT("magazine"), S.Magazine); J->SetNumberField(TEXT("shots"), S.Shots);
    J->SetNumberField(TEXT("spread_state"), S.SpreadState);
    J->SetNumberField(TEXT("path_remaining"), S.PathRemaining); J->SetNumberField(TEXT("path_failures"), S.PathFailures);
    return J;
}
}

CombatAI::InputSnapshot UEnemyCombatComponent::CaptureDecisionInput() const
{
    CombatAI::InputSnapshot S;
    S.Generation = EncounterGeneration; S.EncounterSeed = EncounterSeed;
    S.SpawnIndex = StableSpawnIndex; S.Seed = Seed;
    S.WorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0;
    S.DeltaSeconds = CaptureDeltaSeconds;
    S.SelfFeet = ValuePosition(Feet()); S.Home = ValuePosition(Home);
    // Only normalized evidence writes these memories. Never dereference Target.
    S.HasMemory = Memory.HasObservation; S.Alert = Memory.Alert; S.Visible = bTargetVisible;
    if (Memory.HasObservation)
    {
        S.KnownGround = ValuePosition(LastKnownGround); S.KnownAim = ValuePosition(LastKnownAim);
        S.LastSeenWorldTime = Memory.LastSeen; S.SightEventId = SightEventId;
        S.TargetEvidence = bTargetVisible ? CombatAI::Evidence::Sight : CombatAI::Evidence::LastSight;
        S.ActionGoal = ValuePosition(State == EEnemyCombatState::Search ? SearchGoal : PathGoal);
        S.SearchAnchor = ValuePosition(SearchAnchor); S.SearchLook = ValuePosition(SearchLook);
    }
    S.StateStarted = StateStarted; S.ReadyAt = Gates.ReadyAt(NextShot); S.NextShot = NextShot;
    S.KnowledgeRevision=Knowledge.Revision; S.RetainedContact=Knowledge.RetainsContact(S.WorldTime);
    if (const auto* H=Knowledge.Dominant(S.WorldTime,bTargetVisible))
    {
        S.DominantEvidence=H->Evidence.Get();
        if (!bTargetVisible && S.DominantEvidence.Kind!=CombatAI::Sense::Sight)
            S.TargetEvidence=S.DominantEvidence.Kind==CombatAI::Sense::Damage ? CombatAI::Evidence::Bearing : CombatAI::Evidence::Sound;
    }
    S.MoveRetryAt = MoveBackoff.Until; S.WeaponRetryAt = WeaponBackoff.Until; S.SearchRetryAt = NextTacticalScan;
    S.ActionId = Action.Token; S.Action = Action.Kind; S.ActionState = Action.Status; S.Failure = Action.Failure;
    S.ActionStarted = Action.Started; S.ActionUpdated = Action.Updated;
    S.SearchIndex = CandidateIndex; S.RequestedWalk = bRequestedWalk; S.Purpose = MovementPurpose;
    S.Objective = Assignment.Objective; S.AssignmentId = Assignment.Token; S.ObjectiveDecidedAt = Assignment.DecidedAt;
    S.PositionPhase = TacticalPhase; S.Contact = Contact; S.ContactAt = ContactAt; S.ContactDecisionAt = ContactDecisionAt;
    S.ScanStartedAt = ScanStartedAt; S.ContactUntil = Gates.ContactUntil; S.AimUntil = Gates.AimUntil;
    S.Context=Context; S.Range=RangeIntent; S.Cover=CoverPhase; S.Side=CoverPlan.Features.Side; S.CoverWait=CoverGate;
    S.CoverOwner=CoverOwner; S.CoverAnchor=ValuePosition(CoverPlan.Anchor); S.CoverPose=ValuePosition(CoverPlan.Pose);
    S.CoverThreat=ValuePosition(CoverThreatGround); S.CoverStarted=CoverStarted; S.CoverPhaseAt=CoverPhaseAt;
    S.CoverBursts=CoverBursts; S.NextCoverScan=NextCoverScan; S.CoverScanning=bCoverScan;
    S.MovementId=MoveAction.Token; S.MovementState=MoveAction.Status; S.MovementFailure=MoveAction.Failure;
    S.Mobile=MobilePhase; S.MobileGoal=ValuePosition(MobileGoal); S.MobileStarted=MobileStarted; S.NextMobileAt=NextMobileAt;
    S.LaunchGate=LastFireGate; S.LeanCaptured=bLeanPoseCaptured;
    if (const auto* E=Enemy())
    {
        S.Motion=E->GetFireMotion(); S.MovingSpread=S.Motion.SpreadCost(Tuning.MovingSpreadDegrees);
        S.LeanRequested=E->RifleLeanTarget;
        if (const auto* Anim=E->Body ? Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance()) : nullptr)
            S.LeanAnimated=Anim->RifleLeanDegrees;
    }
    S.PauseUntil = Gates.PauseUntil; S.ReloadUntil = Gates.ReloadUntil;
    S.HoldStartedAt = HoldStartedAt; S.MoveStartedAt = TacticalMoveStartedAt;
    S.NextReassess = NextTacticalScan; S.NextSector = NextLookAt;
    S.EvidenceAge = Memory.HasObservation ? FMath::Max(0.0, S.WorldTime - Memory.LastSeen) : -1;
    const auto& Position = bSelectedPosition ? SelectedPosition : HeldPosition;
    S.HasPosition = bSelectedPosition || bHeldPosition;
    S.SelectedPosition = ValuePosition(S.HasPosition ? Position.Ground : Feet());
    S.SelectedFacing = ValuePosition(bSelectedPosition ? SelectedPosition.Ground +
        SelectedPosition.FacingBasis.RotateAngleAxis(45.f*SelectedPosition.Rating.Facing,FVector::UpVector)*400 + FVector(0,0,140) :
        Assignment.Objective == CombatAI::TacticalObjective::Engage ? LastKnownAim : SearchLook);
    if (S.HasPosition) { S.PositionScore = Position.Rating.Score; S.Protection = Position.Rating.Protection; S.Exposure = Position.Rating.Exposure; }
    S.CandidateCount = TacticalCandidates.Num(); S.EvaluatedCount = CandidateIndex; S.RejectedCount = TacticalRejected;
    S.TransferAttempts = Transfers.Attempts; S.LookSector = LookSector; S.Scanning = bTacticalScan;
    S.GeometryQueries = TacticalQueryCount; S.PeakAssessmentQueries = TacticalPeakQueries; S.Rejections = RejectionCounts;
    FCStringAnsi::Strncpy(S.TacticalReason.data(), TCHAR_TO_UTF8(*TacticalReason), S.TacticalReason.size());
    S.Intent = static_cast<uint8>(State); S.Path = LastPathOutcome; S.Enabled = bEnabled;
    S.Magazine = Magazine; S.Shots = Shots; S.SpreadState = Spread.GetCurrentSeed();
    S.PathRemaining = FMath::Max(0, Path.Num() - PathIndex); S.PathFailures = PathFailures;
    if (const auto* E = Enemy())
    {
        S.Authority = static_cast<uint8>(E->Authority); S.Ready = E->IsReady(); S.Dead = E->IsDead();
        S.RifleHeld = E->IsRifleHeld(); S.RightHandOccupied = E->bRightHandOccupied;
        S.RequestedCrouch=E->bCrouchCommand; S.ActualCrouch=E->IsMovementCrouched();
    }
    using Gate = CombatAI::DecisionGate;
    if (!bEnabled || State == EEnemyCombatState::Disabled) S.Gate = Gate::Disabled;
    else if (S.Dead || S.Authority != static_cast<uint8>(EGASPEnemyAuthority::Locomotion)) S.Gate = Gate::Physics;
    else if (!S.Ready) S.Gate = Gate::Readiness;
    else if (State == EEnemyCombatState::Reload) S.Gate = Gate::Reload;
    else if (bPlanning) S.Gate = Gate::Path;
    else if (Action.Kind == CombatAI::ActionKind::Move && Action.Status == CombatAI::ActionStatus::Running) S.Gate = Gate::Travel;
    else if (State == EEnemyCombatState::Search)
        S.Gate = bTargetVisible ? (WeaponBackoff.Blocks(LastKnownGround.X, LastKnownGround.Y, S.WorldTime) ? Gate::WeaponBackoff : Gate::RouteBackoff) :
            bTacticalScan ? Gate::Scan : Gate::Observation;
    else if (S.WorldTime < Gates.ContactUntil) S.Gate = Gate::Contact;
    else if (S.WorldTime < Gates.AimUntil) S.Gate = Gate::Aim;
    else if (S.WorldTime < Gates.PauseUntil) S.Gate = Gate::BurstPause;
    else if (S.WorldTime < NextShot) S.Gate = Gate::Cadence;
    else if (State == EEnemyCombatState::Aim || State == EEnemyCombatState::Burst) S.Gate = Gate::LaunchSafety;
    return S;
}
void UEnemyCombatComponent::RecordTrace(CombatAI::Event Kind, const TCHAR* Why)
{
    DecisionTrace->Push(Kind, CaptureDecisionInput(), TCHAR_TO_UTF8(Why));
}
void UEnemyCombatComponent::RecordPath(CombatAI::PathOutcome Outcome, const TCHAR* Why)
{
    if (LastPathOutcome == Outcome && Outcome != CombatAI::PathOutcome::Failed) return;
    LastPathOutcome = Outcome;
    RecordTrace(CombatAI::Event::Path, Why);
}
void UEnemyCombatComponent::AppendObservationStatus(const TSharedRef<FJsonObject>& Root) const
{
    Root->SetNumberField(TEXT("capture_schema"), CombatAI::SchemaVersion);
    auto Settings = MakeShared<FJsonObject>();
    for (TFieldIterator<FNumericProperty> It(FEnemyCombatTuning::StaticStruct()); It; ++It)
    {
        const void* Value = It->ContainerPtrToValuePtr<void>(&Tuning);
        Settings->SetNumberField(It->GetName(), It->IsFloatingPoint() ? It->GetFloatingPointPropertyValue(Value) :
            static_cast<double>(It->GetSignedIntPropertyValue(Value)));
    }
    Root->SetObjectField(TEXT("tuning_at_status_request"), Settings);
    Root->SetObjectField(TEXT("decision_input"), SnapshotJson(CaptureDecisionInput()));
    Root->SetNumberField(TEXT("trace_capacity"), CombatAI::TraceCapacity);
    Root->SetStringField(TEXT("trace_total"), LexToString(DecisionTrace->Total()));
    Root->SetStringField(TEXT("capture_policy"), TEXT("sight-cadence input samples and events; bounded tail, not full physics replay"));
    Root->SetStringField(TEXT("fairness_channel"), TEXT("reserved separate contract; no privileged inputs collected or consumed"));
    TArray<TSharedPtr<FJsonValue>> Entries;
    for (size_t I = 0; I < DecisionTrace->Size(); ++I)
    {
        const auto& E = DecisionTrace->At(I);
        auto J = MakeShared<FJsonObject>();
        J->SetStringField(TEXT("sequence"), LexToString(E.Sequence));
        J->SetStringField(TEXT("event"), EventName(E.Kind));
        J->SetStringField(TEXT("reason"), UTF8_TO_TCHAR(E.Reason.data()));
        J->SetObjectField(TEXT("input"), SnapshotJson(E.Input));
        Entries.Add(MakeShared<FJsonValueObject>(J));
    }
    Root->SetArrayField(TEXT("decision_events"), Entries);
}
