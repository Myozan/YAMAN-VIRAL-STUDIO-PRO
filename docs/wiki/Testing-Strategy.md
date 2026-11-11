# Quality Engineering & Testing Strategy

**QA 3.3: 59 collected test cases — latest local run 57 passed, 2 skipped.** The skips are symlink tests; this Windows account cannot create symlinks.

## Run locally

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
python -m compileall -q app tests
node --check web/app.js
node --check web/sw.js
python -c "import json; json.load(open('web/manifest.webmanifest', encoding='utf-8'))"
```

## Implemented coverage

| Area | Coverage | Test cases |
|---|---|---:|
| Autopilot | SQLite create/read, timezone validation, due/manual claim, run history and deduplication | 6 |
| Learning Engine | Engagement/retention, sample threshold, platform isolation | 3 |
| FastAPI | Health, validation, task contracts, cancellation, restart recovery, publish confirmation and OAuth state | 9 |
| Security regression | URL allowlists, workspace containment, OAuth vault, SSRF/DNS/redirect checks | 32 |
| QA 3.3 reliability | Retry validation, concurrent task journaling, lifespan lifecycle, FFmpeg/FFprobe synthetic render and corrupt media | 9 |
| **Total** | | **59** |

Latest local run: **57 passed, 2 skipped**. Tests do not contact live OAuth, paid AI or social publishing APIs.

## QA 3.3 changes

- FastAPI startup/shutdown now uses the lifespan context; deprecated `on_event` hooks were removed.
- Autopilot scheduler lifecycle is owned by the application. Shutdown signals the scheduler and performs a bounded thread join.
- Task state updates and SQLite event journaling are protected by a process-local reentrant lock.
- Agent retry accepts only failed, interrupted or cancelled tasks and requires the original job and clip to exist.
- FFprobe-based output validation checks file size, valid metadata, positive finite duration and a video stream. Rendered platform clips are validated after FFmpeg.

## QA 3.3 tests

- Concurrent updates to a task preserve all 64 journal events and SQLite integrity.
- Agent retry rejects running tasks, missing source projects and missing clips; valid failed tasks enqueue a new retry.
- FastAPI lifespan starts and stops the scheduler.
- FFmpeg renders a synthetic video with audio; FFprobe verifies its streams and duration.
- Audio-only and corrupt files are rejected as invalid video output.

## QA 3.2 security changes

- YouTube source URLs require canonical HTTPS and supported hostnames.
- Runway/Pexels downloads reject localhost, private DNS answers, credentials and unsafe schemes/ports.
- Redirects are revalidated with a bounded redirect count.
- Workspace traversal and resolved symlink escapes are rejected.
- OAuth vault ciphertext, round-trip decryption and wrong-key failure are tested.

## QA 3.1 API regressions retained

- Health contract, validation and 404 contracts.
- Task cancellation persistence, event history and idempotency.
- Restart recovery of in-flight tasks.
- Explicit publishing confirmation before OAuth token lookup.
- Invalid OAuth state and callback replay rejection.

## Next P0 priorities

- Cross-process task locks and retry idempotency.
- Multi-process SQLite contention and Autopilot double-claim stress.
- Run symlink tests on Windows CI with symlink privileges.
- DNS rebinding-resistant transport with IP pinning.
- OAuth key rotation and vault backup/restore lifecycle.

## Honest coverage boundary

The current run is not a security certification. Symlink tests are skipped because the current Windows account cannot create symlinks. Task locking is process-local, not cross-process. DNS rebinding remains a hardening item because the HTTP client resolves the hostname again after validation. v1.8.0 remains local-use only and must not be exposed directly to LAN or the public internet.

Full matrix: [Quality Engineering & Testing Strategy](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/TESTING-STRATEGY.md).
