$ErrorActionPreference = 'Stop'

$xmlFiles = Get-ChildItem -Path test-results -Filter *.xml -Recurse -ErrorAction SilentlyContinue
if (-not $xmlFiles) {
    "## Test Results`n`nNo JUnit XML files were produced." | Add-Content -Path $env:GITHUB_STEP_SUMMARY
    exit 0
}

$rows    = New-Object System.Collections.Generic.List[string]
$total   = 0
$passed  = 0
$failed  = 0
$skipped = 0

foreach ($xmlFile in $xmlFiles) {
    [xml]$doc = Get-Content -Path $xmlFile.FullName -Raw
    $suites = if ($doc.testsuites) { $doc.testsuites.testsuite } else { @($doc.testsuite) }

    foreach ($suite in $suites) {
        if (-not $suite) { continue }

        $sTests    = [int]($suite.tests    ?? 0)
        $sFailures = [int]($suite.failures ?? 0)
        $sErrors   = [int]($suite.errors   ?? 0)
        $sSkipped  = [int]($suite.skipped  ?? 0)
        $sPassed   = $sTests - $sFailures - $sErrors - $sSkipped

        $total   += $sTests
        $passed  += $sPassed
        $failed  += ($sFailures + $sErrors)
        $skipped += $sSkipped

        $suiteName = if ($suite.name) { $suite.name } else { $xmlFile.BaseName }
        $rows.Add("| $suiteName | $sPassed | $($sFailures + $sErrors) | $sSkipped | $sTests |")
    }
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
