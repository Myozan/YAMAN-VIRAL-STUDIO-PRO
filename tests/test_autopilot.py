from datetime import datetime, timedelta, timezone
import sqlite3
import pytest
from app import autopilot

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
    assert [x["id"] for x in autopilot.claim_due(db_path)] == [due["id"]]
    assert autopilot.get_autopilot(db_path, due["id"])["last_status"] == "running"
    assert autopilot.claim_due(db_path) == []

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
