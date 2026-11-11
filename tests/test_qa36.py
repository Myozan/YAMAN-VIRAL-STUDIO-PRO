import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from requests import TooManyRedirects
from fastapi.testclient import TestClient

from app import main, secure_http


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "TASK_DB", tmp_path / "qa36-api.sqlite3")
    main.task_states.clear()
    main.init_task_store()
    with TestClient(main.app) as client:
        yield client
    main.task_states.clear()


def _dns(ip):
    return [(None, None, None, None, (ip, 443))]


def test_public_transport_rejects_private_dns_before_connect(monkeypatch):
    monkeypatch.setattr(secure_http.socket, "getaddrinfo", lambda *a, **k: _dns("10.1.2.3"))
    with pytest.raises(ValueError, match="non-public"):
        secure_http.request_public_https("GET", "https://api.example.test/data", timeout=2)


def test_public_transport_rejects_mixed_dns_answer_set(monkeypatch):
    monkeypatch.setattr(secure_http.socket, "getaddrinfo", lambda *a, **k: _dns("93.184.216.34") + _dns("192.168.1.4"))
    with pytest.raises(ValueError, match="non-public"):
        secure_http.request_public_https("GET", "https://api.example.test/data", timeout=2)


def test_cross_origin_redirect_drops_authorization_and_cookie(monkeypatch):
    class Response:
        def __init__(self, status, location=None):
            self.status_code = status
            self.headers = {"Location": location} if location else {}
        def close(self): pass

    calls = []
    monkeypatch.setattr(secure_http, "resolve_public_ips", lambda host: ["93.184.216.34"])
    def fake_request(method, url, **kwargs):
        calls.append((method, url, dict(kwargs["headers"] or {})))
        return Response(302, "https://cdn.example.test/asset") if len(calls) == 1 else Response(200)
    monkeypatch.setattr(secure_http, "_single_request", fake_request)
    response = secure_http.request_public_https(
        "GET", "https://api.example.test/start", headers={
            "Authorization": "Bearer secret", "Cookie": "session=secret", "Accept": "application/json"
        }, timeout=3, max_redirects=1,
    )
    assert response.status_code == 200
    assert calls[0][2]["Authorization"] == "Bearer secret"
    assert "Authorization" not in calls[1][2]
    assert "Cookie" not in calls[1][2]
    assert calls[1][2]["Accept"] == "application/json"


def test_redirect_to_private_destination_is_blocked_before_second_request(monkeypatch):
    class Redirect:
        status_code = 302
        headers = {"Location": "https://internal.example.test/admin"}
        def close(self): pass
    calls = []
    def resolve(host, *args, **kwargs):
        ip = "10.0.0.8" if host == "internal.example.test" else "93.184.216.34"
        return _dns(ip)
    monkeypatch.setattr(secure_http.socket, "getaddrinfo", resolve)
    monkeypatch.setattr(secure_http, "_single_request", lambda *a, **k: calls.append(a[1]) or Redirect())
    with pytest.raises(ValueError, match="non-public"):
        secure_http.request_public_https("GET", "https://api.example.test/start", timeout=3, max_redirects=2)
    assert calls == ["https://api.example.test/start"]


def test_non_get_redirect_is_not_followed_by_default(monkeypatch):
    class Redirect:
        status_code = 302
        headers = {"Location": "https://upload.example.test/next"}
        def close(self): pass
    monkeypatch.setattr(secure_http, "resolve_public_ips", lambda host: ["93.184.216.34"])
    monkeypatch.setattr(secure_http, "_single_request", lambda *a, **k: Redirect())
    response = secure_http.request_public_https("POST", "https://api.example.test/upload", json={"ok": True}, timeout=3)
    assert response.status_code == 302


def test_task_state_merges_across_independent_processes(tmp_path):
    database = tmp_path / "shared-task-state.sqlite3"
    worker_script = '''import sys
from pathlib import Path
from app import main
main.TASK_DB = Path(sys.argv[1])
main.init_task_store()
worker = int(sys.argv[2])
for index in range(20):
    main.set_task("multi-worker-task", index, f"worker-{worker}-step-{index}", **{f"w{worker}_{index}": True})
'''
    processes = [
        subprocess.Popen([sys.executable, "-c", worker_script, str(database), str(worker)],
                         cwd=str(Path(__file__).resolve().parents[1]),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for worker in range(4)
    ]
    failures = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=90)
        if process.returncode:
            failures.append((process.returncode, stdout, stderr))
    assert not failures, failures
    with sqlite3.connect(database) as db:
        row = db.execute("SELECT payload_json FROM tasks WHERE task_id='multi-worker-task'").fetchone()
        events = db.execute("SELECT COUNT(*) FROM task_events WHERE task_id='multi-worker-task'").fetchone()[0]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    state = json.loads(row[0])
    assert sum(1 for key in state if key.startswith("w")) == 80
    assert events == 80
    assert integrity == "ok"


