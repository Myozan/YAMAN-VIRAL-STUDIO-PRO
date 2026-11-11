import json
import shutil
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main


def test_task_updates_are_serialized_under_concurrent_writes(tmp_path, monkeypatch):
    database = tmp_path / "concurrent.sqlite3"
    monkeypatch.setattr(main, "TASK_DB", database)
    main.task_states.clear()
    main.init_task_store()

    def update(index):
        return main.set_task("shared-task", index, f"stage-{index}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(update, range(1, 65)))

    with sqlite3.connect(database) as db:
        row = db.execute("SELECT status,percent,payload_json FROM tasks WHERE task_id='shared-task'").fetchone()
        event_count = db.execute("SELECT COUNT(*) FROM task_events WHERE task_id='shared-task'").fetchone()[0]
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]

    assert row is not None
    assert row[0] == "running"
    assert 1 <= row[1] <= 64
    assert json.loads(row[2])["task_id"] == "shared-task"
    assert event_count == 64
    assert integrity == "ok"
    assert len(results) == 64


def test_agent_retry_rejects_running_task(api):
    main.set_task(
        "agent-running", 20, "Agent running", task_type="agents",
        request={"job_id": "job-x", "clip_id": 1, "platforms": ["youtube"]},
    )
    response = api.post("/api/tasks/agent-running/retry")
    assert response.status_code == 409
    assert "only failed" in response.json()["detail"].lower()


def test_agent_retry_requires_source_job_to_be_reopened(api):
    main.set_task(
        "agent-failed", 100, "Agent failed", "failed", task_type="agents",
        request={"job_id": "missing-job", "clip_id": 1, "platforms": ["youtube"]},
    )
    response = api.post("/api/tasks/agent-failed/retry")
    assert response.status_code == 409
    assert "reopen" in response.json()["detail"].lower()


def test_agent_retry_rejects_missing_clip(api):
    main.set_task(
        "agent-failed-clip", 100, "Agent failed", "failed", task_type="agents",
        request={"job_id": "job-existing", "clip_id": 99, "platforms": ["youtube"]},
    )
    main.jobs["job-existing"] = {"clips": [{"id": 1}], "folder": str(api_tmp_folder())}
    response = api.post("/api/tasks/agent-failed-clip/retry")
    assert response.status_code == 404


def api_tmp_folder():
    return Path(main.TASK_DB).parent


def test_agent_retry_queues_only_a_failed_task(api, monkeypatch):
    main.jobs["job-retry"] = {
        "clips": [{"id": 3, "text": "A valid clip", "duration": 10}],
        "folder": str(Path(main.TASK_DB).parent),
    }
    main.set_task(
        "agent-failed-valid", 100, "Agent failed", "failed", task_type="agents",
        request={"job_id": "job-retry", "clip_id": 3, "platforms": ["youtube"]},
    )
    scheduled = []
    monkeypatch.setattr(main, "run_agents_task", lambda *args: scheduled.append(args))
    response = api.post("/api/tasks/agent-failed-valid/retry")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "queued"
    assert body["retry_of"] == "agent-failed-valid"
    assert len(scheduled) == 1
    assert scheduled[0][0] == body["task_id"]


def test_fastapi_lifespan_starts_and_stops_scheduler():
    with TestClient(main.app):
        assert main._scheduler_thread is not None
        assert main._scheduler_thread.is_alive()
        assert not main._scheduler_stop.is_set()

    assert main._scheduler_stop.is_set()
    assert not main._scheduler_thread.is_alive()


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/FFprobe not installed")
def test_synthetic_ffmpeg_render_is_validated_by_ffprobe(tmp_path):
    output = tmp_path / "qa33-synthetic.mp4"
    command = [
        shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "testsrc=size=320x240:rate=24",
        "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=44100",
        "-t", "1.5", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-movflags", "+faststart", str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr

    info = main.probe_media_info(output)
    assert 1.0 <= info["duration"] <= 2.0
    assert info["size_bytes"] > 1024
    assert {stream["codec_type"] for stream in info["streams"]} >= {"video", "audio"}


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/FFprobe not installed")
def test_probe_rejects_audio_only_output(tmp_path):
    output = tmp_path / "audio-only.m4a"
    result = subprocess.run([
        shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
        "-t", "1", "-c:a", "aac", str(output),
    ], capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    with pytest.raises(RuntimeError, match="no video stream"):
        main.probe_media_info(output)


def test_probe_rejects_corrupt_media_file(tmp_path):
    corrupt = tmp_path / "corrupt.mp4"
    corrupt.write_bytes(b"not a media container" * 100)
    with pytest.raises(RuntimeError, match="could not be probed"):
        main.probe_media_info(corrupt)
import pytest


@pytest.fixture
def api(tmp_path, monkeypatch):
    database = tmp_path / "qa33-api.sqlite3"
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



def test_agent_retry_is_idempotently_reserved(api, monkeypatch):
    main.jobs["job-retry-once"] = {
        "clips": [{"id": 8, "text": "Retry once", "duration": 5}],
        "folder": str(Path(main.TASK_DB).parent),
    }
    main.set_task(
        "agent-failed-once", 100, "Agent failed", "failed", task_type="agents",
        request={"job_id": "job-retry-once", "clip_id": 8, "platforms": ["youtube"]},
    )
    scheduled = []
    monkeypatch.setattr(main, "run_agents_task", lambda *args: scheduled.append(args))

    first = api.post("/api/tasks/agent-failed-once/retry")
    second = api.post("/api/tasks/agent-failed-once/retry")

    assert first.status_code == 200
    assert second.status_code == 409
    assert len(scheduled) == 1
    with sqlite3.connect(main.TASK_DB) as db:
        claim = db.execute(
            "SELECT retry_task_id FROM task_retry_claims WHERE source_task_id=?",
            ("agent-failed-once",),
        ).fetchone()
    assert claim == (first.json()["task_id"],)


def test_retry_claim_table_survives_database_reopen(tmp_path):
    database = tmp_path / "retry-claims.sqlite3"
    original = main.TASK_DB
    try:
        main.TASK_DB = database
        main.init_task_store()
        with sqlite3.connect(database) as db:
            db.execute(
                "INSERT INTO task_retry_claims(source_task_id,retry_task_id,created_at) VALUES(?,?,?)",
                ("source", "retry", "2026-01-01T00:00:00+00:00"),
            )
        main.init_task_store()
        with sqlite3.connect(database) as db:
            assert db.execute("SELECT retry_task_id FROM task_retry_claims WHERE source_task_id='source'").fetchone() == ("retry",)
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        main.TASK_DB = original
