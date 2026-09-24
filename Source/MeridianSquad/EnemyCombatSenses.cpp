#include "EnemyCombatComponent.h"
#include "GASPEnemyFixture.h"
#include "Engine/World.h"
#include "Dom/JsonObject.h"
#include "DrawDebugHelpers.h"
#include "HAL/IConsoleManager.h"

namespace
{
TAutoConsoleVariable<int32> SensesDebug(TEXT("msq.EnemySenses.Debug"), 0,
    TEXT("Draw permitted hypothesis regions/bearings; no live hidden source positions."));
FVector Vector(CombatAI::Position P) { return {P.X,P.Y,P.Z}; }
}

void UEnemyCombatComponent::ReceiveStimulus(const CombatAI::Stimulus& Record)
{
    const auto* E = Enemy();
    if (!bEnabled || !E || E->IsDead() || State == EEnemyCombatState::Disabled) return;
    // Delivery is memory-only, including during physical recovery. This method
    // cannot move, fire, dereference a source actor or cancel a weapon deadline.
    auto Data = Record.Get(); Data.Observer = StableSpawnIndex;
    if (!Knowledge.Accept(CombatAI::Stimulus(Data), GetWorld()->GetTimeSeconds())) return;
    Memory.Alert = Memory.HasObservation = true;
    bEvidencePending = true;
    RecordTrace(CombatAI::Event::Stimulus, TEXT("accepted uncertain sensory evidence; pending world-time response"));
}

void UEnemyCombatComponent::ApplyEvidenceIntent(double Now)
{
    const auto* H = Knowledge.Dominant(Now,bTargetVisible);
    if (!H) return;
    const auto& S = H->Evidence.Get();
    if (SensesDebug.GetValueOnGameThread())
    {
        DrawDebugSphere(GetWorld(), Vector(S.Region)+FVector(0,0,80), FMath::Max(25.0,S.Uncertainty),
            12, FColor::Yellow, false, 0, 0, 1);
        if (S.Kind == CombatAI::Sense::Damage)
            DrawDebugDirectionalArrow(GetWorld(), Feet()+FVector(0,0,100),
                Feet()+Vector(S.Bearing)*350+FVector(0,0,100), 30, FColor::Orange, false, 0);
    }
    if (!bEvidencePending || bTargetVisible || Now < NextEvidenceResponse || State == EEnemyCombatState::Reload ||
        CoverPhase != CombatAI::CoverPhase::None || bCoverScan) return;
    if (S.Kind == CombatAI::Sense::Sight || S.Id == IntentEvidenceId) { bEvidencePending=false; return; }
    const FVector Region = Vector(S.Region);
    bEvidencePending=false; IntentEvidenceId=S.Id;
    NextEvidenceResponse=Now+.25;
    // A sound supplies only its captured region. It never becomes a fire target.
    LastKnownGround=Region; LastKnownGround.Z=Home.Z;
    LastKnownAim=LastKnownGround+FVector(0,0,130);
    if (State != EEnemyCombatState::Search || Assignment.Objective != CombatAI::TacticalObjective::ProtectedObservation)
    {
        BeginSearch(TEXT("fresh sound redirects protected investigation"));
    }
    else
    {
        // Regional updates belong to the same investigation. Keep the assignment
        // token, scan deadline/progress, movement action and finite transfer budget.
        // The cached winner and an active destination are rechecked against this
        // latest permitted region before authorizing further movement.
        SearchAnchor=LastKnownGround;
        Assignment.EvidenceId=IntentEvidenceId;
        NextHoldValidation=FMath::Min(NextHoldValidation,Now);
        if (!bTacticalScan && !bSelectedPosition)
            NextTacticalScan=FMath::Min(NextTacticalScan,Now+.25);
    }
    SearchLook=LastKnownAim; NextLookAt=Now+.35;
    Enemy()->SetRifleAimTarget(SearchLook);
    NextSight=FMath::Min(NextSight, Now+.05);
}

void UEnemyCombatComponent::AppendSensesStatus(const TSharedRef<FJsonObject>& Root) const
{
    auto J = MakeShared<FJsonObject>();
    const double Now=GetWorld()->GetTimeSeconds();
    J->SetStringField(TEXT("generation"),LexToString(Knowledge.Generation));
    J->SetStringField(TEXT("revision"),LexToString(Knowledge.Revision));
    J->SetBoolField(TEXT("contact_retained"),Knowledge.RetainsContact(Now));
    J->SetStringField(TEXT("clock_policy"),TEXT("world occurrence/receipt/reaction; projectile simulation field is separate"));
    J->SetStringField(TEXT("acoustics"),TEXT("distance and one static occlusion trace; uncertain region; no room/portal propagation"));
    TArray<TSharedPtr<FJsonValue>> Rows;
    static const TCHAR* Names[]={TEXT("sight"),TEXT("step"),TEXT("landing"),TEXT("shot"),TEXT("impact"),TEXT("incoming_bearing")};
    for (const auto& H : Knowledge.Hypotheses) if (H.Valid)
    {
        const auto& S=H.Evidence.Get(); auto Row=MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("id"),LexToString(S.Id)); Row->SetStringField(TEXT("kind"),Names[static_cast<uint8>(S.Kind)]);
        Row->SetStringField(TEXT("shot_id"),LexToString(S.Shot));
        Row->SetStringField(TEXT("projectile_generation"),LexToString(S.ProjectileGeneration));
        Row->SetNumberField(TEXT("occurred_world"),S.OccurredWorld); Row->SetNumberField(TEXT("received_world"),S.ReceivedWorld);
        Row->SetNumberField(TEXT("projectile_simulation_time"),S.SimulationTime);
        Row->SetStringField(TEXT("region"),Vector(S.Region).ToString()); Row->SetStringField(TEXT("bearing"),Vector(S.Bearing).ToString());
        Row->SetNumberField(TEXT("confidence_now"),H.ConfidenceAt(Now)); Row->SetNumberField(TEXT("uncertainty_cm"),S.Uncertainty);
        Row->SetNumberField(TEXT("known_identity"),S.KnownIdentity); Row->SetNumberField(TEXT("source_category"),static_cast<uint8>(S.Category));
        Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    J->SetArrayField(TEXT("hypotheses"),Rows); Root->SetObjectField(TEXT("senses"),J);
}
