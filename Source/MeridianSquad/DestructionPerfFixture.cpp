#include "DestructionPerfFixture.h"
#include "OpeningLobbyCharacter.h"
#include "PrototypeGrenadeComponent.h"
#include "NGDPropComponent.h"
#include "CombatProjectileWorld.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/InputComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/WorldSettings.h"
#include "Kismet/GameplayStatics.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/Parse.h"
#include "RenderTimer.h"
#include "DynamicRHI.h"
#include "RHI.h"
#include "Serialization/JsonSerializer.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
#include "ProfilingDebugging/MiscTrace.h"
#include "UnrealClient.h"

namespace
{
TArray<TSharedPtr<FJsonValue>> PropStates(UWorld* World)
{
    TArray<TSharedPtr<FJsonValue>> Rows;
    for (TActorIterator<AActor> It(World); It; ++It)
        if (auto* Prop = It->FindComponentByClass<UNGDPropComponent>())
        {
            TSharedPtr<FJsonObject> Row;
            if (FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Prop->GetState()), Row))
            {
                Row->SetStringField(TEXT("actor_name"), It->GetName());
                Row->SetStringField(TEXT("location"), It->GetActorLocation().ToString());
                Rows.Add(MakeShared<FJsonValueObject>(Row));
            }
        }
    return Rows;
}
}

ADestructionPerfFixture::ADestructionPerfFixture()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
    Marker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Charge"));
    SetRootComponent(Marker);
    Marker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Marker->SetCastShadow(false);
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Instructions"));
    Label->SetupAttachment(Marker);
    Label->SetRelativeLocation(FVector(0, 0, 55));
    Label->SetRelativeRotation(FRotator(0, -90, 0));
    Label->SetWorldSize(14);
    Label->SetHorizontalAlignment(EHTA_Center);
    Label->SetTextRenderColor(FColor(255, 180, 60));
}

void ADestructionPerfFixture::BeginPlay()
{
    Super::BeginPlay();
    Marker->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")));
    Marker->SetWorldScale3D(FVector(.22f));
    // Keep the instruction text independent of the small marker scale.
    Label->SetAbsolute(false, false, true);
    Label->SetWorldScale3D(FVector(1));
    Label->SetWorldLocation(GetActorLocation() + FVector(0, 0, 55));
    Label->SetText(FText::FromString(TEXT("F7: BLAST (2s)\nF6: RESET")));
    if (auto* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        EnableInput(PC);
        InputComponent->BindKey(EKeys::F7, IE_Pressed, this, &ADestructionPerfFixture::Arm);
    }
    History.SetNum(8192);
    Capture.Reserve(16384);
    LastTick = FPlatformTime::Seconds();
    if (FParse::Value(FCommandLine::Get(), TEXT("DestructionPerfAuto="), AutoName))
    {
        FParse::Value(FCommandLine::Get(), TEXT("DestructionPerfRepeats="), AutoRemaining);
        AutoRemaining = FMath::Clamp(AutoRemaining, 1, 5);
        AutoAt = LastTick + 12;
        if (auto* PC = UGameplayStatics::GetPlayerController(this, 0))
        {
            if (APawn* Pawn = PC->GetPawn())
            {
                Pawn->SetActorLocation(FVector(-550, -600, 90));
                if (auto* Movement = Pawn->FindComponentByClass<UCharacterMovementComponent>()) Movement->DisableMovement();
            }
            PC->SetControlRotation(FRotator(-2, 90, 0));
        }
    }
}

