# Quality Engineering & Testing Strategy â€” v1.8.0

This document separates executed automated coverage from remaining release assurance. Passing tests are evidence for tested paths only, not a security certification.

## 1. QA 3.7 historical baseline

The suite collects **100 test cases**. Latest full Windows/Python 3.12 run: **98 passed, 2 skipped**. The two skips are workspace symlink tests; the connected Windows account cannot create symlinks.

| Suite | Coverage | Test cases |
|---|---|---:|
| Autopilot | SQLite initialization, create/read, timezone validation, due/manual claims, run history and deduplication | 6 |
| Learning engine | Engagement/retention, sample threshold, platform isolation | 3 |
| FastAPI integration | Health, request validation, task contracts, cancellation, worker lease recovery, publishing and OAuth state | 10 |
| Security regression | URL validation, path containment, OAuth vault and SSRF/redirect cases | 32 |
| QA 3.3 reliability | Agent retry eligibility and source validation, concurrent task journaling, app lifespan, synthetic FFmpeg/FFprobe and corrupt media | 9 |
| QA 3.4 durability | Cross-process SQLite write contention, retry reservation idempotency and claim persistence | 3 |
| QA 3.5 security and concurrency | IP-pinned HTTPS transport (including Pexels API search), OAuth vault key rotation, rollback and persistent key-source selection | 9 |
| QA 3.6 shared transport and multi-worker consistency | Pinned API transport, process-safe task updates, worker leases, job rehydration, atomic retry scheduling and provider 308 handling | 12 |
| QA 3.7 durable queue engine | Atomic claims, multi-process single-owner race, killed-worker lease recovery/backoff, max attempts, cancellation, idempotency and delayed jobs | 7 |
| QA 3.7 worker integration | API-to-worker dispatch, task rehydration, interrupted task reopening, cancellation revocation, orphan recovery exclusion, path validation, replacement-process handoff, stale-owner write rejection and public requeue status | 9 |
| **Total** | | **100** |

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



## 3. QA 3.7 durable queue and worker integration

- Added `app/task_queue.py` with atomic enqueue/claim, priority, delayed availability, owner-bound leases, heartbeat renewal, bounded exponential recovery, maximum attempts, idempotency keys and cancellation.
- FastAPI lifespan now starts a durable queue worker in each process. The worker claims one core media task at a time and renews its 90-second lease every 15 seconds while executing.
- Remote/local analysis, render, summary and agent-team requests now persist JSON task payloads and queue rows in the same SQLite transaction as the public task record and initial event. Agent retry claims, task records, events and queue payloads are also committed together.
- Workers reconstruct Pydantic request models and rehydrate saved project data from validated workspace `job.json` snapshots. They no longer depend on the accepting process's in-memory job dictionary.
- Expired worker leases are requeued with bounded exponential delay and three attempts by default. Exhausted tasks are synchronized to failed in the public task/event history. Cancelled tasks lose their lease and cannot be completed by the former owner.
- Queue recovery is deliberately at-least-once: a crash after writing an output but before acknowledging completion may cause a repeat attempt. At the QA 3.7 baseline, Autopilot still used its old scheduling path; QA 3.8 later moves manual and scheduled Autopilot runs into the durable queue.
- Same-host SQLite WAL only; multi-host queue execution remains out of scope and requires PostgreSQL plus a durable distributed broker.

## 4. QA 3.7 executed tests

- Queue engine tests cover idempotent enqueue, six-process single-owner claim race, expired lease recovery/backoff, maximum attempt exhaustion, owner-bound heartbeat/completion, delayed jobs and cancellation revocation.
- Worker integration tests verify API enqueue reaches the durable worker, summary/render/agent payloads are reconstructed, interrupted task state can be reopened by a replacement claim, cancelled claims are not dispatched, startup orphan recovery does not interrupt queued queue-owned work, and analysis payload paths cannot escape the workspace.
- A subprocess is forcibly terminated after claiming a task; a separate process then starts the actual FastAPI queue worker loop, reclaims and completes the same task. A previous owner cannot overwrite the replacement worker's progress, and lease recovery is visible as queued in task history. Agent retry regression tests assert the durable queue payload rather than process-local BackgroundTasks scheduling.

