param([ValidateSet('start','stop','check','smoke')][string]$Action = 'start')
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Environment.ps1"
& $KimodoPython "$PSScriptRoot\manage.py" $Action
exit $LASTEXITCODE
