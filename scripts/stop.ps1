[CmdletBinding()]
param(
    [switch]$StopDependencies,
    [switch]$StopTunnel
)

& (Join-Path $PSScriptRoot "stop-demo.ps1") @PSBoundParameters
