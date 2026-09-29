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
#include "HAL/PlatformMemory.h"
#include "Misc/EngineVersion.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollectionProxyData.h"
#include "GeometryCollection/GeometryCollectionSimulationTypes.h"
#include "NiagaraComponent.h"
#include "UObject/UObjectIterator.h"
#include "AudioDevice.h"
#include "AudioDeviceHandle.h"
#include "AudioThread.h"

namespace
{
const TCHAR* PhaseNames[] = {TEXT("DP01_Intact"), TEXT("DP01_Burst"), TEXT("DP01_Early"), TEXT("DP01_Active"), TEXT("DP01_Settled")};
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
                Row->SetStringField(TEXT("actor_path"), It->GetPathName());
                Row->SetStringField(TEXT("adapter_path"), Prop->GetPathName());
                Row->SetStringField(TEXT("rotation"), It->GetActorRotation().ToString());
                Row->SetStringField(TEXT("scale"), It->GetActorScale3D().ToString());
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
    bDiagnostics = FParse::Param(FCommandLine::Get(), TEXT("DestructionPerfDiagnostics"));
    if (bDiagnostics) AudioObservation = MakeShared<FAudioObservation, ESPMode::ThreadSafe>();
    RefreshProps();
    if (FParse::Value(FCommandLine::Get(), TEXT("DestructionPerfAuto="), AutoName))
    {
        FParse::Value(FCommandLine::Get(), TEXT("DestructionPerfRepeats="), AutoRemaining);
        AutoRemaining = FMath::Clamp(AutoRemaining, 1, 5);
        AutoAt = LastTick + 12;
        if (auto* PC = UGameplayStatics::GetPlayerController(this, 0))
        {
            PC->SetIgnoreLookInput(true);
            PC->SetIgnoreMoveInput(true);
            if (APawn* Pawn = PC->GetPawn())
            {
                Pawn->SetActorLocation(FVector(-550, -600, 90));
                if (auto* Movement = Pawn->FindComponentByClass<UCharacterMovementComponent>()) Movement->DisableMovement();
            }
            PC->SetControlRotation(FRotator(-2, 90, 0));
        }
    }
}

void ADestructionPerfFixture::RefreshProps()
{
    Props.Reset();
    PreviousActive.Reset();
    ObservedActivations.Reset();
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
        if (auto* Prop = It->FindComponentByClass<UNGDPropComponent>()) Props.Add(Prop);
}

void ADestructionPerfFixture::SetPhase(int32 NewPhase)
{
    if (Phase == NewPhase) return;
    if (Phase >= 0) { TRACE_END_REGION(PhaseNames[Phase]); }
    Phase = NewPhase;
    if (Phase >= 0)
    {
        TRACE_BEGIN_REGION(PhaseNames[Phase]);
        TRACE_BOOKMARK(TEXT("DP01 Phase %s run=%d"), PhaseNames[Phase], AutoIndex);
        if (Metadata)
            Metadata->SetNumberField(FString(PhaseNames[Phase]) + TEXT("_platform_seconds"), FPlatformTime::Seconds());
    }
}

