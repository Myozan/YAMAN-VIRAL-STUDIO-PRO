# QA 3.8 — Queue Operations and Runtime Observability

## Scope

QA 3.8 extends the QA 3.7 durable SQLite queue with an operational status surface. The product version remains 1.8.0.

## Queue health API

- `GET /api/queue/health` returns queue counts for queued, running, completed, failed and cancelled tasks.
- Worker entries include process ID, host, start time and last heartbeat.
- Heartbeats older than the configured worker stale window (currently 45 seconds) are marked unhealthy.
- The response intentionally excludes task payloads, media paths and task error contents.
- Queue database read errors return HTTP 503.
- A queue with no registered workers is not reported as healthy; stale worker heartbeats also make the health state unhealthy.

This endpoint is an operational diagnostic, not an authentication boundary. Until the application has a complete authentication and authorization layer, keep the service bound to loopback or behind a trusted private access layer; do not expose it directly to a LAN or the public internet.

## Storage and recovery constraints

- SQLite WAL is supported only on a local filesystem shared by processes on the same host.
- Do not place the live SQLite WAL database on a NAS share or network filesystem.
- For NAS protection, use a SQLite online backup operation to create a consistent snapshot on local storage, then copy that snapshot and the associated workspace assets to the NAS.
- A raw copy of an actively-written SQLite database plus its WAL/SHM files is not a supported backup procedure.
- Multi-host workers require a different coordination architecture and are out of scope.

## QA 3.8 validation plan

1. Start two independent Uvicorn processes against the same local workspace database and verify both register worker heartbeats.
2. Enqueue a harmless deterministic task and verify only one worker claims it.
3. Terminate the owning process during a long-running test handler; verify lease expiry and re-claim by the surviving process.
4. Verify the queue health API reports worker count, queue counts and stale heartbeats without exposing payload data.
5. Verify backup/restore using SQLite's online backup API and a disposable workspace fixture.
6. Run the complete test suite, compile checks, JavaScript syntax checks and whitespace validation.

## Current completion status

- Implemented: queue snapshot primitive and `GET /api/queue/health`.
- Implemented: unit tests for queue counts, worker heartbeat freshness and payload omission.
- Implemented: `tools/backup_workspace.py` uses SQLite online backup snapshots and copies workspace assets for NAS/offline storage.
- Implemented: `tools/restore_workspace.py` validates SQLite integrity and requires explicit `--confirm-restore`; stop the application before restoring.
- Validated: two independent Windows Uvicorn processes registered in the same disposable local SQLite database; both health endpoints saw both workers and reported fresh heartbeats.
- Validated: backup/restore round trip against a disposable SQLite database and workspace media fixture.
- Validated: full test suite — 103 passed, 2 skipped; Python compile, JavaScript syntax, PWA manifest JSON and `git diff --check` passed.
- Pending: real two-Uvicorn-process lease-expiry failover with a long-running handler and the production 90-second lease.
- Pending: long FFmpeg/Whisper interruption test using a disposable media fixture.
- Pending: moving Autopilot scheduled and manual runs into the durable queue. The existing scheduler still executes its cycle in a process-local thread and must not be treated as durable.
