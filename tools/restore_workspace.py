"""Preflight and restore a verified workspace snapshot.

Stop all YAMAN processes before running. The command overwrites matching
workspace files and SQLite databases and requires --confirm-restore.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path


HASH_CHUNK_SIZE = 1024 * 1024


def file_digest(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(HASH_CHUNK_SIZE), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def safe_relative(value: str, label: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"Unsafe {label} path: {value}")
    return relative


def verify_hash(path: Path, entry: dict, label: str) -> None:
    size, digest = file_digest(path)
    if size != int(entry.get("size_bytes", -1)) or digest != entry.get("sha256"):
        raise ValueError(f"{label} checksum/size mismatch: {path}")


def sqlite_integrity(path: Path) -> None:
    db = sqlite3.connect(path)
    try:
        check = db.execute("PRAGMA integrity_check").fetchone()
        if not check or check[0] != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {path}")
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore a YAMAN workspace snapshot")
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
    version = manifest.get("format")
    if version not in (1, 2) or manifest.get("sqlite_method") != "sqlite3.Connection.backup":
        parser.error("Unsupported or invalid backup format.")
    if version == 2 and manifest.get("hash_algorithm") != "sha256":
        parser.error("Unsupported backup hash algorithm.")

    files_root = snapshot / "files"
    file_entries = manifest.get("files", []) if version == 2 else []
    database_entries = manifest.get("databases", [])
    if not isinstance(file_entries, list) or not isinstance(database_entries, list):
        parser.error("Invalid backup manifest entries.")
    if version == 2 and int(manifest.get("file_count", -1)) != len(file_entries):
        parser.error("Backup file count does not match the manifest.")
    if version == 2 and any(not isinstance(item, dict) or not isinstance(item.get("path"), str)
                            for item in file_entries):
        parser.error("Invalid file entry in backup manifest.")

    # Preflight every source and database before changing the destination.
    verified_files: list[tuple[Path, Path]] = []
    if files_root.is_dir():
        actual_files = {
            path.relative_to(files_root).as_posix()
            for path in files_root.rglob("*") if path.is_file() and not path.is_symlink()
        }
        if version == 2:
            expected_files = {entry.get("path") for entry in file_entries}
            if actual_files != expected_files or len(expected_files) != len(file_entries):
                parser.error("Backup file list does not match the manifest.")
        for source in files_root.rglob("*"):
            if not source.is_file() or source.is_symlink():
                continue
            relative = source.relative_to(files_root)
            target = (workspace / relative).resolve()
            if workspace not in target.parents:
                parser.error("Snapshot contains a path outside the workspace.")
            if version == 2:
                entry = next((item for item in file_entries
                              if item.get("path") == relative.as_posix()), None)
                if entry is None:
                    parser.error(f"File is missing from manifest: {relative}")
                try:
                    verify_hash(source, entry, "Workspace file")
                except (OSError, ValueError) as exc:
                    parser.error(str(exc))
            verified_files.append((source, target))
    elif version == 2 and file_entries:
        parser.error("Snapshot files directory is missing.")

    verified_databases: list[tuple[Path, Path, str]] = []
    for entry in database_entries:
        try:
            relative = safe_relative(entry["source"], "database source")
            backup_relative = safe_relative(entry["backup"], "database backup")
        except (KeyError, ValueError) as exc:
            parser.error(str(exc))
        source = (snapshot / backup_relative).resolve()
        if snapshot not in source.parents or not source.is_file():
            parser.error(f"Database backup is missing or unsafe: {entry.get('backup')}")
        target = (workspace / relative).resolve()
        if workspace not in target.parents:
            parser.error("Database restore target is outside workspace.")
        try:
            if version == 2:
                verify_hash(source, entry, "SQLite backup")
            sqlite_integrity(source)
        except (OSError, ValueError, sqlite3.Error, RuntimeError) as exc:
            parser.error(str(exc))
        verified_databases.append((source, target, relative.as_posix()))

    # Only after all source files pass preflight do we modify the workspace.
    for source, target in verified_files:
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".restore.tmp")
        shutil.copy2(source, temp)
        temp.replace(target)

    restored = []
    for source, target, relative in verified_databases:
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".restore.tmp")
        shutil.copy2(source, temp)
        sqlite_integrity(temp)
        for suffix in ("-wal", "-shm", "-journal"):
            Path(str(target) + suffix).unlink(missing_ok=True)
        temp.replace(target)
        restored.append(relative)

    print(json.dumps({
        "restored_workspace": str(workspace),
        "restored_files": len(verified_files),
        "restored_databases": restored,
        "verified": True,
        "warning": "Restart YAMAN only after verifying restored files.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
