param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Name,
    [string]$Engine = 'D:/UE_5.8',
    [switch]$Trace,
    [switch]$NamedEvents,
    [switch]$Diagnostics,
    [ValidateSet('reference','profile_observe','profile_batch','collision_off')][string]$IsolationMode = 'reference',
    [ValidateSet('vendor','observe','native')][string]$CollisionMode = 'vendor',
    [ValidateSet('immediate','batch')][string]$NotificationMode = 'immediate',
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$EvidenceSubdirectory = 'DP-01',
    [switch]$NoNiagara,
    [switch]$NoSound,
    [switch]$SlowdownAfterBlast,
    [ValidateRange(1,5)][int]$Repeats = 1
)
$ErrorActionPreference = 'Stop'
if ($IsolationMode -ne 'reference' -and $CollisionMode -ne 'vendor') {
    throw 'DP-02 delegate isolation must use the original vendor collision mode.'
}
$ProjectRoot = (Resolve-Path "$PSScriptRoot/../..").Path
$OutputRoot = Join-Path $ProjectRoot "Saved/DestructionPerf01/$EvidenceSubdirectory"
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$LogPath = Join-Path $OutputRoot ($Name + '.log')
$ManifestPath = Join-Path $OutputRoot ($Name + '-launch.json')
if ((Test-Path -LiteralPath $LogPath) -or (Test-Path -LiteralPath $ManifestPath)) { throw 'Use a fresh run name; evidence is immutable.' }
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) { throw 'Close the editor/game before the isolated run.' }
$CandidateCommit = (git -C $ProjectRoot rev-parse HEAD).Trim()
$IdentityFiles = @(
    Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'Content/NextGenDestruction') -Recurse -File
    Get-Item -LiteralPath (Join-Path $ProjectRoot 'Content/Maps/L_OpeningLobby_PainterStone01.umap')
    Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'Config') -File
)
$AssetHashes = [ordered]@{}
foreach ($File in ($IdentityFiles | Sort-Object FullName)) {
    $Relative = $File.FullName.Substring($ProjectRoot.Length + 1).Replace('\', '/')
    $AssetHashes[$Relative] = (Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256).Hash
}
$HashText = ($AssetHashes | ConvertTo-Json -Compress)
$Hasher = [Security.Cryptography.SHA256]::Create()
try { $Identity = [BitConverter]::ToString($Hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($HashText))).Replace('-', '').ToLowerInvariant() }
finally { $Hasher.Dispose() }
$SourceHashes = [ordered]@{}
foreach ($File in (Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'Source/MeridianSquad') -File | Sort-Object Name)) {
    $SourceHashes[$File.Name] = (Get-FileHash -LiteralPath $File.FullName).Hash
}
$Executable = Join-Path $Engine 'Engine/Binaries/Win64/UnrealEditor.exe'
$Arguments = @(
    (Join-Path $ProjectRoot 'MeridianSquad.uproject'),
    '/Game/Maps/L_OpeningLobby_PainterStone01', '-game', '-windowed', '-ResX=1920', '-ResY=1080',
    '-NoVSync', '-NoSplash', '-Unattended', '-DestructionPerfScreenshot', "-DestructionPerfAuto=$Name", "-DestructionPerfRepeats=$Repeats", "-abslog=$LogPath"
)
$Arguments += "-DestructionPerfCommit=$CandidateCommit"
$Arguments += "-DestructionPerfIdentity=$Identity"
$Arguments += "-DestructionPerfEvidence=$EvidenceSubdirectory"
$Arguments += "-DestructionPerfIsolation=$IsolationMode"
$Arguments += "-DestructionCollisionMode=$CollisionMode"
$Arguments += "-DestructionNotificationMode=$NotificationMode"
if ($Diagnostics) { $Arguments += '-DestructionPerfDiagnostics' }
if ($NamedEvents) { $Arguments += '-statnamedevents' }
$Commands = 't.MaxFPS 0,r.VSync 0,r.ScreenPercentage 100'
if ($NoNiagara) { $Commands += ',fx.NiagaraComponentsEnabled 0' }
$Arguments += '-ExecCmds="' + $Commands + '"'
if ($NoSound) { $Arguments += '-nosound' }
if ($SlowdownAfterBlast) { $Arguments += '-DP03SlowdownAfterBlast' }
if ($Trace) {
    $Arguments += '-trace=cpu,frame,task,gpu,bookmark,counters,region'
    $Arguments += "-tracefile=$OutputRoot/$Name.utrace"
}
else {
    # Explicitly disable default/auto-connect trace channels in the control.
    $Arguments += '-trace=none'
    $Arguments += '-traceautostart=0'
}
$Record = [ordered]@{ name=$Name; executable=$Executable; arguments=$Arguments;
    candidate_commit=$CandidateCommit; workload_identity=$Identity; asset_config_hashes=$AssetHashes; source_hashes=$SourceHashes;
    engine_build=(Get-Content -LiteralPath (Join-Path $Engine 'Engine/Build/Build.version') -Raw | ConvertFrom-Json);
    diagnostics=[bool]$Diagnostics; named_events=[bool]$NamedEvents; trace=[bool]$Trace; isolation_mode=$IsolationMode;
    collision_mode=$CollisionMode; notification_mode=$NotificationMode;
    dll_sha256=(Get-FileHash (Join-Path $ProjectRoot 'Binaries/Win64/UnrealEditor-MeridianSquad.dll')).Hash;
    map_sha256=(Get-FileHash (Join-Path $ProjectRoot 'Content/Maps/L_OpeningLobby_PainterStone01.umap')).Hash;
    started_utc=[DateTime]::UtcNow.ToString('o') }
$Record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
# Render a real game viewport while keeping the unattended helper launch hidden.
$Process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru
Write-Output "Started $Name PID=$($Process.Id); native fixture warms 12s, detonates after 2s and records 15s."
Write-Output "Log: $LogPath"
