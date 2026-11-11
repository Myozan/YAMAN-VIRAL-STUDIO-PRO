# Quality Engineering & Testing Strategy — v1.8.0

This document distinguishes automated coverage that is implemented and executed from future release-assurance work. Passing tests are evidence for tested paths only, not a security certification.

## 1. QA 3.2 current baseline

The suite collects **50 test cases**: **48 passed and 2 skipped** in the current Windows/Python 3.12 run. The two skips are symlink tests because the connected Windows account does not have permission to create symlinks.

| Suite | Coverage | Test cases |
|---|---|---:|
| Autopilot | SQLite initialization, create/read, invalid timezone, due/manual claims, run history, processed-file deduplication, deletion | 6 |
| Learning engine | Engagement/retention calculations, minimum sample threshold, platform isolation | 3 |
| FastAPI integration | Health contract, request validation, task/job contracts, cancellation, restart recovery, publish confirmation, OAuth state | 9 |
| Security regression | YouTube URL validation, workspace traversal/symlink containment, OAuth vault encryption and wrong-key behavior, SSRF/DNS/redirect validation | 32 |
| **Total collected** | | **50** |

Latest local run: `48 passed, 2 skipped, 4 warnings`. Four warnings are existing FastAPI `on_event` deprecations. No live OAuth, paid provider or external publishing call is made by these tests.

## 2. Run locally

Python 3.12 is the supported CI runtime.

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
python -m compileall -q app tests
node --check web/app.js
node --check web/sw.js
python -c "import json; json.load(open('web/manifest.webmanifest', encoding='utf-8'))"
```

`requirements-dev.txt` contains test-only dependencies. Application runtime dependencies remain in `requirements.txt`.

## 3. QA 3.2 security changes

- YouTube ingestion accepts only canonical HTTPS URLs on the supported YouTube host allowlist. Userinfo, non-standard ports, HTTP, localhost/IP literals and lookalike hosts are rejected.
- Runway and Pexels media-download URLs are checked for HTTPS, standard port, absent URL credentials, localhost/internal suffixes, and DNS answers that are not globally routable.
- Remote media downloads disable automatic redirects and validate every redirect destination before following it; redirect count is bounded.
- Auto-Editor paths are resolved and required to remain inside the workspace, including symlink resolution.
- Saved-job recovery rejects job folders that resolve outside the workspace.
- OAuth vault tests verify encrypted-at-rest token bytes, successful round-trip, and fail-closed behavior with a wrong or malformed Fernet key.

## 4. QA 3.1 API regression coverage retained

- `GET /api/health` returns the expected health contract.
- Invalid analysis request values are rejected with HTTP 422.
- Unknown task, job and task-event resources return HTTP 404.
- Task cancellation persists state and is idempotent.
- Task event history records cancellation.
- In-flight tasks are marked interrupted when the task store is reinitialized after a simulated restart.
- Publishing without explicit confirmation is rejected before OAuth token lookup.
- OAuth state is consumed once; a replayed callback is rejected.
- Unsupported publishing providers and invalid OAuth callback state are rejected.

## 5. Defect found and fixed during QA 3.1

The OAuth callback regression test exposed a first-run failure: the `oauth_states` table was created only when OAuth authorization was initiated. A callback with an unknown state before any OAuth start therefore raised SQLite OperationalError instead of returning the intended HTTP 400. The table is now initialized with the task store, so invalid callbacks are rejected cleanly. A replay test also verifies that a state is consumed once.

## 6. Remaining coverage priorities

**P0**
- Agent retry behavior, task concurrency and duplicate execution stress.
- SQLite multi-connection concurrency and integrity checks.
- Synthetic FFmpeg render with ffprobe output validation.
- Windows symlink tests on a CI runner configured with symlink privileges.
- DNS rebinding-resistant transport that pins the validated destination IP.

**P1**
- Ollama timeout, connection failure and malformed JSON.
- Agent fallback status and deterministic QA outcomes.
- Mobile browser navigation and PWA flows.
- External provider quota and error handling.
- Full OAuth key rotation and backup/restore lifecycle.

## 7. CI and test design rules

- CI installs application and test dependencies, then runs the same pytest suite.
- No real paid API, live OAuth account or production credential is used in tests.
- Mock external providers and use synthetic or redistributable media.
- Use temporary directories and isolated databases.
- Keep tests deterministic and repeatable.
- Do not silently skip required release checks.

## 8. Release gates

A release candidate requires passing CI and P0 tests, Windows 10/11 + Python 3.12 smoke checks, a rights-cleared media render validated by ffprobe, a verified backup/restore drill, and a clean release archive with no secrets or private media.

## 9. Current limitations

The current local run is not a security certification. Symlink tests were skipped because symlink creation is not permitted in the connected Windows environment. DNS is checked before each request and redirect, but the HTTP client performs its own DNS resolution; DNS rebinding is therefore a remaining hardening item. Real FFmpeg output, browser automation, concurrency stress and full OAuth key rotation are not yet claimed as passing. The application remains local-use only and must not be exposed directly to a LAN or the public internet.

## Related documentation

- [Security & Privacy](wiki/Security.md)
- [Engineering Architecture](ENGINEERING-ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS-RUNBOOK.md)