void ADestructionPerfFixture::Arm()
{
    if (bSpent || ArmedAt || GetWorld()->GetWorldSettings()->GetEffectiveTimeDilation() != 1.f) return;
    auto* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
    auto* Grenades = Pawn ? Pawn->FindComponentByClass<UPrototypeGrenadeComponent>() : nullptr;
    if (!Grenades) return;
    TRACE_BOOKMARK(TEXT("DestructionPerf01 Arm"));
    TRACE_BEGIN_REGION(TEXT("DestructionPerfPreBlast"));
    Metadata = MakeShared<FJsonObject>();
    Metadata->SetStringField(TEXT("schema"), TEXT("DestructionPerf01-v1"));
    Metadata->SetStringField(TEXT("run_name"), AutoName);
    Metadata->SetNumberField(TEXT("run_index"), ++AutoIndex);
    Metadata->SetStringField(TEXT("world"), GetWorld()->GetName());
    Metadata->SetStringField(TEXT("cpu"), FPlatformMisc::GetCPUBrand());
    Metadata->SetStringField(TEXT("gpu"), GRHIAdapterName);
    Metadata->SetStringField(TEXT("blast_location"), GetActorLocation().ToString());
    Metadata->SetNumberField(TEXT("blast_radius_cm"), Grenades->BlastRadius);
    Metadata->SetArrayField(TEXT("props_before"), PropStates(GetWorld()));
    Metadata->SetStringField(TEXT("thread_time_note"), TEXT("Engine global timings exclude idle, are delayed, and are not additive. GPU zero means unavailable. PIE includes editor work."));
    for (const TCHAR* Name : {TEXT("t.MaxFPS"), TEXT("r.VSync"), TEXT("r.ScreenPercentage"), TEXT("sg.EffectsQuality"), TEXT("sg.ShadowQuality"), TEXT("r.Nanite"), TEXT("fx.NiagaraComponentsEnabled")})
        if (auto* Var = IConsoleManager::Get().FindConsoleVariable(Name)) Metadata->SetStringField(Name, Var->GetString());
    if (auto* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        int32 X = 0, Y = 0; PC->GetViewportSize(X, Y);
        Metadata->SetNumberField(TEXT("viewport_width"), X);
        Metadata->SetNumberField(TEXT("viewport_height"), Y);
        FVector Eye; FRotator Rotation; PC->GetPlayerViewPoint(Eye, Rotation);
        Metadata->SetStringField(TEXT("camera_location"), Eye.ToString());
        Metadata->SetStringField(TEXT("camera_rotation"), Rotation.ToString());
    }
    if (!Grenades->SpawnFixed(GetActorLocation())) { TRACE_END_REGION(TEXT("DestructionPerfPreBlast")); Metadata.Reset(); return; }
    ArmedAt = FPlatformTime::Seconds();
    Capture.Reset();
    for (int32 I = 0; I < HistoryCount; ++I)
    {
        const FSample& S = History[(HistoryHead - HistoryCount + I + History.Num()) % History.Num()];
        if (S.Time >= ArmedAt - 7) Capture.Add(S);
    }
    bSpent = true;
    Marker->SetVisibility(false);
    Label->SetText(FText::FromString(TEXT("ARMED - 2s\nRECORDING")));
}

void ADestructionPerfFixture::MarkDetonation()
{
    if (!ArmedAt || DetonatedAt) return;
    DetonatedAt = FPlatformTime::Seconds();
    TRACE_BOOKMARK(TEXT("DestructionPerf01 Detonation"));
    TRACE_END_REGION(TEXT("DestructionPerfPreBlast"));
    TRACE_BEGIN_REGION(TEXT("DestructionPerfBlast"));
    Label->SetText(FText::FromString(TEXT("RECORDING - 15s")));
}

void ADestructionPerfFixture::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const double Now = FPlatformTime::Seconds();
    const FSample S{Now, (Now - LastTick) * 1000,
        FPlatformTime::ToMilliseconds(GGameThreadTime), FPlatformTime::ToMilliseconds(GRenderThreadTime),
        FPlatformTime::ToMilliseconds(GRHIThreadTime), FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles())};
    LastTick = Now;
    History[HistoryHead] = S;
    HistoryHead = (HistoryHead + 1) % History.Num();
    HistoryCount = FMath::Min(HistoryCount + 1, History.Num());
    if (ArmedAt)
    {
        Capture.Add(S);
        if (DetonatedAt && Now - DetonatedAt >= 15) SaveCapture(TEXT("complete"));
        else if (Now - ArmedAt > 25 || Capture.Num() >= 32768) SaveCapture(TEXT("incomplete_timeout_or_capacity"));
    }
    if (AutoAt && Now >= AutoAt) { AutoAt = 0; Arm(); }
    if (ResetAt && Now >= ResetAt)
    {
        ResetAt = 0;
        if (auto* Combat = ACombatProjectileWorld::Find(GetWorld())) Combat->ResetTargets();
        AutoAt = FPlatformTime::Seconds() + 12;
    }
    if (QuitAt && Now >= QuitAt) FPlatformMisc::RequestExit(false);
}

