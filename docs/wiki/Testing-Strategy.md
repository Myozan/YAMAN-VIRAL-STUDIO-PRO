# Quality Engineering & Testing Strategy

**QA 3.1 baseline: 17 automated tests** across Autopilot, Learning Engine and FastAPI integration coverage.

## Run locally

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

## Implemented coverage

| Area | Coverage | Tests |
|---|---|---:|
| Autopilot | SQLite create/read, timezone validation, due/manual claim, run history, deduplication, deletion | 6 |
| Learning Engine | Engagement/retention, sample threshold, platform isolation | 3 |
| FastAPI | Health, 422 validation, 404 contracts, task cancel/events, restart recovery, publish confirmation, provider rejection, OAuth invalid/replay protection | 9 |
| **Total** | | **18** |

FastAPI tests use TestClient and isolated temporary databases. Ollama is stubbed; tests do not contact live OAuth, paid AI or social publishing APIs.

## API regressions covered in QA 3.1

- Health response contract.
- Pydantic rejects invalid analysis input with HTTP 422.
- Unknown task, job and task event return HTTP 404.
- Task cancellation persists, records an event and remains idempotent.
- In-flight task is marked interrupted after simulated task-store restart.
- Publish endpoint rejects missing explicit confirmation before OAuth token access.
- Unsupported publishing provider and invalid OAuth state are rejected.
- OAuth callback state is consumed once; replay is rejected.

## CI

GitHub Actions installs application dependencies plus `requirements-dev.txt`, runs compile checks and the full pytest suite, then validates frontend assets, manifest and JavaScript syntax.

## Next P0 priorities

- Agent retry API and missing resource handling.
- OAuth state expiry boundary, one-time use and disconnect vault tests.
- Secret vault wrong-key and rotation tests.
- Path traversal, symlink and SSRF regression tests.
- SQLite multi-connection and Autopilot concurrency tests.
- Synthetic FFmpeg render with ffprobe validation.

## Honest coverage boundary

These 17 tests are a growing regression baseline, not comprehensive QA. Real media render, browser automation, concurrency stress, complete vault lifecycle and security scanning are still pending.

Full matrix: [Quality Engineering & Testing Strategy](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/TESTING-STRATEGY.md).
