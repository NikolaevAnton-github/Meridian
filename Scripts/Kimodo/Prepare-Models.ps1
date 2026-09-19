$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Environment.ps1"
Remove-Item Env:HF_HUB_OFFLINE -ErrorAction SilentlyContinue
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$out = "$KimodoRoot\logs\models-$stamp.stdout.log"
$err = "$KimodoRoot\logs\models-$stamp.stderr.log"
Write-Host "Preparing pinned models. Progress: $out and $err"
$p = Start-Process -FilePath $KimodoPython -ArgumentList "$PSScriptRoot\prepare_models.py" -WorkingDirectory $KimodoRoot -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
Get-Content -LiteralPath $out
if ($p.ExitCode -ne 0) { Write-Host "Download failed. See $err" }
exit $p.ExitCode
