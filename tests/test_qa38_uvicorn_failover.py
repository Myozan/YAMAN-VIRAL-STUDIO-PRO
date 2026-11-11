import json
import os
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _server_command():
    return r"""
import sys, time
from pathlib import Path
import uvicorn
import app.main as m
from app import task_queue

m.TASK_DB = Path(sys.argv[1])
m.init_task_store()
m.autopilot_store.init_autopilot(m.TASK_DB)
m.WORKER_STALE_SECONDS = 2

def qa_dispatch(task_id, task_type, payload):
    current = task_queue.get(m.TASK_DB, task_id)
    if current["attempts"] == 1:
        print("FIRST_OWNER", m.WORKER_ID, flush=True)
        while True:
            m.check_task_cancelled(task_id)
            time.sleep(0.1)
    m.set_task(task_id, 100, "QA failover completed", "completed", qa_smoke=True)

m._dispatch_durable_task = qa_dispatch
uvicorn.run(m.app, host="127.0.0.1", port=int(sys.argv[2]), log_level="error")
"""


def _wait_until(predicate, timeout=35, interval=0.2, message="condition not reached"):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            last = predicate()
            if last:
                return last
        except Exception:
            pass
        time.sleep(interval)
    raise AssertionError(f"{message}; last={last!r}")


def _queue_row(database, task_id):
    with sqlite3.connect(database, timeout=5) as db:
        return db.execute(
            "SELECT status,attempts,owner_id,lease_expires_at FROM task_queue WHERE task_id=?",
            (task_id,),
        ).fetchone()


def _health(port):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/queue/health", timeout=2) as response:
        return json.loads(response.read().decode("utf-8"))


@pytest.mark.skipif(os.name != "nt", reason="Real Uvicorn worker failover smoke test targets Windows")
def test_two_uvicorn_processes_reclaim_task_after_owner_process_is_killed(tmp_path):
    database = tmp_path / "orchestration.sqlite3"
    task_id = "qa38-" + uuid.uuid4().hex
    seed_code = r"""
import sys
from pathlib import Path
import app.main as m
m.TASK_DB = Path(sys.argv[1])
m.init_task_store()
m.autopilot_store.init_autopilot(m.TASK_DB)
m.enqueue_durable_task(sys.argv[2], "qa_smoke", {}, "QA failover queued")
"""
    seed = subprocess.run(
        [sys.executable, "-c", seed_code, str(database), task_id],
        cwd=ROOT, capture_output=True, text=True, timeout=45,
    )
    assert seed.returncode == 0, seed.stderr

    env = os.environ.copy()
    env["YAMAN_QUEUE_LEASE_SECONDS"] = "10"
    env["YAMAN_QUEUE_HEARTBEAT_SECONDS"] = "2"
    env["YAMAN_WORKER_HEARTBEAT_SECONDS"] = "1"
    env["YAMAN_WORKER_STALE_SECONDS"] = "2"
    env["YAMAN_QUEUE_POLL_SECONDS"] = "0.1"
    port_one, port_two = _free_port(), _free_port()
    first = second = None
    try:
        first = subprocess.Popen(
            [sys.executable, "-c", _server_command(), str(database), str(port_one)],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        first_claim = _wait_until(
            lambda: (row if (row := _queue_row(database, task_id)) and row[0] == "running" else None),
            timeout=45, message="first Uvicorn worker did not claim the task",
        )
        assert str(first.pid) in first_claim[2]

        second = subprocess.Popen(
            [sys.executable, "-c", _server_command(), str(database), str(port_two)],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        two_workers = _wait_until(
            lambda: (health if (health := _health(port_two))["worker_count"] >= 2 else None),
            timeout=45, message="second Uvicorn process did not register alongside first",
        )
        assert two_workers["ok"] is True

        first.kill()
        first.wait(timeout=10)

        completed = _wait_until(
            lambda: (row if (row := _queue_row(database, task_id)) and row[0] == "completed" else None),
            timeout=40, message="replacement Uvicorn worker did not recover and complete task",
        )
        assert completed[1] == 2
        assert completed[2] is None

        with sqlite3.connect(database, timeout=5) as db:
            public = db.execute("SELECT status,payload_json FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            events = [row[0] for row in db.execute(
                "SELECT event_type FROM task_events WHERE task_id=? ORDER BY id", (task_id,)
            )]
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert public[0] == "completed"
        assert json.loads(public[1])["qa_smoke"] is True
        assert "queued" in events and "completed" in events

        healthy = _wait_until(
            lambda: (health if (health := _health(port_two))["worker_count"] == 1 and health["ok"] else None),
            timeout=25, message="stale worker registry entry was not pruned",
        )
        assert healthy["stale_worker_count"] == 0
    finally:
        for process in (first, second):
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
