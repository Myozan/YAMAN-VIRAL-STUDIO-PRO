import pytest
import sqlite3
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def api(tmp_path, monkeypatch):
    database = tmp_path / "api.sqlite3"
    monkeypatch.setattr(main, "TASK_DB", database)
    main.task_states.clear()
    main.jobs.clear()
    main._cancelled_tasks.clear()
    main.init_task_store()
    monkeypatch.setattr(main, "ollama_status", lambda: {"connected": False, "model": "test"})
    with TestClient(main.app) as client:
        yield client
    main.task_states.clear()
    main.jobs.clear()
    main._cancelled_tasks.clear()


def test_health_endpoint_is_available(api):
    response = api.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["ollama"] is False
    assert "youtube" in body["platforms"]


def test_analyze_rejects_out_of_range_clip_count(api):
    response = api.post("/api/analyze", json={"clips": 0, "min_seconds": 20, "max_seconds": 55})
    assert response.status_code == 422


def test_unknown_task_and_job_return_not_found(api):
    assert api.get("/api/tasks/does-not-exist").status_code == 404
    assert api.get("/api/jobs/does-not-exist").status_code == 404
    assert api.get("/api/tasks/does-not-exist/events").status_code == 404


def test_cancel_task_is_persisted_and_idempotent(api):
    main.set_task("task-cancel-1", 35, "Rendering")
    first = api.post("/api/tasks/task-cancel-1/cancel")
    second = api.post("/api/tasks/task-cancel-1/cancel")
    assert first.status_code == 200
    assert first.json() == {"cancelled": True, "status": "cancelled"}
    assert second.status_code == 200
    assert second.json() == {"cancelled": False, "status": "cancelled"}
    assert api.get("/api/tasks/task-cancel-1").json()["status"] == "cancelled"
    events = api.get("/api/tasks/task-cancel-1/events")
    assert events.status_code == 200
    assert events.json()["events"][-1]["event"] == "cancelled"


def test_task_store_init_does_not_interrupt_an_active_worker(api):
    main.set_task("task-restart-1", 60, "Rendering", task_type="render")
    main.init_task_store()
    response = api.get("/api/tasks/task-restart-1")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert main.recover_orphaned_tasks() == 0


def test_stale_worker_lease_marks_only_its_tasks_interrupted(api):
    main.set_task("task-stale-1", 60, "Rendering", task_type="render")
    with sqlite3.connect(main.TASK_DB) as db:
        db.execute("UPDATE task_workers SET heartbeat_at='2000-01-01T00:00:00+00:00' WHERE worker_id=?", (main.WORKER_ID,))
    assert main.recover_orphaned_tasks() == 1
    assert api.get("/api/tasks/task-stale-1").json()["status"] == "interrupted"


def test_publish_requires_explicit_confirmation_before_side_effects(api, monkeypatch):
    def forbidden_token_lookup(_platform):
        pytest.fail("OAuth token lookup must not happen without explicit confirmation")

    monkeypatch.setattr(main, "oauth_access_token", forbidden_token_lookup)
    response = api.post("/api/publish/youtube", json={
        "job_id": "missing-job", "clip_id": 1, "title": "QA safety test",
        "confirm_publish": False,
    })
    assert response.status_code == 400
    assert "confirmation" in response.json()["detail"].lower()


def test_unknown_publish_provider_is_rejected(api):
    response = api.post("/api/publish/unknown", json={
        "job_id": "missing-job", "clip_id": 1, "title": "QA safety test",
        "confirm_publish": True,
    })
    assert response.status_code == 404


def test_oauth_callback_rejects_unknown_or_expired_state(api):
    response = api.get("/api/oauth/callback/youtube", params={"code": "fake-code", "state": "not-issued"})
    assert response.status_code == 400
    assert "invalid or expired" in response.json()["detail"].lower()

def test_oauth_state_is_single_use_even_when_token_exchange_fails(api, monkeypatch):
    import sqlite3
    import time
    from fastapi import HTTPException

    with sqlite3.connect(main.TASK_DB) as db:
        db.execute(
            "INSERT INTO oauth_states(state,platform,verifier,redirect_uri,created_at) VALUES(?,?,?,?,?)",
            ("single-use-state", "youtube", "verifier", "http://localhost/callback", time.time()),
        )

    def fail_token_config(_platform):
        raise HTTPException(503, "OAuth app not configured")

    monkeypatch.setattr(main, "oauth_client", fail_token_config)
    first = api.get("/api/oauth/callback/youtube", params={"code": "fake", "state": "single-use-state"})
    assert first.status_code == 503

    with sqlite3.connect(main.TASK_DB) as db:
        remaining = db.execute("SELECT COUNT(*) FROM oauth_states WHERE state=?", ("single-use-state",)).fetchone()[0]
    assert remaining == 0

    replay = api.get("/api/oauth/callback/youtube", params={"code": "fake", "state": "single-use-state"})
    assert replay.status_code == 400