def test_task_reads_ignore_stale_process_cache(api):
    main.set_task("shared-read-task", 42, "DB current state", task_type="render")
    main.task_states["shared-read-task"] = {"task_id": "shared-read-task", "status": "failed", "stage": "stale cache"}
    state = main.get_task("shared-read-task")
    assert state["status"] == "running"
    assert state["stage"] == "DB current state"


def test_terminal_task_state_cannot_be_overwritten_by_late_worker_progress(api):
    main.set_task("terminal-task", 20, "Rendering")
    main.set_task("terminal-task", 20, "Cancelled by user", "cancelled")
    state = main.set_task("terminal-task", 90, "Late worker update", "running")
    assert state["status"] == "cancelled"
    assert state["stage"] == "Cancelled by user"
    assert main.task_is_cancelled("terminal-task")


def test_saved_job_can_be_loaded_by_a_worker_without_the_memory_cache(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    folder = workspace / "shared-job-001"
    folder.mkdir(parents=True)
    video = folder / "source.mp4"
    video.write_bytes(b"video-placeholder")
    (folder / "job.json").write_text(json.dumps({
        "job_id": "shared-job-001", "video": str(video), "duration": 42.5,
        "language": "tr", "segments": [{"start": 0, "end": 4, "text": "Merhaba"}],
        "clips": [{"id": 1, "text": "Merhaba", "start": 0, "end": 4}],
    }), encoding="utf-8")
    monkeypatch.setattr(main, "WORK", workspace)
    main.jobs.clear()
    loaded = main.get_job_state("shared-job-001")
    assert loaded is not None
    assert loaded["duration"] == 42.5
    assert loaded["clips"][0]["id"] == 1
    assert main.jobs["shared-job-001"] is loaded


def test_saved_job_loader_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "WORK", tmp_path / "workspace")
    main.WORK.mkdir()
    main.jobs.clear()
    assert main.get_job_state("../outside") is None


def test_retry_claim_and_retry_task_row_commit_together(api, monkeypatch):
    main.jobs["qa36-retry-job"] = {
        "folder": str(Path(main.TASK_DB).parent), "clips": [{"id": 4, "text": "A clip"}],
    }
    main.set_task("qa36-retry-source", 100, "Failed", "failed", task_type="agents",
                  request={"job_id": "qa36-retry-job", "clip_id": 4, "platforms": ["youtube"]})
    monkeypatch.setattr(main, "run_agents_task", lambda *args: None)
    response = api.post("/api/tasks/qa36-retry-source/retry")
    assert response.status_code == 200
    retry_id = response.json()["task_id"]
    with sqlite3.connect(main.TASK_DB) as db:
        claim = db.execute("SELECT retry_task_id FROM task_retry_claims WHERE source_task_id=?",
                           ("qa36-retry-source",)).fetchone()
        task = db.execute("SELECT status,payload_json FROM tasks WHERE task_id=?", (retry_id,)).fetchone()
        queued = db.execute("SELECT task_type,payload_json FROM task_queue WHERE task_id=?", (retry_id,)).fetchone()
    assert claim == (retry_id,)
    assert task[0] in {"queued", "running", "failed", "completed"}
    assert json.loads(task[1])["retry_of"] == "qa36-retry-source"
    assert queued is not None
    assert queued[0] == "agents"
    assert json.loads(queued[1])["request"]["job_id"] == "qa36-retry-job"


def test_public_transport_preserves_provider_308_upload_status(monkeypatch):
    class ResumeIncomplete:
        status_code = 308
        headers = {"Range": "bytes=0-1023"}
        def close(self): pass
    monkeypatch.setattr(secure_http, "resolve_public_ips", lambda host: ["93.184.216.34"])
    monkeypatch.setattr(secure_http, "_single_request", lambda *a, **k: ResumeIncomplete())
    response = secure_http.request_public_https("PUT", "https://upload.example.test/session", data=b"chunk", timeout=3)
    assert response.status_code == 308
    assert response.headers["Range"] == "bytes=0-1023"
