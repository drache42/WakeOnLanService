# Plan: WakeOnLanService CI/CD Pipeline

## TL;DR
Implement a full CI/CD pipeline for WakeOnLanService: semver PR labeling with AI classification, label-gated merges, automatic versioning from PR labels, Docker Hub image promotion, GitHub Releases, Discord notifications, and Dependabot automerge. Keep reusable workflow pattern and Docker Hub registry. Structured in 3 phases for Claude Sonnet 4.6 execution.

## Reference Files
All reference templates from the source project are available locally in `TODO/reference/`. These are the starting points -- each must be adapted for this Python/Flask project. **Do not reference or access any other repository.**

```
TODO/reference/
  scripts/
    compute-version.ps1     # Version computation from PR labels (language-agnostic)
    classify-pr.ps1          # AI classification via Anthropic Claude API
    apply-semver-label.ps1   # Label management and bot comments
    fetch-pr-diff.ps1        # Fetch PR diff via GitHub API
    notify-discord.ps1       # Discord webhook notifications
    post-fork-notice.ps1     # Fork PR handling comment
    publish-test-summary.ps1 # Test summary for .NET TRX format (must be REWRITTEN for pytest JUnit XML)
  workflows/
    classify-pr.yml          # AI PR classification workflow
    label-gate.yml           # Required status check for semver labels
    automerge.yml            # Dependabot auto-merge for patch/minor
    main.yml                 # Main pipeline (.NET/ghcr.io -- must be REWRITTEN for Python/Docker Hub)
    pr.yml                   # PR validation (.NET -- must be REWRITTEN for Python reusable workflows)
  config/
    release.yml              # GitHub Release notes categorization
    dependabot.yml           # Dependabot config (.NET/NuGet -- must be REWRITTEN for pip/Docker)
```

## Current State (WakeOnLanService)
- `main.yml` orchestrates lint, unit-tests, integration-tests (reusable workflows), docker-publish on `release/*` tags
- Docker Hub: `drache42/wakeonlanservice`
- Manual version tags (`release/X.Y.Z`)
- No semver labeling, no auto-release, no Discord, no Dependabot config, no test summaries
- Secrets that already exist: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- Existing reusable workflows: `linter.yml`, `unit-tests.yml`, `integration-tests.yml`, `docker-publish.yml`

## Target State
- PR labeling with Claude AI classification (`semver: major/minor/patch`)
- Label gate (required status check blocks merge without label)
- PR validation with test summaries
- On merge to main: compute version from PR labels, build+push Docker image, auto-release (git tag + GitHub Release + image promotion)
- Discord notifications on failures and releases
- Dependabot with automerge for patch/minor
- Reusable workflows preserved for lint/test/integration

---

## Phase 1: Foundation -- Scripts, Config, and Reusable Workflow Updates

**Goal:** Create all supporting scripts and configuration files. Update existing reusable workflows to produce test artifacts.

### Steps

