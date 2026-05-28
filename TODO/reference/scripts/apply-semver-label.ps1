$ErrorActionPreference = 'Stop'

$repo           = $env:GITHUB_REPOSITORY
$prNumber       = $env:PR_NUMBER
$classification = if ($env:CLASSIFICATION) { $env:CLASSIFICATION } else { 'unknown' }
$rationale      = if ($env:RATIONALE)      { $env:RATIONALE }      else { 'No rationale provided.' }

$labelMap = @{
    major   = 'semver: major'
    minor   = 'semver: minor'
    patch   = 'semver: patch'
    unknown = 'semver: unknown'
}
$semverLabels = @($labelMap.Values)
$labelToApply = if ($labelMap.ContainsKey($classification)) { $labelMap[$classification] } else { 'semver: unknown' }

# Remove existing semver labels except the one we're applying
$currentLabels = @(gh api "repos/$repo/issues/$prNumber/labels" | ConvertFrom-Json)
foreach ($label in $currentLabels) {
    if ($label.name -in $semverLabels -and $label.name -ne $labelToApply) {
        $encodedName = [uri]::EscapeDataString($label.name)
        gh api --method DELETE "repos/$repo/issues/$prNumber/labels/$encodedName" | Out-Null
    }
}

# Apply label if not already present
if ($currentLabels.name -notcontains $labelToApply) {
    gh issue edit $prNumber --repo $repo --add-label $labelToApply
}

# Post or update bot comment
$marker   = '<!-- semver-bot -->'
$emojiMap = @{ major = '🔴'; minor = '🟡'; patch = '🟢'; unknown = '🟠' }
$emoji    = if ($emojiMap.ContainsKey($classification)) { $emojiMap[$classification] } else { '🟠' }

$body = @"
$marker
$emoji **SemVer classification:** ``$labelToApply``

**Rationale:** $rationale
"@

$comments = @(gh api "repos/$repo/issues/$prNumber/comments" --paginate --jq '.[]' | ForEach-Object { $_ | ConvertFrom-Json })
$existing = $comments | Where-Object { $_.body -like "*$marker*" } | Select-Object -First 1

if ($existing) {
    @{ body = $body } | ConvertTo-Json | gh api --method PATCH "repos/$repo/issues/comments/$($existing.id)" --input - | Out-Null
} else {
    @{ body = $body } | ConvertTo-Json | gh api --method POST "repos/$repo/issues/$prNumber/comments" --input - | Out-Null
}