## 5. QA 3.6 shared transport and multi-worker changes

- Added `app/secure_http.py` as the common requests-based public HTTPS transport. It rejects credentials, non-standard ports, local names and non-public DNS answers; pins the socket to a validated public IP; preserves the DNS hostname for TLS SNI/certificate checks; and disables ambient proxy inheritance.
- Third-party REST calls for OAuth, YouTube/TikTok/Instagram publishing and uploads, Runway, Pexels, RSS research and GitHub updater metadata/archive downloads now use the shared transport. Redirects are off by default. Explicit RSS/GitHub redirects are validated and pinned per hop; cross-origin redirects strip Authorization/Cookie headers. Provider status 308 is returned unchanged when redirects are disabled (important for YouTube resumable uploads).
- Local Ollama calls remain direct local-service HTTP by design. `yt-dlp` and Edge TTS use their own protocol/client transports and are not claimed to be covered by the requests-based adapter.
- Task state is now read from SQLite as the authority. `set_task` uses `BEGIN IMMEDIATE` and merges against the latest database payload, so concurrent workers cannot overwrite one another's state fields. Terminal states cannot be replaced by late progress updates; cancellation checks read SQLite.
- Added a worker registry with a 10-second heartbeat and 45-second stale lease. Starting a worker no longer marks every other worker's running tasks interrupted. Stale tasks are recovered by the heartbeat reaper; graceful worker shutdown interrupts only tasks owned by that worker.
- Saved analysis jobs are rehydrated from validated `job.json` files on demand, allowing a different worker to serve render/agent/publish requests without relying on another process's Python dictionary.
- Retry claim reservation and the queued retry task/event are inserted in the same SQLite transaction, eliminating the previous claim-without-task crash window. Autopilot due claims remain protected by their existing database transaction.


## 6. QA 3.6 executed tests

- Public and mixed public/private DNS answer sets are rejected before a socket is opened.
- Cross-origin redirects drop Authorization and Cookie; redirects to private destinations are blocked before the next request; non-GET redirects are not followed by default. Provider HTTP 308 upload status is preserved when redirects are disabled.
- Four independent processes write 80 distinct state fields to one task. All fields and all 80 journal events survive, and SQLite integrity remains `ok`.
- Task reads ignore stale process-local cache; a late progress update cannot overwrite a terminal cancellation.
- A worker with a fresh heartbeat is not interrupted by another worker's startup; an expired lease is recovered as interrupted.
- A worker without a populated in-memory job cache can safely load a saved project; path traversal job IDs are rejected.
- Retry claim, task row, event and durable queue payload are committed together; duplicate retry requests are rejected.

## 7. QA 3.5 security and concurrency changes

- All remote media GETs, including the Pexels search request, now resolve each HTTPS hostname, reject the entire answer set if any address is non-public, and pin the connection to a validated IP. The TLS connection retains the original hostname for SNI and certificate hostname verification. Ambient proxy settings are not inherited for this security-sensitive fetch. Every redirect is independently validated and pinned. Pexels search and media downloads use this same path.
- OAuth secret rotation now decrypts and re-encrypts the token, app-credential and visual-provider vaults using a new Fernet key. Existing vaults are backed up before replacement; staged ciphertext is verified; a failed replacement restores every already-replaced file. Environment-managed rotation writes a persistent rotated-key file, selected on subsequent startup, instead of relying on an in-memory environment change.
- Autopilot's existing `BEGIN IMMEDIATE` due-claim transaction is now tested with two independent Python processes racing for the same due schedule. Exactly one process may claim it.

## 8. QA 3.5 executed tests

