#include "DestructionTraceExportCommandlet.h"

#if WITH_EDITOR
#include "Common/ProviderLock.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Modules/ModuleManager.h"
#include "Serialization/JsonSerializer.h"
#include "TraceServices/AnalysisService.h"
#include "TraceServices/ITraceServicesModule.h"
#include "TraceServices/ModuleService.h"
#include "TraceServices/Model/AnalysisSession.h"
#include "TraceServices/Model/Frames.h"
#include "TraceServices/Model/Regions.h"
#include "TraceServices/Model/TasksProfiler.h"
#include "TraceServices/Model/Threads.h"
#include "TraceServices/Model/TimingProfiler.h"

namespace DestructionTraceExport
{
using FJson = TSharedPtr<FJsonObject>;

void SetTimestamp(const FJson& Json, const TCHAR* Key, double Value)
{
    if (FMath::IsFinite(Value) && Value != TraceServices::FTaskInfo::InvalidTimestamp)
    {
        Json->SetNumberField(Key, Value);
    }
    else
    {
        Json->SetField(Key, MakeShared<FJsonValueNull>());
    }
}

TArray<TSharedPtr<FJsonValue>> TaskIds(const TArray<TaskTrace::FId>& Ids)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    for (const TaskTrace::FId Id : Ids)
    {
        // Task IDs are uint64; strings avoid JSON double precision loss.
        Values.Add(MakeShared<FJsonValueString>(LexToString(Id)));
    }
    return Values;
}

TArray<TSharedPtr<FJsonValue>> Relations(const TArray<TraceServices::FTaskInfo::FRelationInfo>& Items)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    for (const auto& Item : Items)
    {
        FJson Json = MakeShared<FJsonObject>();
        Json->SetStringField(TEXT("task_id"), LexToString(Item.RelativeId));
        SetTimestamp(Json, TEXT("timestamp"), Item.Timestamp);
        Json->SetNumberField(TEXT("thread_id"), Item.ThreadId);
        Values.Add(MakeShared<FJsonValueObject>(Json));
    }
    return Values;
}

FJson FrameJson(const TraceServices::FFrame& Frame)
{
    FJson Json = MakeShared<FJsonObject>();
    Json->SetStringField(TEXT("index"), LexToString(Frame.Index));
    SetTimestamp(Json, TEXT("start"), Frame.StartTime);
    SetTimestamp(Json, TEXT("end"), Frame.EndTime);
    if (FMath::IsFinite(Frame.EndTime))
    {
        Json->SetNumberField(TEXT("duration_ms"), (Frame.EndTime - Frame.StartTime) * 1000.0);
    }
    return Json;
}
}
#endif

UDestructionTraceExportCommandlet::UDestructionTraceExportCommandlet()
{
    IsClient = false;
    IsServer = false;
    IsEditor = true;
    LogToConsole = true;
}

