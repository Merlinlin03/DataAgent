[CmdletBinding()]
param(
    [switch]$Background
)

$ErrorActionPreference = "Stop"
$cloudflaredCommand = Get-Command cloudflared -ErrorAction SilentlyContinue
$cloudflaredPath = if ($cloudflaredCommand) { $cloudflaredCommand.Source } else { $null }

if (-not $cloudflaredPath) {
    $installedPath = "C:\\Program Files (x86)\\cloudflared\\cloudflared.exe"
    if (Test-Path $installedPath) {
        $cloudflaredPath = $installedPath
    }
}

if (-not $cloudflaredPath) {
    Write-Host "cloudflared is not installed. Install it with: winget install --id Cloudflare.cloudflared"
    exit 1
}

try {
    Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:5173/" -TimeoutSec 5 | Out-Null
} catch {
    throw "Frontend is unavailable. Run .\\scripts\\start-demo.ps1 first."
}

Write-Host "Starting Cloudflare Quick Tunnel. Keep this window open during the demo."
Write-Host "The public HTTPS address will be printed below. It changes after each restart."

if ($Background) {
    $projectRoot = Split-Path -Parent $PSScriptRoot
    $runtimeDir = Join-Path $projectRoot ".run"
    $logDir = Join-Path $projectRoot "logs"
    $tunnelOutput = Join-Path $logDir "cloudflared.tunnel.log"
    $tunnelError = Join-Path $logDir "cloudflared.tunnel.err.log"
    New-Item -ItemType Directory -Force -Path $runtimeDir, $logDir | Out-Null
    Remove-Item $tunnelOutput, $tunnelError -Force -ErrorAction SilentlyContinue

    $tunnelProcess = Start-Process `
        -FilePath $cloudflaredPath `
        -ArgumentList "tunnel", "--no-autoupdate", "--url", "http://127.0.0.1:5173" `
        -WindowStyle Hidden `
        -RedirectStandardOutput $tunnelOutput `
        -RedirectStandardError $tunnelError `
        -PassThru
    $tunnelProcess.Id | Set-Content (Join-Path $runtimeDir "tunnel.pid")

    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        $url = Select-String -Path $tunnelOutput, $tunnelError -Pattern 'https://[-a-z0-9]+\.trycloudflare\.com' -AllMatches -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Matches.Value } |
            Select-Object -First 1
        if ($url) {
            Write-Host "Public demo URL: $url"
            return
        }
        Start-Sleep -Seconds 1
    }

    Write-Warning "Tunnel is running, but its URL was not detected. Check $tunnelError."
    return
}

& $cloudflaredPath tunnel --no-autoupdate --url "http://127.0.0.1:5173"
