[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot ".run"
$logDir = Join-Path $projectRoot "logs"
$containers = @("mysql", "qdrant", "embedding", "elasticsearch")

if (-not (Test-Path (Join-Path $projectRoot ".env"))) {
    throw "Missing .env. Copy .env.example to .env and fill in local credentials."
}

foreach ($container in $containers) {
    $isRunning = (& docker inspect -f '{{.State.Running}}' $container 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Docker container '$container' was not found. Create it before starting the demo."
    }
    if ($isRunning -ne "true") {
        & docker start $container | Out-Null
    }
}

function Wait-ForHttp([string]$Url, [int]$Attempts = 20) {
    for ($attempt = 0; $attempt -lt $Attempts; $attempt++) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3 | Out-Null
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    throw "Service did not become available: $Url"
}

New-Item -ItemType Directory -Force -Path $runtimeDir, $logDir | Out-Null

try {
    Wait-ForHttp "http://127.0.0.1:9200"
} catch {
    throw "Elasticsearch is not ready. Check Docker Desktop and container logs."
}

$apiUrl = "http://127.0.0.1:8000/openapi.json"
try {
    Invoke-WebRequest -UseBasicParsing -Uri $apiUrl -TimeoutSec 3 | Out-Null
    Write-Host "API already running on http://127.0.0.1:8000"
} catch {
    $apiProcess = Start-Process `
        -FilePath (Join-Path $projectRoot ".venv\\Scripts\\python.exe") `
        -ArgumentList "main.py" `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir "api.stdout.log") `
        -RedirectStandardError (Join-Path $logDir "api.stderr.log") `
        -PassThru
    $apiProcess.Id | Set-Content (Join-Path $runtimeDir "api.pid")
    Wait-ForHttp $apiUrl
}

$frontendUrl = "http://127.0.0.1:5173/"
try {
    Invoke-WebRequest -UseBasicParsing -Uri $frontendUrl -TimeoutSec 3 | Out-Null
    Write-Host "Frontend already running on http://127.0.0.1:5173"
} catch {
    $frontendRoot = Join-Path $projectRoot "frontend"
    $frontendProcess = Start-Process `
        -FilePath "node.exe" `
        -ArgumentList "node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", "5173" `
        -WorkingDirectory $frontendRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir "frontend.stdout.log") `
        -RedirectStandardError (Join-Path $logDir "frontend.stderr.log") `
        -PassThru
    $frontendProcess.Id | Set-Content (Join-Path $runtimeDir "frontend.pid")
    Wait-ForHttp $frontendUrl
}

Write-Host ""
Write-Host "InsightQuery demo is ready: http://127.0.0.1:5173/"
Write-Host "Run .\\scripts\\start-tunnel.ps1 to create a temporary public HTTPS URL."
