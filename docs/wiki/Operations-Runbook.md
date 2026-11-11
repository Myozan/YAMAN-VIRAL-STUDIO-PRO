# Operations Runbook

## Startup checks

1. Python 3.12 environment is active.
2. FFmpeg and FFprobe are available on PATH.
3. Start Ollama if local AI is needed.
4. Run `run_windows.bat`.
5. Open `http://127.0.0.1:8765`.
6. Check `GET /api/health`.

## Backup set

Back up together:
- `workspace/`
- `settings.local.json`
- `.oauth.key` if the default local key is used
- externally managed encryption key material, stored separately

Stop the app before a simple file-copy backup of SQLite. Encrypt the backup.

## Recovery

1. Restore into a separate folder.
2. Restore SQLite files, job folders, encrypted vaults and matching key material.
3. Verify database integrity and vault decryption.
4. Start the app and inspect task history.
5. Confirm a sample job and output video can be opened.
6. Switch the active workspace only after successful validation.

## Common failures

| Symptom | Response |
|---|---|
| Ollama disconnected | Start service; verify URL and model |
| Whisper fails | Try CPU/tiny model; inspect CUDA and memory |
| FFmpeg fails | Check FFprobe, codec and free disk space |
| OAuth callback rejected | Restart flow; verify state and redirect URI |
| Provider upload rejected | Check scopes, app review, quota and account eligibility |
| Task interrupted | Inspect partial output; retry when safe |

Do not share tokens, API keys, cookies, authorization headers or private media in issue reports.

Full operations notes: [Operations Runbook](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/OPERATIONS-RUNBOOK.md).
