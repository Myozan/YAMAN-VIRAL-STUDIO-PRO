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

A healthy API does not imply all optional providers are configured. Third-party requests-based HTTPS APIs use the pinned transport; local Ollama remains a separate local-service connection, while yt-dlp and Edge TTS use their own client transports.

## 3. Graceful shutdown

- Stop the application using its terminal window.
- Avoid terminating during a render or database write.
- Each worker registers a heartbeat every 10 seconds. A task is marked interrupted only after its owning worker lease expires (45 seconds) or that worker shuts down; starting another worker does not interrupt active work. A background reaper checks stale leases every 10 seconds.
- Inspect task history after a crash and confirm partial outputs before retrying. The current FastAPI `BackgroundTasks` queue is process-local: recovered tasks are marked interrupted, not automatically replayed on another worker.
- Retry interrupted work only after confirming that any partial output is safe to replace.

## 4. Multi-worker operating boundary

- Multiple Uvicorn workers may share the same local `workspace/orchestration.sqlite3` database on one host. SQLite WAL requires a local filesystem; do not place the database on a network share.
- Task state, cancellation and saved job metadata are shared through SQLite/filesystem. Actual background execution remains tied to the worker that accepted the request.
- Multi-host execution is not supported by this SQLite/BackgroundTasks setup. It requires a shared PostgreSQL database and a durable task broker/worker system.

## 5. Backup

Recommended offline backup set:
- Entire `workspace/` directory.
- `settings.local.json`.
- `.oauth.key` if the default local key file is used.
- `.oauth.key.rotated` if environment-managed OAuth key rotation has been performed.
- Any externally managed key material referenced by environment variables (stored separately and securely).

Stop the application before a plain file-copy backup of SQLite. Encrypt the backup and restrict access.

## 6. Restore

1. Restore into a separate working directory first.
2. Restore workspace databases, job folders, encrypted vault files and key material as a matched set, including `.oauth.key.rotated` when present.
3. Verify SQLite integrity using a read-only copy.
4. Start the app and inspect task history, job loading and OAuth vault decryption.
5. Open a sample output and verify it with FFprobe.
6. Switch the production workspace only after validation.

## 7. Common incidents

| Symptom | Likely cause | Response |
|---|---|---|
| Ollama disconnected | Service stopped, wrong URL, model unavailable | Start Ollama, verify URL and installed model |
| Whisper initialization error | Model download, CUDA runtime or memory issue | Try CPU/tiny model and inspect logs |
| FFmpeg render fails | Missing codec, bad source or disk full | Run FFprobe, verify free space and FFmpeg install |
| OAuth callback rejected | State mismatch/expiry or redirect URI mismatch | Restart OAuth flow and verify exact redirect URI |
| Provider upload rejected | Missing scope, app review, quota or account eligibility | Inspect sanitized provider response and app permissions |
| Task interrupted | App restarted or process exited | Inspect partial files and retry if safe |
| Encrypted vault cannot decrypt | Key mismatch or missing key | Restore matching key/vault backup; do not overwrite originals |

## 8. Incident data handling

- Never paste OAuth tokens, API keys, cookies or full authorization headers into issue reports.
- Redact personal media paths and source URLs if they identify private content.
- Preserve sanitized timestamps, endpoint, status code and correlation/task ID.
- Rotate exposed provider credentials immediately.
