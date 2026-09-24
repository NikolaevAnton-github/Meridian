# Start and stop the pinned local Multica components; task scheduling stays in Multica.
[CmdletBinding()]
param(
    [ValidateSet('Start', 'StartServices', 'Stop', 'Status', 'StartApi', 'StartWeb', 'StartRuntime')]
    [string]$Action = 'Status'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$toolRoot = Join-Path $projectRoot '.tools\multica'
$stateRoot = Join-Path $projectRoot 'Saved\Multica'
$recordPath = Join-Path $stateRoot 'processes.json'
$nodePath = 'C:\Users\Origa\AppData\Local\JetBrains\Rider2026.2\acp-agents\.runtimes\node\24.13.0\node.exe'
$settings = Get-Content -LiteralPath (Join-Path $toolRoot 'local-config.json') -Raw | ConvertFrom-Json
$records = @{}
if (Test-Path -LiteralPath $recordPath) {
    $saved = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    foreach ($property in $saved.PSObject.Properties) { $records[$property.Name] = $property.Value }
}

function Save-Records {
    $records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $recordPath -Encoding UTF8
}

function Get-OwnedProcess([string]$Name) {
    if (-not $records.ContainsKey($Name)) { return $null }
    $record = $records[$Name]
    $process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if ($process -and $process.Path -eq $record.path -and
        $process.StartTime.ToUniversalTime().ToString('o') -eq $record.started_at) {
        return $process
    }
    return $null
}

function Start-Component([string]$Name, [string]$Executable, [string[]]$Arguments,
    [string]$Directory, [hashtable]$Environment) {
    if (Get-OwnedProcess $Name) { Write-Output "$Name is already running."; return }
    $port = @{ api = 8080; web = 3000 }[$Name]
    if ($port -and (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue)) {
        throw "Port $port is already occupied by a process not owned by this launcher."
    }
    $previous = @{}
    try {
        foreach ($key in $Environment.Keys) {
            $previous[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
            [Environment]::SetEnvironmentVariable($key, [string]$Environment[$key], 'Process')
        }
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments `
            -WorkingDirectory $Directory -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $stateRoot "$Name.log") `
            -RedirectStandardError (Join-Path $stateRoot "$Name.error.log")
        $records[$Name] = @{
            pid = $process.Id; path = $Executable
            started_at = $process.StartTime.ToUniversalTime().ToString('o')
        }
        Save-Records
        Write-Output "$Name started (PID $($process.Id))."
    } finally {
        foreach ($key in $previous.Keys) {
            [Environment]::SetEnvironmentVariable($key, $previous[$key], 'Process')
        }
    }
}

function Invoke-PgControl([string]$Operation) {
    $arguments = @('-D', ('"' + (Join-Path $stateRoot 'postgres-data') + '"'), '-w')
    if ($Operation -eq 'start') {
        $arguments += @('-l', ('"' + (Join-Path $stateRoot 'postgres.log') + '"'),
            '-o', '"-h 127.0.0.1 -p 15432 -c max_connections=20 -c shared_buffers=64MB"')
    } else { $arguments += @('-m', 'fast') }
    $arguments += $Operation
    $process = Start-Process -FilePath (Join-Path $toolRoot 'pgsql\bin\pg_ctl.exe') `
        -ArgumentList $arguments -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $stateRoot 'pg-control.log') `
        -RedirectStandardError (Join-Path $stateRoot 'pg-control.error.log')
    # -Wait also waits for PostgreSQL descendants on Windows; wait for pg_ctl only.
    # Retain the native handle so Windows PowerShell can read ExitCode after exit.
    $null = $process.Handle
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { throw "PostgreSQL $Operation failed; inspect Saved/Multica/pg-control logs." }
}

function Wait-Http([string]$Url, [string]$Name, [int]$Port) {
    $deadline = [DateTime]::UtcNow.AddSeconds(30)
    do {
        $process = Get-OwnedProcess $Name
        if (-not $process) { throw "$Name exited before becoming ready; inspect Saved/Multica logs." }
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            $listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
            if ($response.StatusCode -eq 200 -and $listeners.Count -eq 1 -and
                $listeners[0].LocalAddress -eq '127.0.0.1' -and
                $listeners[0].OwningProcess -eq $process.Id) { return }
        } catch { }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Health check timed out: $Url. Inspect Saved/Multica logs."
}

# Administrative access needs the services but does not need a task worker.
if ($Action -in @('Start', 'StartServices')) {
    $pg = Get-NetTCPConnection -State Listen -LocalPort 15432 -ErrorAction SilentlyContinue
    if (-not $pg) { Invoke-PgControl 'start' }
    elseif ($pg.LocalAddress -ne '127.0.0.1' -or
        (Get-Process -Id $pg.OwningProcess).Path -ne (Join-Path $toolRoot 'pgsql\bin\postgres.exe') -or
        $pg.OwningProcess -ne [int](Get-Content -LiteralPath (Join-Path $stateRoot 'postgres-data\postmaster.pid') -TotalCount 1)) {
        throw 'Port 15432 belongs to a different PostgreSQL instance or bind address.'
    }
}

if ($Action -in @('Start', 'StartServices', 'StartApi')) {
    $apiEnvironment = @{}
    foreach ($property in $settings.environment.PSObject.Properties) {
        $apiEnvironment[$property.Name] = [string]$property.Value
    }
    $apiEnvironment['GOMEMLIMIT'] = '512MiB'
    Start-Component 'api' (Join-Path $toolRoot 'bin\server.exe') @('--') `
        (Join-Path $toolRoot 'source\server') $apiEnvironment
    Wait-Http 'http://127.0.0.1:8080/health' 'api' 8080
}

if ($Action -in @('Start', 'StartServices', 'StartWeb')) {
    $webEnvironment = @{
        REMOTE_API_URL = 'http://127.0.0.1:8080'; NEXT_TELEMETRY_DISABLED = '1'
        NODE_OPTIONS = '--max-old-space-size=1024'; NODE_ENV = 'production'
    }
    Start-Component 'web' $nodePath @('node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', '3000') `
        (Join-Path $toolRoot 'source\apps\web') $webEnvironment
    Wait-Http 'http://127.0.0.1:3000/health' 'web' 3000
}

if ($Action -in @('Start', 'StartRuntime')) {
    # This project-scoped daemon policy runs for every task before injection.
    . (Join-Path $PSScriptRoot 'ContextBudget/python.ps1')
    $contextPython = Get-ContextPython
    if (-not (Test-Path -LiteralPath $settings.environment.MULTICA_CODEX_PATH -PathType Leaf)) {
        throw 'The configured native Codex executable is missing; update the local path after a Rider upgrade.'
    }
    $runtimeEnvironment = @{
        PATH = (Split-Path $nodePath -Parent) + ';' + (Join-Path $toolRoot 'bin') + ';' + $env:PATH
        OPENAI_API_KEY = ''; ANTHROPIC_API_KEY = ''; GEMINI_API_KEY = ''; GOOGLE_API_KEY = ''
        AZURE_OPENAI_API_KEY = ''; MULTICA_LLM_API_KEY = ''; MULTICA_LLM_BASE_URL = ''
        MULTICA_CLOUD_URL = ''; MULTICA_DAEMON_AUTO_RELOAD = 'false'
        MULTICA_CONTEXT_PROJECT_ROOT = $projectRoot
        CONTEXT_BUDGET_PYTHON = $contextPython
    }
    foreach ($key in @('MULTICA_SERVER_URL', 'MULTICA_CODEX_PATH', 'MULTICA_DAEMON_MAX_CONCURRENT_TASKS',
        'MULTICA_DAEMON_AUTO_UPDATE', 'MULTICA_CODEX_MULTI_AGENT', 'MULTICA_WORKSPACES_ROOT')) {
        $runtimeEnvironment[$key] = [string]$settings.environment.$key
    }
    $profilePath = Join-Path $env:USERPROFILE '.multica\profiles\meridiansquad\config.json'
    if (-not (Test-Path -LiteralPath $profilePath)) { throw 'Authenticate the meridiansquad CLI profile first.' }
    Start-Component 'runtime' (Join-Path $toolRoot 'bin\multica.exe') `
        @('--profile', 'meridiansquad', 'daemon', 'start', '--foreground', '--no-auto-update', '--no-auto-reload', '--max-concurrent-tasks', '1') `
        $projectRoot $runtimeEnvironment
    $deadline = [DateTime]::UtcNow.AddSeconds(30)
    $runtimeReady = $false
    do {
        $process = Get-OwnedProcess 'runtime'
        if (-not $process) { throw 'Runtime exited before becoming ready; inspect Saved/Multica logs.' }
        $statusText = & (Join-Path $toolRoot 'bin\multica.exe') --profile meridiansquad daemon status --output json 2>$null
        if ($LASTEXITCODE -eq 0) {
            $runtimeStatus = $statusText | ConvertFrom-Json
            if ($runtimeStatus.pid -eq $process.Id -and $runtimeStatus.status -eq 'running' -and
                $runtimeStatus.agents -contains 'codex') { $runtimeReady = $true; break }
        }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    if (-not $runtimeReady) { throw 'Runtime health check timed out; inspect Saved/Multica logs.' }
}

if ($Action -eq 'Stop') {
    if (Get-OwnedProcess 'runtime') {
        & (Join-Path $toolRoot 'bin\multica.exe') --profile meridiansquad daemon stop
        if ($LASTEXITCODE -ne 0) { throw 'Runtime stop failed; leaving API and database available.' }
        $deadline = [DateTime]::UtcNow.AddSeconds(30)
        while ((Get-OwnedProcess 'runtime') -and [DateTime]::UtcNow -lt $deadline) {
            Start-Sleep -Milliseconds 500
        }
        if (Get-OwnedProcess 'runtime') { throw 'Runtime is still stopping; API and database remain available.' }
    }
    foreach ($name in @('web', 'api')) {
        $process = Get-OwnedProcess $name
        if ($process) { Stop-Process -Id $process.Id; Write-Output "$name stopped." }
    }
    & (Join-Path $toolRoot 'pgsql\bin\pg_ctl.exe') -D (Join-Path $stateRoot 'postgres-data') status *> $null
    if ($LASTEXITCODE -eq 0) { Invoke-PgControl 'stop' }
}

if ($Action -eq 'Status') {
    $componentStatus = foreach ($name in @('api', 'web', 'runtime')) {
        $process = Get-OwnedProcess $name
        [PSCustomObject]@{ Component = $name; Running = [bool]$process; PID = $process.Id
            WorkingSetMiB = [math]::Round($process.WorkingSet64 / 1MB, 1) }
    }
    $componentStatus | Format-Table -AutoSize
    Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -in @(3000, 8080, 15432) } |
        Format-Table LocalAddress, LocalPort, OwningProcess -AutoSize
}
