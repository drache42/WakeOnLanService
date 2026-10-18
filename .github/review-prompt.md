Review this pull request for the WakeOnLanService application, a Python/Flask web service that sends Wake-on-LAN packets and ships as a multi-architecture (amd64 and arm64) Docker image run on a Raspberry Pi.

Focus on:
- Correctness and potential bugs
- Security issues (OWASP Top 10, injection, auth, SECRET_KEY and other secrets in code, unvalidated MAC address or URL input)
- Python and Flask idioms and best practices (app factory, blueprints, error handling, logging)
- Dockerfile and container changes (ENTRYPOINT, EXPOSE, base image, arm64 compatibility, non-root user)
- Test coverage for new logic (pytest unit tests and Docker-based integration tests)
- Breaking changes to HTTP endpoints, environment variables (MAC_ADDRESS, URL, SECRET_KEY) or the create_app signature
