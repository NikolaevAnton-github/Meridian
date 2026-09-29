<#
.SYNOPSIS
Exports completed DestructionPerf01 traces with headless Unreal Insights.
.EXAMPLE
./Scripts/DestructionPerf01/export_trace.ps1 -Name trace03 -OutputDirectory Saved/DestructionPerf01/trace03-insights -ExpectedRepeats 2 -IncludeThreads
.EXAMPLE
./Scripts/DestructionPerf01/export_trace.ps1 -Name dp01_trace01 -OutputDirectory Saved/DestructionPerf01/DP-01/trace01-warm -RegionBoundsPath Saved/DestructionPerf01/DP-01/dependencies01/warm15.json -RegionIndex 1 -Regions DP01_Burst,DP01_Early -IncludeTimingEvents
.NOTES
Run after the measured game has exited. The trace must contain the native
DestructionPerfPreBlast and DestructionPerfBlast regions (build03 or newer).
The preblast region is the two-second fuse, not the five-second CSV baseline.
UE 5.8's timer-statistics exporter always includes GPU timelines. The game-*
files therefore contain GameThread CPU scopes plus GPU scopes, not pure CPU.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [string]$Engine = 'D:/UE_5.8',
    [string]$TracePath,
    [ValidatePattern('^[A-Za-z0-9_]+$')]
    [string[]]$Regions = @('DestructionPerfPreBlast', 'DestructionPerfBlast'),
    [string]$RegionBoundsPath,
    [ValidateRange(0, 99)]
    [int]$RegionIndex = 0,
    [switch]$IncludeThreads,
    [switch]$IncludeTimingEvents,
    [switch]$IncludeCounterValues,
    [ValidatePattern('^[A-Za-z0-9_/*?:, .()-]+$')]
    [string]$CounterFilter = 'Chaos/*,DP01/*,STAT_AudioSources*,STAT_AudioVirtualLoops*,STAT_TotalLLM,STAT_WorkingSetSizeLLM,STAT_PagefileUsedLLM,Trace/Memory/*',
    [ValidateRange(1, 100)]
    [int]$ExpectedRepeats = 1,
    [ValidateRange(10, 3600)]
    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$SavedRoot = [IO.Path]::GetFullPath((Join-Path $ProjectRoot 'Saved')).TrimEnd('\', '/')
if (-not $TracePath) {
    $CurrentTrace = Join-Path $SavedRoot "DestructionPerf01/DP-01/$Name.utrace"
    $LegacyTrace = Join-Path $SavedRoot "DestructionPerf01/$Name.utrace"
    if ((Test-Path -LiteralPath $CurrentTrace) -and (Test-Path -LiteralPath $LegacyTrace)) {
        throw 'Both current and legacy traces exist; specify -TracePath explicitly.'
    }
    $TracePath = if (Test-Path -LiteralPath $CurrentTrace) { $CurrentTrace } else { $LegacyTrace }
}
elseif (-not [IO.Path]::IsPathRooted($TracePath)) { $TracePath = Join-Path $ProjectRoot $TracePath }
$TracePath = [IO.Path]::GetFullPath($TracePath)
$Executable = Join-Path $Engine 'Engine/Binaries/Win64/UnrealInsights.exe'
if (-not (Test-Path -LiteralPath $TracePath -PathType Leaf)) { throw "Trace does not exist: $TracePath" }
if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) { throw "Unreal Insights does not exist: $Executable" }
if ((Get-Item -LiteralPath $TracePath).Length -eq 0) { throw "Trace is empty: $TracePath" }
if (Get-Process -Name UnrealEditor, UnrealEditor-Cmd, UnrealInsights -ErrorAction SilentlyContinue) {
    throw 'Finish the measured game/editor run and any existing Insights analysis before exporting.'
}