- A pinned HTTPS connection opens its socket to the validated IP while preserving the DNS hostname used by urllib3 for TLS identity checks.
- OAuth key rotation preserves all three vault payloads, creates timestamped backups, rejects the old key afterward and leaves the source vault untouched for an invalid new key.
- Simulated disk failure during the replacement phase restores the original bytes for all encrypted vaults.
- Local key-file rotation persists the new key; environment-key rotation writes a dedicated key file that is selected by the next process after the environment variable is absent. A missing legacy key fails closed.
- Two independent Autopilot processes racing on one due schedule produce exactly one claim and a healthy SQLite integrity check.

## 9. QA 3.4 durability changes

- Agent retries now use a SQLite `BEGIN IMMEDIATE` transaction and a unique `task_retry_claims.source_task_id` reservation. The database, not a process-local Python lock, is the authority for whether a source task has already been retried.
- A second retry request for the same source task returns HTTP 409 and cannot enqueue a second agent run. The reservation survives application/database reopen.
- Retry eligibility, request payload, source project and clip are checked before the reservation is committed.
- The test suite now starts independent Python processes that contend on one SQLite database and verifies all committed rows plus `PRAGMA integrity_check`.

## 10. QA 3.4 executed tests

- Four independent writer processes each commit 40 rows (160 total) without lost writes or database corruption.
- A retry reservation is created once; a duplicate request is rejected and the background task is scheduled only once.
- Retry reservations persist across database initialization/reopen.

## 11. QA 3.3 reliability changes

- FastAPI startup and shutdown are now managed through an application lifespan context rather than deprecated `on_event` hooks.
- The Autopilot scheduler is started with the application and signalled to stop during shutdown. Its 20-second wait is interruptible and the thread is joined with a bounded timeout.
- Task state snapshots and SQLite event writes are serialized with a process-local reentrant lock to prevent concurrent in-process updates from overwriting each other.
- Agent retry is limited to failed, interrupted or cancelled agent tasks. Running, queued and completed tasks are rejected; retry still requires the source project and clip to be available.
- A media probe helper checks file existence/size, ffprobe validity, finite positive duration and presence of a video stream. Rendered platform clips are probed after FFmpeg exits successfully.

## 12. QA 3.3 executed tests

- Concurrent writes to one task produce a complete event journal and pass SQLite `PRAGMA integrity_check`.
- Agent retry rejects running tasks, missing source projects and missing clips; a valid failed task queues a new retry task.
- FastAPI lifespan starts the scheduler and stops it on application shutdown.
- A synthetic test-pattern video with audio is rendered by the installed FFmpeg binary and validated with FFprobe.
- Audio-only and corrupt media are rejected by the video-output validator.

## 13. QA 3.2 security changes

- YouTube ingestion accepts canonical HTTPS URLs on the supported host allowlist only.
- Runway/Pexels downloads reject non-HTTPS, localhost/internal names, credentials, non-standard ports and non-public DNS answers.
- Redirects are manually followed with destination revalidation and a bounded redirect count.
- Auto-Editor and saved-job restoration enforce workspace path containment, including resolved symlink targets.
- OAuth vault tests verify encrypted-at-rest tokens, round-trip decryption and fail-closed behavior for wrong/malformed keys.

## 14. QA 3.1 API regression coverage retained

- Health contract and Pydantic request validation.
- Unknown task, job and task-event resources return HTTP 404.
- Task cancellation persists state, records events and remains idempotent.
- In-flight tasks are marked interrupted after their owning worker lease expires.
- Publishing without explicit confirmation is rejected before OAuth token lookup.
- Unsupported providers and invalid OAuth state are rejected; OAuth state replay is rejected.

## 15. Remaining coverage priorities

**P0**
- Full production-length Whisper transcription and FFmpeg render interrupted mid-job, followed by task recovery and output integrity validation.
- Physical NAS SMB backup/restore rehearsal with a real share, network interruption and restore into a separate workspace.
- Windows symlink tests on a runner with symlink privileges.
- Offline restore drill for encrypted vault backups, including rotated key material.
- Multi-host deployment with a shared PostgreSQL database and durable broker; the current SQLite WAL design is intended for multiple workers on one host and a local filesystem.

