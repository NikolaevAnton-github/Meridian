# Repository and staged-blob validation share the same implementation.
[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [ValidateSet('Worktree','Staged')][string]$Mode = 'Worktree',
    [switch]$RelevantOnly,
    [switch]$AllowManagedRuntime,
    [string]$Output
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $RepositoryRoot) { $RepositoryRoot = Split-Path -Parent $PSScriptRoot }
. (Join-Path $PSScriptRoot 'ContextBudget/python.ps1')
$contextArgs = @((Join-Path $PSScriptRoot 'ContextBudget/context_budget.py'), '--root', $RepositoryRoot, 'guard', '--mode', $Mode.ToLowerInvariant())
if ($RelevantOnly) { $contextArgs += '--relevant-only' }
if ($AllowManagedRuntime -or $Mode -eq 'Worktree') { $contextArgs += '--allow-managed-runtime' }
if ($Output) { $contextArgs += @('--output', $Output) }
& (Get-ContextPython) @contextArgs
exit $LASTEXITCODE
