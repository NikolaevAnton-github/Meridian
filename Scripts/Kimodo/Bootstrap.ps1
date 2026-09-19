# Run in Windows PowerShell. Requires the existing VS 2022 C++ toolchain and Git.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Environment.ps1"
$ProgressPreference = 'SilentlyContinue'
try {
    $installLease = [System.IO.File]::Open((Join-Path $KimodoRoot 'runtime\workload.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
} catch {
    throw 'Another Kimodo operation is active. Stop/wait for it before installing.'
}
try {
$installedBytes = (Get-ChildItem -LiteralPath $KimodoRoot -Recurse -File -Force | Measure-Object -Property Length -Sum).Sum
$reserve = 18000000000
if (Test-Path -LiteralPath $KimodoPython) { $reserve = 6000000000 }
if (($installedBytes + $reserve) -gt 45000000000 -or (Get-PSDrive -Name D).Free -lt $reserve) {
    throw 'Insufficient installation headroom within the 45 GB cap. Review local generated data; no files were removed.'
}

function Invoke-Logged([string]$Exe, [string[]]$Arguments, [string]$Name) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $stdout = Join-Path $KimodoRoot "logs\$Name-$stamp.stdout.log"
    $stderr = Join-Path $KimodoRoot "logs\$Name-$stamp.stderr.log"
    $p = Start-Process -FilePath $Exe -ArgumentList $Arguments -WorkingDirectory $KimodoRoot -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($p.ExitCode -ne 0) { throw "$Name failed ($($p.ExitCode)). See $stdout and $stderr" }
    Write-Host "$Name completed."
}

$uv = Join-Path $KimodoRoot 'tools\uv\uv.exe'
if (-not (Test-Path -LiteralPath $uv)) {
    $archive = Join-Path $KimodoRoot 'tools\uv.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://github.com/astral-sh/uv/releases/download/0.12.17/uv-x86_64-pc-windows-msvc.zip' -OutFile $archive
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne 'A252121D5B59398FCB137C6EA448176459A44010F33F67E0072305A637119CA7') { throw 'uv archive hash mismatch' }
    Expand-Archive -LiteralPath $archive -DestinationPath (Join-Path $KimodoRoot 'tools\uv')
}
Invoke-Logged $uv @('python','install','3.11.13','--no-bin') 'python'
if (-not (Test-Path -LiteralPath $KimodoPython)) {
    Invoke-Logged $uv @('venv','--python','3.11.13','--managed-python',"$KimodoRoot\.venv") 'venv'
}

$sources = @(
    @('https://github.com/nv-tlabs/kimodo.git', 'source', '1aece8c124d73d255ceff5086d983b844c9f4e94'),
    @('https://github.com/nv-tlabs/kimodo-viser.git', 'vendor\kimodo-viser', '7c82ad8f8640bad9dff8ded5c5eee908eeb08f11'),
    @('https://github.com/NVlabs/SOMA-X.git', 'vendor\SOMA-X', 'cc1f3967755f8e36d187d2e26114633dbd651cd5')
)
foreach ($source in $sources) {
    $dest = Join-Path $KimodoRoot $source[1]
    $label = $source[1].Replace('\','-')
    if (-not (Test-Path -LiteralPath $dest)) {
        Invoke-Logged 'git.exe' @('clone',$source[0],$dest) "clone-$label"
        Invoke-Logged 'git.exe' @('-C',$dest,'checkout','--detach',$source[2]) "pin-$label"
    }
    $actual = & git -C $dest rev-parse HEAD
    if ($actual -ne $source[2]) { throw "Source revision mismatch in $dest; preserve it and inspect manually." }
    $dirty = @(& git -C $dest status --porcelain --untracked-files=no)
    if ($dirty.Count -gt 0) { throw "Tracked upstream edits exist in $dest; preserve and inspect them before reinstalling." }
}

Invoke-Logged $uv @('pip','install','--python',$KimodoPython,'torch==2.10.0','--index-url','https://download.pytorch.org/whl/cu128') 'pytorch'
Invoke-Logged $uv @('pip','install','--python',$KimodoPython,'cmake==3.31.6','setuptools==80.9.0','wheel==0.45.1','psutil==7.2.2') 'build-tools'
$constraint = Join-Path $PSScriptRoot 'constraints.txt'
if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'requirements.lock')) {
    $constraint = Join-Path $PSScriptRoot 'requirements.lock'
}
Invoke-Logged $uv @('pip','install','--python',$KimodoPython,'--constraint',$constraint,'--editable',"$KimodoRoot\source",'--editable',"$KimodoRoot\vendor\kimodo-viser",'--editable',"$KimodoRoot\vendor\SOMA-X") 'kimodo'
& "$PSScriptRoot\Build-Frontend.ps1"
Write-Host 'Dependencies installed. Use Prepare-Models.cmd, then Start-Kimodo.cmd. See README.md.'
} finally {
    $installLease.Dispose()
}