int32 UDestructionTraceExportCommandlet::Main(const FString& Params)
{
#if !WITH_EDITOR
    UE_LOG(LogTemp, Error, TEXT("DestructionTraceExport requires an Editor build."));
    return 1;
#else
    using namespace DestructionTraceExport;
    FString TraceFile;
    FString Output;
    FString RegionName = TEXT("DestructionPerfBlast");
    double Duration = 3.0;
    double StartOffset = 0.0;
    double MinWaitMs = 0.1;
    int32 RegionIndex = 0;
    int32 MaxTasks = 100000;
    int32 MaxWaits = 100000;
    FParse::Value(*Params, TEXT("TraceFile="), TraceFile);
    FParse::Value(*Params, TEXT("Output="), Output);
    FParse::Value(*Params, TEXT("Region="), RegionName);
    FParse::Value(*Params, TEXT("Duration="), Duration);
    FParse::Value(*Params, TEXT("StartOffset="), StartOffset);
    FParse::Value(*Params, TEXT("MinWaitMs="), MinWaitMs);
    FParse::Value(*Params, TEXT("RegionIndex="), RegionIndex);
    FParse::Value(*Params, TEXT("MaxTasks="), MaxTasks);
    FParse::Value(*Params, TEXT("MaxWaits="), MaxWaits);
    const bool bIncludeParallelFor = FParse::Param(*Params, TEXT("IncludeParallelFor"));
    if (TraceFile.IsEmpty() || Output.IsEmpty() || Duration <= 0.0 || Duration > 60.0 ||
        StartOffset < 0.0 || MinWaitMs < 0.0 || RegionIndex < 0 || MaxTasks < 1 || MaxTasks > 1000000 ||
        MaxWaits < 1 || MaxWaits > 1000000)
    {
        UE_LOG(LogTemp, Error, TEXT("Usage: -run=DestructionTraceExport -TraceFile=<utrace> -Output=<new Saved json> [-Region=DestructionPerfBlast -RegionIndex=0 -StartOffset=0 -Duration=3 -MinWaitMs=0.1 -IncludeParallelFor]"));
        return 1;
    }
    TraceFile = FPaths::ConvertRelativePathToFull(TraceFile);
    Output = FPaths::ConvertRelativePathToFull(Output);
    const FString SavedRoot = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir());
    FPaths::NormalizeFilename(TraceFile);
    FPaths::NormalizeFilename(Output);
    FPaths::CollapseRelativeDirectories(Output);
    if (!FPaths::IsUnderDirectory(Output, SavedRoot) || FPaths::FileExists(Output) ||
        IFileManager::Get().FileSize(*TraceFile) <= 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Require a completed nonempty trace and a new output file below project Saved: %s"), *Output);
        return 1;
    }

    ITraceServicesModule& TraceModule = FModuleManager::LoadModuleChecked<ITraceServicesModule>(TEXT("TraceServices"));
    // Editor-hosted analysis disables task profiling by default, unlike standalone Insights.
    const TSharedPtr<TraceServices::IModuleService> Modules = TraceModule.GetModuleService();
    Modules->SetModuleEnabled(TEXT("TraceModule_TasksProfiler"), true);
    // This bounded exporter consumes no allocation data; the capture has no memory channel.
    Modules->SetModuleEnabled(TEXT("TraceModule_Memory"), false);
    const TSharedPtr<TraceServices::IAnalysisService> Analysis = TraceModule.GetAnalysisService();
    const TSharedPtr<const TraceServices::IAnalysisSession> Session = Analysis->Analyze(*TraceFile);
    if (!Session.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Trace analysis failed: %s"), *TraceFile);
        return 2;
    }

    FJson Root = MakeShared<FJsonObject>();
    bool bTruncated = false;
    int32 NumMatchedWaits = 0;
    int32 NumTasks = 0;
    {
        TraceServices::FAnalysisSessionReadScope Scope(*Session);
        const TraceServices::ITasksProvider* Tasks = TraceServices::ReadTasksProvider(*Session);
        const TraceServices::ITimingProfilerProvider* Timing = TraceServices::ReadTimingProfilerProvider(*Session);
        if (!Tasks || !Timing || Tasks->GetNumTasks() == 0)
        {
            UE_LOG(LogTemp, Error, TEXT("Trace has no task/timing data. Capture cpu,task,region channels."));
            return 2;
        }
        const TraceServices::IThreadProvider& Threads = TraceServices::ReadThreadProvider(*Session);
        const TraceServices::ITimingProfilerTimerReader& Timers = Timing->GetTimerReader();
        const TraceServices::IRegionProvider& RegionProvider = TraceServices::ReadRegionProvider(*Session);
        const TraceServices::FProviderReadScopeLock RegionScope(RegionProvider);
        TArray<TraceServices::FTimeRegion> Matches;
        TArray<TraceServices::FTimeRegion> BlastRegions;
        TArray<TSharedPtr<FJsonValue>> RegionValues;
        RegionProvider.GetDefaultTimeline().EnumerateRegions(0.0, Session->GetDurationSeconds(),
            [&](const TraceServices::FTimeRegion& Region)
            {
                const FString Name = Region.Timer ? Region.Timer->Name : TEXT("");
                if (Name.StartsWith(TEXT("DP01_")) || Name.StartsWith(TEXT("DestructionPerf")))
                {
                    FJson Json = MakeShared<FJsonObject>();
                    Json->SetStringField(TEXT("name"), Name);
                    SetTimestamp(Json, TEXT("begin"), Region.BeginTime);
                    SetTimestamp(Json, TEXT("end"), Region.EndTime);
                    RegionValues.Add(MakeShared<FJsonValueObject>(Json));
                }
                if (Name == RegionName && FMath::IsFinite(Region.EndTime))
                {
                    Matches.Add(Region);
                }
                if (Name == TEXT("DestructionPerfBlast") && FMath::IsFinite(Region.EndTime))
                {
                    BlastRegions.Add(Region);
                }
                return true;
            });
        Matches.Sort([](const auto& A, const auto& B) { return A.BeginTime < B.BeginTime; });
        if (!Matches.IsValidIndex(RegionIndex))
        {
            UE_LOG(LogTemp, Error, TEXT("Completed region %s index %d not found (matches=%d)."), *RegionName, RegionIndex, Matches.Num());
            return 3;
        }
        const double Begin = Matches[RegionIndex].BeginTime + StartOffset;
        const double End = FMath::Min(Begin + Duration, Matches[RegionIndex].EndTime);
        if (End <= Begin)
        {
            UE_LOG(LogTemp, Error, TEXT("Requested interval is outside the completed region."));
            return 3;
        }
        Root->SetStringField(TEXT("schema"), TEXT("DP01-task-dependencies-v1"));
        Root->SetStringField(TEXT("trace_file"), TraceFile);
        Root->SetStringField(TEXT("region"), RegionName);
        Root->SetNumberField(TEXT("region_index"), RegionIndex);
        Root->SetNumberField(TEXT("interval_start_seconds"), Begin);
        Root->SetNumberField(TEXT("interval_end_seconds"), End);
        Root->SetNumberField(TEXT("minimum_wait_ms"), MinWaitMs);
        Root->SetBoolField(TEXT("include_parallel_for"), bIncludeParallelFor);
        Root->SetNumberField(TEXT("trace_task_count"), static_cast<double>(Tasks->GetNumTasks()));
        Root->SetArrayField(TEXT("regions"), RegionValues);
        const TraceServices::IFrameProvider& Frames = TraceServices::ReadFrameProvider(*Session);
        TArray<TSharedPtr<FJsonValue>> FrameValues;
        Frames.EnumerateFrames(ETraceFrameType::TraceFrameType_Game, Begin, End,
            [&](const TraceServices::FFrame& Frame)
            {
                if (Frame.EndTime > Begin && Frame.StartTime < End)
                {
                    // Preserve complete frame bounds and duration. Clipping a
                    // boundary frame would hide the very hitch being measured.
                    FrameValues.Add(MakeShared<FJsonValueObject>(FrameJson(Frame)));
                }
            });
        Root->SetArrayField(TEXT("game_frames_overlapping_interval"), FrameValues);
        Root->SetField(TEXT("blast_frame"), MakeShared<FJsonValueNull>());
        for (const TraceServices::FTimeRegion& Blast : BlastRegions)
        {
            if (Blast.BeginTime < End && Blast.EndTime > Begin)
            {
                SetTimestamp(Root, TEXT("blast_region_start_seconds"), Blast.BeginTime);
                TraceServices::FFrame Frame;
                if (Frames.GetFrameFromTime(ETraceFrameType::TraceFrameType_Game, Blast.BeginTime, Frame) &&
                    Frame.StartTime <= Blast.BeginTime && Frame.EndTime > Blast.BeginTime)
                {
                    Root->SetObjectField(TEXT("blast_frame"), FrameJson(Frame));
                }
                break;
            }
        }

        TArray<TSharedPtr<FJsonValue>> WaitValues;
        TSet<TaskTrace::FId> SelectedIds;
        TArray<TaskTrace::FId> PendingIds;
        auto SelectTask = [&](TaskTrace::FId Id)
        {
            if (Id == TaskTrace::InvalidId || SelectedIds.Contains(Id))
            {
                return;
            }
            if (SelectedIds.Num() >= MaxTasks)
            {
                bTruncated = true;
                return;
            }
            SelectedIds.Add(Id);
            PendingIds.Add(Id);
        };
        int32 NumUnmatchedWaits = 0;
        int32 NumEligibleWaits = 0;
        Threads.EnumerateThreads([&](const TraceServices::FThreadInfo& Thread)
        {
            uint32 TimelineIndex = 0;
            if (!Timing->GetCpuThreadTimelineIndex(Thread.Id, TimelineIndex))
            {
                return;
            }
            Timing->ReadTimeline(TimelineIndex, [&](const TraceServices::ITimingProfilerProvider::Timeline& Timeline)
            {
                Timeline.EnumerateEvents(Begin, End, [&](double EventBegin, double EventEnd, uint32 Depth, const TraceServices::FTimingProfilerEvent& Event)
                {
                    if ((FMath::Min(EventEnd, End) - FMath::Max(EventBegin, Begin)) * 1000.0 < MinWaitMs)
                    {
                        return TraceServices::EEventEnumerate::Continue;
                    }
                    const TraceServices::FTimingProfilerTimer* Timer = Timers.GetTimer(Event.TimerIndex);
                    if (!Timer || !Timer->Name)
                    {
                        return TraceServices::EEventEnumerate::Continue;
                    }
                    const FString TimerName(Timer->Name);
                    const bool bKnownWait = TimerName == TEXT("WaitUntilTasksComplete") || TimerName == TEXT("GameThreadWaitForTask") ||
                        TimerName == TEXT("Tasks::Wait") || TimerName == TEXT("Tasks::BusyWait");
                    const bool bNamedThreadWait = TimerName == TEXT("WaitForTasks");
                    const bool bParallelFor = bIncludeParallelFor && TimerName == TEXT("ParallelFor");
                    if (!bKnownWait && !bNamedThreadWait && !bParallelFor)
                    {
                        return TraceServices::EEventEnumerate::Continue;
                    }
                    ++NumEligibleWaits;
                    if (WaitValues.Num() >= MaxWaits)
                    {
                        bTruncated = true;
                        return TraceServices::EEventEnumerate::Continue;
                    }
                    // ProcessUntilTasksComplete records a WaitingScope inside its loop,
                    // then waits in the named thread's WaitForTasks scope. The provider
                    // accepts only four UI timer names but its lookup uses thread/time.
                    // Query that recorded waiting interval; never infer edges from overlap.
                    const TCHAR* LookupName = bNamedThreadWait ? TEXT("WaitUntilTasksComplete") : Timer->Name;
                    const TraceServices::FWaitingForTasks* Wait = Tasks->TryGetWaiting(LookupName, Thread.Id, EventBegin);
                    TArray<TaskTrace::FId> WaitedTasks;
                    if (Wait)
                    {
                        WaitedTasks = Wait->Tasks;
                    }
                    else if (bParallelFor)
                    {
                        WaitedTasks = Tasks->TryGetParallelForTasks(Timer->Name, Thread.Id, EventBegin, EventEnd);
                    }
                    FJson Json = MakeShared<FJsonObject>();
                    Json->SetStringField(TEXT("timer"), TimerName);
                    Json->SetStringField(TEXT("provider_lookup_timer"), LookupName);
                    Json->SetNumberField(TEXT("thread_id"), Thread.Id);
                    Json->SetStringField(TEXT("thread_name"), Thread.Name ? Thread.Name : TEXT(""));
                    Json->SetNumberField(TEXT("depth"), Depth);
                    SetTimestamp(Json, TEXT("event_start"), EventBegin);
                    SetTimestamp(Json, TEXT("event_end"), EventEnd);
                    Json->SetNumberField(TEXT("interval_overlap_ms"), (FMath::Min(EventEnd, End) - FMath::Max(EventBegin, Begin)) * 1000.0);
                    Json->SetStringField(TEXT("relation_source"), Wait ?
                        (bNamedThreadWait ? TEXT("TaskProvider.WaitingAtNamedThreadScope") : TEXT("TaskProvider.Waiting")) :
                        (bParallelFor ? TEXT("TaskProvider.ParallelForLaunchWindow") : TEXT("unmatched")));
                    Json->SetArrayField(TEXT("awaited_task_ids"), TaskIds(WaitedTasks));
                    if (Wait)
                    {
                        SetTimestamp(Json, TEXT("wait_start"), Wait->StartedTimestamp);
                        SetTimestamp(Json, TEXT("wait_end"), Wait->FinishedTimestamp);
                    }
                    if (const TraceServices::FTaskInfo* OwnerTask = Tasks->TryGetTask(Thread.Id, EventBegin))
                    {
                        Json->SetStringField(TEXT("waiting_task_id"), LexToString(OwnerTask->Id));
                        SelectTask(OwnerTask->Id);
                    }
                    for (const TaskTrace::FId Id : WaitedTasks)
                    {
                        SelectTask(Id);
                    }
                    if (WaitedTasks.Num() > 0) { ++NumMatchedWaits; }
                    else { ++NumUnmatchedWaits; }
                    WaitValues.Add(MakeShared<FJsonValueObject>(Json));
                    return TraceServices::EEventEnumerate::Continue;
                });
            });
        });

        TArray<TSharedPtr<FJsonValue>> TaskValues;
        TArray<TSharedPtr<FJsonValue>> MissingTasks;
        for (int32 Index = 0; Index < PendingIds.Num(); ++Index)
        {
            const TraceServices::FTaskInfo* Task = Tasks->TryGetTask(PendingIds[Index]);
            if (!Task)
            {
                MissingTasks.Add(MakeShared<FJsonValueString>(LexToString(PendingIds[Index])));
                continue;
            }
            FJson Json = MakeShared<FJsonObject>();
            Json->SetStringField(TEXT("id"), LexToString(Task->Id));
            Json->SetStringField(TEXT("name"), Task->DebugName ? Task->DebugName : TEXT(""));
            Json->SetBoolField(TEXT("tracked"), Task->bTracked);
            Json->SetNumberField(TEXT("requested_thread"), Task->ThreadToExecuteOn);
            Json->SetNumberField(TEXT("started_thread_id"), Task->StartedThreadId);
            const TCHAR* ThreadName = Threads.GetThreadName(Task->StartedThreadId);
            Json->SetStringField(TEXT("started_thread_name"), ThreadName ? ThreadName : TEXT(""));
            Json->SetNumberField(TEXT("launched_thread_id"), Task->LaunchedThreadId);
            Json->SetNumberField(TEXT("completed_thread_id"), Task->CompletedThreadId);
            SetTimestamp(Json, TEXT("created"), Task->CreatedTimestamp);
            SetTimestamp(Json, TEXT("launched"), Task->LaunchedTimestamp);
            SetTimestamp(Json, TEXT("scheduled"), Task->ScheduledTimestamp);
            SetTimestamp(Json, TEXT("started"), Task->StartedTimestamp);
            SetTimestamp(Json, TEXT("finished"), Task->FinishedTimestamp);
            SetTimestamp(Json, TEXT("completed"), Task->CompletedTimestamp);
            SetTimestamp(Json, TEXT("destroyed"), Task->DestroyedTimestamp);
            Json->SetArrayField(TEXT("prerequisites"), Relations(Task->Prerequisites));
            Json->SetArrayField(TEXT("nested_tasks"), Relations(Task->NestedTasks));
            Json->SetArrayField(TEXT("parent_tasks"), Relations(Task->ParentTasks));
            // Follow blockers only; expanding subsequents would pull future and
            // unrelated work into a bounded wait investigation.
            for (const auto& Relation : Task->Prerequisites) { SelectTask(Relation.RelativeId); }
            for (const auto& Relation : Task->NestedTasks) { SelectTask(Relation.RelativeId); }
            TaskValues.Add(MakeShared<FJsonValueObject>(Json));
        }
        NumTasks = TaskValues.Num();
        Root->SetArrayField(TEXT("waits"), WaitValues);
        Root->SetArrayField(TEXT("tasks"), TaskValues);
        Root->SetArrayField(TEXT("missing_task_ids"), MissingTasks);
        Root->SetNumberField(TEXT("eligible_wait_count"), NumEligibleWaits);
        Root->SetNumberField(TEXT("matched_wait_count"), NumMatchedWaits);
        Root->SetNumberField(TEXT("unmatched_wait_count"), NumUnmatchedWaits);
        Root->SetBoolField(TEXT("truncated"), bTruncated);
        Root->SetNumberField(TEXT("max_tasks"), MaxTasks);
        Root->SetNumberField(TEXT("max_waits"), MaxWaits);
        Root->SetStringField(TEXT("limits"), TEXT("TaskProvider edges establish waits; overlapping worker scopes alone do not. Four task wait timers, named-thread WaitForTasks and optional ParallelFor are queried. WaitForTasks uses the provider's supported-name alias with the actual scope thread/start to find recorded WaitingScope edges. Other sync/render waits remain unattributed. Prerequisite/nested closure can precede the selected interval. Nested/parallel durations must not be summed as frame time. Phase regions use observed game-tick boundaries."));
    }

    FString JsonText;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonText);
    if (!FJsonSerializer::Serialize(Root.ToSharedRef(), Writer) ||
        !IFileManager::Get().MakeDirectory(*FPaths::GetPath(Output), true) ||
        !FFileHelper::SaveStringToFile(JsonText, *Output, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        UE_LOG(LogTemp, Error, TEXT("Could not write task dependency export: %s"), *Output);
        return 4;
    }
    UE_LOG(LogTemp, Display, TEXT("DP01 dependencies: matched waits=%d tasks=%d truncated=%s output=%s"),
        NumMatchedWaits, NumTasks, bTruncated ? TEXT("true") : TEXT("false"), *Output);
    return bTruncated || NumMatchedWaits == 0 ? 5 : 0;
#endif
}
