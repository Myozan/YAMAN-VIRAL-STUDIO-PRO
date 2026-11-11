# Operations Runbook — v1.8.0

## 1. Startup

1. Confirm Python 3.12 virtual environment is available.
2. Confirm FFmpeg and FFprobe are on PATH.
3. Start Ollama if AI inference is required.
4. Run `run_windows.bat`.
5. Open `http://127.0.0.1:8765`.
6. Check `GET /api/health` and verify optional dependencies as needed.

## 2. Health checks

| Check | Command / endpoint | Healthy indication |
|---|---|---|
| API | GET /api/health | JSON response, application responds |
| System | GET /api/system/metrics | CPU/memory metrics returned |
| Ollama | GET /api/ollama/status | Connected and model list available |
| FFmpeg | `ffmpeg -version` | Version information |
| FFprobe | `ffprobe -version` | Version information |
| Auto-Editor | GET /api/auto-editor/status | Installed state reported |
| Durable queue | GET /api/queue/health | `ok=true`, live worker and queue counts |
| Queue tasks | GET /api/queue/tasks?limit=50 | Recent task metadata without private payloads |

A healthy API does not imply all optional providers are configured. Third-party requests-based HTTPS APIs use the pinned transport; local Ollama remains a separate local-service connection, while yt-dlp and Edge TTS use their own client transports.

## 3. Graceful shutdown

- Stop the application using its terminal window.
- Avoid terminating during a render or database write.
- Each process registers a worker heartbeat every 10 seconds. Core media tasks also renew a task-specific 90-second execution lease every 15 seconds.
- Analysis (remote/local), render, summary and agent tasks are stored in the durable SQLite queue and claimed by the process worker poller. If a worker disappears, another same-host worker requeues the task after its execution lease expires; worker-crash retry delay grows exponentially and is capped at five minutes, with three attempts by default. Application-level task failures remain failed for explicit review/retry.
- Queue execution is at-least-once. A crash after an output is written but before completion is acknowledged can repeat the handler. Inspect partial outputs and confirm overwrite safety before manual intervention.
- Autopilot manual and scheduled runs are now enqueued in the same durable SQLite queue. The scheduler thread only claims due schedules; content generation is performed by queue workers. Other non-core workflows may still use process-local scheduling.

## 4. Multi-worker operating boundary

- Multiple Uvicorn workers may share the same local `workspace/orchestration.sqlite3` database on one host. Task state, queue payloads, leases, cancellation, Autopilot schedules and saved job metadata are shared through SQLite/filesystem.
- The default global queue concurrency is one task (`YAMAN_QUEUE_MAX_CONCURRENT=1`) to protect local CPU/GPU resources. Increase only after load testing the actual machine.
- Queue lease defaults: 90 seconds, renewed every 15 seconds. Worker process heartbeats default to 10 seconds; stale worker registrations are pruned after 45 seconds.
- The Autopilot page includes a live queue monitor with task counts, worker heartbeats, global concurrency and recent task metadata. Use its refresh action after starting or cancelling work.
- SQLite WAL requires a local filesystem; do not place the database on a network share. Multi-host execution is not supported and requires PostgreSQL plus a durable distributed broker/worker system.

## 5. Backup

Recommended offline backup set:
- Entire `workspace/` directory.
- `settings.local.json`.
- `.oauth.key` if the default local key file is used.
- `.oauth.key.rotated` if environment-managed OAuth key rotation has been performed.
- Any externally managed key material referenced by environment variables (stored separately and securely).

Use `python tools/backup_workspace.py --destination "\\\\NAS\\YamanBackups"` for a consistent online SQLite snapshot followed by a copy to the NAS. The database snapshot is staged locally first; do not copy the live SQLite/WAL files directly. Back up `settings.local.json` and matching OAuth key material separately and securely. Encrypt the backup and restrict access.

## 6. Restore

1. Stop every YAMAN/Uvicorn process before restoring.
2. Restore into a separate working directory first when possible.
3. Run `python tools/restore_workspace.py --snapshot "<snapshot-folder>" --workspace ".\\workspace" --confirm-restore`.
4. Restore `settings.local.json` and matching OAuth key material as a matched set, including `.oauth.key.rotated` when present.
5. Verify SQLite integrity, task history, job loading and OAuth vault decryption.
6. Open a sample output and verify it with FFprobe.
7. Switch the production workspace only after validation.

## 7. Common incidents

| Symptom | Likely cause | Response |
|---|---|---|
| Ollama disconnected | Service stopped, wrong URL, model unavailable | Start Ollama, verify URL and installed model |
| Whisper initialization error | Model download, CUDA runtime or memory issue | Try CPU/tiny model and inspect logs |
| FFmpeg render fails | Missing codec, bad source or disk full | Run FFprobe, verify free space and FFmpeg install |
| OAuth callback rejected | State mismatch/expiry or redirect URI mismatch | Restart OAuth flow and verify exact redirect URI |
| Provider upload rejected | Missing scope, app review, quota or account eligibility | Inspect sanitized provider response and app permissions |
| Task remains running after worker crash | Queue lease has not expired yet | Allow the 90-second execution lease to expire; inspect queue/task history and partial outputs |
| Task failed after repeated worker crashes | Maximum queue attempts exhausted | Inspect the last error and partial outputs, then create a fresh task after resolving the cause |
| Encrypted vault cannot decrypt | Key mismatch or missing key | Restore matching key/vault backup; do not overwrite originals |

## 8. Incident data handling

- Never paste OAuth tokens, API keys, cookies or full authorization headers into issue reports.
- Redact personal media paths and source URLs if they identify private content.
- Preserve sanitized timestamps, endpoint, status code and correlation/task ID.
- Rotate exposed provider credentials immediately.
