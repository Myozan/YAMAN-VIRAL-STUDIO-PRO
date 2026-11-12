"""Create a verified, SQLite-consistent workspace backup suitable for a NAS."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
DATABASE_SUFFIXES = {".sqlite", ".sqlite3", ".db"}
IGNORED_DIRS = {"__pycache__", ".cache", "tmp", "temp"}
HASH_CHUNK_SIZE = 1024 * 1024


def file_digest(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(HASH_CHUNK_SIZE), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def copy_verified(source: Path, destination: Path) -> dict[str, int | str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    source_size, source_hash = file_digest(source)
    copied_size, copied_hash = file_digest(destination)
    if (source_size, source_hash) != (copied_size, copied_hash):
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"Backup copy verification failed: {source}")
    return {"size_bytes": copied_size, "sha256": copied_hash}


def backup_sqlite(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(
        f"file:{source.resolve().as_posix()}?mode=ro", uri=True, timeout=30
    )
    try:
        dst = sqlite3.connect(destination, timeout=30)
        try:
            src.backup(dst, pages=256, sleep=0.05)
            check = dst.execute("PRAGMA integrity_check").fetchone()
            if not check or check[0] != "ok":
                raise RuntimeError(f"SQLite integrity check failed for {source}: {check}")
        finally:
            dst.close()
    finally:
        src.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a verified YAMAN workspace backup")
    parser.add_argument("--destination", required=True, type=Path,
                        help="Local folder or mounted NAS share")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    args = parser.parse_args()
    source = args.workspace.resolve()
    if not source.is_dir():
        parser.error(f"Workspace does not exist: {source}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = args.destination.expanduser().resolve() / f"YAMAN-VIRAL-STUDIO-{stamp}"
    files_root = snapshot / "files"
    db_root = snapshot / "databases"
    files_root.mkdir(parents=True, exist_ok=False)
    db_root.mkdir(parents=True, exist_ok=True)

    database_manifest = []
    file_manifest = []
    file_count = 0
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if path.is_symlink() or path.is_dir():
            continue
        if path.name.endswith(("-wal", "-shm", "-journal")):
            continue
        if path.suffix.lower() in DATABASE_SUFFIXES:
            target = db_root / relative
            # SQLite online backup snapshots the live DB locally first; only a
            # closed, integrity-checked snapshot is copied to the destination.
            with tempfile.TemporaryDirectory(prefix="yaman-sqlite-snapshot-") as staging:
                local_snapshot = Path(staging) / relative.name
                backup_sqlite(path, local_snapshot)
                metadata = copy_verified(local_snapshot, target)
            database_manifest.append({
                "source": relative.as_posix(),
                "backup": target.relative_to(snapshot).as_posix(),
                **metadata,
            })
            continue

        target = files_root / relative
        metadata = copy_verified(path, target)
        file_manifest.append({"path": relative.as_posix(), **metadata})
        file_count += 1

    manifest = {
        "format": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_workspace": str(source),
        "file_count": file_count,
        "files": file_manifest,
        "databases": database_manifest,
        "sqlite_method": "sqlite3.Connection.backup",
        "hash_algorithm": "sha256",
    }
    manifest_tmp = snapshot / "manifest.json.tmp"
    manifest_tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_tmp.replace(snapshot / "manifest.json")
    print(json.dumps({
        "backup": str(snapshot), "files": file_count,
        "databases": len(database_manifest), "verified": True,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
