param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Name,
    [string]$Engine = 'D:/UE_5.8',
    [switch]$Trace,
    [switch]$NoNiagara,
    [switch]$NoSound,
    [ValidateRange(1,5)][int]$Repeats = 1
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path "$PSScriptRoot/../..").Path
$OutputRoot = Join-Path $ProjectRoot 'Saved/DestructionPerf01'
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$LogPath = Join-Path $OutputRoot ($Name + '.log')
$ManifestPath = Join-Path $OutputRoot ($Name + '-launch.json')
if ((Test-Path -LiteralPath $LogPath) -or (Test-Path -LiteralPath $ManifestPath)) { throw 'Use a fresh run name; evidence is immutable.' }
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) { throw 'Close the editor/game before the isolated run.' }
$Executable = Join-Path $Engine 'Engine/Binaries/Win64/UnrealEditor.exe'
$Arguments = @(
    (Join-Path $ProjectRoot 'MeridianSquad.uproject'),
    '/Game/Maps/L_OpeningLobby_PainterStone01', '-game', '-windowed', '-ResX=1920', '-ResY=1080',
    '-NoVSync', '-NoSplash', '-Unattended', '-DestructionPerfScreenshot', "-DestructionPerfAuto=$Name", "-DestructionPerfRepeats=$Repeats", "-abslog=$LogPath"
)
$Commands = 't.MaxFPS 0,r.VSync 0,r.ScreenPercentage 100'
if ($NoNiagara) { $Commands += ',fx.NiagaraComponentsEnabled 0' }
$Arguments += '-ExecCmds="' + $Commands + '"'
if ($NoSound) { $Arguments += '-nosound' }
if ($Trace) {
    $Arguments += '-trace=cpu,frame,gpu,bookmark,counters,region'
    $Arguments += "-tracefile=$OutputRoot/$Name.utrace"
}
$Record = [ordered]@{ name=$Name; executable=$Executable; arguments=$Arguments;
    dll_sha256=(Get-FileHash (Join-Path $ProjectRoot 'Binaries/Win64/UnrealEditor-MeridianSquad.dll')).Hash;
    map_sha256=(Get-FileHash (Join-Path $ProjectRoot 'Content/Maps/L_OpeningLobby_PainterStone01.umap')).Hash;
    started_utc=[DateTime]::UtcNow.ToString('o') }
$Record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
# This game window is the actual interactive performance target.
$Process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -PassThru
Write-Output "Started $Name PID=$($Process.Id); native fixture warms 12s, detonates after 2s and records 15s."
Write-Output "Log: $LogPath"
