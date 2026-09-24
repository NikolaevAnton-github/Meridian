# MSQ-138: build a staged runner only. Deployment belongs to the controller.
[CmdletBinding()]
param([switch]$SkipTests)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$contextRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$contextToolRoot = Join-Path $contextRoot '.tools/multica'
$contextEvidence = Join-Path $contextRoot 'Saved/ContextBudget02/Worker'
$contextStage = Join-Path $contextEvidence 'staged-bin'
$null = New-Item -ItemType Directory -Path $contextStage -Force
$contextGo = Join-Path $contextToolRoot 'go/bin/go.exe'
$contextServer = Join-Path $contextToolRoot 'source/server'
. (Join-Path $PSScriptRoot 'python.ps1')
$contextPython = Get-ContextPython
$contextPrevious = @{}
try {
    foreach ($key in @('GOCACHE','GOMODCACHE','GOMEMLIMIT','GOMAXPROCS')) {
        $contextPrevious[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
    }
    $env:GOCACHE = Join-Path $contextToolRoot 'go-cache'
    $env:GOMODCACHE = Join-Path $contextToolRoot 'go-modules'
    $env:GOMEMLIMIT = '768MiB'
    $env:GOMAXPROCS = '2'
    & $contextPython (Join-Path $PSScriptRoot 'export_patch.py')
    if ($LASTEXITCODE -ne 0) { throw 'Additive patch export failed.' }
    if (-not $SkipTests) {
        $testLog = Join-Path $contextEvidence 'build-tests.log'
        & $contextPython (Join-Path $PSScriptRoot 'context_budget.py') --root $contextRoot run --label go-tests --timeout 600 -- $contextGo test -C $contextServer ./internal/daemon ./pkg/agent -run '^TestContextBudget' -count=1 -p 1 | Set-Content -LiteralPath $testLog -Encoding UTF8
        if ($LASTEXITCODE -ne 0) { throw "Focused tests failed; inspect $testLog" }
    }
    $buildLog = Join-Path $contextEvidence 'build.log'
    $contextBuildDate = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $contextLdFlags = "-X main.version=0.4.43 -X main.commit=2ae2dbbb8-ContextBudget02 -X main.date=$contextBuildDate"
    & $contextPython (Join-Path $PSScriptRoot 'context_budget.py') --root $contextRoot run --label multica-build --timeout 900 -- $contextGo build -C $contextServer -p 1 -trimpath -ldflags $contextLdFlags -o (Join-Path $contextStage 'multica.exe') ./cmd/multica | Set-Content -LiteralPath $buildLog -Encoding UTF8
    if ($LASTEXITCODE -ne 0) { throw "Runner build failed; inspect $buildLog" }
    $contextCandidate = [ordered]@{
        task = 'MSQ-138'; built_at = [DateTime]::UtcNow.ToString('o')
        source_commit = (& git -C (Join-Path $contextToolRoot 'source') rev-parse HEAD).Trim()
        binary = 'Saved/ContextBudget02/Worker/staged-bin/multica.exe'
        binary_sha256 = (Get-FileHash -LiteralPath (Join-Path $contextStage 'multica.exe') -Algorithm SHA256).Hash.ToLowerInvariant()
        patch_sha256 = (Get-FileHash -LiteralPath (Join-Path $contextRoot 'Tools/ContextBudget02-Multica.patch') -Algorithm SHA256).Hash.ToLowerInvariant()
        live_binary_sha256 = (Get-FileHash -LiteralPath (Join-Path $contextToolRoot 'bin/multica.exe') -Algorithm SHA256).Hash.ToLowerInvariant()
        deployed = $false
    }
    $contextCandidate | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $contextEvidence 'candidate.json') -Encoding UTF8
    [pscustomobject]@{ passed = $true; staged_binary = $contextCandidate.binary; sha256 = $contextCandidate.binary_sha256; deployed = $false } | ConvertTo-Json -Compress
} finally {
    foreach ($key in $contextPrevious.Keys) { [Environment]::SetEnvironmentVariable($key, $contextPrevious[$key], 'Process') }
}
