<#
.SYNOPSIS
Exports completed DestructionPerf01 traces with headless Unreal Insights.
.EXAMPLE
./Scripts/DestructionPerf01/export_trace.ps1 -Name trace03 -OutputDirectory Saved/DestructionPerf01/trace03-insights -ExpectedRepeats 2 -IncludeThreads
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
    [switch]$IncludeThreads,
    [ValidateRange(1, 100)]
    [int]$ExpectedRepeats = 1,
    [ValidateRange(10, 3600)]
    [int]$TimeoutSeconds = 300
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$SavedRoot = [IO.Path]::GetFullPath((Join-Path $ProjectRoot 'Saved')).TrimEnd('\', '/')
$TracePath = Join-Path $SavedRoot "DestructionPerf01/$Name.utrace"
$Executable = Join-Path $Engine 'Engine/Binaries/Win64/UnrealInsights.exe'
if (-not (Test-Path -LiteralPath $TracePath -PathType Leaf)) { throw "Trace does not exist: $TracePath" }
if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) { throw "Unreal Insights does not exist: $Executable" }
if ((Get-Item -LiteralPath $TracePath).Length -eq 0) { throw "Trace is empty: $TracePath" }
if (Get-Process -Name UnrealEditor, UnrealInsights -ErrorAction SilentlyContinue) {
    throw 'Finish the measured game/editor run and any existing Insights analysis before exporting.'
}

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
$Regions = @('DestructionPerfPreBlast', 'DestructionPerfBlast')
foreach ($Region in $Regions) {
    foreach ($ThreadScope in @('all', 'game')) {
        # A region placeholder also preserves separate exports if the native
        # trace happens to contain repeated intervals of the same region.
        $Pattern = (Join-Path $OutputDirectory "$ThreadScope-{region}.csv").Replace('\', '/')
        $ThreadFilter = if ($ThreadScope -eq 'game') { 'GameThread' } else { '*' }
        $ExportCommands.Add(('TimingInsights.ExportTimerStatistics "{0}" -region={1} -threads={2} -sortBy=TotalInclusiveTime -sortOrder=Descending' -f $Pattern, $Region, $ThreadFilter))
        for ($RepeatIndex = 0; $RepeatIndex -lt $ExpectedRepeats; $RepeatIndex++) {
            $RegionSuffix = if ($RepeatIndex -eq 0) { '' } else { "_$RepeatIndex" }
            $ExpectedFiles.Add((Join-Path $OutputDirectory "$ThreadScope-$Region$RegionSuffix.csv"))
        }
    }
}
$CountersPath = (Join-Path $OutputDirectory 'counters.csv').Replace('\', '/')
# UE 5.8 passes the complete remaining command to ExportCountersAsText as its
# filename, without tokenization or quote removal. Keep this path unquoted.
$ExportCommands.Add("TimingInsights.ExportCounters $CountersPath")
$ExpectedFiles.Add($CountersPath)
if ($IncludeThreads) {
    $ThreadsPath = (Join-Path $OutputDirectory 'threads.csv').Replace('\', '/')
    $ExportCommands.Add(('TimingInsights.ExportThreads "{0}"' -f $ThreadsPath))
    $ExpectedFiles.Add($ThreadsPath)
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
    started_utc = $StartedUtc
    notes = @(
        'Preblast region is the 2-second armed fuse; blast region is the 15-second post-field interval.',
        'Timer inclusive/exclusive costs overlap across nested scopes and threads; do not sum as frame time.',
        'ExportCounters is the counter inventory (Id/Type/Name), not counter sample values.',
        'UE 5.8 always includes GPU timelines in timer statistics. game-* filters CPU to GameThread but retains GPU rows.',
        'Do not attribute SceneRender, RenderGraphExecute, or other GPU scope rows to GameThread solely from the filename.',
        'Repeated region intervals use engine-generated suffixed filenames and remain in this directory.'
    )
}
$Manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'launch.json') -Encoding UTF8

$Process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru
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
    $_.Name -match '^(all|game)-DestructionPerf(PreBlast|Blast)(_[0-9]+)?\.csv$'
})
$FilesToValidate = @(@($ExpectedFiles.ToArray()) + @($TimerExports.FullName) | Sort-Object -Unique)
$HeaderOnlyFiles = @($FilesToValidate | Where-Object {
    # A missing named region must not silently pass as a successful export
    # merely because the process exited. GPU rows can still exist without CPU.
    (Test-Path -LiteralPath $_ -PathType Leaf) -and @(Get-Content -LiteralPath $_ -TotalCount 2).Count -lt 2
})
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
    files = @(Get-ChildItem -LiteralPath $OutputDirectory -File | Select-Object Name, Length)
}
$Result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'completion.json') -Encoding UTF8
if ($TimedOut -or $Process.ExitCode -ne 0 -or $MissingFiles.Count -gt 0 -or $HeaderOnlyFiles.Count -gt 0) {
    throw "Insights export failed or incomplete. Preserve and inspect $OutputDirectory"
}
Write-Output "Exported both regions (all timelines and GameThread CPU plus GPU), counter inventory$(if ($IncludeThreads) { ', and thread inventory' }): $OutputDirectory"