**P1**
- Ollama timeout, connection failure and malformed JSON.
- Agent fallback and deterministic quality outcomes.
- Browser automation and mobile PWA flows.
- Provider quota/error handling and release backup/restore drills.

## 16. CI and release gates

CI must install application and development dependencies, run the full pytest suite, compile Python, validate JavaScript and parse the PWA manifest. A release candidate additionally requires Windows 10/11 smoke checks, rights-cleared media render validation, verified backup/restore and a clean release archive without secrets or private media.

## 17. Current limitations

The current local run is not a security certification. Two symlink tests were skipped because this Windows account cannot create symlinks. Requests-based third-party HTTPS APIs now use the pinned transport; local Ollama remains a separate local-service path, while yt-dlp and Edge TTS use their own clients. Task state, cancellation and job metadata are consistent across workers on the same host, and core media tasks now use the SQLite durable queue with at-least-once recovery after lease expiry. Autopilot and other non-core flows still use their existing process-local scheduling path. SQLite WAL must stay on a local filesystem; use PostgreSQL plus a durable broker for multi-host execution. OAuth rotation keeps timestamped pre-rotation copies and a dedicated rotated-key file when the key is environment-managed, so backup retention and offline restore remain operator responsibilities. Keep the rotated key file protected and include it in the matched offline backup set. v1.8.0 remains local-use only and must not be exposed directly to a LAN or the public internet.

## Related documentation

- [Security & Privacy](wiki/Security.md)
- [Engineering Architecture](ENGINEERING-ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS-RUNBOOK.md)


## 11. QA 3.8 queue operations and Autopilot durability

- Full Windows/Python 3.12 regression run: **126 passed, 2 skipped (128 total)**. The two skips are Windows symlink privilege cases.
- Added a real two-Uvicorn-process failover test. The first process is terminated while holding a queue task; the second process reclaims and completes it after a shortened test lease. Production default lease remains 90 seconds.
- Global active-task concurrency is enforced transactionally by SQLite. Default is one active task across all same-host Uvicorn workers; configure with `YAMAN_QUEUE_MAX_CONCURRENT`.
- Manual and scheduled Autopilot runs now share the durable queue. Due schedule advancement, public task/event journal insertion and queue insertion are atomic. The scheduler thread only enqueues; workers perform content generation.
- Autopilot duplicate active runs are rejected, legacy process-local running states are reconciled during upgrade, and run history is idempotent by durable task ID.
- Stale worker progress writes are rejected after lease expiry or ownership transfer. Active leases continue to renew during graceful shutdown until the current handler exits.
- Added `GET /api/queue/health` and `GET /api/queue/tasks`, plus a responsive Autopilot queue monitor. The monitor exposes worker heartbeats, queue counts, global concurrency and recent task metadata; agent tasks retain the existing safe retry action.
- Added a synthetic FFmpeg fixture test that renders twice to the same output path and validates the resulting MP4 with FFprobe.
- Added consistent SQLite online backup staging and restore verification. The test uses a local disposable destination; physical NAS share rehearsal remains an environment-specific release check.
- Static validation passed: Python compileall, Node syntax for app/service worker, PWA manifest JSON and Git whitespace checks.


## 12. QA 3.9 process recovery and backup integrity

- Full Windows/Python 3.12 suite: **130 passed, 2 skipped (132 total)**. The two skips are existing Windows symlink privilege cases.
- Windows Job Object process ownership ensures FFmpeg exits when its worker is forcibly terminated. The lifecycle integration test verifies the child process is gone.
- A separate two-Uvicorn-process soak test uses production defaults: 90-second task lease, 15-second lease heartbeat, 10-second worker heartbeat and 45-second stale-worker threshold.
- Workspace backup manifest v2 records SHA-256 and byte size for all files and SQLite snapshots. Restore preflights every source before modifying the target and remains compatible with v1 snapshots.
- Tampered backup data is rejected before workspace modification.
- Physical NAS rehearsal and a representative long Whisper-plus-FFmpeg media interruption test remain production sign-off items.
