$ErrorActionPreference = 'Stop'

$latestTag = git tag -l 'v*' --sort=-v:refname | Select-Object -First 1
Write-Host "Latest tag: $(if ($latestTag) { $latestTag } else { 'none' })"

if (-not $latestTag) {
    $major    = 1
    $minor    = 0
    $patch    = 0
    $taggedAt = '1970-01-01T00:00:00Z'
} else {
    $parts    = $latestTag.TrimStart('v').Split('.')
    $major    = [int]$parts[0]
    $minor    = [int]$parts[1]
    $patch    = [int]$parts[2]
    $taggedAt = git log -1 --format='%cI' $latestTag
}

Write-Host "Current version: $major.$minor.$patch (tagged at $taggedAt)"
$shortSha = $env:GITHUB_SHA.Substring(0, 7)

$taggedAtDto = [DateTimeOffset]::Parse($taggedAt)
$allPRs      = gh pr list --repo $env:GITHUB_REPOSITORY --state merged --base main --limit 1000 --json number,labels,mergedAt | ConvertFrom-Json
$mergedPRs   = @($allPRs | Where-Object { $_.mergedAt -ne $null -and [DateTimeOffset]::Parse($_.mergedAt) -gt $taggedAtDto })

$prCount = $mergedPRs.Count
Write-Host "PRs merged since last tag: $prCount"

if ($prCount -eq 0) {
    Write-Host 'No PRs merged since last tag.'
    "skip=true"                    | Add-Content -Path $env:GITHUB_OUTPUT
    "version=$major.$minor.$patch" | Add-Content -Path $env:GITHUB_OUTPUT
    "short_sha=$shortSha"          | Add-Content -Path $env:GITHUB_OUTPUT
    exit 0
}

$triggerPR      = $mergedPRs | Sort-Object mergedAt | Select-Object -Last 1
$triggerHasSkip = $triggerPR.labels | Where-Object { $_.name -eq 'skip-release' }

if ($triggerHasSkip) {
    Write-Host 'Triggering PR has skip-release -- deferring release.'
    "skip=true"                    | Add-Content -Path $env:GITHUB_OUTPUT
    "version=$major.$minor.$patch" | Add-Content -Path $env:GITHUB_OUTPUT
    "short_sha=$shortSha"          | Add-Content -Path $env:GITHUB_OUTPUT
    exit 0
}

$hasMajor     = $false
$hasMinor     = $false
$hasPatch     = $false
$hasAnySemver = $false

foreach ($pr in $mergedPRs) {
    $labelNames = @($pr.labels | ForEach-Object { $_.name })
    if ($labelNames -contains 'semver: major') {
        $hasMajor = $true; $hasAnySemver = $true
    } elseif ($labelNames -contains 'semver: minor') {
        $hasMinor = $true; $hasAnySemver = $true
    } elseif ($labelNames -contains 'semver: patch') {
        $hasPatch = $true; $hasAnySemver = $true
    }
}

if (-not $hasAnySemver) {
    Write-Host 'No semver labels found among merged PRs -- skipping release.'
    "skip=true"                    | Add-Content -Path $env:GITHUB_OUTPUT
    "version=$major.$minor.$patch" | Add-Content -Path $env:GITHUB_OUTPUT
    "short_sha=$shortSha"          | Add-Content -Path $env:GITHUB_OUTPUT
    exit 0
}

if ($hasMajor) {
    $newVersion = "$($major + 1).0.0"
} elseif ($hasMinor) {
    $newVersion = "$major.$($minor + 1).0"
} else {
    $newVersion = "$major.$minor.$($patch + 1)"
}

Write-Host "New version: $newVersion"
"skip=false"           | Add-Content -Path $env:GITHUB_OUTPUT
"version=$newVersion"  | Add-Content -Path $env:GITHUB_OUTPUT
"short_sha=$shortSha"  | Add-Content -Path $env:GITHUB_OUTPUT
