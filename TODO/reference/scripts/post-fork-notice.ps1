$ErrorActionPreference = 'Stop'

$repo     = $env:GITHUB_REPOSITORY
$prNumber = $env:PR_NUMBER
$marker   = '<!-- semver-bot -->'

$body = @"
$marker
⚠️ **SemVer classification skipped** — this PR is from a fork.
A maintainer must apply one of the following labels manually:
``semver: major``, ``semver: minor``, ``semver: patch``, or ``skip-release``.
"@

$comments = @(gh api "repos/$repo/issues/$prNumber/comments" --paginate --jq '.[]' | ForEach-Object { $_ | ConvertFrom-Json })
$existing = $comments | Where-Object { $_.body -like "*$marker*" } | Select-Object -First 1

if ($existing) {
    @{ body = $body } | ConvertTo-Json | gh api --method PATCH "repos/$repo/issues/comments/$($existing.id)" --input - | Out-Null
} else {
    @{ body = $body } | ConvertTo-Json | gh api --method POST "repos/$repo/issues/$prNumber/comments" --input - | Out-Null
}
