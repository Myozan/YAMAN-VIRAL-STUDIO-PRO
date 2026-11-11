# Quality Engineering & Testing Strategy

**QA 3.2: 50 collected test cases — latest local run 48 passed, 2 skipped.** The two skips are Windows symlink tests; the connected account cannot create symlinks.

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
| Autopilot | SQLite create/read, timezone validation, due/manual claim, run history, deduplication, deletion | 6 |
| Learning Engine | Engagement/retention, sample threshold, platform isolation | 3 |
| FastAPI | Health, validation, 404 contracts, task cancel/events, restart recovery, publish confirmation, provider rejection, OAuth state | 9 |
| Security regression | URL allowlists, path traversal/symlink containment, OAuth vault encryption, SSRF/DNS/redirect checks | 32 |
| **Total** | | **50** |

FastAPI tests use TestClient and isolated temporary databases. Tests do not contact live OAuth, paid AI or social publishing APIs. Latest run: **48 passed, 2 skipped, 4 FastAPI deprecation warnings**.

## QA 3.2 security changes

- YouTube source URLs require canonical HTTPS, supported hostnames, no userinfo and standard port only.
- Runway/Pexels media download URLs reject localhost, private/non-global DNS answers, non-HTTPS schemes and credential-bearing URLs.
- Redirects are followed manually with destination revalidation and a bounded redirect count.
- Auto-Editor rejects parent traversal, absolute paths outside the workspace and symlink escapes.
- Saved-job restoration ignores workspace folder symlinks that resolve outside the workspace.
- OAuth vault tests verify ciphertext-at-rest, round-trip decryption and fail-closed behavior for wrong/malformed keys.

## QA 3.1 API regressions retained

- Health response contract and Pydantic validation.
- Unknown task, job and task event return HTTP 404.
- Task cancellation persists, records an event and remains idempotent.
- In-flight task is marked interrupted after simulated task-store restart.
- Publish endpoint rejects missing explicit confirmation before OAuth token access.
- Unsupported publishing provider and invalid OAuth state are rejected.
- OAuth callback state is consumed once; replay is rejected.

## CI

GitHub Actions installs application dependencies plus `requirements-dev.txt`, runs compile checks and the full pytest suite, then validates frontend assets, manifest and JavaScript syntax.

## Next P0 priorities

- Agent retry and duplicate task execution/concurrency tests.
- SQLite multi-connection concurrency and integrity tests.
- Synthetic FFmpeg render with ffprobe validation.
- Execute symlink tests on a Windows CI runner with symlink privileges.
- DNS rebinding-resistant transport with validated destination IP pinning.
- Full OAuth key rotation and vault backup/restore lifecycle.

## Honest coverage boundary

The current run is not a security certification. Symlink tests are skipped on this Windows device because symlink creation is not permitted. DNS validation is performed before requests and redirects, but the HTTP client resolves the hostname again; DNS rebinding remains a hardening item. Real FFmpeg output, browser automation and concurrency stress are not yet claimed as passing. v1.8.0 remains local-use only and must not be exposed directly to LAN or the public internet.

Full matrix: [Quality Engineering & Testing Strategy](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/TESTING-STRATEGY.md).
