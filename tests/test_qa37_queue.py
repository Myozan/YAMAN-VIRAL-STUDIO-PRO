import multiprocessing
import sqlite3
from datetime import timedelta

from app import task_queue


def _claim_worker(database, worker_id, output):
    task = task_queue.claim(database, worker_id)
    output.put(task["task_id"] if task else None)


def test_queue_schema_enqueue_and_idempotency(tmp_path):
    database = tmp_path / "queue.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    first = task_queue.enqueue(database, "render", {"clip_id": 7}, idempotency_key="render:job:7")
    duplicate = task_queue.enqueue(database, "render", {"clip_id": 99}, idempotency_key="render:job:7")
    assert first["task_id"] == duplicate["task_id"]
    assert duplicate["payload"] == {"clip_id": 7}
    assert duplicate["status"] == "queued"


def test_only_one_process_can_claim_a_task(tmp_path):
    database = tmp_path / "queue-race.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task = task_queue.enqueue(database, "analyze", {"source": "video.mp4"})
    ctx = multiprocessing.get_context("spawn")
    output = ctx.Queue()
    workers = [ctx.Process(target=_claim_worker, args=(str(database), f"worker-{i}", output)) for i in range(6)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(30)
        assert worker.exitcode == 0
    claimed = [output.get(timeout=3) for _ in workers]
    assert claimed.count(task["task_id"]) == 1
    assert claimed.count(None) == 5
    state = task_queue.get(database, task["task_id"])
    assert state["status"] == "running"
    assert state["attempts"] == 1


def test_expired_lease_is_requeued_with_backoff_then_failed_at_limit(tmp_path):
    database = tmp_path / "queue-recovery.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task = task_queue.enqueue(database, "agents", {}, max_attempts=2)
    claimed = task_queue.claim(database, "worker-dead", lease_seconds=10)
    expired = task_queue.utcnow() + timedelta(seconds=11)
    result = task_queue.recover_expired(database, now=expired, retry_base_seconds=1)
    assert result == {"requeued": 1, "failed": 0}
    recovered = task_queue.get(database, task["task_id"])
    assert recovered["status"] == "queued"
    assert recovered["owner_id"] is None
    assert recovered["attempts"] == 1
    assert recovered["last_error"] == "Worker lease expired"
    # Make the retry immediately eligible and claim it for a second worker.
    with task_queue.connect(database) as db:
        db.execute("UPDATE task_queue SET available_at=? WHERE task_id=?", (task_queue.stamp(), task["task_id"]))
    second = task_queue.claim(database, "worker-two", lease_seconds=10)
    assert second["attempts"] == 2
    result = task_queue.recover_expired(database, now=task_queue.utcnow() + timedelta(seconds=11))
    assert result == {"requeued": 0, "failed": 1}
    assert task_queue.get(database, task["task_id"])["status"] == "failed"


def test_heartbeat_and_completion_require_current_owner(tmp_path):
    database = tmp_path / "queue-owner.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task = task_queue.enqueue(database, "summary", {"job_id": "job1"})
    claimed = task_queue.claim(database, "worker-a")
    assert claimed["task_id"] == task["task_id"]
    assert not task_queue.heartbeat(database, task["task_id"], "worker-b")
    assert task_queue.heartbeat(database, task["task_id"], "worker-a")
    assert not task_queue.complete(database, task["task_id"], "worker-b")
    assert task_queue.complete(database, task["task_id"], "worker-a")
    assert task_queue.get(database, task["task_id"])["status"] == "completed"


def test_delayed_task_is_not_claimed_early(tmp_path):
    database = tmp_path / "queue-delay.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task_queue.enqueue(database, "publish", {}, delay_seconds=60)
    assert task_queue.claim(database, "worker-a") is None



def test_cancel_revokes_running_lease(tmp_path):
    database = tmp_path / "queue-cancel.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task = task_queue.enqueue(database, "render", {})
    task_queue.claim(database, "worker-a")
    assert task_queue.cancel(database, task["task_id"])
    assert not task_queue.heartbeat(database, task["task_id"], "worker-a")
    assert not task_queue.complete(database, task["task_id"], "worker-a")
    assert task_queue.get(database, task["task_id"])["status"] == "cancelled"


def test_killed_worker_process_lease_is_reclaimed_by_replacement(tmp_path):
    import subprocess
    import sys
    import time

    database = tmp_path / "queue-killed-worker.sqlite3"
    with task_queue.connect(database) as db:
        task_queue.init_schema(db)
    task = task_queue.enqueue(database, "render", {"job_id": "job-kill"}, max_attempts=3)
    script = (
        "import sys,time; from app import task_queue; "
        "t=task_queue.claim(sys.argv[1], 'worker-that-will-die', lease_seconds=10); "
        "print(t['task_id'] if t else 'NO_TASK', flush=True); time.sleep(60)"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", script, str(database)],
        cwd=str(__import__("pathlib").Path(__file__).resolve().parents[1]),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        claimed_line = process.stdout.readline().strip()
        assert claimed_line == task["task_id"]
    finally:
        process.kill()
        process.communicate(timeout=10)
    # Simulate elapsed lease time without sleeping through the real 10-second minimum.
    with task_queue.connect(database) as db:
        db.execute("UPDATE task_queue SET lease_expires_at=? WHERE task_id=?",
                   (task_queue.stamp(task_queue.utcnow() - timedelta(seconds=1)), task["task_id"]))
    recovered = task_queue.recover_expired(database)
    assert recovered == {"requeued": 1, "failed": 0}
    with task_queue.connect(database) as db:
        db.execute("UPDATE task_queue SET available_at=? WHERE task_id=?",
                   (task_queue.stamp(), task["task_id"]))
    replacement = task_queue.claim(database, "replacement-worker", lease_seconds=10)
    assert replacement["task_id"] == task["task_id"]
    assert replacement["owner_id"] == "replacement-worker"
    assert replacement["attempts"] == 2
