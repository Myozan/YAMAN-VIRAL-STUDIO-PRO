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

A healthy API does not imply all optional providers are configured.

## 3. Graceful shutdown

- Stop the application using its terminal window.
- Avoid terminating during a render or database write.
- If the process crashes, restart and inspect task history. Queued/running tasks from the prior process are marked interrupted at startup.
- Retry interrupted work only after confirming that any partial output is safe to replace.

## 4. Backup

Recommended offline backup set:
- Entire `workspace/` directory.
- `settings.local.json`.
- `.oauth.key` if the default local key file is used.
- Any externally managed key material referenced by environment variables (stored separately and securely).

Stop the application before a plain file-copy backup of SQLite. Encrypt the backup and restrict access.

## 5. Restore

1. Restore into a separate working directory first.
2. Restore workspace databases, job folders, encrypted vault files and key material as a matched set.
3. Verify SQLite integrity using a read-only copy.
4. Start the app and inspect task history, job loading and OAuth vault decryption.
5. Open a sample output and verify it with FFprobe.
6. Switch the production workspace only after validation.

## 6. Common incidents

| Symptom | Likely cause | Response |
|---|---|---|
| Ollama disconnected | Service stopped, wrong URL, model unavailable | Start Ollama, verify URL and installed model |
| Whisper initialization error | Model download, CUDA runtime or memory issue | Try CPU/tiny model and inspect logs |
| FFmpeg render fails | Missing codec, bad source or disk full | Run FFprobe, verify free space and FFmpeg install |
| OAuth callback rejected | State mismatch/expiry or redirect URI mismatch | Restart OAuth flow and verify exact redirect URI |
| Provider upload rejected | Missing scope, app review, quota or account eligibility | Inspect sanitized provider response and app permissions |
| Task interrupted | App restarted or process exited | Inspect partial files and retry if safe |
| Encrypted vault cannot decrypt | Key mismatch or missing key | Restore matching key/vault backup; do not overwrite originals |

## 7. Incident data handling

- Never paste OAuth tokens, API keys, cookies or full authorization headers into issue reports.
- Redact personal media paths and source URLs if they identify private content.
- Preserve sanitized timestamps, endpoint, status code and correlation/task ID.
- Rotate exposed provider credentials immediately.
