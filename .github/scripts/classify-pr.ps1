$ErrorActionPreference = 'Stop'

$files = Get-Content -Path /tmp/pr_files.txt -Raw -ErrorAction SilentlyContinue
$diff  = Get-Content -Path /tmp/pr_truncated.diff -Raw -ErrorAction SilentlyContinue

if ([string]::IsNullOrWhiteSpace($env:ANTHROPIC_MODEL)) {
    Write-Host 'ANTHROPIC_MODEL repository variable is not set -- skipping classification.'
    'classification=unknown' | Add-Content -Path $env:GITHUB_OUTPUT
    'rationale<<EOF_RATIONALE' | Add-Content -Path $env:GITHUB_OUTPUT
    'ANTHROPIC_MODEL repository variable is not configured -- set it in repository variables and apply a semver label manually.' | Add-Content -Path $env:GITHUB_OUTPUT
    'EOF_RATIONALE' | Add-Content -Path $env:GITHUB_OUTPUT
    exit 0
}

$systemPrompt = @'
You are a semantic versioning expert for the WakeOnLanService application (Python/Flask). Apply standard semver principles adapted for a deployed application: major = breaking deployment change; minor = new backward-compatible capability; patch = everything else. The changed-files list is always complete; the diff content may be truncated on very large PRs.

Project-specific rules (apply the HIGHEST matching tier):

MAJOR (breaking change): HTTP endpoint removed or renamed; required environment variable removed or renamed (MAC_ADDRESS, URL, SECRET_KEY); Flask app factory (create_app) signature changed incompatibly; Dockerfile ENTRYPOINT or EXPOSE changed; commit message contains "BREAKING CHANGE:"

MINOR (new backward-compatible feature): new HTTP endpoint/route added; new Flask blueprint registered; new environment variable with safe default; new HTML template page; new Python module added to src/wakeonlanservice/

PATCH (default): bug fixes; changes only in tests/ docs/ or *.md files; CI/infra/build changes (.github/ docker/); refactors with no behavioral change; dependency version bumps; logging improvements

Respond with valid JSON only, no other text: {"classification": "major"|"minor"|"patch", "rationale": "one sentence explaining the primary signal"}
'@

$userContent = "PR Title: $($env:PR_TITLE)`n`nChanged files (complete):`n$files`n`nDiff (may be truncated):`n$diff"

$payload = @{
    model      = $env:ANTHROPIC_MODEL
    max_tokens = 256
    system     = $systemPrompt
    messages   = @(
        @{
            role    = 'user'
            content = $userContent
        }
    )
} | ConvertTo-Json -Depth 5 -Compress

$classification = ''
$rationale      = ''

try {
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri 'https://api.anthropic.com/v1/messages' `
        -Headers @{
            'x-api-key'         = $env:ANTHROPIC_API_KEY
            'anthropic-version' = '2023-06-01'
        } `
        -ContentType 'application/json' `
        -Body $payload

    $rawText       = $response.content[0].text
    # Strip markdown code fences that some models add despite being told not to
    $rawText       = ($rawText -replace '(?ms)^\s*```[a-zA-Z]*\s*', '') -replace '(?ms)```\s*$', ''
    $parsed        = $rawText.Trim() | ConvertFrom-Json -ErrorAction SilentlyContinue
    $classification = $parsed.classification
    $rationale      = $parsed.rationale
} catch {
    Write-Host "API call failed: $_"
}

$validClassifications = @('major', 'minor', 'patch')
if ([string]::IsNullOrWhiteSpace($classification) -or $classification -notin $validClassifications) {
    $classification = 'unknown'
    $rationale      = 'Classification failed -- please apply a semver label manually.'
}

"classification=$classification" | Add-Content -Path $env:GITHUB_OUTPUT
'rationale<<EOF_RATIONALE'       | Add-Content -Path $env:GITHUB_OUTPUT
$rationale                       | Add-Content -Path $env:GITHUB_OUTPUT
'EOF_RATIONALE'                  | Add-Content -Path $env:GITHUB_OUTPUT
