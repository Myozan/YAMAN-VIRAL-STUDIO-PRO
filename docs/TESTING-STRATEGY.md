# Quality Engineering & Testing Strategy â€” v1.8.0

This document separates executed automated coverage from remaining release assurance. Passing tests are evidence for tested paths only, not a security certification.

## 1. QA 3.5 current baseline

The suite collects **70 test cases**. Latest Windows/Python 3.12 run: **68 passed, 2 skipped**. The two skips are workspace symlink tests; the connected Windows account cannot create symlinks.

| Suite | Coverage | Test cases |
|---|---|---:|
| Autopilot | SQLite initialization, create/read, timezone validation, due/manual claims, run history and deduplication | 6 |
| Learning engine | Engagement/retention, sample threshold, platform isolation | 3 |
| FastAPI integration | Health, request validation, task contracts, cancellation, restart recovery, publishing and OAuth state | 9 |
| Security regression | URL validation, path containment, OAuth vault and SSRF/redirect cases | 32 |
| QA 3.3 reliability | Agent retry eligibility and source validation, concurrent task journaling, app lifespan, synthetic FFmpeg/FFprobe and corrupt media | 9 |
| QA 3.4 durability | Cross-process SQLite write contention, retry reservation idempotency and claim persistence | 3 |
| QA 3.5 security and concurrency | IP-pinned HTTPS transport, OAuth vault key rotation, rollback and persistent key-source selection | 8 |
| **Total** | | **67** |

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



## 3. QA 3.5 security and concurrency changes

- Remote media downloads now resolve each HTTPS hostname, reject the entire answer set if any address is non-public, and pin the connection to a validated IP. The TLS connection retains the original hostname for SNI and certificate hostname verification. Ambient proxy settings are not inherited for this security-sensitive fetch. Every redirect is independently validated and pinned.
- OAuth secret rotation now decrypts and re-encrypts the token, app-credential and visual-provider vaults using a new Fernet key. Existing vaults are backed up before replacement; staged ciphertext is verified; a failed replacement restores every already-replaced file. Environment-managed rotation writes a persistent rotated-key file, selected on subsequent startup, instead of relying on an in-memory environment change.
- Autopilot's existing `BEGIN IMMEDIATE` due-claim transaction is now tested with two independent Python processes racing for the same due schedule. Exactly one process may claim it.

## 4. QA 3.5 executed tests

- A pinned HTTPS connection opens its socket to the validated IP while preserving the DNS hostname used by urllib3 for TLS identity checks.
- OAuth key rotation preserves all three vault payloads, creates timestamped backups, rejects the old key afterward and leaves the source vault untouched for an invalid new key.
- Simulated disk failure during the replacement phase restores the original bytes for all encrypted vaults.
- Local key-file rotation persists the new key; environment-key rotation writes a dedicated key file that is selected by the next process after the environment variable is absent. A missing legacy key fails closed.
- Two independent Autopilot processes racing on one due schedule produce exactly one claim and a healthy SQLite integrity check.

## 5. QA 3.4 durability changes

- Agent retries now use a SQLite `BEGIN IMMEDIATE` transaction and a unique `task_retry_claims.source_task_id` reservation. The database, not a process-local Python lock, is the authority for whether a source task has already been retried.
- A second retry request for the same source task returns HTTP 409 and cannot enqueue a second agent run. The reservation survives application/database reopen.
- Retry eligibility, request payload, source project and clip are checked before the reservation is committed.
- The test suite now starts independent Python processes that contend on one SQLite database and verifies all committed rows plus `PRAGMA integrity_check`.

## 6. QA 3.4 executed tests

- Four independent writer processes each commit 40 rows (160 total) without lost writes or database corruption.
- A retry reservation is created once; a duplicate request is rejected and the background task is scheduled only once.
- Retry reservations persist across database initialization/reopen.

## 7. QA 3.3 reliability changes

- FastAPI startup and shutdown are now managed through an application lifespan context rather than deprecated `on_event` hooks.
- The Autopilot scheduler is started with the application and signalled to stop during shutdown. Its 20-second wait is interruptible and the thread is joined with a bounded timeout.
- Task state snapshots and SQLite event writes are serialized with a process-local reentrant lock to prevent concurrent in-process updates from overwriting each other.
- Agent retry is limited to failed, interrupted or cancelled agent tasks. Running, queued and completed tasks are rejected; retry still requires the source project and clip to be available.
- A media probe helper checks file existence/size, ffprobe validity, finite positive duration and presence of a video stream. Rendered platform clips are probed after FFmpeg exits successfully.

## 8. QA 3.3 executed tests

- Concurrent writes to one task produce a complete event journal and pass SQLite `PRAGMA integrity_check`.
- Agent retry rejects running tasks, missing source projects and missing clips; a valid failed task queues a new retry task.
- FastAPI lifespan starts the scheduler and stops it on application shutdown.
- A synthetic test-pattern video with audio is rendered by the installed FFmpeg binary and validated with FFprobe.
- Audio-only and corrupt media are rejected by the video-output validator.

## 9. QA 3.2 security changes

- YouTube ingestion accepts canonical HTTPS URLs on the supported host allowlist only.
- Runway/Pexels downloads reject non-HTTPS, localhost/internal names, credentials, non-standard ports and non-public DNS answers.
- Redirects are manually followed with destination revalidation and a bounded redirect count.
- Auto-Editor and saved-job restoration enforce workspace path containment, including resolved symlink targets.
- OAuth vault tests verify encrypted-at-rest tokens, round-trip decryption and fail-closed behavior for wrong/malformed keys.

## 10. QA 3.1 API regression coverage retained

- Health contract and Pydantic request validation.
- Unknown task, job and task-event resources return HTTP 404.
- Task cancellation persists state, records events and remains idempotent.
- In-flight tasks are marked interrupted after simulated task-store restart.
- Publishing without explicit confirmation is rejected before OAuth token lookup.
- Unsupported providers and invalid OAuth state are rejected; OAuth state replay is rejected.

## 11. Remaining coverage priorities

**P0**
- Cross-process coordination for task-state snapshots and Autopilot double-claim stress. The retry reservation is now database-backed, but general task-state writes still use a process-local lock.
- Windows symlink tests on a runner with symlink privileges.
- Offline restore drill for encrypted vault backups, including rotated key material.
- Full task-state consistency across multiple application worker processes.

**P1**
- Ollama timeout, connection failure and malformed JSON.
- Agent fallback and deterministic quality outcomes.
- Browser automation and mobile PWA flows.
- Provider quota/error handling and release backup/restore drills.

## 12. CI and release gates

CI must install application and development dependencies, run the full pytest suite, compile Python, validate JavaScript and parse the PWA manifest. A release candidate additionally requires Windows 10/11 smoke checks, rights-cleared media render validation, verified backup/restore and a clean release archive without secrets or private media.

## 13. Current limitations

The current local run is not a security certification. Two symlink tests were skipped because this Windows account cannot create symlinks. Task locking is process-local; cross-process coordination remains future work. Remote media GET transport pins the validated IP and preserves TLS hostname verification. General task-state in-memory snapshots still use a process-local lock; do not run multiple application workers against one workspace. OAuth rotation keeps timestamped pre-rotation copies and a dedicated rotated-key file when the key is environment-managed, so backup retention and offline restore remain operator responsibilities. Keep the rotated key file protected and include it in the matched offline backup set. v1.8.0 remains local-use only and must not be exposed directly to a LAN or the public internet.

## Related documentation

- [Security & Privacy](wiki/Security.md)
- [Engineering Architecture](ENGINEERING-ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS-RUNBOOK.md)
