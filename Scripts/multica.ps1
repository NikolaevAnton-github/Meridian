# Optional Multica board only. DirectWorkflow01 retires all worker execution.
[CmdletBinding()]
param(
    [ValidateSet('Start', 'StartServices', 'Stop', 'Status', 'StartApi', 'StartWeb')]
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

function Start-SharedDatabase {
    $arguments = @('-D', ('"' + (Join-Path $stateRoot 'postgres-data') + '"'), '-w')
    $arguments += @('-l', ('"' + (Join-Path $stateRoot 'postgres.log') + '"'),
        '-o', '"-h 127.0.0.1 -p 15432 -c max_connections=20 -c shared_buffers=64MB"', 'start')
    $process = Start-Process -FilePath (Join-Path $toolRoot 'pgsql\bin\pg_ctl.exe') `
        -ArgumentList $arguments -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $stateRoot 'pg-control.log') `
        -RedirectStandardError (Join-Path $stateRoot 'pg-control.error.log')
    # -Wait also waits for PostgreSQL descendants on Windows; wait for pg_ctl only.
    # Retain the native handle so Windows PowerShell can read ExitCode after exit.
    $null = $process.Handle
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { throw 'PostgreSQL start failed; inspect Saved/Multica/pg-control logs.' }
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
    if (-not $pg) { Start-SharedDatabase }
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

if ($Action -eq 'Stop') {
    foreach ($name in @('web', 'api')) {
        $process = Get-OwnedProcess $name
        if ($process) { Stop-Process -Id $process.Id; Write-Output "$name stopped." }
    }
    Write-Output 'Board stopped; shared PostgreSQL retained for the asset registry.'
}

if ($Action -eq 'Status') {
    $componentStatus = foreach ($name in @('api', 'web')) {
        $process = Get-OwnedProcess $name
        [PSCustomObject]@{ Component = $name; Running = [bool]$process; PID = $process.Id
            WorkingSetMiB = [math]::Round($process.WorkingSet64 / 1MB, 1) }
    }
    $componentStatus | Format-Table -AutoSize
    Write-Output 'Worker execution is retired; this launcher is board-only.'
    Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -in @(3000, 8080, 15432) } |
        Format-Table LocalAddress, LocalPort, OwningProcess -AutoSize
}
