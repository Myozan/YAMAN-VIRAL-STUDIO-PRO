import json
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_workspace_backup_and_restore_uses_consistent_sqlite_snapshot(tmp_path):
    workspace = tmp_path / "workspace"
    destination = tmp_path / "nas"
    workspace.mkdir()
    database = workspace / "orchestration.sqlite3"
    db = sqlite3.connect(database)
    try:
        db.execute("CREATE TABLE sample(value TEXT)")
        db.execute("INSERT INTO sample VALUES('before-backup')")
        db.commit()
    finally:
        db.close()
    (workspace / "media.txt").write_text("original media", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "backup_workspace.py"),
         "--destination", str(destination), "--workspace", str(workspace)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    snapshot = Path(payload["backup"])
    manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["sqlite_method"] == "sqlite3.Connection.backup"
    assert len(manifest["databases"]) == 1

    db = sqlite3.connect(database)
    try:
        db.execute("UPDATE sample SET value='changed-after-backup'")
        db.commit()
    finally:
        db.close()
    (workspace / "media.txt").write_text("changed media", encoding="utf-8")

    restore = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "restore_workspace.py"),
         "--snapshot", str(snapshot), "--workspace", str(workspace), "--confirm-restore"],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert restore.returncode == 0, restore.stderr
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT value FROM sample").fetchone()[0] == "before-backup"
    assert (workspace / "media.txt").read_text(encoding="utf-8") == "original media"


def test_restore_requires_explicit_confirmation(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "manifest.json").write_text(
        json.dumps({"format": 1, "sqlite_method": "sqlite3.Connection.backup", "databases": []}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "restore_workspace.py"),
         "--snapshot", str(snapshot), "--workspace", str(tmp_path / "workspace")],
        cwd=ROOT, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0
    assert "--confirm-restore" in result.stderr