1. **Create `.github/scripts/` directory with 7 scripts:**

   a. **`compute-version.ps1`** -- Use `TODO/reference/scripts/compute-version.ps1` as template. Logic is language-agnostic (queries merged PRs since last `v*` tag, aggregates semver labels, bumps version). **Change the default fallback version from `1.1.2` to `1.0.0`** (lines 7-9: `$major=1`, `$minor=0`, `$patch=0`) to match WOL's current pyproject.toml version. Everything else stays the same.

   b. **`classify-pr.ps1`** -- Use `TODO/reference/scripts/classify-pr.ps1` as template. Keep all the Anthropic API calling logic, error handling, and output format identical. **Replace only the `$systemPrompt` here-string** with this WakeOnLanService-specific prompt:
      ```
      You are a semantic versioning expert for the WakeOnLanService application (Python/Flask). Apply standard semver principles adapted for a deployed application: major = breaking deployment change; minor = new backward-compatible capability; patch = everything else. The changed-files list is always complete; the diff content may be truncated on very large PRs.

      Project-specific rules (apply the HIGHEST matching tier):

      MAJOR (breaking change): HTTP endpoint removed or renamed; required environment variable removed or renamed (MAC_ADDRESS, URL, SECRET_KEY); Flask app factory (create_app) signature changed incompatibly; Dockerfile ENTRYPOINT or EXPOSE changed; commit message contains "BREAKING CHANGE:"

      MINOR (new backward-compatible feature): new HTTP endpoint/route added; new Flask blueprint registered; new environment variable with safe default; new HTML template page; new Python module added to src/wakeonlanservice/

      PATCH (default): bug fixes; changes only in tests/ docs/ or *.md files; CI/infra/build changes (.github/ docker/); refactors with no behavioral change; dependency version bumps; logging improvements

      Respond with valid JSON only, no other text: {"classification": "major"|"minor"|"patch", "rationale": "one sentence explaining the primary signal"}
      ```

   c. **`apply-semver-label.ps1`** -- Copy `TODO/reference/scripts/apply-semver-label.ps1` verbatim (generic, no project-specific content).
   
   d. **`fetch-pr-diff.ps1`** -- Copy `TODO/reference/scripts/fetch-pr-diff.ps1` verbatim (generic GitHub API calls).
   
   e. **`notify-discord.ps1`** -- Copy `TODO/reference/scripts/notify-discord.ps1` verbatim (generic webhook post).
   
   f. **`post-fork-notice.ps1`** -- Copy `TODO/reference/scripts/post-fork-notice.ps1` verbatim (generic PR comment).
   
   g. **`publish-test-summary.ps1`** -- **Write a NEW script** for pytest JUnit XML format. Do NOT use the reference `publish-test-summary.ps1` (that one parses .NET TRX files). The new script must:
      - Search for `*.xml` files under `test-results/` recursively
      - Parse each as JUnit XML: `<testsuite>` elements have attributes `name`, `tests`, `failures`, `errors`, `skipped`
      - Calculate passed = tests - failures - errors - skipped
      - Output a markdown table to `$env:GITHUB_STEP_SUMMARY` with columns: Suite | Passed | Failed | Skipped | Total
      - Output an overall summary line
      - Handle the case where no XML files are found gracefully
      - Use `$ErrorActionPreference = 'Stop'`

2. **Create `.github/release.yml`** -- Copy `TODO/reference/config/release.yml` verbatim. It categorizes release notes by semver labels and excludes `skip-release`. No changes needed.

3. **Create `.github/dependabot.yml`** -- **Write new** based on `TODO/reference/config/dependabot.yml` structure but with these ecosystems:
   - `pip` (directory: `/`, schedule: weekly, target-branch: main, group non-major patch+minor)
   - `docker` (directory: `/docker`, schedule: weekly, target-branch: main, group non-major patch+minor)
   - `github-actions` (directory: `/`, schedule: weekly, target-branch: main, group non-major patch+minor)

4. **Update `.github/workflows/unit-tests.yml`** -- Add JUnit XML output and artifact upload:
   - Change the pytest run step command to: `poetry run pytest tests/unit --junitxml=test-results/unit-py${{ matrix.python-version }}.xml`
   - Add a new step after the pytest step:
     ```yaml
     - name: Upload test results
       if: always()
       uses: actions/upload-artifact@v4
       with:
         name: test-results-unit-py${{ matrix.python-version }}
         path: test-results/
         if-no-files-found: warn
     ```

5. **Update `.github/workflows/integration-tests.yml`** -- Add JUnit XML output and artifact upload:
   - Change the pytest run step command to: `poetry run pytest tests/integration -v --log-cli-level=INFO --junitxml=test-results/integration.xml`
   - Add a new step after the pytest step:
     ```yaml
     - name: Upload test results
       if: always()
       uses: actions/upload-artifact@v4
       with:
         name: test-results-integration
         path: test-results/
         if-no-files-found: warn
     ```

6. **No changes to `linter.yml`** -- Linting has no test output to capture.

### Files Created/Modified
- CREATE: `.github/scripts/compute-version.ps1`
- CREATE: `.github/scripts/classify-pr.ps1`
- CREATE: `.github/scripts/apply-semver-label.ps1`
- CREATE: `.github/scripts/fetch-pr-diff.ps1`
- CREATE: `.github/scripts/notify-discord.ps1`
- CREATE: `.github/scripts/post-fork-notice.ps1`
- CREATE: `.github/scripts/publish-test-summary.ps1`
- CREATE: `.github/release.yml`
- CREATE: `.github/dependabot.yml`
- MODIFY: `.github/workflows/unit-tests.yml`
- MODIFY: `.github/workflows/integration-tests.yml`

