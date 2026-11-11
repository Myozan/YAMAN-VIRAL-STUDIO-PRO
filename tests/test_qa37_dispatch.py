import json
import sqlite3
import threading
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main, task_queue


@pytest.fixture
def queue_db(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "TASK_DB", tmp_path / "qa37-dispatch.sqlite3")
    main.task_states.clear()
    main.jobs.clear()
    main.init_task_store()
    yield
    main.task_states.clear()
    main.jobs.clear()


@pytest.fixture
def queue_api(queue_db):
    with TestClient(main.app) as client:
        yield client


def test_analyze_api_is_dispatched_by_durable_worker(queue_api, monkeypatch):
    completed = threading.Event()

    def fake_analyze(task_id, req, folder, source_video=None):
        assert req.url is not None
        assert folder.parent == main.WORK.resolve()
        main.set_task(task_id, 100, "Test analysis completed", "completed",
                      result={"job_id": task_id})
        completed.set()

    monkeypatch.setattr(main, "run_analyze_task", fake_analyze)
    response = queue_api.post("/api/analyze", json={
        "url": "https://www.youtube.com/watch?v=abcdefghijk",
        "clips": 3, "min_seconds": 10, "max_seconds": 30, "language": "tr"
    })
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    assert completed.wait(8), "Durable worker did not execute the queued analysis"
    with sqlite3.connect(main.TASK_DB) as db:
        task = db.execute("SELECT status,payload_json FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        queued = db.execute("SELECT status,attempts FROM task_queue WHERE task_id=?", (task_id,)).fetchone()
        events = db.execute("SELECT event_type FROM task_events WHERE task_id=?", (task_id,)).fetchall()
    assert task[0] == "completed"
    assert json.loads(task[1])["result"]["job_id"] == task_id
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with sqlite3.connect(main.TASK_DB) as db:
            queued = db.execute("SELECT status,attempts FROM task_queue WHERE task_id=?", (task_id,)).fetchone()
        if queued and queued[0] == "completed":
            break
        time.sleep(0.05)
    assert queued == ("completed", 1)
    assert any(row[0] == "queued" for row in events)
    assert any(row[0] == "completed" for row in events)


def test_worker_can_reopen_interrupted_task_after_queue_reclaim(queue_db, monkeypatch):
    task_id = "recover-qa37-001"
    main.enqueue_durable_task(task_id, "agents", {"request": {
        "job_id": "saved-job", "clip_id": 1, "platforms": ["youtube"]
    }}, "Queued for recovery")
    main.set_task(task_id, 15, "Previous worker stopped", "interrupted", error="simulated crash")
    monkeypatch.setattr(main, "_dispatch_durable_task",
                        lambda current_id, task_type, payload: main.set_task(
                            current_id, 100, "Recovered by replacement worker", "completed"))
    claimed = task_queue.claim(main.TASK_DB, main.WORKER_ID, lease_seconds=30)
    assert claimed and claimed["task_id"] == task_id
    main._execute_durable_task(claimed)
    state = main.get_task_state(task_id)
    queue_state = task_queue.get(main.TASK_DB, task_id)
    assert state["status"] == "completed"
    assert state["stage"] == "Recovered by replacement worker"
    assert queue_state["status"] == "completed"
    assert queue_state["attempts"] == 1


def test_startup_orphan_recovery_does_not_interrupt_queued_durable_tasks(queue_db):
    task_id = "queued-not-orphan-001"
    main.enqueue_durable_task(task_id, "agents", {"request": {
        "job_id": "saved-job", "clip_id": 1, "platforms": ["youtube"]
    }}, "Waiting in durable queue")
    recovered = main.recover_orphaned_tasks()
    state = main.get_task_state(task_id)
    assert state["status"] == "queued"
    assert recovered == 0


def test_queue_payload_rejects_workspace_path_escape(queue_db, monkeypatch):
    task_id = "unsafe-folder-task"
    main.enqueue_durable_task(task_id, "analyze", {
        "request": {"url": None, "clips": 2, "min_seconds": 10, "max_seconds": 30, "language": "tr"},
        "folder": str(Path(main.WORK).parent / "outside")
    }, "Unsafe analysis")
    with pytest.raises(RuntimeError, match="outside workspace"):
        main._dispatch_durable_task(task_id, "analyze", task_queue.get(main.TASK_DB, task_id)["payload"])


def test_summary_render_and_agent_payloads_rehydrate_and_dispatch(queue_db, monkeypatch):
    job_id = "dispatch-saved-job"
    main.jobs[job_id] = {
        "folder": str(Path(main.TASK_DB).parent),
        "clips": [{"id": 5, "text": "A useful clip", "start": 0, "end": 8}],
        "segments": [{"start": 0, "end": 8, "text": "A useful clip"}],
    }
    calls = []
    monkeypatch.setattr(main, "run_summary_task", lambda *args: calls.append(("summary", args)))
    monkeypatch.setattr(main, "run_render_task", lambda *args: calls.append(("render", args)))
    monkeypatch.setattr(main, "run_agents_task", lambda *args: calls.append(("agents", args)))

    summary = main.SummaryRequest(job_id=job_id, target_seconds=60, format="smart")
    main._dispatch_durable_task("summary-001", "summary", {"request": summary.model_dump()})
    render = main.RenderRequest(job_id=job_id, clip_id=5, platforms=["youtube"])
    main._dispatch_durable_task("render-001", "render", {
        "request": render.model_dump(), "platforms": ["youtube"]
    })
    agents = main.TeamRequest(job_id=job_id, clip_id=5, platforms=["youtube"])
    main._dispatch_durable_task("agents-001", "agents", {"request": agents.model_dump()})

    assert [item[0] for item in calls] == ["summary", "render", "agents"]
    assert calls[0][1][0:3] == ("summary-001", job_id, main.jobs[job_id])
    assert calls[1][1][0] == "render-001"
    assert calls[1][1][3]["id"] == 5
    assert calls[2][1][0] == "agents-001"


def test_cancelled_claim_is_not_dispatched(queue_db, monkeypatch):
    task_id = "cancel-before-dispatch"
    main.enqueue_durable_task(task_id, "agents", {"request": {
        "job_id": "saved-job", "clip_id": 1, "platforms": ["youtube"]
    }}, "Queued")
    claimed = task_queue.claim(main.TASK_DB, main.WORKER_ID, lease_seconds=30)
    assert claimed is not None
    assert task_queue.cancel(main.TASK_DB, task_id)
    main.set_task(task_id, 1, "Cancelled before execution", "cancelled")
    invoked = []
    monkeypatch.setattr(main, "_dispatch_durable_task", lambda *args: invoked.append(args))
    main._execute_durable_task(claimed)
    assert invoked == []
    assert main.get_task_state(task_id)["status"] == "cancelled"
    assert task_queue.get(main.TASK_DB, task_id)["status"] == "cancelled"


def test_replacement_process_worker_executes_task_after_claiming_process_is_killed(queue_db):
    import subprocess
    import sys

    task_id = "real-worker-failover-qa37"
    main.enqueue_durable_task(task_id, "test-failover", {"marker": "handoff"}, "Waiting for worker")
    root = Path(__file__).resolve().parents[1]
    first_worker_script = (
        "import sys,time; from app import task_queue; "
        "task=task_queue.claim(sys.argv[1], 'worker-to-kill', lease_seconds=10); "
        "print(task['task_id'] if task else 'NO_TASK', flush=True); time.sleep(60)"
    )
    first = subprocess.Popen(
        [sys.executable, "-c", first_worker_script, str(main.TASK_DB)],
        cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        assert first.stdout.readline().strip() == task_id
    finally:
        first.kill()
        first.communicate(timeout=10)

    with task_queue.connect(main.TASK_DB) as db:
        db.execute("UPDATE task_queue SET lease_expires_at=?,available_at=? WHERE task_id=?",
                   (task_queue.stamp(task_queue.utcnow() - __import__("datetime").timedelta(seconds=1)),
                    task_queue.stamp(), task_id))

    replacement_script = r'''
import sys, time
from pathlib import Path
from app import main, task_queue
database = Path(sys.argv[1])
task_id = sys.argv[2]
main.TASK_DB = database
main.WORKER_ID = "replacement-process-worker"
main.QUEUE_LEASE_SECONDS = 10
main.init_task_store()
def dispatch(current_id, task_type, payload):
    main.set_task(current_id, 100, "Completed by replacement process", "completed",
                  result={"worker": "replacement-process-worker"})
main._dispatch_durable_task = dispatch
main.start_durable_task_worker()
deadline = time.monotonic() + 20
state = None
while time.monotonic() < deadline:
    state = task_queue.get(database, task_id)
    if state and state["status"] == "completed":
        break
    time.sleep(0.1)
main.stop_durable_task_worker()
if not state or state["status"] != "completed":
    raise SystemExit("replacement worker did not complete the task")
'''
    result = subprocess.run(
        [sys.executable, "-c", replacement_script, str(main.TASK_DB), task_id],
        cwd=str(root), capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    queue_state = task_queue.get(main.TASK_DB, task_id)
    public_state = main.get_task_state(task_id)
    assert queue_state["status"] == "completed"
    assert queue_state["owner_id"] is None
    assert queue_state["attempts"] == 2
    assert public_state["status"] == "completed"
    assert public_state["result"]["worker"] == "replacement-process-worker"


def test_previous_worker_cannot_write_after_replacement_claim(queue_db, monkeypatch):
    task_id = "stale-worker-write-guard"
    main.enqueue_durable_task(task_id, "test-lease", {}, "Queued")
    first = task_queue.claim(main.TASK_DB, "worker-old", lease_seconds=10)
    assert first is not None
    with task_queue.connect(main.TASK_DB) as db:
        db.execute("UPDATE task_queue SET lease_expires_at=? WHERE task_id=?",
                   (task_queue.stamp(task_queue.utcnow() - __import__("datetime").timedelta(seconds=1)), task_id))
    assert task_queue.recover_expired(main.TASK_DB) == {"requeued": 1, "failed": 0}
    with task_queue.connect(main.TASK_DB) as db:
        db.execute("UPDATE task_queue SET available_at=? WHERE task_id=?",
                   (task_queue.stamp(), task_id))
    second = task_queue.claim(main.TASK_DB, "worker-new", lease_seconds=30)
    assert second is not None and second["owner_id"] == "worker-new"

    monkeypatch.setattr(main, "WORKER_ID", "worker-old")
    stale = main.set_task(task_id, 80, "Late update from old worker")
    assert stale["stage"] == "Queued"
    assert stale["status"] == "queued"

    monkeypatch.setattr(main, "WORKER_ID", "worker-new")
    fresh = main.set_task(task_id, 20, "Replacement worker progress")
    assert fresh["stage"] == "Replacement worker progress"
    assert fresh["status"] == "running"


def test_expired_queue_lease_is_reflected_as_queued_in_public_task_history(queue_db, monkeypatch):
    task_id = "public-requeue-state"
    main.enqueue_durable_task(task_id, "test-lease", {}, "Queued")
    monkeypatch.setattr(main, "WORKER_ID", "worker-before-crash")
    task_queue.claim(main.TASK_DB, "worker-before-crash", lease_seconds=10)
    main.set_task(task_id, 35, "Processing before crash", "running")
    with task_queue.connect(main.TASK_DB) as db:
        db.execute("UPDATE task_queue SET lease_expires_at=? WHERE task_id=?",
                   (task_queue.stamp(task_queue.utcnow() - __import__("datetime").timedelta(seconds=1)), task_id))
    assert task_queue.recover_expired(main.TASK_DB) == {"requeued": 1, "failed": 0}
    assert main._sync_requeued_queue_tasks() == 1
    state = main.get_task_state(task_id)
    assert state["status"] == "queued"
    assert state["stage"] == "Worker lease expired; queued for retry"
    with sqlite3.connect(main.TASK_DB) as db:
        events = db.execute("SELECT event_type FROM task_events WHERE task_id=?", (task_id,)).fetchall()
    assert events[-1][0] == "queued"
