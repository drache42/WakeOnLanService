MAJOR (breaking change): HTTP endpoint removed or renamed; required environment variable removed or renamed (MAC_ADDRESS, URL, SECRET_KEY); Flask app factory (create_app) signature changed incompatibly; Dockerfile ENTRYPOINT or EXPOSE changed; commit message contains "BREAKING CHANGE:"

MINOR (new backward-compatible feature): new HTTP endpoint/route added; new Flask blueprint registered; new environment variable with safe default; new HTML template page; new Python module added to src/wakeonlanservice/

PATCH (default): bug fixes; changes only in tests/ docs/ or *.md files; CI/infra/build changes (.github/ docker/); refactors with no behavioral change; dependency version bumps; logging improvements
