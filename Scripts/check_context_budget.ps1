# Check repository context size and navigation without loading historical content.
[CmdletBinding()]
param(
    [string]$RepositoryRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $RepositoryRoot) { $RepositoryRoot = Split-Path -Parent $PSScriptRoot }
$contextRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$spec = Get-Content -LiteralPath (Join-Path $contextRoot 'Tools/ContextBudget.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$failures = [System.Collections.Generic.List[string]]::new()
$files = [System.Collections.Generic.List[object]]::new()
$navigation = [System.Collections.Generic.List[string]]::new()
$startupBytes = 0

function Measure-ContextFile([string]$RelativePath, [long]$MaximumBytes, [string]$Layer) {
    $path = Join-Path $contextRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $failures.Add("Missing ${Layer}: $RelativePath")
        return 0
    }
    $bytes = (Get-Item -LiteralPath $path).Length
    $files.Add([pscustomobject]@{ path = $RelativePath; layer = $Layer; bytes = $bytes; max_bytes = $MaximumBytes })
    if ($bytes -gt $MaximumBytes) { $failures.Add("Budget exceeded: $RelativePath ($bytes > $MaximumBytes bytes)") }
    $navigation.Add($RelativePath)
    return $bytes
}

foreach ($entry in $spec.startup) {
    $startupBytes += Measure-ContextFile $entry.path $entry.max_bytes 'startup'
}
if ($startupBytes -gt $spec.startup_max_bytes) { $failures.Add('Combined startup budget exceeded') }
foreach ($policy in Get-ChildItem -LiteralPath (Join-Path $contextRoot $spec.policy_directory) -Filter '*.md' -File) {
    $null = Measure-ContextFile ($spec.policy_directory + '/' + $policy.Name) $spec.policy_max_bytes 'on-demand'
}
foreach ($path in $spec.navigation) { $navigation.Add($path) }

# Check direct local link targets only. Never recursively read linked documents.
$linkCount = 0
foreach ($relative in $navigation) {
    $path = Join-Path $contextRoot $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $failures.Add("Missing navigation document: $relative")
        continue
    }
    $body = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    foreach ($link in [regex]::Matches($body, '\[[^\]]+\]\(([^)]+)\)')) {
        $target = $link.Groups[1].Value
        if ($target -match '^[a-zA-Z][a-zA-Z0-9+.-]*:' -or $target.StartsWith('#')) { continue }
        $local = [Uri]::UnescapeDataString(($target -split '#', 2)[0])
        $destination = Join-Path (Split-Path -Parent $path) $local
        $linkCount++
        if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) { $failures.Add("Broken link in ${relative}: $target") }
    }
}

$baselineBytes = 0
foreach ($snapshot in $spec.snapshots) {
    $baselineBytes += $snapshot.bytes
    $path = Join-Path $contextRoot $snapshot.path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $failures.Add("Missing snapshot: $($snapshot.path)")
        continue
    }
    if ((Get-Item -LiteralPath $path).Length -ne $snapshot.bytes -or
        (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $snapshot.sha256) {
        $failures.Add("Changed immutable snapshot: $($snapshot.path)")
    }
}

[pscustomobject]@{
    passed = ($failures.Count -eq 0)
    measurement = 'File bytes; not native model tokens or total host input'
    baseline_startup_bytes = $baselineBytes
    startup_bytes = $startupBytes
    startup_max_bytes = $spec.startup_max_bytes
    reduction_percent = [Math]::Round(100 * (1 - $startupBytes / [double]$baselineBytes), 2)
    files = @($files.ToArray())
    direct_local_link_targets_checked = $linkCount
    immutable_snapshots_checked = @($spec.snapshots).Count
    failures = @($failures.ToArray())
} | ConvertTo-Json -Depth 5
if ($failures.Count -gt 0) { exit 1 }
