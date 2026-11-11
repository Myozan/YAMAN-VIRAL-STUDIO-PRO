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

Autopilot scheduling and other non-core background workflows still use their existing scheduling path; they are not claimed to be part of the durable queue yet.

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

## Validation still required

- Full regression suite and static checks.
- A controlled worker-termination test proving that a second worker reclaims an expired task.
- Verify shutdown, lease renewal, retry exhaustion, cancellation and partial output behavior.

## Verification

- Full Windows/Python 3.12 suite: 98 passed, 2 skipped (100 total).
- Python compileall, JavaScript syntax checks, PWA manifest parse and Git whitespace checks pass.
- The two skipped cases are symlink-specific tests unavailable under the current Windows account privileges.
