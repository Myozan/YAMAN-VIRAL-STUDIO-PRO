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
