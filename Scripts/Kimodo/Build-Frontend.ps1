# Build the official Viser client without invoking its POSIX npm/npx wrappers.
# Uses the upstream lockfile and a portable Node distribution inside the install root.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Environment.ps1"
$ProgressPreference = 'SilentlyContinue'
$nodeDir = Join-Path $KimodoRoot 'tools\node-v20.19.0-win-x64'
$node = Join-Path $nodeDir 'node.exe'
if (-not (Test-Path -LiteralPath $node)) {
    $archive = Join-Path $KimodoRoot 'tools\node.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://nodejs.org/dist/v20.19.0/node-v20.19.0-win-x64.zip' -OutFile $archive
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne 'BE72284C7BC62DE07D5A9FD0AE196879842C085F11F7F2B60BF8864C0C9D6A4F') { throw 'Node archive hash mismatch' }
    Expand-Archive -LiteralPath $archive -DestinationPath (Join-Path $KimodoRoot 'tools')
}
$env:Path = "$nodeDir;$env:Path"
$env:NODE_OPTIONS = '--max-old-space-size=2048'
$client = Join-Path $KimodoRoot 'vendor\kimodo-viser\src\viser\client'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$args = @("$nodeDir\node_modules\npm\bin\npm-cli.js",'ci','--legacy-peer-deps','--no-audit','--no-fund')
$p = Start-Process -FilePath $node -ArgumentList $args -WorkingDirectory $client -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput "$KimodoRoot\logs\frontend-install-$stamp.stdout.log" -RedirectStandardError "$KimodoRoot\logs\frontend-install-$stamp.stderr.log"
if ($p.ExitCode -ne 0) { throw 'Frontend dependency install failed. See logs.' }
$args = @("$client\node_modules\vite\bin\vite.js",'build','--base','./','--outDir',"$client\build")
$p = Start-Process -FilePath $node -ArgumentList $args -WorkingDirectory $client -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput "$KimodoRoot\logs\frontend-build-$stamp.stdout.log" -RedirectStandardError "$KimodoRoot\logs\frontend-build-$stamp.stderr.log"
if ($p.ExitCode -ne 0) { throw 'Frontend build failed. See logs.' }
& $KimodoPython -c "from viser._client_autobuild import _write_last_built_src_hash, _compute_src_hash, client_dir; _write_last_built_src_hash(_compute_src_hash(client_dir / 'src'))"
if ($LASTEXITCODE -ne 0) { throw 'Frontend source hash registration failed.' }
Write-Host 'Viser frontend built. Upstream tracked files were not patched.'
