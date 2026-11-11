import sqlite3

from app import autopilot, main, task_queue


BASE = {
    "name": "QA Autopilot", "niche": "technology", "language": "tr",
    "clips": 3, "min_seconds": 10, "max_seconds": 30,
    "platforms": ["youtube"], "frequency": "daily", "publish_time": "09:00",
    "timezone": "Europe/Istanbul", "enabled": True,
}


def _prepare(database, monkeypatch):
    monkeypatch.setattr(main, "TASK_DB", database)
    main.init_task_store()
    autopilot.init_autopilot(database)
    item = autopilot.create_autopilot(database, BASE)
    return item


def test_autopilot_dispatch_uses_stable_task_id_and_reconciles_finished_run(tmp_path, monkeypatch):
    database = tmp_path / "autopilot-replay.sqlite3"
    item = _prepare(database, monkeypatch)
    queued = autopilot.enqueue_manual_run(database, item["id"])
    task_id = queued["task_id"]
    claimed = task_queue.claim(database, main.WORKER_ID, lease_seconds=90)
    assert claimed["task_id"] == task_id

    autopilot.finish_run(
        database, item["id"], "review", "already produced",
        task_id=task_id, outputs=[{"type": "clip", "url": "/workspace/final.mp4"}],
    )
    main.run_autopilot_cycle(item, task_id=task_id)

    state = main.get_task_state(task_id)
    assert state["status"] == "completed"
    assert state["outputs"] == [{"type": "clip", "url": "/workspace/final.mp4"}]
    with sqlite3.connect(database) as db:
        assert db.execute(
            "SELECT COUNT(*) FROM autopilot_runs WHERE task_id=?", (task_id,)
        ).fetchone()[0] == 1


def test_stale_autopilot_worker_cannot_mark_schedule_running(tmp_path, monkeypatch):
    database = tmp_path / "autopilot-stale-owner.sqlite3"
    item = _prepare(database, monkeypatch)
    queued = autopilot.enqueue_manual_run(database, item["id"])
    task_id = queued["task_id"]
    claimed = task_queue.claim(database, "replacement-worker", lease_seconds=90)
    assert claimed["task_id"] == task_id

    monkeypatch.setattr(main, "WORKER_ID", "stale-worker")
    main.run_autopilot_cycle(item, task_id=task_id)

    current = autopilot.get_autopilot(database, item["id"])
    assert current["last_status"] == "queued"
    with sqlite3.connect(database) as db:
        assert db.execute(
            "SELECT status FROM autopilot_runs WHERE task_id=?", (task_id,)
        ).fetchone() is None
        assert db.execute(
            "SELECT status FROM tasks WHERE task_id=?", (task_id,)
        ).fetchone()[0] == "queued"


def test_durable_dispatch_resolves_autopilot_from_shared_store(tmp_path, monkeypatch):
    database = tmp_path / "autopilot-dispatch.sqlite3"
    item = _prepare(database, monkeypatch)
    calls = []
    monkeypatch.setattr(
        main, "run_autopilot_cycle",
        lambda resolved, task_id=None: calls.append((resolved["id"], task_id)),
    )
    main._dispatch_durable_task(
        "durable-autopilot-task", "autopilot",
        {"autopilot_id": item["id"], "item": {"id": "stale-payload-copy"}},
    )
    assert calls == [(item["id"], "durable-autopilot-task")]


def test_expired_worker_lease_cannot_write_public_task_progress(tmp_path, monkeypatch):
    database = tmp_path / "expired-lease-progress.sqlite3"
    monkeypatch.setattr(main, "TASK_DB", database)
    main.init_task_store()
    task_id = "expired-lease-task"
    main.enqueue_durable_task(task_id, "analyze", {"request": {}, "folder": str(tmp_path)}, "queued")
    claimed = task_queue.claim(database, main.WORKER_ID, lease_seconds=10)
    assert claimed["task_id"] == task_id
    main.set_task(task_id, 5, "worker started", "running")
    with sqlite3.connect(database) as db:
        db.execute(
            "UPDATE task_queue SET lease_expires_at='2000-01-01T00:00:00+00:00' WHERE task_id=?",
            (task_id,),
        )
    before = main.get_task_state(task_id)
    returned = main.set_task(task_id, 75, "stale worker progress", "running")
    after = main.get_task_state(task_id)
    assert after["status"] == "running"
    assert after["stage"] == before["stage"]
    assert returned["stage"] == before["stage"]
