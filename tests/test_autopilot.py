from datetime import datetime, timedelta, timezone
import subprocess
import sys
import sqlite3
import json
import pytest
from app import autopilot, task_queue

BASE = {
    "name": "QA schedule", "niche": "technology", "language": "tr",
    "clips": 4, "min_seconds": 15, "max_seconds": 45,
    "platforms": ["youtube"], "frequency": "daily", "publish_time": "09:00",
    "timezone": "Europe/Istanbul", "enabled": True,
}

def test_init_create_and_read_autopilot(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    assert item["id"] and item["name"] == BASE["name"]
    assert item["platforms"] == ["youtube"] and item["enabled"] is True
    assert datetime.fromisoformat(item["next_run"]).tzinfo is not None

def test_invalid_timezone_is_rejected(db_path):
    autopilot.init_autopilot(db_path)
    with pytest.raises(ValueError, match="saat dilimi"):
        autopilot.create_autopilot(db_path, {**BASE, "timezone": "Not/A_Timezone"})

def test_claim_due_only_claims_due_enabled_items(db_path):
    autopilot.init_autopilot(db_path)
    due = autopilot.create_autopilot(db_path, BASE)
    disabled = autopilot.create_autopilot(db_path, {**BASE, "name": "Disabled", "enabled": False})
    past = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE autopilots SET next_run=? WHERE id=?", (past, due["id"]))
        db.execute("UPDATE autopilots SET next_run=? WHERE id=?", (past, disabled["id"]))
    queued = autopilot.claim_due(db_path)
    assert [x["id"] for x in queued] == [due["id"]]
    assert queued[0]["queue_task_id"]
    assert autopilot.get_autopilot(db_path, due["id"])["last_status"] == "queued"
    assert autopilot.claim_due(db_path) == []
    with sqlite3.connect(db_path) as db:
        row = db.execute("SELECT task_type,status,payload_json FROM task_queue").fetchone()
        assert row[0:2] == ("autopilot", "queued")
        assert json.loads(row[2])["trigger"] == "scheduled"
        assert db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1

def test_manual_claim_has_explicit_states(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    assert autopilot.claim_manual(db_path, "missing") == "missing"
    assert autopilot.claim_manual(db_path, item["id"]) == "claimed"
    assert autopilot.claim_manual(db_path, item["id"]) == "running"

def test_finish_run_persists_history_and_deduplicates_processed_file(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    autopilot.finish_run(db_path, item["id"], "completed", "ok", task_id="task-1", outputs=["clip.mp4"], processed_file="source.mp4")
    autopilot.finish_run(db_path, item["id"], "completed", "ok", processed_file="source.mp4")
    current = autopilot.get_autopilot(db_path, item["id"])
    assert current["last_status"] == "completed" and current["processed_files"] == ["source.mp4"]
    with sqlite3.connect(db_path) as db:
        count = db.execute("SELECT COUNT(*) FROM autopilot_runs WHERE autopilot_id=?", (item["id"],)).fetchone()[0]
    assert count == 2

def test_delete_is_idempotent(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    assert autopilot.delete_autopilot(db_path, item["id"]) is True
    assert autopilot.delete_autopilot(db_path, item["id"]) is False


def test_due_autopilot_is_claimed_by_only_one_process(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    past = (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat()
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE autopilots SET next_run=? WHERE id=?", (past, item["id"]))

    worker = "import json,sys; from pathlib import Path; from app.autopilot import claim_due; print(json.dumps([x['id'] for x in claim_due(Path(sys.argv[1]))]))"
    processes = [
        subprocess.Popen([sys.executable, "-c", worker, str(db_path)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for _ in range(2)
    ]
    outputs = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=30)
        assert process.returncode == 0, stderr
        outputs.extend(json.loads(stdout))
    assert outputs.count(item["id"]) == 1
    with sqlite3.connect(db_path) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_manual_run_is_atomically_enqueued_and_duplicate_is_rejected(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    result = autopilot.enqueue_manual_run(db_path, item["id"])
    assert result["status"] == "queued"
    assert result["task_id"]
    duplicate = autopilot.enqueue_manual_run(db_path, item["id"])
    assert duplicate["status"] == "already_queued"
    assert "task_id" not in duplicate
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM task_queue").fetchone()[0] == 1
        row = db.execute("SELECT status,payload_json FROM task_queue").fetchone()
        assert row[0] == "queued"
        assert json.loads(row[1])["trigger"] == "manual"
        assert db.execute("SELECT COUNT(*) FROM task_events").fetchone()[0] == 1


def test_finish_run_is_idempotent_for_same_durable_task_id(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    autopilot.finish_run(db_path, item["id"], "review", "first", task_id="durable-task",
                         outputs=[{"file": "first.mp4"}])
    autopilot.finish_run(db_path, item["id"], "review", "replayed", task_id="durable-task",
                         outputs=[{"file": "final.mp4"}])
    with sqlite3.connect(db_path) as db:
        rows = db.execute(
            "SELECT COUNT(*),MAX(message),MAX(output_json) FROM autopilot_runs WHERE task_id='durable-task'"
        ).fetchone()
    assert rows[0] == 1
    assert rows[1] == "replayed"
    assert "final.mp4" in rows[2]


def test_manual_and_scheduled_runs_share_the_same_active_run_guard(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    past = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE autopilots SET next_run=? WHERE id=?", (past, item["id"]))
    scheduled = autopilot.claim_due(db_path)
    assert len(scheduled) == 1
    assert autopilot.enqueue_manual_run(db_path, item["id"])["status"] == "already_queued"
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM task_queue").fetchone()[0] == 1


def test_queue_task_listing_never_returns_payload(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    autopilot.enqueue_manual_run(db_path, item["id"])
    rows = __import__("app.task_queue", fromlist=["list_recent"]).list_recent(db_path)
    assert len(rows) == 1
    assert rows[0]["task_type"] == "autopilot"
    assert "payload" not in rows[0]
    assert "payload_json" not in rows[0]


def test_completed_run_can_be_recovered_by_durable_task_id(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    autopilot.finish_run(db_path, item["id"], "review", "outputs ready",
                         task_id="autopilot-task-1", outputs=[{"url": "ready.mp4"}])
    run = autopilot.get_run_by_task(db_path, "autopilot-task-1")
    assert run["status"] == "review"
    assert run["message"] == "outputs ready"
    assert run["outputs"] == [{"url": "ready.mp4"}]


def test_running_autopilot_cannot_be_deleted_or_edited(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    assert autopilot.enqueue_manual_run(db_path, item["id"])["status"] == "queued"
    assert autopilot.delete_autopilot(db_path, item["id"]) is False
    with pytest.raises(ValueError, match="düzenlenemez"):
        autopilot.update_autopilot(db_path, item["id"], {"name": "changed"})


def test_legacy_in_process_running_state_is_recovered_on_upgrade(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    with sqlite3.connect(db_path) as db:
        db.execute(
            "UPDATE autopilots SET last_status='running',last_message='old process task' WHERE id=?",
            (item["id"],),
        )
    autopilot.init_autopilot(db_path)
    recovered = autopilot.get_autopilot(db_path, item["id"])
    assert recovered["last_status"] == "failed"
    assert "yükseltme" in recovered["last_message"]


def test_autopilot_upgrade_keeps_live_durable_queue_run(db_path):
    autopilot.init_autopilot(db_path)
    item = autopilot.create_autopilot(db_path, BASE)
    queued = autopilot.enqueue_manual_run(db_path, item["id"])
    with sqlite3.connect(db_path) as db:
        db.execute(
            "UPDATE autopilots SET last_status='running' WHERE id=?",
            (item["id"],),
        )
    autopilot.init_autopilot(db_path)
    assert autopilot.get_autopilot(db_path, item["id"])["last_status"] == "running"
    assert task_queue.get(db_path, queued["task_id"])["status"] == "queued"