### Verification
- All `.ps1` scripts should be syntactically valid PowerShell
- YAML files should be valid (no tabs, proper indentation)
- Reusable workflow changes should not break existing test functionality
- `publish-test-summary.ps1` should handle both single and multiple JUnit XML files
- `compute-version.ps1` default version should be `1.0.0` (not `1.1.2`)
- `classify-pr.ps1` system prompt should reference Python/Flask, not .NET

---

## Phase 2: Workflows -- PR Pipeline, Main Pipeline, and Automation

**Goal:** Create the new workflow files and rewrite main.yml to implement the full CI/CD pipeline.

### Steps

1. **Create `.github/workflows/pr.yml`** -- PR Validation workflow. Use `TODO/reference/workflows/pr.yml` for structural reference but **rewrite completely** for Python:
   - Trigger: `pull_request` to `main`
   - Permissions: `contents: read`
   - Jobs:
     - `lint`: calls `./.github/workflows/linter.yml` with `python-version: "3.13"`
     - `unit-tests`: calls `./.github/workflows/unit-tests.yml` with `matrix: '["3.9", "3.10", "3.11", "3.12", "3.13"]'`
     - `integration-tests`: calls `./.github/workflows/integration-tests.yml` with `python-version: "3.13"`
     - `test-summary` (inline job): depends on `[lint, unit-tests, integration-tests]`, runs `if: always()`, uses `ubuntu-latest` with `shell: pwsh`:
       1. Checkout code (to access `.github/scripts/`)
       2. Download all artifacts matching `test-results-*` pattern using `actions/download-artifact@v4` with `path: test-results/` and `merge-multiple: true`
       3. Run `.github/scripts/publish-test-summary.ps1`
     - `notify-discord` (inline job): depends on `[lint, unit-tests, integration-tests, test-summary]`, runs only when any prior job failed AND PR is from same repo (not fork). Uses `shell: pwsh`:
       1. Posts failure notification via inline Discord webhook call (env: `DISCORD_WEBHOOK_URL` from secrets, `DISCORD_MESSAGE` with repo/PR/branch/run info)
       2. The inline script should be: `if ([string]::IsNullOrWhiteSpace($env:DISCORD_WEBHOOK_URL)) { exit 0 }; Write-Output "::add-mask::$env:DISCORD_WEBHOOK_URL"; $payload = @{ content = $env:DISCORD_MESSAGE } | ConvertTo-Json -Compress; Invoke-RestMethod -Method Post -Uri $env:DISCORD_WEBHOOK_URL -ContentType 'application/json' -Body $payload | Out-Null`

2. **Create `.github/workflows/classify-pr.yml`** -- Copy `TODO/reference/workflows/classify-pr.yml` verbatim. It is already generic -- it calls `.github/scripts/` which will contain the WOL-specific classify-pr.ps1 from Phase 1. Uses `actions/checkout@v6`. No changes needed.

3. **Create `.github/workflows/label-gate.yml`** -- Copy `TODO/reference/workflows/label-gate.yml` verbatim. It is fully generic (checks for semver labels via GitHub API). No changes needed.

4. **Create `.github/workflows/automerge.yml`** -- Copy `TODO/reference/workflows/automerge.yml` verbatim. It is fully generic (enables auto-merge for Dependabot patch/minor PRs). No changes needed.

