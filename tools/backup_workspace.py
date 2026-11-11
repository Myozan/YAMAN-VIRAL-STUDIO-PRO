r"""Create a consistent local-first workspace backup suitable for copying to a NAS.

Example:
  python tools/backup_workspace.py --destination \\NAS\YamanBackups
The live SQLite files are snapshotted with SQLite's online backup API; never copy
an active WAL database as a plain file.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
DATABASE_SUFFIXES = {".sqlite", ".sqlite3", ".db"}
IGNORED_DIRS = {"__pycache__", ".cache", "tmp", "temp"}


def backup_sqlite(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{source.resolve().as_posix()}?mode=ro", uri=True, timeout=30)
    try:
        dst = sqlite3.connect(destination, timeout=30)
        try:
            src.backup(dst, pages=256, sleep=0.05)
            dst.execute("PRAGMA integrity_check")
            check = dst.execute("PRAGMA integrity_check").fetchone()
            if not check or check[0] != "ok":
                raise RuntimeError(f"SQLite integrity check failed for {source}: {check}")
        finally:
            dst.close()
    finally:
        src.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a consistent YAMAN workspace backup")
    parser.add_argument("--destination", required=True, type=Path, help="Local folder or mounted NAS share")
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
    file_count = 0
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            continue
        if path.is_dir():
            continue
        if path.suffix.lower() in DATABASE_SUFFIXES:
            target = db_root / relative
            backup_sqlite(path, target)
            database_manifest.append({
                "source": relative.as_posix(),
                "backup": target.relative_to(snapshot).as_posix(),
            })
            continue
        if path.name.endswith(("-wal", "-shm", "-journal")):
            continue
        target = files_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        file_count += 1

    manifest = {
        "format": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_workspace": str(source),
        "file_count": file_count,
        "databases": database_manifest,
        "sqlite_method": "sqlite3.Connection.backup",
    }
    (snapshot / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"backup": str(snapshot), "files": file_count,
                      "databases": len(database_manifest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
