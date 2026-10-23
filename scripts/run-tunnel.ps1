param(
    [string]$TunnelClient = "$env:LOCALAPPDATA\agentpass\bin\tunnel-client.exe",
    [string]$Profile = "agentpass-local"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $TunnelClient)) {
    throw "tunnel-client not found at $TunnelClient"
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

& $TunnelClient run --profile $Profile
