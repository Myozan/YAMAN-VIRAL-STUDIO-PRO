# QA 3.7 — Durable Task Queue

**Status:** Runtime integration implemented; full regression and process-handoff test completed.

## Objective

Replace process-local scheduling for core media jobs with a durable SQLite-backed queue. A task can be claimed by another same-host worker after its execution lease expires.

## Runtime integration

The FastAPI lifespan now starts and stops a durable queue worker. The worker:

1. Claims one eligible task atomically.
2. Renews its task-specific lease while the handler runs.
3. Reconstructs the request from the persisted JSON payload.
4. Rehydrates source project metadata from the workspace when needed.
5. Executes the registered handler.
6. Synchronizes terminal status with the existing task history and event API.
7. Allows another worker to reclaim the task after lease expiry.

The durable dispatcher is now used for:
- Remote video analysis.
- Local video analysis.
- Clip rendering.
- Summary video generation.
- Agent-team analysis and the existing agent retry route.

Autopilot manual and scheduled runs now use the same durable queue. The scheduler only claims due schedules and atomically enqueues them; content generation runs inside the queue worker. Other non-core background workflows may still use process-local scheduling.

## Queue contract

The implementation in `app/task_queue.py` provides:

- Durable task specifications stored as JSON.
- Atomic enqueue and claim operations using short `BEGIN IMMEDIATE` transactions.
- Priority and scheduled availability timestamps.
- Owner-bound execution leases with explicit heartbeat renewal.
- Expired-lease recovery with bounded exponential retry delay.
- Maximum attempt enforcement and terminal failure after the final lease expires.
- Idempotency keys to prevent duplicate enqueue operations.
- Owner-checked completion and cancellation that revokes the former worker's lease.
- SQLite indexes for ready work, expired leases, and owner lookups.

The task record and queue record are inserted in the same SQLite transaction for new API tasks. Agent retry claims, task records, events, and queue records are also committed together.

## Safety properties

1. A task can be claimed by only one worker at a time.
2. A worker cannot renew or complete a task after its lease expires.
3. A cancelled task cannot be completed by its former owner.
4. Expired tasks are requeued only while attempts remain; otherwise they become failed in both queue and task history.
5. Queue transactions do not wrap media processing or other long-running work.
6. Retry delay is bounded to five minutes.
7. The queue uses at-least-once execution semantics: a process crash after producing an output but before acknowledging completion can cause the handler to run again. Output paths and handlers must therefore remain safely repeatable.
8. The database must remain on a local filesystem when using SQLite WAL.

## Deployment boundary

This queue supports multiple worker processes on one host sharing a local SQLite database and workspace. It does not provide multi-host coordination. A multi-host deployment requires PostgreSQL plus a durable distributed broker/worker architecture.

## QA 3.8 additions

- Global active-task concurrency is enforced inside the SQLite claim transaction. Default is one active task across all same-host Uvicorn processes (`YAMAN_QUEUE_MAX_CONCURRENT=1`).
- Worker heartbeat rows are pruned after the stale threshold; a resumed process re-registers itself with an upsert heartbeat.
- Queue health and metadata endpoints: `GET /api/queue/health` and `GET /api/queue/tasks`.
- Autopilot schedule/manual enqueue, task journal and schedule state are committed atomically. Same due occurrence is not enqueued twice across processes.
- Autopilot run-history writes are idempotent by durable task ID; stale workers cannot mutate schedule state after lease loss.
- NAS backup stages SQLite online snapshots locally before copying them to the destination. Restore validates integrity and requires explicit confirmation.

## Verification

- Real Windows smoke test starts two independent Uvicorn processes. The first worker is killed during a task; the second reclaims and completes it after a shortened test lease. Production lease default remains 90 seconds.
- Backup/restore round trip verified with a disposable local workspace fixture. A physical NAS share rehearsal remains environment-specific.
- Long real FFmpeg/Whisper process interruption remains a separate media-specific soak test; generic queue process failover is verified.
- Full regression suite and static checks are recorded in the QA 3.8 operations page.
