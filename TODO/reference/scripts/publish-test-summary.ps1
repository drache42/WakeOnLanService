$ErrorActionPreference = 'Stop'

function Get-Count($Counters, [string]$Name) {
    $value = $Counters.$Name
    if ([string]::IsNullOrWhiteSpace("$value")) {
        return 0
    }
    return [int]$value
}

$trxFiles = Get-ChildItem -Path artifacts/test-results -Filter *.trx -Recurse -ErrorAction SilentlyContinue
if (-not $trxFiles) {
    "## Test Results`n`nNo TRX files were produced." | Add-Content -Path $env:GITHUB_STEP_SUMMARY
    exit 0
}

$rows = New-Object System.Collections.Generic.List[string]
$total   = 0
$passed  = 0
$failed  = 0
$skipped = 0

foreach ($trxFile in $trxFiles) {
    [xml]$trx = Get-Content -Path $trxFile.FullName -Raw
    $counters = $trx.TestRun.ResultSummary.Counters

    $fileTotal   = Get-Count $counters total
    $filePassed  = Get-Count $counters passed
    $fileFailed  = (Get-Count $counters failed) + (Get-Count $counters error) + (Get-Count $counters timeout) + (Get-Count $counters aborted)
    $fileSkipped = (Get-Count $counters notExecuted) + (Get-Count $counters notRunnable) + (Get-Count $counters inconclusive)

    $total   += $fileTotal
    $passed  += $filePassed
    $failed  += $fileFailed
    $skipped += $fileSkipped

    $rows.Add("| $($trxFile.BaseName) | $filePassed | $fileFailed | $fileSkipped | $fileTotal |")
}

@(
    "## Test Results"
    ""
    "| Suite | Passed | Failed | Skipped | Total |"
    "| --- | ---: | ---: | ---: | ---: |"
    $rows
    ""
    "**Overall:** Passed $passed, Failed $failed, Skipped $skipped, Total $total"
) | Add-Content -Path $env:GITHUB_STEP_SUMMARY
