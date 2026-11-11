"""Restore a workspace snapshot. Stop all YAMAN processes before running.

This operation overwrites matching workspace files and SQLite databases. It
requires the explicit --confirm-restore switch.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore a YAMAN workspace backup")
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--confirm-restore", action="store_true")
    args = parser.parse_args()
    if not args.confirm_restore:
        parser.error("Restore refused. Stop YAMAN and pass --confirm-restore after verifying the snapshot.")
    snapshot = args.snapshot.resolve()
    workspace = args.workspace.resolve()
    manifest_path = snapshot / "manifest.json"
    if not manifest_path.is_file():
        parser.error(f"Snapshot manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != 1 or manifest.get("sqlite_method") != "sqlite3.Connection.backup":
        parser.error("Unsupported or invalid backup format.")

    files_root = snapshot / "files"
    if files_root.is_dir():
        for source in files_root.rglob("*"):
            if not source.is_file() or source.is_symlink():
                continue
            target = (workspace / source.relative_to(files_root)).resolve()
            if workspace not in target.parents:
                parser.error("Snapshot contains a path outside the workspace.")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    restored = []
    for entry in manifest.get("databases", []):
        relative = Path(entry["source"])
        if relative.is_absolute() or ".." in relative.parts:
            parser.error("Unsafe database path in manifest.")
        source = (snapshot / entry["backup"]).resolve()
        if snapshot not in source.parents or not source.is_file():
            parser.error(f"Database backup is missing or unsafe: {entry['backup']}")
        target = (workspace / relative).resolve()
        if workspace not in target.parents:
            parser.error("Database restore target is outside workspace.")
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".restore.tmp")
        shutil.copy2(source, temp)
        db = sqlite3.connect(temp)
        try:
            check = db.execute("PRAGMA integrity_check").fetchone()
            if not check or check[0] != "ok":
                raise RuntimeError(f"SQLite integrity check failed: {relative}")
        finally:
            db.close()
        for suffix in ("-wal", "-shm", "-journal"):
            Path(str(target) + suffix).unlink(missing_ok=True)
        temp.replace(target)
        restored.append(relative.as_posix())

    print(json.dumps({"restored_workspace": str(workspace),
                      "restored_databases": restored,
                      "warning": "Restart YAMAN only after verifying restored files."},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