void ADestructionPerfFixture::SaveCapture(const FString& Outcome)
{
    if (!Metadata || !ArmedAt) return;
    if (DetonatedAt) { TRACE_END_REGION(TEXT("DestructionPerfBlast")); }
    else { TRACE_END_REGION(TEXT("DestructionPerfPreBlast")); }
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("DestructionPerf01/Captures");
    IFileManager::Get().MakeDirectory(*Directory, true);
    const FString Stem = Directory / (FDateTime::UtcNow().ToString(TEXT("%Y%m%d-%H%M%S")) + TEXT("-") + FGuid::NewGuid().ToString(EGuidFormats::Digits));
    FString CSV = TEXT("relative_seconds,frame_ms,game_ms,render_ms,rhi_ms,gpu_ms\n");
    const double Origin = DetonatedAt ? DetonatedAt : ArmedAt;
    for (const FSample& S : Capture)
        CSV += FString::Printf(TEXT("%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n"), S.Time - Origin, S.Frame, S.Game, S.Render, S.RHI, S.GPU);
    Metadata->SetStringField(TEXT("outcome"), Outcome);
    Metadata->SetBoolField(TEXT("detonation_observed"), DetonatedAt > 0);
    Metadata->SetNumberField(TEXT("fuse_real_seconds"), DetonatedAt ? DetonatedAt - ArmedAt : -1);
    Metadata->SetArrayField(TEXT("props_after"), PropStates(GetWorld()));
    FString JSON; FJsonSerializer::Serialize(Metadata.ToSharedRef(), TJsonWriterFactory<>::Create(&JSON));
    const bool Saved = FFileHelper::SaveStringToFile(CSV, *(Stem + TEXT(".csv")), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)
        && FFileHelper::SaveStringToFile(JSON, *(Stem + TEXT(".json")), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    LastOutput = Saved ? Stem : TEXT("SAVE FAILED");
    if (Saved && FParse::Param(FCommandLine::Get(), TEXT("DestructionPerfScreenshot")))
        FScreenshotRequest::RequestScreenshot(Stem + TEXT(".png"), true, false);
    UE_LOG(LogTemp, Display, TEXT("DestructionPerf01 %s %s"), *Outcome, *LastOutput);
    Label->SetText(FText::FromString(Saved ? TEXT("CAPTURE SAVED\nF6: RESET") : TEXT("CAPTURE SAVE FAILED")));
    ArmedAt = DetonatedAt = 0;
    Capture.Reset(); Metadata.Reset();
    if (!AutoName.IsEmpty())
    {
        if (--AutoRemaining > 0 && Outcome == TEXT("complete")) ResetAt = FPlatformTime::Seconds() + 2;
        else QuitAt = FPlatformTime::Seconds() + 2;
    }
}

void ADestructionPerfFixture::ResetFixture()
{
    if (ArmedAt) SaveCapture(TEXT("aborted_reset"));
    bSpent = false;
    HistoryCount = 0;
    LastTick = FPlatformTime::Seconds();
    Marker->SetVisibility(true);
    Label->SetText(FText::FromString(TEXT("F7: BLAST (2s)\nF6: RESET")));
}

void ADestructionPerfFixture::EndPlay(const EEndPlayReason::Type Reason)
{
    if (ArmedAt) SaveCapture(TEXT("aborted_end_play"));
    Super::EndPlay(Reason);
}

FString ADestructionPerfFixture::GetState() const
{
    return FString::Printf(TEXT("{\"spent\":%s,\"recording\":%s,\"detonated\":%s,\"samples\":%d,\"output\":\"%s\"}"),
        bSpent ? TEXT("true") : TEXT("false"), ArmedAt ? TEXT("true") : TEXT("false"), DetonatedAt ? TEXT("true") : TEXT("false"), Capture.Num(), *LastOutput);
}
