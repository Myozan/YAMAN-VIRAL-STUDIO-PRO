import json
import os
import socket
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until(predicate, timeout, message):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            last = predicate()
            if last:
                return last
        except Exception:
            pass
        time.sleep(0.5)
    raise AssertionError(f"{message}; last={last!r}")


@pytest.mark.skipif(os.name != "nt", reason="Production lease soak targets Windows worker processes")
def test_default_90_second_lease_recovers_after_worker_process_kill(tmp_path):
    database = tmp_path / "production-lease.sqlite3"
    task_id = "qa39-90s-" + uuid.uuid4().hex
    seed_code = r"""
import sys
from pathlib import Path
import app.main as m
m.TASK_DB = Path(sys.argv[1])
m.init_task_store()
m.autopilot_store.init_autopilot(m.TASK_DB)
m.enqueue_durable_task(sys.argv[2], "qa_smoke", {}, "QA 3.9 production lease soak")
"""
    seed = subprocess.run(
        [sys.executable, "-c", seed_code, str(database), task_id],
        cwd=ROOT, capture_output=True, text=True, timeout=45,
    )
    assert seed.returncode == 0, seed.stderr

    env = os.environ.copy()
    for key in (
        "YAMAN_QUEUE_LEASE_SECONDS",
        "YAMAN_QUEUE_HEARTBEAT_SECONDS",
        "YAMAN_WORKER_HEARTBEAT_SECONDS",
        "YAMAN_WORKER_STALE_SECONDS",
        "YAMAN_QUEUE_POLL_SECONDS",
    ):
        env.pop(key, None)

    server_code = r"""
import sys, time
from pathlib import Path
import uvicorn
import app.main as m
from app import task_queue

m.TASK_DB = Path(sys.argv[1])
m.init_task_store()
m.autopilot_store.init_autopilot(m.TASK_DB)
m.WORKER_STALE_SECONDS = 45

def qa_dispatch(task_id, task_type, payload):
    current = task_queue.get(m.TASK_DB, task_id)
    if current["attempts"] == 1:
        while True:
            m.check_task_cancelled(task_id)
            time.sleep(0.2)
    m.set_task(task_id, 100, "QA 3.9 production lease recovered", "completed",
               recovered_after_default_lease=True)

m._dispatch_durable_task = qa_dispatch
uvicorn.run(m.app, host="127.0.0.1", port=int(sys.argv[2]), log_level="error")
"""
    ports = (_free_port(), _free_port())
    first = second = None

    def queue_row():
        with sqlite3.connect(database, timeout=5) as db:
            return db.execute(
                "SELECT status,attempts,owner_id FROM task_queue WHERE task_id=?",
                (task_id,),
            ).fetchone()

    def health(port):
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/queue/health", timeout=3
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    import urllib.request

    try:
        first = subprocess.Popen(
            [sys.executable, "-c", server_code, str(database), str(ports[0])],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        first_claim = _wait_until(
            lambda: (row if (row := queue_row()) and row[0] == "running" else None),
            45, "first worker did not claim the task",
        )
        assert str(first.pid) in first_claim[2]

        second = subprocess.Popen(
            [sys.executable, "-c", server_code, str(database), str(ports[1])],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        _wait_until(
            lambda: (value if (value := health(ports[1]))["worker_count"] >= 2 else None),
            45, "second worker did not register",
        )

        first.kill()
        first.wait(timeout=10)

        completed = _wait_until(
            lambda: (row if (row := queue_row()) and row[0] == "completed" else None),
            155, "replacement worker did not reclaim task after the default 90-second lease",
        )
        assert completed[1] == 2
        assert completed[2] is None
        with sqlite3.connect(database, timeout=5) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            public = db.execute(
                "SELECT status,payload_json FROM tasks WHERE task_id=?", (task_id,)
            ).fetchone()
        assert public[0] == "completed"
        assert json.loads(public[1])["recovered_after_default_lease"] is True
    finally:
        for process in (first, second):
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
