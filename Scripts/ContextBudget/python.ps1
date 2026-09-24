# Resolve an existing Python 3.11+ installation; never install packages.
function Get-ContextPython {
    $candidates = @()
    if ($env:CONTEXT_BUDGET_PYTHON) { $candidates += $env:CONTEXT_BUDGET_PYTHON }
    $candidates += @(Get-ChildItem -Path (Join-Path $env:APPDATA 'uv/python/cpython-*/python.exe') -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | ForEach-Object { $_.FullName })
    $candidates += @(Get-Command python3, python -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | ForEach-Object { $_.Source })
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            & $candidate -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        }
    }
    throw 'Python 3.11+ required. Set process-local CONTEXT_BUDGET_PYTHON to an existing interpreter.'
}
