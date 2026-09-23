#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
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
    static const TCHAR* Objectives[] = {TEXT("none"), TEXT("engage_observed_threat"), TEXT("protected_observation")};
    static const TCHAR* Phases[] = {TEXT("none"), TEXT("scanning"), TEXT("moving"), TEXT("holding"), TEXT("fallback")};
    static const TCHAR* Contacts[] = {TEXT("none"), TEXT("initial"), TEXT("continuous"), TEXT("brief_reacquisition"), TEXT("known_reacquisition"), TEXT("new_direction")};
    static const TCHAR* Gates[] = {TEXT("none"), TEXT("disabled"), TEXT("physical_authority"), TEXT("readiness"), TEXT("reload"), TEXT("contact_response"), TEXT("aim_settle"), TEXT("burst_pause"), TEXT("cadence"), TEXT("path_planning"), TEXT("travel"), TEXT("geometry_scan"), TEXT("active_observation"), TEXT("weapon_backoff"), TEXT("route_backoff"), TEXT("alignment_and_launch_safety")};
    J->SetStringField(TEXT("objective"), Objectives[static_cast<uint8>(S.Objective)]);
    J->SetStringField(TEXT("position_phase"), Phases[static_cast<uint8>(S.PositionPhase)]);
    J->SetStringField(TEXT("contact_class"), Contacts[static_cast<uint8>(S.Contact)]);
    J->SetStringField(TEXT("pending_gate"), Gates[static_cast<uint8>(S.Gate)]);
    J->SetStringField(TEXT("tactical_reason"), UTF8_TO_TCHAR(S.TacticalReason.data()));
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
        S.TargetEvidence == CombatAI::Evidence::LastSight ? TEXT("last_sight") : TEXT("none"));
    J->SetStringField(TEXT("path_outcome"), PathName(S.Path));
    J->SetBoolField(TEXT("enabled"), S.Enabled); J->SetBoolField(TEXT("ready"), S.Ready);
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
    // Only the successful sight adapter writes these memories. Never dereference Target.
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
    S.MoveRetryAt = MoveBackoff.Until; S.WeaponRetryAt = WeaponBackoff.Until; S.SearchRetryAt = NextTacticalScan;
    S.ActionId = Action.Token; S.Action = Action.Kind; S.ActionState = Action.Status; S.Failure = Action.Failure;
    S.ActionStarted = Action.Started; S.ActionUpdated = Action.Updated;
    S.SearchIndex = CandidateIndex; S.RequestedWalk = bRequestedWalk; S.Purpose = MovementPurpose;
    S.Objective = Assignment.Objective; S.AssignmentId = Assignment.Token; S.ObjectiveDecidedAt = Assignment.DecidedAt;
    S.PositionPhase = TacticalPhase; S.Contact = Contact; S.ContactAt = ContactAt; S.ContactDecisionAt = ContactDecisionAt;
    S.ScanStartedAt = ScanStartedAt; S.ContactUntil = Gates.ContactUntil; S.AimUntil = Gates.AimUntil;
    S.PauseUntil = Gates.PauseUntil; S.ReloadUntil = Gates.ReloadUntil;
    S.HoldStartedAt = HoldStartedAt; S.MoveStartedAt = TacticalMoveStartedAt;
    S.NextReassess = NextTacticalScan; S.NextSector = NextLookAt;
    S.EvidenceAge = Memory.HasObservation ? FMath::Max(0.0, S.WorldTime - Memory.LastSeen) : -1;
    const auto& Position = bSelectedPosition ? SelectedPosition : HeldPosition;
    S.HasPosition = bSelectedPosition || bHeldPosition;
    S.SelectedPosition = ValuePosition(S.HasPosition ? Position.Ground : Feet());
    S.SelectedFacing = ValuePosition(bSelectedPosition ? SelectedPosition.Ground +
        TacticalDirection(SelectedPosition.Rating.Facing)*400 + FVector(0,0,140) :
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
    DecisionTrace.Push(Kind, CaptureDecisionInput(), TCHAR_TO_UTF8(Why));
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
    Root->SetStringField(TEXT("trace_total"), LexToString(DecisionTrace.Total()));
    Root->SetStringField(TEXT("capture_policy"), TEXT("sight-cadence input samples and events; bounded tail, not full physics replay"));
    Root->SetStringField(TEXT("fairness_channel"), TEXT("reserved separate contract; no privileged inputs collected or consumed"));
    TArray<TSharedPtr<FJsonValue>> Entries;
    for (size_t I = 0; I < DecisionTrace.Size(); ++I)
    {
        const auto& E = DecisionTrace.At(I);
        auto J = MakeShared<FJsonObject>();
        J->SetStringField(TEXT("sequence"), LexToString(E.Sequence));
        J->SetStringField(TEXT("event"), EventName(E.Kind));
        J->SetStringField(TEXT("reason"), UTF8_TO_TCHAR(E.Reason.data()));
        J->SetObjectField(TEXT("input"), SnapshotJson(E.Input));
        Entries.Add(MakeShared<FJsonValueObject>(J));
    }
    Root->SetArrayField(TEXT("decision_events"), Entries);
}
