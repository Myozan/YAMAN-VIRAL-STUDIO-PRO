# Developer Guide

## Development environment

- Windows 10/11
- Python 3.12
- Git
- FFmpeg and FFprobe
- Ollama for local AI development
- Node.js for JavaScript syntax checks

## Setup

    git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
    cd YAMAN-VIRAL-STUDIO-PRO
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Copy-Item .env.example .env

Run locally with:

    .\run_windows.bat

## Project structure

    app/                 FastAPI backend and application services
    web/                 Frontend and PWA assets
    docs/                Product and technical documentation
    docs/wiki/           Wiki-ready Markdown source pages
    tools/               Maintenance and update utilities
    workspace/           Local database, jobs and media (runtime data)
    .github/workflows/   CI workflows

## Code quality checks

    python -m compileall -q app
    node --check web/app.js
    node --check web/sw.js

Run the checks relevant to your changes. For UI changes, verify desktop and narrow mobile layouts. For API/media changes, add a repeatable manual test plan.

## Adding an API endpoint

1. Define a Pydantic request model with strict bounds and patterns.
2. Validate file paths, URLs, platform values and ownership boundaries.
3. Keep blocking media work in background tasks where appropriate.
4. Return stable JSON and actionable errors.
5. Add endpoint details to API-Reference.md.
6. Verify the live OpenAPI document and test both success and failure paths.

## Adding a provider integration

- Keep provider-specific behavior behind a small adapter.
- Use official APIs and documented OAuth scopes.
- Encrypt credentials at rest and never log secrets.
- Handle quotas, retries, revocation and provider-specific restrictions.
- Require explicit user confirmation for publication.
- Document account eligibility and app-review limitations.

## Pull request checklist

Follow the repository [CONTRIBUTING.md](../../CONTRIBUTING.md). Never commit workspace data, model files, OAuth vaults, private media, tokens or encryption keys.
