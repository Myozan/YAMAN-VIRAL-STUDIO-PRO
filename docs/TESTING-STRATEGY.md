# Quality Engineering & Testing Strategy — v1.8.0

This document separates executed automated coverage from remaining release assurance. Passing tests are evidence for tested paths only, not a security certification.

## 1. QA 3.3 current baseline

The suite collects **59 test cases**. Latest Windows/Python 3.12 run: **57 passed, 2 skipped**. The two skips are workspace symlink tests; the connected Windows account cannot create symlinks.

| Suite | Coverage | Test cases |
|---|---|---:|
| Autopilot | SQLite initialization, create/read, timezone validation, due/manual claims, run history and deduplication | 6 |
| Learning engine | Engagement/retention, sample threshold, platform isolation | 3 |
| FastAPI integration | Health, request validation, task contracts, cancellation, restart recovery, publishing and OAuth state | 9 |
| Security regression | URL validation, path containment, OAuth vault and SSRF/redirect cases | 32 |
| QA 3.3 reliability | Agent retry eligibility and source validation, concurrent task journaling, app lifespan, synthetic FFmpeg/FFprobe and corrupt media | 9 |
| **Total** | | **59** |

No live OAuth, paid provider or external publishing call is made by the tests.

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

## 3. QA 3.3 reliability changes

- FastAPI startup and shutdown are now managed through an application lifespan context rather than deprecated `on_event` hooks.
- The Autopilot scheduler is started with the application and signalled to stop during shutdown. Its 20-second wait is interruptible and the thread is joined with a bounded timeout.
- Task state snapshots and SQLite event writes are serialized with a process-local reentrant lock to prevent concurrent in-process updates from overwriting each other.
- Agent retry is limited to failed, interrupted or cancelled agent tasks. Running, queued and completed tasks are rejected; retry still requires the source project and clip to be available.
- A media probe helper checks file existence/size, ffprobe validity, finite positive duration and presence of a video stream. Rendered platform clips are probed after FFmpeg exits successfully.

## 4. QA 3.3 executed tests

- Concurrent writes to one task produce a complete event journal and pass SQLite `PRAGMA integrity_check`.
- Agent retry rejects running tasks, missing source projects and missing clips; a valid failed task queues a new retry task.
- FastAPI lifespan starts the scheduler and stops it on application shutdown.
- A synthetic test-pattern video with audio is rendered by the installed FFmpeg binary and validated with FFprobe.
- Audio-only and corrupt media are rejected by the video-output validator.

## 5. QA 3.2 security changes

- YouTube ingestion accepts canonical HTTPS URLs on the supported host allowlist only.
- Runway/Pexels downloads reject non-HTTPS, localhost/internal names, credentials, non-standard ports and non-public DNS answers.
- Redirects are manually followed with destination revalidation and a bounded redirect count.
- Auto-Editor and saved-job restoration enforce workspace path containment, including resolved symlink targets.
- OAuth vault tests verify encrypted-at-rest tokens, round-trip decryption and fail-closed behavior for wrong/malformed keys.

## 6. QA 3.1 API regression coverage retained

- Health contract and Pydantic request validation.
- Unknown task, job and task-event resources return HTTP 404.
- Task cancellation persists state, records events and remains idempotent.
- In-flight tasks are marked interrupted after simulated task-store restart.
- Publishing without explicit confirmation is rejected before OAuth token lookup.
- Unsupported providers and invalid OAuth state are rejected; OAuth state replay is rejected.

## 7. Remaining coverage priorities

**P0**
- Cross-process task locking and duplicate retry idempotency.
- Multi-process SQLite contention and Autopilot double-claim stress.
- Windows symlink tests on a runner with symlink privileges.
- DNS rebinding-resistant transport that pins the validated destination IP.
- Full OAuth key rotation and vault backup/restore lifecycle.

**P1**
- Ollama timeout, connection failure and malformed JSON.
- Agent fallback and deterministic quality outcomes.
- Browser automation and mobile PWA flows.
- Provider quota/error handling and release backup/restore drills.

## 8. CI and release gates

CI must install application and development dependencies, run the full pytest suite, compile Python, validate JavaScript and parse the PWA manifest. A release candidate additionally requires Windows 10/11 smoke checks, rights-cleared media render validation, verified backup/restore and a clean release archive without secrets or private media.

## 9. Current limitations

The current local run is not a security certification. Two symlink tests were skipped because this Windows account cannot create symlinks. Task locking is process-local; cross-process coordination remains future work. DNS checks are performed before requests and redirects, but the HTTP client resolves the hostname again; DNS rebinding remains a hardening item. v1.8.0 remains local-use only and must not be exposed directly to a LAN or the public internet.

## Related documentation

- [Security & Privacy](wiki/Security.md)
- [Engineering Architecture](ENGINEERING-ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS-RUNBOOK.md)