5. **Rewrite `.github/workflows/main.yml`** -- Use `TODO/reference/workflows/main.yml` for structural patterns (compute-version, auto-release, notify-discord jobs) but **rewrite completely** for Python/Docker Hub. The new file should:
   - **Name:** `Main Pipeline`
   - **Trigger:** `push` to `main` + `workflow_dispatch` (remove PR triggers, remove tag triggers that exist in current main.yml)
   - **Permissions:** `contents: read`
   - **Concurrency:** `group: main-pipeline`, `cancel-in-progress: false`
   - **Jobs:**
     - `lint`: calls `./.github/workflows/linter.yml` with `python-version: "3.13"`
     - `unit-tests`: calls `./.github/workflows/unit-tests.yml` with `matrix: '["3.9", "3.10", "3.11", "3.12", "3.13"]'`
     - `integration-tests`: calls `./.github/workflows/integration-tests.yml` with `python-version: "3.13"`
     - `test-summary` (inline): same structure as in pr.yml above. Depends on `[lint, unit-tests, integration-tests]`, `if: always()`.
     - `compute-version` (inline): **only on push to main** (`if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}`). Depends on `[lint, unit-tests, integration-tests]`. Permissions: `contents: read`, `pull-requests: read`. Uses `pwsh` shell. Checkout with `fetch-depth: 0`. Runs `.github/scripts/compute-version.ps1`. Outputs: `version`, `skip`, `short_sha`. Env: `GH_TOKEN: ${{ github.token }}`.
     - `publish-main-image` (inline): Depends on `[lint, unit-tests, integration-tests, compute-version]`. Condition: `github.event_name == 'push' && github.ref == 'refs/heads/main' && needs.compute-version.result == 'success'`. Uses `pwsh` shell. Steps:
       1. Checkout code
       2. Setup Docker Buildx (`docker/setup-buildx-action@v3`)
       3. Login to Docker Hub (`docker/login-action@v3` with `username: ${{ secrets.DOCKER_USERNAME }}`, `password: ${{ secrets.DOCKER_PASSWORD }}` -- **no registry field** since Docker Hub is default)
       4. Compute image name: `$shortSha = $env:GITHUB_SHA.Substring(0, 7); "image=drache42/wakeonlanservice" | Add-Content $env:GITHUB_OUTPUT; "short_sha=$shortSha" | Add-Content $env:GITHUB_OUTPUT`
       5. Build and push Docker image (`docker/build-push-action@v5`) with:
          - `context: .`
          - `file: docker/Dockerfile`
          - `push: true`
          - Tags: `drache42/wakeonlanservice:main`, `drache42/wakeonlanservice:sha-<short_sha>`
          - Labels: `org.opencontainers.image.source`, `org.opencontainers.image.revision`
          - Cache: `cache-from: type=gha,scope=app-image`, `cache-to: type=gha,mode=max,scope=app-image`
     - `auto-release` (inline): Depends on `[compute-version, publish-main-image]`. Condition: push to main AND `compute-version.outputs.skip == 'false'` AND `publish-main-image.result == 'success'`. Permissions: `contents: write`. Uses `pwsh` shell. Steps:
       1. Checkout with `fetch-depth: 0`
       2. Configure git identity (`github-actions[bot]`)
       3. Create and push release tag `v<version>` (skip if tag already exists)
       4. Setup Docker Buildx + Login to Docker Hub
       5. Promote Docker image: `docker buildx imagetools create` to retag `sha-<sha>` as `<version>`, `<major.minor>`, and `latest` -- **single image** (not worker/admin like reference):
          ```
          docker buildx imagetools create \
            --tag "drache42/wakeonlanservice:$VERSION" \
            --tag "drache42/wakeonlanservice:$MAJOR_MINOR" \
            --tag "drache42/wakeonlanservice:latest" \
            "drache42/wakeonlanservice:sha-$SHORT_SHA"
          ```
       6. Create GitHub Release (`gh release create "v$VERSION" --title "v$VERSION" --generate-notes --latest`). Skip if release already exists.
       7. Discord release notification via `.github/scripts/notify-discord.ps1`
     - `notify-discord` (inline): Depends on all jobs. Condition: `always()` AND any job failed. Posts failure notification via `.github/scripts/notify-discord.ps1`. Needs checkout to access the script.

6. **Delete `.github/workflows/docker-publish.yml`** -- Replaced by inline Docker steps in main.yml. The `release/*` tag-based flow is superseded by the label-based auto-release.

### Files Created/Modified/Deleted
- CREATE: `.github/workflows/pr.yml`
- CREATE: `.github/workflows/classify-pr.yml`
- CREATE: `.github/workflows/label-gate.yml`
- CREATE: `.github/workflows/automerge.yml`
- REWRITE: `.github/workflows/main.yml`
- DELETE: `.github/workflows/docker-publish.yml`

### Verification
- All YAML workflows should have valid syntax (proper indentation, no tabs)
- Job dependency graph should have no circular dependencies
- `compute-version` job's `if` condition correctly gates on push-to-main only
- `auto-release` job's `if` condition correctly gates on `skip==false` + publish success
- Docker login uses `secrets.DOCKER_USERNAME` and `secrets.DOCKER_PASSWORD` (existing secrets), NOT ghcr.io
- Docker image name is `drache42/wakeonlanservice` (single image, not worker/admin)
- Dockerfile path is `docker/Dockerfile` (not `infra/Dockerfile`)
- GitHub Release uses `github.token` (built-in)
- Git tag push uses `contents: write` permission
- `classify-pr.yml` uses `pull_request_target` (not `pull_request`) for secret access
- `label-gate.yml` handles both direct PR events and `workflow_run` events
- PR workflow triggers ONLY on `pull_request` to main (not push, not tags)
- Main workflow triggers ONLY on `push` to main + `workflow_dispatch` (no PR triggers, no tag triggers)

