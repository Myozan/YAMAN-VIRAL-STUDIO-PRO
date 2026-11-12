# QA 3.9 — Production Reliability & NAS Recovery

## Scope

QA 3.9 hardens worker-crash cleanup and backup integrity on top of QA 3.8. Product version remains v1.8.0.

## Media child-process lifecycle

- Added `app/process_control.py` with a shared media subprocess runner.
- On Windows, each media child is assigned to a Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
- When the worker exits normally, times out, or is forcibly terminated, closing the Job Object terminates its FFmpeg process tree.
- FFmpeg invocations in the main render pipeline and face-tracked framing now use the managed runner.
- If Windows refuses Job Object assignment, the child is terminated and the operation fails rather than leaving an untracked encoder running.
- This is a Windows-specific process-tree guarantee; it does not claim distributed or cross-host process supervision.

## Backup format v2

- Backup manifest format is now v2 and records SHA-256 plus byte size for each copied workspace file and SQLite snapshot.
- Every copied file is read back and compared with its source hash before the manifest is finalized.
- The manifest is written through a temporary file and atomically renamed last. An interrupted backup without a complete manifest is not restorable.
- SQLite databases are still snapshotted with SQLite's online backup API into local temporary storage before copying to the destination.
- Restore preflights every file path, file hash, database hash and SQLite integrity before changing the target workspace.
- Workspace files are restored through temporary files and atomic replacement.
- Restore remains backward-compatible with v1 snapshots; v1 snapshots do not have file hashes.
- Restore still requires `--confirm-restore` and all YAMAN processes must be stopped first.

## Validation performed

- Windows worker-kill test confirms the FFmpeg child exits when its parent worker is forcibly terminated.
- Production-default lease integration test uses the configured 90-second lease, 15-second task heartbeat, 10-second worker heartbeat and 45-second stale-worker threshold. A second Uvicorn process reclaims and completes the task after the first is killed.
- Backup/restore round-trip test verifies restored file and SQLite contents.
- Tampered snapshot test confirms checksum rejection occurs before any target workspace file is changed.
- Existing FFmpeg render/replay smoke test remains in place.
- Local end-to-end media validation used the cached Faster-Whisper `small` model on CPU to transcribe the 47.88-second demo input (10 English segments), then rendered a 12-second captioned vertical MP4 at 1080 x 1920 and verified it with FFprobe (9.08-second render, 308,080-byte output).
- The worker-kill test uses a synthetic live FFmpeg input. A full production-length Whisper transcription plus render interrupted mid-job remains a separate soak test.
- Full Windows/Python 3.12 suite after cross-platform path validation: **131 passed, 2 skipped (133 total)**. The two skips are the existing Windows symlink privilege tests.
- Static validation passed: `compileall` for app/tests/tools, Node syntax checks for `web/app.js` and `web/sw.js`, PWA manifest JSON parsing and `git diff --check`.

## CI follow-up

The first GitHub Actions run showed that the Ubuntu runner lacked FFmpeg/FFprobe and exposed a Windows-drive-path validation mismatch on POSIX. The workflow now installs FFmpeg on both Linux and Windows runners, and the Auto-Editor endpoint rejects POSIX absolute paths, Windows drive/UNC paths and traversal before resolving workspace files. The Windows process-recovery CI job passed on the initial run; the updated full workflow must be rechecked after the follow-up push.

## NAS production rehearsal

- No physical NAS share was mounted or mapped on the Windows test machine during this run.
- Local disposable-destination backup/restore tests do not prove NAS permissions, network interruption behavior, throughput or hardware reliability.
- Before production sign-off, run the backup against the actual UNC share and restore into a separate disposable workspace on that share.
- Never place the live SQLite WAL database itself on the NAS; only copy the SQLite online snapshot.

## Operational commands

Backup to a verified NAS share:

```powershell
python tools/backup_workspace.py --destination "\\NAS\YamanBackups"
```

Restore to a separate test workspace first:

```powershell
python tools/restore_workspace.py --snapshot "<snapshot-folder>" --workspace ".\workspace-restore-test" --confirm-restore
```

Stop every YAMAN/Uvicorn process before restoring into the production workspace.
