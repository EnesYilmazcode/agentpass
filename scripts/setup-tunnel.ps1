param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^tunnel_[A-Za-z0-9]+$')]
    [string]$TunnelId,

    [string]$TunnelClient = "$env:LOCALAPPDATA\agentpass\bin\tunnel-client.exe",
    [string]$Profile = "agentpass-local"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $TunnelClient)) {
    throw "tunnel-client not found at $TunnelClient"
}
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment not found. Run: py -m venv .venv"
}
if (-not $env:CONTROL_PLANE_API_KEY) {
    $secureKey = Read-Host "OpenAI tunnel runtime API key" -AsSecureString
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try {
        $env:CONTROL_PLANE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
    }
}

$mcpCommand = "`"$python`" -m agentpass.mcp"
& $TunnelClient init `
    --sample sample_mcp_stdio_local `
    --profile $Profile `
    --tunnel-id $TunnelId `
    --mcp-command $mcpCommand

if ($LASTEXITCODE -ne 0) {
    throw "tunnel-client init failed with exit code $LASTEXITCODE"
}

& $TunnelClient doctor --profile $Profile --explain
if ($LASTEXITCODE -ne 0) {
    throw "tunnel-client doctor failed with exit code $LASTEXITCODE"
}

Write-Host "Tunnel profile '$Profile' is valid. Start it with:"
Write-Host "  & '$TunnelClient' run --profile '$Profile'"