void ADestructionPerfFixture::SampleDiagnostics()
{
    TRACE_CPUPROFILER_EVENT_SCOPE(DP01_SampleDiagnostics);
    const FPlatformMemoryStats Memory = FPlatformMemory::GetStats();
    Diagnostics.PhysicalBytes = Memory.UsedPhysical;
    Diagnostics.VirtualBytes = Memory.UsedVirtual;
    Diagnostics.PeakPhysicalBytes = Memory.PeakUsedPhysical;
    Diagnostics.ActiveTransforms = Diagnostics.SleepingTransforms = Diagnostics.DynamicTransforms = 0;
    Diagnostics.ObservedActivations = 0;
    for (const auto& WeakProp : Props)
        if (const auto* Prop = WeakProp.Get())
            if (const auto* Collection = Prop->GetOwner()->FindComponentByClass<UGeometryCollectionComponent>())
                if (const auto* Dynamic = Collection->GetDynamicCollection())
                {
                    const FString Key = Prop->GetOwner()->GetPathName() + TEXT("|") + Prop->ObjectId.ToString();
                    TBitArray<>& Previous = PreviousActive.FindOrAdd(Key);
                    const bool bHasPrevious = Previous.Num() == Dynamic->Active.Num();
                    if (!bHasPrevious) Previous.Init(false, Dynamic->Active.Num());
                    int32& Activations = ObservedActivations.FindOrAdd(Key);
                    for (int32 Index = 0; Index < Dynamic->Active.Num(); ++Index)
                    {
                        if (bHasPrevious && !Previous[Index] && Dynamic->Active[Index]) ++Activations;
                        Previous[Index] = Dynamic->Active[Index];
                        if (!Dynamic->Active[Index]) continue;
                        ++Diagnostics.ActiveTransforms;
                        const int32 State = Dynamic->DynamicState[Index];
                        if (State == static_cast<int32>(EObjectStateTypeEnum::Chaos_Object_Sleeping)) ++Diagnostics.SleepingTransforms;
                        if (State == static_cast<int32>(EObjectStateTypeEnum::Chaos_Object_Dynamic)) ++Diagnostics.DynamicTransforms;
                    }
                    Diagnostics.ObservedActivations += Activations;
                }
    Diagnostics.NiagaraComponents = 0;
    for (TObjectIterator<UNiagaraComponent> It; It; ++It)
        if (It->GetWorld() == GetWorld() && It->IsActive()) ++Diagnostics.NiagaraComponents;
    if (const FAudioDeviceHandle Device = GetWorld()->GetAudioDevice(); Device.IsValid())
    {
        // Audio state belongs to its thread. The shared result outlives the fixture if a command is pending.
        auto Observation = AudioObservation;
        FAudioThread::RunCommandOnAudioThread([Device, Observation]()
        {
            Observation->Sources.Store(Device->GetNumActiveSources());
        });
        Diagnostics.AudioSources = Observation->Sources.Load();
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
    Metadata->SetStringField(TEXT("schema"), TEXT("DestructionPerf01-v2"));
    Metadata->SetStringField(TEXT("run_name"), AutoName);
    Metadata->SetNumberField(TEXT("run_index"), ++AutoIndex);
    Metadata->SetStringField(TEXT("engine"), FEngineVersion::Current().ToString());
    Metadata->SetBoolField(TEXT("diagnostics_enabled"), bDiagnostics);
    FString TraceChannels, CandidateCommit, WorkloadIdentity;
    FParse::Value(FCommandLine::Get(), TEXT("trace="), TraceChannels);
    FParse::Value(FCommandLine::Get(), TEXT("DestructionPerfCommit="), CandidateCommit);
    FParse::Value(FCommandLine::Get(), TEXT("DestructionPerfIdentity="), WorkloadIdentity);
    Metadata->SetBoolField(TEXT("trace_enabled"), !TraceChannels.IsEmpty() && TraceChannels != TEXT("none"));
    Metadata->SetStringField(TEXT("trace_channels"), TraceChannels);
    Metadata->SetBoolField(TEXT("named_events_enabled"), FParse::Param(FCommandLine::Get(), TEXT("statnamedevents")));
    Metadata->SetStringField(TEXT("candidate_commit"), CandidateCommit);
    Metadata->SetStringField(TEXT("workload_identity"), WorkloadIdentity);
    Metadata->SetStringField(TEXT("counter_note"), TEXT("break_events are cumulative notifications. Diagnostic memory is process bytes sampled at most 10Hz; peaks are process lifetime, not allocations. GC transforms are game-thread mirrored Active/DynamicState, not solver body counts. observed_transform_activations counts sampled false-to-true transitions since reset; a lower bound, not exact newly released bodies. Niagara is IsActive world components, not particles. audio_active_sources is asynchronous audio-thread device source count, delayed by at least one diagnostic sample. Missing values are -1 (memory zero when disabled). Contacts use solver trace counters where available."));
    Metadata->SetStringField(TEXT("phase_note"), TEXT("CSV DP01 phases use sample-end real time. Trace DP01_Intact covers armed fuse only; later regions change at first fixture tick crossing .5/3/10 seconds, so boundaries may overshoot. frame_ms is consecutive fixture tick delta, not exact engine-frame duration. Engine timings are delayed. Save/serialization excluded."));
    Metadata->SetStringField(TEXT("world"), GetWorld()->GetName());
    Metadata->SetStringField(TEXT("cpu"), FPlatformMisc::GetCPUBrand());
    Metadata->SetStringField(TEXT("gpu"), GRHIAdapterName);
    Metadata->SetStringField(TEXT("blast_location"), GetActorLocation().ToString());
    Metadata->SetNumberField(TEXT("blast_radius_cm"), Grenades->BlastRadius);
    Metadata->SetArrayField(TEXT("props_before"), PropStates(GetWorld()));
    Metadata->SetStringField(TEXT("thread_time_note"), TEXT("Engine global timings exclude idle, are delayed, and are not additive. GPU zero means unavailable. PIE includes editor work."));
    for (const TCHAR* Name : {TEXT("t.MaxFPS"), TEXT("r.VSync"), TEXT("r.ScreenPercentage"), TEXT("sg.ViewDistanceQuality"), TEXT("sg.AntiAliasingQuality"), TEXT("sg.PostProcessQuality"), TEXT("sg.EffectsQuality"), TEXT("sg.ShadowQuality"), TEXT("sg.GlobalIlluminationQuality"), TEXT("sg.ReflectionQuality"), TEXT("sg.TextureQuality"), TEXT("sg.FoliageQuality"), TEXT("sg.ShadingQuality"), TEXT("r.Nanite"), TEXT("fx.NiagaraComponentsEnabled")})
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
    ArmedSimulation = GetWorld()->GetTimeSeconds();
    Metadata->SetNumberField(TEXT("armed_platform_seconds"), ArmedAt);
    Metadata->SetNumberField(TEXT("armed_simulation_seconds"), ArmedSimulation);
    SetPhase(0);
    TRACE_BOOKMARK(TEXT("DP01 Start run=%d real=%.6f sim=%.6f"), AutoIndex, ArmedAt, ArmedSimulation);
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
    DetonatedSimulation = GetWorld()->GetTimeSeconds();
    Metadata->SetNumberField(TEXT("detonation_platform_seconds"), DetonatedAt);
    Metadata->SetNumberField(TEXT("detonation_simulation_seconds"), DetonatedSimulation);
    Metadata->SetNumberField(TEXT("detonation_engine_frame"), static_cast<double>(GFrameCounter));
    SetPhase(1);
    TRACE_BOOKMARK(TEXT("DP01 Blast run=%d frame=%llu real=%.6f sim=%.6f"), AutoIndex, GFrameCounter, DetonatedAt, DetonatedSimulation);
    TRACE_BOOKMARK(TEXT("DestructionPerf01 Detonation"));
    TRACE_END_REGION(TEXT("DestructionPerfPreBlast"));
    TRACE_BEGIN_REGION(TEXT("DestructionPerfBlast"));
    Label->SetText(FText::FromString(TEXT("RECORDING - 15s")));
}

void ADestructionPerfFixture::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bRefreshProps) { RefreshProps(); bRefreshProps = false; }
    const double Now = FPlatformTime::Seconds();
    FSample S{Now, (Now - LastTick) * 1000,
        FPlatformTime::ToMilliseconds(GGameThreadTime), FPlatformTime::ToMilliseconds(GRenderThreadTime),
        FPlatformTime::ToMilliseconds(GRHIThreadTime), FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles())};
    S.EngineFrame = GFrameCounter;
    S.Simulation = GetWorld()->GetTimeSeconds();
    for (const auto& Prop : Props) if (Prop.IsValid()) S.BreakEvents += Prop->BreakEvents;
    if (bDiagnostics)
    {
        S.bDiagnosticSample = Now >= NextDiagnosticAt;
        if (S.bDiagnosticSample) { SampleDiagnostics(); NextDiagnosticAt = Now + .1; }
        S.PhysicalBytes = Diagnostics.PhysicalBytes; S.VirtualBytes = Diagnostics.VirtualBytes;
        S.PeakPhysicalBytes = Diagnostics.PeakPhysicalBytes;
        S.ActiveTransforms = Diagnostics.ActiveTransforms; S.SleepingTransforms = Diagnostics.SleepingTransforms;
        S.DynamicTransforms = Diagnostics.DynamicTransforms; S.NiagaraComponents = Diagnostics.NiagaraComponents;
        S.ObservedActivations = Diagnostics.ObservedActivations; S.AudioSources = Diagnostics.AudioSources;
    }
    LastTick = Now;
    History[HistoryHead] = S;
    HistoryHead = (HistoryHead + 1) % History.Num();
    HistoryCount = FMath::Min(HistoryCount + 1, History.Num());
    if (ArmedAt)
    {
        Capture.Add(S);
        if (DetonatedAt)
        {
            const double Elapsed = Now - DetonatedAt;
            SetPhase(Elapsed >= 10 ? 4 : Elapsed >= 3 ? 3 : Elapsed >= .5 ? 2 : 1);
        }
        if (DetonatedAt && Now - DetonatedAt >= 15) SaveCapture(TEXT("complete"));
        else if (Now - ArmedAt > 25 || Capture.Num() >= 32768) SaveCapture(TEXT("incomplete_timeout_or_capacity"));
    }
    if (AutoAt && Now >= AutoAt) { AutoAt = 0; Arm(); }
    if (ResetAt && Now >= ResetAt)
    {
        ResetAt = 0;
        if (auto* Combat = ACombatProjectileWorld::Find(GetWorld())) Combat->ResetTargets();
        RefreshProps();
        AutoAt = FPlatformTime::Seconds() + 12;
    }
    if (QuitAt && Now >= QuitAt) FPlatformMisc::RequestExit(false);
}

