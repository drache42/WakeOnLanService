$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($env:DISCORD_WEBHOOK_URL)) {
    Write-Host 'DISCORD_WEBHOOK_URL is not set. Skipping notification.'
    exit 0
}

Write-Output "::add-mask::$env:DISCORD_WEBHOOK_URL"

$payload = @{ content = $env:DISCORD_MESSAGE } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri $env:DISCORD_WEBHOOK_URL -ContentType 'application/json' -Body $payload | Out-Null
