# Intentionally lenient — missing data is handled gracefully by classify-pr.ps1

# Fetch complete file list with per-file stats (never truncated)
gh api `
    --paginate `
    "repos/$env:GITHUB_REPOSITORY/pulls/$env:PR_NUMBER/files" `
    --jq '.[] | "\(.status)\t\(.filename)\t+\(.additions)/-\(.deletions)"' `
    2>$null | Set-Content -Path /tmp/pr_files.txt -ErrorAction SilentlyContinue

# Fetch full diff and truncate to ~100 KB
gh api `
    -H "Accept: application/vnd.github.diff" `
    "repos/$env:GITHUB_REPOSITORY/pulls/$env:PR_NUMBER" `
    2>$null | Set-Content -Path /tmp/pr.diff -Encoding utf8 -ErrorAction SilentlyContinue

if (Test-Path /tmp/pr.diff) {
    $bytes = [System.IO.File]::ReadAllBytes('/tmp/pr.diff')
    $count = [Math]::Min($bytes.Length, 102400)
    if ($count -gt 0) {
        [System.IO.File]::WriteAllBytes('/tmp/pr_truncated.diff', $bytes[0..($count - 1)])
    }
}
