# QA 3.8 — Queue Operations, Autopilot Durability and Recovery

## Scope

QA 3.8 completes the next reliability layer on top of the QA 3.7 durable SQLite queue. Product version remains v1.8.0.

## Queue operations API

- `GET /api/queue/health` reports queued/running/completed/failed/cancelled counts, worker PID/host/heartbeat state and the configured global concurrency limit.
- `GET /api/queue/tasks?limit=50&status=queued` lists recent task metadata. Limit is 1–100; status filters are queued, running, completed, failed or cancelled.
- Task listing never returns the serialized task payload. The health API also excludes payloads and media paths.
- A queue without a live worker is unhealthy. Stale worker registrations are pruned by active workers after the configured heartbeat threshold.
- Database read errors return HTTP 503; invalid filters/limits return HTTP 422.
- The Autopilot page contains a responsive queue monitor for worker health, queue counts, global concurrency and recent task metadata. Failed/cancelled agent tasks expose the existing safe retry flow.

These endpoints are operational diagnostics, not an authentication boundary. Keep the application on loopback or behind a trusted private access layer; do not expose it directly to a LAN or the public internet until authentication and authorization are implemented.

## Worker concurrency and leases

- Default lease: 90 seconds (`YAMAN_QUEUE_LEASE_SECONDS`).
- Default queue lease heartbeat: 15 seconds (`YAMAN_QUEUE_HEARTBEAT_SECONDS`).
- Default process heartbeat: 10 seconds (`YAMAN_WORKER_HEARTBEAT_SECONDS`).
- Default worker stale threshold: 45 seconds (`YAMAN_WORKER_STALE_SECONDS`).
- Default global active-task limit: 1 (`YAMAN_QUEUE_MAX_CONCURRENT`). Lower numeric priority values run first; Autopilot tasks use priority 40 and ordinary tasks default to 100.
- The global concurrency limit is enforced inside the same SQLite write transaction as task claiming. Multiple Uvicorn processes therefore cannot exceed the configured active-task cap.
- Each Uvicorn process runs one queue polling thread. With the default global cap, two or more Uvicorn processes provide worker failover without launching multiple heavy Whisper/FFmpeg jobs simultaneously.
- Test-only timing overrides are environment variables; production defaults remain 90-second leases.

## Autopilot durability

- Manual `POST /api/autopilot/{id}/run` requests are atomically inserted into the durable queue and the public task/event journal.
- The schedule poller only claims due schedules and enqueues them; it no longer executes content generation inside its process-local thread.
- Due-schedule advancement, Autopilot state transition and queue insertion share one SQLite transaction. Multiple Uvicorn schedulers cannot enqueue the same due occurrence.
- Manual and scheduled triggers share the same active-run guard.
- Autopilot task payloads retain a schedule snapshot and stable task ID. Replayed completion updates the existing run history instead of inserting duplicate history rows.
- Worker lease loss is checked at pipeline checkpoints. A stale worker cannot overwrite task progress or mark the Autopilot run failed after a replacement worker has taken ownership.
- Worker heartbeats re-register a worker row if it was pruned during a long process pause; stale worker rows are cleaned up without permanently losing a resumed worker.
- Autopilot outputs remain in review; publishing still requires user approval.

## Storage and NAS recovery

- SQLite WAL is supported only on a local filesystem shared by processes on the same host.
- Never place the live WAL database on a NAS/network share.
- `tools/backup_workspace.py` creates each SQLite online snapshot in local temporary storage, verifies it, then copies the consistent database snapshot and workspace assets to the destination.
- `tools/restore_workspace.py` validates manifest paths and SQLite integrity and requires `--confirm-restore`. Stop all YAMAN processes before restoring.
- Do not copy a live database together with WAL/SHM files as a substitute for SQLite's online backup API.
- NAS hardware/share throughput and an actual network-share restore rehearsal must be verified on the target NAS before production backup sign-off.
- Multi-host workers remain out of scope; this architecture is same-host SQLite only.

## Validation performed

- Final full Windows/Python 3.12 suite: **126 passed, 2 skipped (128 total)**. The two skips are the existing Windows symlink privilege tests.
- Python compileall, JavaScript syntax checks, PWA manifest JSON parsing and `git diff --check` all passed.
- Real Windows integration test starts two independent Uvicorn processes against one disposable SQLite database.
- The first process claims a task and is forcibly terminated while executing.
- The second process waits for lease expiry, reclaims the same task, completes it and updates the public task/event journal.
- The test uses a shortened 10-second lease and accelerated heartbeats to keep CI/runtime practical; production lease default remains 90 seconds.
- The test verifies stale worker registry cleanup and SQLite integrity.
- Backup/restore round trip is verified using a disposable workspace and SQLite database on a local filesystem (not a physical NAS share).
- Unit coverage includes Autopilot atomic scheduling, duplicate manual-run prevention, cross-process due-run claiming, replay-safe run history, legacy in-process run recovery, task metadata privacy, queue concurrency caps and stale-lease progress rejection.
- A real FFmpeg fixture is rendered twice to the same deterministic output path and re-probed with FFprobe to verify overwrite/replay safety.

## Remaining external validation

- A long real Whisper/FFmpeg media job killed mid-encode has not been exercised end-to-end with a representative production video. A synthetic FFmpeg render/replay is verified; hard process termination during a live encode still needs a longer media-specific soak.
- Physical NAS share write/read/restore rehearsal remains environment-specific and must be run against the actual NAS.
- GitHub Actions status is not inferred from local tests; check the commit's Actions run separately.

## Operational commands

Backup to a mounted NAS share:

```powershell
python tools/backup_workspace.py --destination "\\NAS\YamanBackups"
```

Restore (stop all YAMAN processes first):

```powershell
python tools/restore_workspace.py --snapshot "\\NAS\YamanBackups\YAMAN-VIRAL-STUDIO-TIMESTAMP" --workspace ".\workspace" --confirm-restore
```

Recommended initial production settings:

```powershell
$env:YAMAN_QUEUE_LEASE_SECONDS = "90"
$env:YAMAN_QUEUE_HEARTBEAT_SECONDS = "15"
$env:YAMAN_WORKER_HEARTBEAT_SECONDS = "10"
$env:YAMAN_WORKER_STALE_SECONDS = "45"
$env:YAMAN_QUEUE_MAX_CONCURRENT = "1"
```
