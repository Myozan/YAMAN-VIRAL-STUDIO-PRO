import sqlite3
import pytest

from app import task_queue


def test_queue_snapshot_reports_counts_and_worker_health(tmp_path):
    database = tmp_path / "queue-health.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
        db.execute("""CREATE TABLE task_workers (
            worker_id TEXT PRIMARY KEY, pid INTEGER NOT NULL, hostname TEXT NOT NULL,
            started_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL
        )""")
    queued = task_queue.enqueue(database, "analyze", {"private": "payload"})
    running = task_queue.enqueue(database, "render", {"private": "payload"})
    task_queue.claim(database, "worker-live")
    with task_queue.connect(database) as db:
        now = task_queue.stamp()
        db.execute(
            "INSERT INTO task_workers VALUES(?,?,?,?,?)",
            ("worker-live", 1234, "test-host", now, now),
        )
    result = task_queue.snapshot(database)
    assert result["ok"] is True
    assert result["counts"]["queued"] == 1
    assert result["counts"]["running"] == 1
    assert result["worker_count"] == 1
    assert result["max_concurrent"] == 1
    assert result["workers"][0]["healthy"] is True
    assert "payload" not in str(result)
    assert queued["task_id"] != running["task_id"]


def test_queue_snapshot_flags_stale_worker_without_exposing_payloads(tmp_path):
    from datetime import timedelta

    database = tmp_path / "queue-stale.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
        db.execute("""CREATE TABLE task_workers (
            worker_id TEXT PRIMARY KEY, pid INTEGER NOT NULL, hostname TEXT NOT NULL,
            started_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL
        )""")
        stale = task_queue.stamp(task_queue.utcnow() - timedelta(minutes=5))
        db.execute(
            "INSERT INTO task_workers VALUES(?,?,?,?,?)",
            ("worker-stale", 1234, "test-host", stale, stale),
        )
    result = task_queue.snapshot(database, stale_after_seconds=45)
    assert result["ok"] is False
    assert result["stale_worker_count"] == 1
    assert result["workers"][0]["healthy"] is False


def test_queue_snapshot_is_not_healthy_without_registered_workers(tmp_path):
    database = tmp_path / "queue-no-workers.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
        db.execute("""CREATE TABLE task_workers (
            worker_id TEXT PRIMARY KEY, pid INTEGER NOT NULL, hostname TEXT NOT NULL,
            started_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL
        )""")
    result = task_queue.snapshot(database)
    assert result["ok"] is False
    assert result["worker_count"] == 0
    assert result["stale_worker_count"] == 0


def test_queue_recent_list_is_bounded_and_excludes_payloads(tmp_path):
    database = tmp_path / "queue-list.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task_queue.enqueue(database, "autopilot", {"secret": "do-not-return"})
    task_queue.enqueue(database, "render", {"secret": "also-private"})
    rows = task_queue.list_recent(database, limit=1, status="queued")
    assert len(rows) == 1
    assert rows[0]["task_type"] in {"autopilot", "render"}
    assert "payload" not in rows[0]
    assert "payload_json" not in rows[0]


def test_queue_recent_list_rejects_unknown_status(tmp_path):
    database = tmp_path / "queue-invalid-filter.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    import pytest
    with pytest.raises(ValueError, match="Invalid queue status"):
        task_queue.list_recent(database, status="secret")


def test_queue_tasks_api_returns_metadata_only_and_validates_filters(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from app import main

    database = tmp_path / "queue-api.sqlite3"
    monkeypatch.setattr(main, "TASK_DB", database)
    main.init_task_store()
    main.enqueue_durable_task("qa-api-task", "autopilot", {"private": "payload"}, "queued")
    response = main.durable_queue_tasks(limit=10, status="queued")
    assert len(response["tasks"]) == 1
    assert response["tasks"][0]["task_id"] == "qa-api-task"
    assert "payload" not in response["tasks"][0]
    with pytest.raises(HTTPException) as error:
        main.durable_queue_tasks(limit=101)
    assert error.value.status_code == 422
    with pytest.raises(HTTPException) as error:
        main.durable_queue_tasks(status="unknown")
    assert error.value.status_code == 422


def test_queue_claim_respects_global_concurrency_limit(tmp_path):
    database = tmp_path / "queue-concurrency.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    first = task_queue.enqueue(database, "analyze", {"n": 1})
    second = task_queue.enqueue(database, "autopilot", {"n": 2}, priority=40)
    claimed = task_queue.claim(database, "worker-one", max_running=1)
    assert claimed["task_id"] == second["task_id"]
    assert task_queue.claim(database, "worker-two", max_running=1) is None
    assert task_queue.complete(database, second["task_id"], "worker-one")
    next_task = task_queue.claim(database, "worker-two", max_running=1)
    assert next_task["task_id"] == first["task_id"]


def test_queue_claim_rejects_nonpositive_concurrency(tmp_path):
    database = tmp_path / "queue-concurrency-invalid.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    with pytest.raises(ValueError, match="max_running"):
        task_queue.claim(database, "worker", max_running=0)


def test_autopilot_manual_api_uses_durable_queue_and_rejects_duplicate(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from app import main, autopilot

    database = tmp_path / "autopilot-api.sqlite3"
    monkeypatch.setattr(main, "TASK_DB", database)
    main.init_task_store()
    autopilot.init_autopilot(database)
    item = autopilot.create_autopilot(database, {
        "name": "API test", "niche": "technology", "language": "tr",
        "clips": 3, "min_seconds": 10, "max_seconds": 30,
        "platforms": ["youtube"], "frequency": "daily", "publish_time": "09:00",
        "timezone": "Europe/Istanbul", "enabled": True,
    })
    result = main.run_autopilot_now(item["id"])
    assert result["queued"] is True
    assert result["task_id"]
    with pytest.raises(HTTPException) as error:
        main.run_autopilot_now(item["id"])
    assert error.value.status_code == 409
    assert task_queue.get(database, result["task_id"])["task_type"] == "autopilot"


def test_worker_heartbeat_recreates_pruned_registry_entry(tmp_path, monkeypatch):
    from app import main

    database = tmp_path / "worker-heartbeat-upsert.sqlite3"
    monkeypatch.setattr(main, "TASK_DB", database)
    main.init_task_store()
    main.heartbeat_task_worker()
    with sqlite3.connect(database) as db:
        row = db.execute(
            "SELECT pid,hostname,heartbeat_at FROM task_workers WHERE worker_id=?",
            (main.WORKER_ID,),
        ).fetchone()
    assert row is not None
    assert row[0] > 0
    assert row[1]
    assert row[2]