# Native task exports retain exact provider region boundaries even when their
# task interval was shortened. Select one occurrence without exporting all runs.
$SelectedBounds = @{}
$BoundsProvenance = $null
if ($RegionBoundsPath) {
    if ($ExpectedRepeats -ne 1) { throw '-RegionBoundsPath requires -ExpectedRepeats 1.' }
    if (-not [IO.Path]::IsPathRooted($RegionBoundsPath)) { $RegionBoundsPath = Join-Path $ProjectRoot $RegionBoundsPath }
    $RegionBoundsPath = (Resolve-Path -LiteralPath $RegionBoundsPath).Path
    $NativeBounds = Get-Content -LiteralPath $RegionBoundsPath -Raw | ConvertFrom-Json
    if (-not $NativeBounds.trace_file) { throw 'Native bounds source has no trace_file.' }
    $NativeTracePath = [string]$NativeBounds.trace_file
    if (-not [IO.Path]::IsPathRooted($NativeTracePath)) { $NativeTracePath = Join-Path $ProjectRoot $NativeTracePath }
    $NativeTracePath = (Resolve-Path -LiteralPath $NativeTracePath).Path
    if (-not $NativeTracePath.Equals((Resolve-Path -LiteralPath $TracePath).Path, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Native region bounds must come from the same trace as -TracePath.'
    }
    foreach ($Region in $Regions) {
        $Occurrences = @($NativeBounds.regions | Where-Object { $_.name -ceq $Region } | Sort-Object { [double]$_.begin })
        if ($RegionIndex -ge $Occurrences.Count) { throw "Missing occurrence $RegionIndex of region $Region in $RegionBoundsPath" }
        $Selected = $Occurrences[$RegionIndex]
        if ($null -eq $Selected.begin -or $null -eq $Selected.end) { throw "Incomplete boundaries for $Region occurrence $RegionIndex" }
        $Begin = [double]$Selected.begin
        $End = [double]$Selected.end
        if ([double]::IsNaN($Begin) -or [double]::IsInfinity($Begin) -or [double]::IsNaN($End) -or [double]::IsInfinity($End) -or $End -le $Begin) {
            throw "Invalid boundaries for $Region occurrence $RegionIndex"
        }
        $SelectedBounds[$Region] = [ordered]@{ region = $Region; region_index = $RegionIndex; start_seconds = $Begin; end_seconds = $End }
    }
    $BoundsProvenance = [ordered]@{ path = $RegionBoundsPath; sha256 = (Get-FileHash -LiteralPath $RegionBoundsPath -Algorithm SHA256).Hash; trace_file = $NativeTracePath; region_index = $RegionIndex }
}
elseif ($PSBoundParameters.ContainsKey('RegionIndex')) { throw '-RegionIndex requires -RegionBoundsPath.' }

if (-not [IO.Path]::IsPathRooted($OutputDirectory)) {
    $OutputDirectory = Join-Path $ProjectRoot $OutputDirectory
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd('\', '/')
$SavedPrefix = $SavedRoot + [IO.Path]::DirectorySeparatorChar
if (-not $OutputDirectory.StartsWith($SavedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Output directory must be a new directory under $SavedRoot"
}
if (Test-Path -LiteralPath $OutputDirectory) {
    throw "Refusing to overwrite or reuse an existing output directory: $OutputDirectory"
}
# Reject a redirected ancestor inside Saved so the lexical containment check
# cannot route export evidence through a junction or symbolic link.
$Ancestor = Split-Path -Parent $OutputDirectory
while ($Ancestor.StartsWith($SavedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    if (Test-Path -LiteralPath $Ancestor) {
        if (((Get-Item -LiteralPath $Ancestor).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Output ancestor is a filesystem redirect: $Ancestor"
        }
    }
    $Ancestor = Split-Path -Parent $Ancestor
}
New-Item -ItemType Directory -Path $OutputDirectory | Out-Null

$ResponsePath = Join-Path $OutputDirectory 'exports.rsp'
$LogPath = Join-Path $OutputDirectory 'insights.log'
$ExpectedFiles = [Collections.Generic.List[string]]::new()
$ExportCommands = [Collections.Generic.List[string]]::new()
foreach ($Region in $Regions) {
    $IntervalArgs = "-region=$Region"
    if ($RegionBoundsPath) {
        $Bound = $SelectedBounds[$Region]
        $IntervalArgs = '-startTime={0} -endTime={1}' -f $Bound.start_seconds.ToString('G17', [Globalization.CultureInfo]::InvariantCulture), $Bound.end_seconds.ToString('G17', [Globalization.CultureInfo]::InvariantCulture)
    }
    foreach ($ThreadScope in @('all', 'game')) {
        # A region placeholder also preserves separate exports if the native
        # trace happens to contain repeated intervals of the same region.
        $Filename = if ($RegionBoundsPath) { "$ThreadScope-$Region.csv" } else { "$ThreadScope-{region}.csv" }
        $Pattern = (Join-Path $OutputDirectory $Filename).Replace('\', '/')
        $ThreadFilter = if ($ThreadScope -eq 'game') { 'GameThread' } else { '*' }
        $ExportCommands.Add(('TimingInsights.ExportTimerStatistics "{0}" {1} -threads={2} -sortBy=TotalInclusiveTime -sortOrder=Descending' -f $Pattern, $IntervalArgs, $ThreadFilter))
        for ($RepeatIndex = 0; $RepeatIndex -lt $ExpectedRepeats; $RepeatIndex++) {
            $RegionSuffix = if ($RepeatIndex -eq 0) { '' } else { "_$RepeatIndex" }
            $ExpectedFiles.Add((Join-Path $OutputDirectory "$ThreadScope-$Region$RegionSuffix.csv"))
        }
    }
    if ($IncludeTimingEvents) {
        # Unlike ExportTimerStatistics, this exporter honors all CPU/GPU thread
        # filters and preserves thread IDs. Export every timer so later exclusive
        # time reconstruction never mistakes omitted child scopes for self time.
        $EventsFilename = if ($RegionBoundsPath) { "events-$Region.csv" } else { 'events-{region}.csv' }
        $EventsPattern = (Join-Path $OutputDirectory $EventsFilename).Replace('\', '/')
        $ExportCommands.Add(('TimingInsights.ExportTimingEvents "{0}" {1} -columns=ThreadId,ThreadName,TimerId,TimerName,StartTime,EndTime,Duration,Depth' -f $EventsPattern, $IntervalArgs))
        if ($RegionBoundsPath) { $SelectedBounds[$Region].path = $EventsPattern }
        for ($RepeatIndex = 0; $RepeatIndex -lt $ExpectedRepeats; $RepeatIndex++) {
            $RegionSuffix = if ($RepeatIndex -eq 0) { '' } else { "_$RepeatIndex" }
            $ExpectedFiles.Add((Join-Path $OutputDirectory "events-$Region$RegionSuffix.csv"))
        }
    }
}
$CountersPath = (Join-Path $OutputDirectory 'counters.csv').Replace('\', '/')
# UE 5.8 passes the complete remaining command to ExportCountersAsText as its
# filename, without tokenization or quote removal. Keep this path unquoted.
$ExportCommands.Add("TimingInsights.ExportCounters $CountersPath")
$ExpectedFiles.Add($CountersPath)
if ($IncludeThreads -or $IncludeTimingEvents) {
    $ThreadsPath = (Join-Path $OutputDirectory 'threads.csv').Replace('\', '/')
    $ExportCommands.Add(('TimingInsights.ExportThreads "{0}"' -f $ThreadsPath))
    $ExpectedFiles.Add($ThreadsPath)
}
if ($IncludeTimingEvents) {
    $TimersPath = (Join-Path $OutputDirectory 'timers.csv').Replace('\', '/')
    $ExportCommands.Add(('TimingInsights.ExportTimers "{0}"' -f $TimersPath))
    $ExpectedFiles.Add($TimersPath)
}
if ($IncludeCounterValues) {
    # Capture-wide values preserve the value preceding a region boundary. Counter
    # availability differs by trace; inventory-only names do not prove samples.
    $ValuesPattern = (Join-Path $OutputDirectory 'counter-{counter}.csv').Replace('\', '/')
    $ExportCommands.Add(('TimingInsights.ExportCounterValues "{0}" -counter="{1}"' -f $ValuesPattern, $CounterFilter))
}
[IO.File]::WriteAllLines($ResponsePath, $ExportCommands, [Text.UTF8Encoding]::new($false))

# The response-file syntax is exercised by the installed engine's
# Insights/Tests/FunctionalTests/ExportCommandsTests.cpp multiple-export test.
$Arguments = @(
    ('-OpenTraceFile="{0}"' -f $TracePath.Replace('\', '/')),
    '-NoUI',
    '-AutoQuit',
    '-Unattended',
    ('-ABSLOG="{0}"' -f $LogPath.Replace('\', '/')),
    ('-ExecOnAnalysisCompleteCmd="@={0}"' -f $ResponsePath.Replace('\', '/'))
)
$StartedUtc = [DateTime]::UtcNow.ToString('o')
$Manifest = [ordered]@{
    name = $Name
    trace_path = $TracePath
    trace_sha256 = (Get-FileHash -LiteralPath $TracePath -Algorithm SHA256).Hash
    executable = $Executable
    arguments = $Arguments
    response_commands = @($ExportCommands.ToArray())
    expected_files = @($ExpectedFiles.ToArray())
    expected_repeats = $ExpectedRepeats
    regions = $Regions
    region_bounds_source = $BoundsProvenance
    selected_region_bounds = @($Regions | ForEach-Object { if ($RegionBoundsPath) { $SelectedBounds[$_] } })
    include_timing_events = [bool]$IncludeTimingEvents
    include_counter_values = [bool]$IncludeCounterValues
    counter_filter = $CounterFilter
    started_utc = $StartedUtc
    notes = @(
        'Preblast region is the 2-second armed fuse; blast region is the 15-second post-field interval.',
        'Timer inclusive/exclusive costs overlap across nested scopes and threads; do not sum as frame time.',
        'ExportCounters is the counter inventory (Id/Type/Name), not counter sample values.',
        'UE 5.8 always includes GPU timelines in timer statistics. game-* filters CPU to GameThread but retains GPU rows.',
        'Do not attribute SceneRender, RenderGraphExecute, or other GPU scope rows to GameThread solely from the filename.',
        'Repeated region intervals use engine-generated suffixed filenames and remain in this directory.',
        'Timing-event exports retain original event bounds, including events crossing a region; clip to the exported region boundaries in insights.log.',
        'With RegionBoundsPath, explicit G17 start/end intervals come from the same-trace native provider export; region-bounds.json preserves those boundaries and the selected occurrence index.',
        'DP01 phase regions transition on observed game ticks; boundary overshoot is retained, not silently relabeled as an exact 0.5/3/10-second cut.',
        'Task dependency edges require DestructionTraceExport commandlet output; concurrent worker scopes alone do not establish a wait dependency.'
    )
}
$Manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'launch.json') -Encoding UTF8

$Process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru
# Keep the native handle so Windows PowerShell can retain the exit status after exit.
$null = $Process.Handle
Write-Output "Started headless Insights for $Name; PID=$($Process.Id). Log: $LogPath"
$Timer = [Diagnostics.Stopwatch]::StartNew()
$TimedOut = $false
while (-not $Process.WaitForExit(1000)) {
    if ($Timer.Elapsed.TotalSeconds -ge $TimeoutSeconds) {
        $TimedOut = $true
        Stop-Process -InputObject $Process -Force
        $Process.WaitForExit()
        break
    }
}
$Timer.Stop()
$Process.Refresh()
$MissingFiles = @($ExpectedFiles | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
$TimerExports = @(Get-ChildItem -LiteralPath $OutputDirectory -File | Where-Object {
    $_.Name -match '^(all|game|events)-[A-Za-z0-9_]+\.csv$'
})
$FilesToValidate = @(@($ExpectedFiles.ToArray()) + @($TimerExports.FullName) | Sort-Object -Unique)
$HeaderOnlyFiles = @($FilesToValidate | Where-Object {
    # A missing named region must not silently pass as a successful export
    # merely because the process exited. GPU rows can still exist without CPU.
    (Test-Path -LiteralPath $_ -PathType Leaf) -and @(Get-Content -LiteralPath $_ -TotalCount 2).Count -lt 2
})
$CounterValueFiles = @(Get-ChildItem -LiteralPath $OutputDirectory -Filter 'counter-*.csv' -File)
$CounterSamplesMissing = $IncludeCounterValues -and @($CounterValueFiles | Where-Object {
    @(Get-Content -LiteralPath $_.FullName -TotalCount 2).Count -gt 1
}).Count -eq 0
$RegionBounds = if ($RegionBoundsPath) {
    @($Regions | ForEach-Object { if ($IncludeTimingEvents) { $SelectedBounds[$_] } })
} else { @(Get-Content -LiteralPath $LogPath | ForEach-Object {
    # The UE 5.8 event exporter also says "timing statistics" in this log line.
    if ($_ -match "Exporting timing (?:events|statistics) for region '([^']+)' \[([0-9.eE+-]+) \.\. ([0-9.eE+-]+)\] to '([^']*events-[^']+)'") {
        [ordered]@{ region = $Matches[1]; start_seconds = [double]::Parse($Matches[2], [Globalization.CultureInfo]::InvariantCulture); end_seconds = [double]::Parse($Matches[3], [Globalization.CultureInfo]::InvariantCulture); path = $Matches[4] }
    }
}) }
$RegionBounds | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'region-bounds.json') -Encoding UTF8
$Result = [ordered]@{
    name = $Name
    pid = $Process.Id
    completed_utc = [DateTime]::UtcNow.ToString('o')
    elapsed_seconds = $Timer.Elapsed.TotalSeconds
    timed_out = $TimedOut
    exit_code = $Process.ExitCode
    expected_repeats = $ExpectedRepeats
    timer_export_files = @($TimerExports.Name)
    missing_exports = $MissingFiles
    header_only_exports = $HeaderOnlyFiles
    counter_value_files = @($CounterValueFiles.Name)
    counter_samples_missing = [bool]$CounterSamplesMissing
    region_bounds = $RegionBounds
    files = @(Get-ChildItem -LiteralPath $OutputDirectory -File | Select-Object Name, Length)
}
$Result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'completion.json') -Encoding UTF8
if ($TimedOut -or $Process.ExitCode -ne 0 -or $MissingFiles.Count -gt 0 -or $HeaderOnlyFiles.Count -gt 0 -or $CounterSamplesMissing) {
    throw "Insights export failed or incomplete. Preserve and inspect $OutputDirectory"
}
Write-Output "Exported $($Regions.Count) regions, counter inventory$(if ($IncludeTimingEvents) { ', thread-resolved timing events' })$(if ($IncludeCounterValues) { ', counter samples' }): $OutputDirectory"
