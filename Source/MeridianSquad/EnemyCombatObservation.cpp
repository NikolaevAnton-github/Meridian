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
    case CombatAI::PathOutcome::Following: return TEXT("following_walk");
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
    J->SetNumberField(TEXT("last_seen_world_time"), S.LastSeenWorldTime);
    J->SetStringField(TEXT("sight_event_id"), LexToString(S.SightEventId));
    J->SetNumberField(TEXT("state_started"), S.StateStarted);
    J->SetNumberField(TEXT("ready_at"), S.ReadyAt);
    J->SetNumberField(TEXT("next_shot"), S.NextShot);
    J->SetNumberField(TEXT("ignore_sight_until"), S.IgnoreSightUntil);
    J->SetStringField(TEXT("intent"), StaticEnum<EEnemyCombatState>()->GetNameStringByValue(S.Intent));
    J->SetStringField(TEXT("physical_authority"), StaticEnum<EGASPEnemyAuthority>()->GetNameStringByValue(S.Authority));
    J->SetStringField(TEXT("alert"), S.HasMemory ? TEXT("legacy_memory_present") : TEXT("legacy_no_memory"));
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
    S.HasMemory = bHasMemory; S.Visible = bTargetVisible;
    if (bHasMemory)
    {
        S.KnownGround = ValuePosition(LastKnownGround); S.KnownAim = ValuePosition(LastKnownAim);
        S.LastSeenWorldTime = LastSeen; S.SightEventId = SightEventId;
        S.TargetEvidence = bTargetVisible ? CombatAI::Evidence::Sight : CombatAI::Evidence::LastSight;
    }
    S.StateStarted = StateStarted; S.ReadyAt = ReadyAt; S.NextShot = NextShot; S.IgnoreSightUntil = IgnoreSightUntil;
    S.Intent = static_cast<uint8>(State); S.Path = LastPathOutcome; S.Enabled = bEnabled;
    S.Magazine = Magazine; S.Shots = Shots; S.SpreadState = Spread.GetCurrentSeed();
    S.PathRemaining = FMath::Max(0, Path.Num() - PathIndex); S.PathFailures = PathFailures;
    if (const auto* E = Enemy())
    {
        S.Authority = static_cast<uint8>(E->Authority); S.Ready = E->IsReady(); S.Dead = E->IsDead();
        S.RifleHeld = E->IsRifleHeld(); S.RightHandOccupied = E->bRightHandOccupied;
    }
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
