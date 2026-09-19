# Interactive only: do not run under a transcript or pass a token as an argument.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Environment.ps1"
Write-Host 'First request/confirm access at https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct'
Write-Host 'Paste a read token only into the hidden local prompt. Choose No for Git credential storage.'
& "$KimodoRoot\.venv\Scripts\hf.exe" auth login
exit $LASTEXITCODE
