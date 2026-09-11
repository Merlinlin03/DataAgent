[CmdletBinding()]
param(
    [switch]$StopDependencies,
    [switch]$StopTunnel
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot ".run"

$processNames = @("api", "frontend")
if ($StopTunnel) {
    $processNames += "tunnel"
}

foreach ($name in $processNames) {
    $pidFile = Join-Path $runtimeDir "$name.pid"
    if (-not (Test-Path $pidFile)) {
        continue
    }

    $processId = Get-Content $pidFile -Raw
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $processId -Force
        Write-Host "Stopped $name process ($processId)."
    }
    Remove-Item $pidFile -Force
}

if ($StopDependencies) {
    & docker stop mysql qdrant embedding elasticsearch | Out-Null
    Write-Host "Stopped InsightQuery Docker dependencies."
}