void ADestructionPerfFixture::SaveCapture(const FString& Outcome)
{
    if (!Metadata || !ArmedAt) return;
    SetPhase(-1);
    TRACE_BOOKMARK(TEXT("DP01 Complete run=%d outcome=%s"), AutoIndex, *Outcome);
    Metadata->SetNumberField(TEXT("completion_platform_seconds"), FPlatformTime::Seconds());
    Metadata->SetNumberField(TEXT("completion_simulation_seconds"), GetWorld()->GetTimeSeconds());
    if (DetonatedAt) { TRACE_END_REGION(TEXT("DestructionPerfBlast")); }
    else { TRACE_END_REGION(TEXT("DestructionPerfPreBlast")); }
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("DestructionPerf01/DP-01/Captures");
    IFileManager::Get().MakeDirectory(*Directory, true);
    const FString Stem = Directory / (FDateTime::UtcNow().ToString(TEXT("%Y%m%d-%H%M%S")) + TEXT("-") + FGuid::NewGuid().ToString(EGuidFormats::Digits));
    FString CSV = TEXT("relative_seconds,frame_ms,game_ms,render_ms,rhi_ms,gpu_ms,engine_frame,simulation_seconds,break_events,diagnostic_sample,process_physical_bytes,process_virtual_bytes,process_peak_physical_bytes,gc_active_transforms,gc_sleeping_transforms,gc_dynamic_transforms,niagara_active_components,observed_transform_activations,audio_active_sources\n");
    const double Origin = DetonatedAt ? DetonatedAt : ArmedAt;
    for (const FSample& S : Capture)
        CSV += FString::Printf(TEXT("%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%llu,%.6f,%d,%d,%llu,%llu,%llu,%d,%d,%d,%d,%d,%d\n"),
            S.Time - Origin, S.Frame, S.Game, S.Render, S.RHI, S.GPU, S.EngineFrame,
            S.Simulation - (DetonatedAt ? DetonatedSimulation : ArmedSimulation), S.BreakEvents, S.bDiagnosticSample ? 1 : 0,
            S.PhysicalBytes, S.VirtualBytes, S.PeakPhysicalBytes, S.ActiveTransforms, S.SleepingTransforms, S.DynamicTransforms, S.NiagaraComponents, S.ObservedActivations, S.AudioSources);
    Metadata->SetStringField(TEXT("outcome"), Outcome);
    Metadata->SetBoolField(TEXT("detonation_observed"), DetonatedAt > 0);
    Metadata->SetNumberField(TEXT("fuse_real_seconds"), DetonatedAt ? DetonatedAt - ArmedAt : -1);
    Metadata->SetArrayField(TEXT("props_after"), PropStates(GetWorld()));
    if (auto* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        FVector Eye; FRotator Rotation; PC->GetPlayerViewPoint(Eye, Rotation);
        Metadata->SetStringField(TEXT("camera_location_after"), Eye.ToString());
        Metadata->SetStringField(TEXT("camera_rotation_after"), Rotation.ToString());
    }
    auto Activations = MakeShared<FJsonObject>();
    for (const auto& Entry : ObservedActivations) Activations->SetNumberField(Entry.Key, Entry.Value);
    Metadata->SetObjectField(TEXT("observed_transform_activations_by_actor_path_and_adapter_id"), Activations);
    FString JSON; FJsonSerializer::Serialize(Metadata.ToSharedRef(), TJsonWriterFactory<>::Create(&JSON));
    const bool Saved = FFileHelper::SaveStringToFile(CSV, *(Stem + TEXT(".csv")), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)
        && FFileHelper::SaveStringToFile(JSON, *(Stem + TEXT(".json")), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    LastOutput = Saved ? Stem : TEXT("SAVE FAILED");
    if (Saved && FParse::Param(FCommandLine::Get(), TEXT("DestructionPerfScreenshot")))
        FScreenshotRequest::RequestScreenshot(Stem + TEXT(".png"), true, false);
    UE_LOG(LogTemp, Display, TEXT("DestructionPerf01 %s %s"), *Outcome, *LastOutput);
    Label->SetText(FText::FromString(Saved ? TEXT("CAPTURE SAVED\nF6: RESET") : TEXT("CAPTURE SAVE FAILED")));
    ArmedAt = DetonatedAt = 0;
    ArmedSimulation = DetonatedSimulation = 0;
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
    // ResetTargets replaces the props after this call; refresh on the next fixture tick.
    bRefreshProps = true;
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