---

## Phase 3: Human Configuration Steps (Guided 1-by-1)

**Goal:** Configure GitHub repository settings that cannot be done via code. The AI walks the user through each step, verifying completion before moving to the next.

### Steps (executed sequentially with verification)

1. **Create GitHub Labels** -- The AI should create these labels via `gh` CLI in the WakeOnLanService repo:
   - `semver: major` (color: `d73a49`)
   - `semver: minor` (color: `fbca04`)
   - `semver: patch` (color: `0e8a16`)
   - `semver: unknown` (color: `e99695`)
   - `skip-release` (color: `ededed`)
   - Verify: `gh label list --repo drache42/WakeOnLanService` shows all 5

2. **Add `ANTHROPIC_API_KEY` repository secret** -- Walk user through:
   - Settings > Secrets and variables > Actions > New repository secret
   - Name: `ANTHROPIC_API_KEY`, Value: their Anthropic API key
   - Verify: `gh secret list --repo drache42/WakeOnLanService` shows ANTHROPIC_API_KEY

3. **Add `ANTHROPIC_MODEL` repository variable** -- Walk user through:
   - Settings > Secrets and variables > Actions > Variables > New repository variable
   - Name: `ANTHROPIC_MODEL`, Value: e.g. `claude-sonnet-4-20250514`
   - Verify: `gh variable list --repo drache42/WakeOnLanService` shows ANTHROPIC_MODEL

4. **Add `DISCORD_WEBHOOK_URL` repository secret** -- Walk user through:
   - Settings > Secrets and variables > Actions > New repository secret
   - Name: `DISCORD_WEBHOOK_URL`, Value: their Discord webhook URL
   - Verify: `gh secret list --repo drache42/WakeOnLanService` shows DISCORD_WEBHOOK_URL

5. **Verify Docker Hub secrets exist** -- `DOCKER_USERNAME` and `DOCKER_PASSWORD` should already be configured.
   - Verify: `gh secret list --repo drache42/WakeOnLanService` shows both
   - If missing, walk user through adding them

6. **Create initial version tag** -- Tag the current main branch as `v1.0.0` so compute-version has a baseline.
   - `git tag -a v1.0.0 HEAD -m "Release v1.0.0"` then `git push origin v1.0.0`
   - Verify: `git tag -l 'v*'` shows `v1.0.0`

7. **Configure branch protection** -- Walk user through adding `label-gate` as a required status check on the `main` branch.
   - Settings > Branches > Branch protection rules > Edit rule for `main`
   - Add `label-gate` to "Require status checks to pass before merging"
   - Verify: open a test PR and confirm the label-gate check appears

### Cleanup

8. **Delete `TODO/reference/` directory** -- After all phases are complete, delete the reference files:
   - `rm -rf TODO/reference/`
   - If `TODO/` is now empty, delete it too

---

## Decisions
- Docker Hub registry preserved (existing `drache42/wakeonlanservice` image)
- Reusable workflow pattern preserved for lint/test/integration
- Full Python matrix (3.9-3.13) on both PR and main
- `release/*` tag workflow removed in favor of PR-label-driven auto-release
- `compute-version.ps1` default version set to 1.0.0 matching pyproject.toml
- `classify-pr.ps1` system prompt rewritten for Python/Flask project specifics
- `publish-test-summary.ps1` written from scratch for JUnit XML (pytest) instead of TRX (.NET)

## Further Considerations
1. **pyproject.toml version sync** -- The version in pyproject.toml (currently 1.0.0) is static and won't auto-update with releases. This is fine for a Docker-deployed service where the Docker tag IS the version. If you later want pyproject.toml to stay in sync, a step could be added to auto-update it (excluded from this plan).
2. **Dockerfile VERSION file** -- The current Dockerfile doesn't consume a VERSION build arg. A build arg could be added to embed the computed version, but since the Docker tag already carries the version this is cosmetic (excluded from this plan).
